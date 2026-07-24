# -*- coding: utf-8 -*-
"""Verify all sys_tl_part*.py: parse, EUC-KR encodable, control-token multiset
matches the English source (system_en.tsv), report coverage + conflicts."""
import importlib.util, glob, os, re, sys

TOKEN = re.compile(r"\[([0-9A-Fa-f]{2}|X|NL|A)\]")

def toks(s):
    # normalize: [X]->[00], [NL]->[01], [A]->[03] for comparison
    out = []
    for m in TOKEN.finditer(s):
        t = m.group(1)
        out.append({"X": "00", "NL": "01", "A": "03"}.get(t, t.upper()))
    return sorted(out)

# load english source tokens
src = {}
for line in open(r"D:\Works\FEv\text\system_en.tsv", encoding="utf-8"):
    idx, _, en = line.rstrip("\n").partition("\t")
    src[int(idx, 16)] = en

parts = sorted(glob.glob(r"D:\Works\FEv\tools\sys_tl_part0[0-3].py"))
all_t = {}
conflicts = []
for p in parts:
    spec = importlib.util.spec_from_file_location(os.path.basename(p)[:-3], p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for k, v in m.T.items():
        if k in all_t:
            conflicts.append(k)
        all_t[k] = v
    print(f"{os.path.basename(p)}: {len(m.T)} entries")

print(f"\ntotal merged: {len(all_t)}  conflicts: {len(conflicts)}")

# checks
euc_fail, tok_mismatch, missing = [], [], []
for k, en in src.items():
    if k not in all_t:
        missing.append(k)
        continue
    ko = all_t[k]
    try:
        TOKEN.sub("", ko).encode("euc-kr")
    except Exception:
        euc_fail.append(k)
    if toks(en) != toks(ko):
        tok_mismatch.append((k, en, ko))

print(f"missing (in src, not translated): {len(missing)}")
print(f"euc-kr fails: {len(euc_fail)} {[hex(x) for x in euc_fail[:10]]}")
print(f"token mismatches: {len(tok_mismatch)}")
for k, en, ko in tok_mismatch[:15]:
    print(f"  0x{k:04X}: EN{toks(en)} != KO{toks(ko)}")
    print(f"     en={en!r}")
    print(f"     ko={ko!r}")
