# Parat

**A SAT solver for hard random 3-SAT, whose "no answer" results come with a proof that anyone can check.**

Parat reads a formula in DIMACS CNF and answers one of three things:
- **SATISFIABLE**, with an assignment that you can check in one second;
- **UNSATISFIABLE**, optionally with a DRAT proof that an independent checker verifies;
- **unknown**, if time runs out.

It is built for the hardest region of random 3-SAT, near the threshold (clause/variable ratio 4.2–4.26). It also
solves structured and industrial files correctly.

> **Who built this.** The code was written by AI (Claude, made by Anthropic), under my direction. My part (Himanshu,
> a student): the ideas and the math behind them (for example the +/−/neutral "signal" for each variable, which turned
> out close to survey propagation; reading a variable flip as a Boolean derivative; the "answer is about n/2.5 flips
> away" pattern), choosing what to attack and in what order, running and checking every race, and deciding what to
> publish, limits included. Many parts are standard methods from the SAT literature (see
> [Acknowledgements](#acknowledgements)). No result here depends on trusting the code: answers, DRAT proofs and
> multiplier certificates are all checked by independent tools.

```
$ bin/parat-linux-x86_64 benchmarks/wall426/w400_2.cnf --proof w400_2.drat --proof-binary
s UNSATISFIABLE                                   # 34.7 s on one core

$ drat-trim benchmarks/wall426/w400_2.cnf w400_2.drat
s VERIFIED                                        # 62 s, independent checker
```

---

## At a glance

- **Certified "no answer".**
  - With `--proof`, every UNSAT result comes with a DRAT proof. drat-trim, the checker used by the SAT Competition,
    verifies it without trusting Parat.
  - Verified so far: all 32 small random files, w400_2 (n=400), w500_2 (n=500), and 67 of 67 general files.
- **Proving "no answer" on hard random 3-SAT: level with march_nh (the specialist), far ahead of CDCL:**
  - w400_2: Parat 26.8–31.8 s, march_nh 27.6–29.6 s (who wins changes from run to run), Kissat > 3000 s.
  - n=500: 142 s vs 169 s for march_nh.
  - New (Oct 12): 7 fresh files at n=380: Parat 106–112 s in total (two runs), march_nh 113 s; Parat needed 132 s
    before this update. Level with march, slightly ahead.
- **Very large random files with an answer (new, Oct 18):** a new engine inside Parat for random 3-SAT with 10,000
  or more variables. One core, every answer checked clause by clause:
  - **10 million variables**, ratio 4.22: **3424 s** (57 minutes), 42.2 million rules.
  - 1 million variables, ratio 4.22: **236 s**; the original survey-propagation solver (Braunstein, Mézard,
    Zecchina): 1742 s.
  - 100,000 variables, ratio 4.25: **4 of 4** files (55–679 s); the original SP solver: 1 of 4.
  - YalSAT and probSAT did not solve even the 100,000-variable, ratio 4.22 file in 300 s.
- **Files that have an answer:**
  - Clearly ahead of probSAT: faster on 13 of 16 hard files, p = 0.01.
  - Level with YalSAT, with a small lead that is not statistically proven.
  - New (Oct 12), 20 fresh files at n=1000, ratio 4.26, 3 seeds: Parat 60/60, mean 2.73 s, median 0.31 s;
    probSAT 60/60, 2.84 s, 0.98 s; YalSAT 59/60, 3.66 s, 0.37 s. A lead on all three measures, but a small one.
  - Every one of thousands of answers was checked clause by clause.
- **New (Oct 11 update): multiplier circuits, proved correct with a certificate.**
  - `parat mult.aag 1 300 --pac cert` proves that a gate-level multiplier really computes a × b, or prints an input
    where it does not.
  - The certificate is checked by pacheck2 (JKU), the checker used for AMulet2's certificates.
  - 128-bit Booth: Parat 2.0 s with certificate, AMulet2 43.7 s. 128-bit array: 1.3 s vs 152 s.
  - On the 28 GenMul designs (the family AMulet2's own papers use), 64-bit: Parat proves 27, AMulet2 8, both
    with 300 s per design. **New (Oct 12): all 27 now come with a certificate that pacheck2 checks** (before: 8).
  - **New (Oct 12): signed multipliers** (two's complement, detected automatically): 26 of the 27 signed GenMul
    designs proved and certified; AMulet2 with `-signed`: 11.
- **Nothing to trust blindly.** The repo has everything needed to redo each table on your own machine:
  - an answer checker,
  - a seeded file generator,
  - a race script with a sign test,
  - all raw logs.

## Quick start

Linux x86-64: `bin/parat-linux-x86_64` is static and needs nothing else. **Windows (new, Oct 12):**
`bin/parat-windows-x86_64.exe`, run it from a terminal (for example Git Bash): `./parat-windows-x86_64.exe file.cnf`.
The Windows build uses one core. There is no macOS build yet.

```bash
git clone https://github.com/himanshu161106-crypto/parat && cd parat
chmod +x bin/parat-linux-x86_64

# 1. solve a file and check the answer yourself
bin/parat-linux-x86_64 benchmarks/hard_n1000/h1000_02.cnf > out.txt
python3 verify/check_model.py benchmarks/hard_n1000/h1000_02.cnf out.txt     # -> OK: all 4200 clauses satisfied

# 2. check a "no answer" yourself (needs drat-trim once)
git clone https://github.com/marijnheule/drat-trim && make -C drat-trim
bash verify/verify_unsat.sh benchmarks/wall426/w400_2.cnf drat-trim/drat-trim   # -> s VERIFIED

# 3. check a multiplier proof yourself (needs pacheck2 once)
git clone https://github.com/d-kfmnn/pacheck2 && (cd pacheck2 && ./configure.sh && make)   # needs g++ and libgmp-dev
bash verify/verify_multiplier.sh benchmarks/multipliers/booth64.aag pacheck2/pacheck   # -> TARGET CHECKED
```

### Your own multiplier: from Verilog to AIGER

Parat reads multipliers as ASCII AIGER (`.aag`), inputs **a** then **b** (least significant bit first), outputs the
product bits. [yosys](https://github.com/YosysHQ/yosys) converts Verilog (RTL or a gate-level netlist) to AIGER.
`pip install yowasp-yosys` gives a ready-made yosys (`yowasp-yosys`); a normal `yosys` install works the same way.

```bash
# mult.v:  module mult(input [15:0] a, input [15:0] b, output [31:0] p); assign p = a * b; endmodule
yosys -q -p "read_verilog mult.v; hierarchy -top mult; synth -flatten -top mult -noabc; aigmap; opt_clean; write_aiger -ascii -symbols mult.aag"
bin/parat-linux-x86_64 mult.aag 1 300                    # -> s CORRECT MULTIPLIER  (or a counterexample)
bin/parat-linux-x86_64 mult.aag 1 300 --pac cert          # + certificate for pacheck2
```

- A gate-level netlist of your own design: replace `synth ... -noabc` by `proc; flatten; techmap; aigmap; opt_clean`,
  so that yosys keeps your gates as they are.
- Port order matters: declare `a` before `b`, and keep the product as the only output.
- **Booth-encoded multipliers from yosys** (`synth -booth`, radix-4 Booth; tested Oct 18, one core, 300 s):

  | design | Parat | certificate | AMulet2 (`-verify`) |
  |---|---|---|---|
  | 32-bit, `-booth -noabc` | proved, 0.14 s | not written ("one step has no certificate form yet") | time-out |
  | 32-bit, `-booth` | proved, 0.27 s | pacheck2 TARGET CHECKED | time-out |
  | 64-bit, `-booth -noabc` | proved, 0.57 s | not written | time-out |
  | 64-bit, `-booth` | time-out | — | not run |

  The `booth64` / `booth128` files in `benchmarks/multipliers/` are radix-4 Booth too, but their partial products
  are added with ripple adders (a simpler structure); GenMul itself has no Booth option.
- **Known limit:** with yosys's default `synth` (which runs ABC logic optimisation) the adder structure is rewritten.
  On a 16-bit multiplier Parat then times out (60 s), and so does AMulet2 on 12 bits (120 s); with `-noabc` or
  `-booth`, or the plain `techmap` flow, Parat proves the same 16-bit multiplier. Optimised netlists are a known hard
  case for algebraic methods.

**Command line:**
- Usage: `parat file.cnf [seed] [time_limit_s] [--proof proof.drat] [--proof-binary]`.
- Output follows the SAT Competition format: `s ...` and `v ...` lines. The exit code is 10 = SAT, 20 = UNSAT,
  0 = unknown.
- The default time limit is 300 s. The seed can also be set with `PARAT_SEED`.
- `--proof FILE` writes a DRAT proof when the answer is UNSAT. `--proof-binary` makes the file about 2x smaller.
  - Proof files are large: about 450 MB for n=400 and 2.2 GB for n=500 (binary).
- Proof mode uses one core and only methods whose steps can be written as DRAT. See [Limits](#limits).

**Multiplier mode (Oct 11 update):** `parat circuit.aag 1 [time_limit_s] [--pac prefix] [--signed | --unsigned]`
- Input: an ASCII AIGER file (`.aag`, as used by AMulet2; convert a binary `.aig` with `aigtoaig`). The first half of
  the inputs is a (least significant bit first), the second half b, the outputs are the product bits.
- Output: `s CORRECT MULTIPLIER` or `s INCORRECT MULTIPLIER` with a counterexample (a, b, circuit output, a × b).
  Exit code 0 / 1.
- `--pac prefix` writes `prefix.polys`, `prefix.proof`, `prefix.spec` (Practical Algebraic Calculus) when the answer is
  CORRECT. Check with `pacheck prefix.polys prefix.proof prefix.spec`.
- Signed or unsigned: Parat decides by simulating the circuit (and prints `c specification: signed ...` for signed);
  `--signed` / `--unsigned` force it. The certificate's target then uses the matching specification.

## Results

**Test machine:** one core per run (pinned with `taskset`) of an Intel Xeon @ 2.80 GHz, Linux, 7 GB RAM. Two runs
at once on the two cores.

**Solvers compared:** Kissat 4.0.4, CaDiCaL 3.0.1, march_nh, YalSAT 1.0.1 (git a0fd39f), probSAT SC13_v2.

**How the comparison was kept fair:**
- Every SATISFIABLE answer of every solver was checked clause by clause. There were no wrong answers.
- Test files were **generated fresh with a seed** and were not used to tune Parat.

### 1. Random 3-SAT: proving "no answer"

Local-search solvers (YalSAT, probSAT) cannot do this. The specialists are lookahead (march) and CDCL (Kissat,
CaDiCaL).

| file (`benchmarks/wall426`, ratio 4.26) | Parat | march_nh | Kissat | CaDiCaL |
|---|---|---|---|---|
| w400_2 (n=400) | **26.8 s** | 28.9 s | > 3000 s | |
| w500_2 (n=500) | **142–148 s** | 169 s | not run | not run |

- In the Oct 11 scorecard (`results/scorecard_oct11.txt`, limit 150 s) march_nh was faster on w400_2 (27.6 s vs
  31.8 s) and Parat on w400_0 (43.7 s vs 47.4 s): **level with march**, not ahead. Kissat and CaDiCaL solved neither.
- The Parat and march numbers in this table come from the same earlier day. On the day the proofs were made the
  machine was slower: w400_2 took 33–35 s, for both the current and the previous Parat build. Compare times only
  within one table.
- On the author's scaling sets (n = 250–500, not in this repo), time grows like:
  - Parat: 2^(n/21.3)
  - march: 2^(n/22.3)
  - CaDiCaL: 2^(n/14.5)
- The growth is still exponential, as for every known solver.

### 2. Random 3-SAT: files that have an answer

Local-search solvers are the specialists here. Files that no run solved are left out; they most likely have no
answer.

| set | files × seeds | limit | Parat | YalSAT | probSAT |
|---|---|---|---|---|---|
| n=600, ratio 4.26 (`fresh_n600`) | 12 × 3 | 20 s | **0.066 s** mean, 36/36 | 0.103 s, 36/36 | 0.128 s, 36/36 |
| n=1000, ratio 4.2 (`fresh_n1000`) | 17 × 3 | 30 s | **0.41 s** mean, 51/51 | 1.21 s, 51/51 | 1.30 s, 51/51 |
| n=1000, hard (`hard_n1000`) | 16 × 10 | 60 s | **5.5 s** mean, **0.59 s** median, 152/160 | 5.9 s, 0.75 s, 153/160 | 10.3 s, 1.57 s, 142/160 |

The hard set was picked with separate seeds (a file counts as hard if any solver needed more than 1 s), then
measured with 10 new seeds.

**What the statistics say:**
- **vs probSAT: Parat is faster.**
  - Hard set: faster on 13 of 16 files (sign test p = 0.01). probSAT needs 1.9x the total time (95% CI 1.13–3.66).
  - Fresh sets: faster on 23 of 29 files (p = 0.001).
- **vs YalSAT: level, with a small lead that is not proven.**
  - Hard set: faster on 11 of 16 files (p = 0.1); total time 1.09x (95% CI 0.96–1.63).
  - Fresh sets: lower total time (2.7x, 95% CI 1.03–4.7), but faster on only 17 of 29 files (p = 0.23).
  - Parat makes about 33% more search steps per second.

**Big files (Oct 11 evening update).** Fresh files, ratio 4.2, 3 files per size × 2 seeds, limit 120 s; runs solved
and average time (a failed run counts 240 s):

| variables | Parat | YalSAT | probSAT |
|---|---|---|---|
| 10,000 | **6/6, 2.7 s** | 6/6, 12.0 s | 6/6, 4.2 s |
| 20,000 | **6/6, 18.7 s** | 4/6, 98.4 s | 6/6, 34.3 s |
| 50,000 | **6/6, 34.7 s** | 0/6 | 6/6, 54.9 s |
| 100,000 | **6/6, 81.6 s** | 0/6 | 0/6 |

Before this update Parat used its n=1000 settings for every size and lost to probSAT from about 5,000 variables on
(same scorecard file, "BEFORE"). It now switches to its own start-value signal from 4,000 variables on.

### 3. Certified "no answer" (DRAT proofs)

**How it works:**
- With `--proof`, Parat writes every reasoning step as a clause. Each clause follows from the formula and the earlier
  clauses by unit propagation, and the last one is the empty clause.
- drat-trim (Marijn Heule) reads the **original formula** and the proof and checks every step. It shares no code with
  Parat.

| files | Parat with proof | proof size (binary) | drat-trim | result |
|---|---|---|---|---|
| 29 random files, n = 150–200 | < 0.1 s each | 12–56 KB | < 0.3 s each | 29 × VERIFIED |
| 3 random files, n=300, ratio 4.26 | 2.5–3.4 s | 14–22 MB | 5–6.5 s | 3 × VERIFIED |
| w400_2 (n=400) | 34.7 s (34.8 s without proof) | 450 MB | 62 s | VERIFIED |
| w500_2 (n=500) | 239 s (machine shared with other jobs) | 2.2 GB | 307 s | VERIFIED |
| `general_unsat/`: 67 files (SATLIB aim/dubois, pigeonhole, parity, colouring, factoring and adder circuits, competition grid networks) | | | | **67 × VERIFIED** |

- Writing the proof costs about 2–6% extra time.
- Check them all yourself: `bash verify/verify_all_unsat.sh benchmarks/general_unsat drat-trim/drat-trim`

### 4. General files

- **Check of 258 files** (20 s limit): SATLIB, colouring, pigeonhole, queens, sudoku, circuits, small industrial.
  - Results: 179 SAT, 72 UNSAT, 7 unknown, **0 wrong answers**.
  - Every SAT answer was checked.
  - Kissat 4.0.4 agrees with every UNSAT answer it could finish (67), and contradicts none.
  - The other 5 are multiplier-equivalence miters (two equal 10–32 bit multipliers). Parat proves them with an
    algebraic method that has no DRAT form yet, and Kissat cannot finish them in 120 s.
- **Earlier lab measurements** (files not in this repo):
  - 42 small industrial files: Parat 24.8 s total vs Kissat 94.9 s, fastest on 33.
  - Weak spot: factoring circuits. On 8 fresh prime-factoring files (28–31 bit) Kissat is about 1.6x faster
    (23.9 s vs 39.2 s in total; it was about 2.5x before the Oct 11 update). On the 5 prime files of the scorecard
    (fprime29–33) Kissat is about 1.8x faster (25.6 s vs 45.4 s, Oct 12 build).

### 5. Multiplier circuits (new, Oct 11 update)

**The question:** does this gate-level circuit compute a × b for every input? (For 128-bit inputs that is 2^256
cases, so testing cannot answer it.)

**How the check works:**
- `prefix.polys` contains only the circuit, one polynomial per AND gate, read from your `.aag` file.
- `prefix.spec` is the statement "outputs = a × b (mod 2^width)".
- `prefix.proof` derives the statement from the circuit. pacheck2 (Daniela Kaufmann, JKU Linz) checks every step with
  exact integers. It shares no code with Parat.

Same files, same machine, one core. Times include writing the certificate.

| circuit | Parat | Parat certificate | AMulet2 | AMulet2 certificate | pacheck2 on both |
|---|---|---|---|---|---|
| array 64-bit | **0.30 s** | 4.0 MB | 6.2 s | 14 MB | CHECKED |
| Booth 64-bit | **0.35 s** | 7.2 MB | 2.5 s | 17 MB | CHECKED |
| Wallace 64-bit | **0.34 s** | 4.2 MB | 0.54 s | 7.1 MB | CHECKED |
| array 128-bit | **1.31 s** | 19 MB | 152 s | 82 MB | CHECKED |
| Booth 128-bit | **2.03 s** | 37 MB | 43.7 s | 104 MB | CHECKED |
| Wallace 128-bit | **1.31 s** | 20 MB | 3.2 s | 43 MB | CHECKED |

- **Array and Booth:** Parat is 7–100x faster, with certificates 2–4x smaller.
- **Wallace:** Parat 1.6–2.5x faster (it was about equal before the Oct 11 evening update).
- **Broken circuits** (one gate changed): Parat answers INCORRECT, prints a counterexample, and writes no certificate.
  `benchmarks/multipliers/*_buggy.aag` are two such files.
- **Tamper test:** changing one gate in `prefix.polys`, halving the modulus, or changing the target makes pacheck2
  reject the certificate.
- **Lab fuzz:** 200 random multipliers of 2–24 bits. All 164 certificates were CHECKED, and none of the 36 broken
  designs got a certificate.
- Raw numbers: `results/multiplier_pac.txt`. Files: `benchmarks/multipliers/` (128-bit ones are gzipped).

### 6. The GenMul family: 28 multiplier designs (Oct 11 evening update)

GenMul (Mahzoon, Große, Drechsler; github amahzoon/genmul) generates the multipliers used in AMulet2's evaluation:
4 partial-product trees (array, Wallace, Dadda, counter-based Wallace with 7:3 counters) × 7 final adders
(ripple carry, carry-lookahead, Ladner-Fischer, Kogge-Stone, Brent-Kung, carry-skip, serial prefix). All 28 are
in `benchmarks/genmul64/` (gzipped AIGER, made with `verify/gen_genmul.py` and yosys).

64-bit, one core, 300 s per design, same machine and files for both:

| | proved CORRECT | median time | with a checked certificate |
|---|---|---|---|
| **Parat** (Oct 12 update) | **27 of 28** | 0.45 s (max 11.5 s) | **27** (Oct 11: 8) |
| AMulet2 | 8 of 28 | 1.3 s on those 8 | 8 |

- AMulet2 ran out of time on 16 designs and stopped without an answer on 4 (all the fast adders: Kogge-Stone,
  Brent-Kung, Ladner-Fischer, carry-lookahead, carry-skip).
- On the 8 designs both prove, Parat is faster on all 8: counter-tree designs 3.3 s vs 110–135 s, the others
  0.2–0.4 s vs 0.4–1.5 s.
- **Not proved by Parat:** Wallace + carry-lookahead (time-out). AMulet2 does not prove it either.
- **Certificates (Oct 12 update):** every proved design now gets a certificate that pacheck2 checks, including the
  fast final adders (Kogge-Stone, Brent-Kung, Ladner-Fischer, carry-lookahead, carry-skip) and the counter-tree
  designs. Some are large: 2 MB to 1.3 GB (`results/genmul64_pac_oct12.txt`); pacheck2 needs up to a few minutes for
  the largest. On the Oct 11 build, designs with a fast final adder got no certificate.
- **Broken designs:** `*_buggy.aag.gz` (one gate input inverted): Parat answers INCORRECT with a counterexample
  (a, b, circuit output, a × b).
- **Soundness tests in the lab:** 540 random GenMul designs (3–10 bits, 28 architectures, most with one broken gate),
  referee = simulation on **all** 2^(2·width) inputs: 0 wrong answers, every counterexample re-simulated, every
  certificate CHECKED.
- Full table: `results/genmul64_race.txt` (Oct 11) and `results/genmul64_pac_oct12.txt` (certificates, Oct 12).

### 7. Scorecard: every category, one table (Oct 11)

One core per run, same machine, every SAT answer checked clause by clause; full numbers in
`results/scorecard_oct11.txt`. **Wrong answers in all categories: 0.**

| category | files | Parat solved | best other | Parat faster / slower than it (files) |
|---|---|---|---|---|
| random 3-SAT with answer, n=1000 hard | 16 × 3 seeds | **47/48** | YalSAT 46/48 | 10 / 6 |
| random 3-SAT, 10k–100k variables | 12 × 2 seeds | **24/24** | probSAT 18/24 | 12 / 0 |
| random 3-SAT "no answer" (n=300–400) | 6 | **6/6** | march_nh 6/6 | 4 / 2 |
| SATLIB classics (uf, aim, dubois, flat) | 102 | **102/102** | Kissat 101/102 | 89 / 7 |
| structured and industrial | 143 | **137/143** | Kissat 134/142 | 96 / 40 |
| circuits (multiplier/adder miters, factoring, sudoku) | 60 | **60/60** | Kissat 37/60 | 39 / 20 |
| multiplier verification (GenMul, 64-bit) | 28 | **27/28** | AMulet2 8/28 | section 6 |

Where Parat is slower: prime factoring and sudoku (Kissat, CaDiCaL), colouring files (about even), and on 40 of the
143 structured files Kissat is faster.

**Oct 12 re-run** (`results/scorecard_oct12.txt`, Parat only; the others from Oct 11): structured 140/143 solved
(was 137), PAR-2 2.66 (was 3.80), faster than Kissat on 107 files and slower on 29; circuits PAR-2 0.38 (was 0.46);
random "no answer" faster than march_nh on 5 of 6. Cost: colouring files without an answer are about 1.8x slower.

### 8. Oct 12 update: what changed

| area | before (Oct 11) | now (Oct 12) | file |
|---|---|---|---|
| GenMul 64-bit, unsigned: certificates | 8 of 28 | **27 of 28** (all proved designs) | `results/genmul64_pac_oct12.txt` |
| GenMul 64-bit, signed | not supported | **26 of 27 proved and certified** (AMulet2 `-signed`: 11) | `results/genmul64_signed_race.txt` |
| bugs that fire on ~1 input in 2^20 | "unknown" | **counterexample on 6 of 8**, 2–16 s | `results/rare_bugs_oct12.txt` |
| random "no answer", ratio 4.26, n=380 (7 files) | 131.8 s (march_nh 112.9 s) | **106–112 s** | `results/random426_unsat_vs_march_oct12.txt` |
| random with answer, n=1000, ratio 4.26 (20 × 3) | — | **60/60, mean 2.73 s** (probSAT 2.84, YalSAT 3.66) | `results/random1000_426_race_oct12.jsonl` |
| 5 big industrial files (50–139 MB, mostly reading time), best of 3 | 5.97 s (Kissat 5.06 s) | **4.70 s** | lab measurement |
| Windows | WSL only | **native `.exe`** (one core) | `bin/` |

- How the signed results were checked: 210 random signed designs (8-bit, most with one broken gate) against
  simulation on all 2^16 inputs: 0 wrong answers. The unsigned soundness tests were repeated on the final build
  (25 + 40 designs): 0 wrong answers, every certificate CHECKED.
- 170 general files: the Oct 12 build and the Oct 11 release give the same answer on every file they both finish,
  and every SAT answer was checked clause by clause.
- In the signed race AMulet2 printed no verdict on 3 designs and pacheck2 rejected the certificates it wrote there;
  this may be a problem in how it was run here. Part of that race ran while another job shared the machine, so its
  times may be inflated (for both tools); clean Parat times are listed at the end of the file.

### 9. Oct 18 update: very large random 3-SAT with an answer

Parat now has a second engine for random 3-SAT (every rule has 3 literals) with **10,000 or more variables**. On one
core it is the only engine; with several cores it runs on one core while the others run the usual engines, and the
first answer wins. It only looks for answers: a formula with no answer ends as "unknown". Every answer is checked
against every rule before it is printed, and again here by `verify/check_model.py`.

Release binary, one core (`taskset -c 0`), same machine; the files are made with `verify/gen_random3.c`
(`./gen_random3 N RATIO SEED > file.cnf` gives the same file again); the 100,000-variable files are in
`benchmarks/big_random/`:

| file | variables | ratio | Parat (this update) | original SP solver (sp-1.4, `-%1`) | Parat before this update | YalSAT / probSAT |
|---|---|---|---|---|---|---|
| b100k_422_1 (seed 1) | 100,000 | 4.22 | **19.4 s** | 114.1 s | 121.3 s | not solved in 300 s |
| b100k_425_1..4 (seeds 1–4) | 100,000 | 4.25 | **4 of 4**: 55, 167, 83, 679 s | 1 of 4 (112 s; with 0.1% steps also 1 of 4) | — | — |
| g1m_422_1 (seed 1) | 1,000,000 | 4.22 | **235.7 s** | 1742.4 s | — | — |
| g10m_422_1 (seed 1) | 10,000,000 | 4.22 | **3424.2 s** | not run | — | — |

- The original SP solver gives up (without an answer) on b100k_425_2..4 in 3–5 minutes; time limit 600 s (1200 s
  with 0.1% steps). Raw results: `results/big_random_oct18.txt`, `results/big_random_sp_races_oct17.jsonl`.
- Where the new engine starts (10,000 variables) was chosen by a race of the lab builds on 12 files (n = 10,000 to
  50,000, ratio 4.20 and 4.24, 120 s): the new engine solved 10, the old Parat 7; the old Parat was faster on the
  easy 10,000-variable files (`results/big_random_switch_race_oct17.jsonl`).
- Lab runs of the engine (before the release build): 1,000,000 variables at ratio 4.24 in 265 s and at 4.25 in
  946 s; 10,000,000 variables at 4.24 in 4635 s.
- Fairness note: some of the original SP solver's runs (Oct 17) and two of the 100,000-variable Parat runs shared the
  machine (2 cores) with other jobs part of the time, so those times may be somewhat inflated. The 1,000,000 and
  10,000,000-variable Parat runs had the machine to themselves.
- **Ratio 4.26** is not solved yet at these sizes (1,000,000 variables, seed 1: no answer after the first 44 minutes).

## Reproduce everything

```bash
# fresh random files nobody has seen (pick any seed)
python3 verify/gen_random.py 1000 4.2 30 123456 fresh/

# race Parat against your own builds of other solvers:
# one core per run, every answer checked, mean/median/PAR2 and a sign test at the end
python3 verify/race.py --limit 60 --seeds 5 \
  --solver "parat=bin/parat-linux-x86_64 {file} {seed}" \
  --solver "yalsat=/path/to/yalsat {file} {seed}" \
  --solver "probsat=/path/to/probSAT -a {file} {seed}" \
  --solver "kissat=/path/to/kissat -q {file}" \
  fresh/*.cnf
```

- `results/` holds the raw logs behind every table, one JSON line per run. `results/README.md` explains each file.
- `benchmarks/README.md` lists where every file comes from and the seeds that regenerate it.

## FAQ

**Is the source code available?**
Not publicly. The binary, the benchmarks and the checking tools are. Every claim can be checked without the source:
SAT answers by the clause checker, UNSAT answers by drat-trim.

**Was this written by AI?**
Yes, the code was written by AI (Claude). The ideas, the math behind them and the direction are mine (Himanshu),
see "Who built this" at the top. The results do not depend on that: every answer, proof and certificate is checked
by independent tools you can run yourself.

**Does this prove P = NP?**
No. Parat is fast in the measured region, but its running time on hard random formulas still grows exponentially
with n, like every known solver's.

**Why should I trust the UNSAT answers?**
You don't have to. Run with `--proof` and check the proof with drat-trim. In proof mode Parat only answers UNSAT when
it can write the proof.

**Can I use Parat at my company?**
Yes, with a commercial license. Free use covers personal use, research, teaching, publishing benchmark results, and
evaluation. See [Licensing](#licensing).

**Other platforms, a library version, or tuning for my formulas?**
Ask via an issue titled "Commercial license" (see below).

## Licensing

- **Free:** personal use, academic research and teaching, publishing benchmark results, and evaluation.
- **Paid commercial license:** use in a product or service, or in a company's production work, for example EDA,
  hardware or software verification, scheduling, planning or configuration tools.
- **To ask** for a license, a custom build (other platforms, an embeddable library, special formula families) or
  support, open a GitHub issue titled **"Commercial license"**.
- Full terms: [LICENSE](LICENSE).
- The scripts in `verify/` and the files in `benchmarks/` are free for any use.

## Limits

- Parat is fastest where the tables say so, and only there. Results come from one machine, and your timings will
  differ; the scripts let you measure them.
- **Proof mode:**
  - It uses one core.
  - It turns off the two methods that have no DRAT form yet: a counting argument for pigeonhole-type formulas and an
    algebraic argument for multiplier circuits. Files that only those methods can solve end as "unknown" in proof
    mode instead of an unchecked UNSAT.
- **Multiplier mode:**
  - It handles unsigned and signed (two's complement) multipliers given as AND-inverter graphs (`.aag`), with
    inputs a then b. Other encodings (for example sign-magnitude) are not supported.
  - It was tested on array, Wallace and Booth designs up to 128 bits, and on the 28 unsigned and 27 signed GenMul
    architectures at 64 bits (27 and 26 proved). Wallace + carry-lookahead is not proved, signed or unsigned.
  - Certificates are written only when every step has a certificate form. Otherwise Parat prints the reason and
    writes nothing. Some certificates are large (up to 1.3 GB at 64 bits).
  - For a broken design Parat looks for a counterexample. On large designs where every method runs out of time,
    the answer is "unknown" (no claim either way). Bugs that fire on very few inputs are found on most, not all,
    test designs (`results/rare_bugs_oct12.txt`).
- **Very large random files (new engine):** it only finds answers; with no answer it ends as "unknown". It is made for
  random 3-SAT; other formulas never use it. Ratio 4.26 at a million variables or more is not solved yet.
- **Multiplier netlists optimised by ABC** (yosys's default `synth`) are a hard case: a 16-bit one timed out
  (AMulet2 also timed out on 12 bits). See "Your own multiplier" above.
- **Proof files are big** (GBs at n=500). drat-trim needs about 1–2x the solve time to check them.
- **Platform:** Linux x86-64, and Windows x86-64 (one core; tested on one Windows PC: the 100,000-variable
  b100k_422_1 file in 21.3 s, Linux 19.4 s).

## Acknowledgements

- Parat builds on many published ideas from the SAT literature.
- The large random engine builds on survey propagation (Braunstein, Mézard, Zecchina, 2005) and backtracking survey
  propagation (Marino, Parisi, Ricci-Tersenghi, 2016). The original SP code (sp-1.4) was used for the comparison.
- The comparisons use Kissat and CaDiCaL (Armin Biere and others), march (Marijn Heule), YalSAT (Armin Biere) and
  probSAT (Adrian Balint).
- The proofs are checked with drat-trim (Marijn Heule, Nathan Wetzler, Warren Hunt).
- Multiplier certificates use the PAC format and are checked with pacheck2; the comparison uses AMulet2 (Daniela
  Kaufmann, Armin Biere and others, JKU Linz).
- Some benchmark files come from SATLIB (Holger Hoos, Thomas Stützle) and the SAT Competition archive.
