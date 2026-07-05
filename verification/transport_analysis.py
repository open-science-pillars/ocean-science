# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "xarray",
#     "netcdf4",
#     "earthaccess",
#     "ecco_access",
#     "ecco_v4_py",
# ]
# ///
# Golden notebook for the transport-analysis workflow (Session 9, SPEC §6):
# MHT at 26.5N on the cached 2010 fluxes, asserted against the recipe
# concept knowledge/recipes/ecco-mht-26n.md (range, spread envelope, and
# the recorded 2010 reproducing anchor). Headless green via
# `python verification/transport_analysis.py`.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    # From knowledge/recipes/ecco-mht-26n.md (steward-verified 2026-07-04);
    # the recipe is the authority, these constants mirror it and the golden
    # fails if recomputation drifts from the recorded anchor.
    RECIPE_RANGE = (0.8, 1.4)          # PW, multi-year mean expectation
    RECIPE_2010_ANCHOR = 1.098         # PW, recorded reproducing run
    RECIPE_2010_MONTHLY_ENVELOPE = (-0.5, 2.2)  # PW, around the recorded series
    return RECIPE_2010_ANCHOR, RECIPE_2010_MONTHLY_ENVELOPE, RECIPE_RANGE


@app.cell
def _():
    import importlib.util
    from pathlib import Path

    import ecco_v4_py as ecco
    import numpy as np
    import xarray as xr

    HERE = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "fetch_ecco_2010", HERE / "fixtures" / "fetch_ecco_2010.py"
    )
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    paths = fx.ensure_cache()
    return ecco, np, paths, xr


@app.cell
def _(paths, xr):
    grid = xr.open_dataset(paths["geometry"])
    flux = xr.open_mfdataset(
        str(paths["ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4"] / "*.nc"),
        combine="by_coords",
    )
    ds = xr.merge([flux, grid])
    assert "ADVx_TH" in ds and "ADVy_TH" in ds
    return (ds,)


@app.cell
def _(RECIPE_2010_ANCHOR, RECIPE_2010_MONTHLY_ENVELOPE, RECIPE_RANGE, ds, ecco, np):
    mht = ecco.calc_meridional_heat_trsp(ds, lat_vals=[26.5])
    series = mht["heat_trsp"].squeeze().compute()
    assert series.attrs.get("units") == "PW"
    vals = np.asarray(series.values, dtype=float)
    mean = float(vals.mean())

    # Recipe assertions:
    lo, hi = RECIPE_RANGE
    assert lo < mean < hi, f"2010 mean {mean:.3f} PW outside recipe range {RECIPE_RANGE}"
    assert abs(mean - RECIPE_2010_ANCHOR) < 0.02, \
        f"drifted from the recorded 2010 anchor: {mean:.3f} vs {RECIPE_2010_ANCHOR}"
    emin, emax = RECIPE_2010_MONTHLY_ENVELOPE
    assert emin < vals.min() and vals.max() < emax, \
        f"monthly values escape the recorded envelope: {vals.min():.2f}..{vals.max():.2f}"

    print("transport_analysis golden: all assertions passed")
    print(f"  MHT 26.5N 2010 mean {mean:.3f} PW (recipe range {RECIPE_RANGE}, "
          f"anchor {RECIPE_2010_ANCHOR}); monthly span {vals.min():.2f}..{vals.max():.2f} PW")
    return


if __name__ == "__main__":
    app.run()
