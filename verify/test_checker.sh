#!/bin/bash
# Negative tests for the checker pipeline (not for the solver): good certificates must pass, and every swapped,
# corrupted, missing or changed piece must make verify_multiplier.sh exit nonzero.
#   test_checker.sh path/to/pacheck path/to/drat-trim
# Uses benchmarks/multipliers/booth16.aag (one-part certificate) and benchmarks/yosys_booth/booth40_abc.aag
# (two-part certificate). Takes about a minute. Exit 0 only if every case behaves as expected.
set -u
PK="$1"; DT="$2"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; V="$HERE/verify/verify_multiplier.sh"
B="$HERE/bin/parat-linux-x86_64"; W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
C16="$HERE/benchmarks/multipliers/booth16.aag"; C40="$HERE/benchmarks/yosys_booth/booth40_abc.aag"
echo "making two certificates ..."
"$B" "$C16" 1 300 --pac "$W/d16" | grep -q "^s CORRECT" || { echo "setup failed (booth16)"; exit 1; }
"$B" "$C40" 1 600 --pac "$W/p40" | grep -q "^s CORRECT" || { echo "setup failed (booth40_abc)"; exit 1; }
[ -f "$W/p40.new.aag" ] && [ -f "$W/p40.eq1.drat" ] || { echo "setup: booth40_abc did not give a two-part certificate"; exit 1; }
pass=0; bad=0
copy() { rm -f "$W/$2".*; for f in "$W/$1".*; do cp "$f" "$W/$2${f#$W/$1}"; done; }   # copy certificate $1 to name $2
expect() {   # expect <0|1> <description> <circuit> <cert prefix>
  "$V" "$3" "$PK" "$DT" --cert "$W/$4" > "$W/out.txt" 2>&1; rc=$?
  if { [ "$1" = 0 ] && [ $rc = 0 ]; } || { [ "$1" = 1 ] && [ $rc != 0 ]; }; then pass=$((pass + 1)); echo "ok    $2  ($(tail -1 "$W/out.txt"))"
  else bad=$((bad + 1)); echo "WRONG $2: exit $rc"; tail -3 "$W/out.txt"; fi; }
expect 0 "booth16, its own certificate" "$C16" d16
expect 0 "booth40_abc, its own two-part certificate" "$C40" p40
expect 1 "booth16 checked with booth40_abc's certificate (swap)" "$C16" p40
copy p40 x; rm -f "$W"/x.new.aag "$W"/x.eq*
expect 1 "booth40_abc with only the PAC part of its certificate (two-part removed)" "$C40" x
expect 1 "booth40_abc checked with booth16's certificate (swap)" "$C40" d16
copy p40 x; python3 -c "import sys; p=sys.argv[1]; b=bytearray(open(p,'rb').read()); n=len(b)//2; b[n:n+64]=bytes(64); open(p,'wb').write(b)" "$W/x.eq1.drat"
expect 1 "one DRAT proof corrupted (64 bytes zeroed)" "$C40" x
copy p40 x; head -c 200 "$W/p40.eq2.drat" > "$W/x.eq2.drat"
expect 1 "one DRAT proof truncated" "$C40" x
copy p40 x; rm -f "$W/x.eq2.drat"
expect 1 "one DRAT proof missing" "$C40" x
copy p40 x; rm -f "$W/x.eq0.cnf"
expect 1 "one equivalence CNF missing" "$C40" x
copy p40 x; echo "1 2 0" >> "$W/x.eq1.cnf"
expect 1 "Parat's equivalence CNF changed (one clause added)" "$C40" x
copy p40 x; python3 - "$W/x.new.aag" << 'EOF'
import sys; p = sys.argv[1]; L = open(p).read().split("\n"); M, I, Lt, O, A = map(int, L[0].split()[1:6])
k = 1 + I + O + A // 2; y, a, b = map(int, L[k].split()); L[k] = "%d %d %d" % (y, a ^ 1, b); open(p, "w").write("\n".join(L))
EOF
expect 1 "one gate of the second circuit changed" "$C40" x
copy d16 x; n=$(wc -l < "$W/x.polys"); echo "$((n + 1)) -s0;" >> "$W/x.polys"
expect 1 "a fake fact added to the PAC polynomials" "$C16" x
copy d16 x; sed -i '0,/^\([0-9]*\) -g\([0-9]*\)+g/s//\1 -g\2-g/' "$W/x.polys"
expect 1 "one gate polynomial changed (sign flipped)" "$C16" x
copy d16 x; sed -i '1s/^1 .*/1 2;/' "$W/x.polys"
expect 1 "modulus changed to 2" "$C16" x
copy d16 x; sed -i 's/+2\*s1+/+2*s2+/' "$W/x.spec"
expect 1 "specification changed" "$C16" x
copy d16 x; head -c 2000 "$W/d16.proof" > "$W/x.proof"
expect 1 "PAC proof truncated" "$C16" x
"$V" "$HERE/benchmarks/multipliers/booth16_buggy.aag" "$PK" "$DT" > "$W/out.txt" 2>&1; rc=$?
if [ $rc != 0 ]; then pass=$((pass + 1)); echo "ok    broken multiplier (booth16_buggy), full run  ($(tail -1 "$W/out.txt"))"
else bad=$((bad + 1)); echo "WRONG broken multiplier certified"; fi
echo "checker tests: $pass as expected, $bad wrong"
[ $bad = 0 ]
