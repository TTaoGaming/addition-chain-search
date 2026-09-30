    // Generated from certificate SHA-256 46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148.
    // Exact scalar exponent n-2: 284 = 251 squarings + 33 multiplications.
    // Public, fixed schedule; existing ring Montgomery helpers unchanged.
    let c2 = sqr_mul(&a, 1, &a, cpu); // certificate row 2
    let c3 = sqr(&c2, cpu); // certificate row 3
    let c4 = sqr(&c3, cpu); // certificate row 4
    let c5 = mul(&c2, &c4, cpu); // certificate row 5
    let c6 = mul(&c4, &c5, cpu); // certificate row 6
    let c7 = mul(&c5, &c6, cpu); // certificate row 7
    let c8 = mul(&c5, &c7, cpu); // certificate row 8
    let c9 = mul(&c7, &c8, cpu); // certificate row 9
    let c10 = mul(&c8, &c9, cpu); // certificate row 10
    let c11 = mul(&c9, &c10, cpu); // certificate row 11
    let c12 = sqr(&c11, cpu); // certificate row 12
    let c13 = sqr(&c12, cpu); // certificate row 13
    let c14 = sqr(&c13, cpu); // certificate row 14
    let c15 = sqr(&c14, cpu); // certificate row 15
    let c16 = sqr(&c15, cpu); // certificate row 16
    let c20 = sqr_mul(&c16, 3, &c11, cpu); // certificate row 20
    let c37 = sqr_mul(&c20, 16, &c20, cpu); // certificate row 37
    let c102 = sqr_mul(&c37, 64, &c37, cpu); // certificate row 102
    let c135 = sqr_mul(&c102, 32, &c37, cpu); // certificate row 135
    let c136 = mul(&c11, &c16, cpu); // certificate row 136
    let mut acc = sqr_mul(&c135, 8, &c10, cpu); // certificate row 145
    sqr_mul_acc(&mut acc, 3, &c11, cpu); // certificate row 149
    sqr_mul_acc(&mut acc, 10, &c136, cpu); // certificate row 160
    sqr_mul_acc(&mut acc, 7, &c7, cpu); // certificate row 168
    sqr_mul_acc(&mut acc, 5, &c6, cpu); // certificate row 174
    sqr_mul_acc(&mut acc, 9, &c10, cpu); // certificate row 184
    sqr_mul_acc(&mut acc, 9, &c10, cpu); // certificate row 194
    sqr_mul_acc(&mut acc, 8, &c136, cpu); // certificate row 203
    sqr_mul_acc(&mut acc, 1, &c7, cpu); // certificate row 205
    sqr_mul_acc(&mut acc, 9, &c10, cpu); // certificate row 215
    sqr_mul_acc(&mut acc, 4, &c6, cpu); // certificate row 220
    sqr_mul_acc(&mut acc, 3, &c9, cpu); // certificate row 224
    sqr_mul_acc(&mut acc, 8, &c10, cpu); // certificate row 233
    sqr_mul_acc(&mut acc, 8, &c10, cpu); // certificate row 242
    sqr_mul_acc(&mut acc, 4, &c11, cpu); // certificate row 247
    sqr_mul_acc(&mut acc, 6, &c11, cpu); // certificate row 254
    sqr_mul_acc(&mut acc, 10, &c9, cpu); // certificate row 265
    sqr_mul_acc(&mut acc, 3, &a, cpu); // certificate row 269
    sqr_mul_acc(&mut acc, 8, &c7, cpu); // certificate row 278
    sqr_mul_acc(&mut acc, 5, &c5, cpu); // certificate row 284

    acc
