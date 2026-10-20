#!/bin/bash
# Check a multiplier proof yourself. usage: verify_multiplier.sh circuit.aag[.gz] path/to/pacheck [path/to/drat-trim]
# Parat proves circuit(a, b) = a*b and writes a PAC certificate; pacheck2 (JKU, not written by us) checks it.
# Get pacheck2 once:  git clone https://github.com/d-kfmnn/pacheck2 && (cd pacheck2 && ./configure.sh && make)
# Update 7: for a multiplier whose final adder was optimised by ABC, Parat proves a second circuit (cert.new.aag) and
# shows with SAT that it gives the same outputs as yours (cert.eq<k>.cnf, one file per 32 outputs). This script then
# (1) checks the PAC certificate of cert.new.aag with pacheck2, (2) rebuilds every cert.eq<k>.cnf itself from YOUR file
# and cert.new.aag (verify/eq_cnf.py) and compares byte for byte, (3) checks every proof cert.eq<k>.drat with drat-trim
# (Univ. of Texas, not written by us): git clone https://github.com/marijnheule/drat-trim && (cd drat-trim && make)
set -eu
F="$1"; P="$2"; DT="${3:-drat-trim}"; D=$(mktemp -d); HERE="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$F" == *.gz ]]; then gunzip -c "$F" > "$D/c.aag"; F="$D/c.aag"; fi
"$HERE/bin/parat-linux-x86_64" "$F" 1 1500 --pac "$D/cert" | grep -E "^s |^c (a|b|circuit|a\*b)"
if [ -f "$D/cert.proof" ]; then
  echo "certificate: $(du -ch "$D"/cert.polys "$D"/cert.proof | tail -1 | cut -f1)"
  "$P" "$D/cert.polys" "$D/cert.proof" "$D/cert.spec" 2>&1 | grep -aE "TARGET CHECKED|error|NOT INFERRED" | sed 's/^\[pck2\] c /pacheck2: /'
fi
if [ -f "$D/cert.eq0.cnf" ]; then
  n=$(ls "$D"/cert.eq*.cnf | wc -l); ok=0
  for ((k = 0; k < n; k++)); do
    python3 "$HERE/verify/eq_cnf.py" "$F" "$D/cert.new.aag" $k "$D/mine$k.cnf"
    if ! cmp -s "$D/mine$k.cnf" "$D/cert.eq$k.cnf"; then echo "eq$k: Parat's CNF differs from the rebuilt one"; continue; fi
    r=$("$DT" "$D/mine$k.cnf" "$D/cert.eq$k.drat" -t 20000 2>&1 | tr -d '\r' | grep -E "^s " | head -1)
    [ "$r" = "s VERIFIED" ] && ok=$((ok + 1)) || echo "eq$k: drat-trim: ${r:-no answer}"
  done
  echo "same outputs as cert.new.aag: $ok of $n SAT files rebuilt by this script and their proofs VERIFIED by drat-trim"
fi
rm -rf "$D"
