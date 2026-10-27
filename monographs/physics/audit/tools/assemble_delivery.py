#!/usr/bin/env python3
"""Assemble an unsealed publication only after formal and publication acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def copy_file(source, destination):
    require(source.is_file() and not source.is_symlink(), f'Not regular: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        require(sha(destination) == sha(source), f'Conflicting copy: {destination}')
    else:
        shutil.copy2(source, destination)
    require(sha(destination) == sha(source), f'Copy mismatch: {destination}')


def copy_tree(source, destination):
    require(source.is_dir() and not source.is_symlink(), f'Not a regular source directory: {source}')
    for p in sorted(source.rglob('*')):
        rel = p.relative_to(source)
        if any(x in {'.lake', '__pycache__', '.git'} for x in rel.parts) or p.suffix == '.pyc':
            continue
        require(not p.is_symlink(), f'Unexpected symlink: {p}')
        if p.is_file():
            copy_file(p, destination / rel)
        else:
            require(p.is_dir(), f'Nonregular source entry: {p}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    task = args.task_root.resolve(strict=True)
    out = args.out.resolve()
    require(not out.exists(), 'Refusing existing delivery directory')
    gate = task / 'verification/centered_run02'
    receipt = json.loads((gate / 'receipt.json').read_text())
    require(receipt['status'] == 'PASS_SCOPED_CENTERED_EXTENSION', 'Formal gate is not passing')
    project = task / 'work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
    require((project / 'BLOCK51_ACCEPTANCE.json').is_file(), 'Formal metadata not finalized')
    publication = task / 'publication'
    baseline = task / 'baseline/Komorebi_Physics_Open_Publication_Package/Komorebi_Physics_Publication/formal'
    copied_roots = [publication, baseline, project, gate,
                   task / 'verification/centered_run01', task / 'attempts',
                   task / 'review', task / 'gate_tools', task / 'formal_records_tools',
                   task / 'publication_notes']
    for source_root in copied_roots:
        require(source_root.is_dir() and not source_root.is_symlink(), f'Missing or linked source tree: {source_root}')
        require(not out.is_relative_to(source_root.resolve()), f'Output inside copied source tree: {source_root}')
    qa_path = publication / 'audit/continuum_publication_qa.json'
    qa = json.loads(qa_path.read_text())
    require(str(qa.get('status', '')).startswith('PASS'), 'Publication QA is not passing')
    out.mkdir(parents=True)
    copy_tree(publication, out)
    formal = out / 'formal'
    copy_tree(baseline, formal)
    current = formal / 'continuum'
    copy_tree(project, current)
    evidence = current / 'verification/block51'
    copy_tree(gate, evidence / 'current')
    copy_tree(task / 'verification/centered_run01', evidence / 'failed_run01')
    copy_tree(task / 'attempts', evidence / 'development')
    copy_tree(task / 'review', evidence / 'review')
    copy_tree(task / 'gate_tools', evidence / 'gate_development')
    copy_tree(task / 'formal_records_tools', evidence / 'metadata_tools')
    copy_file(task / 'BASELINE_MATHEMATICAL_INPUTS.json', evidence / 'BASELINE_MATHEMATICAL_INPUTS.json')
    copy_file(task / 'review/FROZEN_SOURCE_REVIEW.json', evidence / 'FROZEN_SOURCE_REVIEW.json')
    copy_file(task / 'TARGET_CONTRACT.md', evidence / 'TARGET_CONTRACT.md')
    for name in ('runtime_recovery_receipt.json', 'runtime_integrity_audit.json',
                 'runtime_verification.json', 'runtime_verification.log',
                 'runtime_integrity_audit.py', 'runtime_recovery_record.py',
                 'runtime_disk_cleanup.json', 'runtime_transfer_cleanup.json'):
        copy_file(task / name, evidence / 'runtime_provenance' / name)
    for name in ('assemble_delivery.py', 'seal_release.py'):
        copy_file(task / name, out / 'audit/tools' / name)
    copy_tree(task / 'publication_notes', out / 'audit/publication_notes')
    ledger = (project / 'PROGRESS_LEDGER_v0.51.0.md').read_text()
    ledger = re.sub(r'\]\(([^)]+)\)', lambda m: '](' + 'formal/continuum/' + m.group(1) + ')', ledger)
    (out / 'PROGRESS_LEDGER_v0.51.0.md').write_text(ledger)
    copy_file(task / 'EXECUTION_NOTES.md', out / 'audit/EXECUTION_NOTES.md')
    identity = {
        'schema': 'komorebi.physics.assembly.v1',
        'status': 'ASSEMBLED_PENDING_BINDING_AND_SEAL',
        'formal_receipt': 'formal/continuum/verification/block51/current/receipt.json',
        'formal_receipt_sha256': sha(gate / 'receipt.json'),
        'publication_qa': 'audit/continuum_publication_qa.json',
        'publication_qa_sha256': sha(qa_path),
        'main_pdf': 'Komorebi_Physics.pdf',
        'main_pdf_sha256': sha(publication / 'Komorebi_Physics.pdf'),
        'parent_publication_archive_sha256': 'd3666da56363b10b6a629f392c9e52247cfa11a802383372877fb93494b24583',
        'parent_generator_archive_sha256': 'a4bbe33f081240bf9b71b0387c7f10052bf4f5daa03513b1c3ea25d18616cf77',
        'note': 'This is an assembly checkpoint, not the final integrity verdict. See PACKAGED_SOURCE_BINDING.json and the external delivery verification receipt.'
    }
    (out / 'audit/ASSEMBLY.json').write_text(json.dumps(identity, indent=2) + '\n')
    print(json.dumps(identity, indent=2))


if __name__ == '__main__':
    main()
