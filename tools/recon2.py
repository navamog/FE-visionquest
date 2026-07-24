# -*- coding: utf-8 -*-
"""Inspect the candidate table at 0x1029EA0: refs, first entries, pointed data."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

BASE = 0x1029EA0
# search refs for addresses BASE-0x40 .. BASE+0x40 step 4
print("refs near table start:")
for cand in range(BASE - 0x40, BASE + 0x44, 4):
    addr = struct.pack("<I", 0x08000000 + cand)
    j = rom.find(addr)
    refs = []
    while j != -1 and len(refs) < 6:
        refs.append(j)
        j = rom.find(addr, j + 1)
    if refs:
        print(f"  {cand:#x}: {[hex(r) for r in refs]}")

print("\nfirst 8 entries and data:")
for k in range(8):
    v = p32(BASE + 4 * k)
    o = v - 0x08000000
    data = rom[o:o + 48]
    print(f"  [{k}] -> {v:#010x}  {data.hex()}")
    print(f"        ascii: {''.join(chr(b) if 32 <= b < 127 else '.' for b in data)}")

# sample some mid-table entries
print("\nsampled entries:")
for k in (100, 500, 1000, 3000, 5000, 10000, 20000, 27000):
    v = p32(BASE + 4 * k)
    o = v - 0x08000000
    data = rom[o:o + 64]
    print(f"  [{k}] -> {v:#010x}: {''.join(chr(b) if 32 <= b < 127 else '.' for b in data)}")
