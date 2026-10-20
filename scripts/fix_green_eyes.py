"""Remove green tint from eyes/lenses inside a box: green-ish hues -> warm skin/brown hue,
strongly green iris pixels also darkened to brown-black.
usage: fix_green_eyes.py in.png out.png x0 y0 x1 y1"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
im = Image.open(src).convert("RGB")
crop = im.crop((x0, y0, x1, y1))
rgb = np.asarray(crop).astype(np.float32)
hsv = np.asarray(crop.convert("HSV")).astype(np.float32)  # H,S,V in 0..255
H, S, V = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255

# how "green" a pixel is: hue 55-190 deg with some saturation (skin/orange glow is 0-45 deg)
hue_w = np.clip((H - 42) / 10, 0, 1) * np.clip((200 - H) / 15, 0, 1)
w = hue_w * np.clip((S - 0.08) / 0.12, 0, 1)
w = np.asarray(Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255
# iris = strongly saturated green; darken those to brown-black
iris = np.clip((S - 0.35) / 0.25, 0, 1) * hue_w
iris = np.asarray(Image.fromarray((iris * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255

newH = np.full_like(H, 22.0)                      # warm skin / brown hue
newS = S * (1 - 0.45 * w) * (1 - 0.3 * iris)      # less saturated
newV = V * (1 - 0.75 * iris)                      # iris -> dark brown-black
new = np.stack([newH * 255 / 360, np.clip(newS, 0, 1) * 255, np.clip(newV, 0, 1) * 255], -1).astype(np.uint8)
new_rgb = np.asarray(Image.fromarray(new, "HSV").convert("RGB")).astype(np.float32)
m = np.maximum(w, iris)[..., None]
out = rgb * (1 - m) + new_rgb * m
res = im.copy()
res.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (x0, y0))
res.save(dst)
print("green-weighted px:", int((w > 0.5).sum()), "iris px:", int((iris > 0.5).sum()))
