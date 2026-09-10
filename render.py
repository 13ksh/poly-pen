"""SVG line renderer for the Poly Pen preview."""

from __future__ import annotations

from glyph import UPM, has_char
from lowpoly import CREAM, STYLES, facet_glyph_styled


def _fmt(value: float) -> str:
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _path(coords: tuple[tuple[float, float], ...], dx: float, dy: float, scale: float) -> str:
    parts: list[str] = []
    for i, (x, y) in enumerate(coords):
        px = dx + x * scale
        py = dy - y * scale
        cmd = "M" if i == 0 else "L"
        parts.append(f"{cmd} {_fmt(px)} {_fmt(py)}")
    parts.append("Z")
    return " ".join(parts)


def render_line_svg(
    text: str,
    *,
    style: str = "ink",
    density: float = 0.5,
    font_size: float = 180.0,
) -> str:
    if style not in STYLES:
        style = "ink"
    spec = STYLES[style]
    scale = font_size / UPM
    margin = font_size * 0.22
    cursor = margin
    paths: list[str] = []
    missing: list[str] = []
    baseline = margin + font_size * 0.82
    height = margin + font_size * 1.15
    for char in text:
        if char == " ":
            cursor += font_size * 0.32
            continue
        if not has_char(char):
            missing.append(char)
            cursor += font_size * 0.42
            continue
        faces, advance = facet_glyph_styled(char, style, density)
        for coords, fill in faces:
            d = _path(coords, cursor, baseline, scale)
            if spec["hairline"]:
                stroke = f'stroke="{CREAM}" stroke-width="{_fmt(max(0.7, font_size * 0.006))}" stroke-linejoin="round"'
            else:
                stroke = 'stroke="none"'
            paths.append(f'<path d="{d}" fill="{fill}" {stroke}/>')
        cursor += max(advance * scale, font_size * 0.18)
    width = max(cursor + margin, font_size)
    body = "\n  ".join(paths) if paths else ""
    note = ""
    if missing:
        uniq = "".join(dict.fromkeys(missing))
        note = f"\n  <!-- missing in Poly Pen: {uniq} -->"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_fmt(width)} {_fmt(height)}" '
        f'width="{_fmt(width)}" height="{_fmt(height)}" role="img">\n'
        f'  <rect width="100%" height="100%" fill="{CREAM}"/>'
        f"{note}\n  {body}\n"
        f"</svg>\n"
    )
