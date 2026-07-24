# -*- coding: utf-8 -*-
"""Map the REAL text table (MSB-set anti-huffman pointers) around 0x10280BC and dump all text."""
import struct, json, os, collections

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

def entry_ok(v):
    a = v & 0x7FFFFFFF
    return v == 0 or (0x08000000 <= a < 0x08000000 + SIZE)

# Confirmed from disassembly at 0x0800A284: ldr r1, =0x09024D7C
st = 0x1024D7C
en = st
while en + 4 < SIZE and entry_ok(p32(en + 4)):
    en += 4
count = (en - st) // 4 + 1
print(f"table {st:#x}..{en:#x} entries={count} (0x{count:X})")

CTRL = {
    0x01: "[NL]", 0x02: "[NL2]", 0x03: "[A]", 0x04: "[----]", 0x05: "[.]",
    0x06: "[..]", 0x07: "[...]", 0x08: "[....]", 0x09: "[OpenFarLeft]",
    0x0A: "[OpenMidLeft]", 0x0B: "[OpenLeft]", 0x0C: "[OpenRight]",
    0x0D: "[OpenMidRight]", 0x0E: "[OpenFarRight]", 0x0F: "[OpenFarFarLeft]",
    0x10: "[LoadFace]", 0x11: "[G]", 0x14: "[MidRight]",
    0x15: "[CloseSpeechFast]", 0x16: "[CloseSpeechSlow]", 0x17: "[ToggleMouth]",
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

os.makedirs(r"D:\Works\FEv\text", exist_ok=True)
meta = {}
stats = collections.Counter()
tot = 0
with open(r"D:\Works\FEv\text\script_dump.txt", "w", encoding="utf-8") as f:
    for idx in range(count):
        v = p32(st + 4 * idx)
        if v == 0:
            stats["null"] += 1
            continue
        comp = not (v & 0x80000000)
        o = (v & 0x7FFFFFFF) - 0x08000000
        if comp:
            stats["huffman?"] += 1
            meta[idx] = {"ptr": v, "off": o, "compressed": True}
            f.write(f"=== 0x{idx:04X} @0x{o:X} [COMPRESSED?] ===\n\n")
            continue
        stats["plain"] += 1
        txt, ln = decode(o)
        tot += ln
        meta[idx] = {"ptr": v, "off": o, "len": ln}
        f.write(f"=== 0x{idx:04X} @0x{o:X} len={ln} ===\n{txt}\n\n")

json.dump(meta, open(r"D:\Works\FEv\text\script_meta.json", "w"))
print("stats:", dict(stats), "total plain bytes:", tot)

