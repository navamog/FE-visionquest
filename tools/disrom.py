# -*- coding: utf-8 -*-
"""Disassemble THUMB code around the refs to 0x0815D48C to read the text lookup logic."""
import struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROM_PATH = r"D:\Works\FEv\Fire Emblem - Vision Quest (v2.3).gba"
rom = open(ROM_PATH, "rb").read()
p32 = lambda o: struct.unpack_from("<I", rom, o)[0]

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.skipdata = True

def dis(start, end, label=""):
    print(f"\n===== {label} rom[{start:#x}..{end:#x}] =====")
    for ins in md.disasm(rom[start:end], 0x08000000 + start):
        extra = ""
        # annotate pc-relative loads
        if ins.mnemonic == "ldr" and "[pc" in ins.op_str:
            try:
                imm = int(ins.op_str.split("#")[1].rstrip("]"), 0)
                lit = ((ins.address + 4) & ~3) + imm
                extra = f"   ; ={p32(lit - 0x08000000):#010x}"
            except Exception:
                pass
        print(f"{ins.address:08x}: {ins.mnemonic:8s} {ins.op_str}{extra}")

start = int(sys.argv[1], 0)
end = int(sys.argv[2], 0)
dis(start, end, sys.argv[3] if len(sys.argv) > 3 else "")
