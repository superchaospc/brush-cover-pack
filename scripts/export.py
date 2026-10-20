"""Export upload-size JPGs from the high-res PNGs of a cover set.

usage: python3 export.py <cover_dir>

Refuses to stretch: a PNG whose aspect ratio is more than 1% off its target is
skipped (fix the composition instead); under 1% the excess is trimmed evenly
before an even resize.
"""
import sys
from pathlib import Path
from PIL import Image

D = Path(sys.argv[1]).expanduser()
SPECS = [
    ("YouTube-16比9-高清.png", "YouTube-16比9-1280x720.jpg", (1280, 720)),
    ("抖音横版-4比3-高清.png", "抖音横版-4比3-1440x1080.jpg", (1440, 1080)),
    ("视频号主页-3比4-高清.png", "视频号主页-3比4-1080x1440.jpg", (1080, 1440)),
    ("竖屏封面-9比16-高清.png", "竖屏封面-9比16-1080x1920.jpg", (1080, 1920)),
    ("方图-1比1-高清.png", "方图-1比1-1080x1080.jpg", (1080, 1080)),
    ("Instagram-4比5-高清.png", "Instagram-4比5-1080x1350.jpg", (1080, 1350)),
    ("公众号-21比9-高清.png", "公众号-21比9-1260x540.jpg", (1260, 540)),
]

for src, dst, (tw, th) in SPECS:
    p = D / src
    if not p.exists():
        print(f"MISSING {src}")
        continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    err = abs(w / h - tw / th) / (tw / th)
    if err > 0.01:
        print(f"RATIO OFF {src}: {w}x{h} ({err:.2%}) — not exported")
        continue
    if err > 0:
        if w / h > tw / th:
            nw = round(h * tw / th); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
        else:
            nh = round(w * th / tw); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    im.resize((tw, th), Image.LANCZOS).save(D / dst, quality=92, optimize=True)
    with Image.open(D / dst) as out:
        out.verify()
    print(f"OK {src} {w}x{h} -> {dst} {tw}x{th} (ratio err {err:.2%})")
