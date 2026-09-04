# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4", "scipy"]
# ///
"""Colocation checks on the observed side of the 26.5N confrontation,
measured from the RAPID release's own files over the model overlap
(2004-04 through 2017-12). Three questions the recipe answers with
numbers from this script rather than with prose:

  1. Is the distributed overturning series moc_mar_hc10 the maximum
     of the distributed streamfunction profile? (twelve-hourly, both
     in moc_transports.nc and moc_vertical.nc) Sample by sample it is
     not; the profile is unfiltered and the series carries the ten-day
     low-pass, so the check is repeated with a zero-phase Butterworth
     at one cycle per ten days applied to the profile first.
  2. Max of the monthly-mean profile versus monthly mean of the
     twelve-hourly maxima: the observed side's own answer to the
     max-of-mean question, since the model's monthly product is a
     monthly-mean velocity field and the confrontation takes the
     maximum of ITS streamfunction. Also the depth of the observed
     monthly-mean maximum, to set beside the model's.
  3. Is the 10-day amoc_depth in meridional_transports.nc the same
     series at monthly resolution?

Usage: rapid_colocation_checks.py RAPID_TREE [--first YYYY-MM] [--last YYYY-MM]
Prints a JSON summary; the recipe cites the numbers and this file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import netCDF4
import numpy as np
from scipy.signal import butter, filtfilt


def month_key(date):
    return f"{date.year:04d}-{date.month:02d}"


def monthly(dates, values, first, last):
    by = {}
    for date, v in zip(dates, values):
        k = month_key(date)
        if first <= k <= last:
            by.setdefault(k, []).append(v)
    return by


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tree", type=Path)
    ap.add_argument("--first", default="2004-04")
    ap.add_argument("--last", default="2017-12")
    args = ap.parse_args()
    root = args.tree.expanduser().resolve()

    tr = netCDF4.Dataset(str(root / "moc_transports.nc"))
    t = tr["time"]
    dates = netCDF4.num2date(t[:], t.units)
    moc = np.ma.filled(tr["moc_mar_hc10"][:].astype(np.float64), np.nan)
    ve = netCDF4.Dataset(str(root / "moc_vertical.nc"))
    depth = ve["depth"][:].astype(np.float64)
    psi = np.ma.filled(ve["stream_function_mar"][:].astype(np.float64), np.nan)  # (depth, time)
    tv = ve["time"]
    if not np.array_equal(tv[:], t[:]):
        sys.exit("the profile file and the transport file have different time axes")

    # 1. the series against the profile maximum, sample by sample
    ok = ~np.isnan(moc) & ~np.isnan(psi).any(axis=0)
    pmax = np.nanmax(psi, axis=0)
    diff = (moc - pmax)[ok]
    q1 = {"samples_compared": int(ok.sum()),
          "unfiltered_profile": {
              "max_abs_difference_Sv": float(np.max(np.abs(diff))),
              "mean_difference_Sv": float(np.mean(diff)),
              "sd_difference_Sv": float(np.std(diff)),
              "samples_over_0.01_Sv": int((np.abs(diff) > 0.01).sum())}}
    # the series is ten-day low-passed; the profile is not. Filter the
    # profile (sixth-order Butterworth, cutoff one cycle per ten days
    # at two samples per day, zero phase), then take the maximum.
    b, a = butter(6, 0.1)
    psif = filtfilt(b, a, np.where(np.isnan(psi), 0.0, psi), axis=1)
    pmaxf = psif.max(axis=0)
    inner = ok.copy()
    inner[:40] = False
    inner[-40:] = False
    difff = (moc - pmaxf)[inner]
    q1["profile_lowpassed_then_maximised"] = {
        "filter": "Butterworth order 6, cutoff 0.1 cycles per day, filtfilt",
        "samples_compared": int(inner.sum()),
        "mean_difference_Sv": float(np.mean(difff)),
        "sd_difference_Sv": float(np.std(difff)),
        "max_abs_difference_Sv": float(np.max(np.abs(difff))),
        "samples_over_0.5_Sv": int((np.abs(difff) > 0.5).sum())}
    q1["sd_twelve_hourly_Sv"] = {"series": float(np.nanstd(moc[ok])),
                                "unfiltered_profile_maximum": float(np.nanstd(pmax[ok]))}

    # 2. max of monthly-mean profile vs monthly mean of the maxima
    months = sorted(monthly(dates, moc, args.first, args.last))
    by_idx = {}
    for i, date in enumerate(dates):
        k = month_key(date)
        if args.first <= k <= args.last and ok[i]:
            by_idx.setdefault(k, []).append(i)
    mean_of_max, max_of_mean, depth_of_max = [], [], []
    for k in months:
        idx = by_idx[k]
        mean_of_max.append(float(np.mean(moc[idx])))
        prof = psi[:, idx].mean(axis=1)
        j = int(np.argmax(prof))
        max_of_mean.append(float(prof[j]))
        depth_of_max.append(float(depth[j]))
    mom, mmx = np.asarray(mean_of_max), np.asarray(max_of_mean)
    q2 = {"months": len(months), "first": months[0], "last": months[-1],
          "mean_of_twelve_hourly_maxima_Sv": float(mom.mean()),
          "max_of_monthly_mean_profile_Sv": float(mmx.mean()),
          "difference_mean_Sv": float((mom - mmx).mean()),
          "difference_max_monthly_Sv": float(np.max(mom - mmx)),
          "difference_min_monthly_Sv": float(np.min(mom - mmx)),
          "depth_of_monthly_mean_maximum_m": {
              "mean": float(np.mean(depth_of_max)),
              "median": float(np.median(depth_of_max)),
              "min": float(np.min(depth_of_max)), "max": float(np.max(depth_of_max))},
          "by_month_difference_Sv": {k: round(float(a - b), 4)
                                     for k, a, b in zip(months, mom, mmx)}}

    # 3. the 10-day product at monthly resolution
    md = netCDF4.Dataset(str(root / "meridional_transports.nc"))
    tm = md["time"]
    d10 = netCDF4.num2date(tm[:], tm.units)
    a10 = np.ma.filled(md["amoc_depth"][:].astype(np.float64), np.nan)
    by10 = monthly(d10, a10, args.first, args.last)
    common = [k for k in months if k in by10]
    diff10 = np.asarray([np.nanmean(by10[k]) - mom[months.index(k)] for k in common])
    # the ten-day samples nearest each twelve-hourly time, for a direct check
    tt = np.asarray([(d - dates[0]).total_seconds() / 86400.0 for d in d10])
    t12 = np.asarray([(d - dates[0]).total_seconds() / 86400.0 for d in dates])
    near = np.searchsorted(t12, tt)
    near = np.clip(near, 0, len(t12) - 1)
    exact = np.abs(t12[near] - tt) < 1e-6
    direct = (a10[exact] - moc[near[exact]])
    direct = direct[~np.isnan(direct)]
    q3 = {"ten_day_samples": int(len(a10)),
          "samples_coinciding_with_a_twelve_hourly_time": int(exact.sum()),
          "direct_max_abs_difference_Sv": float(np.max(np.abs(direct))),
          "monthly_means_compared": len(common),
          "monthly_mean_difference_mean_Sv": float(diff10.mean()),
          "monthly_mean_difference_max_abs_Sv": float(np.max(np.abs(diff10))),
          "note": "a monthly mean of three ten-day samples is a coarser "
                  "average than a monthly mean of sixty twelve-hourly "
                  "samples; the direct comparison at coinciding times is "
                  "the identity check"}

    print(json.dumps({"tree": str(root), "overlap": [args.first, args.last],
                      "series_vs_profile_maximum": q1,
                      "max_of_mean_vs_mean_of_max": q2,
                      "ten_day_product": q3}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
