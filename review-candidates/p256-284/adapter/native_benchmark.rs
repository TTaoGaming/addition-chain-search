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
