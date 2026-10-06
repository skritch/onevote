import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import json
    import math
    import sys
    import zipfile
    import argparse
    from pathlib import Path

    import re

    import geopandas as gpd
    import requests


@app.cell
def _():
    _parser = argparse.ArgumentParser(description="Download congressional district shapefiles")
    _parser.add_argument(
        "-o", "--output",
        default="./.data/shapefiles/",
        type=str,
        help="Output directory for shapefiles",
    )
    _args = _parser.parse_args()
    data_dir = Path(_args.output)
    return (data_dir,)


@app.cell
def _():
    # Election year -> Congress whose district boundaries were used.
    # 95th Congress is skipped: the 94th boundary set covers both 94th and 95th.
    ELECTION_TO_CONGRESS = {
        1976: 94,
        # 1978: 96,
        1980: 97,
        # 1982: 98,
        1984: 99,
        # 1986: 100,
        1988: 101,
        # 1990: 102,
        1992: 103,
        # 1994: 104,
        1996: 105,
        # 1998: 106,
        2000: 107,
        # 2002: 108,
        2004: 109,
        # 2006: 110,
        2008: 111,
        # 2010: 112,
        2012: 113,
        2014: 114,
        2016: 115,
        2018: 116,
        2020: 117,
        2022: 118,
        2024: 119,
        # 120th Congress may not yet be in the database;
        # falls back to 119th if unavailable (same post-2020 redistricting maps).
        2026: 120,
    }

    BASE_URL = (
        "https://github.com/JeffreyBLewis/congressional-district-boundaries"
        "/releases/download/latest-shapefiles"
    )
    return BASE_URL, ELECTION_TO_CONGRESS


@app.cell
def _(BASE_URL):
    def download_congress(congress_num: int, output_dir: Path) -> bool:
        """Download and extract shapefile zip for one Congress. Returns True on success."""
        name = f"districts{congress_num:03d}"
        congress_dir = output_dir / name

        if congress_dir.exists() and any(congress_dir.glob("*.shp")):
            print(f"  {name}: already present, skipping")
            return True

        url = f"{BASE_URL}/{name}.zip"
        zip_path = output_dir / f"{name}.zip"

        print(f"  {name}: downloading {url}")
        try:
            response = requests.get(url, stream=True, timeout=60)
        except requests.RequestException as e:
            print(f"  {name}: request failed — {e}")
            return False

        if response.status_code == 404:
            print(f"  {name}: not found (404)")
            return False

        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        received = 0
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
                received += len(chunk)
                if total:
                    pct = 100 * received / total
                    mb = received / 1_048_576
                    print(f"\r    {pct:5.1f}%  {mb:.1f} MB", end="", flush=True)
        print()

        congress_dir.mkdir(exist_ok=True)
        print(f"  {name}: extracting…")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(congress_dir)
        zip_path.unlink()

        shp_files = list(congress_dir.rglob("*.shp"))
        print(f"  {name}: done ({len(shp_files)} .shp file(s))")
        return True

    return (download_congress,)


@app.cell
def _(ELECTION_TO_CONGRESS, data_dir, download_congress):
    data_dir.mkdir(parents=True, exist_ok=True)

    unique_congresses = sorted(set(ELECTION_TO_CONGRESS.values()))
    print(f"Output: {data_dir}")
    print(f"Need {len(unique_congresses)} unique Congress boundary sets: {unique_congresses}")

    downloaded: dict[int, bool] = {}
    for _congress_num in unique_congresses:
        downloaded[_congress_num] = download_congress(_congress_num, data_dir)
    return (downloaded,)


@app.cell
def _(ELECTION_TO_CONGRESS, data_dir, downloaded: dict[int, bool]):
    actual_mapping: dict[int, int] = {}
    for _year, _congress in sorted(ELECTION_TO_CONGRESS.items()):
        if downloaded.get(_congress):
            actual_mapping[_year] = _congress
        else:
            _fallback = next(
                (c for c in range(_congress - 1, 0, -1) if downloaded.get(c)),
                None,
            )
            if _fallback:
                actual_mapping[_year] = _fallback
                print(f"Warning: Congress {_congress} unavailable, using {_fallback} for {_year}")
            else:
                print(f"Error: no boundary data found for {_year} election", file=sys.stderr)

    _mapping_path = data_dir / "election_congress_mapping.json"
    _mapping_path.write_text(
        json.dumps(
            {
                "description": (
                    "Maps election years to the Congress whose district boundaries were used. "
                    "Source: https://cdmaps.polisci.ucla.edu/"
                ),
                "election_to_congress": {str(k): v for k, v in sorted(actual_mapping.items())},
            },
            indent=2,
        )
    )
    print(f"Mapping written to {_mapping_path}")
    print("Done.")
    return


@app.cell
def _():
    STATE_NAME_TO_ABBR = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY",
    }
    return (STATE_NAME_TO_ABBR,)


@app.cell
def _():
    VIEWPORT_W = 800
    VIEWPORT_H = 600
    PADDING = 20
    PAD = 8  # SVG units of breathing room around tight viewbox bbox

    coord_re = re.compile(r"(\d+\.\d+),(\d+\.\d+)")

    # Post-projection coordinate clips for viewbox computation.
    # Exclude outlier island chains that pass the viewport bounds filter but
    # should not drive the bounding box (e.g. HI's northwestern chain).
    CLIP: dict[str, dict[str, float]] = {
        "HI": {"x_min": 200, "y_min": 150},
    }

    def compute_viewboxes(districts_by_congress: dict, state_abbr: str) -> dict:
        clip = CLIP.get(state_abbr, {})
        x_min_clip = clip.get("x_min", 0)
        y_min_clip = clip.get("y_min", 0)
        viewbox_by_congress: dict[str, str] = {}
        for congress_num, districts in districts_by_congress.items():
            xs: list[float] = []
            ys: list[float] = []
            for path_d in districts.values():
                for m in coord_re.finditer(path_d):
                    x, y = float(m.group(1)), float(m.group(2))
                    if x_min_clip <= x <= VIEWPORT_W and y_min_clip <= y <= VIEWPORT_H:
                        xs.append(x)
                        ys.append(y)
            if xs:
                vb_x = min(xs) - PAD
                vb_y = min(ys) - PAD
                vb_w = max(xs) - min(xs) + 2 * PAD
                vb_h = max(ys) - min(ys) + 2 * PAD
                viewbox_by_congress[congress_num] = f"{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}"
        return viewbox_by_congress

    def simplify_tol(minx, miny, maxx, maxy) -> float:
        """Tolerance targeting ~1.5 SVG pixels for this state's projection scale."""
        cy = (miny + maxy) / 2
        lon_scale = math.cos(math.radians(cy))
        w = (maxx - minx) * lon_scale
        h = maxy - miny
        avail_w = VIEWPORT_W - 2 * PADDING
        avail_h = VIEWPORT_H - 2 * PADDING
        px_per_deg = min(avail_w / max(w, 1e-9), avail_h / max(h, 1e-9))
        return min(max(1.5 / max(px_per_deg, 1.0), 0.001), 0.5)

    # Per-state geographic bounds overrides.
    # Clamps the bounding box used by make_projector and simplify_tol so that remote
    # island chains don't skew the projection scale or simplification tolerance.
    # Format: (lon_min, lat_min, lon_max, lat_max), use None to leave a side unclamped.
    _BOUNDS_OVERRIDE: dict[str, tuple[float | None, float | None, float | None, float | None]] = {
        # Hawaii: exclude the Northwestern Hawaiian Islands chain (Nihoa, Midway, etc.),
        # which span to 28°N and -177°W, tripling the effective geographic area.
        # Keep only the main inhabited island chain (Niihau eastward, south of 23.5°N).
        "HI": (-162.0, None, None, 23.5),
    }

    def display_bounds(state_gdf, state_abbr: str = ""):
        """Bounding box for projection, handling antimeridian-crossing states.

        If the total bounds span > 180° of longitude (e.g. Alaska's Aleutian Islands
        wrapping past 180°), decompose each geometry into its constituent polygons and
        keep only those whose centroid is in the western hemisphere (lon < 0), giving
        a tight bbox around the mainland rather than the full globe width.

        Per-state overrides in _BOUNDS_OVERRIDE further clamp states whose remote island
        chains would otherwise skew the projection scale and simplification tolerance.
        """
        from shapely.ops import unary_union
        minx, miny, maxx, maxy = state_gdf.total_bounds
        if maxx - minx > 180:
            western = []
            for geom in state_gdf.geometry:
                polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
                western.extend(p for p in polys if p.centroid.x < 0)
            if western:
                b = unary_union(western).bounds
                minx, maxx = b[0], b[2]
        override = _BOUNDS_OVERRIDE.get(state_abbr, (None, None, None, None))
        if override[0] is not None: minx = max(minx, override[0])
        if override[1] is not None: miny = max(miny, override[1])
        if override[2] is not None: maxx = min(maxx, override[2])
        if override[3] is not None: maxy = min(maxy, override[3])
        return minx, miny, maxx, maxy

    def make_projector(minx, miny, maxx, maxy):
        """Equirectangular projection normalized to the viewport, corrected for latitude."""
        cy = (miny + maxy) / 2
        lon_scale = math.cos(math.radians(cy))
        w = (maxx - minx) * lon_scale
        h = maxy - miny
        avail_w = VIEWPORT_W - 2 * PADDING
        avail_h = VIEWPORT_H - 2 * PADDING
        scale = min(avail_w / max(w, 1e-9), avail_h / max(h, 1e-9))
        x_off = PADDING + (avail_w - w * scale) / 2
        y_off = PADDING + (avail_h - h * scale) / 2

        def project(lon, lat):
            return (
                x_off + (lon - minx) * lon_scale * scale,
                y_off + (maxy - lat) * scale,  # flip Y: lat increases up, SVG Y increases down
            )
        return project

    def ring_to_svg(coords, proj):
        pts = [proj(x, y) for x, y in list(coords)[:-1]]  # drop closing duplicate
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"

    def geom_to_svg(geom, proj):
        if geom.geom_type == "Polygon":
            parts = [ring_to_svg(geom.exterior.coords, proj)]
            parts += [ring_to_svg(h.coords, proj) for h in geom.interiors]
            return " ".join(parts)
        elif geom.geom_type == "MultiPolygon":
            return " ".join(geom_to_svg(p, proj) for p in geom.geoms)
        return ""

    return compute_viewboxes, display_bounds, geom_to_svg, make_projector, simplify_tol


@app.cell
def _(ELECTION_TO_CONGRESS, STATE_NAME_TO_ABBR, compute_viewboxes, data_dir, display_bounds, geom_to_svg, make_projector, simplify_tol):
    svg_dir = data_dir.parent / "district_paths"
    svg_dir.mkdir(exist_ok=True)

    _congress_to_years: dict[int, list[int]] = {}
    for _yr, _c in ELECTION_TO_CONGRESS.items():
        _congress_to_years.setdefault(_c, []).append(_yr)

    _all_congresses = sorted(set(ELECTION_TO_CONGRESS.values()))

    def build_state_file(state_name: str, state_abbr: str) -> None:
        out_path = svg_dir / f"{state_abbr}.json"
        if out_path.exists():
            print(f"  {state_abbr}: already exists, skipping")
            return

        districts_by_congress: dict[str, dict[str, str]] = {}
        year_to_congress_key: dict[int, int] = {}
        prev_key: int | None = None

        for congress_num in _all_congresses:
            shp_path = data_dir / f"districts{congress_num:03d}" / f"districts{congress_num:03d}.shp"
            if not shp_path.exists():
                for yr in _congress_to_years.get(congress_num, []):
                    if prev_key is not None:
                        year_to_congress_key[yr] = prev_key
                continue

            gdf = gpd.read_file(shp_path)
            state_gdf = gdf[gdf["STATENAME"] == state_name]
            if state_gdf.empty:
                continue

            # Boundaries are new for this state if any district first appeared in this congress.
            has_new = (state_gdf["STARTCONG"].astype(int) == congress_num).any()
            if not has_new and prev_key is not None:
                for yr in _congress_to_years.get(congress_num, []):
                    year_to_congress_key[yr] = prev_key
                continue

            bounds = display_bounds(state_gdf, state_abbr)
            proj = make_projector(*bounds)
            tol = simplify_tol(*bounds)
            paths: dict[str, str] = {}
            for _, row in state_gdf.iterrows():
                d_key = "AL" if int(float(row["DISTRICT"])) == 0 else str(int(float(row["DISTRICT"])))
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                paths[d_key] = geom_to_svg(geom.simplify(tol, preserve_topology=True), proj)

            districts_by_congress[str(congress_num)] = paths
            prev_key = congress_num
            for yr in _congress_to_years.get(congress_num, []):
                year_to_congress_key[yr] = congress_num

        if not districts_by_congress:
            print(f"  {state_abbr}: no data found")
            return

        viewbox_by_congress = compute_viewboxes(districts_by_congress, state_abbr)
        out_path.write_text(json.dumps({
            "yearToCongress": {str(k): v for k, v in sorted(year_to_congress_key.items())},
            "districtsByCongress": districts_by_congress,
            "viewboxByCongress": viewbox_by_congress,
        }))
        n = len(districts_by_congress)
        print(f"  {state_abbr}: {n} unique boundary set(s)")

    for _state_name, _state_abbr in STATE_NAME_TO_ABBR.items():
        build_state_file(_state_name, _state_abbr)

    return (svg_dir,)


if __name__ == "__main__":
    app.run()
