#!/usr/bin/env python3
"""Offline certificate, generator, and published-file integrity checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
EXPECTED = '46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148'


def run(*args):
    subprocess.run([sys.executable, '-B', *map(str, args)], cwd=ROOT, check=True)


def main():
    manifest = json.loads((ROOT / 'SHA256SUMS.json').read_text())
    for name, expected in manifest.items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'published file hash mismatch: {name}')
    run('adapter/check_chain_independent.py', 'adapter/candidate.json', '--sha256', EXPECTED, '--modular')
    for path in sorted((ROOT / 'history/alternative_certificates').glob('*.json')):
        run('adapter/check_chain_independent.py', path, '--modular')
    run('adapter/test_adapter.py')
    with tempfile.TemporaryDirectory(prefix='p256-review-') as tmp:
        run('adapter/generate_ring.py', '--out', tmp)
        for generated in Path(tmp).iterdir():
            if generated.read_bytes() != (ROOT / 'adapter' / generated.name).read_bytes():
                raise ValueError(f'generator output mismatch: {generated.name}')
    print(f'{len(manifest)} published file hashes matched')
    print('PASS_P256_REVIEW')


if __name__ == '__main__':
    main()
