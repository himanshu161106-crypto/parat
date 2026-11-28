# Parat — v1.5

A SAT solver and multiplier verifier. Parat reads a formula in DIMACS CNF and answers:

- **SATISFIABLE**, with an assignment you can check yourself, clause by clause
- **UNSATISFIABLE**, optionally with a DRAT proof that an independent checker verifies
- **unknown**, if time runs out

Next to a CDCL core, Parat has special engines for formula families where general CDCL is weak: noisy parity,
circuits with few inputs, linear equations over GF(2) and GF(3), syndrome decoding, pigeonhole and counting
arguments, and gate-level multipliers (proved correct up to 512 × 512 bits, with checkable certificates).

---

## Highlights of v1.5

- **A 2048 × 2048-bit Wallace multiplier (42 million AND gates) proved correct in about 3.5 minutes** on one CPU core
  with 8 GB RAM (the part that does not fit in RAM goes to disk). A wrong gate gives INCORRECT with a counterexample
  (tested up to 512 bits).
- **Checkable certificates for big multipliers:** a 1024 × 1024-bit PAC certificate (13 GB, 3.1 million steps) was
  checked piece by piece by the independent checker [pacheck](https://github.com/d-kfmnn/pacheck2):
  CERTIFICATE CHECKED (see [Multiplier certificates](#multiplier-certificates)).
- **SAT Competition 2026: 10 main-track files that no competition solver solved within 300 s** are solved by
  Parat v1.5. Three of them (minimum-disagreement-parity) were not solved by any solver at all.
- **Noisy parity** (minimal/minimum-disagreement-parity): the 5 files that no other solver solved within 300 s take
  0.06–4.5 s; competition best was 730 s, 946 s, or not solved.
- **Datapath and multiplier equivalence**: 6 files UNSAT in 0.8–115 s on a laptop; competition best 284–1902 s.
- **One program per system** (Windows, Linux, macOS; Intel/AMD and ARM). Each one is the whole solver and handles
  multipliers from 8 to 8192 bits, picking the number width by itself (tested up to 2048 bits).

Details and per-file tables: [`results/sc26_nov24/`](results/sc26_nov24/).

---

## Downloads

Download from the **Releases** page — one file per system, nothing else needed:

| file | system |
|---|---|
| `parat-v1.5-windows-x64.exe` | Windows 10/11, Intel/AMD 64-bit |
| `parat-v1.5-windows-arm64.exe` | Windows on ARM (Snapdragon laptops) |
| `parat-v1.5-linux-x64` | Linux, Intel/AMD 64-bit (static) |
| `parat-v1.5-linux-arm64` | Linux on ARM 64-bit, e.g. Raspberry Pi 4/5 with a 64-bit OS (static) |
| `parat-v1.5-macos-apple-silicon` | macOS on M1/M2/M3/M4 |
| `parat-v1.5-macos-intel` | macOS on Intel |

`SHA256SUMS.txt` lists the checksums. The Windows
x64 and Linux x64 programs were tested on real machines, Linux ARM64 under an emulator. The macOS and Windows-ARM
programs were cross-compiled and have not been run on real hardware yet — please report problems.

On macOS the program is not signed by Apple. Once, after downloading:

```
xattr -d com.apple.quarantine parat-v1.5-macos-*
chmod +x parat-v1.5-macos-*
```

---

## Quick start

Windows (Command Prompt or PowerShell):

```
parat-v1.5-windows-x64.exe file.cnf
parat-v1.5-windows-x64.exe file.cnf 0 300          (seed 0, time limit 300 s)
```

Linux / macOS:

```
./parat-v1.5-linux-x64 file.cnf
./parat-v1.5-linux-x64 file.cnf --proof proof.drat   # UNSAT with a DRAT proof
drat-trim file.cnf proof.drat                        # -> s VERIFIED, independent checker
./parat-v1.5-linux-x64 mult.aig 1 300 --pac cert     # prove a multiplier correct, with a certificate
pacheck cert.polys cert.proof cert.spec              # -> TARGET CHECKED (small certificates)
python3 pac_verify.py mult.aig cert                  # -> s CERTIFICATE CHECKED (any size, piece by piece)
```

Output follows the SAT Competition format: `s ...` and `v ...` lines. Exit code `10` = SAT, `20` = UNSAT,
`0` = unknown, `2` = input error.

---

## SAT Competition 2026 (main track)

### Files no competition solver solved within 300 s

| file | family | answer | Parat v1.5 | best in competition |
|---|---|---|---:|---:|
| 1eea3d91 | minimal-disagreement-parity | SAT | 0.1 s | 730 s |
| 61fee64c | minimal-disagreement-parity | SAT | 0.06 s | 946 s |
| 16ca57f2 | minimum-disagreement-parity | UNSAT | 2–4 s | not solved |
| 23daec2c | minimum-disagreement-parity | UNSAT | 1–2 s | not solved |
| 425c81fc | minimum-disagreement-parity | UNSAT | 2–3 s | not solved |
| 27495ba0 | datapath-equivalence-checking | UNSAT | 0.8 s | 1902 s |
| 2a38c5d4 | datapath-equivalence-checking | UNSAT | 92.6 s | 1620 s |
| 5ab5ac8d | datapath-equivalence-checking | UNSAT | 88.1 s | 1772 s |
| e685a5d9 | datapath-equivalence-checking | UNSAT | 89.5 s | 1690 s |
| de8c42d5 | multiplier-equivalence-checking | UNSAT | 81.9 s | 675 s |

Datapath and multiplier times: Windows laptop, 16 GB RAM. Noisy parity: Linux. "Best in competition" is the fastest
time any competition solver reported (SAT Competition 2026 results).

How these are solved:

- **Noisy parity.** XOR constraints and Gaussian elimination give each sample's error bit as an affine function of the
  secret. Information-set decoding (Prange) finds the secret with the fewest mismatches. For UNSAT: the counter's
  bound is confirmed by clause learning, every secret with few enough mismatches is enumerated exactly, and each one
  is refuted.
- **upsim.** Circuits with up to ~40 inputs whose gates are read from unit propagation (no gate patterns assumed):
  every input value is simulated, 64 per machine word, with constant folding and shared gates per block.

### Where Parat is weaker: general / industrial files

61 general files that competition solvers solve within 300 s, 120 s per file, one core:

| solver | solved | PAR-2 |
|---|---:|---:|
| Kissat 4.0 | 37 | 7085 |
| Parat v1.5 | 25 | 9285 |

On general industrial formulas a mature CDCL solver such as Kissat is clearly ahead; Parat's strength is the families
above. Per-file table: [`results/sc26_nov24/groupC_61files_120s.csv`](results/sc26_nov24/groupC_61files_120s.csv).

A full run of Parat v1.5 on all 400 main-track files (300 s each) is in progress; its results will be added here.

### Checks

Every SAT model is checked clause by clause against the original file. In the runs above there was no wrong answer.
The noisy-parity and upsim UNSAT answers come from normal mode; they do not come with a DRAT proof yet.

---

## Earlier benchmarks (v1.4)

### Random and SATLIB

| benchmark | instances | result |
|---|---:|---|
| UF50-218 | 1,000 | 1,000 valid SAT models |
| UF250-1065 | 100 | 100 valid SAT models |
| BMS_k3_n100_m429 | 500 | 500 valid SAT models |
| flat200-479 | 100 | 100 valid SAT models |
| UUF100-430 | 1,000 | 1,000 UNSAT, as expected |
| UUF200-860 | 99 | 99 UNSAT, as expected |
| UUF250-1065 | 100 | 100 UNSAT, as expected |
| SAT Competition 2005 Industrial | 176 | 144 valid SAT models, 32 timeouts |
| Random 3-SAT, 50,000 variables, ratio 4.22 | 1 | solved in 36 s, model valid on all 211,000 clauses |

### Multiplier verification (AIGER `.aag` / `.aig`)

v1.5, Linux, one core, 7–8 GB RAM, Wallace designs from `gen_mult`:

| operands | AND gates | answer | time |
|---|---:|---|---:|
| 256 × 256 bits | 0.66 M | CORRECT | 3.4 s |
| 512 × 512 bits | 2.6 M | CORRECT | 8.9 s |
| 512 × 512 bits, one gate wrong | 2.6 M | INCORRECT + counterexample | 0.1 s |
| 2048 × 2048 bits | 42 M | CORRECT | 2 min 57 s |

v1.4 (normal build):

| operands | product | time |
|---|---:|---:|
| 16 × 16 bits | 32 bits | 0.13 s |
| 32 × 32 bits | 64 bits | 0.74 s |
| 64 × 64 bits | 128 bits | 4.40 s |
| 128 × 128 bits | 256 bits | 6.32 s |
| 256 × 256 bits | 512 bits | 13.89 s |
| 512 × 512 bits | 1,024 bits | 26.71 s |

- 512-bit array, Wallace and Booth designs: all proved CORRECT in 20–30 s each. With one gate changed: INCORRECT with
  the exact counterexample in 41 s.
- 512-bit Wallace (2.6 M AND gates) with a PAC certificate: ~5.5 min to write it, `pacheck2` checks it in ~2.5 min.
- Multiplier-equivalence miter, 10-bit: proved in 0.009 s (a general CDCL solver needed over 2 minutes).

### Proofs

| test | result |
|---|---|
| DRAT proof, 31-bit prime-factoring UNSAT file | written in 11.3 s, `s VERIFIED` by `drat-trim` in 31.0 s |
| PAC certificate, 64-bit Wallace multiplier | written in 0.57 s, `TARGET CHECKED` by `pacheck2` in 0.50 s |

Older result files are in [`results/`](results/); benchmark files and generators in [`benchmarks/`](benchmarks/) and
[`verify/`](verify/).

---

## Multiplier certificates

`--pac cert` writes a PAC certificate (`cert.polys`, `cert.proof`, `cert.spec`). Small ones can be checked directly
with `pacheck`. Big ones are checked piece by piece with
[`tools/pac_verify.py`](tools/pac_verify.py) (Python 3, standard library only) and `pacheck`:

```
PARAT_PAC_CHK=600000000 PARAT_PAC_CHKMAX=600000000 ./parat-v1.5-linux-x64 w1024.aig 1 100000 --pac cert
python3 tools/pac_verify.py w1024.aig cert --pacheck ./pacheck --jobs 2
```

`pac_verify.py` does not trust anything Parat wrote:

1. It builds every gate polynomial and the spec (sum 2^k s_k - sum 2^(i+j) a_i b_j) from the AIGER file itself and
   compares Parat's `.polys` / `.spec` with them.
2. It cuts the proof into pieces; pacheck checks every step of every piece. A piece may only use lines of `.polys` or
   lines of earlier pieces.
3. The last step must give exactly the spec.

| certificate | size | pieces | check time | largest pacheck |
|---|---:|---:|---:|---:|
| 512 × 512 bits | 1.1 GB | 7 | 97 s | 1.6 GB |
| 1024 × 1024 bits | 13.2 GB | 49 | 12.7 min | 1.6 GB |

Twelve kinds of deliberate errors (a changed step, spec, gate or polys line, a missing or extra line, another rule, a
writer stopped half way, ...) were all rejected. `--follow` checks while Parat is still writing; `--jobs N` checks N
pieces at the same time.

---

## Command line

```
parat file.cnf [seed] [time_limit_s] [--proof proof.drat] [--proof-binary]
```

- Default time limit 300 s. The seed can also be set with `PARAT_SEED`.
- `--proof FILE` writes a DRAT proof when the answer is UNSAT; `--proof-binary` makes it about half the size.
- Proof mode uses one core and only methods whose steps can be written as DRAT.

```
parat circuit.aag 1 [time_limit_s] [--pac prefix] [--signed | --unsigned]
```

- ASCII AIGER input: first half of the inputs is `a` (least significant bit first), second half `b`; outputs are the
  product bits.
- Output `s CORRECT MULTIPLIER`, or `s INCORRECT MULTIPLIER` with a counterexample. `--pac prefix` writes
  `prefix.polys`, `prefix.proof`, `prefix.spec` when the answer is CORRECT.

---

## Limits

- Proof mode turns off the methods without a DRAT form yet (noisy parity, upsim, counting mod q, the algebraic
  multiplier method). Files only those solve end as "unknown" in proof mode, never as an unchecked UNSAT.
- On general industrial files Parat is behind mature CDCL solvers (see the table above).
- Multipliers up to 8192 x 8192 bits in one program (tested up to 2048 bits; about 9 GB for 2048 bits, the rest
  spilled to disk; 4096 and 8192 bits need far more memory).
- Multiplier mode handles unsigned and signed (two's complement) AND-inverter graphs, inputs `a` then `b`.
- Certificates can be large (hundreds of MB at wide bit-widths).
- The very-large random 3-SAT engine only finds answers; without one it ends as "unknown".

## Licensing

- Free: personal use, academic research and teaching, publishing benchmark results, evaluation.
- Your results are yours: answers, proofs and certificates Parat writes for your files belong to you.
- Paid commercial licence for use in a product, service or a company's production work.
- Full terms: [`LICENSE`](LICENSE) (Parat Software License).

## Acknowledgements

Parat builds on published ideas: CDCL (VSIDS, Luby and Glucose restarts, clause minimization and shrinking, bounded
variable elimination, bounded variable addition, equivalent literals), WalkSAT-style local search, survey
propagation, Gaussian elimination, Prange's information-set decoding, and algebraic/PAC methods for multipliers.
Comparisons and checks use Kissat, `drat-trim` (Marijn Heule, Nathan Wetzler, Warren Hunt) and `pacheck2` (Daniela
Kaufmann, Armin Biere and others, JKU Linz). Competition files and results: SAT Competition 2026.
