#!/bin/bash
# Verify every 'no answer' in a folder with DRAT proofs:
#   bash verify/verify_all_unsat.sh benchmarks/general_unsat drat-trim/drat-trim [time_limit_s]
# For each .cnf file: Parat runs with --proof (binary DRAT), drat-trim checks it. One line per file, then a summary.
DIR="$1"; DT="${2:-drat-trim/drat-trim}"; LIM="${3:-300}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"; PARAT="$HERE/bin/parat-linux-x86_64"
[ -d "$DIR" ] && [ -x "$DT" ] || { echo "usage: $0 folder path/to/drat-trim [time_limit_s]"; exit 2; }
ok=0; bad=0; other=0; P=$(mktemp /tmp/parat_proof.XXXXXX)
for f in "$DIR"/*.cnf; do
  R=$("$PARAT" "$f" 1 "$LIM" --proof "$P" --proof-binary 2>/dev/null | grep '^s ' || true)
  if [ "$R" = "s UNSATISFIABLE" ]; then
    V=$("$DT" "$f" "$P" -t 50000 | tr '\r' '\n' | grep -aE "^s " | head -1)
    echo "$(basename "$f"): $R, proof $(du -h "$P" | cut -f1) -> $V"
    if [ "$V" = "s VERIFIED" ]; then ok=$((ok+1)); else bad=$((bad+1)); fi
  else echo "$(basename "$f"): ${R:-no result} (no proof to check)"; other=$((other+1)); fi
done
rm -f "$P"
echo "== $ok VERIFIED, $bad NOT verified, $other without an UNSAT result"
