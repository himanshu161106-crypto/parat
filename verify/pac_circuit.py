#!/usr/bin/env python3
"""Check, independently of Parat, that a PAC certificate is about YOUR circuit and says "outputs = a*b".

pacheck2 checks that cert.proof derives cert.spec from the polynomials in cert.polys. It does not know where those
polynomials came from. This script closes that gap. It reads the circuit (.aag) and checks:
  1. every polynomial in cert.polys is a true fact about this circuit: the definition of one of its AND gates
     (-g + x*y), of one output (-s + x), or the modulus 2^O (O = number of outputs). One extra or changed line
     (a fake fact) makes the check fail. A certificate made for another circuit fails here;
  2. cert.spec equals  sum 2^i s_i - a*b  (unsigned, or two's complement signed) modulo 2^O.
Exit 0 only if both hold. Constants and repeated inputs are folded with the identities x&0 = 0, x&!x = 0, x&1 = x,
x&x = x (all true), the same way Parat writes its file. Inputs: first half a0.., second half b0..; outputs s0...
  pac_circuit.py circuit.aag cert.polys cert.spec"""
import sys, re

def fail(msg):
    print("pac_circuit: FAIL: " + msg); sys.exit(1)

def load_aag(path):
    with open(path) as f:
        hdr = f.readline().split()
        if len(hdr) < 6 or hdr[0] != "aag": fail("not an ASCII AIGER file: " + path)
        M, I, L, O, A = map(int, hdr[1:6])
        if L: fail("latches are not supported")
        ins = [int(f.readline()) for _ in range(I)]
        outs = [int(f.readline()) for _ in range(O)]
        gates = [tuple(map(int, f.readline().split())) for _ in range(A)]
    return M, ins, outs, gates

TERM = re.compile(r"([+-]?)([^+-]+)")
def parse_poly(text, where):
    """'-g3+1-g4*g5+2*s1' -> {frozenset(names): int}; Boolean variables (x*x = x)."""
    text = text.strip()
    if text.endswith(";"): text = text[:-1]
    text = text.replace(" ", "")
    if not text: fail("empty polynomial in " + where)
    p, pos = {}, 0
    for m in TERM.finditer(text):
        if m.start() != pos: fail("cannot read polynomial in " + where)
        pos = m.end()
        sign = -1 if m.group(1) == "-" else 1
        coef, mono = sign, set()
        for fac in m.group(2).split("*"):
            if fac.isdigit(): coef *= int(fac)
            elif re.fullmatch(r"[a-z][0-9]+", fac): mono.add(fac)
            else: fail("unknown factor '%s' in %s" % (fac, where))
        k = frozenset(mono); p[k] = p.get(k, 0) + coef
        if p[k] == 0: del p[k]
    if pos != len(text): fail("cannot read polynomial in " + where)
    return p

def key(p): return tuple(sorted((tuple(sorted(m)), c) for m, c in p.items()))

def main():
    if len(sys.argv) != 4: print(__doc__); sys.exit(2)
    M, ins, outs, gates = load_aag(sys.argv[1])
    I, O = len(ins), len(outs)
    if I % 2: fail("odd number of inputs")
    w = I // 2; T = M + 1
    name = {}
    for i, l in enumerate(ins):
        if l & 1 or l < 2: fail("input literal %d is not a plain variable" % l)
        name[l >> 1] = ("a%d" % i) if i < w else ("b%d" % (i - w))
    mp = {v: v for v in range(1, M + 1)}
    def axl(l):                       # AIGER literal -> folded signed literal (T = true, -T = false)
        v = l >> 1; x = mp[v] if v else -T
        return -x if l & 1 else x
    def lp(x):                        # signed literal -> polynomial
        if x == T: return {frozenset(): 1}
        if x == -T: return {}
        v = abs(x); n = name.get(v, "g%d" % v)
        return {frozenset([n]): 1} if x > 0 else {frozenset(): 1, frozenset([n]): -1}
    def mul(p, q):
        r = {}
        for m1, c1 in p.items():
            for m2, c2 in q.items():
                m = m1 | m2; r[m] = r.get(m, 0) + c1 * c2
                if r[m] == 0: del r[m]
        return r
    def add(p, q, s=1):
        r = dict(p)
        for m, c in q.items():
            r[m] = r.get(m, 0) + s * c
            if r[m] == 0: del r[m]
        return r
    allowed = {}
    for y, a, b in gates:
        Y = y >> 1; la, lb = axl(a), axl(b)
        if la == -T or lb == -T or la == -lb: mp[Y] = -T; continue
        if la == T: mp[Y] = lb; continue
        if lb == T or la == lb: mp[Y] = la; continue
        allowed[key(add(mul(lp(la), lp(lb)), {frozenset(["g%d" % Y]): 1}, -1))] = "gate g%d" % Y
    for i, l in enumerate(outs):
        allowed[key(add(lp(axl(l)), {frozenset(["s%d" % i]): 1}, -1))] = "output s%d" % i
    mod = 1 << O
    n_lines = n_gate = n_out = 0
    with open(sys.argv[2]) as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            parts = line.split(None, 1)
            if len(parts) != 2: fail("polys line %d: no index" % ln)
            p = parse_poly(parts[1], "polys line %d" % ln); n_lines += 1
            if not p: continue                                   # 0 = 0: no information
            if len(p) == 1 and frozenset() in p:
                if p[frozenset()] % mod: fail("polys line %d: constant %d is not a multiple of 2^%d" % (ln, p[frozenset()], O))
                continue
            what = allowed.get(key(p))
            if what is None: fail("polys line %d is not the definition of any gate or output of this circuit" % ln)
            if what.startswith("gate"): n_gate += 1
            else: n_out += 1
    with open(sys.argv[3]) as f: spec = parse_poly(f.read(), "spec")
    S = {}
    for i in range(O): S = add(S, {frozenset(["s%d" % i]): 1 << i})
    def ab(signed):
        r = {}
        for i in range(w):
            for j in range(w):
                c = 1 << (i + j)
                if signed and ((i == w - 1) != (j == w - 1)): c = -c
                r = add(r, {frozenset(["a%d" % i, "b%d" % j]): c})
        return r
    found = None
    for signed in (False, True):
        d = add(spec, add(S, ab(signed), -1), -1)
        if all(c % mod == 0 for c in d.values()): found = "signed" if signed else "unsigned"; break
    if not found: fail("cert.spec is not 'outputs = a*b (mod 2^%d)' for this circuit's inputs and outputs" % O)
    print("pac_circuit: OK: %d polynomials, every one a gate (%d) or output (%d) of this circuit or the modulus;"
          " spec = a*b mod 2^%d (%s)" % (n_lines, n_gate, n_out, O, found))

main()
