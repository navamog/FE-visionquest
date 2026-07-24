# -*- coding: utf-8 -*-
"""Find real text table: locate string starts (byte after 0x00) in text region,
then search ROM for pointers to those exact starts."""
import struct, re

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

# string starts in 0x18C0000..0x18D0000: position p where rom[p-1]==0 and rom[p] printable
starts = []
for p in range(0x18C0000, 0x18E0000):
    if rom[p - 1] == 0 and rom[p] != 0 and (0x20 <= rom[p] < 0x7F or rom[p] in (1, 2, 3, 0x80)):
        starts.append(p)
        if len(starts) >= 30:
            break
print(f"found {len(starts)} string starts, e.g. {[hex(s) for s in starts[:5]]}")

ptr_locs = []
for s in starts:
    addr = struct.pack("<I", 0x08000000 + s)
    j = rom.find(addr)
    found = []
    while j != -1 and len(found) < 4:
        found.append(j)
        j = rom.find(addr, j + 1)
    if found:
        ptr_locs.append((s, found))

print("\nstring start -> pointer locations:")
for s, locs in ptr_locs[:30]:
    print(f"  {s:#x} <- {[hex(x) for x in locs]}")
