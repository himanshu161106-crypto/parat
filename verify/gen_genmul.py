#!/usr/bin/env python3
"""Make the AMulet-style benchmark family with GenMul (JKU/Bremen generator, the one behind the sp-ar-rc ... names) and
yosys: Verilog -> AIGER. usage: GENMUL_BIN_DIR=.../genmul/build/bin gen_genmul.py width out_dir [signed 0/1]   (needs: pip install yowasp-yosys)"""
import subprocess, sys, os, itertools
GM = os.environ.get("GENMUL_BIN_DIR", "genmul/build/bin")   # where GenMul (github amahzoon/genmul) was built
PPA = {1: "ar", 2: "wt", 3: "dt", 4: "ct"}; FSA = {1: "rc", 2: "cl", 3: "lf", 4: "ks", 5: "bk", 6: "cs", 7: "sp"}
w, out = int(sys.argv[1]), os.path.abspath(sys.argv[2]); sg = int(sys.argv[3]) if len(sys.argv) > 3 else 0
os.makedirs(out, exist_ok=True)
for a, f in itertools.product(PPA, FSA):
    name = f"{'s' if sg else 'u'}-sp-{PPA[a]}-{FSA[f]}-{w}"; dst = os.path.join(out, name + ".aag")
    if os.path.exists(dst): continue
    r = subprocess.run(["./genmul"], input=f"{2 if sg else 1}\n{a}\n{f}\n{w}\n{w}\n", cwd=GM, capture_output=True, text=True)
    vl = [l for l in r.stdout.splitlines() if l.startswith("Output file:")]
    if not vl: print(name, "GENMUL FAILED", flush=True); continue
    v = vl[0].split(":", 1)[1].strip()
    vp = os.path.join(GM, v)
    r = subprocess.run(["yowasp-yosys", "-q", "-p", f"read_verilog {v}; hierarchy -top Mult_{w}_{w}; flatten; proc; opt_clean; techmap; aigmap; opt_clean; write_aiger -ascii -symbols out.aag"], cwd=GM, capture_output=True, text=True)   # wasm yosys: relative paths only
    if os.path.exists(os.path.join(GM, "out.aag")): os.replace(os.path.join(GM, "out.aag"), dst)
    else: print(r.stderr[-500:])
    if os.path.exists(vp): os.remove(vp)
    print(name, os.path.getsize(dst) if os.path.exists(dst) else "FAILED", flush=True)
