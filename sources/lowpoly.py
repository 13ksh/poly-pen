"""Facet Nanum Pen Script outlines into shaded triangles."""

from __future__ import annotations

import hashlib
import math
from functools import lru_cache

from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

from glyph import glyph_geometry, iter_polys

CREAM = "#f4eee4"
STYLES = {
    "ink": {
        "label": "면",
        "simplify": 28.0,
        "max_seg": 96.0,
        "inset": 0.0,
        "hairline": False,
        "lo": 16,
        "hi": 124,
        "contrast": 1.65,
    },
    "chunky": {
        "label": "큰 조각",
        "simplify": 42.0,
        "max_seg": 132.0,
        "inset": 0.0,
        "hairline": False,
        "lo": 14,
        "hi": 142,
        "contrast": 2.05,
    },
    "fine": {
        "label": "고운 면",
        "simplify": 16.0,
        "max_seg": 58.0,
        "inset": 0.0,
        "hairline": False,
        "lo": 18,
        "hi": 112,
        "contrast": 1.35,
    },
}


def resample_ring(coords, max_seg: float) -> list[tuple[float, float]]:
    pts = list(coords)
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    out: list[tuple[float, float]] = []
    count = len(pts)
    if count < 3:
        return pts
    for i in range(count):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % count]
        dx, dy = x1 - x0, y1 - y0
        dist = math.hypot(dx, dy)
        steps = max(1, int(math.ceil(dist / max(max_seg, 1.0))))
        for step in range(steps):
            t = step / steps
            out.append((x0 + dx * t, y0 + dy * t))
    if out:
        out.append(out[0])
    return out


def prepare_polygon(poly: Polygon, simplify: float, max_seg: float) -> list[Polygon]:
    simple = poly.simplify(simplify, preserve_topology=True)
    parts: list[Polygon] = []
    for item in iter_polys(simple):
        exterior = resample_ring(item.exterior.coords, max_seg)
        holes = [resample_ring(hole.coords, max_seg) for hole in item.interiors]
        try:
            rebuilt = Polygon(exterior, holes)
        except Exception:
            parts.append(item)
            continue
        if rebuilt.is_empty:
            continue
        if not rebuilt.is_valid:
            rebuilt = make_valid(rebuilt)
        parts.extend(iter_polys(rebuilt))
    return parts


def triangulate(geom, simplify: float, max_seg: float) -> list[Polygon]:
    faces: list[Polygon] = []
    for poly in iter_polys(geom):
        for part in prepare_polygon(poly, simplify, max_seg):
            try:
                tris = constrained_delaunay_triangles(part)
            except Exception:
                continue
            faces.extend(iter_polys(tris))
    return faces


def shade_face(tri: Polygon, lo: int, hi: int, contrast: float) -> str:
    """Per-face tilt. Thin pen strokes have almost no ridge, so light the face itself."""
    pts = list(tri.exterior.coords)[:3]
    if len(pts) < 3:
        return "#222222"
    cx = (pts[0][0] + pts[1][0] + pts[2][0]) / 3.0
    cy = (pts[0][1] + pts[1][1] + pts[2][1]) / 3.0
    key = hashlib.md5(f"{cx:.1f},{cy:.1f}".encode()).digest()
    nx = (key[0] / 255.0 - 0.5) * contrast
    ny = (key[1] / 255.0 - 0.5) * contrast
    nz = 1.0
    mag = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    nx, ny, nz = nx / mag, ny / mag, nz / mag
    lx, ly, lz = -0.45, 0.70, 0.78
    length = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / length, ly / length, lz / length
    diffuse = max(0.0, nx * lx + ny * ly + nz * lz)
    gray = lo + (hi - lo) * (0.12 + 0.88 * diffuse)
    gray += (key[2] / 255.0 - 0.5) * (hi - lo) * 0.12
    value = int(max(lo, min(hi, gray)))
    return f"#{value:02x}{value:02x}{value:02x}"


@lru_cache(maxsize=8192)
def facet_glyph(
    char: str,
    simplify: float,
    max_seg: float,
    inset: float,
    lo: int,
    hi: int,
    contrast: float,
) -> tuple[tuple, float]:
    geom, advance = glyph_geometry(char)
    if geom is None or geom.is_empty:
        return (), advance
    tris = triangulate(geom, simplify, max_seg)
    faces = []
    for tri in tris:
        face = tri
        if inset > 0:
            try:
                face = tri.buffer(-inset)
            except Exception:
                continue
            if face.is_empty:
                continue
        for part in iter_polys(face):
            coords = list(part.exterior.coords)
            if len(coords) < 4:
                continue
            faces.append((tuple((x, y) for x, y in coords), shade_face(part, lo, hi, contrast)))
    return tuple(faces), advance


def font_polys(
    char: str,
    simplify: float = 28.0,
    max_seg: float = 96.0,
    inset: float = 0.0,
    expand: float = 0.0,
) -> tuple[list[Polygon], float]:
    """Low-poly silhouette for TrueType. Touching triangles become one outline."""
    geom, advance = glyph_geometry(char)
    if geom is None or geom.is_empty:
        return [], advance
    if expand > 0:
        try:
            fat = geom.buffer(expand)
            if fat is not None and not fat.is_empty:
                geom = make_valid(fat)
        except Exception:
            pass
        advance = float(advance) + expand * 1.8
    tris = triangulate(geom, simplify, max_seg)
    if not tris:
        return [], advance
    faces: list[Polygon] = list(tris)
    if inset > 0:
        inset_faces: list[Polygon] = []
        for tri in tris:
            try:
                shrunk = tri.buffer(-inset)
            except Exception:
                shrunk = None
            if shrunk is not None and not shrunk.is_empty and shrunk.area >= 4.0:
                inset_faces.extend(iter_polys(shrunk))
            else:
                inset_faces.append(tri)
        faces = inset_faces or list(tris)
    try:
        merged = unary_union(faces)
    except Exception:
        merged = geom
    return iter_polys(merged), advance


def facet_glyph_styled(char: str, style: str, density: float) -> tuple[tuple, float]:
    spec = STYLES[style]
    t = max(0.0, min(1.0, density))
    simplify = spec["simplify"] * (1.55 - 0.9 * t)
    max_seg = spec["max_seg"] * (1.55 - 0.9 * t)
    return facet_glyph(
        char,
        round(simplify, 2),
        round(max_seg, 2),
        spec["inset"],
        spec["lo"],
        spec["hi"],
        spec["contrast"],
    )
