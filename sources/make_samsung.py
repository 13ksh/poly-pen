"""Make a Samsung Sans drop-in copy of Poly Pen.

Samsung's Samsung Sans FlipFont APK looks for assets/fonts/Samsungsans.ttf.
This copies Poly Pen to that filename. The OpenType family name stays Poly Pen.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "fonts" / "ttf" / "PolyPen-Regular.ttf"
BOLD_SRC = ROOT / "fonts" / "ttf" / "PolyPen-Bold.ttf"
OUT_DIR = ROOT / "fonts" / "samsung"
SLOT = OUT_DIR / "Samsungsans.ttf"
BOLD_SLOT = OUT_DIR / "Samsungsans-Bold.ttf"
ZIP_PATH = ROOT / "downloads" / "PolyPen-SamsungSans.zip"
ZFONT_ZIP = ROOT / "downloads" / "PolyPen-zFont-OneUI8.zip"
OFL = ROOT / "OFL.txt"
HOWTO = OUT_DIR / "설치.txt"
ZFONT_HOWTO = OUT_DIR / "zfont-oneui8.txt"

HOWTO_TEXT = """Poly Pen → Samsung Sans 자리에 넣기
================================

이 파일은 삼성 공식 폰트가 아닙니다.
Poly Pen(Nanum Pen Script 포크)을 Samsung Sans APK가 찾는
파일 이름(Samsungsans.ttf / Samsungsans-Bold.ttf)으로 저장한 것입니다.

zFont 3 + One UI 8을 쓰면 이 방법은 필요 없습니다.
PolyPen-Regular.ttf와 PolyPen-Bold.ttf를 zFont Downloads에서 고르면 됩니다.
"""

ZFONT_TEXT = """Poly Pen → zFont 3 · One UI 8
==============================

1. Play 스토어에서 zFont 3 설치
   https://play.google.com/store/apps/details?id=com.htetznaing.zfont2
2. PolyPen-Regular.ttf 와 PolyPen-Bold.ttf 를 폰에 받습니다.
3. zFont 3 → Downloads에서 Regular를 고른 뒤, Bold가 있으면 같이 넣습니다.
4. One UI 8 선택 → Create
5. zFile 설치를 물어보면 설치한 뒤 다시 Create
6. Install Package
7. 설정 → 디스플레이 → Font size and style 에서 적용

OpenType 가족 이름은 Poly Pen입니다. SIL OFL 1.1.
Regular 400과 Bold 700이 같이 있어야
Discord / YouTube처럼 굵은 글씨를 쓰는 앱이 기본 폰트로 넘어가지 않습니다.
One UI 8.5 / 최신 보안 패치에서는 막힐 수 있습니다.
"""


def main() -> Path:
    if not SRC.exists():
        raise FileNotFoundError(f"Missing {SRC}")
    from fix_android import fix_font

    fix_font(SRC, style="Regular")
    if BOLD_SRC.exists():
        fix_font(BOLD_SRC, style="Bold")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, SLOT)
    if BOLD_SRC.exists():
        shutil.copy2(BOLD_SRC, BOLD_SLOT)
    elif BOLD_SLOT.exists():
        BOLD_SLOT.unlink()
    HOWTO.write_text(HOWTO_TEXT, encoding="utf-8")
    ZFONT_HOWTO.write_text(ZFONT_TEXT, encoding="utf-8")
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(SLOT, "Samsungsans.ttf")
        if BOLD_SLOT.exists():
            zf.write(BOLD_SLOT, "Samsungsans-Bold.ttf")
        zf.write(OFL, "OFL.txt")
        zf.write(HOWTO, "설치.txt")
    with zipfile.ZipFile(ZFONT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(SRC, "PolyPen-Regular.ttf")
        if BOLD_SRC.exists():
            zf.write(BOLD_SRC, "PolyPen-Bold.ttf")
        zf.write(OFL, "OFL.txt")
        zf.write(ZFONT_HOWTO, "zfont-oneui8.txt")
    print(f"wrote {SLOT} ({SLOT.stat().st_size} bytes)")
    if BOLD_SLOT.exists():
        print(f"wrote {BOLD_SLOT} ({BOLD_SLOT.stat().st_size} bytes)")
    print(f"wrote {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")
    print(f"wrote {ZFONT_ZIP} ({ZFONT_ZIP.stat().st_size} bytes)")
    return SLOT


if __name__ == "__main__":
    main()
