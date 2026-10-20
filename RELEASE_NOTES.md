# Update 7, Oct 20 2026: multipliers optimised by ABC, and 256-bit multipliers

**Download:** `bin/parat-linux-x86_64` and `bin/parat-windows-x86_64.exe` (release v1.2).

## New
- **Multipliers whose adders were rewritten by ABC** (yosys's default flow) are now proved. yosys `synth -booth`
  with ABC on: 32, 40, 48, 56, 64 and **128 bits (128,350 AND gates, 110 s)** proved; before, 40-bit and up timed
  out. With `--pac` they come with a certificate: pacheck2 TARGET CHECKED plus DRAT files that drat-trim verifies
  (128-bit: 126 s, 194 MB). AMulet2 (`-verify`, one core, 300 s) times out on all of them, 32 to 64 bits.
  Table: README section 10.
- **256 × 256-bit multipliers** (512-bit output) are supported; a 505,552-gate Booth design is proved in 6 s.
- `verify/eq_cnf.py` (new) and `verify/verify_multiplier.sh` (extended): rebuild Parat's SAT files from your own
  circuit and check every proof with drat-trim, next to the pacheck2 check.
- Broken designs: a SAT counterexample that the new step finds is checked against a × b at once, so broken ABC
  designs are answered INCORRECT in 8–22 s.

## Fixed
- Above 128-bit inputs, the counterexample search used a reference product that was too short, so a correct
  multiplier could be reported INCORRECT (v1.1, only for designs wider than 128 bits).
- The largest algebra attempt is now limited to 1,000,000 terms (it could use 5 GB or more on designs it then failed
  on; every proof in the 71-design check below needs less than 500,000).

## Checks on the final build
- 71 multipliers from the earlier tables: every answer the same as before, total 286 s.
- yosys Booth designs with ABC 32–128 bits, the 256-bit design, 4 broken designs: all answers right
  (`results/abc_booth_oct20.txt`). Certificates 56- and 128-bit: pacheck2 TARGET CHECKED, every DRAT file VERIFIED,
  every SAT file rebuilt byte for byte by `verify/eq_cnf.py`.
- Release smoke test from a fresh copy (README commands, old and new multiplier paths, broken designs, the README
  Verilog flow with and without ABC): 14 of 14 passed. No method names in the binary's strings.

## Honest limits
- The new step was tested on yosys `synth -booth` netlists. Other ABC netlists may still time out; Wallace +
  carry-lookahead (GenMul `wt-cl`) is still not proved.
- The 256-bit design's ABC step was done by yosys 0.33 (WASM ABC took more than 2 hours); that netlist is proved by
  the old algebra directly, so the 256-bit result shows the wider numbers, not the new step.
- For these designs Parat runs copies of itself as child processes and writes temporary files (deleted at the end).
  The Windows build was compiled from the same sources but this new path was only tested on Linux.

# Update 6, Oct 18 2026: certificates for yosys Booth multipliers

**Download:** `bin/parat-linux-x86_64` and `bin/parat-windows-x86_64.exe`.

## Fixed
- **yosys Booth multipliers (`synth -booth -noabc`) now get a certificate.** Before, Parat proved them but wrote
  no certificate ("one step has no certificate form yet"). Now 32, 64 and 128 bits: pacheck2 TARGET CHECKED
  (`results/yosys_booth_pac_oct18.txt`). 128-bit: proved in 1.5 s, certificate in 22 s (283 MB).

## Checks on the final build
- benchmarks/multipliers: every certificate TARGET CHECKED, broken designs INCORRECT; 200 random fuzz designs:
  0 problems; 4 GenMul designs re-checked (same certificate sizes as before); 67 of 67 UNSAT files still UNSAT.
- Release smoke test: 15 of 15 passed. No method names in the binary's strings.

## Still open
- 64-bit `synth -booth` with ABC and other ABC-optimised netlists still time out. Wallace + carry-lookahead is still
  not proved. Ratio 4.26 at a million variables is not solved yet.

# Update 5, Oct 18 2026: very large random 3-SAT, Verilog how-to, who built it

**Download:** `bin/parat-linux-x86_64` and `bin/parat-windows-x86_64.exe`.

## New
- **A second engine for random 3-SAT with 10,000+ variables** (only for formulas where every rule has 3 literals;
  it only finds answers). One core, release binary, every answer checked:
  10,000,000 variables at ratio 4.22: 3424 s; 1,000,000 at 4.22: 236 s (original survey-propagation solver:
  1742 s); 100,000 at 4.25: 4 of 4 files (original SP solver: 1 of 4). Table: README section 9.
- **`verify/gen_random3.c`:** seeded generator that rebuilds the big files byte for byte.
- **README "Your own multiplier: from Verilog to AIGER"**: tested yosys commands (thanks to a reader on r/chipdesign).
- **README "Who built this"**: the code was written by AI (Claude); the ideas, the math and the direction are
  Himanshu's.

## Checks on the final build
- Every big random answer checked clause by clause (`results/big_random_oct18.txt`); the generator rebuilds every
  big file byte for byte.
- 67 of 67 files in `benchmarks/general_unsat/` still answered UNSAT; booth64 certificate: pacheck2 TARGET CHECKED;
  the README's yosys commands tested end to end (16-bit multiplier proved, certificate TARGET CHECKED).
- Release smoke test (every README command from a fresh copy): 15 of 15 passed.
- The binary was scanned: no method names in its strings.

## Honest limits
- The new engine does not prove "no answer", and ratio 4.26 at a million variables or more is not solved yet.
- Multiplier netlists optimised by ABC (yosys's default `synth`) time out (16 bits; AMulet2 also times out on 12).
- Everything from Update 4 still applies (factoring vs Kissat, Wallace + carry-lookahead, certificate size).

# Update 4, Oct 12 2026: certificates for every proved GenMul design, signed multipliers, Windows

**Download:** `bin/parat-linux-x86_64` and, new, `bin/parat-windows-x86_64.exe` (also attached to the v1.0 release page).

## New
- **Certificates:** all 27 GenMul designs that Parat proves at 64 bits now come with a PAC certificate that pacheck2
  checks (before: 8). This includes the fast final adders (Kogge-Stone, Brent-Kung, Ladner-Fischer,
  carry-lookahead, carry-skip) and the counter-tree designs (`results/genmul64_pac_oct12.txt`).
- **Signed multipliers** (two's complement), detected automatically (`--signed` / `--unsigned` to force): 26 of the
  27 signed GenMul designs at 64 bits proved and certified; AMulet2 `-signed`: 11 (`results/genmul64_signed_race.txt`).
- **Rare bugs:** bugs that change the output on about 1 input in 2^20 are now found on 6 of 8 test designs in
  2–16 s; before, the answer was "unknown" (`results/rare_bugs_oct12.txt`, files in `benchmarks/rare_bugs/`).
- **Random 3-SAT, ratio 4.26:** "no answer" files at n=380: 132 s -> 106–112 s for 7 files (march_nh 113 s).
  Files with an answer at n=1000: 60/60 solved, mean 2.73 s (probSAT 2.84 s, YalSAT 3.66 s).
- **Structured files:** 140 of 143 solved (was 137), PAR-2 3.80 -> 2.66 s (`results/scorecard_oct12.txt`).
- **Big files** are read about 20% faster (5 industrial files: 5.97 -> 4.70 s; Kissat 5.06 s).
- **Windows:** a native `.exe` (one core). Run it from a terminal, for example Git Bash.

## Checks on the final build
- 67 of 67 DRAT proofs on `benchmarks/general_unsat/` verified by drat-trim.
- 170 general files: same answers as the Oct 11 release, every SAT answer checked.
- Fuzz: 210 signed and 65 unsigned random multipliers (most broken): 0 wrong answers, every certificate CHECKED.

## Honest limits
- Prime factoring: Kissat is still about 1.8x faster.
- Wallace + carry-lookahead (signed or unsigned) is not proved. AMulet2 does not prove it either.
- Some certificates are big (up to 1.3 GB at 64 bits).
- Colouring files without an answer became about 1.8x slower (the price of solving more colouring files that have one).
- The Windows build uses one core and has been tested on one PC so far.

---

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
