#!/bin/bash
# Rebuilds booth<W>_nofraig.aag: yosys 0.69 (native build, git 9f75ca1f9; yowasp-yosys 0.69 gives the same gates),
# Booth mapping + yosys's default ABC script WITHOUT the "&fraig -x" step (that one step needs about 24 hours at
# 256 bits; without it 256 bits takes about 2 minutes). Everything else is the default flow.
#   bash make_nofraig.sh WIDTH        -> booth<WIDTH>_nofraig.aag
set -e; W=$1; Y=${YOSYS:-yosys}
echo "module mb(input [$((W-1)):0] a, input [$((W-1)):0] b, output [$((2*W-1)):0] p); assign p = a * b; endmodule" > mb$W.v
$Y -q -p "read_verilog mb$W.v; hierarchy -top mb; synth -flatten -top mb -booth -noabc; abc -script +strash;&get,-n;&put;scorr;dc2;dretime;strash;&get,-n;&dch,-f;&nf;&put; opt -fast; aigmap; opt_clean; write_aiger -ascii -symbols booth${W}_nofraig.aag"
rm -f mb$W.v; echo "wrote booth${W}_nofraig.aag"
