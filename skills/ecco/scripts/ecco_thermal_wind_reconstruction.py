#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "netCDF4"]
# ///
"""Sanctioned computation: currents reconstructed from density alone by
thermal wind integrated from a level of no motion, ECCO v4r4, scored
against the model's own currents with the level-of-no-motion error
separated from the density-explains-shear question.

THE QUESTION. Given only the ocean's density, how well can the
currents be reconstructed? Thermal wind gives the VERTICAL SHEAR of
the geostrophic current from horizontal density gradients,

    du/dz =  (g / (f rho)) drho/dy
    dv/dz = -(g / (f rho)) drho/dx

with rho = rho0 + RHOAnoma, and shear integrated in z gives velocity
only up to an unknown constant per column: the current at some
reference depth. The classical closure assumes a LEVEL OF NO MOTION,
zero current at that depth, and the ECCO tutorial takes it at 3000 m
because deep currents tend to be much weaker than shallow ones. That
assumption is the weak link, and this computation measures it rather
than assuming it away.

WHAT IS COMPUTED, per tile in the tile frame (no rotation enters;
compare the frame note), at C points:

1. thermal-wind shear at every level from the centered horizontal
   density gradient (the same centered-difference scheme as the
   geostrophic balance computation, over the C-point averaged dxC and
   dyC), local rho in the denominator per the tutorial;
2. the RECONSTRUCTED current: shear integrated by the trapezoid rule
   between cell centers from the reference level (the model level
   nearest --reference-depth-m) upward to the surface and downward to
   the seafloor, zero at the reference level;
3. the model's UVEL and VVEL averaged to C points, and the model's own
   vertical shear by centered difference across levels;
4. three scores, each per level and aggregated over depth bands,
   Pearson r over both components and the RMS error ratio (RMS of the
   vector error over RMS of the model vector; 1.0 means no better
   than predicting rest):
   - ABSOLUTE: reconstruction against the model's actual currents.
     This is the answer to the question as asked; it carries the
     level-of-no-motion error in full;
   - RELATIVE: reconstruction against the model's current RELATIVE
     TO THE REFERENCE LEVEL, u(z) - u(z_ref). This is the shear-only
     skill: how well density explains the vertical structure once the
     unknown constant is granted. The gap between absolute and
     relative IS the level-of-no-motion error;
   - SHEAR: thermal-wind shear against the model's own shear, level
     by level. Where this is high, density controls the vertical
     shear of the real flow; where it is low it does not (mixing,
     friction, ageostrophic motion, or discretization);
5. the reference-level current itself, the thing the closure sets to
   zero: its median and 90th percentile speed over the domain.

Validation domain, as for the geostrophic computation: tile interiors,
10 <= |lat| <= 55 degrees, seafloor deeper than 3000 m, and the
column wet at the reference level. The equatorial band is excluded
because f -> 0; shelf and slope cells because friction and boundary
currents break the balance the reconstruction rests on. The 0 to 100 m
band is REPORTED AND NOT VALIDATED: the tutorial shows geostrophy
itself failing in the top 100 m, and this receipt carries that band
as a disclosure so no consumer can quote the interior skill as if it
held at the surface.

PER-CELL FIELDS (optional, --fields PATH): the maps behind the
scalars, written to a NumPy .npz with the file's and every array's
sha256 recorded in the receipt under `fields` (the attester fails a
receipt whose fields file is missing or altered): XC, YC, CS, SN,
Depth; a per-column SHEAR SKILL over the 100 to 1000 m band (one minus
the ratio of the shear error variance to the model shear variance,
both components, all levels in the band; near 1 where density
controls the shear, at or below 0 where it does not); the model speed
at the reference level (the level-of-no-motion error map); and, at
--map-depth-m, the reconstructed and model components and the absolute
and relative error magnitudes. Components are tile-frame and need the
CS and SN rotation before any east-north vector map; the scalar maps
need none.

Usage:
  ecco_thermal_wind_reconstruction.py --month 2009-12
      [--reference-depth-m 3000] [--map-depth-m 350]
      [--data-root ~/ECCO_V4r4] [--receipt tw_receipt.json]
      [--fields tw_fields.npz]
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
GEOMETRY = "geometry/GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
DOMAIN = "10-55 deg latitude, seafloor deeper than 3000 m, wet at the reference level"
MARGIN = 3
MIN_POINTS = 100
BANDS = [("0-100 m", 0.0, 100.0),
         ("100-1000 m", 100.0, 1000.0),
         ("1000 m to reference", 1000.0, None),
         ("below reference", None, None)]


def centered(field, spacing, axis):
    """Interior centered difference at C points along the last two axes."""
    out = np.full_like(field, np.nan)
    if axis == "x":
        out[..., :, 1:-1] = ((field[..., :, 2:] - field[..., :, :-2])
                             / (spacing[..., :, 1:-1] * 2.0))
    else:
        out[..., 1:-1, :] = ((field[..., 2:, :] - field[..., :-2, :])
                             / (spacing[..., 1:-1, :] * 2.0))
    return out


def load(ds, name):
    """A variable with its fill value turned into NaN. ECCO granules
    mark land and dry faces with _FillValue 9.97e+36, not NaN, and
    np.asarray on the masked array netCDF4 returns silently keeps the
    fill; a fill that reaches a difference or a sum ruins it without
    raising. Everything read from a granule comes through here, promoted
    to float64: the horizontal density gradient is this computation's
    whole signal, and 1029 + RHOAnoma in float32 would round the anomaly
    to 6e-5 kg m-3, sixty times coarser than the granule stores it."""
    return np.ma.filled(np.ma.masked_invalid(ds[name][0]).astype(np.float64),
                        np.nan)


def to_c_x(face_field):
    out = np.full_like(face_field, np.nan)
    out[..., :, :-1] = 0.5 * (face_field[..., :, :-1] + face_field[..., :, 1:])
    return out


def to_c_y(face_field):
    out = np.full_like(face_field, np.nan)
    out[..., :-1, :] = 0.5 * (face_field[..., :-1, :] + face_field[..., 1:, :])
    return out


def write_fields(path, arrays, note):
    """Per-cell arrays beside the receipt, hashed twice: the file as a
    whole (what the stdlib attester checks) and each array's raw bytes
    (what a renderer with NumPy checks, and what makes two runs on the
    same data comparable array by array)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: np.ascontiguousarray(v) for k, v in arrays.items()}
    np.savez_compressed(path, **arrays)
    return {
        "path": str(path),
        "format": "npz",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "arrays": {k: {"shape": list(v.shape), "dtype": str(v.dtype),
                       "sha256": hashlib.sha256(v.tobytes()).hexdigest()}
                   for k, v in arrays.items()},
        "note": note,
    }


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


def score(pred_u, pred_v, true_u, true_v, mask):
    """Pearson r over both components and the RMS error ratio, or None
    when fewer than MIN_POINTS cells qualify."""
    n = int(mask.sum())
    if n < MIN_POINTS:
        return None, None, n
    a = np.concatenate([pred_u[mask], pred_v[mask]])
    b = np.concatenate([true_u[mask], true_v[mask]])
    r = float(np.corrcoef(a, b)[0, 1])
    ratio = float(np.sqrt(np.sum((a - b) ** 2) / np.sum(b ** 2)))
    return r, ratio, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--month", required=True)
    ap.add_argument("--reference-depth-m", type=float, default=3000.0,
                    help="level of no motion, snapped to the nearest "
                         "model level (default 3000, the tutorial's)")
    ap.add_argument("--map-depth-m", type=float, default=350.0,
                    help="depth of the per-cell velocity and error maps")
    ap.add_argument("--data-root", type=Path, default=Path.home() / "ECCO_V4r4")
    ap.add_argument("--receipt", type=Path, default=Path("tw_receipt.json"))
    ap.add_argument("--fields", type=Path, default=None,
                    help="also write the per-cell arrays to this .npz and "
                         "record their hashes in the receipt")
    args = ap.parse_args()

    g = netCDF4.Dataset(args.data_root / GEOMETRY)
    xc = np.asarray(g["XC"][:]); yc = np.asarray(g["YC"][:])
    cs = np.asarray(g["CS"][:]); sn = np.asarray(g["SN"][:])
    dxC = np.asarray(g["dxC"][:]); dyC = np.asarray(g["dyC"][:])
    hFacC = np.asarray(g["hFacC"][:])
    hFacW = np.asarray(g["hFacW"][:])
    hFacS = np.asarray(g["hFacS"][:])
    depth = np.asarray(g["Depth"][:])
    Z = np.asarray(g["Z"][:])
    nz = Z.size
    k_ref = int(np.argmin(np.abs(Z + args.reference_depth_m)))
    k_map = int(np.argmin(np.abs(Z + args.map_depth_m)))
    f = 2.0 * OMEGA * np.sin(np.deg2rad(yc))
    wet = hFacC > 0

    dens = netCDF4.Dataset(
        args.data_root / DENS /
        f"OCEAN_DENS_STRAT_PRESS_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    rho = np.where(wet, RHO0 + load(dens, "RHOAnoma"), np.nan)
    vel = netCDF4.Dataset(
        args.data_root / VEL /
        f"OCEAN_VELOCITY_mon_mean_{args.month}_ECCO_V4r4_native_llc0090.nc")
    # UVEL lives on west faces and VVEL on south faces, so each takes
    # its own face mask (hFacW, hFacS): masking a face velocity with
    # the cell mask leaves fill at wet cells whose face is dry.
    u_m = to_c_x(np.where(hFacW > 0, load(vel, "UVEL"), np.nan))
    v_m = to_c_y(np.where(hFacS > 0, load(vel, "VVEL"), np.nan))

    # Thermal-wind shear at every level, C points, tile frame.
    dx_c = to_c_x(dxC[None])[0]
    dy_c = to_c_y(dyC[None])[0]
    drdx = centered(rho, np.broadcast_to(dx_c, rho.shape), "x")
    drdy = centered(rho, np.broadcast_to(dy_c, rho.shape), "y")
    with np.errstate(divide="ignore", invalid="ignore"):
        s_u = (G / (f * rho)) * drdy      # du/dz
        s_v = -(G / (f * rho)) * drdx     # dv/dz

    # Integrate from the reference level: zero there, trapezoid between
    # cell centers upward and downward. A NaN shear anywhere on the path
    # (a dry neighbour, a tile edge) leaves that cell unreconstructed.
    u_rec = np.full_like(s_u, np.nan)
    v_rec = np.full_like(s_v, np.nan)
    u_rec[k_ref] = np.where(wet[k_ref] & np.isfinite(s_u[k_ref]), 0.0, np.nan)
    v_rec[k_ref] = np.where(wet[k_ref] & np.isfinite(s_v[k_ref]), 0.0, np.nan)
    for k in range(k_ref - 1, -1, -1):
        dz = Z[k] - Z[k + 1]
        u_rec[k] = u_rec[k + 1] + 0.5 * (s_u[k] + s_u[k + 1]) * dz
        v_rec[k] = v_rec[k + 1] + 0.5 * (s_v[k] + s_v[k + 1]) * dz
    for k in range(k_ref + 1, nz):
        dz = Z[k - 1] - Z[k]
        u_rec[k] = u_rec[k - 1] - 0.5 * (s_u[k - 1] + s_u[k]) * dz
        v_rec[k] = v_rec[k - 1] - 0.5 * (s_v[k - 1] + s_v[k]) * dz

    # The model's own shear across levels, at cell centers.
    su_m = np.full_like(u_m, np.nan)
    sv_m = np.full_like(v_m, np.nan)
    dz2 = (Z[:-2] - Z[2:])[:, None, None, None]
    su_m[1:-1] = (u_m[:-2] - u_m[2:]) / dz2
    sv_m[1:-1] = (v_m[:-2] - v_m[2:]) / dz2

    # Domain and per-level masks.
    margin = np.zeros_like(yc, dtype=bool)
    margin[:, MARGIN:-MARGIN, MARGIN:-MARGIN] = True
    domain = (margin & (np.abs(yc) >= 10.0) & (np.abs(yc) <= 55.0)
              & (depth > 3000.0) & wet[k_ref]
              & np.isfinite(u_m[k_ref]) & np.isfinite(v_m[k_ref]))
    u_rel = u_m - u_m[k_ref][None]
    v_rel = v_m - v_m[k_ref][None]
    fin_vel = (np.isfinite(u_rec) & np.isfinite(v_rec)
               & np.isfinite(u_m) & np.isfinite(v_m) & wet)
    fin_shear = (np.isfinite(s_u) & np.isfinite(s_v)
                 & np.isfinite(su_m) & np.isfinite(sv_m) & wet)
    level_mask = fin_vel & domain[None]
    shear_mask = fin_shear & domain[None]

    by_level = []
    for k in range(nz):
        if k == k_ref:
            continue
        r_abs, q_abs, n = score(u_rec[k], v_rec[k], u_m[k], v_m[k], level_mask[k])
        if n < MIN_POINTS:
            continue
        r_rel, q_rel, _ = score(u_rec[k], v_rec[k], u_rel[k], v_rel[k], level_mask[k])
        r_sh, _, n_sh = score(s_u[k], s_v[k], su_m[k], sv_m[k], shear_mask[k])
        sp = np.hypot(u_m[k], v_m[k])[level_mask[k]]
        by_level.append({
            "depth_m": float(-Z[k]), "n_points": n,
            "r_absolute": r_abs, "rms_ratio_absolute": q_abs,
            "r_relative": r_rel, "rms_ratio_relative": q_rel,
            "r_shear": r_sh, "n_points_shear": n_sh,
            "median_model_speed_m_s": float(np.median(sp)),
        })

    def band_scores(lo, hi):
        if lo is None:                       # below the reference level
            ks = [k for k in range(k_ref + 1, nz)]
        else:
            top = hi if hi is not None else -Z[k_ref]
            ks = [k for k in range(nz)
                  if k != k_ref and lo <= -Z[k] < top
                  and (hi is not None or k < k_ref)]
        if not ks:
            return None
        m = level_mask[ks]
        sm = shear_mask[ks]
        r_abs, q_abs, n = score(u_rec[ks], v_rec[ks], u_m[ks], v_m[ks], m)
        if n < MIN_POINTS:
            return {"n_points": n, "note": "fewer than 100 cells; not scored"}
        r_rel, q_rel, _ = score(u_rec[ks], v_rec[ks], u_rel[ks], v_rel[ks], m)
        r_sh, _, n_sh = score(s_u[ks], s_v[ks], su_m[ks], sv_m[ks], sm)
        return {"depths_m": [float(-Z[ks[0]]), float(-Z[ks[-1]])],
                "levels": len(ks), "n_points": n,
                "r_absolute": r_abs, "rms_ratio_absolute": q_abs,
                "r_relative": r_rel, "rms_ratio_relative": q_rel,
                "r_shear": r_sh, "n_points_shear": n_sh}

    bands = {name: band_scores(lo, hi) for name, lo, hi in BANDS}

    ref_speed = np.hypot(u_m[k_ref], v_m[k_ref])[domain]
    reference = {
        "depth_used_m": float(-Z[k_ref]), "level_index": k_ref,
        "n_points": int(domain.sum()),
        "median_model_speed_m_s": float(np.median(ref_speed)),
        "p90_model_speed_m_s": float(np.percentile(ref_speed, 90)),
    }

    # Per-column shear skill over 100 to 1000 m for the "where" map.
    ks_band = [k for k in range(nz) if 100.0 <= -Z[k] < 1000.0]
    e = np.where(shear_mask[ks_band],
                 (s_u[ks_band] - su_m[ks_band]) ** 2
                 + (s_v[ks_band] - sv_m[ks_band]) ** 2, np.nan)
    t = np.where(shear_mask[ks_band],
                 su_m[ks_band] ** 2 + sv_m[ks_band] ** 2, np.nan)
    n_col = np.isfinite(e).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        skill = 1.0 - np.nansum(e, axis=0) / np.nansum(t, axis=0)
    skill = np.where((n_col >= len(ks_band) // 2) & domain, skill, np.nan)

    receipt = {
        "run_id": (datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y%m%dT%H%M%SZ") + "-" + str(uuid.uuid4())[:8]),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data": data_identity(args.data_root),
        "bound_parameters": {
            "month": args.month,
            "reference_depth_m": args.reference_depth_m,
            "map_depth_m": args.map_depth_m,
            "collections": [DENS, VEL],
            "rho0_kg_m3": RHO0, "g_m_s2": G, "omega_s1": OMEGA,
            "validation_domain": DOMAIN,
        },
        "reference": reference,
        "bands": bands,
        "by_level": by_level,
        "level_of_no_motion_caveat": (
            "the reconstruction sets the current to zero at the reference "
            "level; the model's current there is not zero (see reference."
            "median_model_speed_m_s), and the gap between the absolute "
            "and relative scores is that assumption's cost. Quote the "
            "absolute score as the reconstruction skill and the relative "
            "score only as the shear-only skill, never one for the other. "
            "The 0-100 m band is reported and not validated: geostrophy "
            "itself fails in the surface layer."),
        "frame_note": ("computed and compared in grid coordinates per "
                       "tile; any mapping to east and north requires the "
                       "CS and SN rotation per the vector-orientation "
                       "concepts"),
        "generated_at": (datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")),
    }
    if args.fields is not None:
        km = k_map
        receipt["fields"] = write_fields(args.fields, {
            "XC": xc, "YC": yc, "CS": cs, "SN": sn, "Depth": depth,
            "shear_skill_100_1000m": skill,
            "speed_model_at_reference": np.where(domain, np.hypot(u_m[k_ref], v_m[k_ref]), np.nan),
            "u_reconstructed_at_depth": np.where(level_mask[km], u_rec[km], np.nan),
            "v_reconstructed_at_depth": np.where(level_mask[km], v_rec[km], np.nan),
            "u_model_at_depth": np.where(level_mask[km], u_m[km], np.nan),
            "v_model_at_depth": np.where(level_mask[km], v_m[km], np.nan),
            "error_absolute_at_depth": np.where(level_mask[km], np.hypot(u_rec[km] - u_m[km], v_rec[km] - v_m[km]), np.nan),
            "error_relative_at_depth": np.where(level_mask[km], np.hypot(u_rec[km] - u_rel[km], v_rec[km] - v_rel[km]), np.nan),
            "mask_domain": domain,
            "mask_at_depth": level_mask[km],
        }, (f"maps at {-Z[km]:.1f} m (map_depth_m) in the tile frame; "
            "shear_skill_100_1000m is one minus the shear error variance "
            "over the model shear variance per column over 100-1000 m; "
            "speed_model_at_reference is the current the level-of-no-motion "
            "closure sets to zero; rotate components with CS and SN before "
            "any east-north vector map"))
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n",
                            encoding="utf-8")

    print(f"run {receipt['run_id']}: month {args.month}, level of no motion "
          f"{-Z[k_ref]:.0f} m (model speed there: median "
          f"{reference['median_model_speed_m_s']:.2e}, p90 "
          f"{reference['p90_model_speed_m_s']:.2e} m/s over {domain.sum():,} columns)")
    for name, b in bands.items():
        if b is None or "r_absolute" not in b:
            print(f"  {name}: {b}")
            continue
        print(f"  {name} ({b['levels']} levels, n = {b['n_points']:,}): "
              f"absolute r = {b['r_absolute']:.4f}, rms ratio {b['rms_ratio_absolute']:.3f}; "
              f"relative r = {b['r_relative']:.4f}, rms ratio {b['rms_ratio_relative']:.3f}; "
              f"shear r = {b['r_shear']:.4f}")
    if args.fields is not None:
        print(f"  fields -> {args.fields} (sha256 {receipt['fields']['sha256'][:12]}...)")
    print(f"  receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
