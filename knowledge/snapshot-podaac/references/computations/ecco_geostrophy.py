#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Sanctioned computation: geostrophic balance and thermal wind, ECCO v4r4.

Two checks in one receipt, both against the model's own fields, both
computed per tile in GRID coordinates so no rotation enters (geostrophy
is frame-invariant in an orthogonal grid, and comparing grid-relative
u_g against grid-relative UVEL sidesteps the rotation trap entirely;
the rotation rule still applies the moment anything is mapped to east
and north, per the vector-orientation and curl-second-rotation
concepts).

1. GEOSTROPHIC BALANCE: u_g = -(1/(rho f)) dp/dy, v_g = +(1/(rho f))
   dp/dx with p = rho0 * (g * ETAN + PHIHYD): the surface loading term
   PLUS the hydrostatic anomaly, because PHIHYD alone omits the
   barotropic pressure and correlates near zero with the model's
   currents (measured r = -0.04 without the term, 2026-09-01, the trap
   its own gotcha now records), and rho = rho0 + RHOAnoma, THE DENSITY
   FACTOR THE OTHER GOTCHA RECORDS.
   Compared against the model's UVEL and VVEL averaged to C points, at
   the depth nearest --depth-m, over tile interiors and wet cells. The
   headline metric is the OPEN-OCEAN INTERIOR: 10 <= |lat| <= 55
   degrees AND seafloor deeper than 3000 m, where a centered-difference
   C-point scheme has the signal to validate balance. The full-band and
   polar figures are reported alongside, never hidden (measured
   2026-09-01: the same scheme reads r = 0.79 over the whole 10-55 band
   because shelf and slope cells, where friction and boundary currents
   break the balance test, drag it; r = 0.92 once Depth > 3000 m).
   Reported: Pearson correlation and median absolute difference per
   band.

2. THERMAL WIND: the vertical shear of the computed geostrophic
   velocity between two depths against the density-gradient form
   -(g/(rho0 f)) * grad(rho): an internal identity whose agreement is
   discretization-limited. Reported: Pearson correlation.

Usage:
  ecco_geostrophy.py --month 2009-12 [--depth-m 350] [--depth2-m 700]
      [--data-root ~/ECCO_V4r4] [--receipt geos_receipt.json]
"""

import argparse
import datetime
import hashlib
import json
import uuid
from pathlib import Path

import netCDF4
import numpy as np

RHO0 = 1029.0
G = 9.81
OMEGA = 7.2921e-5
DENS = "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4"
VEL = "ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4"
SSH = "ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4"
GEOMETRY = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"


def centered(field, spacing, axis):
    """Interior centered difference at C points along the last-two axes."""
    out = np.full_like(field, np.nan)
    if axis == "x":
        num = field[..., :, 2:] - field[..., :, :-2]
        den = spacing[..., :, 1:-1] * 2.0
        out[..., :, 1:-1] = num / den
    else:
        num = field[..., 2:, :] - field[..., :-2, :]
        den = spacing[..., 1:-1, :] * 2.0
        out[..., 1:-1, :] = num / den
    return out


def to_c_x(face_field):
    out = np.full_like(face_field, np.nan)
    out[..., :, :-1] = 0.5 * (face_field[..., :, :-1] + face_field[..., :, 1:])
    return out


def to_c_y(face_field):
    out = np.full_like(face_field, np.nan)
    out[..., :-1, :] = 0.5 * (face_field[..., :-1, :] + face_field[..., 1:, :])
    return out


def data_identity(root):
    """Which tree fed this run. The root, and the RECORD.json stamp the
    verify tool leaves in a tree it has checked against its manifest
    (record name, manifest sha256, verification time, report sha256).
    A tree with no stamp is recorded as unverified, never invented."""
    root = Path(root).expanduser().resolve()
    stamp = root / "RECORD.json"
    return {"data_root": str(root),
            "record": json.loads(stamp.read_text()) if stamp.exists()
            else "unverified: no RECORD.json in this tree"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--month", required=True)
    ap.add_argument("--depth-m", type=float, default=350.0)
    ap.add_argument("--depth2-m", type=float, default=700.0)
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, default=Path("geos_receipt.json"))
    args = ap.parse_args()

    g = netCDF4.Dataset(args.data_root / GEOMETRY)
    yc = np.asarray(g["YC"][:])
    dxC = np.asarray(g["dxC"][:]); dyC = np.asarray(g["dyC"][:])
    hFacC = np.asarray(g["hFacC"][:])
    Z = np.asarray(g["Z"][:])
    k1 = int(np.argmin(np.abs(Z + args.depth_m)))
    k2 = int(np.argmin(np.abs(Z + args.depth2_m)))
    f = 2.0 * OMEGA * np.sin(np.deg2rad(yc))

    dens = netCDF4.Dataset(
        args.data_root / DENS /
        f"OCEAN_DENS_STRAT_PRESS_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    phi = np.asarray(dens["PHIHYD"][0])
    rhoa = np.asarray(dens["RHOAnoma"][0])
    sshds = netCDF4.Dataset(
        args.data_root / SSH /
        f"SEA_SURFACE_HEIGHT_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    etan = np.asarray(sshds["ETAN"][0])
    phi = phi + G * etan[None, :, :, :]   # FULL pressure potential
    vel = netCDF4.Dataset(
        args.data_root / VEL /
        f"OCEAN_VELOCITY_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    uvel = np.asarray(vel["UVEL"][0]); vvel = np.asarray(vel["VVEL"][0])

    # dxC/dyC live on face locations; use their C-point average as the
    # centered-difference metric (correlation-grade validation, not a
    # bit-exact reproduction of the staggered helper).
    dx_c = to_c_x(dxC[None])[0]
    dy_c = to_c_y(dyC[None])[0]

    def geos_at(k):
        p = RHO0 * np.where(hFacC[k] > 0, phi[k], np.nan)
        rho = RHO0 + rhoa[k]
        dpdx = centered(p, dx_c[None].repeat(1, 0), "x")[...]
        dpdy = centered(p, dy_c[None].repeat(1, 0), "y")[...]
        with np.errstate(divide="ignore", invalid="ignore"):
            u_g = -dpdy / (rho * f)
            v_g = dpdx / (rho * f)
        return u_g, v_g

    u_g, v_g = geos_at(k1)
    u_c = to_c_x(np.where(hFacC[k1] > 0, uvel[k1], np.nan))
    v_c = to_c_y(np.where(hFacC[k1] > 0, vvel[k1], np.nan))

    margin = np.zeros_like(yc, dtype=bool)
    margin[:, 3:-3, 3:-3] = True
    finite = (margin & (hFacC[k1] > 0)
              & np.isfinite(u_g) & np.isfinite(v_g)
              & np.isfinite(u_c) & np.isfinite(v_c))
    depth = np.asarray(g["Depth"][:])
    band = finite & (np.abs(yc) >= 10.0) & (np.abs(yc) <= 55.0)
    valid = band & (depth > 3000.0)
    polar = finite & (np.abs(yc) > 55.0)
    a = np.concatenate([u_g[valid], v_g[valid]])
    b = np.concatenate([u_c[valid], v_c[valid]])
    r_vel = float(np.corrcoef(a, b)[0, 1])
    med = float(np.median(np.abs(a - b)))
    ab_ = np.concatenate([u_g[band], v_g[band]])
    bb_ = np.concatenate([u_c[band], v_c[band]])
    r_band = float(np.corrcoef(ab_, bb_)[0, 1])
    ap_ = np.concatenate([u_g[polar], v_g[polar]])
    bp_ = np.concatenate([u_c[polar], v_c[polar]])
    r_polar = float(np.corrcoef(ap_, bp_)[0, 1]) if polar.sum() > 100 else None

    # Thermal wind: shear of computed geostrophic velocity vs density form
    u_g2, v_g2 = geos_at(k2)
    dz = float(Z[k1] - Z[k2])
    shear_u = (u_g - u_g2) / dz
    shear_v = (v_g - v_g2) / dz
    rho_bar = 0.5 * (rhoa[k1] + rhoa[k2])
    rho_bar = np.where((hFacC[k1] > 0) & (hFacC[k2] > 0), rho_bar, np.nan)
    drdx = centered(rho_bar, dx_c[None].repeat(1, 0), "x")
    drdy = centered(rho_bar, dy_c[None].repeat(1, 0), "y")
    with np.errstate(divide="ignore", invalid="ignore"):
        tw_u = (G / (RHO0 * f)) * drdy
        tw_v = -(G / (RHO0 * f)) * drdx
    valid2 = (valid & (hFacC[k2] > 0) & np.isfinite(shear_u)
              & np.isfinite(shear_v) & np.isfinite(tw_u) & np.isfinite(tw_v))
    a2 = np.concatenate([shear_u[valid2], shear_v[valid2]])
    b2 = np.concatenate([tw_u[valid2], tw_v[valid2]])
    r_tw = float(np.corrcoef(a2, b2)[0, 1])

    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + str(uuid.uuid4())[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {
            "month": args.month, "depth_m": args.depth_m,
            "depth2_m": args.depth2_m,
            "collections": [SSH, DENS, VEL],
            "rho0_kg_m3": RHO0, "g_m_s2": G, "omega_s1": OMEGA,
        },
        "geostrophic": {
            "depth_used_m": float(-Z[k1]),
            "validation_domain": "10-55 deg latitude, seafloor deeper than 3000 m",
            "r_velocity": r_vel,
            "median_abs_diff_m_s": med,
            "n_points": int(valid.sum()),
            "r_velocity_full_band": r_band,
            "n_points_full_band": int(band.sum()),
            "r_velocity_polar_band": r_polar,
            "n_points_polar": int(polar.sum()),
        },
        "thermal_wind": {
            "depths_m": [float(-Z[k1]), float(-Z[k2])],
            "r_shear": r_tw,
            "n_points": int(valid2.sum()),
        },
        "frame_note": ("computed and compared in grid coordinates per "
                       "tile; any mapping to east and north requires the "
                       "CS and SN rotation per the vector-orientation "
                       "concepts"),
        "generated_at": (datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")),
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n",
                            encoding="utf-8")
    print(f"run {receipt['run_id']}: month {args.month}")
    print(f"  geostrophic vs model at {-Z[k1]:.0f} m, open-ocean interior "
          f"(10-55 deg, >3000 m): r = {r_vel:.4f}, "
          f"median |diff| = {med:.2e} m/s, n = {valid.sum():,}")
    print(f"  full 10-55 band incl shelf/slope: r = {r_band:.4f}, "
          f"n = {band.sum():,}")
    if r_polar is not None:
        print(f"  polar band (|lat| > 55): r = {r_polar:.4f}, "
              f"n = {polar.sum():,} (reported, not validated)")
    print(f"  thermal wind identity {-Z[k1]:.0f} to {-Z[k2]:.0f} m: "
          f"r = {r_tw:.4f}, n = {valid2.sum():,}")
    print(f"  receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
