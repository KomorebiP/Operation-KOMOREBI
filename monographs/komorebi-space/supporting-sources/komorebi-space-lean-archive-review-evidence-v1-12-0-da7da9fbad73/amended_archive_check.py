#!/usr/bin/env python3
"""Read-only independent verification of the actual v1.12.0 delivery ZIP.

Does not import, run, or delegate decisions to project packaging/replay helpers.
Only the external review JSON is written. Run after packaging is complete.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import zipfile

RELEASE = 'Komorebi_Space_Lean_Continuation_v1.12.0'
PARENT = 'Komorebi_Space_Lean_Continuation_v1.11.0'
PARENT_SHA = '40a5ddecb526dcb1f60c4475e3648f2b5aa906d2b4b5070f4a8b1c59db4d83d1'
PDF_SHA = '8118e4871a705f67295f0fb2e1038466e0015420e1716a37cc33669ef6af30cb'
PROJECT = 'wr15_v1.12.0/'
RUN = PROJECT + 'integration/runs/clean_wr15_01/'
PARENT_RUN = 'limits_v1.11.0/integration/runs/clean_limits_01/'
ORIGINAL_CHECKER_SHA = 'ea1f397bc41674ea2de8784442be52020b7d5b5bd466eaa5b25c5f9979024904'
PACKAGER_SHA = '3a2015755345db474406401dca00027f8a5abc7ea8eefc543b6cf78e59959e59'
ADAPTER_SHA = 'fdcc7edf41b2c301abd13ec01041d44eee52148cbf05f2332bc39b23c5862853'
NEW_PRODUCTION_SHA = {
    'KomorebiSpace/CoordinateBasisChange.lean': '964ed871bf33db57c854b653125b9bf92416eefb5bc5df40877cd909ef366c07',
    'KomorebiSpace/CoordinateCovector.lean': '151661fac5f9ef5e2212ef41d76bf179299b5da4c5df10bf07844f18e04decfe'}
EXCLUDED_DIRS = {'build', '__pycache__', '.lake', '.git', 'runtime', 'downloads'}
ROOT_DOCUMENTS = ['README.md', 'PROGRESS_LEDGER.md', 'PROGRESS_LEDGER.json',
                  'VERIFICATION_SUMMARY.json', 'FORMAL_COVERAGE.json', 'NEXT_RESEARCH_BLOCK.md']
COMPILED_ENDINGS = ('.olean', '.olean.private', '.olean.server', '.ilean', '.pyc', '.o', '.a', '.so', '.dll', '.dylib', '.exe')
AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULES = {'KomorebiSpace.CoordinateBasisChange', 'KomorebiSpace.CoordinateCovector'}


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def digest(stream):
    result = hashlib.sha256()
    while block := stream.read(2 ** 20):
        result.update(block)
    return result.hexdigest()


def file_digest(path):
    insist(path.is_file() and all(not p.is_symlink() for p in (path, *path.parents)),
           f'Not an ordinary file or symlink ancestor: {path}')
    with path.open('rb') as stream:
        return digest(stream)


def path_is_safe(name):
    return (bool(name) and not name.startswith('/') and '\\' not in name and ':' not in name
            and all(ord(c) >= 32 and ord(c) != 127 for c in name)
            and all(p not in ('', '.', '..') for p in name.split('/')))


def is_excluded(relative):
    return any(p in EXCLUDED_DIRS for p in relative.split('/')) or relative.endswith(COMPILED_ENDINGS)


def filesystem_inventory(root, filtered=False):
    insist(root.is_dir() and not root.is_symlink(), f'Not an ordinary directory: {root}')
    found = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        base = Path(folder)
        dirs[:] = sorted(d for d in dirs if not filtered or d not in EXCLUDED_DIRS)
        for d in dirs:
            insist(not (base / d).is_symlink(), f'Directory symlink: {base / d}')
        for filename in sorted(files):
            path = base / filename
            relative = path.relative_to(root).as_posix()
            if filtered and is_excluded(relative):
                continue
            insist(path_is_safe(relative), f'Noncanonical filesystem path: {relative}')
            insist(stat.S_ISREG(path.lstat().st_mode), f'Nonregular file: {path}')
            found[relative] = file_digest(path)
    return found


class Archive:
    def __init__(self, path, top):
        self.path = path
        self.top = top + '/'
        self.sha256 = file_digest(path)
        self.zip = zipfile.ZipFile(path, 'r')
        self.files = {}
        seen, canonical = set(), set()
        for entry in self.zip.infolist():
            name = entry.filename
            insist(name not in seen, f'Duplicate ZIP member: {name}')
            seen.add(name)
            clean = name[:-1] if entry.is_dir() else name
            insist(clean not in canonical, f'File/directory ZIP collision: {name}')
            canonical.add(clean)
            insist(path_is_safe(clean), f'Unsafe ZIP path: {name}')
            insist(name == self.top or name.startswith(self.top), f'Unexpected ZIP root: {name}')
            kind = stat.S_IFMT(entry.external_attr >> 16)
            insist(kind in (0, stat.S_IFDIR if entry.is_dir() else stat.S_IFREG),
                   f'ZIP symlink or special member: {name}')
            insist(not (entry.flag_bits & 1), f'Encrypted member: {name}')
            if not entry.is_dir():
                relative = name[len(self.top):]
                insist(path_is_safe(relative), f'Unsafe payload path: {relative}')
                with self.zip.open(entry) as stream:
                    self.files[relative] = digest(stream)  # Reading to EOF checks ZIP CRC too.
        insist(self.zip.testzip() is None, 'ZIP CRC failure')
        for relative in self.files:
            pieces = relative.split('/')
            insist(not any('/'.join(pieces[:i]) in self.files for i in range(1, len(pieces))),
                   f'File used as directory in ZIP: {relative}')
        manifest = {}
        for line in self.read('SHA256SUMS.txt').decode('utf-8').splitlines():
            match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
            insist(match is not None, f'Malformed manifest line: {line!r}')
            value, relative = match.groups()
            insist(path_is_safe(relative) and relative not in manifest and relative != 'SHA256SUMS.txt',
                   f'Invalid/duplicate/self-referential manifest entry: {relative}')
            manifest[relative] = value
        insist(manifest == {n: h for n, h in self.files.items() if n != 'SHA256SUMS.txt'},
               'Manifest is not exactly the complete ZIP payload with correct hashes')

    def read(self, name):
        insist(name in self.files, f'Missing archived file: {name}')
        return self.zip.read(self.top + name)

    def json(self, name):
        return json.loads(self.read(name))

    def subset(self, prefix):
        return {n[len(prefix):]: h for n, h in self.files.items() if n.startswith(prefix)}


def strip_lean_comments(text):
    """Keep source line boundaries while excluding nested comments and strings."""
    out, pos, nesting, quoted = [], 0, 0, False
    while pos < len(text):
        pair = text[pos:pos + 2]
        if nesting:
            if pair == '/-': nesting += 1; pos += 2
            elif pair == '-/': nesting -= 1; pos += 2
            else: out.append('\n' if text[pos] == '\n' else ' '); pos += 1
        elif quoted:
            if text[pos] == '\\': out.extend('  '); pos += 2
            elif text[pos] == '"': quoted = False; out.append(' '); pos += 1
            else: out.append('\n' if text[pos] == '\n' else ' '); pos += 1
        elif pair == '/-': nesting = 1; out.extend('  '); pos += 2
        elif pair == '--':
            end = text.find('\n', pos)
            if end == -1: break
            out.extend(' ' * (end - pos)); pos = end
        elif text[pos] == '"': quoted = True; out.append(' '); pos += 1
        else: out.append(text[pos]); pos += 1
    insist(nesting == 0 and not quoted, 'Unclosed Lean comment or string in count scan')
    return ''.join(out)


def check_exact_commands(a, work, rec, post, controls):
    """Reconstruct all recorded invocations from archived inputs, without a helper."""
    run = work / RUN
    source, build = run / 'source', run / 'build'
    runtime = Path(rec['runtime'])
    lean = runtime / 'toolchain/bin/lean'
    flags = [str(lean), '-j1', '-DwarningAsError=true', '-DautoImplicit=false']
    pins = a.json('formal/pinned-dependencies.json')['packages']
    expected = [('lean_version', [str(lean), '--version'], False, [])]
    caches, dependencies = [], []
    for pin in pins:
        package = runtime / 'workspace/.lake/packages' / pin['name']
        expected.extend([
            ('pin_' + pin['name'], ['git', '-C', str(package), 'rev-parse', 'HEAD'], False, []),
            ('clean_' + pin['name'], ['git', '-C', str(package), 'diff', '--exit-code', 'HEAD', '--'], False, [])])
        cache = package / '.lake/build/lib/lean'
        cached = rec['dependency_cache_directories'][pin['name']]
        insist(cached['path'] == str(cache) and type(cached['exists']) is bool,
               'Unexpected recorded cache location: ' + pin['name'])
        if cached['exists']:
            caches.append(str(cache))
        dependencies.append({'name': pin['name'], 'expected': pin['rev'], 'actual': pin['rev']})
    insist(rec['dependencies'] == dependencies and
           rec['environment']['LEAN_PATH'] == ':'.join([str(build), *caches]),
           'Dependency pins or recorded Lean search path differ')
    for module in rec['compile_order']:
        relative = module.replace('.', '/')
        expected.append(('compile_' + module,
                         flags + ['-o', str(build / (relative + '.olean')), str(source / (relative + '.lean'))],
                         False, []))
    expected.append(('axiom_export', flags + [str(source / 'ExportAudit.lean')], False, []))
    for control in controls:
        label = 'control_' + control['path'].removeprefix('tests/').removesuffix('.lean').replace('/', '_')
        expected.append((label, flags + [str(source / control['path'])],
                         control['kind'] != 'positive', control['required_markers']))
    for pin in pins:
        package = runtime / 'workspace/.lake/packages' / pin['name']
        expected.extend([
            ('terminal_pin_' + pin['name'], ['git', '-C', str(package), 'rev-parse', 'HEAD'], False, []),
            ('terminal_clean_' + pin['name'], ['git', '-C', str(package), 'diff', '--exit-code', 'HEAD', '--'], False, [])])
    labels = [item[0] for item in expected]
    insist(labels == rec['exact_command_labels'] == post['exact_command_labels'],
           'Actual source/control inputs do not generate the recorded command list')
    insist(set(a.subset(RUN + 'logs/')) == {label + '.log' for label in labels},
           'Unrecorded or missing command log')
    insist(len(expected) == len(rec['commands']), 'Exact command count mismatch')
    for actual, (label, argv, negative, markers) in zip(rec['commands'], expected, strict=True):
        insist(actual['label'] == label and actual['argv'] == argv and actual['cwd'] == str(source),
               'Command target, arguments, or working directory changed: ' + label)
        insist(actual['log'] == 'logs/' + label + '.log' and actual['expected_rejection'] is negative
               and actual['required_markers'] == markers, 'Command expectation changed: ' + label)
        if label.startswith('pin_') or label.startswith('terminal_pin_'):
            pin = next(pin for pin in pins if label in ('pin_' + pin['name'], 'terminal_pin_' + pin['name']))
            insist(a.read(RUN + actual['log']).decode().strip() == pin['rev'], 'Revision log mismatch: ' + label)
    version = a.read(RUN + 'logs/lean_version.log').decode().strip()
    insist(version == rec['lean_version'] and '4.34.0-rc2' in version and
           '6a10ac8c22beadecabdbb0919c2b50214762f91d' in version, 'Compiler version identity mismatch')
    snapshot = a.json(RUN + 'runtime_snapshot.json')
    insist(snapshot['file_sha256']['toolchain/bin/lean'] == rec['lean_binary_sha256'],
           'Runtime inventory and receipt bind different compiler bytes')
    adapter = rec.get('executable_path_adapter')
    if adapter:
        insist(Path(adapter['path']).relative_to(runtime).as_posix() == 'compat/app_path.so' and
               adapter['sha256'] == ADAPTER_SHA and
               rec['environment'].get('LD_PRELOAD') == adapter['path'], 'Runtime adapter binding mismatch')
    else:
        insist('LD_PRELOAD' not in rec['environment'], 'Undeclared runtime adapter')
    objects = rec['object_sha256']
    insist(objects == rec['postcompile_object_sha256'] == post['object_sha256'] and
           set(objects) == {m.replace('.', '/') + '.olean' for m in rec['compile_order']},
           'Bound final compiled-object inventory disagrees or is incomplete')


def verify(work, archive_path, report):
    checks = report['checks']
    a = Archive(archive_path, RELEASE)
    report.update(archive=str(archive_path), archive_sha256=a.sha256,
                  archive_bytes=archive_path.stat().st_size, payload_files=len(a.files) - 1,
                  total_archive_files_with_manifest=len(a.files), manifest_sha256=a.files['SHA256SUMS.txt'])
    checks.append('Actual ZIP has safe unique regular-file paths, correct CRC, and complete SHA-256 manifest.')
    checker_name = PROJECT + 'reviews/archive/independent_archive_check.py'
    freeze = a.json(PROJECT + 'reviews/archive/FROZEN_CHECKER.json')
    insist(a.files[checker_name] == ORIGINAL_CHECKER_SHA == freeze['checker_sha256'],
           'Archived original checker differs from its pinned frozen revision')
    report['original_frozen_checker_sha256'] = ORIGINAL_CHECKER_SHA
    expanded = archive_path.with_suffix('')
    insist(filesystem_inventory(expanded) == a.files, 'Expanded release differs from actual ZIP')
    parent = Archive(work / 'recovery' / (PARENT + '.zip'), PARENT)
    insist(parent.sha256 == PARENT_SHA and len(parent.files) == 5863, 'Wrong predecessor archive identity/count')
    insist(filesystem_inventory(work / 'recovery/v1.11.0' / PARENT) == parent.files,
           'Expanded predecessor differs from the pinned parent ZIP')
    insist(a.subset('inherited_v1.11.0/') == parent.files, 'Predecessor files not preserved byte-for-byte')
    pdf = 'inherited_v1.11.0/inherited_v1.10.0/publication/Komorebi_Space_Monograph_v1.10.0.pdf'
    insist(a.files.get(pdf) == PDF_SHA, 'Historical v1.10.0 PDF identity changed')
    insist(all(not n.lower().endswith('.pdf') or n.startswith('inherited_v1.11.0/') for n in a.files),
           'Newly relabeled PDF outside inherited history')
    insist(not any(n.endswith(COMPILED_ENDINGS) or
                   (not n.startswith('inherited_v1.11.0/') and
                    any(p in EXCLUDED_DIRS for p in n.split('/'))) for n in a.files),
           'Compiled payload, or excluded directory outside pinned inherited history, present')
    report.update(parent_archive_sha256=parent.sha256, parent_files_preserved=5863,
                  historical_pdf_sha256=a.files[pdf], new_pdf_claimed=False)
    checks.append('All 5,863 pinned predecessor files preserved; historical PDF identity unchanged; no new PDF or compiled objects.')
    insist(a.subset(PROJECT) == filesystem_inventory(work / 'wr15_v1.12.0', filtered=True),
           'Current project evidence omitted, changed, or added during packaging')
    for name in ROOT_DOCUMENTS:
        insist(a.files[name] == a.files[PROJECT + name], f'Root release document differs: {name}')
    expected_top = set(ROOT_DOCUMENTS) | {'SHA256SUMS.txt', 'formal', 'wr15_v1.12.0', 'inherited_v1.11.0'}
    insist({n.split('/')[0] for n in a.files} == expected_top, 'Unexpected/missing top-level release content')
    checks.append('Current project evidence retained and all six root release documents match its accepted copies.')

    rec = a.json(RUN + 'receipt.json')
    post = a.json(RUN + 'postflight.json')
    summary = a.json('VERIFICATION_SUMMARY.json')
    ledger = a.json('PROGRESS_LEDGER.json')
    coverage = a.json('FORMAL_COVERAGE.json')
    receipt_sha, post_sha = a.files[RUN + 'receipt.json'], a.files[RUN + 'postflight.json']
    insist(rec['status'] == post['status'] == summary['status'] == coverage['status'] == 'PASS', 'Non-PASS acceptance evidence')
    insist(rec['schema'] == 'komorebi-space-wr15-clean-replay-v1' and
           post['schema'] == 'komorebi-space-wr15-postflight-v1', 'Wrong run schemas')
    insist(rec['label'] == 'clean_wr15_01' and rec['attempt_number'] == 1, 'Wrong accepted run identity')
    insist(ledger['status'] == 'ACCEPTED', 'Release ledger not accepted')
    for item in (post, summary, ledger):
        field = 'run_receipt_sha256' if item is post else 'formal_receipt_sha256'
        insist(item[field] == receipt_sha, 'Acceptance binds a different receipt')
    for item in (summary, ledger):
        insist(item['postflight_sha256'] == post_sha, 'Acceptance binds a different postflight')
    insist(post['gates'] and all(v is True for v in post['gates'].values()), 'Failed postflight gate')
    insist(rec['lean_executed'] is True and rec['clean_project_build'] is True and rec['initial_project_objects'] == {},
           'No clean Lean execution evidence')
    insist(rec['compile_policy'] == {'autoImplicit': False, 'threads': 1, 'warningAsError': True}, 'Compiler policy changed')
    for field in ('source_unchanged_during_run', 'runtime_unchanged_during_run', 'helpers_unchanged_during_run',
                  'objects_unchanged_after_compile', 'inherited_declarations_preserved'):
        insist(rec[field] is True, f'Failed replay identity gate: {field}')
    source = a.subset('formal/')
    insist(source == a.subset(RUN + 'source/') == rec['source_snapshot_sha256'] == post['source_snapshot_sha256'],
           'Current formal tree differs from the accepted source snapshot')
    parent_source = parent.subset('formal/')
    insist(all(source.get(n) == h for n, h in NEW_PRODUCTION_SHA.items()),
           'New production source differs from its independently frozen identity')
    inherited_production = {n: h for n, h in parent_source.items() if n.startswith('KomorebiSpace/') and n.endswith('.lean')}
    insist(len(inherited_production) == 151 and all(source.get(n) == h for n, h in inherited_production.items()),
           'An inherited production module changed in the current formal tree')
    inventory_name = PROJECT + 'integration/assemblies/' + Path(rec['assembly_path']).name + '/inventory.json'
    inventory = a.json(inventory_name)
    insist(a.files[inventory_name] == rec['inventory_sha256'] == post['inventory_sha256'] == summary['inventory_sha256'],
           'Assembly hash mismatch')
    insist(inventory['project_file_sha256'] == source, 'Assembly source inventory differs')
    insist(a.subset(inventory_name.removesuffix('inventory.json') + 'source/') == source,
           'Archived assembly sources differ from the accepted snapshot')
    allowed_changes = {'KomorebiSpaceCombined.lean', 'ExportAudit.lean', 'control_manifest.json',
                       'new_modules.txt', 'type_modules.txt', 'wanted_modules.txt', 'parent_declarations.json'}
    insist(set(inventory['allowed_inherited_changes']) == allowed_changes and
           all(source.get(n) == h for n, h in parent_source.items() if n not in allowed_changes),
           'Inherited source/control payload changed outside the exact allowlist')
    insist(a.read('formal/KomorebiSpaceCombined.lean') == parent.read('formal/KomorebiSpaceCombined.lean') +
           ''.join('import ' + m + '\n' for m in rec['new_modules']).encode(),
           'Combined root changed beyond the two additive imports')
    insist(a.subset(PROJECT + 'formal/') == inventory['overlay_input_sha256'] == a.json(PROJECT + 'records/FROZEN_OVERLAY.json')['source_sha256'],
           'Frozen overlay identity mismatch')
    runtime_sha = a.files[RUN + 'runtime_snapshot.json']
    insist(runtime_sha == rec['runtime_snapshot_sha256'] == post['runtime_snapshot_sha256'] == summary['runtime_snapshot_sha256'],
           'Archived runtime inventory is not the reviewed inventory')
    report.update(formal_receipt_sha256=receipt_sha, postflight_sha256=post_sha,
                  source_snapshot_files=len(source), runtime_snapshot_sha256=runtime_sha)
    checks.append('Formal tree, frozen overlay, assembly, runtime inventory, receipt and postflight bind the same accepted replay.')

    helpers = a.json(PROJECT + 'reviews/reviewed_helpers.json')
    actual_helpers = a.subset(PROJECT + 'integration/scripts/')
    insist(helpers['status'] == 'PASS', 'Helper review not passed')
    insist(actual_helpers == helpers['files'] == rec['verifier_input_sha256'] == inventory['helpers_sha256'] == post['reviewed_verifier_sha256'],
           'Exact reviewed helper identities differ')
    insist(source['ExportAudit.lean'] == actual_helpers['ExportAudit.lean'],
           'Executed export helper differs from the reviewed helper')
    insist(helpers['postflight_sha256'] == a.files[PROJECT + 'integration/postflight/validate.py'] == post['validator_sha256'],
           'Exact reviewed postflight identity differs')
    insist(a.files[PROJECT + 'reviews/reviewed_helpers.json'] == post['review_manifest_sha256'], 'Postflight review manifest mismatch')
    insist(rec['reviewed_helpers_sha256'] == post['review_manifest_sha256'] and
           rec['postflight_sha256'] == helpers['postflight_sha256'], 'Replay review identity mismatch')
    insist(datetime.fromisoformat(helpers['reviewed_utc']) <= datetime.fromisoformat(rec['started_utc']),
           'Helper review did not precede execution')
    evidence = ledger['acceptance_evidence_sha256']
    insist(evidence == summary['acceptance_evidence_sha256'], 'Summary/ledger acceptance evidence mismatch')
    required = {'reviews/WR15_MATH_AUDIT.md', 'reviews/VERIFIER_REVIEW.md', 'reviews/reviewed_helpers.json',
                'reviews/PACKAGING_SCRIPT_REVIEW.md', 'records/FINAL_AUDIT_SIGNOFF.json', 'formal/tests/control_manifest.json'}
    required.add('integration/postflight/validate.py')
    required.update('integration/scripts/' + n for n in helpers['files'])
    required.update(RUN.removeprefix(PROJECT) + n for n in
                    ('receipt.json', 'postflight.json', 'axioms.json', 'new_declarations.json',
                     'declarations_sorted.json', 'runtime_snapshot.json'))
    insist(required <= evidence.keys(), 'Required final review missing from accepted evidence')
    for name, value in evidence.items():
        insist(a.files[PROJECT + name] == value, 'Changed acceptance evidence: ' + name)
    signoff = a.json(PROJECT + 'records/FINAL_AUDIT_SIGNOFF.json')
    insist(signoff['status'] == 'PASS' and signoff['formal_receipt_sha256'] == receipt_sha and signoff['postflight_sha256'] == post_sha,
           'Final coordinator signoff does not bind the accepted replay')
    for name, value in signoff['review_sha256'].items():
        insist(a.files[PROJECT + name] == value, 'Changed signed-off review: ' + name)
    packaging_sha = a.files[PROJECT + 'packaging/package_release.py']
    insist(packaging_sha == PACKAGER_SHA, 'Packaging script differs from the pinned root-reviewed revision')
    insist(packaging_sha in a.read(PROJECT + 'reviews/PACKAGING_SCRIPT_REVIEW.md').decode(), 'Exact packaging script not reviewed')
    insist(ledger['review_verdicts'] == {'mathematics': 'PASS', 'verifier': 'PASS', 'packaging_script': 'PASS'},
           'Final review verdicts are not all accepted')
    verifier_review = a.read(PROJECT + 'reviews/VERIFIER_REVIEW.md').decode()
    insist(all(value in verifier_review for value in (receipt_sha, post_sha, post['review_manifest_sha256'])),
           'Final verifier review does not bind the accepted receipt, postflight and helper manifest')
    checks.append('All helpers and final acceptance reviews retain their exact reviewed identities.')

    commands = rec['commands']
    insist(len(commands) == post['command_count'] == summary['recorded_commands'], 'Final command count disagreement')
    labels = [c['label'] for c in commands]
    insist(len(set(labels)) == len(labels) and labels == rec['exact_command_labels'] == post['exact_command_labels'], 'Command inventory/order mismatch')
    insist({c['log']: c['log_sha256'] for c in commands} == post['command_log_sha256'], 'Postflight command logs differ')
    for c in commands:
        insist(c['passed'] is True and c['timeout'] is False, 'Failed/timed out command: ' + c['label'])
        insist(path_is_safe(c['log']) and a.files[RUN + c['log']] == c['log_sha256'], 'Changed command log: ' + c['label'])
        if c['expected_rejection']:
            insist(c['exit_code'] == 1, 'Negative command has wrong exit status: ' + c['label'])
            log = a.read(RUN + c['log']).decode('utf-8')
            insist(c['required_markers'] and all(marker in log for marker in c['required_markers']), 'Required rejection diagnostic missing: ' + c['label'])
            infrastructure = ('unknown module', 'unknown identifier', 'unknown constant', 'object file',
                              'failed to load', 'no such file', 'not found', 'cannot execute',
                              'segmentation fault', 'stack overflow', 'maximum recursion depth',
                              'maximum number of heartbeats', 'out of memory', 'failed to synthesize')
            insist('error:' in log.lower() and not any(x in log.lower() for x in infrastructure),
                   'Infrastructure failure disguised as an intended rejection: ' + c['label'])
        else:
            insist(c['exit_code'] == 0, 'Positive command failed: ' + c['label'])
    controls = a.json('formal/control_manifest.json')['controls']
    insist(controls == rec['controls'] == inventory['controls'], 'Control manifests differ')
    counts = dict(Counter(c['kind'] for c in controls))
    insist(len(controls) == summary['control_files'] and counts == summary['controls'],
           'Positive/negative/policy control counts disagree')
    parent_controls = parent.json('formal/control_manifest.json')['controls']
    insist(len(parent_controls) == 39 and [c for c in controls if c['scope'] != 'wr15'] == parent_controls,
           'Inherited controls changed')
    insist({c['path'] for c in controls} == {n for n in source if n.startswith('tests/') and n.endswith('.lean')},
           'A control source is missing from the command inventory')
    insist(all(c['path'] in source for c in controls), 'Control source missing')
    for control in controls:
        matches = [c for c in commands if any(arg.endswith('/source/' + control['path']) for arg in c['argv'])]
        insist(len(matches) == 1, 'Control does not have exactly one recorded compiler invocation: ' + control['path'])
        command = matches[0]
        insist(command['expected_rejection'] == (control['kind'] != 'positive')
               and command['required_markers'] == control['required_markers'], 'Control invocation policy differs from manifest')
        insist({'-j1', '-DwarningAsError=true', '-DautoImplicit=false'} <= set(command['argv']), 'Control compiler flags differ')
    production = [n for n in source if n.startswith('KomorebiSpace/') and n.endswith('.lean')]
    roots = [name + '.lean' for name in rec['entrypoints']]
    insist(len(production) == rec['production_modules'] == summary['production_modules'] ==
           len(inherited_production) + len(NEW_MODULES) and len(roots) == 3, 'Production/root count mismatch')
    compiled = production + roots
    insist({n: source[n] for n in compiled} == rec['source_sha256'] and
           len(compiled) == rec['compile_targets'] == summary['compile_targets'], 'Compilation target mismatch')
    order = rec['compile_order']
    insist(len(order) == len(set(order)) == len(compiled) and
           {m.replace('.', '/') + '.lean' for m in order} == set(compiled), 'Compile order omits or adds source')
    insist(a.read('formal/wanted_modules.txt').decode().splitlines() == order and
           set(a.read('formal/new_modules.txt').decode().splitlines()) == NEW_MODULES and
           NEW_MODULES <= set(a.read('formal/type_modules.txt').decode().splitlines()), 'Exporter input lists disagree')
    for field in ('compile_order', 'source_sha256', 'compile_targets', 'production_modules', 'entrypoints', 'new_modules', 'controls'):
        insist(rec[field] == inventory[field], 'Receipt/assembly disagreement: ' + field)
    check_exact_commands(a, work, rec, post, controls)
    insist(set(rec['new_modules']) == NEW_MODULES, 'Unexpected new module inventory')
    explicit = sum(len(re.findall(r'\b(?:theorem|lemma)\s+', strip_lean_comments(a.read('formal/' + n).decode()))) for n in compiled)
    insist(explicit == rec['explicit_theorem_lemma_count'] == summary['explicit_theorem_lemma_count'], 'Explicit theorem total mismatch')
    report.update(recorded_commands=len(commands), controls=counts, control_files=len(controls),
                  production_modules=len(production), compile_targets=len(compiled), explicit_theorem_lemma_count=explicit)
    checks.append(f'All {len(commands)} recorded commands/log hashes/rejection markers and {len(controls)} controls agree; {len(production)} modules plus three roots contain {explicit} explicit theorems.')

    audit = a.json(RUN + 'axioms.json')
    rows = audit['declarations']
    byname = {row['name']: row for row in rows}
    insist(len(byname) == len(rows) == audit['count'] == rec['axiom_declarations'] == post['axiom_declarations'] == summary['axiom_declarations'], 'Declaration census mismatch')
    insist(f'Cumulative declaration/axiom audit passed: {len(rows)} declarations' in
           a.read(RUN + 'logs/axiom_export.log').decode(), 'Audit log does not report the exported declaration count')
    insist(audit['unexpected'] == [] and all(r['unsafe'] is False and set(r['axioms']) <= AXIOMS for r in rows), 'Unsafe declaration/unapproved axiom')
    insist(sorted(set().union(*(set(r['axioms']) for r in rows))) == rec['axiom_union'] == sorted(AXIOMS), 'Axiom union mismatch')
    insist(a.files[RUN + 'axioms.json'] == rec['axiom_report_sha256'] == post['axiom_report_sha256'] == summary['axiom_report_sha256'], 'Axiom report hash mismatch')
    parent_rows = parent.json(PARENT_RUN + 'axioms.json')['declarations']
    fields = ('name', 'kind', 'module', 'unsafe')
    def signature(row):
        return tuple(row[k] for k in fields) + (tuple(sorted(row['axioms'])),)
    insist(len(parent_rows) == rec['parent_declarations'] == summary['inherited_declarations'] == 4982, 'Parent declaration count mismatch')
    insist(all(r['name'] in byname and signature(r) == signature(byname[r['name']]) for r in parent_rows), 'Inherited declaration changed/missing')
    baseline = a.json('formal/parent_declarations.json')
    insist(sorted(map(signature, baseline['declarations'])) == sorted(map(signature, parent_rows)), 'Copied parent declaration catalogue is not the pinned predecessor catalogue')
    parent_run = PARENT_RUN
    for key, filename in [('parent_receipt_sha256', 'receipt.json'), ('parent_postflight_sha256', 'postflight.json'),
                          ('parent_axiom_report_sha256', 'axioms.json')]:
        insist(baseline[key] == rec[key] == parent.files[parent_run + filename], 'Parent evidence identity mismatch: ' + key)
    new = sorted((row for row in rows if row['module'] in NEW_MODULES), key=lambda row: row['name'])
    insist(new == a.json(RUN + 'new_declarations.json'), 'New declaration report differs from full export')
    insist(len(new) == rec['new_axiom_declarations'] == post['new_axiom_declarations'] == summary['new_axiom_declarations'], 'New exported declaration count mismatch')
    insist(len(rows) == len(parent_rows) + len(new), 'Unexpected unaccounted declaration')
    insist(all(row.get('type_mode') == 'full' and row['type'].strip() and '⋯' not in row['type'] for row in new), 'Missing/truncated full new type')
    insist(sorted(rows, key=lambda r: (r['module'], r['name'])) == a.json(RUN + 'declarations_sorted.json'), 'Sorted declaration report mismatch')
    public = []
    for module in sorted(NEW_MODULES):
        text = strip_lean_comments(a.read('formal/' + module.replace('.', '/') + '.lean').decode())
        namespaces = re.findall(r'^namespace\s+(\S+)', text, re.M)
        insist(namespaces == ['KomorebiSpace.CoordinateCovector'], 'Unexpected public declaration namespace')
        declarations = re.findall(r'^\s*(?:noncomputable\s+)?(theorem|lemma|def)\s+(\S+)', text, re.M)
        public.extend((namespaces[0] + '.' + name, kind) for kind, name in declarations)
        insist(all(byname.get(namespaces[0] + '.' + name, {}).get('module') == module for _, name in declarations),
               'A public declaration is exported from the wrong module')
    theorems = sum(kind in {'theorem', 'lemma'} for _, kind in public)
    insist(theorems == summary['new_explicit_theorems'] and len(public) == summary['new_named_public_declarations'], 'New explicit/public declaration counts differ')
    insist(all(name in byname and byname[name]['kind'] == ('definition' if kind == 'def' else 'theorem') for name, kind in public), 'A new named declaration lacks the expected export')
    type_sha = a.files[RUN + 'new_declarations.json']
    insist(type_sha == summary['new_declarations_sha256'], 'Accepted complete type report hash mismatch')
    math = a.read(PROJECT + 'reviews/WR15_MATH_AUDIT.md').decode()
    for value in [receipt_sha, post_sha, a.files[RUN + 'axioms.json'], type_sha] + [source[m.replace('.', '/') + '.lean'] for m in sorted(NEW_MODULES)]:
        insist(value in math, 'Final mathematical review lacks required source/export/type/receipt hash')
    insist(not re.search(r'Primary verdict[^\n]*(?:incomplete|provisional|pending)', math[:2500], re.I), 'Mathematical review still carries a provisional primary verdict')
    report.update(axiom_declarations=len(rows), inherited_declarations_preserved=len(parent_rows),
                  new_exported_declarations=len(new), new_explicit_theorems=theorems,
                  new_named_public_declarations=len(public), new_declarations_sha256=type_sha,
                  axiom_report_sha256=a.files[RUN + 'axioms.json'], acceptance_evidence_sha256=evidence,
                  reviewed_helper_sha256=actual_helpers, postflight_validator_sha256=post['validator_sha256'])
    checks.append(f'All 4,982 inherited declaration signatures are preserved; all {len(new)} new declarations have full types; {theorems} explicit theorems and {len(public)} public declarations are present and final mathematical review binds their exact evidence.')

    complete = [f'WR{i:02}' for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16]]
    written = ['WR10', 'WR11', 'WR12']
    insist(coverage['complete'] == ledger['complete_formal_groups'] == complete and coverage['partial'] == ledger['partial_formal_groups'] == [], 'Complete/partial coverage mismatch')
    insist(coverage['written_only'] == ledger['open_formal_groups'] == written, 'Written-only coverage mismatch')
    insist(coverage['formal_receipt_sha256'] == receipt_sha, 'Coverage refers to a different receipt')
    report.update(complete_formal_groups=complete, partial_formal_groups=[], written_only_formal_groups=written)
    checks.append('Coverage is exactly 13 complete groups, zero partial groups, and WR10–WR12 written-only.')

    delivery_path = archive_path.parent / 'Komorebi_Space_Lean_Delivery_Verification_v1.12.0.json'
    delivery = json.loads(delivery_path.read_text())
    insist(delivery['status'] == 'PASS' and delivery['archive_sha256'] == a.sha256 and delivery['archive_bytes'] == archive_path.stat().st_size, 'External delivery record describes another archive')
    for key in ('manifest_sha256', 'formal_receipt_sha256', 'postflight_sha256', 'axiom_report_sha256'):
        insist(delivery[key] == report[key], 'Delivery binding mismatch: ' + key)
    insist(delivery['acceptance_evidence_sha256'] == evidence and delivery['packaging_script_sha256'] == packaging_sha, 'Delivery review/script evidence mismatch')
    insist(delivery['type_audit_sha256'] == evidence['reviews/WR15_MATH_AUDIT.md'], 'Delivery mathematical audit mismatch')
    for key, expected in [('payload_files', len(a.files)-1), ('total_archive_files_with_manifest', len(a.files)),
                          ('parent_files_preserved_including_manifest', 5863), ('command_count', len(commands)), ('control_count', len(controls)),
                          ('production_modules', len(production)), ('compile_targets', len(compiled)), ('axiom_declarations', len(rows)), ('new_axiom_declarations', len(new))]:
        insist(delivery[key] == expected, 'Delivery count mismatch: ' + key)
    insist(delivery['new_pdf_claimed'] is False and delivery['compiled_objects_included'] is False and delivery['portable_runtime_included'] is False, 'Incorrect delivery scope claims')
    insist(delivery['parent_archive_sha256'] == parent.sha256 and delivery['parent_payload_files'] == 5862 and
           delivery['parent_expanded_compared_with_pinned_zip_bytes'] is True and
           delivery['current_formal_source_byte_identical'] is True, 'Delivery ancestry/source assertions disagree')
    insist(delivery['crc'] == delivery['payload_sha256'] == 'PASS' and
           delivery['new_modules'] == rec['new_modules'] and
           delivery['explicit_theorem_lemma_count'] == explicit, 'Delivery scope/count assertions disagree')
    progress = archive_path.parent / 'Komorebi_Space_Lean_Progress_v1.12.0.md'
    insist(file_digest(progress) == a.files['PROGRESS_LEDGER.md'] == delivery['progress_sha256'], 'External progress file differs')
    insist(file_digest(archive_path) == a.sha256, 'Archive changed during independent review')
    report.update(delivery_verification_sha256=file_digest(delivery_path), packaging_script_sha256=packaging_sha,
                  external_progress_sha256=file_digest(progress), zip_crc='PASS', payload_sha256='PASS')
    checks.append('External delivery verification binds this actual ZIP, accepted evidence/reviews and all final counts; external progress matches.')
    a.zip.close()
    parent.zip.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    work = args.workspace.resolve()
    archive = args.archive or work / 'output' / (RELEASE + '.zip')
    output = args.report or work / 'output/Komorebi_Space_Lean_Independent_Archive_Review_v1.12.0.json'
    report = {'schema': 'komorebi-space-independent-archive-review-v1', 'status': 'FAIL',
              'reviewer': '/root/wr15_coordinates (artifact identity review only)', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'checker_sha256': file_digest(Path(__file__).resolve()), 'checks': [],
              'independence': 'Independent standard-library implementation; packaging/replay helpers were neither imported nor executed.',
              'scope': 'Actual archive identities, complete ancestry, accepted source/evidence binding, counts, and published coverage.',
              'limitations': ['No second Lean compilation or runtime-cache rehash; those operations are covered by the bound independently reviewed postflight.',
                              'The checker author authored CoordinateCovector.lean. This is explicitly not an independent mathematical review of that proof; a separate reviewer owns the mathematical audit whose identity is checked here.',
                              'Inherited declaration preservation compares name, kind, module, unsafe flag and axiom sets; it is not a proof-expression identity check.']}
    try:
        evidence = Path(__file__).resolve().parent
        amendment = json.loads((evidence / 'AMENDMENT.json').read_text())
        insist(amendment['original_checker_sha256'] == ORIGINAL_CHECKER_SHA and
               amendment['amended_checker_sha256'] == report['checker_sha256'],
               'External checker amendment identities disagree')
        for name, value in amendment['evidence_sha256'].items():
            insist(path_is_safe(name) and file_digest(evidence / name) == value,
                   'External amendment evidence changed: ' + name)
        approval = json.loads((evidence / 'ROOT_REVIEW.json').read_text())
        insist(approval['status'] == 'PASS' and approval['amended_checker_sha256'] == report['checker_sha256']
               and approval['amendment_sha256'] == file_digest(evidence / 'AMENDMENT.json'),
               'External amendment has not received matching root review')
        report['prior_failed_review'] = {'status': 'FAIL', 'path': str(evidence / 'attempt_001_FAIL.json'),
            'sha256': file_digest(evidence / 'attempt_001_FAIL.json')}
        report['checker_amendment'] = {'reason': amendment['reason'], 'evidence_directory': str(evidence),
            'amendment_record_sha256': file_digest(evidence / 'AMENDMENT.json'),
            'root_review_sha256': file_digest(evidence / 'ROOT_REVIEW.json'),
            'original_checker_sha256': ORIGINAL_CHECKER_SHA, 'amended_checker_sha256': report['checker_sha256']}
        verify(work, archive, report)
        report['status'] = 'PASS'
    except Exception as error:
        report['failure'] = f'{type(error).__name__}: {error}'
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    insist(not output.resolve().is_relative_to(work / 'wr15_v1.12.0') and not output.resolve().is_relative_to(archive.with_suffix('')),
           'Review report must remain outside the frozen project and archive tree')
    insist(output.parent.is_dir() and not output.exists() and
           all(not p.is_symlink() for p in (output, *output.parents)),
           'External review destination must be new in an existing directory')
    with output.open('x') as stream:
        stream.write(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': report['status'], 'checks_passed': len(report['checks']),
                      'report': str(output), 'failure': report.get('failure')}, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
