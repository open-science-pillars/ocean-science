# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "xarray", "netCDF4", "dask", "ecco_v4_py"]
# ///
"""Derivation behind the heat-budget recipe's quantization statement.

NOT A SANCTIONED COMPUTATION. No receipt, no attester. It exists so the
recipe's claim can be reproduced and disputed rather than taken on faith.

The tendency is built from float32 THETA and ETAN snapshots, so the
smallest tendency the archive can represent is one unit in the last place
of the stored value divided by the snapshot interval. A residual at or
below that is storage precision, not formulation error.

Measured 2026-08-31 on the baseline subset (3,341,772 wet cell-months,
2010): median residual 0.66x the floor, 96.4 percent of cells within 3x,
99.7 percent within 10x. An earlier version of the recipe asserted 0.15x
and 99.6 percent within 3x; those figures had no derivation on record and
do not reproduce.

Mirrors the sanctioned pointwise heat budget formulation and reproduces
its baseline cell count exactly.
"""
import numpy as np, xarray as xr, ecco_v4_py as ecco
from pathlib import Path

RHOCONST, C_P = 1029.0, 3994.0
R_SW, ZETA1, ZETA2 = 0.62, 0.6, 20.0
root = Path.home()/"ECCO_V4r4"; TILE, INT, YEAR = 1, 89, 2010
grid = xr.open_dataset(root/"geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc").isel(tile=TILE)
def mon(s):
    d = xr.open_mfdataset(str(root/s/"*.nc"), combine="by_coords").isel(tile=TILE)
    return d.sel(time=slice(f"{YEAR}-01-01", f"{YEAR}-12-31"))
def snp(s):
    d = xr.open_mfdataset(str(root/s/"*.nc"), combine="by_coords").isel(tile=TILE)
    return d.sel(time=slice(f"{YEAR}-01-01", f"{YEAR+1}-01-01T23:59"))
flux = mon("ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4")
hf = mon("ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4")
sts, sssh = snp("ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4"), snp("ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4")

hfacc = grid.hFacC.values; depth = grid.Depth.values
dt = ((sts.time.values[1:]-sts.time.values[:-1])/np.timedelta64(1,"s")).astype(np.float64)
with np.errstate(divide="ignore", invalid="ignore"):
    sfac = np.where(depth>0, 1.0+sssh.ETAN.values/depth, 1.0)
theta = sts.THETA.values
stheta = theta*sfac[:,None,:,:]
g_total = (stheta[1:]-stheta[:-1])/dt[:,None,None,None]

vol = grid.rA.values[None]*grid.drF.values[:,None,None]*hfacc
ax,ay = np.nan_to_num(flux.ADVx_TH.values), np.nan_to_num(flux.ADVy_TH.values)
dx,dy = np.nan_to_num(flux.DFxE_TH.values), np.nan_to_num(flux.DFyE_TH.values)
def h_conv(fx_,fy_):
    return -((fx_[:,:,:INT,1:INT+1]-fx_[:,:,:INT,0:INT])+(fy_[:,:,1:INT+1,0:INT]-fy_[:,:,0:INT,0:INT]))
def v_conv(fr):
    fr = np.where(hfacc[None]>0, np.nan_to_num(fr), 0.0)
    frp = np.concatenate([fr, np.zeros_like(fr[:,:1])], axis=1)
    return frp[:,1:]-frp[:,:-1]
vol_i = vol[:,:INT,:INT]
with np.errstate(divide="ignore", invalid="ignore"):
    g_adv = np.where(vol_i>0, (h_conv(ax,ay)+v_conv(flux.ADVr_TH.values)[:,:,:INT,:INT])/vol_i, 0.0)
    g_dif = np.where(vol_i>0, (h_conv(dx,dy)+v_conv(flux.DFrE_TH.values+flux.DFrI_TH.values)[:,:,:INT,:INT])/vol_i, 0.0)
Z = grid.Z.values; RF = np.concatenate([grid.Zp1.values[:-1],[np.nan]])
q1 = R_SW*np.exp(RF[:-1]/ZETA1)+(1-R_SW)*np.exp(RF[:-1]/ZETA2)
q2 = R_SW*np.exp(RF[1:]/ZETA1)+(1-R_SW)*np.exp(RF[1:]/ZETA2)
zc = int(np.where(Z<-200)[0][0]); q1[zc:]=0; q2[zc-1:]=0
mskc = (hfacc>0).astype(np.float64); mskc_dn = np.concatenate([mskc[1:], np.zeros_like(mskc[:1])],axis=0)
tflux, qsw = np.nan_to_num(hf.TFLUX.values), np.nan_to_num(hf.oceQsw.values)
forc_sub = (q1[None,:,None,None]*(mskc[None]==1)-q2[None,:,None,None]*(mskc_dn[None]==1))*qsw[:,None]
forc_surf = (tflux-(1-(q1[0]-q2[0]))*qsw)*mskc[0][None]
forch = np.concatenate([forc_surf[:,None], forc_sub[:,1:]], axis=1)
geo = np.asarray(ecco.read_llc_to_tiles(str(root),"geothermalFlux.bin",less_output=True))[TILE]
geo3d = geo[None,None]*(mskc-mskc_dn)[None]
hfd = hfacc*grid.drF.values[:,None,None]
with np.errstate(divide="ignore", invalid="ignore"):
    g_forc = np.where(hfd[None]>0, ((forch+geo3d)/(RHOCONST*C_P))/hfd[None], 0.0)

wet = hfacc[:,:INT,:INT]>0
sel = np.broadcast_to(wet[None], g_total[:,:,:INT,:INT].shape)
res = np.abs((g_total[:,:,:INT,:INT]-(g_adv+g_dif+g_forc[:,:,:INT,:INT])))[sel]

# The floor: one ulp of the STORED float32 tendency inputs, per second.
ulp = np.maximum(np.spacing(stheta[:-1].astype(np.float32)),
                 np.spacing(stheta[1:].astype(np.float32))).astype(np.float64)
floor = (ulp/dt[:,None,None,None])[:,:,:INT,:INT][sel]
ratio = res/np.where(floor>0, floor, np.nan)
ratio = ratio[np.isfinite(ratio)]
print(f"wet cell-months: {res.size:,}")
print(f"residual        max {res.max():.3e}  p99.9 {np.percentile(res,99.9):.3e}  median {np.median(res):.3e}")
print(f"quantization floor       median {np.median(floor):.3e} degC/s")
print(f"\nresidual / floor: median {np.median(ratio):.4f}")
for k in (1,2,3,5,10):
    print(f"  within {k:2d}x the floor: {100*np.mean(ratio<=k):.2f}%")
