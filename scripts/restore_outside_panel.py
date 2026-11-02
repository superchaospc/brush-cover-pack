#!/usr/bin/env python3
"""字板以外全部贴回：新图只保留文字板（黑色笔刷、黄色飞溅和里面的字），人物和背景从清楚的版本贴回。只用 PIL。

  python3 restore_outside_panel.py GOOD.png EDITED.png OUT.png [--grow 0.012] [--feather 0.006] [--check]

- 用于只改了字（换字体、放大字、改文案）的那一轮：改图模式会把人物和背景整体重画变糊。
- GOOD 和 EDITED 必须是同一构图（人物位置没挪）。脚本先在字板以外的区域里找 ±10 像素内的最佳对齐，
  平均差异大于 --max-diff（默认 22）就拒绝贴回，说明构图变了。
- 字板范围：新旧两版差别大于 --thresh 的像素（字和字板变了，人物背景只是糊、差别小），闭运算连成片，只留最大一块并填洞，再外扩 --grow（占宽度比例）。
- --sharpen 90：贴回后再只给人物和背景加一点锐化（AI 出的 1600 像素图本身偏软，用户会嫌糊）。
- --check 只打印对齐结果，并把字板遮罩存到 OUT 供检查。
"""
import argparse
from PIL import Image, ImageChops, ImageFilter, ImageStat

ap = argparse.ArgumentParser()
ap.add_argument('good'); ap.add_argument('edited'); ap.add_argument('out')
ap.add_argument('--grow', type=float, default=0.012)
ap.add_argument('--feather', type=float, default=0.006)
ap.add_argument('--max-diff', type=float, default=22)
ap.add_argument('--check', action='store_true')
ap.add_argument('--sharpen', type=float, default=0, help='贴回后只给字板以外加锐化（UnsharpMask 百分比，常用 90；0=不锐化）')
ap.add_argument('--thresh', type=int, default=60, help='新旧像素差大于它才算字板（0-255）')
a = ap.parse_args()

ed = Image.open(a.edited).convert('RGB'); W, H = ed.size
gd = Image.open(a.good).convert('RGB')
if gd.size != ed.size:
    gd = gd.resize(ed.size, Image.LANCZOS)

def odd(n): n = max(3, int(n)); return n if n % 2 else n + 1

# 字板遮罩：在缩小图上找“暗或亮黄”的像素，闭运算连成片，只留面积最大的一块并填掉内部的洞
s = max(4, W // 240)
sw, sh = W // s, H // s
small = ed.resize((sw, sh))
gsmall = gd.resize((sw, sh))
# 只改了字：新旧差别大的地方就是字板和字；人物、背景只是变糊，差别小
diff = ImageChops.difference(small, gsmall)
dr, dg, db = diff.split()
m = ImageChops.lighter(ImageChops.lighter(dr, dg), db).point(lambda v: 255 if v > a.thresh else 0)
r = odd(sw * 0.02)
m = m.filter(ImageFilter.MaxFilter(r)).filter(ImageFilter.MinFilter(r))
px = m.load()
seen = [[False] * sh for _ in range(sw)]
best_comp = []
for x0 in range(sw):
    for y0 in range(sh):
        if px[x0, y0] > 127 and not seen[x0][y0]:
            comp, stack = [], [(x0, y0)]; seen[x0][y0] = True
            while stack:
                x, y = stack.pop(); comp.append((x, y))
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < sw and 0 <= ny < sh and not seen[nx][ny] and px[nx, ny] > 127:
                        seen[nx][ny] = True; stack.append((nx, ny))
            if len(comp) > len(best_comp):
                best_comp = comp
m = Image.new('L', (sw, sh), 0); mp = m.load()
for x, y in best_comp:
    mp[x, y] = 255
# 填洞：从边缘漫灌背景，没灌到的都算字板
bg = [[False] * sh for _ in range(sw)]
stack = [(x, y) for x in range(sw) for y in (0, sh - 1)] + [(x, y) for y in range(sh) for x in (0, sw - 1)]
while stack:
    x, y = stack.pop()
    if 0 <= x < sw and 0 <= y < sh and not bg[x][y] and mp[x, y] == 0:
        bg[x][y] = True
        stack += [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
for x in range(sw):
    for y in range(sh):
        if not bg[x][y]:
            mp[x, y] = 255
m = m.filter(ImageFilter.MaxFilter(odd(sw * a.grow)))
m = m.filter(ImageFilter.GaussianBlur(max(1, sw * a.feather)))
panel = m.resize((W, H), Image.LANCZOS)
outside = ImageChops.invert(panel)
cover = ImageStat.Stat(panel).mean[0] / 255

# 对齐：在字板以外比较
sm_out = outside.resize((sw, sh)).point(lambda v: 255 if v > 200 else 0)
ge = gd.resize((sw, sh)); es = ed.resize((sw, sh))
best = None
for dy in range(-3, 4):
    for dx in range(-3, 4):
        g = ImageChops.offset(ge, dx, dy)
        d = ImageStat.Stat(ImageChops.difference(es, g).convert('L'), sm_out).mean[0]
        if best is None or d < best[0]:
            best = (d, dx * s, dy * s)
d0, dx, dy = best
for ddy in range(-3, 4):
    for ddx in range(-3, 4):
        g = ImageChops.offset(gd, dx + ddx, dy + ddy).resize((sw, sh))
        d = ImageStat.Stat(ImageChops.difference(es, g).convert('L'), sm_out).mean[0]
        if d < best[0]:
            best = (d, dx + ddx, dy + ddy)
diff, dx, dy = best
print(f'panel covers {cover:.0%} of the frame; aligned dx={dx} dy={dy}, mean diff outside panel={diff:.1f}')
if diff > a.max_diff:
    raise SystemExit(f'REFUSED: diff {diff:.1f} > {a.max_diff} — 构图变了，不能贴回')
if a.check:
    panel.save(a.out)  # --check 时把遮罩存到 OUT 方便看
    raise SystemExit(0)
g = ImageChops.offset(gd, dx, dy)
out = Image.composite(g, ed, outside)
if a.sharpen > 0:  # AI 原图本身偏软：只锐化人物和背景，字板不动
    out = Image.composite(out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=int(a.sharpen), threshold=2)), out, outside)
out.save(a.out)
print('->', a.out)
