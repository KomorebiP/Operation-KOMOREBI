#!/usr/bin/env python3
"""Package a completed Reviewed Core release without modifying its formal root.

Requires both actual cold gates, their comparison, and the final admission record.
Creates a full source/receipt/object archive with exact-set integrity checks on a
stage and clean extraction. All new receipts are outside the immutable archive.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
CANONICAL = 'Machine_Native_Reasoning_Reviewed_Core_1.0.0'
SNAPSHOT_SHA = '727af49876690ee83bb18b46895dea01aae296bfeaf83331221870970e59daf0'
PREDECESSOR_SHA = '206a735d18d4d96f8dfd32f80622f905f214233678f941dc0968c8205435ad45'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def canonical(name):
    require(isinstance(name, str) and bool(name), 'Empty member name')
    require('\\' not in name and ':' not in name and all(ord(c) >= 32 for c in name),
            'Invalid member characters: ' + name)
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(c not in ('', '.', '..') for c in name.split('/')),
            'Noncanonical member: ' + name)
    require(str(p) == name, 'Noncanonical member: ' + name)
    return p


def files(root):
    answer = []
    for path in sorted(root.rglob('*')):
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode), 'Symlink in package source: ' + str(path))
        if stat.S_ISDIR(mode):
            continue
        require(stat.S_ISREG(mode), 'Nonregular file: ' + str(path))
        canonical(path.relative_to(root).as_posix())
        answer.append(path)
    return answer


def bind_release(root):
    """Read-only exact source, run, log, object, snapshot and admission binding."""
    verify = module(root/'scripts/verify.py', 'source_pin_verifier')
    pins = verify.source_pins()
    f = load(root/'evidence/final19/report.json')
    g = load(root/'evidence/fresh19/report.json')
    c = load(root/'evidence/CORE32_COMPARISON.json')
    q = load(root/'evidence/SEQUENCE19.json')
    s = load(root/'evidence/SOURCE_SNAPSHOT_BLOCK19.json')
    a = load(root/'release/ADMISSION_RECORD.json')
    require(all(x.get('status') == 'PASS' for x in (f, g, c, q, s, a)), 'Release not fully admitted')
    require(len(pins) == s['source_count'] == 501, 'Wrong source input count')
    require(pins == f['input_sha256_before'] == f['input_sha256_after'] ==
            g['input_sha256_before'] == g['input_sha256_after'] == s['source_inputs'],
            'Exact source input closure changed')
    require(c['comparisons'] and all(c['comparisons'].values()), 'Failed recorded comparison')
    require(c['final_receipt_sha256'] == sha(root/'evidence/final19/report.json'), 'Primary receipt binding')
    require(c['fresh_receipt_sha256'] == sha(root/'evidence/fresh19/report.json'), 'Fresh receipt binding')
    require(a['primary']['report_sha256'] == c['final_receipt_sha256'], 'Admission primary binding')
    require(a['fresh']['report_sha256'] == c['fresh_receipt_sha256'], 'Admission fresh binding')
    require(a['comparison']['sha256'] == sha(root/'evidence/CORE32_COMPARISON.json'), 'Admission comparison binding')
    require(a['version'] == '1.0.0', 'Unexpected release version')
    require(a['counts']['selected_source_results'] == a['counts']['selected_source_total'] == 27,
            'Selected-core admission count')
    require(a['counts']['pending_source_results'] == 0, 'Pending selected source results')
    sup_admission = {row['path']: row for row in a['supervisors']}
    for name, report in [('final19', f), ('fresh19', g)]:
        require(report['source_results_formalized'] == 27 and report['source_results_not_formalized'] == 0,
                'Gate selected scope')
        rel = f'evidence/{name}_supervisor.json'
        sup = load(root/rel)
        require(sup['status'] == 'completed' and sup['exit_code'] == 0, name + ' supervisor failed')
        require(sup_admission[rel]['sha256'] == sha(root/rel) and sup_admission[rel]['receipt'] == sup,
                name + ' admission supervisor binding')
        require(report['steps'], name + ' has no command steps')
        for step in report['steps']:
            require(step['passed'] and not step['timed_out'], name + ' failed command')
            canonical(step['log'])
            require(sha(root/'evidence'/name/step['log']) == step['log_sha256'], name + ' log mismatch')
        for rel, expected in report['local_object_sha256'].items():
            canonical(rel)
            require(sha(root/'evidence'/name/'objects'/rel) == expected, name + ' object mismatch: ' + rel)
    mods = load(root/'MODULES.json')
    require(len(mods) == c['production_object_count'] == 79, 'Wrong production module count')
    for name in mods:
        require(c['production_objects'][name]['identical'], 'Production binary difference')
        rel = name.replace('.', '/') + '.olean'
        require(f['local_object_sha256'][rel] == g['local_object_sha256'][rel] ==
                c['production_objects'][name]['final_sha256'] == c['production_objects'][name]['fresh_sha256'],
                'Production comparison binding')
    snapshot = root/'evidence/CORE32_FROZEN_SOURCE.zip'
    require(sha(snapshot) == s['sha256'] == c['source_snapshot_sha256'] ==
            a['source_snapshot_sha256'] == SNAPSHOT_SHA, 'Snapshot hash binding')
    with zipfile.ZipFile(snapshot) as z:
        names = z.namelist()
        require(z.testzip() is None, 'Snapshot CRC error')
        require(len(names) == len(set(names)) == 501 and set(names) == set(pins), 'Snapshot exact membership')
        for n in names:
            canonical(n)
            require(hashlib.sha256(z.read(n)).hexdigest() == pins[n], 'Snapshot source mismatch: ' + n)
    predecessor = root/'evidence/history18/Machine_Native_Reasoning_Lean_Core25_Source_and_Receipts.zip'
    require(predecessor.stat().st_size == 10674438 and sha(predecessor) == PREDECESSOR_SHA,
            'Intact predecessor archive mismatch')
    return {'status': 'PASS', 'source_inputs': len(pins), 'source_snapshot_sha256': SNAPSHOT_SHA,
            'production_object_count': len(mods), 'primary_sha256': c['final_receipt_sha256'],
            'fresh_sha256': c['fresh_receipt_sha256'], 'admission_sha256': sha(root/'release/ADMISSION_RECORD.json'),
            'comparison_sha256': sha(root/'evidence/CORE32_COMPARISON.json')}


def compare(root, output):
    argv = [sys.executable, '-B', str(root/'scripts/compare_rebuild.py'),
            '--final', str(root/'evidence/final19'), '--fresh', str(root/'evidence/fresh19'),
            '--snapshot', str(root/'evidence/CORE32_FROZEN_SOURCE.zip'), '--out', str(output)]
    run = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=90)
    output.with_suffix('.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    require(run.returncode == 0, 'Delivered comparison failed: ' + run.stdout + run.stderr)
    d = load(output)
    require(d['status'] == 'PASS' and all(d['comparisons'].values()), 'Delivered comparison did not pass')
    return {'status': d['status'], 'checks': len(d['comparisons']), 'sha256': sha(output),
            'production_objects': d['production_object_count']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True, help='Completed formal tree, read only')
    ap.add_argument('--out-dir', type=Path, required=True, help='New output directory outside formal root')
    ap.add_argument('--canonical-name', default=CANONICAL)
    ap.add_argument('--require-path', action='append', default=[], help='Additional required regular payload path, e.g. reader PDF')
    args = ap.parse_args()
    root = args.root.resolve(strict=True)
    out = args.out_dir.resolve()
    require(out != root and not out.is_relative_to(root), 'Output must be outside the formal tree')
    require(not out.exists(), 'Refusing existing output directory: ' + str(out))
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', args.canonical_name), 'Unsafe package root name')
    for rel in args.require_path:
        canonical(rel)
        require((root/rel).is_file() and not (root/rel).is_symlink(), 'Required payload missing: ' + rel)
    source_binding = bind_release(root)
    original = files(root)
    out.mkdir(parents=True)
    stage = out/'staging'/args.canonical_name
    stage.mkdir(parents=True)
    omitted = []
    for p in original:
        rel = p.relative_to(root)
        if rel.as_posix() == 'MANIFEST.json':
            continue
        if '__pycache__' in rel.parts or p.suffix == '.pyc':
            omitted.append({'path': rel.as_posix(), 'bytes': p.stat().st_size,
                            'sha256': sha(p), 'reason': 'regenerable Python bytecode cache'})
            continue
        require(p.suffix.lower() not in ('.ttf', '.otf', '.woff', '.woff2'),
                'Standalone font requires explicit packaging review: ' + str(p))
        dest = stage/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        require(sha(dest) == sha(p), 'Source changed during copy: ' + rel.as_posix())
    write(stage/'release/PACKAGE_CACHE_OMISSIONS.json', omitted)
    # Packaging instructions are release metadata, outside the exact frozen
    # proof-input closure. Include this portable helper in the sealed payload.
    helper = stage/'release/build_scripts/package19.py'
    helper.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), helper)
    old_start = stage/'START_HERE.txt'
    if old_start.exists():
        dest = stage/'evidence/history18/START_HERE_before_final_package.txt'
        if not dest.exists():
            shutil.copy2(old_start, dest)
    old_start.write_text('''MACHINE-NATIVE REASONING — REVIEWED MATHEMATICAL CORE — 1.0.0
All 27 selected Reviewed Core v0.2 results are formally admitted.
Full source, receipts and current proof objects are included.

Read release/REPORT.md, release/PROOF_GUIDE.md, and
release/ACCEPTED_PROGRESS_LEDGER.md. The expanded monograph is separate.

Before creating build outputs:
    python -B tools/verify_package.py

See release/RUNTIME_REPRODUCTION.md for the separately stored pinned runtime
and the executable-path adapter used on this host. See release/ARCHIVE_LAYOUT.md
for exact current and historical evidence limits.
''', encoding='utf-8')
    staged_binding = bind_release(stage)
    require(staged_binding == source_binding, 'Staged gate binding changed')
    staged_comparison = compare(stage, out/'staged_comparison.json')
    vp = module(stage/'tools/verify_package.py', 'package_integrity')
    entries = [{'path': p.relative_to(stage).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in files(stage)]
    write(stage/'MANIFEST.json', {'schema': vp.SCHEMA, 'version': '1.0.0', 'flavor': 'full', 'files': entries})
    staged_integrity = vp.verify(stage)
    archive = out/(args.canonical_name + '.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        for p in files(stage):
            z.write(p, args.canonical_name + '/' + p.relative_to(stage).as_posix())
    with tempfile.TemporaryDirectory(prefix='clean_extract_', dir=out) as tmp:
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            expected = {args.canonical_name + '/' + row['path'] for row in entries}
            expected.add(args.canonical_name + '/MANIFEST.json')
            require(len(names) == len(set(names)) and set(names) == expected, 'Archive exact membership')
            require(z.testzip() is None, 'Archive CRC error')
            for info in z.infolist():
                p = canonical(info.filename)
                require(p.parts[0] == args.canonical_name and len(p.parts) > 1, 'Unexpected archive root')
                require(stat.S_ISREG(info.external_attr >> 16), 'Nonregular archive member')
            z.extractall(tmp)
        extracted = Path(tmp)/args.canonical_name
        extracted_integrity = vp.verify(extracted)
        extracted_binding = bind_release(extracted)
        require(extracted_binding == source_binding, 'Clean extraction binding changed')
        extracted_comparison = compare(extracted, out/'extracted_comparison.json')
        require(vp.verify(extracted) == extracted_integrity, 'Checks changed clean extraction')
    require(vp.verify(stage) == staged_integrity, 'Packaging changed stage')
    require(bind_release(root) == source_binding, 'Formal input changed during packaging')
    archive_sha = sha(archive)
    receipt = {'schema': 'komorebi.machine_reasoning.reviewed_core.delivery.v1',
               'status': 'PASS', 'version': '1.0.0', 'flavor': 'full',
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'archive': archive.name, 'archive_bytes': archive.stat().st_size, 'archive_sha256': archive_sha,
               'manifest_payload_files': len(entries), 'zip_members': len(names),
               'staged_integrity': staged_integrity, 'extracted_integrity': extracted_integrity,
               'staged_comparison': staged_comparison, 'extracted_comparison': extracted_comparison,
               'source_binding': source_binding, 'exact_source_pin_closure': True,
               'clean_extraction_verified': True, 'current_compiled_objects_included': True,
               'required_payload_paths': args.require_path, 'omitted_bytecode_files': len(omitted),
               'predecessor_archive_sha256': PREDECESSOR_SHA,
               'packager_sha256': sha(Path(__file__)),
               'scope': 'Delivery integrity and completed-receipt binding, not a new Lean proof run or independent kernel.'}
    write(out/(args.canonical_name + '_Delivery_Verification.json'), receipt)
    (out/(archive.name + '.sha256')).write_text(archive_sha + '  ' + archive.name + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
