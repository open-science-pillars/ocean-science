"""The attester side of the sanctioned trend with interval, shared by
every attester that meets one.

Stdlib only. Written from the method statement in
computations/ecco_trend_ci.py, not copied from that file's structure:
its own incomplete beta, its own t quantile, its own least squares.
Three attesters import it: trend_ci_check.py for a standalone trend
receipt, and steric_check.py and sea_level_partition.py for the
interval block those computations embed beside their own trend. One
independent chain, so a defect in the recompute shows up in all
three at once rather than hiding in a copy.

check_block(block, values, method_path) is the whole contract for an
embedded block: the block names the sanctioned method by hash and that
hash matches the file on disk; the deseasonalization declared is the
one policy for a series that long; the trend recomputes from the
series (jointly with the climatology when one is removed); and
either the interval recomputed from the series matches every stated
number within REL_TOL, or the block says stated false and the
recompute agrees that no interval is honest. A block cannot dodge its
interval by claiming a refusal the recompute does not reproduce.
"""

import hashlib
import math
from pathlib import Path

CONFIDENCE = 0.95
MONTHS_PER_YEAR = 12.0
MIN_MONTHS = 6
CLIM_MIN_YEARS = 2
MIN_DOF = 1.0
REL_TOL = 1e-9
BLOCK_NUMBERS = ["trend", "ci_low", "ci_high", "half_width",
                 "naive_half_width", "r1", "n_eff", "dof", "se",
                 "t_quantile"]
DEFAULT_METHOD = (Path(__file__).resolve().parent.parent
                  / "computations" / "ecco_trend_ci.py")


def betacf(a, b, x, max_iter=500, eps=1e-15):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / (c if abs(c) > tiny else tiny)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * betacf(a, b, x) / a
    return 1.0 - front * betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t >= 0 else tail


def t_quantile(p, df):
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
        if hi > 1e12:
            raise ArithmeticError("t quantile out of range")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13 * max(1.0, hi):
            break
    return 0.5 * (lo + hi)




def recompute(values, deseasonalize):
    """The chain from the series alone. Always returns the fit (a
    slope needs three months); the interval fields are present only
    when the chain can state one, and "interval" says which."""
    y = list(values)
    n = len(y)
    if n < 3:
        return None
    t = list(range(n))
    if deseasonalize == "climatology":
        years = n // 12
        clim = [sum(y[k::12]) / years for k in range(12)]
        y = [v - clim[i % 12] for i, v in enumerate(y)]
        tclim = [sum(t[k::12]) / years for k in range(12)]
        t = [v - tclim[i % 12] for i, v in enumerate(t)]
    tbar = sum(t) / n
    ybar = sum(y) / n
    sxx = sum((ti - tbar) ** 2 for ti in t)
    slope = sum((ti - tbar) * (v - ybar) for ti, v in zip(t, y)) / sxx
    intercept = ybar - slope * tbar
    e = [v - intercept - slope * ti for ti, v in zip(t, y)]
    ss = sum(v * v for v in e)
    out = {"n": n, "series_fit": y, "slope_per_month": slope,
           "intercept": intercept, "sxx": sxx, "interval": False}
    if n < MIN_MONTHS:
        return out
    r1 = sum(a * b for a, b in zip(e, e[1:])) / ss
    n_eff = min(float(n), n * (1.0 - r1) / (1.0 + r1))
    dof = n_eff - 2.0
    out.update({"r1": r1, "n_eff": n_eff, "dof": dof})
    if dof < MIN_DOF:
        return out
    se = math.sqrt(ss / dof / sxx)
    tq = t_quantile(0.5 + CONFIDENCE / 2.0, dof)
    out.update({"interval": True, "se_per_month": se, "t_quantile": tq,
                "naive_se_per_month": math.sqrt(ss / (n - 2) / sxx)})
    return out


def close(a, b):
    return abs(a - b) <= REL_TOL * max(1.0, abs(a), abs(b))


def consecutive(dates):
    ym = [int(d[:4]) * 12 + int(d[5:7]) - 1 for d in dates]
    return all(b - a == 1 for a, b in zip(ym, ym[1:]))


def default_deseasonalize(n):
    return ("climatology" if n % 12 == 0 and n >= 12 * CLIM_MIN_YEARS
            else "none")


def check_block(block, values, method_path=DEFAULT_METHOD):
    """Return None when the embedded interval block is attested, else
    the reason it fails. values: the monthly series in the units the
    block reports per year."""
    if not isinstance(block, dict):
        return "interval block missing or not an object"
    want = hashlib.sha256(Path(method_path).read_bytes()).hexdigest()
    if block.get("method") != "trend-ci":
        return f"interval method {block.get('method')!r} is not trend-ci"
    if block.get("method_code_sha256") != want:
        return "interval method_code_sha256 does not match the sanctioned " \
               "trend computation"
    if block.get("confidence") != CONFIDENCE:
        return f"interval confidence {block.get('confidence')} != {CONFIDENCE}"
    n = len(values)
    if block.get("n") != n:
        return f"interval n {block.get('n')} != {n} series values"
    if not all(isinstance(v, (int, float)) and math.isfinite(v)
               for v in values):
        return "series has a non-finite value"
    des = block.get("deseasonalize")
    if des != default_deseasonalize(n):
        return f"deseasonalize {des!r} is not the policy for {n} months " \
               f"({default_deseasonalize(n)})"
    c = recompute(values, des)
    if c is not None:
        trend = c["slope_per_month"] * MONTHS_PER_YEAR
        v = block.get("trend")
        if not isinstance(v, (int, float)) or not close(v, trend):
            return f"trend {v} does not recompute ({trend})"
    elif "trend" in block:
        return f"a trend is stated for {n} months; a slope needs 3"
    if block.get("stated") is False:
        if c is not None and c["interval"]:
            return "block refuses an interval the recompute states: " \
                   f"{c['dof']:.2f} degrees of freedom is enough"
        if not isinstance(block.get("reason"), str) or not block["reason"]:
            return "refused interval carries no reason"
        return None
    if block.get("stated") is not True:
        return "interval block must say stated true or false"
    if c is None or not c["interval"]:
        return "block states an interval the recompute refuses " \
               f"({n} months; under {MIN_DOF} degree of freedom or " \
               f"fewer than {MIN_MONTHS} months)"
    half = c["t_quantile"] * c["se_per_month"] * MONTHS_PER_YEAR
    naive_half = (t_quantile(0.5 + CONFIDENCE / 2.0, n - 2)
                  * c["naive_se_per_month"] * MONTHS_PER_YEAR)
    mine = {"trend": trend, "ci_low": trend - half, "ci_high": trend + half,
            "half_width": half, "naive_half_width": naive_half,
            "r1": c["r1"], "n_eff": c["n_eff"], "dof": c["dof"],
            "se": c["se_per_month"] * MONTHS_PER_YEAR,
            "t_quantile": c["t_quantile"]}
    for k in BLOCK_NUMBERS:
        v = block.get(k)
        if not isinstance(v, (int, float)) or not close(v, mine[k]):
            return f"interval {k} {v} does not recompute ({mine[k]})"
    sig = (trend - half) * (trend + half) > 0
    if block.get("significant_at_confidence") is not sig:
        return "significance flag disagrees with the interval"
    return None
