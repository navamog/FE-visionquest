# -*- coding: utf-8 -*-
"""Relational search: find a dword sequence whose successive differences match the
gaps between consecutive string starts — works for any base/offset encoding.
Also try 16-bit halfword tables."""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)

starts = []
prev = 1
for p in range(0x18C0000, 0x18D0000):
    b = rom[p]
    if prev == 0 and b != 0:
        starts.append(p)
    prev = b

deltas = [starts[i+1] - starts[i] for i in range(6)]
print("string starts:", [hex(s) for s in starts[:7]])
print("deltas:", [hex(d) for d in deltas])

# 32-bit scan, stride 4: check chain of 6 deltas anywhere (also non-contiguous stride 8/12?)
import numpy as np
arr = np.frombuffer(rom[:SIZE & ~3], dtype="<u4")
for stride_words in (1, 2, 3, 4):
    d0 = deltas[0]
    idx = np.where(arr[stride_words:].astype(np.int64) - arr[:-stride_words].astype(np.int64) == d0)[0]
    good = []
    for i in idx:
        ok = True
        for k, dk in enumerate(deltas):
            a = i + k * stride_words
            b = a + stride_words
            if b >= len(arr) or int(arr[b]) - int(arr[a]) != dk:
                ok = False
                break
        if ok:
            good.append(i)
    if good:
        print(f"stride {stride_words*4}B: matches at {[hex(int(g)*4) for g in good[:10]]}")
        for g in good[:3]:
            print("   values:", [hex(int(arr[g + k*stride_words])) for k in range(7)])
