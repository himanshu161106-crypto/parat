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
