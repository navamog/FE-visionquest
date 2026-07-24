# -*- coding: utf-8 -*-
"""Classify non-MSB (huffman) entries in the text table: dummy vs real compressed strings."""
import struct, collections

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

TABLE = 0x1024D7C
COUNT = 0x7FFF

vals = collections.Counter()
real = []
for idx in range(COUNT):
    v = p32(TABLE + 4 * idx)
    if v and not (v & 0x80000000):
        vals[v] += 1
        real.append((idx, v))

print("top targets among non-MSB entries:")
for v, c in vals.most_common(5):
    print(f"  {v:#010x} x{c}")

dummy = vals.most_common(1)[0][0]
realones = [(i, v) for i, v in real if v != dummy]
print(f"\nnon-dummy huffman entries: {len(realones)}")
print("first 30:", [(hex(i), hex(v)) for i, v in realones[:30]])
# index range distribution
if realones:
    idxs = [i for i, _ in realones]
    print(f"index range: {min(idxs):#x}..{max(idxs):#x}")
