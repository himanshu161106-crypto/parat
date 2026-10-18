#!/bin/bash
# Rebuilds the files in this folder with yosys (tested: yowasp-yosys 0.69, `pip install yowasp-yosys`).
#   bash make.sh WIDTH noabc   -> boothWIDTH_noabc.aag   (synth -booth -noabc)
#   bash make.sh WIDTH abc     -> boothWIDTH_abc.aag     (synth -booth, ABC optimisation on)
# Another yosys version can give a different (but equivalent) netlist.
set -e; W=$1; MODE=$2; Y=${YOSYS:-yowasp-yosys}
echo "module mb(input [$((W-1)):0] a, input [$((W-1)):0] b, output [$((2*W-1)):0] p); assign p = a * b; endmodule" > mb$W.v
OPT="-booth"; [ "$MODE" = noabc ] && OPT="-booth -noabc"
$Y -q -p "read_verilog mb$W.v; hierarchy -top mb; synth -flatten -top mb $OPT; aigmap; opt_clean; write_aiger -ascii -symbols booth${W}_$MODE.aag"
rm -f mb$W.v; echo "wrote booth${W}_$MODE.aag"
