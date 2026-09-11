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
OUT_DIR = ROOT / "fonts" / "samsung"
SLOT = OUT_DIR / "Samsungsans.ttf"
ZIP_PATH = ROOT / "downloads" / "PolyPen-SamsungSans.zip"
OFL = ROOT / "OFL.txt"
HOWTO = OUT_DIR / "설치.txt"

HOWTO_TEXT = """Poly Pen → Samsung Sans 자리에 넣기
================================

이 파일은 삼성 공식 폰트가 아닙니다.
Poly Pen(Nanum Pen Script 포크)을 Samsung Sans APK가 찾는
파일 이름(Samsungsans.ttf)으로 저장한 것입니다.

1. Galaxy Store에서 Samsung Sans를 설치합니다.
2. Samsungsans.ttf를 이 패키지에서 받습니다.
3. MT Manager 등으로 설치된 Samsung Sans APK를 엽니다.
4. assets/fonts/ 안의 Samsungsans.ttf를 이 파일로 바꿉니다.
5. APK를 다시 서명한 뒤 설치합니다.
6. 설정 → 디스플레이 → Font size and style에서 Samsung Sans를 고릅니다.

OpenType 가족 이름은 Poly Pen입니다. SIL OFL 1.1.
"""


def main() -> Path:
    if not SRC.exists():
        raise FileNotFoundError(f"Missing {SRC}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, SLOT)
    HOWTO.write_text(HOWTO_TEXT, encoding="utf-8")
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(SLOT, "Samsungsans.ttf")
        zf.write(OFL, "OFL.txt")
        zf.write(HOWTO, "설치.txt")
    print(f"wrote {SLOT} ({SLOT.stat().st_size} bytes)")
    print(f"wrote {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")
    return SLOT


if __name__ == "__main__":
    main()
