# Parat v1.5 — final checks (Nov 28 2026)

All runs use the released programs (one file per system, `parat-v1.5-*`), checksums as on the Releases page.

## Multipliers (Wallace designs from `gen_mult`, one CPU core)

| operands | AND gates | answer | time | machine |
|---|---:|---|---:|---|
| 64 × 64 bits | 41 k | CORRECT | < 1 s | Linux, Windows (Wine) |
| 256 × 256 bits | 0.66 M | CORRECT | 3.4 s | Linux |
| 256 × 256 bits, one gate wrong | 0.66 M | INCORRECT + counterexample | < 1 s | Linux, Windows (Wine) |
| 512 × 512 bits | 2.6 M | CORRECT | 8.9 s | Linux |
| 512 × 512 bits, one gate wrong | 2.6 M | INCORRECT + counterexample | 0.1 s | Linux |
| 2048 × 2048 bits | 42 M | CORRECT | 3 min 36 s | Linux, 8 GB RAM, rest on disk |
| 2048 × 2048 bits | 42 M | CORRECT | 3 min 35 s | Windows program (Wine), 8 GB RAM, rest on disk |

The same 2048-bit file was proved on the user's 16 GB Windows laptop earlier in November with an older build
(about 7 and 12 minutes).

## PAC certificates, checked piece by piece by pacheck (`tools/pac_verify.py`)

| certificate | write time | size | pieces | check time | largest pacheck | result |
|---|---:|---:|---:|---:|---:|---|
| 512 × 512 bits | 71 s | 1.1 GB | 7 | 97 s | 1.6 GB | CERTIFICATE CHECKED |
| 1024 × 1024 bits | 16.5 min | 7.7 GB | 20 | 8.7 min | 3.4 GB | CERTIFICATE CHECKED |
| 1024 × 1024 bits (600 MB checkpoints off, 100 MB on) | 13.9 min | 13.2 GB | 49 | 12.7 min | 1.6 GB | CERTIFICATE CHECKED |
| 512 × 512 bits, written and checked at the same time (`--follow --jobs 3`) | — | — | 35 | 2 min 43 s in all | 0.4 GB | CERTIFICATE CHECKED |

Also checked: Wallace, Booth and array multipliers (8–64 bits), and certificates written by the Windows program and
checked by the Windows build of pacheck.

Deliberate errors, all rejected by `pac_verify.py`: a changed proof step, the last step removed, the last result
changed, the spec changed, a gate of the circuit changed, a polys line changed, a step using a line that does not
exist, another rule (`=`), the same line id twice, a line without result, Parat stopped half way (`--follow`).
The proof reader was also run with read blocks of 3, 7, 50 and 997 bytes (all CERTIFICATE CHECKED).

Writing a certificate got faster and smaller in v1.5: 512 bits 13.7 min → 71 s, memory 5.4 GB → 1.9 GB, proof without
checkpoints 2.2 GB → 0.8 GB.

## SAT Competition 2026 files, final program, user's laptop (Linux part, 2 cores, 3 GB)

| file | family | answer | time |
|---|---|---|---:|
| 1eea3d91 | minimal-disagreement-parity | SAT | 0.09 s |
| 61fee64c | minimal-disagreement-parity | SAT | 0.06 s |
| 16ca57f2 | minimum-disagreement-parity | UNSAT | 4.5 s |
| 23daec2c | minimum-disagreement-parity | UNSAT | 1.6 s |
| 425c81fc | minimum-disagreement-parity | UNSAT | 2.2 s |
| 27495ba0 | datapath-equivalence-checking | UNSAT | 1.6 s |
| de8c42d5 | multiplier-equivalence-checking | UNSAT | 115 s |

No competition solver solved any of these within 300 s; 16ca57f2, 23daec2c and 425c81fc were not solved by any
solver. Earlier v1.5 runs of the other datapath files: [`../sc26_nov24/`](../sc26_nov24/).

## CNF and proofs

| test | Linux | Windows (Wine) |
|---|---|---|
| random 3-SAT, 250 vars, 1000 clauses | SAT, model checked | SAT |
| random 3-SAT, 200 vars, 850 clauses | UNSAT, DRAT `s VERIFIED` (drat-trim) | — |
| pigeonhole 9 into 8 | UNSAT, DRAT `s VERIFIED` (drat-trim, Linux and Windows builds) | UNSAT |

Linux ARM64 program (qemu): 64-bit and 256-bit multipliers CORRECT, SAT and UNSAT CNF answers correct.
macOS and Windows-ARM programs: built, not yet run on real hardware.
