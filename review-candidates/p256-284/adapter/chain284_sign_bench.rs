//! Local end-to-end ECDSA signing benchmark; not a public API change.
use ring::{rand::SystemRandom, signature::{EcdsaKeyPair, ECDSA_P256_SHA256_ASN1_SIGNING}};
use std::{hint::black_box, time::Instant};

fn main() {
    let iterations: usize = std::env::args().nth(1).unwrap_or_else(|| "2000".into()).parse().unwrap();
    let rng = SystemRandom::new();
    let key = EcdsaKeyPair::from_pkcs8(
        &ECDSA_P256_SHA256_ASN1_SIGNING,
        include_bytes!("../tests/ecdsa_test_private_key_p256.p8"), &rng,
    ).unwrap();
    let message = [0x42u8; 32];
    for _ in 0..1000 {
        black_box(key.sign(&rng, black_box(&message)).unwrap());
    }
    let start = Instant::now();
    for _ in 0..iterations {
        black_box(key.sign(&rng, black_box(&message)).unwrap());
    }
    println!("{}", start.elapsed().as_nanos());
}
