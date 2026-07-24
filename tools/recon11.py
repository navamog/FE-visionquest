# -*- coding: utf-8 -*-
"""Find code references to the new text table: any dword valued 0x09020000..0x09050000."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

import numpy as np
arr = np.frombuffer(rom[:SIZE & ~3], dtype="<u4")
idx = np.where((arr >= 0x09000000) & (arr < 0x09100000))[0]
print(f"{len(idx)} dwords valued 0x0900xxxx-0x0910xxxx")
import collections
c = collections.Counter(int(arr[i]) for i in idx)
for val, cnt in c.most_common(20):
    locs = [hex(int(i) * 4) for i in idx if int(arr[i]) == val][:6]
    print(f"  {val:#010x} x{cnt}  at {locs}")
