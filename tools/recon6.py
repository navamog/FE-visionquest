# -*- coding: utf-8 -*-
"""Map the text table around 0x15D1524: find start/end allowing null entries, count, refs."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

ANCHOR = 0x15D1524
ok = lambda v: v == 0 or (0x08000000 <= v < 0x08000000 + SIZE)

st = ANCHOR
while st >= 4 and ok(p32(st - 4)):
    st -= 4
en = ANCHOR
while en + 4 < SIZE and ok(p32(en + 4)):
    en += 4
count = (en - st) // 4 + 1
print(f"table region {st:#x}..{en:#x}  entries={count}")

def find_refs(rom_off, limit=8):
    addr = struct.pack("<I", 0x08000000 + rom_off)
    refs, j = [], rom.find(addr)
    while j != -1 and len(refs) < limit:
        refs.append(j)
        j = rom.find(addr, j + 1)
    return refs

# refs to plausible starts
for cand in (st, st + 4, st - 4):
    r = find_refs(cand)
    if r:
        print(f"refs to {cand:#x}: {[hex(x) for x in r]}")

# stats on entries
import collections
nonzero = 0
targets = []
for o in range(st, en + 4, 4):
    v = p32(o)
    if v:
        nonzero += 1
        targets.append(v)
print(f"nonzero entries: {nonzero}")
targets.sort()
print(f"target range: {targets[0]:#x} .. {targets[-1]:#x}")
hist = collections.Counter((t - 0x08000000) >> 20 for t in targets)
print("target MB histogram:", {f'{k:#x}': v for k, v in sorted(hist.items())})

# first entries + a few samples decoded as GBAFE text
def show(idx):
    v = p32(st + 4 * idx)
    if not v:
        print(f"  [{idx}] NULL")
        return
    o = v - 0x08000000
    raw = rom[o:o+80]
    txt = ''.join(chr(b) if 32 <= b < 127 else f'<{b:02X}>' for b in raw.split(b'\0')[0])
    print(f"  [{idx}] {v:#010x}: {txt[:100]}")
for i in list(range(6)) + [0x10, 0x100, 0x4E1, 0x800, 0x1000]:
    if st + 4 * i <= en:
        show(i)
