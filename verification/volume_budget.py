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
# Golden notebook for the volume budget (Session 18, SPEC §10.5): the z*
# volume budget on the ECCO v4r4 native grid, formulation per
# knowledge/recipes/ecco-volume-budget.md. The budget closes on transport
# convergence ALONE (WVELMASS carries the surface freshwater flux; a separate
# oceFWflx forcing term double-counts and blows up the k=0 residual, which this
# golden also demonstrates). POINTWISE closure on interior wet cells of one
# tile. Headless green via `python verification/volume_budget.py`.

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
        "fetch_ecco_2010", HERE / "fixtures" / "fetch_ecco_2010.py")
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    paths = fx.ensure_cache()

    # Recipe tolerance (knowledge/recipes/ecco-volume-budget.md, measured
    # 2026-07-05: max 4.6e-12, p99.9 5.4e-13 1/s; absolute).
    TOL_ABS_MAX = 1e-11    # 1/s, ~2x measured max
    TOL_ABS_P999 = 1e-12   # 1/s, ~2x measured p99.9
    TILE = 1
    return TILE, TOL_ABS_MAX, TOL_ABS_P999, np, paths, xr


@app.cell
def _(TILE, np, paths, xr):
    grid = xr.open_dataset(paths["geometry"]).isel(tile=TILE)

    def mf(sn):
        return xr.open_mfdataset(str(paths[sn] / "*.nc"), combine="by_coords").isel(tile=TILE)

    vflux = mf("ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4")
    vflux = vflux.sel(time=vflux.time.dt.year == 2010)
    snp_ssh = mf("ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4")
    fresh = mf("ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4")
    fresh = fresh.sel(time=fresh.time.dt.year == 2010)
    assert snp_ssh.sizes["time"] == 13 and vflux.sizes["time"] == 12

    dt = ((snp_ssh.time.values[1:] - snp_ssh.time.values[:-1]) / np.timedelta64(1, "s")).astype(np.float64)
    return dt, fresh, grid, snp_ssh, vflux


@app.cell
def _(dt, grid, np, snp_ssh, vflux):
    depth = grid.Depth.values
    hfacc = grid.hFacC.values
    vol = grid.rA.values[None] * grid.drF.values[:, None, None] * hfacc
    with np.errstate(divide="ignore", invalid="ignore"):
        sfac = np.where(depth > 0, 1.0 + snp_ssh.ETAN.values / depth, 1.0)

    # Term 1: tracer = 1, so tendency is d(s*)/dt, uniform down each column.
    g_total = (sfac[1:] - sfac[:-1]) / dt[:, None, None]
    g_total = np.broadcast_to(g_total[:, None, :, :], (12, 50, 90, 90))

    def h_conv(fx_, fy_):
        fx_, fy_ = np.nan_to_num(fx_), np.nan_to_num(fy_)
        return -((fx_[:, :, :89, 1:90] - fx_[:, :, :89, 0:89])
                 + (fy_[:, :, 1:90, 0:89] - fy_[:, :, 0:89, 0:89]))

    def v_conv(fr):
        fr = np.where(hfacc[None] > 0, np.nan_to_num(fr), 0.0)
        frp = np.concatenate([fr, np.zeros_like(fr[:, :1])], axis=1)
        return frp[:, 1:] - frp[:, :-1]

    # Mass-weighted volume transports from UVELMASS/VVELMASS/WVELMASS.
    u = np.nan_to_num(vflux.UVELMASS.values) * grid.dyG.values[None, None] * grid.drF.values[None, :, None, None]
    v = np.nan_to_num(vflux.VVELMASS.values) * grid.dxG.values[None, None] * grid.drF.values[None, :, None, None]
    w = np.nan_to_num(vflux.WVELMASS.values) * grid.rA.values[None, None]
    adv_h = h_conv(u, v)
    adv_v = v_conv(w)[:, :, :89, :89]
    vol_i = vol[:, :89, :89]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_adv = np.where(vol_i > 0, (adv_h + adv_v) / vol_i, 0.0)
    return g_adv, g_total, hfacc


@app.cell
def _(TOL_ABS_MAX, TOL_ABS_P999, g_adv, g_total, hfacc, np):
    gt = g_total[:, :, :89, :89]
    wet = hfacc[:, :89, :89] > 0
    # Closure: tendency = transport convergence, NO separate FW forcing.
    res = np.abs((gt - g_adv)[np.broadcast_to(wet[None], gt.shape)])
    n = int(res.size)
    r_max, r_p999 = float(res.max()), float(np.percentile(res, 99.9))
    print(f"volume_budget: cells {n}, absolute residual (1/s) max {r_max:.2e}, p99.9 {r_p999:.2e}")
    assert n > 1_000_000, "subset unexpectedly small"
    assert r_max <= TOL_ABS_MAX, f"closure FAILED: max {r_max:.2e} > {TOL_ABS_MAX} (a separate FW forcing term double-counts; see the recipe)"
    assert r_p999 <= TOL_ABS_P999, f"closure FAILED: p99.9 {r_p999:.2e} > {TOL_ABS_P999}"
    print("volume_budget golden: pointwise closure PASSED at the recipe tolerance")
    return


if __name__ == "__main__":
    app.run()
