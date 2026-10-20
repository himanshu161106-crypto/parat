#!/bin/bash
# Oct 20: same flow as make.sh WIDTH abc (synth -booth with ABC), but the ABC step runs in native yosys (apt yosys 0.33,
# its yosys-abc) because WASM ABC was too slow for 256-bit (> 2 h). Step 1 (yowasp-yosys 0.69): synth -booth -noabc
# (everything except abc). Step 2 (native): abc -fast; opt -fast (what synth runs in place of -noabc), then aigmap.
set -e; W=$1
echo "module mb(input [$((W-1)):0] a, input [$((W-1)):0] b, output [$((2*W-1)):0] p); assign p = a * b; endmodule" > mb$W.v
yowasp-yosys -q -p "read_verilog mb$W.v; hierarchy -top mb; synth -flatten -top mb -booth -noabc; write_rtlil step1_$W.il"
yosys -q -p "read_rtlil step1_$W.il; abc -fast; opt -fast; aigmap; opt_clean; write_aiger -ascii -symbols booth${W}_abcsplit.aag"
rm -f mb$W.v; echo "wrote booth${W}_abcsplit.aag"
