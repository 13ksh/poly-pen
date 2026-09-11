# Sources

Poly Pen is a **fork of Nanum Pen Script**.

This folder is the font source. There are no UFO or Glyphs masters.
The starting outlines are the unmodified Nanum Pen Script TTF in
`../fonts/nanum/`. The Modified Version is built here:

- `glyph.py` — load Nanum Pen Script outlines
- `lowpoly.py` — facet and merge triangles
- `build_font.py` — compile PolyPen-Regular.ttf and PolyPen-Bold.ttf
- `styles.py` — weight recipe
- `glyph_coverage.py` — coverage helpers
- `render.py` — SVG preview of facets
- `config.yaml` — family recipe
- `build.sh` — one-command build

```bash
./build.sh
```
