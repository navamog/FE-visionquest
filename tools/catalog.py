# -*- coding: utf-8 -*-
"""Compact catalog of all PLAIN (VQ custom) story strings: id + snippet, in table order.
Helps locate the prologue/ch1 dialogue block. Writes text/story_index.txt."""
import struct, json

rom = open(r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA", "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]
TABLE = 0x1024D7C
COUNT = 0x7FFF

def snippet(o, n=60):
    out = []
    i = o
    while i < SIZE and len(out) < n:
        b = rom[i]
        if b == 0:
            break
        if b == 0x10 and i + 1 < SIZE:
            i += 2
            continue
        if b == 0x80 and i + 1 < SIZE:
            i += 2
            continue
        if 0x20 <= b < 0x7f:
            out.append(chr(b))
        elif b == 1:
            out.append(" / ")
        elif b == 3:
            out.append(" | ")
        i += 1
    return "".join(out)

rows = []
for idx in range(COUNT):
    v = p32(TABLE + 4 * idx)
    if v and (v & 0x80000000):
        o = (v & 0x7FFFFFFF) - 0x08000000
        rows.append((idx, o, snippet(o)))

with open(r"D:\Works\FEv\text\story_index.txt", "w", encoding="utf-8") as f:
    for idx, o, sn in rows:
        f.write(f"0x{idx:04X}\t{sn}\n")
print(f"{len(rows)} plain story strings -> text/story_index.txt")
# also show first 60 in table order
for idx, o, sn in rows[:60]:
    print(f"0x{idx:04X}  {sn[:70]}")
