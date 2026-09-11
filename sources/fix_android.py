"""Make Poly Pen tables match what Android / Samsung loaders expect.

Does not impersonate Monotype or Samsung as the vendor.
Preserves Regular vs Bold from the filename (or an explicit style).
"""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont, newTable

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
# Latin 1252 + Korean 949, same bits Nanum Pen Script uses.
CODEPAGE_LATIN_KR = 524289

STYLES = {
    "Regular": {
        "weight": 400,
        "macStyle": 0,
        "fsSelection": 0x00C0,
        "styleName": "Regular",
        "psName": "PolyPen-Regular",
        "fullName": "Poly Pen Regular",
        "unique": "1.000;PPEN;PolyPen-Regular",
        "panoseWeight": 5,
    },
    "Bold": {
        "weight": 700,
        "macStyle": 1,
        "fsSelection": 0x00A0,
        "styleName": "Bold",
        "psName": "PolyPen-Bold",
        "fullName": "Poly Pen Bold",
        "unique": "1.000;PPEN;PolyPen-Bold",
        "panoseWeight": 8,
    },
}


def detect_style(path: Path, font: TTFont | None = None) -> str:
    name = path.name.lower()
    if "bold" in name:
        return "Bold"
    if font is not None:
        weight = int(getattr(font["OS/2"], "usWeightClass", 400) or 400)
        if weight >= 600:
            return "Bold"
        style = font["name"].getDebugName(2) or ""
        if style.lower() == "bold":
            return "Bold"
    return "Regular"


def fix_font(path: Path = FONT, style: str | None = None) -> Path:
    font = TTFont(str(path), recalcBBoxes=True, recalcTimestamp=True)
    if style is None:
        style = detect_style(path, font)
    spec = STYLES[style]
    os2 = font["OS/2"]
    os2.version = 4
    os2.fsType = 0
    os2.fsSelection = int(spec["fsSelection"])
    os2.achVendID = "PPEN"
    os2.usWeightClass = int(spec["weight"])
    os2.usWidthClass = 5
    os2.usDefaultChar = 0
    os2.usBreakChar = 32
    os2.usMaxContext = 1
    os2.ulCodePageRange1 = CODEPAGE_LATIN_KR
    os2.recalcCodePageRanges(font)
    os2.ulCodePageRange1 |= 1  # keep 1252 even if recalc drops it
    os2.ulCodePageRange1 |= 1 << 19  # CP949
    os2.updateFirstAndLastCharIndex(font)
    try:
        os2.panose.bWeight = int(spec["panoseWeight"])
    except Exception:
        pass

    nam = font["name"]
    english = {
        0: nam.getDebugName(0) or "",
        1: "Poly Pen",
        2: spec["styleName"],
        3: spec["unique"],
        4: spec["fullName"],
        5: "Version 1.000",
        6: spec["psName"],
        8: "The Poly Pen Project Authors",
        9: "The Poly Pen Project Authors",
        11: "https://github.com/13ksh/poly-pen",
        12: "https://github.com/13ksh/poly-pen",
        13: nam.getDebugName(13) or "",
        14: "https://openfontlicense.org",
        16: "Poly Pen",
        17: spec["styleName"],
    }
    keep = [r for r in nam.names if r.nameID not in english]
    nam.names = keep
    for nid, value in english.items():
        if not value:
            continue
        nam.setName(value, nid, 1, 0, 0)
        nam.setName(value, nid, 3, 1, 0x409)
        nam.setName(value, nid, 3, 1, 0x412)

    if "DSIG" in font:
        del font["DSIG"]
    dsig = newTable("DSIG")
    dsig.ulVersion = 1
    dsig.usFlag = 0
    dsig.usNumSigs = 0
    dsig.signatureRecords = []
    font["DSIG"] = dsig

    gasp = newTable("gasp")
    gasp.gaspRange = {8: 10, 65535: 15}
    font["gasp"] = gasp

    font["head"].macStyle = int(spec["macStyle"])
    font["head"].lowestRecPPEM = 8
    font["OS/2"].fsSelection = int(spec["fsSelection"])
    font.save(str(path))
    return path


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else FONT
    out = fix_font(target)
    print(f"fixed {out} ({out.stat().st_size} bytes)")
