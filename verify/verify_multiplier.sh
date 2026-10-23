#!/bin/bash
# Check a multiplier proof yourself.
#   verify_multiplier.sh circuit.aag[.gz] path/to/pacheck path/to/drat-trim            (runs Parat, then checks)
#   verify_multiplier.sh circuit.aag[.gz] path/to/pacheck path/to/drat-trim --cert P   (checks existing files P.*)
# Exit status: 0 = CERTIFIED (every check below passed), 1 = NOT CERTIFIED (the reason is printed).
# Checks (all must pass; tools not written by us: pacheck2 from JKU, drat-trim from UT Austin):
#  1. Parat answered CORRECT (first form only).
#  2. verify/pac_circuit.py: every polynomial in P.polys is a gate or output definition of the circuit the certificate
#     is about (your circuit, or for ABC-optimised designs P.new.aag) or the modulus 2^O, and P.spec is
#     "outputs = a*b mod 2^O". A certificate made for another circuit, or with an added/changed line, fails here.
#  3. pacheck2: P.proof derives P.spec from P.polys -> "TARGET CHECKED".
#  4. Only when P.new.aag is present (ABC-optimised designs): for every range of 32 outputs k = 0 .. ceil(O/32)-1,
#     verify/eq_cnf.py rebuilds the CNF "your circuit and P.new.aag differ on these outputs" from YOUR file, it must be
#     byte-identical to Parat's P.eq<k>.cnf, and drat-trim must VERIFY Parat's proof P.eq<k>.drat on the rebuilt CNF.
#     Every range must be present; a missing, changed or unverified one fails.
# Get the checkers once:
#   git clone https://github.com/d-kfmnn/pacheck2 && (cd pacheck2 && ./configure.sh && make)
#   git clone https://github.com/marijnheule/drat-trim && (cd drat-trim && make)
set -u
if [ $# -lt 3 ]; then sed -n '2,4p' "$0"; exit 1; fi
F="$1"; PK="$2"; DT="$3"; CERT=""
if [ $# -ge 5 ] && [ "$4" = "--cert" ]; then CERT="$5"; fi
HERE="$(cd "$(dirname "$0")/.." && pwd)"; D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
fail() { echo "NOT CERTIFIED: $*"; exit 1; }
[ -f "$F" ] || fail "circuit file $F not found"
command -v "$PK" > /dev/null 2>&1 || [ -x "$PK" ] || fail "pacheck2 not found: $PK"
command -v "$DT" > /dev/null 2>&1 || [ -x "$DT" ] || fail "drat-trim not found: $DT"
if [[ "$F" == *.gz ]]; then gunzip -c "$F" > "$D/c.aag" || fail "cannot unpack $F"; F="$D/c.aag"; fi

# 1. Parat (unless an existing certificate is given)
if [ -z "$CERT" ]; then
  CERT="$D/cert"
  "$HERE/bin/parat-linux-x86_64" "$F" 1 1500 --pac "$CERT" > "$D/parat.txt" 2>&1
  grep -E "^s |^c (a|b|circuit|a\*b)" "$D/parat.txt"
  grep -q "^s CORRECT MULTIPLIER" "$D/parat.txt" || fail "Parat did not prove the circuit correct"
fi
for x in polys proof spec; do [ -f "$CERT.$x" ] || fail "missing certificate file $CERT.$x"; done

# which circuit the PAC part is about
if [ -f "$CERT.new.aag" ]; then PACC="$CERT.new.aag"; MODE="two-part (ABC-optimised design)"
else PACC="$F"; MODE="one-part"; fi
echo "certificate: $MODE, $(du -ch "$CERT".polys "$CERT".proof "$CERT".spec | tail -1 | cut -f1)"

# 2. the certificate is about this circuit and states a*b
python3 "$HERE/verify/pac_circuit.py" "$PACC" "$CERT.polys" "$CERT.spec" || fail "the PAC files do not belong to this circuit / this specification"

# 3. pacheck2
"$PK" "$CERT.polys" "$CERT.proof" "$CERT.spec" > "$D/pck.txt" 2>&1
grep -aq "TARGET CHECKED" "$D/pck.txt" || { grep -aE "error|NOT" "$D/pck.txt" | head -3; fail "pacheck2 did not report TARGET CHECKED"; }
echo "pacheck2: TARGET CHECKED"

# 4. your circuit == P.new.aag, every output range
if [ "$MODE" != "one-part" ]; then
  O=$(head -1 "$F" | awk '{print $5}'); NP=$(( (O + 31) / 32 ))
  for ((k = 0; k < NP; k++)); do
    [ -f "$CERT.eq$k.cnf" ] || fail "missing $CERT.eq$k.cnf (outputs $((32 * k))..)"
    [ -f "$CERT.eq$k.drat" ] || fail "missing $CERT.eq$k.drat (outputs $((32 * k))..)"
    python3 "$HERE/verify/eq_cnf.py" "$F" "$CERT.new.aag" $k "$D/mine$k.cnf" || fail "cannot rebuild the SAT file for range $k"
    cmp -s "$D/mine$k.cnf" "$CERT.eq$k.cnf" || fail "range $k: Parat's CNF differs from the one rebuilt from your file"
    r=$("$DT" "$D/mine$k.cnf" "$CERT.eq$k.drat" -t 20000 2>&1 | tr -d '\r' | grep -E "^s " | head -1)
    [ "$r" = "s VERIFIED" ] || fail "range $k: drat-trim: ${r:-no answer}"
  done
  echo "drat-trim: $NP of $NP output ranges VERIFIED (each CNF rebuilt from your file)"
fi
echo "CERTIFIED: the circuit computes a*b (every check passed)"
exit 0
