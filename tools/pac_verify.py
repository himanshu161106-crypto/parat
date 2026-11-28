#!/usr/bin/env python3
"""pac_verify.py - check a Parat PAC certificate for an unsigned n x n multiplier, piece by piece.

  python pac_verify.py circuit.aig cert [--pacheck PATH] [--chunk-mb 300] [--work DIR] [--keep]

Reads circuit.aig (or .aag) and the three files cert.polys, cert.proof, cert.spec written by
`parat circuit.aig 1 T --pac cert`. Needs only Python 3 (standard library) and the pacheck program
(PAC checker by D. Kaufmann, A. Biere and others: https://github.com/d-kfmnn/pacheck2).

What is checked, and why that is enough:
 1. cert.polys: every line must be exactly the polynomial of one gate or output of circuit.aig
    (-g + L(x)*L(y) for g = x AND y, -s_k + L(o_k) for output k, with L(x) = x or 1-x), or line 1 = 2^W
    (W = number of outputs; it makes the proof work modulo 2^W). This script builds these polynomials from the
    AIG itself, so nothing written by Parat is trusted here.
 2. cert.spec must be exactly  sum_k 2^k s_k - sum_{i,j} 2^(i+j) a_i b_j  (a = first half of the inputs,
    b = second half, least significant bit first): the product of a and b equals the outputs, modulo 2^W.
    W = 2n, so modulo 2^W is the full product.
 3. cert.proof is cut into pieces of about --chunk-mb MB. Each piece is given to pacheck together with the
    lines it uses from outside the piece ("axioms"). Every axiom must be a line of cert.polys (checked in 1) or a
    line of an earlier piece (checked by pacheck before). pacheck checks every step of the piece; the target of
    the last piece is cert.spec (checked in 2). Only the rules "%" (linear combination) and "d" (delete) are
    accepted.
So: if this script prints "s CERTIFICATE CHECKED", pacheck has checked a derivation of the spec from the gates of
circuit.aig, and the circuit multiplies correctly. Trusted: this script, pacheck, and the AIG file.
"""
import sys, os, re, subprocess, argparse, time, hashlib
from array import array

def die(msg):
    print("s CERTIFICATE NOT CHECKED")
    print("c reason: " + msg)
    sys.exit(1)

# ---------------------------------------------------------------- AIG
def read_aig(path):
    f = open(path, 'rb')
    hdr = f.readline().split()
    fmt = hdr[0].decode(); M, I, L, O, A = map(int, hdr[1:6])
    if L != 0: die("the circuit has latches")
    outs = []
    gates = array('i', [0]) * (2 * (A))       # rhs0, rhs1 per AND, in order
    lhs = array('i', [0]) * A
    if fmt == 'aag':
        ins = [int(f.readline().split()[0]) for _ in range(I)]
        outs = [int(f.readline().split()[0]) for _ in range(O)]
        for k in range(A):
            x, y, z = map(int, f.readline().split()[:3]); lhs[k] = x; gates[2 * k] = y; gates[2 * k + 1] = z
        invars = [l >> 1 for l in ins]
    elif fmt == 'aig':
        outs = [int(f.readline().split()[0]) for _ in range(O)]
        invars = list(range(1, I + 1))
        data = f.read(); p = 0
        def dec():
            nonlocal p
            x = 0; i = 0
            while True:
                c = data[p]; p += 1
                x |= (c & 0x7f) << (7 * i)
                if c & 0x80 == 0: return x
                i += 1
        for k in range(A):
            l = 2 * (I + L + k + 1); d0 = dec(); d1 = dec()
            r0 = l - d0; r1 = r0 - d1
            lhs[k] = l; gates[2 * k] = r0; gates[2 * k + 1] = r1
    else: die("unknown AIGER format " + fmt)
    return I, O, invars, outs, lhs, gates

# ---------------------------------------------------------------- polynomials
TERM = re.compile(rb'([+-]?)([0-9]*)(\*?)([A-Za-z_][A-Za-z0-9_]*(?:\*[A-Za-z_][A-Za-z0-9_]*)*)?')

def parse_poly(t):
    """text -> {monomial (sorted tuple of names): integer}, multilinear (x*x = x)"""
    t = t.strip().rstrip(b';').strip()
    if t.startswith(b'(') and t.endswith(b')'): t = t[1:-1]
    P = {}; pos = 0; n = len(t)
    if n == 0: return P
    while pos < n:
        m = TERM.match(t, pos)
        if not m or m.end() == pos: die("cannot read polynomial near: " + t[pos:pos + 60].decode(errors='replace'))
        sg, num, star, mono = m.groups()
        if num == b'' and mono is None: die("cannot read polynomial near: " + t[pos:pos + 60].decode(errors='replace'))
        c = int(num) if num else 1
        if sg == b'-': c = -c
        if num and mono and not star: die("bad term near: " + t[pos:pos + 60].decode(errors='replace'))
        key = tuple(sorted(set(mono.split(b'*')))) if mono else ()
        P[key] = P.get(key, 0) + c
        if P[key] == 0: del P[key]
        pos = m.end()
    return P

def lit_poly(l, name):
    """L(l) as {monomial: coef}"""
    if l == 0: return {}
    if l == 1: return {(): 1}
    v = name(l >> 1)
    return {(v,): 1} if l % 2 == 0 else {(): 1, (v,): -1}

def mul(P, Q):
    R = {}
    for a, x in P.items():
        for b, y in Q.items():
            k = tuple(sorted(set(a) | set(b))); R[k] = R.get(k, 0) + x * y
            if R[k] == 0: del R[k]
    return R

def add_to(P, Q, s=1):
    for k, c in Q.items():
        P[k] = P.get(k, 0) + s * c
        if P[k] == 0: del P[k]
    return P

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('aig'); ap.add_argument('cert')
    ap.add_argument('--pacheck', default=None); ap.add_argument('--chunk-mb', type=float, default=300.0)
    ap.add_argument('--work', default=None); ap.add_argument('--keep', action='store_true')
    ap.add_argument('--jobs', type=int, default=1, help='pieces checked at the same time')
    ap.add_argument('--log', default=None, help='also write everything printed to this file')
    ap.add_argument('--follow', action='store_true', help='check while Parat is still writing the proof (waits for CERT.ready, ends at CERT.done; CERT.exited without CERT.done = Parat stopped)')
    a = ap.parse_args()
    if a.log:
        class Tee:
            def __init__(s, *f): s.f = f
            def write(s, x):
                for f in s.f: f.write(x)
            def flush(s):
                for f in s.f: f.flush()
        sys.stdout = Tee(sys.stdout, open(a.log, 'a'))
    t0 = time.time()
    pk = a.pacheck
    if not pk:
        here = os.path.dirname(os.path.abspath(__file__))
        for c in ['pacheck.exe', 'pacheck']:
            if os.path.exists(os.path.join(here, c)): pk = os.path.join(here, c); break
        if not pk: pk = 'pacheck'
    if os.path.exists(pk): pk = os.path.abspath(pk)
    work = a.work or (a.cert + '_chunks'); os.makedirs(work, exist_ok=True)
    fpol, fprf, fspec = a.cert + '.polys', a.cert + '.proof', a.cert + '.spec'
    def parat_gone(): return a.follow and os.path.exists(a.cert + '.exited') and not os.path.exists(a.cert + '.done')
    if a.follow:
        print("c waiting for Parat to write %s.polys and %s.spec ..." % (a.cert, a.cert)); sys.stdout.flush()
        while not os.path.exists(a.cert + '.ready'):
            if parat_gone(): die("Parat stopped before writing the certificate")
            time.sleep(2)
    for x in (fpol, fprf, fspec):
        if not os.path.exists(x): die("missing file " + x)

    I, O, invars, outs, lhs, gates = read_aig(a.aig)
    if I % 2: die("odd number of inputs")
    n = I // 2; W = O
    if W != 2 * n: die("expected %d outputs for %d x %d bits, found %d" % (2 * n, n, n, W))
    names = {}
    for i, v in enumerate(invars): names[v] = ('a%d' % i if i < n else 'b%d' % (i - n)).encode()
    def name(v): return names.get(v) or b'g%d' % v
    # the same simplification Parat makes while reading: AND with false or x AND not x = false, AND with true = the
    # other input, x AND x = x. A literal is +v / -v (variable v, negated), T = true, -T = false.
    M = max([v for v in invars] + [l >> 1 for l in lhs] + [0]); T = M + 1
    mp = array('i', range(M + 2))
    def AXL(l):
        v = mp[l >> 1] if l >> 1 else -T
        return -v if l & 1 else v
    ga = array('i', [0]) * (M + 2); gb = array('i', [0]) * (M + 2)   # var -> inputs of its AND gate (0: not a gate)
    for k in range(len(lhs)):
        Y = lhs[k] >> 1; la = AXL(gates[2 * k]); lb = AXL(gates[2 * k + 1])
        if la == -T or lb == -T or la == -lb: mp[Y] = -T; continue
        if la == T: mp[Y] = lb; continue
        if lb == T or la == lb: mp[Y] = la; continue
        ga[Y] = la; gb[Y] = lb
    ngate = sum(1 for x in ga if x)
    outl = [AXL(l) for l in outs]
    def L(x):
        if x == T: return {(): 1}
        if x == -T: return {}
        return {(name(x),): 1} if x > 0 else {(): 1, (name(-x),): -1}
    print("c circuit: %d x %d bits, %d outputs, %d AND gates (%d after folding constants and repeated inputs)" % (n, n, W, len(lhs), ngate)); sys.stdout.flush()

    # 1. polys
    offs = array('q'); lens = array('i'); nlines = 0
    with open(fpol, 'rb') as f:
        pos = 0
        for line in f:
            s = line.strip()
            if not s: pos += len(line); continue
            sp = s.index(b' '); pid = int(s[:sp]); body = s[sp + 1:]
            while len(offs) <= pid: offs.append(-1); lens.append(0)
            if offs[pid] >= 0: die("polys: id %d given twice" % pid)
            offs[pid] = pos; lens[pid] = len(line); pos += len(line); nlines += 1
            P = parse_poly(body)
            if pid == 1 and P == {(): 1 << W}: continue
            first = re.match(rb'-([sg])([0-9]+)', body)
            if not first: die("polys line %d is not a gate or output polynomial" % pid)
            kind, idx = first.group(1), int(first.group(2))
            if kind == b's':
                if idx >= W: die("polys line %d: no output s%d" % (pid, idx))
                E = add_to({(b's%d' % idx,): -1}, L(outl[idx]))
            else:
                if idx > M or not ga[idx]: die("polys line %d: g%d is not an AND gate of the circuit" % (pid, idx))
                E = add_to({(name(idx),): -1}, mul(L(ga[idx]), L(gb[idx])))
            if P != E: die("polys line %d is not the polynomial of %s%d in the circuit" % (pid, kind.decode(), idx))
    if len(offs) < 2 or offs[1] < 0: die("polys: line 1 (the modulus 2^W) missing")
    print("c polys: %d lines, each one a gate or output of the circuit (%.0f s)" % (nlines, time.time() - t0)); sys.stdout.flush()

    # 2. spec, term by term: s_k -> 2^k, a_i*b_j -> -2^(i+j), every one exactly once (read in blocks, any size)
    TERMRE = re.compile(rb'([+-]?)([0-9]*)(\*?)([A-Za-z0-9_*]*)')
    def spec_ok(f, start, end, what):
        seen_s = bytearray(W); seen_ab = bytearray(n * n); cnt = 0; f.seek(start); left = end - start; rest = b''
        while True:
            blk = f.read(min(left, 1 << 26)) if left > 0 else b''; left -= len(blk)
            buf = rest + blk
            if left > 0:
                cut = max(buf.rfind(b'+'), buf.rfind(b'-'))
                if cut <= 0: rest = buf; continue
                part, rest = buf[:cut], buf[cut:]
            else:
                part, rest = buf.strip().rstrip(b';').strip(), b''
            for m in TERMRE.finditer(part):
                if m.end() == m.start(): continue
                sg, num, star, mono = m.groups()
                c = int(num) if num else 1
                if sg == b'-': c = -c
                vs = mono.split(b'*') if mono else []
                if len(vs) == 1 and vs[0].startswith(b's'):
                    k = int(vs[0][1:])
                    if k >= W or seen_s[k] or c != 1 << k: die(what + ": wrong term for s%d" % k)
                    seen_s[k] = 1
                elif len(vs) == 2:
                    x, y = sorted(vs)
                    if not (x.startswith(b'a') and y.startswith(b'b')): die(what + ": unexpected term " + mono.decode())
                    i2, j2 = int(x[1:]), int(y[1:])
                    if i2 >= n or j2 >= n or seen_ab[i2 * n + j2] or c != -(1 << (i2 + j2)): die(what + ": wrong term for a%d*b%d" % (i2, j2))
                    seen_ab[i2 * n + j2] = 1
                else: die(what + ": unexpected term " + (mono or b'').decode())
                cnt += 1
            if left <= 0: break
        if cnt != W + n * n or not all(seen_s) or not all(seen_ab): die(what + ": terms missing")
        return cnt
    with open(fspec, 'rb') as f: cnt = spec_ok(f, 0, os.path.getsize(fspec), "spec")
    del ga, gb, mp, lhs, gates
    print("c spec: exactly  sum 2^k s_k - sum 2^(i+j) a_i b_j  (%d terms) (%.0f s)" % (cnt, time.time() - t0)); sys.stdout.flush()

    # 3. proof, piece by piece
    dcon = array('q'); dend = array('q')        # derived id -> offset of its conclusion, end of line
    limit = int(a.chunk_mb * 1048576)
    fp = open(fprf, 'rb'); fpo = open(fpol, 'rb')
    cur = []; cur_bytes = 0; cur_ids = set(); ax = set(); nchunk = 0; checked = 0; nsteps = 0; lastid = -1
    def is_known_derived(i): return i < len(dcon) and dcon[i] >= 0

    def copy(src, off, ln, g):                  # copy ln bytes from src at off into g, in blocks
        src.seek(off)
        while ln > 0:
            b = src.read(min(ln, 1 << 26))
            if not b: die("unexpected end of the proof file")
            g.write(b); ln -= len(b)

    running = []
    def reap(block):                            # collect finished pacheck runs; block: wait for at least one
        nonlocal checked
        while True:
            done_any = False
            for it in list(running):
                pr, k, nst, nb, nax, ts, files = it
                mem = ''
                if hasattr(os, 'wait4'):
                    pid, st, ru = os.wait4(pr.pid, os.WNOHANG)
                    if pid == 0: continue
                    pr.returncode = os.waitstatus_to_exitcode(st); mem = ', pacheck %.1f GB' % (ru.ru_maxrss / 1048576.0)
                elif pr.poll() is None: continue
                running.remove(it); done_any = True
                out = open(files[2], 'rb').read().decode(errors='replace')
                if pr.returncode != 0 or 'INFERENCES CHECKED' not in out:
                    for o in running: o[0].kill()
                    tail = '\n'.join(out.strip().splitlines()[-6:])
                    die("pacheck rejected piece %d (exit %d):\n%s" % (k, pr.returncode, tail))
                checked += nst
                print("c piece %d: %d steps, %.0f MB, %d axioms: pacheck: every step correct (%.0f s; total %.0f s%s)" % (k, nst, nb / 1048576, nax, time.time() - ts, time.time() - t0, mem)); sys.stdout.flush()
                if not a.keep:
                    for x in files: os.remove(x)
            if done_any or not block or not running: return
            time.sleep(0.2)

    def flush():
        nonlocal cur, cur_bytes, cur_ids, ax, nchunk, checked, nsteps
        if not cur: return
        nchunk += 1
        cp, cq = os.path.join(work, 'piece%d.polys' % nchunk), os.path.join(work, 'piece%d.proof' % nchunk)
        with open(cp, 'wb') as g:
            for r in sorted(ax):
                if r < len(offs) and offs[r] >= 0 and not is_known_derived(r):
                    fpo.seek(offs[r]); g.write(fpo.read(lens[r]).rstrip(b'\r\n') + b'\n')
                elif is_known_derived(r):
                    g.write(b'%d ' % r); copy(fp2, dcon[r], dend[r] - dcon[r], g); g.write(b'\n')
                else: die("proof piece %d uses line %d, which is not in the polys and not checked before" % (nchunk, r))
        with open(cq, 'wb') as g:
            for (lid, typ, off, ln) in cur:
                if typ == b'd' and not (lid in cur_ids or lid in ax): continue
                copy(fp2, off, ln, g)
        pre = None
        if os.name != 'nt':
            import resource
            def pre(): resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        lgn = os.path.join(work, 'piece%d.log' % nchunk); lg = open(lgn, 'wb')
        pr = subprocess.Popen([pk, cp, cq], stdout=lg, stderr=subprocess.STDOUT, preexec_fn=pre); lg.close()
        running.append((pr, nchunk, sum(1 for c in cur if c[1] == b'%'), cur_bytes, len(ax), time.time(), (cp, cq, lgn)))
        while len(running) >= max(1, a.jobs): reap(True)
        cur = []; cur_bytes = 0; cur_ids = set(); ax = set()

    # the proof is read in blocks of 64 MB: a line can be many GB, only its line ids are kept.
    # buf[lo:] is the unread part; base is the file offset of buf[0].
    fp2 = open(fprf, 'rb')
    BLK = int(os.environ.get('PACV_BLK', 1 << 26))
    buf = b''; base = 0; lo = 0; eof = False
    def more():
        nonlocal buf, base, lo, eof
        if eof: return False
        b = fp.read(BLK)
        while not b and a.follow and not os.path.exists(a.cert + '.done'):
            if parat_gone(): die("Parat stopped before the proof was complete")
            reap(False); time.sleep(2); b = fp.read(BLK)
        if not b: eof = True; return False
        if lo: buf = buf[lo:]; base += lo; lo = 0
        buf += b; return True
    HDR = re.compile(rb'([0-9]+) (%|d)')
    WS = b'\n\r \t'
    while True:
        while len(buf) - lo < 64 and more(): pass
        while lo < len(buf) and buf[lo] in WS: lo += 1
        if lo >= len(buf):
            if not more(): break
            continue
        while len(buf) - lo < 64 and more(): pass
        m = HDR.match(buf, lo)
        if not m: die("proof: only the rules %% and d are accepted (line at byte %d)" % (base + lo))
        lid = int(m.group(1)); typ = m.group(2); off = base + lo
        if typ == b'd':
            e = buf.find(b'\n', lo)
            while e < 0 and more(): e = buf.find(b'\n', lo)
            if e < 0: e = len(buf)
            if not re.fullmatch(rb'[0-9]+ d\s*;\s*', buf[lo:e]): die("proof: bad delete line at byte %d" % off)
            cur.append((lid, typ, off, e + 1 - lo if e < len(buf) else e - lo)); lo = min(e + 1, len(buf)); continue
        if cur_bytes >= limit: flush()          # start a new piece before this line (the last piece is never empty)
        if lid < len(offs) and offs[lid] >= 0: die("proof: line %d has the id of a polys line" % lid)
        if is_known_derived(lid) or lid in cur_ids: die("proof: id %d used twice" % lid)
        p = m.end() - lo                         # positions below are relative to lo (lo moves when buf is refilled)
        def at(k): return lo + k
        while len(buf) - at(p) < 40 and more(): pass
        if buf[at(p):at(p) + 1] == b' ': p += 1
        while True:                             # items "id" or "id *(Q)", separated by " + ", up to ", "
            while len(buf) - at(p) < 40 and more(): pass
            t = at(p)
            while t < len(buf) and 48 <= buf[t] <= 57: t += 1
            if t == at(p): die("proof: cannot read the uses of line %d" % lid)
            r = int(buf[at(p):t])
            if r not in cur_ids: ax.add(r)
            if not (buf.startswith(b' *(', t) or buf.startswith(b' + ', t) or buf.startswith(b', ', t)): die("proof: cannot read the uses of line %d" % lid)
            while True:
                q1 = buf.find(b' + ', t)
                q2 = buf.find(b', ', t, q1 if q1 >= 0 else len(buf))
                if q2 >= 0 or q1 >= 0: break
                lo2 = max(lo, len(buf) - 2)       # keep only the last 2 bytes of this item (a separator may be cut)
                buf = buf[lo2:]; base += lo2; lo = 0; t = 0
                if not more(): die("proof: line %d has no conclusion" % lid)
            if q2 >= 0: c0 = q2 + 2 - lo; break
            p = q1 + 3 - lo
        con_off = base + lo + c0
        e = buf.find(b'\n', lo + c0)
        while e < 0:
            lo2 = max(lo + c0, len(buf) - 1); buf = buf[lo2:]; base += lo2; lo = 0; c0 = 0
            if not more(): e = len(buf); break
            e = buf.find(b'\n', lo + c0)
        end = base + e
        while len(dcon) <= lid: dcon.append(-1); dend.append(-1)
        dcon[lid] = con_off; dend[lid] = end if buf[e - 1:e] != b'\r' else end - 1
        ln = end + 1 - off if e < len(buf) else end - off
        cur.append((lid, typ, off, ln)); cur_ids.add(lid); cur_bytes += ln; lastid = lid
        lo = min(e + 1, len(buf))
    flush()
    while running: reap(True)
    if lastid < 0: die("proof: no steps")
    spec_ok(fp2, dcon[lastid], dend[lastid], "the last step's result (line %d)" % lastid)
    print("c the last step (line %d) gives exactly the spec" % lastid)
    print("c %d proof steps checked by pacheck in %d pieces (%.0f s)" % (checked, nchunk, time.time() - t0))
    print("s CERTIFICATE CHECKED")

if __name__ == '__main__':
    main()
