// Local validation only. Not part of the production patch.
use super::*;

fn baseline_scalar_inv_to_mont(a: Scalar<R>, cpu: cpu::Features) -> Scalar<R> {
    // Calculate the modular inverse of scalar |a| using Fermat's Little
    // Theorem:
    //
    //    a**-1 (mod n) == a**(n - 2) (mod n)
    //
    // The exponent (n - 2) is:
    //
    //    0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f

    #[inline]
    fn mul(a: &Scalar<R>, b: &Scalar<R>, _cpu: cpu::Features) -> Scalar<R> {
        binary_op(p256_scalar_mul_mont, a, b)
    }

    #[inline]
    fn sqr(a: &Scalar<R>, _cpu: cpu::Features) -> Scalar<R> {
        let mut tmp = Scalar::zero();
        unsafe { p256_scalar_sqr_rep_mont(tmp.limbs.as_mut_ptr(), a.limbs.as_ptr(), 1) }
        tmp
    }

    // Returns (`a` squared `squarings` times) * `b`.
    #[inline]
    fn sqr_mul(
        a: &Scalar<R>,
        squarings: LeakyWord,
        b: &Scalar<R>,
        cpu: cpu::Features,
    ) -> Scalar<R> {
        debug_assert!(squarings >= 1);
        let mut tmp = Scalar::zero();
        unsafe { p256_scalar_sqr_rep_mont(tmp.limbs.as_mut_ptr(), a.limbs.as_ptr(), squarings) }
        mul(&tmp, b, cpu)
    }

    // Sets `acc` = (`acc` squared `squarings` times) * `b`.
    #[inline]
    fn sqr_mul_acc(acc: &mut Scalar<R>, squarings: LeakyWord, b: &Scalar<R>, _cpu: cpu::Features) {
        debug_assert!(squarings >= 1);
        {
            let acc = acc.limbs.as_mut_ptr();
            unsafe { p256_scalar_sqr_rep_mont(acc, acc.cast_const(), squarings) }
        }
        binary_op_assign(p256_scalar_mul_mont, acc, b);
    }

    let _1 = &a;

    let _10 = sqr(_1, cpu); // 2
    let _100 = sqr(&_10, cpu); // 4
    let _101 = mul(&_100, _1, cpu); // 5
    let _111 = mul(&_101, &_10, cpu); // 7

    let _1000 = sqr(&_100, cpu); // 8
    let _10000 = sqr(&_1000, cpu); // 16
    let _100000 = sqr(&_10000, cpu); // 32

    let _100111 = mul(&_111, &_100000, cpu); // 39 = 7 + 32
    let _101011 = mul(&_100, &_100111, cpu); // 43 = 4 + 39
    let _101111 = mul(&_100, &_101011, cpu); // 47 = 4 + 39
    let _1001111 = mul(&_100000, &_101111, cpu); // 79 = 32 + 47
    let _86 = sqr(&_101011, cpu); // 86 = 43 * 2
    let _1011011 = mul(&_101, &_86, cpu); // 91 = 5 + 86
    let _92 = mul(_1, &_1011011, cpu); // 92 = 1 + 91
    let _1100011 = mul(&_111, &_92, cpu); // 99 = 7 + 92
    let _10111111 = mul(&_92, &_1100011, cpu); // 191 = 92 + 99
    let _11011111 = mul(&_100000, &_10111111, cpu); // 223 = 32 + 191

    let ff = mul(&_100000, &_11011111, cpu); // 255 = 32 + 223
    let ffff = sqr_mul(&ff, 0 + 8, &ff, cpu);
    let ffffffff = sqr_mul(&ffff, 0 + 16, &ffff, cpu);

    // ffffffff00000000ffffffff
    let mut acc = sqr_mul(&ffffffff, 32 + 32, &ffffffff, cpu);

    // ffffffff00000000ffffffffffffffff
    sqr_mul_acc(&mut acc, 0 + 32, &ffffffff, cpu);

    // The rest of the exponent, in binary, is:
    //
    //    1011110011100110111110101010110110100111000101111001111010000100
    //    1111001110111001110010101100001011111100011000110010010101001111

    sqr_mul_acc(&mut acc, 6, &_101111, cpu);
    sqr_mul_acc(&mut acc, 2 + 3, &_111, cpu);
    sqr_mul_acc(&mut acc, 2 + 8, &_11011111, cpu);
    sqr_mul_acc(&mut acc, 1 + 3, &_101, cpu);
    sqr_mul_acc(&mut acc, 1 + 7, &_1011011, cpu);
    sqr_mul_acc(&mut acc, 1 + 6, &_100111, cpu);
    sqr_mul_acc(&mut acc, 3 + 6, &_101111, cpu);
    sqr_mul_acc(&mut acc, 2 + 3, &_111, cpu);
    sqr_mul_acc(&mut acc, 3, &_101, cpu);
    sqr_mul_acc(&mut acc, 4 + 7, &_1001111, cpu);
    sqr_mul_acc(&mut acc, 2 + 3, &_111, cpu);
    sqr_mul_acc(&mut acc, 1 + 3, &_111, cpu);
    sqr_mul_acc(&mut acc, 2 + 3, &_111, cpu);
    sqr_mul_acc(&mut acc, 2 + 6, &_101011, cpu);
    sqr_mul_acc(&mut acc, 4 + 8, &_10111111, cpu);
    sqr_mul_acc(&mut acc, 3 + 7, &_1100011, cpu);
    sqr_mul_acc(&mut acc, 2 + 1, _1, cpu);
    sqr_mul_acc(&mut acc, 2 + 3, &_101, cpu);
    sqr_mul_acc(&mut acc, 1 + 7, &_1001111, cpu);

    acc
}

fn scalar(hex: &str) -> Scalar<Unencoded> {
    Scalar::from(&PublicScalar::<Unencoded>::from_hex(hex))
}

fn montgomery(hex: &str) -> Scalar<R> {
    Scalar::from(&PublicScalar::<R>::from_hex(hex))
}

#[test]
fn p256_chain284_independent_oracle() {
    let cpu = cpu::features();
    let mut count = 0;
    for line in include_str!("p256_chain284_vectors.txt").lines() {
        let mut fields = line.split_whitespace();
        let plain = scalar(fields.next().unwrap());
        let input = montgomery(fields.next().unwrap());
        let expected = montgomery(fields.next().unwrap());
        assert!(fields.next().is_none());
        let candidate = p256_scalar_inv_to_mont(input, cpu);
        let baseline = baseline_scalar_inv_to_mont(input, cpu);
        assert_eq!(candidate.limbs, expected.limbs, "candidate vector {count}");
        assert_eq!(baseline.limbs, expected.limbs, "baseline vector {count}");
        let product = SCALAR_OPS.scalar_product(&plain, &candidate, cpu);
        let product_expected = if count == 0 { Scalar::zero() } else { Scalar::one() };
        assert_eq!(product.limbs, product_expected.limbs, "inverse product {count}");
        count += 1;
    }
    assert_eq!(count, 1792);
}
// Appended to the local validation module for ROUND3. No production exports.
extern crate std;

#[test]
#[ignore = "run deliberately in release with --test-threads=1"]
fn p256_chain284_paired_microbenchmark() {
    use std::{hint::black_box, time::Instant, vec::Vec};
    let cpu = cpu::features();
    let inputs: Vec<Scalar<R>> = include_str!("p256_chain284_vectors.txt")
        .lines().rev().take(64)
        .map(|line| montgomery(line.split_whitespace().nth(1).unwrap()))
        .collect();
    type Inverse = fn(Scalar<R>, cpu::Features) -> Scalar<R>;
    let baseline: Inverse = baseline_scalar_inv_to_mont;
    let candidate: Inverse = p256_scalar_inv_to_mont;
    let iterations = 16384;
    let measure = |f: Inverse| {
        let f = black_box(f);
        let start = Instant::now();
        for i in 0..iterations {
            let _ = black_box(f(black_box(inputs[i % inputs.len()]), cpu));
        }
        start.elapsed().as_nanos()
    };
    for _ in 0..4 {
        let _ = black_box(measure(baseline));
        let _ = black_box(measure(candidate));
    }
    std::println!("kind,round,order,iterations,baseline_ns,candidate_ns");
    for round in 0..41 {
        let (b, c, order) = if round % 2 == 0 {
            let b = measure(baseline);
            let c = measure(candidate);
            (b, c, "BC")
        } else {
            let c = measure(candidate);
            let b = measure(baseline);
            (b, c, "CB")
        };
        std::println!("scalar_inverse,{round},{order},{iterations},{b},{c}");
    }
}
