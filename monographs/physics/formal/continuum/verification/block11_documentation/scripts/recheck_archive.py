#!/usr/bin/env python3
"""Freshly extract, checksum and fully reverify a checked source ZIP.

A successful ZIP/manifest test alone is not theorem verification: this also
runs the extracted Lean verifier and compares the completed proof audit.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
import zipfile


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def safe_path(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError(f'Unsafe archive path: {name}')
    return p


def checksums(root: Path) -> dict:
    manifest = json.loads((root / 'PACKAGE_MANIFEST.json').read_text())
    errors: list[str] = []
    for item in manifest['files']:
        path = root.joinpath(*safe_path(item['path']).parts)
        if not path.is_file() or sha256(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            errors.append(item['path'])
    lines = (root / 'SHA256SUMS.txt').read_text().splitlines()
    for line in lines:
        digest, name = line.split('  ', 1)
        path = root.joinpath(*safe_path(name).parts)
        if not path.is_file() or sha256(path) != digest:
            errors.append(name)
    if errors:
        raise ValueError(f'Checksum failures: {sorted(set(errors))}')
    return {'status': 'PASS', 'manifest_payload_files': len(manifest['files']),
            'checksum_records': len(lines), 'mismatches': 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True,
                        help='New extraction parent; must not already exist')
    parser.add_argument('--out', type=Path, required=True, help='External evidence directory')
    args = parser.parse_args()
    archive, kit = args.archive.resolve(), args.kit.resolve()
    destination, out = args.destination.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'schema_version': 1, 'status': 'INCOMPLETE',
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'archive': str(archive), 'destination': str(destination)}
    result_path = out / 'archive_check.json'
    start = time.monotonic()

    def save() -> None:
        result_path.write_text(json.dumps(report, indent=2) + '\n')

    save()
    try:
        if destination.exists():
            raise ValueError('Extraction destination already exists; refusing a stale recheck')
        if out == destination or destination in out.parents:
            raise ValueError('Evidence directory must be outside the extraction destination')
        report['archive_sha256_before'] = sha256(archive)
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP CRC failure')
            roots = set()
            for item in z.infolist():
                parts = safe_path(item.filename).parts
                if not parts:
                    continue
                roots.add(parts[0])
                if stat.S_ISLNK(item.external_attr >> 16):
                    raise ValueError('Symlink in source archive')
            if len(roots) != 1:
                raise ValueError('Expected exactly one package root')
            destination.mkdir(parents=True)
            z.extractall(destination)
            report['zip_crc'] = 'PASS'
            report['zip_members'] = len(z.infolist())
        root = destination / next(iter(roots))
        report['package_root'] = str(root)
        report['checksums_before'] = checksums(root)
        original = json.loads((root / 'verification/final/report.json').read_text())
        if original['status'] != 'PASS':
            raise ValueError('Packaged verification report is not PASS')
        command = [sys.executable, str(root / 'scripts/verify.py'), '--kit', str(kit),
                   '--out', str(out / 'fresh_verification'), '--timeout', '240']
        report['verifier_argv'] = command
        save()
        with (out / 'verifier_console.log').open('w') as stream:
            proc = subprocess.run(command, cwd=root, stdout=stream,
                                  stderr=subprocess.STDOUT, timeout=1800)
        report['verifier_returncode'] = proc.returncode
        fresh = json.loads((out / 'fresh_verification/report.json').read_text())
        if proc.returncode != 0 or fresh['status'] != 'PASS':
            raise ValueError('Extracted full verification did not pass')
        for key in ['source_sha256', 'counts', 'negative_controls', 'negative_control_details', 'allowed_axioms', 'dependencies']:
            if fresh[key] != original[key]:
                raise ValueError(f'Fresh audit differs from packaged audit: {key}')
        if fresh['axiom_audit']['dependencies'] != original['axiom_audit']['dependencies']:
            raise ValueError('Axiom dependencies differ between full runs')
        report['checksums_after'] = checksums(root)
        report['archive_sha256_after'] = sha256(archive)
        if report['archive_sha256_before'] != report['archive_sha256_after']:
            raise ValueError('Archive changed during recheck')
        report.update(status='PASS', counts=fresh['counts'], negative_controls=fresh['negative_controls'],
                      block02_source_preservation=fresh['block02_source_preservation'],
                      block03_source_preservation=fresh['block03_source_preservation'],
                      block04_source_preservation=fresh['block04_source_preservation'],
                      block05_source_preservation=fresh['block05_source_preservation'],
                      block06_source_preservation=fresh["block06_source_preservation"],
                      block07_source_preservation=fresh["block07_source_preservation"],
                      block08_source_preservation=fresh["block08_source_preservation"],
                      block09_source_preservation=fresh["block09_source_preservation"],
                      block10_source_preservation=fresh["block10_source_preservation"],
                      verified_source_inputs=len(fresh['source_sha256']),
                      proof_input_hashes_identical=True, axiom_dependencies_identical=True,
                      fresh_report=str(out / 'fresh_verification/report.json'),
                      fresh_report_sha256=sha256(out / 'fresh_verification/report.json'),
                      runtime_rebuilt_wholesale=False)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        report.update(status='FAIL', error=str(error))
    finally:
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        report['seconds'] = round(time.monotonic() - start, 4)
        save()
    print(json.dumps(report, indent=2), flush=True)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
