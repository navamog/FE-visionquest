# -*- coding: utf-8 -*-
"""Verify v3 ROM + FE8U base hashes, then locate v3 text system via 0xA2A0 pointer."""
import zlib, hashlib, struct

def info(path):
    d = open(path, "rb").read()
    print(f"{path.split(chr(92))[-1]}")
    print(f"  size {len(d):#x}  CRC32 {zlib.crc32(d):08X}  MD5 {hashlib.md5(d).hexdigest().upper()}")
    return d

base = info(r"D:\Works\FEv\Fire Emblem - The Sacred Stones (USA, Australia).gba")
v3 = info(r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA")

p32 = lambda rom, o: struct.unpack_from("<I", rom, o)[0]
print("\nv3 text table ptr @0xA2A0:", hex(p32(v3, 0xA2A0)))
print("v3 literal @0x0800A284 area:", hex(p32(v3, 0xA284 + 0x18)))  # not exact; check 0xA2A0 first
print("v2.3-style check: anti-huffman sig @0x2BA4:", v3[0x2BA4:0x2BAC].hex(' '))
print("font tables: dlg 0x58C7EC entry 'A':", hex(p32(v3, 0x58C7EC + 4 * 0x41)),
      " menu 0x58F6F4 'A':", hex(p32(v3, 0x58F6F4 + 4 * 0x41)))
print("huffman root ptr @0x15D488:", hex(p32(v3, 0x15D488)))
# base ROM sanity
print("\nbase ptr @0xA2A0:", hex(p32(base, 0xA2A0)))
