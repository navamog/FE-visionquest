# -*- coding: utf-8 -*-
"""Pointer reverse-search with relaxed string-start condition."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

starts = []
prev = 1
for p in range(0x18C0000, 0x18D0000):
    b = rom[p]
    if prev == 0 and b != 0:
        starts.append(p)
    prev = b
print(f"{len(starts)} starts: {[hex(s) for s in starts[:10]]}")

hits = []
for s in starts[:40]:
    addr = struct.pack("<I", 0x08000000 + s)
    j = rom.find(addr)
    found = []
    while j != -1 and len(found) < 4:
        found.append(j)
        j = rom.find(addr, j + 1)
    hits.append((s, found))

for s, f in hits:
    print(f"  {s:#x} <- {[hex(x) for x in f]}  firstbytes={rom[s:s+8].hex()}")
