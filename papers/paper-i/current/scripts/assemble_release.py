#!/usr/bin/env python3
"""Assemble the two-file delivery and check the complete release manifest."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('historical_archive', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = args.historical_archive.resolve()
    expected = '16d3c743b06fa8ceadc3d2499a52c96247a55bc03ea5ec2844d6f0d363d318cc'
    if not source.is_file() or source.stat().st_size != 58279775 or digest(source) != expected:
        parser.error('Historical ZIP is missing or differs from the accepted predecessor')
    target = root / 'source/predecessor/Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12.zip'
    if target.exists():
        if not target.is_file() or digest(target) != expected:
            parser.error('Destination already exists with different content; no file was overwritten')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(target) != expected:
            raise ValueError('Copied historical ZIP hash mismatch')
    subprocess.run([sys.executable, str(root / 'scripts/verify_integrity.py')], check=True)
    print('PASS: both delivery parts form the complete release')


if __name__ == '__main__':
    main()
