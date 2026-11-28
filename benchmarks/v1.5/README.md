# v1.5 benchmark files

| file | what | Parat v1.5 |
|---|---|---|
| `multipliers/wallace64.aag`, `booth64.aag`, `array64.aag` | 64 × 64-bit Wallace, Booth and array multipliers | CORRECT, PAC certificate checked |
| `multipliers/wallace256.aig.gz` | 256 × 256-bit Wallace multiplier (0.66 M AND gates) | CORRECT, 3.4 s |
| `multipliers/wallace256_buggy.aig.gz` | the same with one gate changed | INCORRECT + counterexample |
| `multipliers/wallace512.aig.gz` | 512 × 512-bit Wallace multiplier (2.6 M AND gates) | CORRECT, 8.9 s; certificate checked in 97 s |
| `certificate_example/booth64.*.xz` | the PAC certificate Parat wrote for `booth64.aag` | `pac_verify.py`: CERTIFICATE CHECKED |
| `sc2026_files.txt` | the 10 SAT Competition 2026 files no competition solver solved within 300 s | all solved, see `results/` |

Unpack first (`gunzip *.gz`, `unxz *.xz`). The 1024- and 2048-bit multipliers are too big for git (45 MB and
178 MB); make them with `gen_mult wallace 1024 w1024.aig` / `gen_mult wallace 2048 w2048.aig`.

Check the example certificate:

```
unxz certificate_example/*.xz
python3 tools/pac_verify.py benchmarks/v1.5/multipliers/booth64.aag benchmarks/v1.5/certificate_example/booth64 --pacheck pacheck
```

Results: [`results/v1.5_nov28/`](../../results/v1.5_nov28/), [`results/sc26_nov24/`](../../results/sc26_nov24/).
