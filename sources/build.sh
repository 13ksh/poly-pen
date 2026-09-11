#!/usr/bin/env bash
# Rebuild Poly Pen from the Nanum Pen Script fork sources.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -r requirements.txt
python3 sources/build_font.py
echo "Built fonts/ttf/PolyPen-Regular.ttf (Nanum Pen Script fork)"
