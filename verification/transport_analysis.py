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
    # From knowledge/recipes/ecco-mht-26n.md (scope-corrected 2026-07-04);
    # the recipe is the authority, these constants mirror it and the golden
    # fails if recomputation drifts from the recorded anchors. The 0.8-1.4
    # multi-year band is ATLANTIC scope and is not asserted on single-year
    # values here; anchors and the basin-sum identity are.
    GLOBAL_2010_ANCHOR = 1.098         # PW, full latitude circle (no mask)
    ATL_2010_ANCHOR = 0.666            # PW, basin_name atlExt
    GLOBAL_MONTHLY_ENVELOPE = (-0.5, 2.2)   # PW, around the recorded series
    return ATL_2010_ANCHOR, GLOBAL_2010_ANCHOR, GLOBAL_MONTHLY_ENVELOPE


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
def _(ATL_2010_ANCHOR, GLOBAL_2010_ANCHOR, GLOBAL_MONTHLY_ENVELOPE, ds, ecco, np):
    # Global circle (no basin mask): the method-reproducibility anchor.
    mht_g = ecco.calc_meridional_heat_trsp(ds, lat_vals=[26.5])
    series = mht_g["heat_trsp"].squeeze().compute()
    assert series.attrs.get("units") == "PW"
    vals = np.asarray(series.values, dtype=float)
    mean_g = float(vals.mean())
    assert abs(mean_g - GLOBAL_2010_ANCHOR) < 0.02, \
        f"global anchor drift: {mean_g:.3f} vs {GLOBAL_2010_ANCHOR}"
    emin, emax = GLOBAL_MONTHLY_ENVELOPE
    assert emin < vals.min() and vals.max() < emax

    # Atlantic (atlExt): the RAPID-comparable scope, plus the basin-sum
    # identity that verified the scope correction (recipe, 2026-07-04).
    mean_a = float(ecco.calc_meridional_heat_trsp(
        ds, lat_vals=[26.5], basin_name="atlExt")["heat_trsp"].squeeze().mean().compute())
    mean_p = float(ecco.calc_meridional_heat_trsp(
        ds, lat_vals=[26.5], basin_name="pacExt")["heat_trsp"].squeeze().mean().compute())
    mean_i = float(ecco.calc_meridional_heat_trsp(
        ds, lat_vals=[26.5], basin_name="indExt")["heat_trsp"].squeeze().mean().compute())
    assert abs(mean_a - ATL_2010_ANCHOR) < 0.02, \
        f"Atlantic anchor drift: {mean_a:.3f} vs {ATL_2010_ANCHOR}"
    assert abs((mean_a + mean_p + mean_i) - mean_g) < 0.01, \
        "basin decomposition must sum to the global circle"

    print("transport_analysis golden: all assertions passed")
    print(f"  2010 MHT 26.5N: global {mean_g:.3f} PW = atl {mean_a:.3f} "
          f"+ pac {mean_p:.3f} + ind {mean_i:.3f}; monthly span "
          f"{vals.min():.2f}..{vals.max():.2f} PW")
    return


if __name__ == "__main__":
    app.run()
