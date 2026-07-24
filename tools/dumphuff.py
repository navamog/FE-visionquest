# -*- coding: utf-8 -*-
"""Decompress the huffman-compressed (vanilla-style) strings.

GBAFE huffman: tree root pointer stored right before the vanilla text table.
Node = 4 bytes (two u16). If right == 0xFFFF: leaf, emit low byte of left
(and high byte too if nonzero: 2-byte char). Else bit0->left node idx, bit1->right.
Bits are read LSB-first from the compressed byte stream.
"""
import struct

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
SIZE = len(rom)
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]
p16 = lambda o: struct.unpack_from("<H", rom, o)[0]

# candidate root-pointer locations near the vanilla table
for loc in (0x15D488, 0x15D484, 0x15D480):
    v = p32(loc)
    print(f"@{loc:#x}: {v:#010x}")

ROOT_PTR_LOC = 0x15D488
root = p32(ROOT_PTR_LOC) - 0x08000000
print(f"huffman root node at {root:#x}, data: {rom[root:root+8].hex()}")
# root's children pointers/table base? In FE8, the value at 0x15D488 points to the
# ROOT NODE itself; tree nodes referenced by index from tree base at 0x15A72C? Try:
# decode using node addresses: node = addr; left = base + idx*4 ...
# Simplest known-good approach (FEBuilder): root at R; each node 4 bytes {u16 a, u16 b};
# if b == 0xFFFF -> leaf(a); else internal: bit ? node b : node a (indices into tree base).
TREE_BASE = None

def decode(off, tree_base, root_off, maxlen=4096):
    out = []
    bitpos = 0
    node = root_off
    i = off
    while len(out) < maxlen:
        a = p16(node)
        b = p16(node + 2)
        if b == 0xFFFF:
            lo = a & 0xFF
            hi = a >> 8
            if lo == 0:
                break
            out.append(lo)
            if hi:
                out.append(hi)
            node = root_off
            continue
        bit = (rom[i + (bitpos >> 3)] >> (bitpos & 7)) & 1
        bitpos += 1
        node = tree_base + 4 * (b if bit else a)
    return bytes(out)

# try tree base = root? In FE8U the root ptr points into the node array; children are
# indices relative to the ARRAY base. Find array base: nodes are before root typically.
# Try assuming array base = 0x15A72C (fe8u decomp gMsgHuffmanTable).
CTRL = {0x01: "[NL]", 0x03: "[A]"}
def render(bs):
    return "".join(chr(c) if 32 <= c < 127 else f"[{c:02X}]" for c in bs)

TABLE = 0x1024D7C
test_targets = [(1, p32(TABLE + 4) - 0x08000000), (3, p32(TABLE + 12) - 0x08000000)]
for base in (0x15A72C, root & ~3, p32(0x15D484) - 0x08000000 if 0x08000000 <= p32(0x15D484) < 0x08000000 + SIZE else None):
    if base is None:
        continue
    try:
        bs = decode(test_targets[0][1], base, root)
        print(f"base {base:#x}: idx1 -> {render(bs[:60])!r}")
    except Exception as e:
        print(f"base {base:#x}: error {e}")
