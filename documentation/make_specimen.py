"""Render documentation/poly-pen-specimen.png from Poly Pen Regular and Bold."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REGULAR = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
BOLD = ROOT / "fonts" / "ttf" / "PolyPen-Bold.ttf"
OUT = Path(__file__).resolve().parent / "poly-pen-specimen.png"


def main() -> None:
    font_title = ImageFont.truetype(str(REGULAR), 168)
    font_line = ImageFont.truetype(str(REGULAR), 88)
    font_bold = ImageFont.truetype(str(BOLD if BOLD.exists() else REGULAR), 88)
    font_caption = ImageFont.truetype(str(REGULAR), 28)
    width, height = 1600, 820
    image = Image.new("RGB", (width, height), "#dceaf8")
    draw = ImageDraw.Draw(image)
    draw.text((72, 72), "Poly Pen", font=font_title, fill="#161412")
    draw.text((72, 280), "가나다라 abcd 1234", font=font_line, fill="#161412")
    draw.text((72, 400), "가나다라 abcd 1234", font=font_bold, fill="#161412")
    draw.text(
        (72, 560),
        "A fork of Nanum Pen Script  ·  Regular 400 / Bold 700",
        font=font_caption,
        fill="#6d675c",
    )
    draw.rectangle((72, 700, 280, 704), fill="#161412")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
