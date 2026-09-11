"""Make Poly Pen tables match what Android / Samsung loaders expect.

Does not impersonate Monotype or Samsung as the vendor.
"""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont, newTable

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
UNIQUE = "1.000;PPEN;PolyPen-Regular"
# Latin 1252 + Korean 949, same bits Nanum Pen Script uses.
CODEPAGE_LATIN_KR = 524289


def fix_font(path: Path = FONT) -> Path:
    font = TTFont(str(path), recalcBBoxes=True, recalcTimestamp=True)
    os2 = font["OS/2"]
    os2.version = 4
    os2.fsType = 0
    os2.fsSelection = 0x00C0
    os2.achVendID = "PPEN"
    os2.usWeightClass = 400
    os2.usWidthClass = 5
    os2.usDefaultChar = 0
    os2.usBreakChar = 32
    os2.usMaxContext = 1
    os2.ulCodePageRange1 = CODEPAGE_LATIN_KR
    os2.recalcCodePageRanges(font)
    os2.ulCodePageRange1 |= 1  # keep 1252 even if recalc drops it
    os2.ulCodePageRange1 |= 1 << 19  # CP949
    os2.updateFirstAndLastCharIndex(font)

    nam = font["name"]
    english = {
        0: nam.getDebugName(0) or "",
        1: "Poly Pen",
        2: "Regular",
        3: UNIQUE,
        4: "Poly Pen Regular",
        5: "Version 1.000",
        6: "PolyPen-Regular",
        8: "The Poly Pen Project Authors",
        9: "The Poly Pen Project Authors",
        11: "https://github.com/13ksh/poly-pen",
        12: "https://github.com/13ksh/poly-pen",
        13: nam.getDebugName(13) or "",
        14: "https://openfontlicense.org",
        16: "Poly Pen",
        17: "Regular",
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

    font["head"].macStyle = 0
    font["head"].lowestRecPPEM = 8
    font["OS/2"].fsSelection = 0x00C0
    font.save(str(path))
    return path


if __name__ == "__main__":
    out = fix_font()
    print(f"fixed {out} ({out.stat().st_size} bytes)")
