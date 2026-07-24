# -*- coding: utf-8 -*-
"""Find the table of pointers into the plaintext script region."""
import struct, collections

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

LO, HI = 0x09700000, 0x08000000 + SIZE  # text region in CPU addresses

# find clusters of aligned dwords pointing into text region (allow zeros inside runs)
hits = []
i = 0
run_start, count, zeros = None, 0, 0
while i < SIZE - 4:
    v = p32(i)
    if LO <= v < HI:
        if run_start is None:
            run_start, count, zeros = i, 0, 0
        count += 1
        zeros = 0
    elif run_start is not None and (v == 0 or 0x08000000 <= v < HI) and zeros < 64:
        zeros += 1
        count += 1
    else:
        if run_start is not None and count >= 200:
            hits.append((run_start, count))
        run_start = None
    i += 4
if run_start and count >= 200:
    hits.append((run_start, count))

print("clusters of pointers into text region:")
for s, c in hits:
    print(f"  {s:#010x} count~{c}")

def find_refs(rom_off, limit=8):
    addr = struct.pack("<I", 0x08000000 + rom_off)
    refs, j = [], rom.find(addr)
    while j != -1 and len(refs) < limit:
        refs.append(j)
        j = rom.find(addr, j + 1)
    return refs

for s, c in hits[:10]:
    # walk back to the true table start: preceding dwords that are 0 or ROM ptrs
    st = s
    while st >= 4:
        v = p32(st - 4)
        if v == 0 or 0x08000000 <= v < HI:
            st -= 4
        else:
            break
    print(f"\ncluster {s:#x}: walked-back start {st:#x}, refs to start: {[hex(r) for r in find_refs(st)]}")
    for k in range(6):
        v = p32(st + 4 * k)
        if 0x08000000 <= v < HI:
            o = v - 0x08000000
            txt = rom[o:o+50]
            print(f"   [{k}] {v:#010x}: {''.join(chr(b) if 32 <= b < 127 else '.' for b in txt)}")
        else:
            print(f"   [{k}] {v:#010x}")
