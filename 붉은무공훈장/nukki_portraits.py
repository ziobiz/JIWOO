"""캐릭터 PNG 누끼 — rembg + 알파 hardened (인물 불투명 / 배경 투명).
_pre_nukki 백업이 있으면 그것으로부터 재생성한다.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from rembg import remove
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BACKUP = ASSETS / "_pre_nukki"
WEB = ROOT.parent / "web" / "public" / "assets"

PATTERNS = [
    "portrait*.png",
    "player*.png",
    "henry*.png",
    "wilson.png",
    "commander.png",
    "soldier.png",
    "jim.png",
    "daniel.png",
    "mark.png",
    "veteran.png",
    "wounded.png",
    "medic.png",
]


def collect_names() -> list[str]:
    names: set[str] = set()
    for pat in PATTERNS:
        for p in ASSETS.glob(pat):
            if p.is_file() and p.parent == ASSETS:
                names.add(p.name)
        for p in BACKUP.glob(pat):
            if p.is_file():
                names.add(p.name)
    return sorted(names)


def harden_alpha(im: Image.Image) -> Image.Image:
    """반투명 몸통을 불투명으로, 아주 약한 알파만 모서리 페더로 남김."""
    import numpy as np

    arr = np.array(im.convert("RGBA"))
    a = arr[:, :, 3]
    # 배경
    bg = a < 28
    # 인물 본체
    body = a >= 100
    arr[bg, 3] = 0
    arr[bg, 0:3] = 0
    arr[body, 3] = 255
    return Image.fromarray(arr, "RGBA")


def cutout_from(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGBA")
    out = remove(img)
    if not isinstance(out, Image.Image):
        out = Image.open(out).convert("RGBA")
    else:
        out = out.convert("RGBA")
    out = harden_alpha(out)
    out.save(dst, "PNG", optimize=True)


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)
    names = collect_names()
    print(f"[start] {len(names)} files")
    for i, name in enumerate(names, 1):
        bak = BACKUP / name
        cur = ASSETS / name
        # 원본 백업 확보
        if not bak.exists() and cur.exists():
            shutil.copy2(cur, bak)
        src = bak if bak.exists() else cur
        if not src.exists():
            print(f"  skip missing {name}")
            continue
        print(f"  [{i}/{len(names)}] {name} …", flush=True)
        cutout_from(src, cur)
        if WEB.is_dir():
            shutil.copy2(cur, WEB / name)
    print("[done]")


if __name__ == "__main__":
    main()
