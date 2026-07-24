# -*- coding: utf-8 -*-
"""Find code referencing the font glyph tables (literals 0x0858C7E4 / 0x0858F6EC)."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)

for base in (0x58C7E4, 0x58F6EC):
    addr = struct.pack("<I", 0x08000000 + base)
    refs, j = [], rom.find(addr)
    while j != -1 and len(refs) < 16:
        refs.append(j)
        j = rom.find(addr, j + 1)
    print(f"refs to {base:#x}: {[hex(r) for r in refs]}")
