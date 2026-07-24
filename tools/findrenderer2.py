# -*- coding: utf-8 -*-
"""Search for literals pointing anywhere near the font tables (biased indexing)."""
import struct
import numpy as np

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
arr = np.frombuffer(rom[:SIZE & ~3], dtype="<u4")

for base in (0x58C7E4, 0x58F6EC):
    lo = 0x08000000 + base - 0x800
    hi = 0x08000000 + base + 0x800
    idx = np.where((arr >= lo) & (arr <= hi))[0]
    print(f"near {base:#x}: {len(idx)} hits")
    for i in idx[:20]:
        print(f"  rom {int(i)*4:#x}: value {int(arr[i]):#010x} (table{int(arr[i]) - 0x08000000 - base:+#x})")
