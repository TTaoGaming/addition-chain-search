# Source and rights notice for review candidates

- The two P-521 certificates were derived from earlier local 582 schedules by
  removing exponent 30 (`15 + 15`) and rebuilding exponent 60 as `29 + 31`.
  Their filenames describe the independently replayed 581 operation counts.
- The secp256k1 certificate was reconstructed from a self-contained research
  witness and matched its recorded SHA-256. The research scaffold follows
  [Brian Smith's public 2017 article](https://briansmith.org/ecc-inversion-addition-chains-01),
  which credits earlier secp256k1 scalar work. No article or library implementation source text is bundled with those earlier certificates. The new `p256-284/` directory includes pinned ring source under its retained upstream notices; see its `SOURCE_NOTICE.md`.
- The checker is newly written Python standard-library code. The linked NIST
  and SECG specifications define the curve parameters; their text is not
  bundled. No `addchain` binary or generated script is bundled. Third-party ring source appears only in the separately documented `p256-284/` addition.

These materials are supplied for technical review only. **No new project reuse license is granted for `review-candidates/`**. Copied ring source in `p256-284/` retains its existing upstream permissions. The `chains/LICENSE` and the skills' MIT
terms do not cover this directory. Publication is not an endorsement by Brian
Smith, NIST, SECG, or any other recipient or source.
