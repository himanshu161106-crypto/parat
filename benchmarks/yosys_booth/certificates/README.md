# Certificates for the yosys 0.69 multipliers without `&fraig`

Each archive holds the complete certificate that `parat circuit.aag 1 7000 --pac booth<W>_nofraig` (v1.3) wrote:
the PAC proof (`.polys`, `.proof`, `.spec`) for the rebuilt circuit `.new.aag`, and one DRAT proof per range of
32 outputs (`.eq<k>.cnf`, `.eq<k>.drat`) that your circuit and `.new.aag` give the same outputs.

| file | design | size | check time (verify_multiplier.sh) |
|---|---|---|---|
| `booth64_nofraig_certificate.tar.xz` | `../booth64_nofraig.aag.gz` | 24 MB (152 MB unpacked) | 19 s |
| `booth128_nofraig_certificate.tar.xz` | `../booth128_nofraig.aag.gz` | 51 MB (209 MB unpacked) | 23 s |
| `booth256_nofraig_certificate.tar.xz` | `../booth256_nofraig.aag.gz` | 197 MB (1.2 GB unpacked), **on the v1.3 release page** (too big for git) | 170 s, 0.8 GB memory |

Checksums of all three: `SHA256SUMS`.

Check one yourself (pacheck2 and drat-trim: see `verify/verify_multiplier.sh` for where to get them):

```bash
cd benchmarks/yosys_booth/certificates
tar xJf booth64_nofraig_certificate.tar.xz
gunzip -k ../booth64_nofraig.aag.gz
../../../verify/verify_multiplier.sh ../booth64_nofraig.aag path/to/pacheck path/to/drat-trim --cert booth64_nofraig
# -> CERTIFIED: the circuit computes a*b (every check passed)
```

The check rebuilds every SAT file from your copy of the circuit (`verify/eq_cnf.py`), so nothing from Parat is taken
on trust except the proofs themselves, and those are checked by tools we did not write.
