# Parat (Linux x86-64) — v1.4

A SAT solver for hard random 3-SAT, whose "no answer" results come with a proof that anyone can check.

Parat reads a formula in DIMACS CNF and answers one of three things:

- **SATISFIABLE**, with an assignment you can check in one second
- **UNSATISFIABLE**, optionally with a DRAT proof that an independent checker verifies
- **unknown**, if time runs out

It is built for the hardest region of random 3-SAT, near the threshold (clause/variable ratio 4.2–4.26). It also solves structured and industrial files correctly, and proves gate-level multiplier circuits correct up to 512-bit operands.

This build is **Linux x86-64 only**: `parat-linux-x86_64`, static, needs nothing else, uses all cores.

---

## What Parat can do (v1.4)

| task | how to run | what you get | how you check it without trusting Parat |
|---|---|---|---|
| Solve a SAT formula (DIMACS CNF) | `parat file.cnf` | an answer, or "no answer" | check the model clause by clause yourself |
| Prove "no answer" | `parat file.cnf --proof p.drat` | UNSAT + a DRAT proof | `drat-trim` |
| Prove a gate-level multiplier correct (`.aag`), unsigned or signed | `parat mult.aag 1 300` | CORRECT, or INCORRECT with a counterexample input | simulate the counterexample |
| ... with a certificate | `parat mult.aag 1 300 --pac cert` | PAC certificate (`.polys`/`.proof`/`.spec`) | `pacheck2` |
| Very large random 3-SAT (10,000+ variables) | `parat big.cnf` | an answer (this engine does not prove "no answer") | check the model clause by clause |

**Strongest where:**
- Hard random 3-SAT near the threshold: proving "no answer" level with specialist lookahead solvers, far ahead of plain CDCL.
- Multipliers: array, Wallace and Booth designs, correctness proofs up to 512 × 512 bits in well under a minute, with PAC certificates that `pacheck2` checks independently.
- Multiplier-equivalence miters (two multipliers that must compute the same thing): proved by algebra in a fraction of a second on cases where CDCL solvers take minutes and do not finish.
- Factoring and SATLIB-style random instances: solved correctly and quickly, with every SAT model independently verified.

**Weaker / not done on this build:**
- Factoring circuits: a general-purpose CDCL solver can be faster on some prime-factoring files.
- The full 28-design GenMul family (Dadda trees, counter-based Wallace, and the fast final-adder variants) is not built/packaged with this release.
- ABC-optimized netlists (yosys `synth -booth` with ABC) and multipliers past 512 bits are outside this build's tested range.
- Windows and macOS binaries are not part of this release.

---
512-Bit Multiplier — Proof-Checked via PAC Certificate
Parat has successfully proven a 512-bit Wallace-tree multiplier (consisting of 2,631,069 AND gates) correct while generating a PAC (Proof-Altering Certificate) alongside the result. This provides more than just a binary answer—it delivers a fully checkable algebraic proof trail.

The generated certificate files (.polys, .proof, and .spec) were independently verified using pacheck2, a completely separate verification tool featuring its own independent math engine that shares no code with Parat.

Execution and Verification Breakdown
Step	Time	Result & Artifact Details
Parat (Solve + Write Certificate)	~5–5.5 min	
s CORRECT MULTIPLIER


(File sizes: 2.18 GB proof, 122 MB polys, 43 MB spec)

pacheck2 (Independent Verification)	~2.5 min	TARGET CHECKED
Total Pipeline Time	~7.5–8 min	Result independently confirmed (zero reliance on self-reporting)
Key Takeaway: Without certificate generation, the exact same 512-bit multiplier is verified correct in just 27 seconds. The additional time required for the certificate funds a complete, rigorous algebraic proof trail for a 2.6-million-gate circuit—enabling anyone to mathematically verify the correctness without having to trust Parat blindly.
# PARAT — Benchmarks & Capabilities

## Overview

Parat is a SAT-solving and logic-circuit verification tool. Its tested capabilities include Boolean satisfiability solving, selected constraint problems, factoring-related CNF instances, and digital multiplier-circuit verification.

## SAT Benchmark Results

| Benchmark | Instances | Result |
|---|---:|---|
| UF50-218 | 1,000 | 1,000 valid SAT models |
| UF250-1065 | 100 | 100 valid SAT models |
| BMS_k3_n100_m429 | 500 | 500 valid SAT models |
| SW100-8-p0-c5 | 1 | 1 valid SAT model |
| flat200-479 | 100 | 100 valid SAT models |
| UUF100-430 | 1,000 | 1,000 expected UNSAT statuses |
| UUF200-860 | 99 | 99 expected UNSAT statuses |
| UUF250-1065 | 100 | 100 expected UNSAT statuses |
| SAT Competition 2005 Industrial | 176 | 144 valid SAT models; 32 timeouts |

Returned SAT assignments in these benchmarks were independently checked against the original CNF clauses. The UUF results represent expected UNSAT-status matches.

## Multiplier Circuit Verification

Parat successfully verified generated full-product multiplier circuits at these sizes:

| Operand Size | Product Width | Recorded Verification Time |
|---|---:|---:|
| 16 × 16 bits | 32 bits | 0.13 seconds |
| 32 × 32 bits | 64 bits | 0.74 seconds |
| 64 × 64 bits | 128 bits | 4.40 seconds |
| 128 × 128 bits | 256 bits | 6.32 seconds |
| 256 × 256 bits | 512 bits | 13.89 seconds |
| 512 × 512 bits | 1,024 bits | 26.71 seconds |

The tested 512-bit-input multiplier contained 2,614,272 AND gates. Its outputs were independently compared with exact integer multiplication for 64 operand pairs. Several deliberately modified circuits were also rejected with counterexamples.

## Additional Capabilities

- **Graph colouring:** Tests on colourable graphs and selected unsatisfiable colourings.
- **Constraint solving:** Generated Sudoku and pigeonhole-style instances.
- **Factoring-related SAT:** Tested composite-number factor pairs, including 15 = 3 × 5 and larger semiprimes.
- **Circuit equivalence:** Selected small adder and multiplier circuits.
- **CNF processing:** DIMACS comments, multi-line clauses and parser edge cases.

## Tested Input Formats

- DIMACS CNF (`.cnf`)
- ASCII AIGER (`.aag`) for selected circuit-verification tasks

## Performance

Reported runtimes were measured on the recorded test machine. Actual performance varies with the benchmark instance, circuit design, hardware and time limit.
## Quick start (Linux x86-64)

```
chmod +x parat-linux-x86_64

# 1. solve a file
./parat-linux-x86_64 file.cnf

# 2. prove "no answer" with a checkable proof
./parat-linux-x86_64 file.cnf --proof proof.drat
drat-trim file.cnf proof.drat        # -> s VERIFIED, independent checker

# 3. prove a multiplier correct, with a certificate
./parat-linux-x86_64 mult.aag 1 300 --pac cert
pacheck cert.polys cert.proof cert.spec   # -> TARGET CHECKED, independent checker
```

`drat-trim` (Marijn Heule) and `pacheck2`/`pacheck` (Daniela Kaufmann, JKU Linz) are small, independent, open-source checkers; neither shares code with Parat. Building them yourself takes a few minutes:

```
git clone https://github.com/marijnheule/drat-trim && make -C drat-trim
git clone https://github.com/d-kfmnn/pacheck2 && (cd pacheck2 && ./configure.sh && make)   # needs g++ and libgmp-dev
```

---

## Command line

```
Usage: parat file.cnf [seed] [time_limit_s] [--proof proof.drat] [--proof-binary]
```
Output follows the SAT Competition format: `s ...` and `v ...` lines. Exit code: `10` = SAT, `20` = UNSAT, `0`/`2` = unknown or input error.

- The default time limit is 300 s. The seed can also be set with `PARAT_SEED`.
- `--proof FILE` writes a DRAT proof when the answer is UNSAT. `--proof-binary` makes the file about half the size.
- Proof mode uses one core and only the methods whose steps can be written as DRAT.

```
Usage: parat circuit.aag 1 [time_limit_s] [--pac prefix] [--signed | --unsigned]
```
- Input: an ASCII AIGER file (`.aag`). The first half of the inputs is `a` (least significant bit first), the second half `b`; the outputs are the product bits.
- Output: `s CORRECT MULTIPLIER` or `s INCORRECT MULTIPLIER` with a counterexample (`a`, `b`, circuit output, `a × b`). Exit code `0` / `1`.
- `--pac prefix` writes `prefix.polys`, `prefix.proof`, `prefix.spec` (Practical Algebraic Calculus) only when the answer is CORRECT. Nothing is written for a broken circuit.
- Signed or unsigned: Parat decides by simulating the circuit; `--signed`/`--unsigned` force it.

---

## Results (this build)

| test | result |
|---|---|
| DRAT proof on a 31-bit prime-factoring UNSAT instance | written in 11.3 s, **independently `s VERIFIED`** by `drat-trim` in 31.0 s |
| PAC certificate on a 64-bit Wallace multiplier | written in 0.57 s, **independently `TARGET CHECKED`** by `pacheck2` in 0.50 s |
| 512-bit array / Wallace / Booth multipliers | all proved CORRECT in 20–30 s each |
| 512-bit Wallace with one gate changed | correctly answered INCORRECT, with the exact counterexample, in 41 s |
| Multiplier-equivalence miter, 10-bit | proved in 0.009 s (a general CDCL solver needed over 2 minutes on the same file and did not finish at 12 bits in 60 s) |
| Random 3-SAT, 50,000 variables, ratio 4.22 | solved in 36 s, model independently valid across all 211,000 clauses |
| 65 fresh random 3-SAT files (SATLIB-style and hard-ratio) | 65/65 correct, every model independently checked clause by clause |
| Malformed/out-of-range input headers | rejected cleanly with an error message and exit code 2 (fixed in this build) |

---

## Licensing

- Free: personal use, academic research and teaching, publishing benchmark results, and evaluation.
- Your results are yours: answers, proofs and certificates that Parat writes for your files belong to you.
- Paid commercial license: use in a product or service, or in a company's production work (for example EDA, hardware or software verification, scheduling, planning or configuration tools).
- Full terms: see `LICENSE` (Parat Software License).
- 

## Limits

- Proof mode uses one core and turns off the methods that have no DRAT form yet (a counting argument for pigeonhole-type formulas, and the algebraic argument for multiplier circuits). Files that only those methods solve end as "unknown" in proof mode instead of an unchecked UNSAT.
- Multiplier mode handles unsigned and signed (two's complement) multipliers given as AND-inverter graphs, inputs `a` then `b`. Other encodings (for example sign-magnitude) are not supported.
- Certificates are written only when every step has a certificate form; otherwise Parat prints the reason and writes nothing. Certificates can be large (hundreds of MB at wide bit-widths).
- For a broken design past Parat's tested range, or where every method runs out of time, the answer is "unknown" — no claim either way.
- The very-large-random-3-SAT engine only finds answers; with no answer it ends as "unknown". It is made for random 3-SAT and is not used on other formula types.
- This is a Linux x86-64 build. It uses all available cores by default.

## Acknowledgements

Parat builds on published ideas from the SAT literature: CDCL (VSIDS, Luby and Glucose restarts, clause minimization, bounded variable elimination, equivalent-literal replacement), survey propagation for very large random 3-SAT, WalkSAT-style local search, and algebraic/PAC methods for multiplier verification. Comparisons and independent checks in this document use Kissat, `drat-trim` (Marijn Heule, Nathan Wetzler, Warren Hunt) and `pacheck2` (Daniela Kaufmann, Armin Biere and others, JKU Linz). Some benchmark files are generated with the standard SATLIB-style random 3-SAT distribution.
