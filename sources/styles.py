"""Poly Pen static styles: Thin 100 through Black 900."""

from __future__ import annotations

# Stroke expand is added to Nanum Pen outlines before faceting.
# Regular stays at 0. Lighter weights shrink; heavier weights grow.
STYLES: dict[str, dict] = {
    "Thin": {
        "weight": 100,
        "expand": -8.0,
        "macStyle": 0,
        "fsSelection": 0x0080,
        "filename": "PolyPen-Thin.ttf",
        "panoseWeight": 2,
    },
    "ExtraLight": {
        "weight": 200,
        "expand": -5.0,
        "macStyle": 0,
        "fsSelection": 0x0080,
        "filename": "PolyPen-ExtraLight.ttf",
        "panoseWeight": 3,
    },
    "Light": {
        "weight": 300,
        "expand": -2.5,
        "macStyle": 0,
        "fsSelection": 0x0080,
        "filename": "PolyPen-Light.ttf",
        "panoseWeight": 4,
    },
    "Regular": {
        "weight": 400,
        "expand": 0.0,
        "macStyle": 0,
        "fsSelection": 0x00C0,
        "filename": "PolyPen-Regular.ttf",
        "panoseWeight": 5,
    },
    "Medium": {
        "weight": 500,
        "expand": 8.0,
        "macStyle": 0,
        "fsSelection": 0x0080,
        "filename": "PolyPen-Medium.ttf",
        "panoseWeight": 6,
    },
    "SemiBold": {
        "weight": 600,
        "expand": 15.0,
        "macStyle": 0,
        "fsSelection": 0x0080,
        "filename": "PolyPen-SemiBold.ttf",
        "panoseWeight": 7,
    },
    "Bold": {
        "weight": 700,
        "expand": 22.0,
        "macStyle": 1,
        "fsSelection": 0x00A0,
        "filename": "PolyPen-Bold.ttf",
        "panoseWeight": 8,
    },
    "ExtraBold": {
        "weight": 800,
        "expand": 28.0,
        "macStyle": 1,
        "fsSelection": 0x00A0,
        "filename": "PolyPen-ExtraBold.ttf",
        "panoseWeight": 9,
    },
    "Black": {
        "weight": 900,
        "expand": 34.0,
        "macStyle": 1,
        "fsSelection": 0x00A0,
        "filename": "PolyPen-Black.ttf",
        "panoseWeight": 10,
    },
}

_DETECT = (
    ("extrabold", "ExtraBold"),
    ("semibold", "SemiBold"),
    ("extralight", "ExtraLight"),
    ("thin", "Thin"),
    ("light", "Light"),
    ("medium", "Medium"),
    ("black", "Black"),
    ("bold", "Bold"),
    ("regular", "Regular"),
)

_WEIGHT_TO_STYLE = {int(spec["weight"]): name for name, spec in STYLES.items()}


def detect_style(path, font=None) -> str:
    name = getattr(path, "name", str(path)).lower()
    for needle, style in _DETECT:
        if needle in name:
            return style
    if font is not None:
        try:
            weight = int(getattr(font["OS/2"], "usWeightClass", 400) or 400)
        except Exception:
            weight = 400
        nearest = min(_WEIGHT_TO_STYLE, key=lambda item: abs(item - weight))
        return _WEIGHT_TO_STYLE[nearest]
    return "Regular"
