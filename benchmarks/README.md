# Benchmark files

| folder | files | what | origin |
|---|---|---|---|
| `fresh_n600/` | 24 | uniform random 3-SAT, n=600, ratio 4.26 | `verify/gen_random.py 600 4.26 24 500000` (file c600_XX = seed 500000+XX) |
| `fresh_n1000/` | 24 | uniform random 3-SAT, n=1000, ratio 4.2 | `gen_random.py 1000 4.2 24 600000` |
| `hard_n1000/` | 16 | the hard ones of 60 files n=1000, ratio 4.2 (seeds 700000-700059) | picked by one separate run per solver, see `results/README.md` |
| `wall426/` | 12 | random 3-SAT at ratio 4.26, n = 300-600; w400_0, w400_2, w500_1 and w500_2 have no answer | random generator of the author's lab |
| `general_unsat/` | 67 | files with no answer: SATLIB (aim, dubois), pigeonhole (php), parity, colouring, factoring and adder circuits, cutting-plane-style random sets, two SAT-competition grid-network files | prefix = source group; SATLIB from the SATLIB library (Hoos & Stützle), the competition files from the SAT Competition archive, the rest generated in the lab |

**Do the regenerated files match?** The random sets can be regenerated with the given seeds, and the clauses come out
identical; only the file names differ.

**What `general_unsat/` is for:** these are exactly the 67 files whose DRAT proofs drat-trim verified. Check them
all with:

```bash
bash verify/verify_all_unsat.sh benchmarks/general_unsat drat-trim/drat-trim
```
