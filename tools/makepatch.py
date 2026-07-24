# -*- coding: utf-8 -*-
"""Build a UPS patch from base v3 ROM -> patched Korean ROM.
UPS handles >16MB ROMs and differing in/out sizes (IPS cannot). Matches the
VQ distribution convention. Round-trip verified."""
import zlib, hashlib, struct

BASE = r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA"
PATCHED = r"D:\Works\FEv\out\vq3kr.gba"
OUT = r"D:\Works\FEv\out\vq3_korean.ups"

src = open(BASE, "rb").read()
dst = open(PATCHED, "rb").read()

def wvlv(n):
    """UPS variable-length value: 7 bits/byte, high bit = terminator, biased."""
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            break
        out.append(x)
        n -= 1
    return bytes(out)

body = bytearray()
n = max(len(src), len(dst))
i = 0
last = 0
while i < n:
    a = src[i] if i < len(src) else 0
    b = dst[i] if i < len(dst) else 0
    if a != b:
        body += wvlv(i - last)          # relative offset from prev block end
        j = i
        while j < n:
            aa = src[j] if j < len(src) else 0
            bb = dst[j] if j < len(dst) else 0
            if aa == bb:
                # peek: continue block only across single matching bytes? UPS blocks
                # end at first XOR==0 that is followed by more zeros; simplest: end here
                break
            body.append(aa ^ bb)
            j += 1
        body.append(0x00)               # block terminator
        last = j + 1
        i = j + 1
    else:
        i += 1

patch = bytearray(b"UPS1")
patch += wvlv(len(src))
patch += wvlv(len(dst))
patch += body
patch += struct.pack("<I", zlib.crc32(src) & 0xffffffff)
patch += struct.pack("<I", zlib.crc32(dst) & 0xffffffff)
patch += struct.pack("<I", zlib.crc32(bytes(patch)) & 0xffffffff)
open(OUT, "wb").write(patch)
print(f"UPS: {OUT}  ({len(patch):,} bytes)")

def h(d):
    return f"CRC32 {zlib.crc32(d)&0xffffffff:08X}  MD5 {hashlib.md5(d).hexdigest().upper()}  SHA1 {hashlib.sha1(d).hexdigest().upper()}"
print("base   :", h(src))
print("patched:", h(dst))

# ---- round-trip: apply UPS to src, compare dst ----
def rvlv(buf, p):
    val = 0
    shift = 0
    while True:
        x = buf[p]; p += 1
        val += (x & 0x7F) << shift
        if x & 0x80:
            break
        shift += 7
        val += 1 << shift
    return val, p

def apply_ups(src, patch):
    assert patch[:4] == b"UPS1"
    p = 4
    isz, p = rvlv(patch, p)
    osz, p = rvlv(patch, p)
    out = bytearray(src) + b"\x00" * (osz - len(src)) if osz > len(src) else bytearray(src[:osz])
    end = len(patch) - 12
    pos = 0
    while p < end:
        rel, p = rvlv(patch, p)
        pos += rel
        while patch[p] != 0:
            out[pos] ^= patch[p]
            pos += 1
            p += 1
        p += 1  # skip terminator
        pos += 1
    return bytes(out)

rt = apply_ups(src, bytes(patch))
print("round-trip:", "OK" if rt == dst else "FAIL")
