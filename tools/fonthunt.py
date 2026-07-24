# -*- coding: utf-8 -*-
"""Hunt for GBAFE font glyph tables: arrays of ~0x100 pointers to Glyph structs.

Glyph struct (decomp): { Glyph* next; u32 sjisByte; u32 width; u32 bitmap[16] } = 0x4C bytes.
"""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

def looks_like_glyph(off):
    if off + 0x4C > SIZE:
        return False
    nxt = p32(off)
    sjis = p32(off + 4)
    width = p32(off + 8)
    if nxt != 0 and not (0x08000000 <= nxt < 0x08000000 + SIZE):
        return False
    if sjis > 0xFF or width > 16:
        return False
    return True

# scan for runs of >=64 consecutive pointers all passing looks_like_glyph (nulls allowed)
runs = []
i = 0
run_start, good = None, 0
while i < SIZE - 4:
    v = p32(i)
    ok = v == 0 or ((0x08000000 <= v < 0x08000000 + SIZE) and looks_like_glyph(v - 0x08000000))
    if ok:
        if run_start is None:
            run_start, good = i, 0
        if v:
            good += 1
    else:
        if run_start is not None and good >= 64:
            runs.append((run_start, (i - run_start) // 4, good))
        run_start = None
    i += 4
if run_start is not None and good >= 64:
    runs.append((run_start, (i - run_start) // 4, good))

print("glyph-table candidates (start, slots, nonnull):")
for s, c, g in runs:
    # find refs
    addr = struct.pack("<I", 0x08000000 + s)
    refs, j = [], rom.find(addr)
    while j != -1 and len(refs) < 6:
        refs.append(j)
        j = rom.find(addr, j + 1)
    print(f"  {s:#010x} slots={c} nonnull={g} refs={[hex(r) for r in refs]}")
