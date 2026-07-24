# -*- coding: utf-8 -*-
"""Emit a clean TSV (id<TAB>english-with-codes) of all huffman system strings
for translation. Skips pure control/placeholder rows."""
import json, struct
rom = open(r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA", "rb").read()
SIZE = len(rom)
meta = json.load(open(r"D:\Works\FEv\text\system_meta.json"))
p16 = lambda o: struct.unpack_from("<H", rom, o)[0]
BASE, ROOT = 0x15A72C, 0x15D484

def decode(off):
    out = []
    bitpos = 0
    node = ROOT
    while True:
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

def render(bs):
    out, i = [], 0
    while i < len(bs):
        c = bs[i]
        if c == 0x80 and i + 1 < len(bs):
            out.append(f"[80{bs[i+1]:02X}]"); i += 2; continue
        if 0x20 <= c < 0x7f:
            out.append(chr(c))
        elif c == 1:
            out.append("[NL]")
        elif c == 3:
            out.append("[A]")
        elif c == 0x1F:
            out.append("[X]")
        else:
            out.append(f"[{c:02X}]")
        i += 1
    return "".join(out)

rows = []
for k, m in meta.items():
    bs = decode(m["off"])
    txt = render(bs)
    # skip rows with no letters (pure codes/punct)
    if any(c.isalpha() for c in txt):
        rows.append((int(k), txt))
rows.sort()
with open(r"D:\Works\FEv\text\system_en.tsv", "w", encoding="utf-8") as f:
    for idx, txt in rows:
        f.write(f"0x{idx:04X}\t{txt}\n")
print(f"{len(rows)} translatable system strings -> text/system_en.tsv")
