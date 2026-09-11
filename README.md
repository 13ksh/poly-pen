# Poly Pen

**Poly Pen is a fork of [Nanum Pen Script](https://fonts.google.com/specimen/Nanum+Pen+Script).**

나눔손글씨 펜 아웃라인을 삼각형으로 접어 만든 손글씨 패밀리입니다. 원본 서체는 Nanum Pen Script가 아니고, Nanum Pen Script의 **포크 / Modified Version**입니다. 가족 이름은 **Poly Pen**이며 예약 이름 Nanum, NanumPen은 쓰지 않습니다.

라이선스는 [SIL Open Font License 1.1](OFL.txt)입니다. 공개 저장소: [github.com/13ksh/poly-pen](https://github.com/13ksh/poly-pen).

## About

Each glyph is faceted into triangles. Faces that touch are merged into one outline so a connected stroke stays one part. Coverage matches the source font (full Hangul plus the rest of the Nanum Pen Script cmap). Styles: Regular 400 and Bold 700. Apps that request bold (Discord, YouTube) stay in this family instead of falling back to a default face.

Upstream source (unmodified OFL Nanum Pen Script) lives in `fonts/nanum/`. Built fonts live in `fonts/ttf/`.

## Specimen

![Poly Pen specimen](https://raw.githubusercontent.com/13ksh/poly-pen/main/documentation/poly-pen-specimen.png)

Test line: `가나다라 abcd 1234`

## License

- **Font Software:** [OFL.txt](OFL.txt) — SIL Open Font License 1.1
- Copyright 2026 The Poly Pen Project Authors (https://github.com/13ksh/poly-pen)
- Copyright 2010 NHN Corporation / Sandoll Communications Inc.

This is a Modified Version of Nanum Pen Script. See [FONTLOG.txt](FONTLOG.txt), [NOTICE.md](NOTICE.md), and [TRADEMARKS.md](TRADEMARKS.md).

Upstream Reserved Font Names (Nanum, NanumPen, and related names) are **not** used in this family name.

## Google Fonts layout

```
AUTHORS.txt
CONTRIBUTORS.txt
FONTLOG.txt
OFL.txt
README.md
TRADEMARKS.md
documentation/
  DESCRIPTION.en_us.html
  poly-pen-specimen.png
fonts/
  nanum/         # unmodified Nanum Pen Script (the upstream of this fork)
  ttf/           # PolyPen-Regular.ttf, PolyPen-Bold.ttf
sources/
  build.sh
  build_font.py
  glyph.py
  lowpoly.py
  config.yaml
requirements.txt
```

## Build

```bash
python3 -m pip install -r requirements.txt
bash sources/build.sh
```

Writes `fonts/ttf/PolyPen-Regular.ttf`, `fonts/ttf/PolyPen-Bold.ttf`, and Samsung Sans slot copies `fonts/samsung/Samsungsans.ttf` / `Samsungsans-Bold.ttf`.

## Tests

```bash
python3 test_lowpoly.py
```
