"""Build Poly Pen: low-poly Nanum Pen Script as a TrueType file."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampNow
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from shapely.geometry import Polygon
from shapely.geometry.polygon import LinearRing

from glyph import UPM, cmap, glyph_geometry, source_font
from lowpoly import font_polys
from styles import STYLES

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = Path.home() / "Desktop"
DOWNLOADS = Path.home() / "Downloads"
ARTIFACTS = Path("/opt/cursor/artifacts")
FAMILY = "Poly Pen"
REPO_URL = "https://github.com/13ksh/poly-pen"
SIMPLIFY = 0.8
INSET = 0.0
_EXPAND = 0.0
ZIP_NAME = "PolyPen-100-900.zip"


def glyph_name(code: int) -> str:
    if code < 0x10000:
        return f"uni{code:04X}"
    return f"u{code:05X}"


def usable_code(code: int) -> bool:
    if 0xD800 <= code <= 0xDFFF:
        return False
    if code in (0xFEFF, 0xFFFE, 0xFFFF):
        return False
    return True


def collect_codepoints() -> list[int]:
    return sorted(code for code in cmap() if usable_code(code))


def _signed_area(points: list[tuple[int, int]]) -> float:
    total = 0.0
    count = len(points)
    for i, (x, y) in enumerate(points):
        nx, ny = points[(i + 1) % count]
        total += x * ny - nx * y
    return total * 0.5


def _ring_points(ring: LinearRing, clockwise: bool) -> list[tuple[int, int]]:
    raw = [(int(round(x)), int(round(y))) for x, y in ring.coords]
    cleaned: list[tuple[int, int]] = []
    for point in raw:
        if not cleaned or cleaned[-1] != point:
            cleaned.append(point)
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
        cleaned.pop()
    if len(cleaned) < 3:
        return []
    ccw = _signed_area(cleaned) > 0
    if clockwise == ccw:
        cleaned.reverse()
    return cleaned


def contours_from_polys(polys: list[Polygon]) -> list[list[tuple[int, int]]]:
    contours: list[list[tuple[int, int]]] = []
    for poly in polys:
        try:
            simple = poly.simplify(SIMPLIFY, preserve_topology=True)
        except Exception:
            simple = poly
        if simple.is_empty:
            continue
        if simple.geom_type == "Polygon":
            parts = [simple]
        elif simple.geom_type == "MultiPolygon":
            parts = [item for item in simple.geoms if item.geom_type == "Polygon"]
        else:
            continue
        for part in parts:
            outer = _ring_points(part.exterior, clockwise=True)
            if len(outer) >= 3:
                contours.append(outer)
            for hole in part.interiors:
                inner = _ring_points(hole, clockwise=False)
                if len(inner) >= 3:
                    contours.append(inner)
    return contours


def _glyph_from_contours(contours: list[list[tuple[int, int]]]):
    pen = TTGlyphPen(None)
    for contour in contours:
        pen.moveTo(contour[0])
        for point in contour[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def _reset_font_caches() -> None:
    source_font.cache_clear()
    cmap.cache_clear()
    glyph_geometry.cache_clear()


def _pool_init(expand: float = 0.0) -> None:
    global _EXPAND
    _EXPAND = expand
    _reset_font_caches()
    cmap()


def _worker(code: int) -> tuple[int, float, list[list[tuple[int, int]]]]:
    try:
        polys, advance = font_polys(chr(code), inset=INSET, expand=_EXPAND)
    except Exception:
        return code, 0.0, []
    return code, float(advance), contours_from_polys(polys)


def source_metrics() -> dict:
    font = source_font()
    os2 = font["OS/2"]
    hhea = font["hhea"]
    return {
        "ascent": int(hhea.ascent),
        "descent": int(hhea.descent),
        "lineGap": int(hhea.lineGap),
        "typoAscender": int(os2.sTypoAscender),
        "typoDescender": int(os2.sTypoDescender),
        "typoLineGap": int(os2.sTypoLineGap),
        "winAscent": int(os2.usWinAscent),
        "winDescent": int(os2.usWinDescent),
        "sCapHeight": int(getattr(os2, "sCapHeight", 674) or 674),
        "sxHeight": int(getattr(os2, "sxHeight", 476) or 476),
        "ySubscriptXSize": int(os2.ySubscriptXSize or 650),
        "ySubscriptYSize": int(os2.ySubscriptYSize or 600),
        "ySubscriptXOffset": int(os2.ySubscriptXOffset or 0),
        "ySubscriptYOffset": int(os2.ySubscriptYOffset or 75),
        "ySuperscriptXSize": int(os2.ySuperscriptXSize or 650),
        "ySuperscriptYSize": int(os2.ySuperscriptYSize or 600),
        "ySuperscriptXOffset": int(os2.ySuperscriptXOffset or 0),
        "ySuperscriptYOffset": int(os2.ySuperscriptYOffset or 350),
        "yStrikeoutSize": int(os2.yStrikeoutSize or 50),
        "yStrikeoutPosition": int(os2.yStrikeoutPosition or 300),
        "underlinePosition": int(font["post"].underlinePosition or -260),
        "underlineThickness": int(font["post"].underlineThickness or 58),
        "panose": os2.panose,
        "space": float(font.getGlyphSet()["space"].width) if "space" in font.getGlyphSet() else 250.0,
    }


def assemble_font(
    rows: list[tuple[int, float, list[list[tuple[int, int]]]]],
    dest: Path,
    *,
    style: str = "Regular",
) -> None:
    spec = STYLES[style]
    ps_name = f"PolyPen-{style}"
    weight = int(spec["weight"])
    metrics = source_metrics()
    cmap_out: dict[int, str] = {}
    glyphs: dict = {}
    advances: dict[str, float] = {}

    glyphs[".notdef"] = _glyph_from_contours(_worker(ord("?"))[2])
    advances[".notdef"] = 600
    glyphs[".null"] = _glyph_from_contours([])
    advances[".null"] = 0
    glyphs["space"] = _glyph_from_contours([])
    advances["space"] = metrics["space"]
    cmap_out[0x20] = "space"
    cmap_out[0xA0] = "space"

    for code, advance, contours in rows:
        if code in (0x20, 0xA0):
            advances["space"] = max(advances["space"], advance if advance > 0 else metrics["space"])
            continue
        name = glyph_name(code)
        glyphs[name] = _glyph_from_contours(contours)
        advances[name] = advance if advance > 0 else 250
        cmap_out[code] = name

    order = [".notdef", ".null", "space"] + [
        glyph_name(code) for code, _, _ in sorted(rows, key=lambda item: item[0]) if code not in (0x20, 0xA0)
    ]
    order = [name for name in order if name in glyphs]

    fb = FontBuilder(int(UPM), isTTF=True)
    now = timestampNow()
    fb.setupHead(fontRevision=1.0, lowestRecPPEM=8, created=now, modified=now, macStyle=int(spec["macStyle"]))
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap_out, allowFallback=True)
    fb.setupGlyf(glyphs)
    hmtx = {}
    glyf = fb.font["glyf"]
    for name, width in advances.items():
        glyph = glyf[name]
        lsb = int(getattr(glyph, "xMin", 0) or 0)
        hmtx[name] = (max(int(round(width)), 0), lsb)
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=metrics["ascent"], descent=metrics["descent"], lineGap=metrics["lineGap"])
    fb.setupNameTable(
        {
            "copyright": (
                "Copyright 2026 The Poly Pen Project Authors (https://github.com/13ksh/poly-pen). "
                "Poly Pen is a fork of Nanum Pen Script under the SIL Open Font License 1.1. "
                "Original copyright NHN Corporation / Sandoll Communications Inc."
            ),
            "familyName": FAMILY,
            "styleName": style,
            "uniqueFontIdentifier": f"1.000;PPEN;{ps_name}",
            "fullName": f"{FAMILY} {style}",
            "psName": ps_name,
            "version": "Version 1.000",
            "manufacturer": "The Poly Pen Project Authors",
            "designer": "The Poly Pen Project Authors",
            "description": (
                "Poly Pen is a fork of Nanum Pen Script (a Modified Version under OFL 1.1). "
                "Outlines are faceted into triangles, then touching faces are merged. "
                "Coverage matches the source font. The family name is Poly Pen. "
                "It does not use the reserved names Nanum or NanumPen. "
                "Styles run Thin 100 through Black 900 so apps that request "
                "medium or bold (Discord, YouTube) stay in this family."
            ),
            "vendorURL": REPO_URL,
            "designerURL": REPO_URL,
            "licenseDescription": (
                "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                "This license is available with a FAQ at: https://openfontlicense.org"
            ),
            "licenseInfoURL": "https://openfontlicense.org",
            "typographicFamily": FAMILY,
            "typographicSubfamily": style,
            "sampleText": "가나다라 abcd 1234",
        }
    )
    fb.setupOS2(
        sTypoAscender=metrics["typoAscender"],
        sTypoDescender=metrics["typoDescender"],
        sTypoLineGap=metrics["typoLineGap"],
        usWinAscent=metrics["winAscent"],
        usWinDescent=metrics["winDescent"],
        usWeightClass=weight,
        usWidthClass=5,
        fsSelection=int(spec["fsSelection"]),
        achVendID="PPEN",
        sCapHeight=metrics["sCapHeight"],
        sxHeight=metrics["sxHeight"],
        fsType=0,
        ySubscriptXSize=metrics["ySubscriptXSize"],
        ySubscriptYSize=metrics["ySubscriptYSize"],
        ySubscriptXOffset=metrics["ySubscriptXOffset"],
        ySubscriptYOffset=metrics["ySubscriptYOffset"],
        ySuperscriptXSize=metrics["ySuperscriptXSize"],
        ySuperscriptYSize=metrics["ySuperscriptYSize"],
        ySuperscriptXOffset=metrics["ySuperscriptXOffset"],
        ySuperscriptYOffset=metrics["ySuperscriptYOffset"],
        yStrikeoutSize=metrics["yStrikeoutSize"],
        yStrikeoutPosition=metrics["yStrikeoutPosition"],
    )
    fb.setupPost(
        keepGlyphNames=False,
        underlinePosition=metrics["underlinePosition"],
        underlineThickness=metrics["underlineThickness"],
    )
    fb.setupDummyDSIG()
    fb.font["OS/2"].panose = metrics["panose"]
    fb.font["OS/2"].recalcCodePageRanges(fb.font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fb.save(dest)


def sanitize_font(path: Path, *, style: str = "Regular") -> Path:
    spec = STYLES[style]
    font = TTFont(path, recalcBBoxes=False, recalcTimestamp=True)
    if "ltag" in font:
        del font["ltag"]
    metrics = source_metrics()
    os2 = font["OS/2"]
    os2.ySubscriptXSize = metrics["ySubscriptXSize"]
    os2.ySubscriptYSize = metrics["ySubscriptYSize"]
    os2.ySubscriptXOffset = metrics["ySubscriptXOffset"]
    os2.ySubscriptYOffset = metrics["ySubscriptYOffset"]
    os2.ySuperscriptXSize = metrics["ySuperscriptXSize"]
    os2.ySuperscriptYSize = metrics["ySuperscriptYSize"]
    os2.ySuperscriptXOffset = metrics["ySuperscriptXOffset"]
    os2.ySuperscriptYOffset = metrics["ySuperscriptYOffset"]
    os2.yStrikeoutSize = metrics["yStrikeoutSize"]
    os2.yStrikeoutPosition = metrics["yStrikeoutPosition"]
    os2.panose = metrics["panose"]
    os2.usWeightClass = int(spec["weight"])
    os2.fsSelection = int(spec["fsSelection"])
    os2.achVendID = "PPEN"
    os2.fsType = 0
    os2.version = 4
    os2.usMaxContext = 1
    os2.recalcCodePageRanges(font)
    os2.ulCodePageRange1 |= 1
    os2.ulCodePageRange1 |= 1 << 19
    os2.updateFirstAndLastCharIndex(font)
    post = font["post"]
    post.formatType = 3.0
    post.extraNames = []
    post.mapping = {}
    post.underlinePosition = metrics["underlinePosition"]
    post.underlineThickness = metrics["underlineThickness"]
    gasp = newTable("gasp")
    gasp.gaspRange = {8: 10, 65535: 15}
    font["gasp"] = gasp
    dsig = newTable("DSIG")
    dsig.ulVersion = 1
    dsig.usFlag = 0
    dsig.usNumSigs = 0
    dsig.signatureRecords = []
    font["DSIG"] = dsig
    font["head"].lowestRecPPEM = 8
    font["head"].macStyle = int(spec["macStyle"])
    font["head"].modified = timestampNow()
    font.save(path)
    return path


def copy_outputs(master: Path) -> list[Path]:
    written = [master]
    name = master.name
    for dest in (DESKTOP / name, DOWNLOADS / name, ARTIFACTS / name):
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.resolve() == master.resolve():
                continue
            shutil.copy2(master, dest)
            written.append(dest)
        except OSError as exc:
            print(f"skip {dest}: {exc}", flush=True)
    return written


def build(
    codes: list[int] | None = None,
    workers: int | None = None,
    dest: Path | None = None,
    *,
    style: str = "Regular",
) -> Path:
    global _EXPAND
    spec = STYLES[style]
    dest = dest or (ROOT / "fonts" / "ttf" / str(spec["filename"]))
    dest.parent.mkdir(parents=True, exist_ok=True)
    codes = list(codes) if codes is not None else collect_codepoints()
    _EXPAND = float(spec["expand"])
    _reset_font_caches()
    workers = max(1, workers or (os.cpu_count() or 2))
    started = time.time()
    rows: list[tuple[int, float, list[list[tuple[int, int]]]]] = []
    print(f"faceting {style} {len(codes)} glyphs expand={_EXPAND} workers={workers}", flush=True)
    if workers == 1 or len(codes) < 8:
        for i, code in enumerate(codes, start=1):
            rows.append(_worker(code))
            if i == 1 or i % 500 == 0 or i == len(codes):
                print(f"facet {i}/{len(codes)}", flush=True)
    else:
        ctx = mp.get_context("fork")
        with ctx.Pool(processes=workers, initializer=_pool_init, initargs=(_EXPAND,)) as pool:
            for i, row in enumerate(pool.imap(_worker, codes, chunksize=16), start=1):
                rows.append(row)
                if i == 1 or i % 500 == 0 or i == len(codes):
                    print(f"facet {i}/{len(codes)}", flush=True)
    empty = sum(1 for _, _, contours in rows if not contours)
    print(f"compiling TrueType {style} ({empty} empty outlines)", flush=True)
    assemble_font(rows, dest, style=style)
    sanitize_font(dest, style=style)
    from fix_android import fix_font

    fix_font(dest, style=style)
    copies = copy_outputs(dest)
    elapsed = round(time.time() - started, 1)
    print(f"wrote {dest} ({dest.stat().st_size} bytes) in {elapsed}s", flush=True)
    for path in copies:
        print(f"copy {path}", flush=True)
    return dest


def zip_family() -> Path:
    dest = ROOT / "downloads" / ZIP_NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    ofl = ROOT / "OFL.txt"
    paths = []
    for spec in STYLES.values():
        path = ROOT / "fonts" / "ttf" / str(spec["filename"])
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}")
        paths.append(path)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in paths:
            archive.write(path, arcname=path.name)
        if ofl.exists():
            archive.write(ofl, arcname="OFL.txt")
    copies = [dest]
    for extra in (DESKTOP / ZIP_NAME, DOWNLOADS / ZIP_NAME, ARTIFACTS / ZIP_NAME):
        try:
            extra.parent.mkdir(parents=True, exist_ok=True)
            if extra.resolve() == dest.resolve():
                continue
            shutil.copy2(dest, extra)
            copies.append(extra)
        except OSError as exc:
            print(f"skip {extra}: {exc}", flush=True)
    print(f"wrote {dest} ({dest.stat().st_size} bytes)", flush=True)
    for path in copies[1:]:
        print(f"copy {path}", flush=True)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Poly Pen (Nanum Pen Script fork)")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--style", choices=tuple(STYLES), default="Regular")
    parser.add_argument("--family", action="store_true", help="Build Thin 100 through Black 900")
    parser.add_argument("--force", action="store_true", help="Rebuild styles that already exist")
    parser.add_argument("--zip-only", action="store_true", help="Zip existing Thin–Black TTFs")
    args = parser.parse_args()
    if args.zip_only:
        zip_family()
        return
    codes = collect_codepoints()
    if args.limit:
        codes = codes[: args.limit]
    styles = list(STYLES) if args.family else [args.style]
    for style in styles:
        dest = args.out if len(styles) == 1 else None
        existing = ROOT / "fonts" / "ttf" / str(STYLES[style]["filename"])
        if dest is None and existing.exists() and args.family and not args.force:
            print(f"skip existing {existing}", flush=True)
            continue
        build(codes=codes, workers=args.workers or None, dest=dest, style=style)
    if args.family or args.style:
        try:
            zip_family()
        except FileNotFoundError as exc:
            print(f"skip zip: {exc}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
