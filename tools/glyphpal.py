# -*- coding: utf-8 -*-
"""Print an English glyph's 2bpp values (bitmap at +8) to learn ink/shadow convention."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

for tbl, name in ((0x58C7EC, "system/menu"), (0x58F6F4, "talk/dialogue")):
    v = p32(tbl + 4 * ord('A'))
    g = v - 0x08000000
    print(f"{name} 'A' glyph @ {g:#x}, width={rom[g+5]}, sjis={rom[g+4]}")
    for y in range(16):
        bits = p32(g + 8 + 4 * y)
        row = "".join(str((bits >> (2 * x)) & 3) for x in range(16))
        print("   ", row.replace("0", "."))
