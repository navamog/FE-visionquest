# -*- coding: utf-8 -*-
"""Dump the full text table (0x15D48C) of FE Vision Quest as a readable script file.

GBAFE text codes: 0x00 end, 0x01 NL, 0x02 NL2?, 0x03 [A], 0x04-0x1F control,
0x20-0x7F ASCII, 0x80 xx = two-byte extended char.
Emits tools/out/script_dump.txt and a JSON with {id: {"ptr":..., "raw":hex}}.
"""
import struct, json, os

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

TABLE = 0x15D48C

# 1) find table entry count: walk while entries are 0 or ROM pointers
n = 0
while True:
    v = p32(TABLE + 4 * n)
    if v == 0 or (0x08000000 <= v < 0x08000000 + SIZE):
        n += 1
        if TABLE + 4 * n >= SIZE:
            break
    else:
        break
print(f"table entries (raw walk): {n} (0x{n:X})")

CTRL = {
    0x01: "[NL]", 0x02: "[NL2]", 0x03: "[A]", 0x04: "[----]", 0x05: "[.]",
    0x06: "[..]", 0x07: "[...]", 0x08: "[....]", 0x09: "[OpenFarLeft]",
    0x0A: "[OpenMidLeft]", 0x0B: "[OpenLeft]", 0x0C: "[OpenRight]",
    0x0D: "[OpenMidRight]", 0x0E: "[OpenFarRight]", 0x0F: "[OpenFarFarLeft]",
    0x10: "[LoadOverworldFaces]", 0x11: "[G]", 0x14: "[MidRight]",
    0x15: "[CloseSpeechFast]", 0x16: "[CloseSpeechSlow]", 0x17: "[ToggleMouthMove]",
    0x18: "[ToggleSmile]", 0x19: "[Yes]", 0x1A: "[No]", 0x1B: "[Buy/Sell]",
    0x1C: "[SendToBack]", 0x1F: "[Clear]",
}

def decode(off):
    out = []
    i = off
    while i < SIZE:
        b = rom[i]
        if b == 0:
            break
        if b == 0x80 and i + 1 < SIZE:
            out.append(f"[80{rom[i+1]:02X}]")
            i += 2
            continue
        if 0x20 <= b < 0x80:
            out.append(chr(b))
        elif b in CTRL:
            out.append(CTRL[b])
        else:
            out.append(f"[{b:02X}]")
        i += 1
    return "".join(out), i - off

os.makedirs(r"D:\Works\FEv\tools\out", exist_ok=True)
meta = {}
nonnull = 0
plain = 0
with open(r"D:\Works\FEv\tools\out\script_dump.txt", "w", encoding="utf-8") as f:
    for idx in range(n):
        v = p32(TABLE + 4 * idx)
        if v == 0:
            continue
        nonnull += 1
        o = v - 0x08000000
        txt, ln = decode(o)
        meta[idx] = {"ptr": v, "off": o, "len": ln}
        plain += 1
        f.write(f"=== 0x{idx:04X} @0x{o:X} len={ln} ===\n{txt}\n\n")

json.dump(meta, open(r"D:\Works\FEv\tools\out\script_meta.json", "w"))
print(f"non-null entries: {nonnull}")
# stats: pointer target distribution
import collections
hist = collections.Counter(m["off"] >> 20 for m in meta.values())
print("string offset MB histogram:", {f'{k:#x}': v for k, v in sorted(hist.items())})
tot = sum(m["len"] for m in meta.values())
print(f"total text bytes: {tot}")
