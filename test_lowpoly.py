from pathlib import Path

from glyph import FONT_PATH, glyph_geometry, has_char
from lowpoly import STYLES, facet_glyph_styled
from render import render_line_svg

ROOT = Path(__file__).resolve().parent


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


if __name__ == "__main__":
    test_source_is_nanum()
    test_full_hangul_slot()
    test_facets_cover_glyph()
    test_svg_contains_paths()
    test_ofl_says_nanum_fork()
    print("ok")
