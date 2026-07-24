# -*- coding: utf-8 -*-
"""Decode a batch of huffman strings and eyeball; if good, dump all to text/system_dump.txt."""
import struct, json

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]
p16 = lambda o: struct.unpack_from("<H", rom, o)[0]

BASE = 0x15A72C
ROOT = 0x15D484
TABLE = 0x1024D7C

def decode(off, maxlen=8192):
    out = []
    bitpos = 0
    node = ROOT
    while len(out) < maxlen:
        a, b = p16(node), p16(node + 2)
        if b == 0xFFFF:
            lo, hi = a & 0xFF, a >> 8
            if lo == 0:
                break
            out.append(lo)
            if hi:
                out.append(hi)
            node = ROOT
        else:
            bit = (rom[off + (bitpos >> 3)] >> (bitpos & 7)) & 1
            bitpos += 1
            node = BASE + 4 * (b if bit else a)
    return bytes(out)

CTRL = {0x01: "[NL]", 0x03: "[A]"}
def render(bs):
    out = []
    i = 0
    while i < len(bs):
        c = bs[i]
        if c == 0x80 and i + 1 < len(bs):
            out.append(f"[80{bs[i+1]:02X}]")
            i += 2
            continue
        out.append(chr(c) if 32 <= c < 127 else CTRL.get(c, f"[{c:02X}]"))
        i += 1
    return "".join(out)

meta = {}
count = 0
with open(r"D:\Works\FEv\text\system_dump.txt", "w", encoding="utf-8") as f:
    for idx in range(0x7FFF):
        v = p32(TABLE + 4 * idx)
        if v and not (v & 0x80000000) and v != 0x080E8414:
            o = v - 0x08000000
            bs = decode(o)
            meta[idx] = {"ptr": v, "off": o, "declen": len(bs)}
            f.write(f"=== 0x{idx:04X} @0x{o:X} [HUFF] ===\n{render(bs)}\n\n")
            count += 1
json.dump(meta, open(r"D:\Works\FEv\text\system_meta.json", "w"))
print(f"dumped {count} huffman strings")

