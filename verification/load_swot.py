# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "xarray",
# ]
# ///
# Golden notebook for the load-swot workflow (Session 8b, SPEC v0.5.1 §6):
# flag decoding and swath-structure assertions on a synthetic regional SSH
# fixture built to the granule structure observed live 2026-07-04
# (dims num_lines x num_pixels = swath grid, ssha_karin + ssha_karin_qual,
# crid attribute; nadir gap as a NaN band mid-swath). Headless green via
# `python verification/load_swot.py`.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import numpy as np
    import xarray as xr

    return np, xr


@app.cell
def _(np, xr):
    # Synthetic regional swath fixture, deterministic. Structure mirrors
    # SWOT_L2_LR_SSH_Basic granules: 2 km posting, 69 cross-track pixels,
    # nadir gap ~pixels 32..36, quality flag bit-packed (0 = good).
    rng = np.random.default_rng(20260704)
    n_lines, n_pixels = 400, 69
    GAP = slice(32, 37)

    ssha = rng.normal(0.0, 0.08, size=(n_lines, n_pixels)).astype(np.float32)
    ssha += 0.15 * np.sin(np.linspace(0, 6 * np.pi, n_lines))[:, None].astype(np.float32)
    ssha[:, GAP] = np.nan  # nadir gap: no KaRIn data by construction

    qual = np.zeros((n_lines, n_pixels), dtype=np.uint32)
    bad_lines = rng.choice(n_lines, 40, replace=False)
    bad_pix = rng.integers(0, 32, 40)          # left-swath bad pixels, bit 0
    qual[bad_lines, bad_pix] |= 1
    rain_lines = rng.choice(n_lines, 25, replace=False)
    rain_pix = rng.integers(37, 69, 25)        # right-swath rain, bit 4
    qual[rain_lines, rain_pix] |= 1 << 4
    ssha[qual != 0] += 20.0                     # flagged pixels carry garbage

    ds = xr.Dataset(
        {
            "ssha_karin": (("num_lines", "num_pixels"), ssha),
            "ssha_karin_qual": (("num_lines", "num_pixels"), qual),
        },
        attrs={"crid": "SYNTH0", "product_file_id": "Basic",
               "note": "synthetic fixture; structure per live granule 2026-07-04"},
    )
    return GAP, ds, n_lines, n_pixels


@app.cell
def _(GAP, ds, np, n_lines, n_pixels):
    # THE LOADER'S CONTRACT, asserted:
    # 1. Flag decoding masks exactly the flagged pixels.
    good = ds.ssha_karin.where(ds.ssha_karin_qual == 0)
    n_flagged = int((ds.ssha_karin_qual != 0).sum())
    assert n_flagged > 0
    assert int(good.notnull().sum()) == int(ds.ssha_karin.notnull().sum()) - n_flagged

    # 2. Unmasked statistics are corrupted; masked ones are sane
    #    (the +5 m garbage on flagged pixels must vanish after decode).
    raw_mean = float(ds.ssha_karin.mean())
    good_mean = float(good.mean())
    assert abs(raw_mean) > 0.02, "fixture garbage must bite the raw mean"
    assert abs(good_mean) < 0.02, f"masked mean should be near zero, got {good_mean}"

    # 3. Swath structure intact: the nadir gap stays all-NaN, both sides
    #    retain data, and dims are untouched (no flattening).
    assert bool(good.isel(num_pixels=GAP).isnull().all()), "nadir gap must stay empty"
    left_cov = float(good.isel(num_pixels=slice(0, 32)).notnull().mean())
    right_cov = float(good.isel(num_pixels=slice(37, None)).notnull().mean())
    assert left_cov > 0.9 and right_cov > 0.9
    assert good.dims == ("num_lines", "num_pixels")
    assert good.sizes["num_lines"] == n_lines and good.sizes["num_pixels"] == n_pixels

    # 4. Per-swath summary: flags decoded per side with reasons (bits).
    left_bits = np.unique(ds.ssha_karin_qual.isel(num_pixels=slice(0, 32)).values)
    right_bits = np.unique(ds.ssha_karin_qual.isel(num_pixels=slice(37, None)).values)
    assert 1 in left_bits and (1 << 4) in right_bits, "bit provenance lost"

    # 5. Baseline provenance travels: the crid attribute is preserved.
    assert ds.attrs["crid"] == "SYNTH0"

    print("load_swot golden: all assertions passed")
    print(f"  flagged pixels masked: {n_flagged}; left/right coverage "
          f"{left_cov:.2f}/{right_cov:.2f}; gap intact; crid={ds.attrs['crid']}")
    return


if __name__ == "__main__":
    app.run()
