#!/usr/bin/env python3
"""Independent answer checker (does not use Parat in any way).

usage:  python3 check_model.py formula.cnf solver_output.txt

Reads the DIMACS formula and the solver output ('s SATISFIABLE' + 'v ...' lines). Prints OK only if every clause of
the formula has at least one true literal under the printed assignment. Exit code 0 = OK, 1 = wrong, 2 = no answer.
"""
import sys


def clauses(fn):
    cur = []
    with open(fn) as f:
        for line in f:
            if not line.strip() or line[0] in "cp%":
                continue
            for t in line.split():
                x = int(t)
                if x == 0:
                    if cur: yield cur
                    cur = []
                else:
                    cur.append(x)
    if cur: yield cur


def main():
    formula, out = sys.argv[1], sys.argv[2]
    status, val = None, {}
    for line in open(out):
        if line.startswith("s "): status = line[2:].strip()
        elif line.startswith("v "):
            for t in line.split()[1:]:
                x = int(t)
                if x: val[abs(x)] = x > 0
    if status != "SATISFIABLE":
        print("no SAT answer to check (status: %s)" % status); sys.exit(2)
    n = 0
    for c in clauses(formula):
        n += 1
        if not any(val.get(abs(l)) == (l > 0) for l in c):
            print("WRONG: clause %d not satisfied: %s" % (n, c)); sys.exit(1)
    print("OK: all %d clauses satisfied" % n)


if __name__ == "__main__":
    main()
