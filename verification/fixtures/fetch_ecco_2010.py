"""Scripted, cached real-data fixture per SPEC §6: the 2010 ECCO subset.

Ensures the collections the ocean golden notebooks need are cached under
~/ECCO_V4r4 (Earthdata login via ~/.netrc required on first fetch; later
runs hit the cache). Nothing here is committed; granules total ~2.5 GB
(heat, salt, and volume budget inputs).
"""
from pathlib import Path
from urllib.request import urlretrieve

DATA = Path.home() / "ECCO_V4r4"

DATED = [
    ("ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
    ("ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
    ("ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
    ("ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4", "2010-01-01", "2011-01-01"),
    ("ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4", "2010-01-01", "2011-01-01"),
    # Salt and volume budget inputs (Session 18, SPEC §10.5):
    ("ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
    ("ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
    ("ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4", "2010-01", "2010-12"),
]
GEO_URL = ("https://github.com/ECCO-GROUP/ECCO-v4-Python-Tutorial/raw/master/"
           "misc/geothermalFlux.bin")


def ensure_cache() -> dict:
    """Fetch anything missing; return paths. Fails loudly without credentials."""
    paths = {"root": DATA}
    DATA.mkdir(exist_ok=True)

    geom_dir = DATA / "geometry"
    geom = geom_dir / "GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc"
    if not geom.exists():
        import earthaccess
        earthaccess.login(strategy="netrc")
        g = earthaccess.search_data(short_name="ECCO_L4_GEOMETRY_LLC0090GRID_V4R4")
        earthaccess.download(g, str(geom_dir))
    paths["geometry"] = geom

    for sn, s, e in DATED:
        d = DATA / sn
        if not d.exists() or not list(d.glob("*.nc")):
            import ecco_access as ea
            ea.ecco_podaac_to_xrdataset(sn, StartDate=s, EndDate=e, version="v4r4",
                                        mode="download_ifspace",
                                        download_root_dir=str(DATA))
        paths[sn] = d

    geo = DATA / "geothermalFlux.bin"
    if not geo.exists():
        urlretrieve(GEO_URL, geo)
    paths["geothermal"] = geo
    return paths


if __name__ == "__main__":
    p = ensure_cache()
    for k, v in p.items():
        print(f"{k}: {v}")
    print("FIXTURE_CACHE_OK")
