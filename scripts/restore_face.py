#!/usr/bin/env python3
"""把清楚的人脸贴回改过字的封面（改图模式连改后脸会发白、发虚、像透明）。只用 PIL。

  python3 restore_face.py GOOD.png EDITED.png OUT.png --box 0.69 0.09 0.87 0.50 [--feather 0.12] [--shape ellipse|rect]

- GOOD：人像还清楚的那一版（人物位置和 EDITED 一样，只是后来又改了字/局部）。
- EDITED：最新一版（字对了，但脸被重画后变淡变糊）。
- --box：要贴回的区域，按画面宽高的比例写（左 上 右 下），框住头发、脸、眼镜到下巴，别框进文字。
- 步骤：两图在 ±8 像素内对齐（用框外一圈背景找最小差）→ 用框外一圈背景算每个通道的亮度增益，把 GOOD 校成 EDITED 的色调 → 椭圆羽化遮罩贴回。
- 贴字板下方、旁边的背景时加 `--skip-panel`：新图里黑色笔刷和黄色飞溅保留，其余像素从清楚版本贴回。
- 框贴着画面边缘、框外一圈是改过的字板时，用 `--calib inside`（按框内整体均值校色），否则增益会算偏。
- 结束会打印对齐偏移和增益；增益偏离 1 超过 0.15 说明两版色调差很多，先人工看一眼。
"""
import argparse
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

ap = argparse.ArgumentParser()
ap.add_argument('good'); ap.add_argument('edited'); ap.add_argument('out')
ap.add_argument('--box', nargs=4, type=float, required=True)
ap.add_argument('--feather', type=float, default=0.12, help='羽化宽度，占框宽的比例')
ap.add_argument('--shape', choices=('ellipse', 'rect'), default='ellipse', help='ellipse=只贴脸；rect=整块人物区域（框到画面右边缘也行）')
ap.add_argument('--skip-panel', action='store_true', help='贴回时避开字板：新图里黑色笔刷和黄色飞溅的像素保留不动（贴字板下方/旁边的背景时用）')
ap.add_argument('--calib', choices=('ring', 'inside', 'none'), default='ring', help='校色参照：ring=框外一圈背景（默认）；inside=框内整体均值（框贴着画面边缘、外圈是改过的字板时用）；none=不校色')
a = ap.parse_args()

ed = Image.open(a.edited).convert('RGB')
W, H = ed.size
gd = Image.open(a.good).convert('RGB')
if gd.size != ed.size:
    gd = gd.resize(ed.size, Image.LANCZOS)
x0, y0, x1, y1 = int(a.box[0] * W), int(a.box[1] * H), int(a.box[2] * W), int(a.box[3] * H)
bw, bh = x1 - x0, y1 - y0
pad = max(12, int(0.08 * bw))
ring = (max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))

def ring_mask(size, inner):
    m = Image.new('L', size, 255)
    ImageDraw.Draw(m).rectangle(inner, fill=0)
    return m

# 1) 对齐：在框外一圈背景上找差异最小的平移
er = ed.crop(ring)
inner = (x0 - ring[0], y0 - ring[1], x1 - ring[0], y1 - ring[1])
rm = ring_mask(er.size, inner)
best = (None, 0, 0)
for dy in range(-8, 9, 2):
    for dx in range(-8, 9, 2):
        g = gd.crop((ring[0] - dx, ring[1] - dy, ring[2] - dx, ring[3] - dy))
        diff = ImageChops.difference(er, g).convert('L')
        s = ImageStat.Stat(diff, rm).mean[0]
        if best[0] is None or s < best[0]:
            best = (s, dx, dy)
_, dx, dy = best
for ddy in (-1, 0, 1):
    for ddx in (-1, 0, 1):
        g = gd.crop((ring[0] - dx - ddx, ring[1] - dy - ddy, ring[2] - dx - ddx, ring[3] - dy - ddy))
        s = ImageStat.Stat(ImageChops.difference(er, g).convert('L'), rm).mean[0]
        if s < best[0]:
            best = (s, dx + ddx, dy + ddy)
_, dx, dy = best
gshift = ImageChops.offset(gd, dx, dy)

# 2) 色调校准：框外一圈背景的通道均值之比
if a.calib == 'inside':
    gm = ImageStat.Stat(gshift.crop((x0, y0, x1, y1))).mean
    em = ImageStat.Stat(ed.crop((x0, y0, x1, y1))).mean
elif a.calib == 'ring':
    gm = ImageStat.Stat(gshift.crop(ring), rm).mean
    em = ImageStat.Stat(er, rm).mean
else:
    gm = em = [1, 1, 1]
gain = [max(0.7, min(1.3, e / g)) if g > 1 else 1.0 for e, g in zip(em, gm)]
patch = gshift.crop((x0, y0, x1, y1))
patch = Image.merge('RGB', [c.point(lambda v, k=k: max(0, min(255, int(v * k)))) for c, k in zip(patch.split(), gain)])

# 3) 椭圆羽化遮罩贴回
f = max(4, int(a.feather * bw))
mask = Image.new('L', (bw, bh), 0)
if a.shape == 'ellipse':
    ImageDraw.Draw(mask).ellipse((f, f, bw - f, bh - f), fill=255)
else:  # 贴到画面边缘的那几边不羽化
    ImageDraw.Draw(mask).rectangle((f if x0 > 0 else 0, f if y0 > 0 else 0, bw - (f if x1 < W else 0), bh - (f if y1 < H else 0)), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(f / 2))
if a.skip_panel:  # 新图里属于字板的像素（很暗，或亮黄飞溅）不贴回
    e = ed.crop((x0, y0, x1, y1))
    dark = e.convert('L').point(lambda v: 255 if v < 50 else 0)
    h, sat, val = e.convert('HSV').split()
    yel = ImageChops.multiply(ImageChops.multiply(h.point(lambda x: 255 if 25 <= x <= 50 else 0), sat.point(lambda x: 255 if x > 150 else 0)), val.point(lambda x: 255 if x > 170 else 0))
    panel = ImageChops.lighter(dark, yel).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
    mask = ImageChops.multiply(mask, ImageChops.invert(panel))
out = ed.copy()
out.paste(patch, (x0, y0), mask)
out.save(a.out)
print(f'aligned dx={dx} dy={dy}, ring diff={best[0]:.1f}, gain={[round(g, 3) for g in gain]} -> {a.out}')
if any(abs(g - 1) > 0.15 for g in gain):
    print('WARN 两版色调差很多，贴回前先人工看一眼')
