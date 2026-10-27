#!/usr/bin/env python3
"""Package a completed proof checkpoint and validate the extracted distribution."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OMIT = {'.lake', '.git', '__pycache__'}

def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def distributable() -> list[Path]:
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in OMIT for x in p.relative_to(ROOT).parts)
                  and p.suffix not in {'.pyc', '.pyo'})

def main() -> int:
    result = json.loads((ROOT/'verification/RESULTS.json').read_text())
    record = json.loads((ROOT/'verification/process_record.json').read_text())
    if result['status'] != 'PASS' or record['exit_status'] != 0:
        raise ValueError('Only a completed passing verification can be packaged')
    command = [sys.executable, 'scripts/validate_manifest.py',
               'verification/computation_manifest.json', '--root', '.']
    subprocess.run(command, cwd=ROOT, check=True)
    files = [p for p in distributable() if p != ROOT/'SHA256SUMS.txt']
    sums = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{sha}  {name}\n' for name,sha in sums.items()))
    archive = ROOT.parent/(ROOT.name+'.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in distributable():
            name = ROOT.name+'/'+p.relative_to(ROOT).as_posix()
            z.write(p, name)
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise ValueError(f'ZIP CRC failure: {bad}')
        for name in z.namelist():
            rel = Path(name)
            if rel.is_absolute() or '..' in rel.parts or rel.parts[0] != ROOT.name:
                raise ValueError(f'Unsafe archive path: {name}')
        with tempfile.TemporaryDirectory(prefix='kzfc_v080_archive_', dir=ROOT.parent) as tmp:
            z.extractall(tmp)
            extracted = Path(tmp)/ROOT.name
            mismatches = [name for name,sha in sums.items()
                          if not (extracted/name).is_file() or digest(extracted/name) != sha]
            actual = {p.relative_to(extracted).as_posix() for p in extracted.rglob('*') if p.is_file()}
            if mismatches or actual != set(sums)|{'SHA256SUMS.txt'}:
                raise ValueError(f'Extracted checksum/file-set failure: {mismatches}')
            check = subprocess.run(command, cwd=extracted, capture_output=True, text=True, check=True)
    report = {
        'status': 'PASS', 'archive': str(archive), 'sha256': digest(archive),
        'bytes': archive.stat().st_size, 'files': len(sums)+1,
        'hashed_files_checked_after_extraction': len(sums), 'zip_crc': 'PASS',
        'exact_file_set': 'PASS', 'extracted_manifest_exit_status': check.returncode,
        'extracted_manifest_output': check.stdout.strip(),
        'proof_verification_session_id': result['session_id'],
        'theorem_declarations': result['theorem_count'],
        'note': 'Archive integrity and manifest checks do not independently reprove Lean soundness.'
    }
    report_path = ROOT.parent/(ROOT.name+'_ARCHIVE_CHECK.json')
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as e:
        print('Packaging failed:',e,file=sys.stderr)
        raise SystemExit(1)
