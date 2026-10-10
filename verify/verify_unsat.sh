#!/bin/bash
# Check a 'no answer' (UNSATISFIABLE) result of Parat yourself, without trusting Parat.
#
#   bash verify/verify_unsat.sh formula.cnf [path/to/drat-trim]
#
# 1. Parat solves the formula and writes a DRAT proof: a list of clauses, each of which follows from the formula and
#    the clauses before it by unit propagation, ending with the empty clause.
# 2. drat-trim (an independent checker by Marijn Heule, used by the SAT Competition) reads the ORIGINAL formula and the
#    proof and checks every step. "s VERIFIED" means the formula really has no solution.
#
# Get drat-trim once:  git clone https://github.com/marijnheule/drat-trim && make -C drat-trim
set -e
F="$1"; DT="${2:-drat-trim/drat-trim}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"; PARAT="$HERE/bin/parat-linux-x86_64"
[ -f "$F" ] || { echo "usage: $0 formula.cnf [drat-trim]"; exit 2; }
[ -x "$DT" ] || { echo "drat-trim not found at $DT (see the comment at the top of this script)"; exit 2; }
P=$(mktemp /tmp/parat_proof.XXXXXX)
t0=$(date +%s.%N)
R=$("$PARAT" "$F" --proof "$P" --proof-binary 2>/dev/null | grep '^s ' || true)
t1=$(date +%s.%N)
echo "Parat: $R ($(echo "$t1 - $t0" | bc) s), proof $(du -h "$P" | cut -f1)"
if [ "$R" != "s UNSATISFIABLE" ]; then echo "not an UNSAT result: nothing to verify (a SAT answer is checked with verify/check_model.py)"; rm -f "$P"; exit 1; fi
"$DT" "$F" "$P" -t 50000 | tr '\r' '\n' | grep -aE "^s |verification time|lemmas in core"
t2=$(date +%s.%N); echo "check time $(echo "$t2 - $t1" | bc) s"
rm -f "$P"
