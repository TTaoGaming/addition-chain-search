# New scalar-chain candidates for technical review

This section is a **separate, review-only addition** to the 2026-09-29 public
packet. It is outside the frozen `chains/` results ZIP and its MIT license.
The exact candidate bytes and a Python standard-library checker are included.

From the project root, run:

```sh
python -B review-candidates/verify.py
```

The expected last line is `PASS_LOCAL_ARITHMETIC_ONLY`. The checker pins each
certificate's SHA-256, checks the exact subgroup scalar target, replays every
earlier-parent addition, counts live squarings and other multiplications,
checks five modular bases, and rejects wrong-target and bad-parent mutations.
It does not execute code from a certificate.

| Exact scalar target | Candidate | Narrow comparison |
| --- | ---: | --- |
| NIST P-521 subgroup `n−2` | [581 = 517S + 64M](certificates/p521_581_517S64M.json) | One operation below our previously published, locally replayed 582. |
| Same P-521 target | [581 = 516S + 65M](certificates/p521_581_516S65M.json) | Same total with one fewer squaring and one more other multiplication. |
| secp256k1 subgroup `n−2` | [288 = 253S + 35M](certificates/secp256k1_288.json) | Two other multiplications below [Brian Smith's dated 2017 290 = 253S + 37M scalar count](https://briansmith.org/ecc-inversion-addition-chains-01). |

`S` is a squaring and `M` is another multiplication. The two P-521 schedules
are alternative cost points, not independent discoveries. P-521's comparison
is with **our earlier 582**, not with a vetted current public best. The curve
orders come from [NIST SP 800-186](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf)
and [SEC 2 v2](https://www.secg.org/sec2-v2.pdf), respectively.

**Evidence ceiling:** This proves local arithmetic and operation counts. It
does not establish shortest-chain optimality, a current world best, native
speed, constant-time behavior, library integration, or outside acceptance.
The complete search trajectories have not been independently reconstructed
here. See the [source and rights notice](SOURCE_NOTICE.md). No license is
granted for these new review materials.
