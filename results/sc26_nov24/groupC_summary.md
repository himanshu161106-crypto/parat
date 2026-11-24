# Group C (general / industrial) - Parat v1.5 vs Kissat 4.0

61 of the 69 Group C files that at least one competition solver solved within 300 s (the 8 largest left out),
120 s per file, one core each, same Linux machine. Per-file table: `groupC_61files_120s.csv`.

| solver | solved | PAR-2 |
|---|---:|---:|
| Kissat 4.0 | 37 | 7085 |
| Parat before BVA (Nov 24 morning) | 23 | 9525 |
| Parat v1.5 (BVA when it removes >= 25% of rules, shrinking on) | 25 | 9285 |

No wrong answer in any run (SAT models checked; UNSAT agrees with the known answers). This is where Parat is
weakest: general CDCL. Kissat is clearly ahead here.
