# -*- coding: utf-8 -*-
"""Prototype: render Hangul via Windows bitmap-strike fonts into 16x16 cells,
compare candidates (Gulim/GulimChe/Dotum/DotumChe at 11-13px) side by side."""
import numpy as np
from PIL import Image, ImageFont, ImageDraw

SAMPLE = "가난다랐마법사왔잖챃퀭튐폡했 뷁"  # incl. complex finals/vowels
CANDIDATES = [
    (r"C:\Windows\Fonts\gulim.ttc", 0, 11), (r"C:\Windows\Fonts\gulim.ttc", 0, 12),
    (r"C:\Windows\Fonts\gulim.ttc", 1, 11), (r"C:\Windows\Fonts\gulim.ttc", 1, 12),
    (r"C:\Windows\Fonts\gulim.ttc", 1, 13),
    (r"C:\Windows\Fonts\batang.ttc", 0, 12),
    (r"C:\Windows\Fonts\malgun.ttf", None, 12),
]

rows = []
labels = []
for path, idx, px in CANDIDATES:
    try:
        f = ImageFont.truetype(path, px, index=idx or 0)
    except Exception as e:
        print(f"skip {path}#{idx}@{px}: {e}")
        continue
    strip = np.zeros((16, 16 * len(SAMPLE)), np.uint8)
    for i, ch in enumerate(SAMPLE):
        img = Image.new("L", (18, 18), 0)
        d = ImageDraw.Draw(img)
        d.text((0, 1), ch, fill=255, font=f)
        a = np.array(img)[:16, :16]
        strip[:, i*16:(i+1)*16] = (a > 96) * 255
    rows.append(strip)
    labels.append(f"{path.split(chr(92))[-1]}#{idx}@{px}px")
    print("rendered", labels[-1])

H = 20
out = np.zeros((H * len(rows), 16 * len(SAMPLE)), np.uint8)
for r, strip in enumerate(rows):
    out[r*H:r*H+16, :] = strip
img = Image.fromarray(out)
img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
img.save(r"D:\Works\FEv\tools\out\hangul_candidates.png")
print("\n".join(f"row {i}: {l}" for i, l in enumerate(labels)))
print("saved tools/out/hangul_candidates.png")
