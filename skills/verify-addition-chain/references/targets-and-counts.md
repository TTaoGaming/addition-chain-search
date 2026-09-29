# Target and operation terms

- A scalar inversion chain exponentiates modulo the prime subgroup order:
  usually `n−2`, or `l−2` when `l` names the order. It is not the field-prime
  inverse.
- A field inversion chain exponentiates modulo the field prime: `p−2`.
  A result for Curve25519 scalar `l−2` cannot be compared with a Curve25519
  field `p−2` result.
- In an exponent DAG, `x_i=x_j+x_k` represents multiplication of powers.
  `j=k` is a squaring `S`; distinct parents are another multiplication `M`.
  Report both counts and the exact cost model rather than collapsing to a
  single vague "faster" number.
- An arithmetic replay can show a certificate reaches its target. It cannot
  show that the search exhausted all possible chains or that a native
  implementation runs faster.
