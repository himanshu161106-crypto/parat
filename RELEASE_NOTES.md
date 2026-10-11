# Update 3, Oct 11 2026 (night): big random files + full scorecard

- Random 3-SAT with an answer, 10,000–100,000 variables: Parat now solves all 24 fresh runs; at 100,000 variables
  YalSAT and probSAT solve none in 120 s (Parat 82 s on average).
- Full scorecard in 7 categories against the best solver of each (`results/scorecard_oct11.txt`), 0 wrong answers.
- Correction: on hard random "no answer" files Parat is level with march_nh (who wins changes from run to run), not
  ahead as an earlier README line said.

---

# Update 2, Oct 11 2026 (evening): the GenMul multiplier family

**Download:** `bin/parat-linux-x86_64` (also attached to the v1.0 release page). Nothing else changes in how it is used.

## New
- Parat proves **27 of the 28 GenMul multiplier designs** at 64 bits: array / Wallace / Dadda / counter trees with
  ripple, carry-lookahead, Ladner-Fischer, Kogge-Stone, Brent-Kung, carry-skip and serial-prefix adders.
  AMulet2 proves 8 of them in the same 300 s per design. Table: `results/genmul64_race.txt`.
- Wallace multipliers are 1.6–2.5x faster than AMulet2 (128-bit: 1.31 s vs 3.2 s, with certificate). Certificates
  are smaller.
- Broken multipliers: faster counterexamples.
- General SAT files: 258-file check, 0 wrong answers, 2 more files solved than before, total time 281 s -> 264 s.

## Honest limits
- Designs with fast final adders are proved, but without a certificate (one kind of step has no certificate form
  yet). Parat says so.
- One GenMul design (Wallace + carry-lookahead) is not proved, by either tool.
- Random 3-SAT with an answer: still level with YalSAT (ahead on 12 of 16 hard files, not statistically proven).
- Prime factoring circuits: Kissat is still about 1.6x faster.

---

# Update, Oct 11 2026 — multiplier circuits with certificates (part of v1.0, binary in bin/)

**Download:** `bin/parat-linux-x86_64` from the repo (static Linux x86-64; on Windows use WSL). Everything else
works the same way.

## New
- **Multiplier mode:** `parat circuit.aag 1 [time_limit_s]`. It proves that a gate-level multiplier (ASCII AIGER, the
  AMulet2 input format) computes a × b, or prints a counterexample input.
- **PAC certificates:** `--pac prefix` writes a certificate that pacheck2 (JKU Linz) checks against the circuit file.
  `verify/verify_multiplier.sh` does both steps.
- Widths up to 128 bits (products up to 256 bits).

## Measured (same machine, one core; raw numbers in results/multiplier_pac.txt)

| circuit | Parat incl. certificate | AMulet2 incl. certificate |
|---|---|---|
| array 128-bit | 1.45 s | 152 s |
| Booth 128-bit | 1.87 s | 43.7 s |
| Wallace 128-bit | 3.43 s | 3.3 s |

- Every Parat certificate was checked by pacheck2 (TARGET CHECKED).
- Broken circuits get a counterexample and no certificate.
- Tampered certificates are rejected.

## Checksum
See SHA256SUMS.

---

# Parat v1.0 — first public release

**Download:** `bin/parat-linux-x86_64`. It is a static Linux x86-64 binary with no dependencies; on Windows, use it
inside WSL.

## What it does
- Solves SAT problems in DIMACS CNF. Output follows the SAT Competition format, with exit codes 10 (SAT), 20 (UNSAT)
  and 0 (unknown).
- **New in this release: certified "no answer".** `--proof proof.drat` writes a DRAT proof for every UNSAT result,
  which the independent checker drat-trim verifies. `--proof-binary` makes the proof file smaller.
- Strongest on hard uniform random 3-SAT near the threshold (ratio 4.2–4.26). It also handles structured and
  industrial files.

## Measured (details and raw logs in README.md and results/)

**Proving "no answer", random 3-SAT at ratio 4.26:**
- w400_2: 26.8 s, against march_nh 28.9 s and Kissat over 3000 s.
- w500_2: 142–148 s, against march_nh 169 s.

**Files with an answer, random 3-SAT:**
- Faster than probSAT: 13 of 16 hard files, p = 0.01.
- Level with YalSAT, with a small lead that is not proven.

**DRAT certificates verified by drat-trim:**
- 32 small random files;
- w400_2 (450 MB proof, checked in 62 s);
- w500_2 (2.2 GB proof);
- 67 of 67 general UNSAT files.

**General check of 258 files:** 0 wrong answers.

## Known limits
- Proof mode uses one core. It switches off two methods that have no DRAT form yet: the counting argument for
  pigeonhole-type formulas and the algebra argument for multiplier circuits. Files that need them end as "unknown".
- Factoring circuits: Kissat is faster.
- Linux x86-64 only.

## Verify this release
```bash
sha256sum bin/parat-linux-x86_64        # compare with the checksum below
bash verify/verify_unsat.sh benchmarks/wall426/w400_2.cnf drat-trim/drat-trim
```

SHA-256 of `bin/parat-linux-x86_64`: see `SHA256SUMS`.
