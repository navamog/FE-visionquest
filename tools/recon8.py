# -*- coding: utf-8 -*-
"""Debug: what does 0x18C0000..0x1900000 actually look like? sample hexdumps + transition census."""
ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()

def dump(o, rows=6):
    for r in range(rows):
        b = rom[o + r*16 : o + r*16 + 16]
        print(f"{o + r*16:08x}  {b.hex(' ')}  {''.join(chr(x) if 32 <= x < 127 else '.' for x in b)}")
    print()

for spot in (0x18C1000, 0x18C8000, 0x18D0000, 0x18E0000, 0x18F0000):
    dump(spot)

# census of 00->nonzero transitions in 0x1700000..0x19F6FA0
region = rom[0x1700000:]
count = 0
first = []
prev = 1
for i, b in enumerate(region):
    if prev == 0 and b != 0:
        count += 1
        if len(first) < 10:
            first.append(0x1700000 + i)
    prev = b
print(f"00->nonzero transitions in 0x1700000+: {count}")
print("first few:", [hex(x) for x in first])
