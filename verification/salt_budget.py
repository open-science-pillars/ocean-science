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
# Golden notebook for the salt budget (Session 18, SPEC §10.5): the four-term
# 2010 salt budget on the ECCO v4r4 native grid, formulation per
# knowledge/recipes/ecco-salt-budget.md, with POINTWISE closure asserted on
# interior wet cells of one tile against the recipe's measured ABSOLUTE
# tolerance. Interior-of-tile is a valid pointwise subset (SPEC §6) and needs
# no tile-seam operators. Headless green via `python verification/salt_budget.py`.

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

    # Recipe tolerance (knowledge/recipes/ecco-salt-budget.md, measured
    # 2026-07-05: max 7.2e-11, p99.9 1.06e-11 g/kg/s; absolute because
    # float32 quantization makes relative ratios meaningless).
    TOL_ABS_MAX = 1.5e-10   # g/kg/s, ~2x measured max
    TOL_ABS_P999 = 2e-11    # g/kg/s, ~2x measured p99.9
    RHOCONST = 1029.0
    TILE = 1
    return TILE, TOL_ABS_MAX, TOL_ABS_P999, RHOCONST, np, paths, xr


@app.cell
def _(TILE, np, paths, xr):
    grid = xr.open_dataset(paths["geometry"]).isel(tile=TILE)

    def mf(sn):
        return xr.open_mfdataset(str(paths[sn] / "*.nc"), combine="by_coords").isel(tile=TILE)

    def m2010(ds):
        return ds.sel(time=ds.time.dt.year == 2010)

    sflux = m2010(mf("ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4"))
    fresh = m2010(mf("ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4"))
    snp_ts = mf("ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4")
    snp_ssh = mf("ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4")
    assert snp_ts.sizes["time"] == 13 and snp_ssh.sizes["time"] == 13
    assert sflux.sizes["time"] == 12, f"expected 12 months, got {sflux.sizes['time']}"

    dt = ((snp_ts.time.values[1:] - snp_ts.time.values[:-1]) / np.timedelta64(1, "s")).astype(np.float64)
    return dt, fresh, grid, sflux, snp_ssh, snp_ts


@app.cell
def _(dt, fresh, grid, np, sflux, snp_ssh, snp_ts):
    depth = grid.Depth.values
    hfacc = grid.hFacC.values
    vol = grid.rA.values[None] * grid.drF.values[:, None, None] * hfacc
    with np.errstate(divide="ignore", invalid="ignore"):
        sfac = np.where(depth > 0, 1.0 + snp_ssh.ETAN.values / depth, 1.0)

    # Term 1: z* tendency of s* * SALT.
    s_salt = snp_ts.SALT.values * sfac[:, None, :, :]
    g_total = (s_salt[1:] - s_salt[:-1]) / dt[:, None, None, None]

    def h_conv(fx_, fy_):
        fx_, fy_ = np.nan_to_num(fx_), np.nan_to_num(fy_)
        return -((fx_[:, :, :89, 1:90] - fx_[:, :, :89, 0:89])
                 + (fy_[:, :, 1:90, 0:89] - fy_[:, :, 0:89, 0:89]))

    def v_conv(fr):
        fr = np.where(hfacc[None] > 0, np.nan_to_num(fr), 0.0)
        frp = np.concatenate([fr, np.zeros_like(fr[:, :1])], axis=1)
        return frp[:, 1:] - frp[:, :-1]

    adv_h = h_conv(sflux.ADVx_SLT.values, sflux.ADVy_SLT.values)
    dif_h = h_conv(sflux.DFxE_SLT.values, sflux.DFyE_SLT.values)
    adv_v = v_conv(sflux.ADVr_SLT.values)[:, :, :89, :89]
    dif_v = v_conv(sflux.DFrE_SLT.values + sflux.DFrI_SLT.values)[:, :, :89, :89]
    vol_i = vol[:, :89, :89]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_adv = np.where(vol_i > 0, (adv_h + adv_v) / vol_i, 0.0)
        g_dif = np.where(vol_i > 0, (dif_h + dif_v) / vol_i, 0.0)

    # Term 4: SFLUX (top layer) + oceSPtnd (3D brine plume), no SW, no geothermal.
    forcS = np.nan_to_num(sflux.oceSPtnd.values).copy()
    forcS[:, 0, :, :] += np.nan_to_num(fresh.SFLUX.values)
    hfac_drf = hfacc * grid.drF.values[:, None, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_forc = np.where(hfac_drf[None] > 0, (forcS / 1029.0) / hfac_drf[None], 0.0)
    return g_adv, g_dif, g_forc, g_total, hfacc


@app.cell
def _(TOL_ABS_MAX, TOL_ABS_P999, g_adv, g_dif, g_forc, g_total, hfacc, np):
    gt = g_total[:, :, :89, :89]
    gf = g_forc[:, :, :89, :89]
    wet = hfacc[:, :89, :89] > 0
    res = np.abs((gt - (g_adv + g_dif + gf))[np.broadcast_to(wet[None], gt.shape)])
    n = int(res.size)
    r_max, r_p999 = float(res.max()), float(np.percentile(res, 99.9))
    print(f"salt_budget: cells {n}, absolute residual (g/kg/s) max {r_max:.2e}, p99.9 {r_p999:.2e}")
    assert n > 1_000_000, "subset unexpectedly small"
    assert r_max <= TOL_ABS_MAX, f"closure FAILED: max {r_max:.2e} > {TOL_ABS_MAX}"
    assert r_p999 <= TOL_ABS_P999, f"closure FAILED: p99.9 {r_p999:.2e} > {TOL_ABS_P999}"
    print("salt_budget golden: pointwise closure PASSED at the recipe tolerance")
    return


if __name__ == "__main__":
    app.run()
