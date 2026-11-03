#!/usr/bin/env python3
"""把清楚版的人脸对齐贴到新图（人物挪过位置、大小也变了也行）。
  python face_transplant.py SRC.png DST.png OUT.png --src-box l t r b --dst-box l t r b [--top 0.30] [--check]
box 按比例写，大致框住整个头（头顶到下巴、两耳之间）。--top：遮罩从头框的这个高度比例开始（0.30≈眉毛上沿，额头留 DST 的）。
"""
import argparse
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('out')
ap.add_argument('--src-box', nargs=4, type=float, required=True)
ap.add_argument('--dst-box', nargs=4, type=float, required=True)
ap.add_argument('--top', type=float, default=0.30)
ap.add_argument('--bottom', type=float, default=0.97)
ap.add_argument('--side', type=float, default=0.14, help='左右各收进的比例（避开耳朵和背景）')
ap.add_argument('--check', action='store_true')
ap.add_argument('--src-pts', nargs=6, type=float, help='像素坐标：左眼x y 右眼x y 嘴中心x y')
ap.add_argument('--dst-pts', nargs=6, type=float)
a = ap.parse_args()

src = cv2.imread(a.src); dst = cv2.imread(a.dst)
H, W = dst.shape[:2]
SH, SW = src.shape[:2]  # SRC 可以和 DST 尺寸不同（不同比例的封面），按各自像素坐标算

def px(b, w, h): return [int(b[0] * w), int(b[1] * h), int(b[2] * w), int(b[3] * h)]
sb, db = px(a.src_box, SW, SH), px(a.dst_box, W, H)

# 初始变换：框对框（等比缩放 + 平移）
s0 = ((db[2] - db[0]) / (sb[2] - sb[0]) + (db[3] - db[1]) / (sb[3] - sb[1])) / 2
cx_s, cy_s = (sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2
cx_d, cy_d = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
M = np.array([[s0, 0, cx_d - s0 * cx_s], [0, s0, cy_d - s0 * cy_s]], np.float32)

if a.src_pts:
    M = cv2.getAffineTransform(np.float32(a.src_pts).reshape(3, 2), np.float32(a.dst_pts).reshape(3, 2))
# ECC 精对齐：在 DST 的脸框里比较梯度
def grad(img):
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    return cv2.magnitude(gx, gy)
roi = np.zeros((H, W), np.uint8)
x0, y0, x1, y1 = db
roi[y0:y1, x0 + (x1 - x0) // 8:x1 - (x1 - x0) // 8] = 255
gd = grad(dst); gs = grad(src)
crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
warp = M.copy()
try:
    if a.src_pts: raise cv2.error("points given, skip ECC")
    # findTransformECC 的 warp 是 DST 坐标 -> SRC 坐标，取逆
    inv = cv2.invertAffineTransform(warp)
    cc, inv = cv2.findTransformECC(gs, gd, inv.astype(np.float32), cv2.MOTION_AFFINE, crit, roi, 5)
    warp = cv2.invertAffineTransform(inv)
    print(f'ECC cc={cc:.3f}')
except cv2.error as e:
    print('ECC failed, using box alignment:', e)
print('scale≈%.3f' % np.sqrt(abs(np.linalg.det(warp[:, :2]))))
ws = cv2.warpAffine(src, warp, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

# 遮罩：眉毛上沿到下巴的椭圆，羽化
bw, bh = x1 - x0, y1 - y0
mask = np.zeros((H, W), np.float32)
mt, mb = y0 + int(bh * a.top), y0 + int(bh * a.bottom)
ml, mr = x0 + int(bw * a.side), x1 - int(bw * a.side)
cv2.ellipse(mask, ((ml + mr) // 2, (mt + mb) // 2), ((mr - ml) // 2, (mb - mt) // 2), 0, 0, 360, 1, -1)
f = max(5, int(bw * 0.06))
mask = cv2.GaussianBlur(mask, (0, 0), f)

# 校色：遮罩内每个通道的均值和标准差对齐到 DST（保留 DST 的打光）
core = mask > 0.6
out_ws = ws.astype(np.float32)
for c in range(3):
    ms, ss = out_ws[..., c][core].mean(), out_ws[..., c][core].std()
    md, sd = dst[..., c][core].astype(np.float32).mean(), dst[..., c][core].astype(np.float32).std()
    k = np.clip(sd / max(ss, 1), 0.8, 1.25)
    out_ws[..., c] = (out_ws[..., c] - ms) * k + md
    print(f'ch{c}: mean {ms:.1f}->{md:.1f}, std gain {k:.3f}')
out_ws = np.clip(out_ws, 0, 255)
diff = np.abs(out_ws - dst.astype(np.float32)).mean(axis=2)[core].mean()
print(f'mean diff inside mask after align={diff:.1f}')
if a.check:
    vis = dst.copy(); vis[mask > 0.5] = (0.5 * vis[mask > 0.5] + [0, 0, 127]).astype(np.uint8)
    cv2.imwrite(a.out, vis); raise SystemExit
m3 = mask[..., None]
out = out_ws * m3 + dst.astype(np.float32) * (1 - m3)
cv2.imwrite(a.out, np.clip(out, 0, 255).astype(np.uint8))
print('->', a.out)
