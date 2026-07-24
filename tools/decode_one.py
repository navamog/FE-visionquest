# -*- coding: utf-8 -*-
"""Decode one uncompressed text record with control codes annotated."""
rom = open(r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA", "rb").read()
o = 24038080  # 0xF9F
s = rom[o:o + 700]
out = []
i = 0
while i < len(s):
    b = s[i]
    if b == 0:
        out.append("[END]")
        break
    if b == 0x10 and i + 1 < len(s):
        out.append(f"[Face{s[i+1]:02X}]")
        i += 2
        continue
    if b == 0x80 and i + 1 < len(s):
        out.append(f"[80{s[i+1]:02X}]")
        i += 2
        continue
    if 0x20 <= b < 0x7f:
        out.append(chr(b))
    elif b == 1:
        out.append("[NL]")
    elif b == 3:
        out.append("[A]\n  ")
    else:
        out.append(f"[{b:02X}]")
    i += 1
print("".join(out))
