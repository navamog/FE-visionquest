# -*- coding: utf-8 -*-
"""Build the Korean test ROM for FE Vision Quest v3.

 1. Render KS X 1001 2,350 Hangul syllables (Gulim 12px) into a glyph bank:
    Glyph = {u32 next=0, u8 sjisByte=0, u8 width, u16 pad, u32 bitmap[16]} = 0x48 B.
    Bank index = (b1-0xB0)*94 + (b2-0xA1) for EUC-KR bytes (b1,b2).
 2. Assemble THUMB hooks replacing the 4 ASCII text functions with EUC-KR-aware
    versions. Keystone constraints: named labels only, literals as .word after ldr.
 3. Trampolines at 0x44C8 / 0x4504 / 0x4538 / 0x4568.
 4. Inject Korean test strings (table entries |0x80000000).
 5. Emit out/vq3kr.gba.
"""
import struct, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB, KS_MODE_LITTLE_ENDIAN

ROM_IN = r"D:\Works\FEv\Fire Emblem - Vision Quest v3.0.GBA"
ROM_OUT = r"D:\Works\FEv\out\vq3kr.gba"
os.makedirs(r"D:\Works\FEv\out", exist_ok=True)

rom = bytearray(open(ROM_IN, "rb").read())
orig_len = len(rom)

def align(n, a):
    return (n + a - 1) & ~(a - 1)

BANK_OFF = align(orig_len, 16)
NSYL = 94 * 25
GLYPH_SZ = 0x48
BANK_SZ = NSYL * GLYPH_SZ
CODE_OFF = align(BANK_OFF + BANK_SZ, 16)
BANK_ADDR = 0x08000000 + BANK_OFF
CODE_ADDR = 0x08000000 + CODE_OFF

# ---------- 1) glyph bank ----------
FONT = ImageFont.truetype(r"C:\Windows\Fonts\gulim.ttc", 12, index=0)
YOFF = 2

def render_syllable(ch):
    img = Image.new("L", (18, 18), 0)
    ImageDraw.Draw(img).text((0, YOFF), ch, fill=255, font=FONT)
    a = (np.array(img)[:16, :16] > 96)
    ink = a.astype(np.uint8) * 3
    sh = np.zeros_like(ink)
    sh[:, 1:] = (a[:, :-1] & ~a[:, 1:]) * 2
    grid = np.maximum(ink, sh)
    xs = np.where(a.any(axis=0))[0]
    width = min((int(xs[-1]) + 2) if len(xs) else 6, 16)
    return grid, width

print("rendering glyph bank...")
bank = bytearray(BANK_SZ)
for b1 in range(0xB0, 0xC9):
    for b2 in range(0xA1, 0xFF):
        ch = bytes((b1, b2)).decode("euc-kr")
        grid, width = render_syllable(ch)
        idx = (b1 - 0xB0) * 94 + (b2 - 0xA1)
        off = idx * GLYPH_SZ
        struct.pack_into("<IBBH", bank, off, 0, 0, width, 0)
        rows = grid.astype(np.uint32)
        for y in range(16):
            row = 0
            for x in range(16):
                row |= int(rows[y, x]) << (2 * x)
            struct.pack_into("<I", bank, off + 8 + 4 * y, row)
print(f"bank: {BANK_SZ:#x} bytes @ ROM {BANK_OFF:#x}")

# ---------- 2) hooks ----------
# Function order: only backward calls between functions (bl works both ways, but
# label_addr() re-assembles closed prefixes). Literals live after each function.
ASM = f"""
kr_lookup:
    cmp r0, #0xB0
    blo kl_ascii
    cmp r0, #0xC8
    bhi kl_ascii
    ldrb r3, [r4, #1]
    cmp r3, #0xA1
    blo kl_ascii
    subs r0, #0xB0
    movs r2, #94
    muls r0, r2
    subs r3, #0xA1
    adds r0, r0, r3
    movs r2, #0x48
    muls r0, r2
    ldr r1, kl_bank
    adds r1, r1, r0
    movs r0, #2
    bx lr
kl_ascii:
    ldr r3, kl_font
    ldr r3, [r3]
    ldr r2, [r3, #4]
    lsls r0, r0, #2
    adds r0, r0, r2
    ldr r1, [r0]
    cmp r1, #0
    bne kl_got
    adds r2, #0xFC
    ldr r1, [r2]
kl_got:
    movs r0, #1
    bx lr
    .align 2
kl_bank: .word {BANK_ADDR:#x}
kl_font: .word 0x02028E70

kr_thunk2:
    bx r2

kr_drawchar:
    push {{r4, r5, lr}}
    adds r5, r0, #0
    adds r4, r1, #0
    ldrb r0, [r4]
    bl kr_lookup
    adds r4, r0, r4
    ldr r3, kdc_font
    ldr r3, [r3]
    ldr r2, [r3, #8]
    adds r0, r5, #0
    bl kr_thunk2
    adds r0, r4, #0
    pop {{r4, r5}}
    pop {{r1}}
    bx r1
    .align 2
kdc_font: .word 0x02028E70

kr_drawstring:
    push {{r4, r5, lr}}
    adds r5, r0, #0
    adds r4, r1, #0
    b kds_test
kds_loop:
    ldrb r0, [r4]
    bl kr_lookup
    adds r4, r0, r4
    ldr r3, kds_font
    ldr r3, [r3]
    ldr r2, [r3, #8]
    adds r0, r5, #0
    bl kr_thunk2
kds_test:
    ldrb r0, [r4]
    cmp r0, #1
    bhi kds_loop
    pop {{r4, r5}}
    pop {{r0}}
    bx r0
    .align 2
kds_font: .word 0x02028E70

kr_charlen:
    push {{r4, r5, lr}}
    adds r4, r0, #0
    adds r5, r1, #0
    ldrb r0, [r4]
    bl kr_lookup
    adds r4, r0, r4
    ldrb r0, [r1, #5]
    str r0, [r5]
    adds r0, r4, #0
    pop {{r4, r5}}
    pop {{r1}}
    bx r1

kr_strlen:
    push {{r4, r5, lr}}
    adds r4, r0, #0
    movs r5, #0
    b ksl_test
ksl_loop:
    bl kr_lookup
    adds r4, r0, r4
    ldrb r0, [r1, #5]
    adds r5, r5, r0
ksl_test:
    ldrb r0, [r4]
    cmp r0, #1
    bhi ksl_loop
    adds r0, r5, #0
    pop {{r4, r5}}
    pop {{r1}}
    bx r1
"""

ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB | KS_MODE_LITTLE_ENDIAN)
encoding, cnt = ks.asm(ASM, CODE_ADDR)
code = bytes(encoding)
print(f"hook code: {len(code)} bytes @ ROM {CODE_OFF:#x}")

def label_addr(name):
    idx = ASM.index("\n" + name + ":")
    prefix = ASM[:idx]
    if not prefix.strip():
        return CODE_ADDR
    enc, _ = ks.asm(prefix, CODE_ADDR)
    pb = bytes(enc)
    assert code[:len(pb)] == pb, f"prefix mismatch for {name}"
    return CODE_ADDR + len(pb)

ADDR_DRAWCHAR = label_addr("kr_drawchar")
ADDR_DRAWSTR = label_addr("kr_drawstring")
ADDR_CHARLEN = label_addr("kr_charlen")
ADDR_STRLEN = label_addr("kr_strlen")
print(f"kr_drawchar={ADDR_DRAWCHAR:#x} kr_drawstring={ADDR_DRAWSTR:#x} "
      f"kr_charlen={ADDR_CHARLEN:#x} kr_strlen={ADDR_STRLEN:#x}")

# sanity: no thumb2 wide instructions (every unit 2 bytes; bl = two 2-byte halves F000-F800)
i = 0
while i < len(code):
    h = struct.unpack_from("<H", code, i)[0]
    if (h >> 11) == 0b11110:  # bl prefix
        i += 4
        continue
    assert (h >> 11) != 0b11101 and (h >> 11) != 0b11111 or (h >> 11) == 0b11111, f"wide instr? @{i}"
    i += 2

# ---------- 3) trampolines ----------
def trampoline(rom_off, target):
    assert rom_off % 4 == 0
    struct.pack_into("<HHI", rom, rom_off, 0x4B00, 0x4718, target | 1)

trampoline(0x4504, ADDR_DRAWCHAR)
trampoline(0x44C8, ADDR_DRAWSTR)
trampoline(0x4538, ADDR_CHARLEN)
trampoline(0x4568, ADDR_STRLEN)

# ---------- 4) translations ----------
TABLE = 0x1024D7C
import re, importlib.util

TOKEN = re.compile(r"\[([0-9A-Fa-f]{2}|X|NL|A)\]")

def encode_ko(s):
    """Convert a translation string with literal [X]/[NL]/[A]/[80xx] tokens into bytes.
    Text runs -> EUC-KR. Tokens -> control bytes. [X] appends 0x00 (terminator)."""
    out = bytearray()
    pos = 0
    for m in TOKEN.finditer(s):
        if m.start() > pos:
            out += s[pos:m.start()].encode("euc-kr")
        t = m.group(1)
        if t == "X":
            out += b"\x00"
        elif t == "NL":
            out += b"\x01"
        elif t == "A":
            out += b"\x03"
        else:
            out += bytes([int(t, 16)])
        pos = m.end()
    if pos < len(s):
        out += s[pos:].encode("euc-kr")
    return bytes(out)

def load_dict(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.T

# story: pre-built byte records (control codes already raw)
import story_tl
entries = {}  # id -> bytes
for tid, data in story_tl.STORY.items():
    entries[tid] = data

# token-safety guard: skip translations whose control-token multiset differs
# from the English source (protects against dropped [X]/[NL]/[80xx] in subagent output)
def src_tokens():
    d = {}
    p = os.path.join(os.path.dirname(__file__), "..", "text", "system_en.tsv")
    if not os.path.exists(p):
        return d
    for line in open(p, encoding="utf-8"):
        idx, _, en = line.rstrip("\n").partition("\t")
        d[int(idx, 16)] = _tokset(en)
    return d

def _tokset(s):
    out = []
    for m in TOKEN.finditer(s):
        t = m.group(1)
        out.append({"X": "00", "NL": "01", "A": "03"}.get(t, t.upper()))
    return sorted(out)

SRC_TOK = src_tokens()

# system: token-string dicts from subagents (optional)
import glob as _glob
sys_count, skipped = 0, 0
for part in sorted(_glob.glob(os.path.join(os.path.dirname(__file__), "sys_tl_part*.py"))):
    T = load_dict(part, os.path.basename(part)[:-3])
    for tid, s in T.items():
        if tid in SRC_TOK and _tokset(s) != SRC_TOK[tid]:
            skipped += 1
            continue  # token mismatch -> keep original, skip translation
        b = encode_ko(s)
        if not b.endswith(b"\x00"):
            b += b"\x00"
        entries[tid] = b
        sys_count += 1
print(f"translations: {len(story_tl.STORY)} story + {sys_count} system "
      f"(skipped {skipped} token-mismatch) = {len(entries)} total")

str_off = align(CODE_OFF + len(code), 4)
blob = bytearray()
for tid, enc in entries.items():
    ptr = 0x08000000 + str_off + len(blob)
    struct.pack_into("<I", rom, TABLE + 4 * tid, ptr | 0x80000000)
    blob += enc
    if len(blob) % 2:
        blob += b"\x00"
print(f"translation blob: {len(blob)} bytes @ {str_off:#x}")

# ---------- 5) emit ----------
new = bytearray(rom)
new += b"\x00" * (BANK_OFF - len(new))
new += bank
new += b"\x00" * (CODE_OFF - len(new))
new += code
new += b"\x00" * (str_off - len(new))
new += blob
new += b"\x00" * (align(len(new), 4) - len(new))
open(ROM_OUT, "wb").write(new)
print(f"wrote {ROM_OUT}: {len(new):#x} bytes")
