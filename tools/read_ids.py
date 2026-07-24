# -*- coding: utf-8 -*-
"""Print full decoded text for given text IDs (control codes annotated)."""
import struct, sys
rom = open(r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA", "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]
TABLE = 0x1024D7C

def decode(o):
    out = []
    i = o
    while i < SIZE:
        b = rom[i]
        if b == 0:
            break
        if b == 0x10 and i + 1 < SIZE:
            out.append(f"[Face{rom[i+1]:02X}]"); i += 2; continue
        if b == 0x80 and i + 1 < SIZE:
            out.append(f"[80{rom[i+1]:02X}]"); i += 2; continue
        if 0x20 <= b < 0x7f:
            out.append(chr(b))
        elif b == 1:
            out.append("[NL]\n")
        elif b == 3:
            out.append("[A]\n----\n")
        else:
            out.append(f"[{b:02X}]")
        i += 1
    return "".join(out)

for a in sys.argv[1:]:
    idx = int(a, 16)
    v = p32(TABLE + 4 * idx)
    o = (v & 0x7FFFFFFF) - 0x08000000
    print(f"===== 0x{idx:04X} @0x{o:X} (comp={not(v&0x80000000)}) =====")
    print(decode(o))
    print()
