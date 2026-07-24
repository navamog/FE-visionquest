# -*- coding: utf-8 -*-
"""Render glyphs from the two candidate font tables to PNG to verify struct layout.

Assumed Glyph: { next(4), u8 sjisByte, u8 ?, u8 width?, u8 ?; bitmap u32[16] 2bpp rows }
We render bitmap interpreting each u32 as 16 2-bit pixels (LSB-first), 16 rows.
"""
import struct, sys
import numpy as np
from PIL import Image

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

def render_table(table, name, slots=0x100):
    CELL = 20
    img = np.full((16 * CELL + 8, 16 * CELL + 8), 32, np.uint8)
    pal = [0, 250, 160, 90]
    for c in range(slots):
        v = p32(table + 4 * c)
        if not v or not (0x08000000 <= v < 0x08000000 + SIZE):
            continue
        g = v - 0x08000000
        row, col = divmod(c, 16)
        y0, x0 = row * CELL + 4, col * CELL + 4
        for y in range(16):
            bits = p32(g + 0xC + 4 * y)
            for x in range(16):
                px = (bits >> (2 * x)) & 3
                img[y0 + y, x0 + x] = pal[px]
    out = rf"D:\Works\FEv\tools\out\{name}.png"
    Image.fromarray(img).resize((img.shape[1]*2, img.shape[0]*2), Image.NEAREST).save(out)
    print("saved", out)

import os
os.makedirs(r"D:\Works\FEv\tools\out", exist_ok=True)

for base in (0x58C7E4, 0x58C7EC, 0x58F6EC, 0x58F6F4):
    render_table(base, f"font_{base:X}")

# also print struct header fields for some ASCII slots of first table
for tbl in (0x58C7E4, 0x58F6EC):
    print(f"\ntable {tbl:#x}:")
    for ch in "AiW .":
        v = p32(tbl + 4 * ord(ch))
        if v and 0x08000000 <= v < 0x08000000 + SIZE:
            g = v - 0x08000000
            print(f"  '{ch}' -> {v:#010x} next={p32(g):#x} hdr={rom[g+4:g+12].hex(' ')}")
        else:
            print(f"  '{ch}' -> {v:#010x}")
