# -*- coding: utf-8 -*-
"""Phase 0 recon: locate the FE8U text table and check text encoding in Vision Quest."""
import struct, sys, collections

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
print(f"ROM size: {len(rom):#x}")

def p32(off):
    return struct.unpack_from("<I", rom, off)[0]

# --- 1) Find candidate text table: long run of 0x08/0x09 pointers ---
# FE8U vanilla text table lives at 0x15D48C-ish; buildfiles repoint it.
# The pointer TO the table sits in literal pools near GetStringFromIndex.
# Vanilla FE8U: the text table pointer is referenced at 0xA2A0? -> find empirically:
# search for aligned dwords whose value is in ROM space and which begin a run of
# >5000 consecutive ROM-space pointers (or 0).
best = []
off = 0
n = len(rom) & ~3
i = 0
run_start = None
run_len = 0
def is_ptr(v):
    return v == 0 or (0x08000000 <= v < 0x08000000 + len(rom))
while i < n:
    v = p32(i)
    if is_ptr(v) and v != 0:
        if run_start is None:
            run_start = i
            run_len = 0
        run_len += 1
    else:
        if run_start is not None and run_len >= 2000:
            best.append((run_start, run_len))
        run_start = None
    i += 4
if run_start is not None and run_len >= 2000:
    best.append((run_start, run_len))

print("\nPointer-run candidates (start, count):")
for s, c in best[:20]:
    print(f"  {s:#010x}  count={c}")

# --- 2) Find references to each candidate (its 0x08-based address appearing in ROM) ---
for s, c in best[:20]:
    addr = struct.pack("<I", 0x08000000 + s)
    refs = []
    j = rom.find(addr)
    while j != -1 and len(refs) < 10:
        refs.append(j)
        j = rom.find(addr, j + 1)
    if refs:
        print(f"\ntable @ {s:#x} referenced from: {[hex(r) for r in refs]}")
