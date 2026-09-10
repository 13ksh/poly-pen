"""Render documentation/poly-pen-specimen.png from Poly Pen Regular."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
OUT = Path(__file__).resolve().parent / "poly-pen-specimen.png"


def main() -> None:
    font_title = ImageFont.truetype(str(FONT), 168)
    font_line = ImageFont.truetype(str(FONT), 88)
    font_caption = ImageFont.truetype(str(FONT), 28)
    width, height = 1600, 720
    image = Image.new("RGB", (width, height), "#dceaf8")
    draw = ImageDraw.Draw(image)
    draw.text((72, 88), "Poly Pen", font=font_title, fill="#161412")
    draw.text((72, 320), "가나다라 abcd 1234", font=font_line, fill="#161412")
    draw.text(
        (72, 500),
        "A fork of Nanum Pen Script  ·  Nanum Pen Script 포크  ·  Regular",
        font=font_caption,
        fill="#6d675c",
    )
    draw.rectangle((72, 640, 280, 644), fill="#161412")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
