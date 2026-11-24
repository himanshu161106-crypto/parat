# SAT Competition 2026 (main track) - families Parat v1.5 solves with new engines

Times: Windows laptop (16 GB) for datapath / multiplier equivalence (`test_nov23.bat`, `test_nov23b.bat`, Nov 24);
Linux container for noisy parity. "Others <= 300 s": how many competition solvers solved the file within 300 s
(SAT Competition 2026 results), "best": the fastest competition time.

| file | family | answer | Parat v1.5 | others <= 300 s | best in competition |
|---|---|---|---:|---:|---:|
| 1eea3d91 | minimal-disagreement-parity | SAT | 0.1 s | 0 | 730 s |
| 61fee64c | minimal-disagreement-parity | SAT | 0.06 s | 0 | 946 s |
| 16ca57f2 | minimum-disagreement-parity | UNSAT | 1.9-3.9 s | 0 | not solved |
| 23daec2c | minimum-disagreement-parity | UNSAT | 1.1-1.9 s | 0 | not solved |
| 425c81fc | minimum-disagreement-parity | UNSAT | 2.0-2.6 s | 0 | not solved |
| db15a856 | minimum-disagreement-parity | SAT | 0.04 s | 2 | 0 s |
| 27495ba0 | datapath-equivalence-checking | UNSAT | 0.8 s | 0 | 1902 s |
| 2a38c5d4 | datapath-equivalence-checking | UNSAT | 92.6 s | 0 | 1620 s |
| 5ab5ac8d | datapath-equivalence-checking | UNSAT | 88.1 s | 0 | 1772 s |
| e685a5d9 | datapath-equivalence-checking | UNSAT | 89.5 s | 0 | 1690 s |
| de8c42d5 | multiplier-equivalence-checking | UNSAT | 81.9 s | 0 | 675 s |
| fac2035b | multiplier-equivalence-checking | UNSAT | 88.9 s | 3 | 284 s |

Checks: every SAT model is checked rule by rule. Noisy parity: 18 shuffled and sign-flipped copies of the six files
give the same answers; the UNSAT argument (counter bound by clause learning + exact enumeration of every secret with
few mismatches + each such secret refuted) was cross-checked with an independent Python enumeration and Kissat.
Datapath / multiplier: removing the miter's output unit makes the files SAT, and Parat then returns a checked model.
These UNSAT answers come from normal mode (no DRAT proof for these two engines yet).
