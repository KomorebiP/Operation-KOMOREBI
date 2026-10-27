#!/usr/bin/env python3
"""Validate the immutable Lean release against its frozen delivery manifest.
This is a byte-integrity check, not a new Lean compilation or proof review.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path, PurePosixPath

CI_ROOT=Path(__file__).resolve().parent
GENERATED={'.git','.lake','.build','.verification-run','__pycache__'}
def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def checked_path(root: Path,name: str) -> Path:
    rel=PurePosixPath(name)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or chr(92) in name:
        raise ValueError(f'Invalid manifest path: {name}')
    path=root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Manifest path leaves the project: {name}')
    return path

def verify_manifest(project: Path, expected_manifest_sha256: str, inventory: bool=True) -> dict:
    project=project.resolve();manifest_path=project/'MANIFEST.json'
    if digest(manifest_path)!=expected_manifest_sha256:
        raise ValueError('The Lean delivery manifest differs from the frozen release baseline.')
    manifest=json.loads(manifest_path.read_text());files=manifest['files']
    for name,record in files.items():
        path=checked_path(project,name)
        if not path.is_file():raise ValueError(f'Missing manifest file: {name}')
        if path.stat().st_size!=record['bytes'] or digest(path)!=record['sha256']:
            raise ValueError(f'Changed frozen Lean payload: {name}')
    if inventory:
        actual=set()
        for path in project.rglob('*'):
            rel=path.relative_to(project)
            if any(part in GENERATED for part in rel.parts):continue
            if path.is_file():actual.add(rel.as_posix())
        expected=set(files)|{'MANIFEST.json'}
        if actual!=expected:
            raise ValueError(f'Unexpected payload inventory: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}')
    return {'kind':'frozen Lean payload byte integrity','passed':True,
            'manifest_sha256':expected_manifest_sha256,'files_checked':len(files),
            'fresh_lean_execution':False}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=Path('Lean'))
    ap.add_argument('--baseline',type=Path,default=CI_ROOT/'frozen_lean_release.json')
    ap.add_argument('--allow-generated-files',action='store_true')
    args=ap.parse_args()
    baseline=json.loads(args.baseline.read_text())
    result=verify_manifest(args.project,baseline['manifest_sha256'],not args.allow_generated_files)
    print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
