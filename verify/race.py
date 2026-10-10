#!/usr/bin/env python3
"""Race Parat against any other SAT solvers on your own machine.

usage:
  python3 race.py --limit 30 --seeds 3 \
      --solver "parat=../bin/parat-linux-x86_64 {file}"  (Parat reads the seed from PARAT_SEED, set automatically) \
      --solver "yalsat=/path/to/yalsat {file} {seed}" \
      --solver "probsat=/path/to/probSAT -a {file} {seed}" \
      files/*.cnf

* every run is pinned to one core (taskset), as many runs at once as --jobs (default: 1 per core, at most 2)
* every SAT answer is checked against every clause (check_model.py logic); a wrong answer is reported loudly
* output: one JSON line per run (also written to --log), then a table over the files that at least one run solved
  (files no run solved most likely have no answer), with mean, median, PAR2 and a sign test per file.
"""
import argparse, json, math, os, queue, shlex, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_model import clauses


def check(fn, out):
    val = {}
    for line in out.splitlines():
        if line.startswith("v "):
            for t in line.split()[1:]:
                x = int(t)
                if x: val[abs(x)] = x > 0
    return all(any(val.get(abs(l)) == (l > 0) for l in c) for c in clauses(fn))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=30); ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=1); ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--solver", action="append", required=True); ap.add_argument("--log", default="race_log.jsonl")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    solvers = dict(s.split("=", 1) for s in a.solver)
    ncpu = len(os.sched_getaffinity(0)); jobs = a.jobs or min(2, ncpu)
    cores = queue.Queue()
    for c in sorted(os.sched_getaffinity(0))[:jobs]: cores.put(c)
    log = open(a.log, "a"); res = {}

    def run(task):
        name, fn, seed = task
        cmd = shlex.split(solvers[name].format(file=fn, seed=seed))
        env = dict(os.environ, PARAT_SEED=str(seed))
        core = cores.get(); t0 = time.time()
        try:
            out = subprocess.run(["taskset", "-c", str(core)] + cmd, capture_output=True, text=True, timeout=a.limit, env=env).stdout
            t = time.time() - t0
            st = next((l[2:].strip() for l in out.splitlines() if l.startswith("s ")), "UNKNOWN")
            r = "SAT" if st == "SATISFIABLE" else "UNSAT" if st == "UNSATISFIABLE" else "UNKNOWN"
            if r == "SAT" and not check(fn, out): r = "WRONG"
        except subprocess.TimeoutExpired:
            r, t = "TIMEOUT", a.limit
        cores.put(core)
        rec = {"solver": name, "file": os.path.basename(fn), "seed": seed, "result": r, "time": round(t, 3)}
        res[task] = rec; log.write(json.dumps(rec) + "\n"); log.flush(); print(json.dumps(rec), flush=True)
        if r == "WRONG": print("!!! WRONG ANSWER", rec, flush=True)

    tasks = [(n, f, s) for f in a.files for s in range(a.seed0, a.seed0 + a.seeds) for n in solvers]
    with ThreadPoolExecutor(jobs) as ex: list(ex.map(run, tasks))

    seeds = range(a.seed0, a.seed0 + a.seeds)
    T = lambda n, f, s: res[(n, f, s)]["time"] if res[(n, f, s)]["result"] in ("SAT", "UNSAT") else a.limit
    solved = [f for f in a.files if any(res[(n, f, s)]["result"] in ("SAT", "UNSAT") for n in solvers for s in seeds)]
    print(f"\n{len(solved)} of {len(a.files)} files solved by at least one run; table over those files")
    print(f"{'solver':12s} {'solved':>9s} {'mean s':>8s} {'median s':>9s} {'PAR2 s':>8s}")
    for n in solvers:
        ts = [T(n, f, s) for f in solved for s in seeds]
        ok = sum(res[(n, f, s)]["result"] in ("SAT", "UNSAT") for f in solved for s in seeds)
        par2 = [t if t < a.limit else 2 * a.limit for t in ts]
        if ts: print(f"{n:12s} {ok:4d}/{len(ts):<4d} {statistics.mean(ts):8.3f} {statistics.median(ts):9.3f} {statistics.mean(par2):8.3f}")
    names = list(solvers)
    for i, p in enumerate(names):
        for o in names[i + 1:]:
            pm = {f: statistics.mean(T(p, f, s) for s in seeds) for f in solved}
            om = {f: statistics.mean(T(o, f, s) for s in seeds) for f in solved}
            w = sum(pm[f] < om[f] for f in solved); l = sum(pm[f] > om[f] for f in solved); n = w + l
            pv = sum(math.comb(n, k) for k in range(max(w, l), n + 1)) / 2 ** n * 2 if n else 1
            print(f"{p} faster than {o} on {w} files, slower on {l} (two-sided sign test p = {min(pv, 1):.4f})")


if __name__ == "__main__":
    main()
