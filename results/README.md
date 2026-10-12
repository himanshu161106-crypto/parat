# Raw results

One JSON line per run. Each line gives the solver ("v"), the file, the seed, the result (SAT / TIMEOUT / WRONG), and
the time in seconds.

| file | what |
|---|---|
| fresh_n600_race.jsonl | 24 files, n=600, ratio 4.26, generator seeds 500000-500023 (`benchmarks/fresh_n600`, file c600_XX = seed 500000+XX); 3 solver seeds; 20 s limit |
| fresh_n1000_race.jsonl | 24 files, n=1000, ratio 4.2, generator seeds 600000-600023 (`benchmarks/fresh_n1000`); 3 seeds; 30 s limit |
| fresh_n1000_2hard_10seeds.jsonl | the 2 hard files of the set above, 10 seeds, 60 s limit |
| hard_n1000_selection_seed99.jsonl | 60 files, n=1000, ratio 4.2, generator seeds 700000-700059; one run per solver with seed 99, used only to pick the hard files |
| hard_n1000_10seeds.jsonl | the 16 picked files (`benchmarks/hard_n1000`), 10 new seeds (1-10), 60 s limit |
| general_258_files.jsonl | 258 general files, 20 s limit; every SAT answer checked; 0 wrong |

Regenerate any set with `verify/gen_random.py N RATIO COUNT SEED OUTDIR`. The files come out identical; only the
names differ.

Solver versions: YalSAT 1.0.1 (git a0fd39f), probSAT SC13_v2 (git d5e1d4c), Kissat 4.0.4, CaDiCaL 3.0.1, march_nh.
Each run was pinned to one core, with 2 runs at once on a 2-core Linux x86-64 machine.

## DRAT proof checks (certified "no answer")

| file | what |
|---|---|
| drat_verify_random_small.txt | 29 random files (n=150-200) + 3 (n=300, ratio 4.26), release binary `--proof-binary`, then drat-trim: every UNSAT one s VERIFIED |
| drat_verify_wall426.txt | w400_2 (text and binary, also with forced warm-up) and w500_2: s VERIFIED, with solve time, proof size and check time |
| drat_verify_general_72.txt | the 72 UNSAT files of the 258-file check: 67 s VERIFIED; the 5 multiplier miters end "unknown" in proof mode |
| drat_verify_general_67_release.txt | the final release binary on `benchmarks/general_unsat/` with `verify/verify_all_unsat.sh`: 67 VERIFIED, 0 not verified |

## Oct 12 update

| file | what |
|---|---|
| genmul64_pac_oct12.txt | the 28 unsigned GenMul designs at 64 bits: proof time (clean machine) and certificate status; 27 proved, 27 certificates CHECKED by pacheck2 |
| genmul64_signed_race.txt | the 27 signed GenMul designs at 64 bits: Parat vs AMulet2 -signed, both with certificates; Parat 26 / 26 CHECKED, AMulet2 11 / 11 CHECKED |
| rare_bugs_oct12.txt | planted bugs that fire on about 1 input in 2^18 ... 2^32: counterexamples found on 6 of 8 (+1 extra file) |
| random426_unsat_vs_march_oct12.txt | ratio 4.26, n=380, 7 files without an answer: Parat old / new vs march_nh (131.8 / 106.4 / 112.9 s in total) |
| random1000_426_race_oct12.jsonl | ratio 4.26, n=1000, the 20 files of `benchmarks/fresh_n1000_426`, 3 seeds, 60 s: Parat 60/60 mean 2.73 s, probSAT 60/60 2.84 s, YalSAT 59/60 3.66 s |
| random_big_424_426_race_oct12.jsonl | ratio 4.24 (n=10k, 20k) and 4.26 (n=5k, 10k), 2 files each, 3 seeds, 100 s: Parat 12, probSAT 12, YalSAT 7 runs solved |
| scorecard_oct12.txt, scorecard_oct12_parat.jsonl | Parat re-run on scorecard categories C-F |
| drat_verify_general_67_oct12.txt | the Oct 12 release binary on `benchmarks/general_unsat/`: DRAT proofs checked by drat-trim |
