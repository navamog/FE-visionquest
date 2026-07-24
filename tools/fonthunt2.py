# -*- coding: utf-8 -*-
"""Looser glyph-table scan + dump candidate structures for manual inspection."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

ROMP = lambda v: 0x08000000 <= v < 0x08000000 + SIZE

runs = []
i = 0
run_start, good = None, 0
targets_seen = None
while i < SIZE - 4:
    v = p32(i)
    ok = False
    if v == 0:
        ok = True
    elif ROMP(v):
        t = v - 0x08000000
        if t + 8 < SIZE:
            first = p32(t)
            ok = first == 0 or ROMP(first) or (0x02000000 <= first < 0x02040000)
    if ok:
        if run_start is None:
            run_start, good = i, 0
            targets_seen = set()
        if v:
            good += 1
            targets_seen.add(v)
    else:
        if run_start is not None and good >= 80 and len(targets_seen) >= 60:
            runs.append((run_start, (i - run_start) // 4, good))
        run_start = None
    i += 4

print(f"{len(runs)} loose candidates")
for s, c, g in runs[:40]:
    # inspect target struct shape: dwords at +4, +8 of first few targets
    shapes = []
    for k in range(c):
        v = p32(s + 4 * k)
        if v and ROMP(v):
            t = v - 0x08000000
            shapes.append((p32(t + 4), p32(t + 8)))
            if len(shapes) >= 3:
                break
    print(f"  {s:#010x} slots={c} nonnull={g} sample(+4,+8)={[(hex(a), hex(b)) for a, b in shapes]}")
