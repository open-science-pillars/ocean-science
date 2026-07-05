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
# Golden notebook for the ocean-budget workflow (Session 9, SPEC §6): the
# full four-term 2010 heat budget, formulation exactly per
# skills/ecco/references/budget-formulation.md (tutorial-quoted), with
# POINTWISE closure asserted on the interior cells of one tile against
# the recipe tolerance (knowledge/recipes/ecco-heat-budget.md: relative
# residual <= 1e-6 vs the dominant term). Interior-of-tile is a valid
# spatial subset for pointwise closure per SPEC §6, and it needs no
# tile-seam operators (within-tile faces are unambiguous).
# Headless green via `python verification/ocean_budget.py`.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


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

    # Recipe tolerance (knowledge/recipes/ecco-heat-budget.md, re-grounded
    # 2026-07-04 on measurement: absolute, because float32 archives make
    # relative ratios meaningless below the quantization floor) and
    # tutorial constants (budget-formulation.md).
    TOL_ABS_MAX = 1e-10    # degC/s, 2x measured max (4.95e-11)
    TOL_ABS_P999 = 1e-11   # degC/s, measured p99.9 was 7.3e-12
    RHOCONST, C_P = 1029.0, 3994.0
    R_SW, ZETA1, ZETA2 = 0.62, 0.6, 20.0
    TILE = 1          # South Atlantic tile; interior cells j,i in 0..88
    return (C_P, R_SW, RHOCONST, TILE, TOL_ABS_MAX, TOL_ABS_P999,
            ZETA1, ZETA2, ecco, np, paths, xr)


@app.cell
def _(TILE, np, paths, xr):
    grid = xr.open_dataset(paths["geometry"]).isel(tile=TILE)
    flux = xr.open_mfdataset(
        str(paths["ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4"] / "*.nc"),
        combine="by_coords").isel(tile=TILE)
    hf = xr.open_mfdataset(
        str(paths["ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4"] / "*.nc"),
        combine="by_coords").isel(tile=TILE)
    snp_ts = xr.open_mfdataset(
        str(paths["ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4"] / "*.nc"),
        combine="by_coords").isel(tile=TILE)
    snp_ssh = xr.open_mfdataset(
        str(paths["ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4"] / "*.nc"),
        combine="by_coords").isel(tile=TILE)
    assert snp_ts.sizes["time"] == 13 and snp_ssh.sizes["time"] == 13
    assert "ETAN" in snp_ssh, f"ETAN missing from SSH snapshots: {sorted(snp_ssh.data_vars)}"

    dt = (snp_ts.time.values[1:] - snp_ts.time.values[:-1]) / np.timedelta64(1, "s")
    dt = dt.astype(np.float64)                     # seconds per month, (12,)
    return dt, flux, grid, hf, snp_ssh, snp_ts


@app.cell
def _(dt, grid, np, snp_ssh, snp_ts):
    # TERM 1: tendency with the z* scale factor (formulation term 1).
    depth = grid.Depth.values                       # (90, 90)
    theta_snp = snp_ts.THETA.values                 # (13, 50, 90, 90)
    etan_snp = snp_ssh.ETAN.values                  # (13, 90, 90)
    with np.errstate(divide="ignore", invalid="ignore"):
        sfac = np.where(depth > 0, 1.0 + etan_snp / depth, 1.0)   # (13, 90, 90)
    stheta = theta_snp * sfac[:, None, :, :]
    g_total = (stheta[1:] - stheta[:-1]) / dt[:, None, None, None]  # (12, 50, 90, 90)
    return (g_total,)


@app.cell
def _(flux, grid, np):
    # Volume element (partial cells IN) and the within-tile convergences.
    vol = (grid.rA.values[None, :, :] * grid.drF.values[:, None, None]
           * grid.hFacC.values)                     # (50, 90, 90)

    hfacc = grid.hFacC.values
    ax = np.nan_to_num(flux.ADVx_TH.values)         # (12, 50, 90, 90) at i_g
    ay = np.nan_to_num(flux.ADVy_TH.values)         # at j_g
    dx = np.nan_to_num(flux.DFxE_TH.values)
    dy = np.nan_to_num(flux.DFyE_TH.values)

    def h_conv(fx_, fy_):
        # convergence for interior cells i,j in 0..88: -(d/dx + d/dy)
        return -((fx_[:, :, :89, 1:90] - fx_[:, :, :89, 0:89])
                 + (fy_[:, :, 1:90, 0:89] - fy_[:, :, 0:89, 0:89]))

    def v_conv(fr):                                 # fr at k_l, (12, 50, 90, 90)
        fr = np.nan_to_num(fr)
        fr = np.where(hfacc[None] > 0, fr, 0.0)     # dry-cell garbage out
        frp = np.concatenate([fr, np.zeros_like(fr[:, :1])], axis=1)  # pad bottom
        return (frp[:, 1:] - frp[:, :-1])           # (12, 50, 90, 90)

    adv_h = h_conv(ax, ay)
    dif_h = h_conv(dx, dy)
    adv_v = v_conv(flux.ADVr_TH.values)[:, :, :89, :89]
    dif_v = v_conv(flux.DFrE_TH.values + flux.DFrI_TH.values)[:, :, :89, :89]

    vol_i = vol[:, :89, :89]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_adv = np.where(vol_i > 0, (adv_h + adv_v) / vol_i, 0.0)
        g_dif = np.where(vol_i > 0, (dif_h + dif_v) / vol_i, 0.0)
    return g_adv, g_dif, vol

@app.cell
def _(C_P, R_SW, RHOCONST, TILE, ZETA1, ZETA2, ecco, grid, hf, np, paths):
    # TERM 4: forcing with shortwave penetration and geothermal.
    Z = grid.Z.values                                # (50,) cell centers
    RF = np.concatenate([grid.Zp1.values[:-1], [np.nan]])  # upper faces + pad
    q1 = R_SW * np.exp(RF[:-1] / ZETA1) + (1 - R_SW) * np.exp(RF[:-1] / ZETA2)
    q2 = R_SW * np.exp(RF[1:] / ZETA1) + (1 - R_SW) * np.exp(RF[1:] / ZETA2)
    zcut = int(np.where(Z < -200)[0][0])
    q1[zcut:] = 0
    q2[zcut - 1:] = 0

    mskc = (grid.hFacC.values > 0).astype(np.float64)         # (50, 90, 90)
    mskc_dn = np.concatenate([mskc[1:], np.zeros_like(mskc[:1])], axis=0)

    tflux = np.nan_to_num(hf.TFLUX.values)           # (12, 90, 90)
    qsw = np.nan_to_num(hf.oceQsw.values)

    forc_sub = (q1[None, :, None, None] * (mskc[None] == 1)
                - q2[None, :, None, None] * (mskc_dn[None] == 1)) * qsw[:, None]
    forc_surf = (tflux - (1 - (q1[0] - q2[0])) * qsw) * mskc[0][None]
    forch = np.concatenate([forc_surf[:, None], forc_sub[:, 1:]], axis=1)

    geoflx = ecco.read_llc_to_tiles(str(paths["geothermal"].parent),
                                    paths["geothermal"].name, less_output=True)
    geo_tile = np.asarray(geoflx)[TILE]              # (90, 90)
    mskb = mskc - mskc_dn                            # bottom wet cell = 1
    geo3d = geo_tile[None, None] * mskb[None]        # (1, 50, 90, 90)

    hfac_drf = grid.hFacC.values * grid.drF.values[:, None, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        g_forc = np.where(hfac_drf[None] > 0,
                          ((forch + geo3d) / (RHOCONST * C_P)) / hfac_drf[None],
                          0.0)
    return (g_forc,)


@app.cell
def _(TOL_ABS_MAX, TOL_ABS_P999, g_adv, g_dif, g_forc, g_total, grid, np):
    # THE CLOSURE ASSERTION: pointwise ABSOLUTE residual on interior wet
    # cells, per the re-grounded recipe tolerance (2026-07-04 measurement).
    gt = g_total[:, :, :89, :89]
    gf = g_forc[:, :, :89, :89]
    wet = grid.hFacC.values[:, :89, :89] > 0         # (50, 89, 89)

    res = np.abs((gt - (g_adv + g_dif + gf))[np.broadcast_to(wet[None], gt.shape)])
    n = int(res.size)
    r_max, r_p999, r_med = float(res.max()), float(np.percentile(res, 99.9)), float(np.median(res))
    print(f"cells checked: {n} (12 months x interior wet cells)")
    print(f"absolute residual (degC/s): max {r_max:.2e}, p99.9 {r_p999:.2e}, median {r_med:.2e}")
    assert n > 1_000_000, "subset unexpectedly small"
    assert r_max <= TOL_ABS_MAX, f"closure FAILED: max {r_max:.2e} > {TOL_ABS_MAX}"
    assert r_p999 <= TOL_ABS_P999, f"closure FAILED: p99.9 {r_p999:.2e} > {TOL_ABS_P999}"
    print("ocean_budget golden: pointwise closure PASSED at the recipe tolerance")
    return


if __name__ == "__main__":
    app.run()
