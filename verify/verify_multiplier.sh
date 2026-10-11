#!/bin/bash
# Check a multiplier proof yourself. usage: verify_multiplier.sh circuit.aag[.gz] path/to/pacheck
# Parat proves circuit(a, b) = a*b and writes a PAC certificate; pacheck2 (JKU, not written by us) checks it against the
# circuit file itself. Get pacheck2 once:  git clone https://github.com/d-kfmnn/pacheck2 && (cd pacheck2 && ./configure.sh && make)
set -eu
F="$1"; P="$2"; D=$(mktemp -d); HERE="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$F" == *.gz ]]; then gunzip -c "$F" > "$D/c.aag"; F="$D/c.aag"; fi
"$HERE/bin/parat-linux-x86_64" "$F" 1 600 --pac "$D/cert" | grep -E "^s |^c (a|b|circuit|a\*b)"
if [ -f "$D/cert.proof" ]; then
  echo "certificate: $(du -ch "$D"/cert.polys "$D"/cert.proof | tail -1 | cut -f1)"
  "$P" "$D/cert.polys" "$D/cert.proof" "$D/cert.spec" 2>&1 | grep -aE "TARGET CHECKED|error|NOT INFERRED" | sed 's/^\[pck2\] c /pacheck2: /'
fi
rm -rf "$D"
