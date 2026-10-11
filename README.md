# Parat

**A SAT solver for hard random 3-SAT, whose "no answer" results come with a proof that anyone can check.**

Parat reads a formula in DIMACS CNF and answers one of three things:
- **SATISFIABLE**, with an assignment that you can check in one second;
- **UNSATISFIABLE**, optionally with a DRAT proof that an independent checker verifies;
- **unknown**, if time runs out.

It is built for the hardest region of random 3-SAT, near the threshold (clause/variable ratio 4.2–4.26). It also
solves structured and industrial files correctly.

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
- **Fastest at proving "no answer" on random 3-SAT among the solvers tested:**
  - w400_2: Parat 26.8 s, march_nh 28.9 s, Kissat > 3000 s.
  - n=500: 142 s vs 169 s for march_nh.
- **Files that have an answer:**
  - Clearly ahead of probSAT: faster on 13 of 16 hard files, p = 0.01.
  - Level with YalSAT, with a small lead that is not statistically proven.
  - Every one of thousands of answers was checked clause by clause.
- **New in v1.1: multiplier circuits, proved correct with a certificate.**
  - `parat mult.aag 1 300 --pac cert` proves that a gate-level multiplier really computes a × b, or prints an input
    where it does not.
  - The certificate is checked by pacheck2 (JKU), the checker used for AMulet2's certificates.
  - 128-bit Booth: Parat 1.9 s with certificate, AMulet2 43.7 s. 128-bit array: 1.5 s vs 152 s.
- **Nothing to trust blindly.** The repo has everything needed to redo each table on your own machine:
  - an answer checker,
  - a seeded file generator,
  - a race script with a sign test,
  - all raw logs.

## Quick start

Linux x86-64; the binary is static and needs nothing else. On Windows use WSL; there is no macOS build yet.

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

**Command line:**
- Usage: `parat file.cnf [seed] [time_limit_s] [--proof proof.drat] [--proof-binary]`.
- Output follows the SAT Competition format: `s ...` and `v ...` lines. The exit code is 10 = SAT, 20 = UNSAT,
  0 = unknown.
- The default time limit is 300 s. The seed can also be set with `PARAT_SEED`.
- `--proof FILE` writes a DRAT proof when the answer is UNSAT. `--proof-binary` makes the file about 2x smaller.
  - Proof files are large: about 450 MB for n=400 and 2.2 GB for n=500 (binary).
- Proof mode uses one core and only methods whose steps can be written as DRAT. See [Limits](#limits).

**Multiplier mode (v1.1):** `parat circuit.aag 1 [time_limit_s] [--pac prefix]`
- Input: an ASCII AIGER file (`.aag`, as used by AMulet2; convert a binary `.aig` with `aigtoaig`). The first half of
  the inputs is a (least significant bit first), the second half b, the outputs are the product bits.
- Output: `s CORRECT MULTIPLIER` or `s INCORRECT MULTIPLIER` with a counterexample (a, b, circuit output, a × b).
  Exit code 0 / 1.
- `--pac prefix` writes `prefix.polys`, `prefix.proof`, `prefix.spec` (Practical Algebraic Calculus) when the answer is
  CORRECT. Check with `pacheck prefix.polys prefix.proof prefix.spec`.

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

- The Parat and march numbers in this table come from the same earlier day. On the day the proofs were made the
  machine was slower: w400_2 took 33–35 s, for both the current and the previous Parat build. Compare times only
  within one table.
- On the author's scaling sets (n = 250–500, not in this repo), time grows like:
  - Parat: 2^(n/21.3)
  - march: 2^(n/22.3)
  - CaDiCaL: 2^(n/14.5)
- Parat is ahead, but the growth is still exponential, as for every known solver.

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
  - Weak spot: factoring circuits, where Kissat is about 2.5x faster (33-bit: 21.9 s vs 8.9 s).

### 5. Multiplier circuits (new in v1.1)

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
| array 64-bit | **0.27 s** | 5.4 MB | 6.2 s | 14 MB | CHECKED |
| Booth 64-bit | **0.40 s** | 8.6 MB | 2.7 s | 17 MB | CHECKED |
| Wallace 64-bit | 0.61 s | 5.6 MB | **0.53 s** | 7.1 MB | CHECKED |
| array 128-bit | **1.45 s** | 28 MB | 152 s | 82 MB | CHECKED |
| Booth 128-bit | **1.87 s** | 46 MB | 43.7 s | 104 MB | CHECKED |
| Wallace 128-bit | 3.43 s | 29 MB | **3.3 s** | 43 MB | CHECKED |

- **Array and Booth:** Parat is 7–100x faster, with certificates 2–3x smaller.
- **Wallace:** about equal; AMulet2 is slightly faster.
- **Broken circuits** (one gate changed): Parat answers INCORRECT, prints a counterexample, and writes no certificate.
  `benchmarks/multipliers/*_buggy.aag` are two such files.
- **Tamper test:** changing one gate in `prefix.polys`, halving the modulus, or changing the target makes pacheck2
  reject the certificate.
- **Lab fuzz:** 200 random multipliers of 2–24 bits. All 164 certificates were CHECKED, and none of the 36 broken
  designs got a certificate.
- Raw numbers: `results/multiplier_pac.txt`. Files: `benchmarks/multipliers/` (128-bit ones are gzipped).

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
  - It handles unsigned multipliers given as AND-inverter graphs (`.aag`), with inputs a then b.
  - It was tested on array, Wallace and Booth designs up to 128 bits. Other architectures (for example Kogge-Stone
    final adders) have not been measured yet.
  - When a circuit is proved CORRECT without the algebraic method (by search), no certificate is written.
- **Proof files are big** (GBs at n=500). drat-trim needs about 1–2x the solve time to check them.
- **Platform:** a Linux x86-64 binary only.

## Acknowledgements

- Parat builds on many published ideas from the SAT literature.
- The comparisons use Kissat and CaDiCaL (Armin Biere and others), march (Marijn Heule), YalSAT (Armin Biere) and
  probSAT (Adrian Balint).
- The proofs are checked with drat-trim (Marijn Heule, Nathan Wetzler, Warren Hunt).
- Multiplier certificates use the PAC format and are checked with pacheck2; the comparison uses AMulet2 (Daniela
  Kaufmann, Armin Biere and others, JKU Linz).
- Some benchmark files come from SATLIB (Holger Hoos, Thomas Stützle) and the SAT Competition archive.
