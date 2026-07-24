# -*- coding: utf-8 -*-
"""Look at raw structure of the script text region + how strings are delimited/referenced."""
import struct, re

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

# hexdump around first big ASCII hit
m = re.search(rb"Looking forward to hearing", rom)
base = m.start()
print(f"'Looking forward...' at {base:#x}")
st = base - 0x100
for row in range(0x30):
    o = st + row * 16
    b = rom[o:o+16]
    print(f"{o:08x}  {b.hex(' ')}  {''.join(chr(x) if 32 <= x < 127 else '.' for x in b)}")

# find any dword in ROM pointing at or near this string start (scan +-0x200 of string start)
print("\nsearching pointers to addresses near string...")
for target in range(base - 0x200, base + 0x10):
    addr = struct.pack("<I", 0x08000000 + target)
    j = rom.find(addr)
    if j != -1:
        print(f"  ptr to {target:#x} found at rom {j:#x}")
