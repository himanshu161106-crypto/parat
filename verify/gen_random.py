#!/usr/bin/env python3
"""Make uniform random 3-SAT files, so anyone can test on files nobody has seen before.

usage:  python3 gen_random.py N_VARS RATIO COUNT SEED OUTDIR
example python3 gen_random.py 1000 4.2 24 600000 fresh/

Each clause: 3 different variables, each negated with chance 1/2. Same seed gives the same files (the benchmark
sets in this repo were made this way; seeds are listed in results/README.md).
"""
import os, random, sys


def gen(fn, n, seed, ratio):
    r = random.Random(seed); m = round(n * ratio)
    with open(fn, "w") as f:
        f.write(f"p cnf {n} {m}\n")
        for _ in range(m):
            vs = r.sample(range(1, n + 1), 3)
            f.write(" ".join(str(v if r.random() < .5 else -v) for v in vs) + " 0\n")


if __name__ == "__main__":
    n, ratio, count, seed, out = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    os.makedirs(out, exist_ok=True)
    for i in range(count):
        gen(os.path.join(out, f"r{n}_{seed + i}.cnf"), n, seed + i, ratio)
    print(f"{count} files in {out}")
