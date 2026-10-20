#!/usr/bin/env python3
"""Rebuild, independently of Parat, the SAT files that say "two circuits give the same outputs".
For a multiplier whose final adder was optimised by ABC, Parat proves a second circuit (cert.new.aag) and shows with
SAT that it gives the same outputs as your circuit, one file per range of 32 outputs (cert.eq<k>.cnf). This script
writes those files again from YOUR circuit file and cert.new.aag, so you can check that Parat's files say exactly
that (byte for byte), and then check Parat's proofs (cert.eq<k>.drat) with drat-trim.
Each file: variable 1 = false, variables 2.. = the shared inputs, one variable per AND gate (an AND of the same two
inputs is written once), and one clause saying "at least one output of this range differs". UNSAT = all equal.
  eq_cnf.py original.aag new.aag k out.cnf      (outputs 32k .. 32k+31)"""
import sys

def load(p):
    L = open(p).read().split("\n"); M, I, Lt, O, A = map(int, L[0].split()[1:6])
    assert Lt == 0, "latches not supported"
    ins = [int(L[1 + i]) for i in range(I)]; outs = [int(L[1 + I + i]) for i in range(O)]
    gates = [tuple(map(int, L[1 + I + O + i].split())) for i in range(A)]
    return ins, outs, gates

(ia, oa, ga), (ib, ob, gb) = load(sys.argv[1]), load(sys.argv[2]); k = int(sys.argv[3])
assert len(ia) == len(ib) and len(oa) == len(ob), "inputs/outputs differ in number"
lo, hi = 32 * k, min(32 * k + 32, len(oa))
G = [(ia, oa, ga), (ib, ob, gb)]
need = []
for ins, outs, gates in G:                 # only the gates these outputs need
    d = {a // 2: (b, c) for a, b, c in gates}; nd = set(); st = [outs[i] // 2 for i in range(lo, hi)]
    while st:
        v = st.pop()
        if v <= 0 or v in nd or v not in d: continue
        nd.add(v); b, c = d[v]; st += [b // 2, c // 2]
    need.append(nd)
mp = [{}, {}]; nv = 1
for xa, xb in zip(ia, ib): nv += 1; mp[0][xa // 2] = nv; mp[1][xb // 2] = nv
def lit(s, l):
    if l // 2 == 0: return -1 if l & 1 else 1      # var 1 is false: literal 0 -> 1, literal 1 -> -1
    v = mp[s][l // 2]; return -v if l & 1 else v
cl = []; H = {}
for s in range(2):
    for a, b, c in G[s][2]:
        if a // 2 not in need[s]: continue
        x1, x2 = lit(s, b), lit(s, c); key = (min(x1, x2), max(x1, x2))
        if key in H: mp[s][a // 2] = H[key]; continue
        nv += 1; y = nv; H[key] = y; mp[s][a // 2] = y
        cl += [[-y, x1], [-y, x2], [y, -x1, -x2]]
ds = []
for i in range(lo, hi):
    x, z = lit(0, oa[i]), lit(1, ob[i]); nv += 1; ds.append(nv)
    cl += [[-nv, x, z], [-nv, -x, -z]]
with open(sys.argv[4], "w") as f:
    f.write(f"p cnf {nv} {len(cl) + 2}\n-1 0\n")
    for c in cl: f.write(" ".join(map(str, c)) + " 0\n")
    f.write(" ".join(map(str, ds)) + " 0\n")
