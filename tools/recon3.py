# -*- coding: utf-8 -*-
"""Better text-table hunt: varied pointer runs + check vanilla FE8U table refs + ASCII sweep."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]
SIZE = len(rom)

def find_refs(rom_off, limit=8):
    addr = struct.pack("<I", 0x08000000 + rom_off)
    refs, j = [], rom.find(addr)
    while j != -1 and len(refs) < limit:
        refs.append(j)
        j = rom.find(addr, j + 1)
    return refs

# 1) vanilla FE8U text table at 0x15D48C — who references it?
print("refs to 0x0815D48C (vanilla FE8U text table):", [hex(r) for r in find_refs(0x15D48C)])

# what's AT 0x15D48C?
print("data @0x15D48C:", rom[0x15D48C:0x15D48C+32].hex())

# 2) varied pointer runs
runs = []
i = 0
run_start = None
vals = set()
count = 0
while i < SIZE - 4:
    v = p32(i)
    if 0x08000000 <= v < 0x08000000 + SIZE:
        if run_start is None:
            run_start, vals, count = i, set(), 0
        vals.add(v)
        count += 1
    else:
        if run_start is not None and count >= 1000 and len(vals) >= count // 4:
            runs.append((run_start, count, len(vals)))
        run_start = None
    i += 4
print("\nvaried pointer runs (start, count, distinct):")
for s, c, d in runs:
    print(f"  {s:#010x} count={c} distinct={d}  refs={[hex(r) for r in find_refs(s, 4)]}")

# 3) ASCII string sweep: find dense readable regions (sample every 0x10000)
print("\nASCII density map (block=64KiB, show blocks >20% printable-run coverage):")
import re
pat = re.compile(rb"[\x20-\x7e]{8,}")
for blk in range(0, SIZE, 0x40000):
    chunk = rom[blk:blk + 0x40000]
    tot = sum(len(m.group()) for m in pat.finditer(chunk))
    if tot > len(chunk) * 0.2:
        m = pat.search(chunk)
        print(f"  {blk:#010x}: {tot*100//len(chunk)}%  e.g. {m.group()[:60]!r}")
