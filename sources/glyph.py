"""Load Nanum Pen Script glyph outlines. Source font by Sandoll / NHN."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "fonts" / "nanum" / "NanumPenScript-Regular.ttf"
UPM = 1000.0


class FlattenPen(BasePen):
    def __init__(self, glyph_set, steps: int = 6) -> None:
        super().__init__(glyph_set)
        self.steps = steps
        self.contours: list[list[tuple[float, float]]] = []
        self._current: list[tuple[float, float]] = []

    def _moveTo(self, pt) -> None:
        self._flush()
        self._current = [pt]

    def _lineTo(self, pt) -> None:
        self._current.append(pt)

    def _curveToOne(self, p1, p2, p3) -> None:
        p0 = self._current[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            u = 1.0 - t
            x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
            y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
            self._current.append((x, y))

    def _qCurveToOne(self, p1, p2) -> None:
        p0 = self._current[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            u = 1.0 - t
            x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
            y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
            self._current.append((x, y))

    def _closePath(self) -> None:
        self._flush()

    def _endPath(self) -> None:
        self._flush()

    def _flush(self) -> None:
        if len(self._current) >= 3:
            self.contours.append(self._current)
        self._current = []


@lru_cache(maxsize=1)
def source_font() -> TTFont:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Missing {FONT_PATH}")
    return TTFont(FONT_PATH)


@lru_cache(maxsize=1)
def cmap() -> dict[int, str]:
    return source_font().getBestCmap() or {}


def has_char(char: str) -> bool:
    return ord(char) in cmap()


def iter_polys(geom: BaseGeometry | None) -> list[Polygon]:
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, (MultiPolygon, GeometryCollection)):
        out: list[Polygon] = []
        for item in geom.geoms:
            out.extend(iter_polys(item))
        return out
    return []


@lru_cache(maxsize=4096)
def glyph_geometry(char: str) -> tuple[BaseGeometry | None, float]:
    font = source_font()
    name = cmap().get(ord(char))
    if name is None:
        return None, 0.0
    glyph_set = font.getGlyphSet()
    pen = FlattenPen(glyph_set, steps=6)
    glyph_set[name].draw(pen)
    advance = float(glyph_set[name].width)
    rings: list[Polygon] = []
    for contour in pen.contours:
        try:
            poly = make_valid(Polygon(contour))
        except Exception:
            continue
        if not poly.is_empty and poly.area > 1e-3:
            rings.append(poly)
    if not rings:
        return None, advance
    rings.sort(key=lambda item: item.area, reverse=True)
    geom: BaseGeometry = rings[0]
    for ring in rings[1:]:
        if geom.contains(ring.representative_point()):
            geom = geom.difference(ring)
        else:
            geom = geom.union(ring)
    geom = make_valid(geom)
    if geom.is_empty:
        return None, advance
    return geom, advance
