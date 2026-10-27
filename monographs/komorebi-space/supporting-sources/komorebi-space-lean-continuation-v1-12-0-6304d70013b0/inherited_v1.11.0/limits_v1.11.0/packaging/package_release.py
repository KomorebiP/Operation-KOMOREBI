#!/usr/bin/env python3
"""Package a frozen, accepted Lean continuation without modifying its predecessor.

Standard-library only. --check-only validates without writing output. --parent-only
checks the pinned predecessor without requiring the new acceptance gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
WORK = PROJECT.parent
PARENT_SHA = 'df099ee00bf5487b2f9b108f4209e6951c9e18b79494e3f4682dd779cb0ed704'
PARENT_NAME = 'Komorebi_Space_Monograph_v1.10.0'
RELEASE_NAME = 'Komorebi_Space_Lean_Continuation_v1.11.0'
ROOT_FILES = ('README.md', 'PROGRESS_LEDGER.md', 'PROGRESS_LEDGER.json',
              'VERIFICATION_SUMMARY.json', 'FORMAL_COVERAGE.json', 'NEXT_RESEARCH_BLOCK.md')
EXCLUDED_DIRS = {'build', '__pycache__'}
EXCLUDED_SUFFIXES = ('.pyc', '.olean', '.ilean', '.olean.private', '.olean.server', '.o', '.so', '.a')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest_stream(stream) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def sha(path: Path) -> str:
    require(not path.is_symlink(), f'Refusing symlink: {path}')
    with path.open('rb') as stream:
        return digest_stream(stream)


def safe_relative(name: str) -> PurePosixPath:
    require(bool(name) and '\\' not in name and ':' not in name and not any(ord(c) < 32 for c in name),
            f'Unsafe relative path: {name!r}')
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix() == name and
            all(part not in {'', '.', '..'} for part in p.parts), f'Unsafe relative path: {name!r}')
    return p


def tree(root: Path, filtered: bool = False) -> dict[str, str]:
    require(root.is_dir() and not root.is_symlink(), f'Expected ordinary directory: {root}')
    result = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        base = Path(folder)
        kept = []
        for name in sorted(dirs):
            if filtered and name in EXCLUDED_DIRS:
                continue
            require(not (base / name).is_symlink(), f'Refusing directory symlink: {base / name}')
            kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            if filtered and name.endswith(EXCLUDED_SUFFIXES):
                continue
            p = base / name
            require(stat.S_ISREG(p.lstat().st_mode), f'Refusing nonregular file: {p}')
            rel = p.relative_to(root).as_posix()
            safe_relative(rel)
            result[rel] = sha(p)
    return dict(sorted(result.items()))


def parse_manifest(data: bytes) -> dict[str, str]:
    result = {}
    for line in data.decode('utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        require(match is not None, f'Malformed checksum line: {line!r}')
        digest, name = match.groups()
        safe_relative(name)
        require(name not in result, f'Duplicate checksum path: {name}')
        result[name] = digest
    require(bool(result), 'Empty checksum manifest')
    return result


def zip_tree(archive: Path, root_name: str) -> tuple[dict[str, str], bytes]:
    """Read all regular ZIP members, rejecting traversal, symlinks, and duplicates."""
    require(not archive.is_symlink(), 'Refusing archive symlink')
    prefix = root_name + '/'
    result = {}
    manifest = None
    with zipfile.ZipFile(archive) as z:
        seen = set()
        for item in z.infolist():
            name = item.filename
            clean = name[:-1] if item.is_dir() else name
            safe_relative(clean)
            require(name not in seen, f'Duplicate ZIP member: {name}')
            seen.add(name)
            require(clean == root_name or name.startswith(prefix), f'Unexpected ZIP root: {name}')
            mode = item.external_attr >> 16
            require(not stat.S_ISLNK(mode), f'ZIP symlink: {name}')
            kind = stat.S_IFMT(mode)
            require(kind in {0, stat.S_IFREG, stat.S_IFDIR}, f'Nonregular ZIP member: {name}')
            if item.is_dir():
                continue
            rel = name[len(prefix):]
            safe_relative(rel)
            require(rel not in result, f'Duplicate ZIP payload path: {rel}')
            with z.open(item) as stream:
                result[rel] = digest_stream(stream)
            if rel == 'SHA256SUMS.txt':
                manifest = z.read(item)
        require(z.testzip() is None, 'ZIP CRC validation failed')
    require(manifest is not None, 'Missing top-level checksum manifest')
    require(parse_manifest(manifest) == {k: v for k, v in result.items() if k != 'SHA256SUMS.txt'},
            'ZIP checksum manifest does not enumerate and match every payload file')
    return dict(sorted(result.items())), manifest


def check_parent(parent: Path, expanded: Path) -> dict:
    require(sha(parent) == PARENT_SHA, 'Pinned predecessor archive hash mismatch')
    archived, _ = zip_tree(parent, PARENT_NAME)
    require(len(archived) == 4828, 'Predecessor must contain 4827 payload files plus its manifest')
    require(tree(expanded) == archived, 'Expanded predecessor differs from the pinned ZIP bytes')
    return {'archive_sha256': PARENT_SHA, 'file_sha256': archived,
            'payload_files': 4827, 'total_files_with_manifest': 4828}


def load(path: Path):
    require(not path.is_symlink(), f'Refusing JSON symlink: {path}')
    return json.loads(path.read_text())


def exact_file(path: Path, expected: str, message: str) -> None:
    require(sha(path) == expected, message)


def check_acceptance(run: Path, type_audit: Path) -> dict:
    require(run.is_relative_to(PROJECT / 'integration/runs'), 'Run must be in this continuation')
    receipt_path, post_path = run / 'receipt.json', run / 'postflight.json'
    rec, post = load(receipt_path), load(post_path)
    require(rec['status'] == post['status'] == 'PASS', 'Formal acceptance gates have not passed')
    receipt_sha, post_sha = sha(receipt_path), sha(post_path)
    require(post['run_receipt_sha256'] == receipt_sha, 'Postflight does not bind this receipt')
    require(all(post['gates'].values()), 'A postflight gate failed')
    require(rec['clean_project_build'] and rec['initial_project_objects'] == {}, 'Not a clean project build')
    require(rec['compile_policy'] == {'autoImplicit': False, 'threads': 1, 'warningAsError': True},
            'Unexpected compiler policy')
    source = tree(run / 'source')
    require(source == rec['source_snapshot_sha256'] == post['source_snapshot_sha256'],
            'Accepted source snapshot changed')
    assembly = Path(rec['assembly_path'])
    require(assembly.is_relative_to(PROJECT / 'integration/assemblies'), 'Unexpected assembly location')
    inventory = load(assembly / 'inventory.json')
    exact_file(assembly / 'inventory.json', rec['inventory_sha256'], 'Assembly inventory changed')
    require(rec['inventory_sha256'] == post['inventory_sha256'], 'Inventory/postflight mismatch')
    require(tree(PROJECT / 'formal') == inventory['overlay_input_sha256'], 'Overlay changed after acceptance')
    require(tree(PROJECT / 'integration/scripts', filtered=True) == rec['verifier_input_sha256'],
            'Verifier helpers changed after acceptance')
    review_path = PROJECT / 'reviews/reviewed_helpers.json'
    review = load(review_path)
    exact_file(review_path, post['review_manifest_sha256'], 'Helper review changed after acceptance')
    exact_file(PROJECT / 'integration/postflight/validate.py', review['postflight_sha256'],
               'Postflight helper changed after review')
    exact_file(run / 'axioms.json', rec['axiom_report_sha256'], 'Axiom report changed')
    require(rec['axiom_report_sha256'] == post['axiom_report_sha256'], 'Axiom report/postflight mismatch')
    exact_file(run / 'runtime_snapshot.json', rec['runtime_snapshot_sha256'], 'Runtime inventory changed')
    require(rec['runtime_snapshot_sha256'] == post['runtime_snapshot_sha256'],
            'Runtime inventory/postflight mismatch')
    audit = load(run / 'axioms.json')
    rows = audit['declarations']
    require(audit['unexpected'] == [] and audit['count'] == len(rows) == rec['axiom_declarations'],
            'Axiom declaration inventory mismatch')
    require(len({row['name'] for row in rows}) == len(rows), 'Duplicate audited declaration')
    require(all(not row['unsafe'] and set(row['axioms']) <= ALLOWED_AXIOMS for row in rows),
            'Unapproved axiom or unsafe declaration')
    new_rows = sorted((r for r in rows if r['module'] in rec['new_modules']), key=lambda r: r['name'])
    require(len(new_rows) == rec['new_axiom_declarations'], 'New declaration count mismatch')
    require(all(r['type'] and r['type_mode'] == 'full' for r in new_rows), 'Missing complete new type export')
    require(new_rows == load(run / 'new_declarations.json'), 'Derived new declaration report changed')
    require(sorted(rows, key=lambda r: (r['module'], r['name'])) == load(run / 'declarations_sorted.json'),
            'Derived cumulative declaration report changed')
    for command in rec['commands']:
        log = safe_relative(command['log'])
        exact_file(run / log, command['log_sha256'], 'Compiler command log changed')
        require(command['passed'] and not command['timeout'], 'Rejected compiler/control command')
    require(len(rec['commands']) == post['command_count'], 'Command count mismatch')
    production = sorted(n for n in source if n.startswith('KomorebiSpace/') and n.endswith('.lean'))
    require(len(production) == rec['production_modules'], 'Production module count mismatch')
    compiled = sorted(n for n in source if n in rec['source_sha256'])
    require(len(compiled) == rec['compile_targets'], 'Compilation target count mismatch')
    require({n: source[n] for n in compiled} == rec['source_sha256'], 'Compiled source hashes changed')
    ledger = load(PROJECT / 'PROGRESS_LEDGER.json')
    require(ledger['status'] == 'ACCEPTED', 'Release ledger is not accepted')
    require(ledger['formal_receipt_sha256'] == receipt_sha and ledger['postflight_sha256'] == post_sha,
            'Release ledger describes another accepted run')
    evidence = ledger['acceptance_evidence_sha256']
    require(bool(evidence), 'No recorded acceptance evidence')
    for required in ('reviews/VERIFIER_REVIEW.md', 'reviews/reviewed_helpers.json',
                     'reviews/PACKAGING_SCRIPT_REVIEW.md', 'formal/tests/control_manifest.json'):
        require(required in evidence, f'Required acceptance review is not bound: {required}')
    for name, digest in evidence.items():
        exact_file(PROJECT / safe_relative(name), digest, f'Acceptance evidence changed: {name}')
    require(sha(Path(__file__)) in (PROJECT / 'reviews/PACKAGING_SCRIPT_REVIEW.md').read_text(),
            'Packaging review does not bind this exact script')
    require(type_audit.is_relative_to(PROJECT), 'Type audit must belong to this continuation')
    type_rel = type_audit.relative_to(PROJECT).as_posix()
    require(type_rel in evidence, 'Final exact-type audit is not bound in accepted ledger')
    audit_text = type_audit.read_text()
    type_bindings = [receipt_sha, rec['axiom_report_sha256']]
    for module in rec['new_modules']:
        name = module.replace('.', '/') + '.lean'
        require(name in source, f'Missing new production source: {name}')
        type_bindings.append(source[name])
    require(all(h in audit_text for h in type_bindings), 'Type audit is missing a source/export/run hash binding')
    for name in ROOT_FILES:
        require((PROJECT / name).is_file() and not (PROJECT / name).is_symlink(), f'Missing release file: {name}')
    require(not any(p.suffix.lower() == '.pdf' for p in PROJECT.rglob('*') if p.is_file()),
            'Lean continuation must not include a newly relabeled PDF')
    return {'formal_receipt_sha256': receipt_sha, 'postflight_sha256': post_sha,
            'axiom_report_sha256': rec['axiom_report_sha256'], 'source_sha256': source,
            'production_modules': len(production), 'compile_targets': len(compiled),
            'explicit_theorem_lemma_count': rec['explicit_theorem_lemma_count'],
            'axiom_declarations': len(rows), 'new_axiom_declarations': len(new_rows),
            'command_count': len(rec['commands']), 'control_count': len(rec['controls']),
            'new_modules': rec['new_modules'], 'acceptance_evidence_sha256': evidence,
            'type_audit': type_rel, 'type_audit_sha256': sha(type_audit)}


def copy_checked(src: Path, dest: Path, files: dict[str, str]) -> None:
    require(not dest.exists() and not dest.is_symlink(), f'Refusing destination overwrite: {dest}')
    dest.mkdir(parents=True)
    for name, expected in files.items():
        rel = safe_relative(name)
        inp, out = src / rel, dest / rel
        exact_file(inp, expected, f'Source changed before copy: {inp}')
        out.parent.mkdir(parents=True, exist_ok=True)
        with inp.open('rb') as source, out.open('xb') as target:
            shutil.copyfileobj(source, target, 1024 * 1024)
        exact_file(out, expected, f'Copy identity failed: {out}')
    require(tree(dest) == files, f'Copied tree mismatch: {dest}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=PROJECT / 'integration/runs/clean_limits_01')
    parser.add_argument('--type-audit', type=Path, default=PROJECT / 'reviews/WR08_WR09_WR16_MATH_AUDIT.md')
    parser.add_argument('--parent-archive', type=Path, default=WORK / 'output' / (PARENT_NAME + '.zip'))
    parser.add_argument('--parent-expanded', type=Path, default=WORK / 'output' / PARENT_NAME)
    parser.add_argument('--output-dir', type=Path, default=WORK / 'output')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--parent-only', action='store_true')
    args = parser.parse_args()
    # Validate original paths before resolve, which would otherwise hide a symlink.
    for key in ('run', 'type_audit', 'parent_archive', 'parent_expanded', 'output_dir'):
        require(not getattr(args, key).is_symlink(), f'Refusing symlink argument: {key}')
    parent_archive, parent_expanded = args.parent_archive.resolve(), args.parent_expanded.resolve()
    parent = check_parent(parent_archive, parent_expanded)
    if args.parent_only:
        print(json.dumps({'status': 'PASS', 'scope': 'pinned predecessor identity only',
                          **{k: v for k, v in parent.items() if k != 'file_sha256'}}, indent=2))
        return
    run, type_audit = args.run.resolve(), args.type_audit.resolve()
    acceptance = check_acceptance(run, type_audit)
    before = tree(PROJECT, filtered=True)
    require(not any('/runtime/' in '/' + n or '/downloads/' in '/' + n for n in before),
            'Unexpected portable runtime content in continuation tree')
    if args.check_only:
        print(json.dumps({'status': 'PASS', 'scope': 'acceptance and parent preflight; no output written',
                          'continuation_files': len(before),
                          **{k: v for k, v in acceptance.items() if k != 'source_sha256'}}, indent=2))
        return
    output = args.output_dir.resolve()
    require(output.is_dir(), 'Output directory must already exist')
    dest, archive = output / RELEASE_NAME, output / (RELEASE_NAME + '.zip')
    verification = output / 'Komorebi_Space_Lean_Delivery_Verification_v1.11.0.json'
    progress = output / 'Komorebi_Space_Lean_Progress_v1.11.0.md'
    for p in (dest, archive, verification, progress):
        require(not p.exists() and not p.is_symlink(), f'Refusing release overwrite: {p}')
    dest.mkdir()
    copy_checked(run / 'source', dest / 'formal', acceptance['source_sha256'])
    copy_checked(PROJECT, dest / PROJECT.name, before)
    copy_checked(parent_expanded, dest / 'inherited_v1.10.0', parent['file_sha256'])
    for name in ROOT_FILES:
        with (PROJECT / name).open('rb') as inp, (dest / name).open('xb') as out:
            shutil.copyfileobj(inp, out)
        exact_file(dest / name, before[name], f'Root release file copy changed: {name}')
    require(before == tree(PROJECT, filtered=True), 'Continuation changed while packaging')
    require(parent['file_sha256'] == tree(parent_expanded), 'Predecessor changed while packaging')
    require(sha(parent_archive) == PARENT_SHA, 'Predecessor archive changed while packaging')
    require(acceptance == check_acceptance(run, type_audit), 'Acceptance bindings changed while packaging')
    payload = tree(dest)
    manifest = ''.join(f'{digest}  {name}\n' for name, digest in payload.items()).encode()
    with (dest / 'SHA256SUMS.txt').open('xb') as stream:
        stream.write(manifest)
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in [*payload, 'SHA256SUMS.txt']:
            z.write(dest / name, RELEASE_NAME + '/' + name)
    archived, archived_manifest = zip_tree(archive, RELEASE_NAME)
    require(archived_manifest == manifest, 'Archive manifest bytes changed')
    require(archived == tree(dest), 'Archive payload differs from expanded release')
    require({n.removeprefix('inherited_v1.10.0/'): h for n, h in archived.items()
             if n.startswith('inherited_v1.10.0/')} == parent['file_sha256'],
            'Archive did not preserve every predecessor file')
    require({n.removeprefix('formal/'): h for n, h in archived.items() if n.startswith('formal/')} ==
            acceptance['source_sha256'], 'Archive current formal source identity failed')
    require(not any(any(part in EXCLUDED_DIRS for part in PurePosixPath(n).parts) or
                    n.endswith(EXCLUDED_SUFFIXES) for n in archived), 'Excluded build object in archive')
    with (PROJECT / 'PROGRESS_LEDGER.md').open('rb') as inp, progress.open('xb') as out:
        shutil.copyfileobj(inp, out)
    result = {'status': 'PASS', 'archive': str(archive), 'archive_sha256': sha(archive),
              'archive_bytes': archive.stat().st_size, 'payload_files': len(payload),
              'total_archive_files_with_manifest': len(archived),
              'manifest_sha256': sha(dest / 'SHA256SUMS.txt'),
              'parent_archive_sha256': PARENT_SHA, 'parent_payload_files': 4827,
              'parent_files_preserved_including_manifest': 4828,
              'parent_expanded_compared_with_pinned_zip_bytes': True,
              'current_formal_source_byte_identical': True,
              'crc': 'PASS', 'payload_sha256': 'PASS',
              'compiled_objects_included': False, 'portable_runtime_included': False,
              'new_pdf_claimed': False, 'historical_pdf_location': 'inherited_v1.10.0/publication/',
              'progress': str(progress), 'progress_sha256': sha(progress),
              'packaging_script_sha256': sha(Path(__file__)),
              **{k: v for k, v in acceptance.items() if k != 'source_sha256'}}
    with verification.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print(f'Packaging rejected: {error}', file=sys.stderr)
        raise SystemExit(1)
