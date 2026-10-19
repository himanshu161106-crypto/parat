# Benchmark files

| folder | files | what | origin |
|---|---|---|---|
| `fresh_n600/` | 24 | uniform random 3-SAT, n=600, ratio 4.26 | `verify/gen_random.py 600 4.26 24 500000` (file c600_XX = seed 500000+XX) |
| `fresh_n1000/` | 24 | uniform random 3-SAT, n=1000, ratio 4.2 | `gen_random.py 1000 4.2 24 600000` |
| `hard_n1000/` | 16 | the hard ones of 60 files n=1000, ratio 4.2 (seeds 700000-700059) | picked by one separate run per solver, see `results/README.md` |
| `wall426/` | 12 | random 3-SAT at ratio 4.26, n = 300-600; w400_0, w400_2, w500_1 and w500_2 have no answer | random generator of the author's lab |
| `general_unsat/` | 67 | files with no answer: SATLIB (aim, dubois), pigeonhole (php), parity, colouring, factoring and adder circuits, cutting-plane-style random sets, two SAT-competition grid-network files | prefix = source group; SATLIB from the SATLIB library (Hoos & Stützle), the competition files from the SAT Competition archive, the rest generated in the lab |
| `multipliers/` | 8 | array / Wallace / Booth multipliers (64 and 128 bit, 128-bit gzipped) and two broken ones (`*_buggy`) | lab generator |
| `genmul64/` | 30 | the 28 unsigned GenMul designs at 64 bits, plus two broken ones (`*_buggy`) | `verify/gen_genmul.py 64 out/` (GenMul + yosys) |
| `genmul64_signed/` | 27 | the signed (two's complement) GenMul designs at 64 bits (GenMul makes no signed array + carry-skip) | `verify/gen_genmul.py 64 out/ 1` |
| `rare_bugs/` | 3 | 64-bit GenMul designs with a planted bug that changes the output only when 18-24 given input bits all match (random testing practically never sees it) | lab script: one gate input XORed with an AND of k random input literals |
| `random426_n380/` | 16 | uniform random 3-SAT, n=380, ratio 4.26 (seeds 770001-770016). No answer: v380_9 ... v380_15; the other 9 have one | lab generator (files included) |
| `big_random/` | 5 | uniform random 3-SAT with 100,000 variables: ratio 4.22 seed 1, ratio 4.25 seeds 1-4 (gzipped). The 1,000,000 and 10,000,000-variable files of the Oct 18 table are too big for git: make them with the generator | `gcc -O2 -o gen_random3 verify/gen_random3.c` then `./gen_random3 100000 4.25 1 > b100k_425_1.cnf` (also `1000000 4.22 1`, `10000000 4.22 1`); byte-identical to the files used |
| `yosys_booth/` | 9 | multipliers made by yosys with Booth encoding (`synth -booth`): `booth32/64/128_noabc` (no ABC optimisation; 128-bit gzipped) and `booth32/40/48/56/64/128_abc` (ABC on; 128-bit gzipped). Parat proves all `_noabc` ones with a checked certificate and the 32 and 48-bit `_abc` ones; 40, 56 and 64-bit `_abc` time out (open case) | `bash benchmarks/yosys_booth/make.sh 48 abc` (yowasp-yosys 0.69; byte-identical to the files here) |
| `fresh_n1000_426/` | 20 | uniform random 3-SAT, n=1000, ratio 4.26, the 20 of 40 fresh files (seeds 5550001-5550040) that some solver solved in 30 s (Parat, probSAT or YalSAT, one seed each) | lab generator (files included) |

**Do the regenerated files match?** The random sets can be regenerated with the given seeds, and the clauses come out
identical; only the file names differ.

**What `general_unsat/` is for:** these are exactly the 67 files whose DRAT proofs drat-trim verified. Check them
all with:

```bash
bash verify/verify_all_unsat.sh benchmarks/general_unsat drat-trim/drat-trim
```
