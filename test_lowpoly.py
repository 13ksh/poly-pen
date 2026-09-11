import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "sources"))

from glyph import FONT_PATH, glyph_geometry, has_char
from lowpoly import STYLES, facet_glyph_styled
from render import render_line_svg


def test_source_is_nanum() -> None:
    assert FONT_PATH.name.startswith("NanumPen")
    assert FONT_PATH.parent.name == "nanum"
    assert has_char("한")
    assert has_char("글")
    geom, advance = glyph_geometry("한")
    assert geom is not None and not geom.is_empty
    assert advance > 100


def test_full_hangul_slot() -> None:
    assert has_char("힣")


def test_facets_cover_glyph() -> None:
    faces, advance = facet_glyph_styled("한", "ink", 0.5)
    assert advance > 100
    assert len(faces) >= 8


def test_svg_contains_paths() -> None:
    svg = render_line_svg("한글", style="ink", density=0.5, font_size=160)
    assert svg.startswith("<svg")
    assert "<path" in svg
    for style in STYLES:
        out = render_line_svg("한글", style=style, density=0.4)
        assert "<path" in out


def test_ofl_says_nanum_fork() -> None:
    text = (ROOT / "OFL.txt").read_text(encoding="utf-8")
    assert "Poly Pen is a fork of Nanum Pen Script" in text
    assert "Reserved Font Name" in text
    assert "does not use the reserved names Nanum or NanumPen" in text
    assert "https://github.com/13ksh/poly-pen" in text


def test_pipeline_scripts_live_in_sources() -> None:
    folder = ROOT / "sources"
    for name in (
        "build.sh",
        "build_font.py",
        "glyph.py",
        "lowpoly.py",
        "glyph_coverage.py",
        "render.py",
        "styles.py",
        "config.yaml",
        "README.md",
    ):
        assert (folder / name).is_file(), name
    readme = (folder / "README.md").read_text(encoding="utf-8")
    assert "glyph.py" in readme
    assert "lowpoly.py" in readme
    assert "build_font.py" in readme
    assert (folder / "make_samsung.py").is_file()


def test_bold_outlines_are_thicker() -> None:
    from lowpoly import font_polys

    thin, _ = font_polys("한", expand=0.0)
    fat, _ = font_polys("한", expand=22.0)
    a0 = sum(poly.area for poly in thin)
    a1 = sum(poly.area for poly in fat)
    assert a0 > 0
    assert a1 > a0 * 1.15
    latin_thin, _ = font_polys("B", expand=0.0)
    latin_fat, _ = font_polys("B", expand=22.0)
    assert sum(poly.area for poly in latin_fat) > sum(poly.area for poly in latin_thin)
    digit_thin, _ = font_polys("8", expand=0.0)
    digit_fat, _ = font_polys("8", expand=22.0)
    assert sum(poly.area for poly in digit_fat) > sum(poly.area for poly in digit_thin)
    hair, _ = font_polys("한", expand=-8.0)
    a_thin = sum(poly.area for poly in hair)
    assert 0 < a_thin < a0


def test_samsung_sans_slot_copy() -> None:
    from make_samsung import SLOT, main as make_samsung

    path = make_samsung()
    assert path == SLOT
    assert path.name == "Samsungsans.ttf"
    src = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
    assert path.read_bytes() == src.read_bytes()
    from fontTools.ttLib import TTFont

    font = TTFont(str(src))
    assert font["name"].getDebugName(3).startswith("1.000;PPEN;")
    assert font["OS/2"].version >= 4
    assert font["OS/2"].usWeightClass == 400
    font.close()
    bold = ROOT / "fonts" / "ttf" / "PolyPen-Bold.ttf"
    if bold.exists():
        from make_samsung import BOLD_SLOT

        assert BOLD_SLOT.exists()
        assert BOLD_SLOT.read_bytes() == bold.read_bytes()
        bfont = TTFont(str(bold))
        assert bfont["OS/2"].usWeightClass == 700
        assert bfont["name"].getDebugName(2) == "Bold"
        assert bfont["name"].getDebugName(6) == "PolyPen-Bold"
        assert bfont["head"].macStyle & 1
        bfont.close()


def test_android_fix_keeps_bold_names() -> None:
    from fix_android import STYLES, detect_style

    assert detect_style(ROOT / "fonts" / "ttf" / "PolyPen-Bold.ttf") == "Bold"
    assert detect_style(ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf") == "Regular"
    assert detect_style(ROOT / "fonts" / "ttf" / "PolyPen-ExtraBold.ttf") == "ExtraBold"
    assert detect_style(ROOT / "fonts" / "ttf" / "PolyPen-ExtraLight.ttf") == "ExtraLight"
    assert STYLES["Thin"]["weight"] == 100
    assert STYLES["Black"]["weight"] == 900
    assert STYLES["Bold"]["weight"] == 700
    assert STYLES["Regular"]["weight"] == 400


if __name__ == "__main__":
    test_source_is_nanum()
    test_full_hangul_slot()
    test_facets_cover_glyph()
    test_svg_contains_paths()
    test_ofl_says_nanum_fork()
    test_pipeline_scripts_live_in_sources()
    test_bold_outlines_are_thicker()
    test_samsung_sans_slot_copy()
    test_android_fix_keeps_bold_names()
    print("ok")
