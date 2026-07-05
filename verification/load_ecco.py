# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "xarray",
#     "netcdf4",
#     "earthaccess",
#     "ecco_access",
# ]
# ///
# Golden notebook for the load-ecco workflow (Session 9, SPEC v0.5.1 §6):
# grid-merge structure assertions on the cached 2010 subset (scripted,
# cached fixture per fixtures/fetch_ecco_2010.py). Headless green via
# `python verification/load_ecco.py`; fails loudly if the cache cannot
# be established (no false greens).

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import importlib.util
    from pathlib import Path

    import numpy as np
    import xarray as xr

    HERE = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "fetch_ecco_2010", HERE / "fixtures" / "fetch_ecco_2010.py"
    )
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    paths = fx.ensure_cache()
    return np, paths, xr


@app.cell
def _(paths, xr):
    grid = xr.open_dataset(paths["geometry"])
    theta = xr.open_mfdataset(
        str(paths["ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4"] / "*.nc"),
        combine="by_coords", chunks={"time": 1},
    )
    ds = xr.merge([theta, grid])
    return ds, grid, theta


@app.cell
def _(ds, grid, np, theta):
    # THE LOADER'S CONTRACT, asserted:
    # 1. Native structure intact after merge.
    assert dict(theta.THETA.sizes) == {"time": 12, "k": 50, "tile": 13, "j": 90, "i": 90}
    assert theta.THETA.chunks is not None, "must be Dask-backed"

    # 2. Grid variables present post-merge (the auto-merge contract),
    #    including partial cells, masks, and rotation fields.
    for v in ("rA", "drF", "hFacC", "hFacW", "hFacS", "maskC", "CS", "SN", "Depth"):
        assert v in ds, f"grid variable {v} missing after merge"
    # Coordinates arrive as coordinates (the llc90 reference nuance).
    for c in ("XC", "YC", "Z"):
        assert c in ds.coords, f"{c} must be a coordinate"

    # 3. Merge did not corrupt alignment: geometry and data agree on
    #    the wet mask footprint at the surface.
    wet_geom = int((grid.hFacC.isel(k=0) > 0).sum())
    wet_data = int(ds.THETA.isel(time=0, k=0).notnull().sum())
    assert wet_geom == wet_data, f"wet footprint mismatch {wet_geom} vs {wet_data}"

    # 4. A native-weighted statistic lands in the physical range
    #    (weights rA*hFacC; the llc90 volume-weighting rule).
    w = (ds.rA * ds.hFacC.isel(k=0)).where(ds.hFacC.isel(k=0) > 0)
    sst = float((ds.THETA.isel(k=0) * w).sum(("tile", "j", "i")).mean("time")
                / w.sum(("tile", "j", "i")))
    assert 15.0 < sst < 22.0, f"implausible native-weighted SST {sst}"

    # 5. Units and identity survived.
    assert ds.THETA.attrs.get("units") == "degree_C"
    print("load_ecco golden: all assertions passed")
    print(f"  merged vars ok; wet footprint {wet_data}; 2010 SST {sst:.3f} degC")
    return


if __name__ == "__main__":
    app.run()
