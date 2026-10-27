#!/usr/bin/env python3
"""Assemble the cumulative Paper IX perturbation release from the working tree.

Run after the fresh Lean gate, independent reconciliation, and release documents
are complete. The staging directory must already contain the previous release,
whose five replaced root documents are retained under historical/tower_release_root.
This script never writes the current README, checklist, or release audit.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

RELEASE = 'PRSC_IX_Complete_Perturbation'
PRIOR_RELEASE = 'PRSC_IX_Complete_Padic_Towers'
EXCLUDED_PARTS = {'build', 'dev_build', '__pycache__', '.git', '.lake'}
EXCLUDED_SUFFIXES = ('.olean', '.olean.server', '.olean.private', '.ir', '.ir.sig', '.pyc')
SOURCE_SUFFIXES = {'.lean', '.py', '.json', '.md', '.log', '.tex', '.txt'}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def copy(source: Path, destination: Path) -> None:
    if not source.is_file() or source.is_symlink():
        raise ValueError(f'Expected an ordinary source file: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if source.read_bytes() != destination.read_bytes():
        raise ValueError(f'Copy mismatch: {destination}')


def allowed_file(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return (path.is_file() and not path.is_symlink()
            and not any(part in EXCLUDED_PARTS for part in relative.parts)
            and not path.name.endswith(EXCLUDED_SUFFIXES)
            and path.suffix in SOURCE_SUFFIXES)


def copy_group(source: Path, destination: Path) -> None:
    if source.exists():
        for path in sorted(source.rglob('*')):
            if allowed_file(path, source):
                copy(path, destination/path.relative_to(source))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--expected-prior-archives', type=int, default=10)
    args = parser.parse_args()
    root = args.workspace.resolve()
    project = root/'polynomial_deformation'
    staging = root/'release_staging'/RELEASE
    prior = root/'release_staging'/PRIOR_RELEASE
    if not staging.is_dir():
        raise ValueError('Prepare the cumulative staging directory before assembling')

    # Previous root bytes must remain present even after the active docs change.
    historical = staging/'historical/tower_release_root'
    for name in ('README.md', 'REMAINING_CHECKLIST.md', 'RELEASE_AUDIT.json',
                 'MANIFEST.json', 'PACKAGE_COMPLETENESS.json'):
        if (historical/name).read_bytes() != (prior/name).read_bytes():
            raise ValueError(f'Prior root document was not preserved: {name}')

    report_path = project/'replay_01/polynomial_deformation_verification.json'
    report = read_json(report_path)
    reconciliation = read_json(project/'audit/reconciliation.json')
    release_audit = read_json(staging/'RELEASE_AUDIT.json')
    report_hash = sha(report_path.read_bytes())
    if not report['status'] == reconciliation['status'] == release_audit['status'] == 'PASS':
        raise ValueError('Gate, reconciliation, and release audit must all pass')
    reconciled_report_hash = reconciliation.get('report_sha256',
                                               reconciliation.get('verification_report_sha256'))
    if reconciled_report_hash != report_hash:
        raise ValueError('Independent reconciliation refers to another gate report')
    if release_audit['release'] != RELEASE or release_audit['report_sha256'] != report_hash:
        raise ValueError('Current release audit is missing or refers to another report')
    if not (project/'INDEPENDENT_PROOF_AUDIT.md').read_text().strip():
        raise ValueError('Independent mathematical audit is empty')

    for group in ('formalization', 'scripts', 'contracts', 'controls', 'audit'):
        copy_group(project/group, staging/'polynomial_deformation'/group)
    for source in sorted(project.iterdir()):
        if source.is_file() and source.suffix in {'.md', '.json'} and source.name != 'ARCHIVE_VALIDATION.json':
            copy(source, staging/'polynomial_deformation'/source.name)
    copy_group(project/'replay_01', staging/'polynomial_deformation/verification')
    for source in sorted(project.glob('replay_01*.log')):
        copy(source, staging/'polynomial_deformation/verification'/source.name)
    for group in ('dev', 'logs'):
        copy_group(project/group, staging/'polynomial_deformation/development'/group)
    copy(project/'assemble_release.py',
         staging/'historical/deformation_release_assembly/assemble_release.py')
    bridge = root/'output/Paper_IX_Perturbation_Deformation_Bridge.md'
    copy(bridge, staging/'research/perturbation'/bridge.name)

    inventory = read_json(project/'inventory.json')
    for entry in (inventory['modules'] + inventory['control_support']
                  + inventory['contracts'] + inventory['negative_controls']):
        if sha((staging/'polynomial_deformation'/entry['source']).read_bytes()) != entry['sha256']:
            raise ValueError(f'Packaged source hash mismatch: {entry["source"]}')
    if sha((staging/'polynomial_deformation/inventory.json').read_bytes()) != report['inventory_sha256']:
        raise ValueError('Packaged inventory does not match the verified inventory')
    for run in report['runs']:
        if sha((staging/'polynomial_deformation/verification'/run['log']).read_bytes()) != run['log_sha256']:
            raise ValueError(f'Packaged gate log mismatch: {run["log"]}')
    for source in [staging/'replay_paper9_deformation.py',
                   *(staging/'polynomial_deformation/scripts').glob('*.py')]:
        ast.parse(source.read_text(), filename=str(source))

    covered = {sha(path.read_bytes()) for path in staging.rglob('*') if path.is_file()}
    baseline = staging/'baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip'
    with zipfile.ZipFile(baseline) as archive:
        baseline_entries = [
            {'path': entry.filename, 'bytes': entry.file_size, 'sha256': sha(archive.read(entry))}
            for entry in archive.infolist() if not entry.is_dir()
        ]
    covered.update(entry['sha256'] for entry in baseline_entries)
    prior_archives = []
    for source in sorted((root/'output').glob('*.zip')):
        if source.name == RELEASE+'.zip':
            continue
        with zipfile.ZipFile(source) as archive:
            entries = [entry for entry in archive.infolist() if not entry.is_dir()]
            missing = [entry.filename for entry in entries if sha(archive.read(entry)) not in covered]
            if missing:
                raise ValueError(f'Missing prior contents in {source.name}: {missing}')
        prior_archives.append({
            'archive': source.name, 'archive_sha256': sha(source.read_bytes()),
            'files': len(entries), 'all_uncompressed_file_hashes_covered': True,
        })
    if len(prior_archives) != args.expected_prior_archives:
        raise ValueError(f'Expected {args.expected_prior_archives} prior archives, found {len(prior_archives)}')
    completeness = {
        'status': 'PASS',
        'scope': 'Known local Paper IX collection plus the checked perturbation block; not a census of remote files',
        'prior_archives': prior_archives,
        'missing_prior_file_hashes': 0,
        'baseline_zip_sha256': sha(baseline.read_bytes()),
        'baseline_entry_inventory': baseline_entries,
        'new_source_inventory': 'polynomial_deformation/inventory.json',
        'new_fresh_gate': 'polynomial_deformation/verification/polynomial_deformation_verification.json',
        'independent_audit': 'polynomial_deformation/INDEPENDENT_PROOF_AUDIT.md',
        'bridge_note': 'research/perturbation/'+bridge.name,
        'bridge_note_sha256': sha(bridge.read_bytes()),
        'manuscript_files_exposed': sum(1 for p in (staging/'manuscript').rglob('*') if p.is_file()),
        'excluded': ['Separate portable Lean runtime', 'Compiled outputs, caches, and symlinks',
                     'Unrelated raw search results',
                     'Full third-party Nishibuchi paper; URL/version/hash record retained',
                     'Duplicate cumulative ZIP containers'],
        'limitations': ['Two older edge manuscripts recovered only as partial source windows',
                        'Annals TeX reconstructed text copy',
                        'Historical main manuscript not revised to absorb every continuation',
                        'Full weighted perturbation and rectangular graph results remain prose-level'],
    }
    (staging/'PACKAGE_COMPLETENESS.json').write_text(json.dumps(completeness, indent=2)+'\n')

    rows = []
    for path in sorted(staging.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink in release: {path}')
        if not path.is_file() or path == staging/'MANIFEST.json':
            continue
        relative = path.relative_to(staging)
        if any(part in EXCLUDED_PARTS for part in relative.parts) or path.name.endswith(EXCLUDED_SUFFIXES):
            raise ValueError(f'Compiled or cached output in release: {relative}')
        rows.append({'path': str(relative), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())})
    manifest = {'release': RELEASE, 'algorithm': 'SHA-256', 'manifest_excludes_itself': True,
                'file_count_excluding_manifest': len(rows), 'files': rows}
    (staging/'MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    output = root/'output'/(RELEASE+'.zip')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(staging.rglob('*')):
            if path.is_file():
                archive.write(path, str(Path(RELEASE)/path.relative_to(staging)))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        expected_names = {str(Path(RELEASE)/row['path']) for row in rows} | {RELEASE+'/MANIFEST.json'}
        if len(archive.infolist()) != len(expected_names) or set(archive.namelist()) != expected_names:
            raise ValueError('ZIP entry set differs from the manifest')
        for row in rows:
            data = archive.read(str(Path(RELEASE)/row['path']))
            if len(data) != row['bytes'] or sha(data) != row['sha256']:
                raise ValueError(f'ZIP entry hash failure: {row["path"]}')
        if archive.read(RELEASE+'/MANIFEST.json') != (staging/'MANIFEST.json').read_bytes():
            raise ValueError('ZIP manifest byte mismatch')
    result = {'status': 'PASS', 'archive': str(output), 'bytes': output.stat().st_size,
              'sha256': sha(output.read_bytes()), 'files': len(rows)+1,
              'prior_archives_covered': len(prior_archives),
              'zip_crc': 'PASS', 'all_entry_hashes': 'PASS',
              'manifest_sha256': sha((staging/'MANIFEST.json').read_bytes())}
    (project/'ARCHIVE_VALIDATION.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
