#!/usr/bin/env bash
# Rebuild Poly Pen from the Nanum Pen Script fork sources.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -r requirements.txt
python3 sources/build_font.py --family
python3 sources/make_samsung.py
echo "Built fonts/ttf/PolyPen-Thin.ttf through PolyPen-Black.ttf (Nanum Pen Script fork)"
echo "Wrote downloads/PolyPen-100-900.zip"
