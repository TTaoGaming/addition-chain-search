# Source and rights notice for review candidates

- The two P-521 certificates were derived from earlier local 582 schedules by
  removing exponent 30 (`15 + 15`) and rebuilding exponent 60 as `29 + 31`.
  Their filenames describe the independently replayed 581 operation counts.
- The secp256k1 certificate was reconstructed from a self-contained research
  witness and matched its recorded SHA-256. The research scaffold follows
  [Brian Smith's public 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01),
  which credits earlier secp256k1 scalar work. No article or library
  implementation source text is bundled here.
- The checker is newly written Python standard-library code. The linked NIST
  and SECG specifications define the curve parameters; their text is not
  bundled. No `addchain` binary, generated script, or third-party code is
  bundled in this section.

These materials are supplied for technical review only. **No reuse license is
granted for `review-candidates/`**. The `chains/LICENSE` and the skills' MIT
terms do not cover this directory. Publication is not an endorsement by Brian
Smith, NIST, SECG, or any other recipient or source.
