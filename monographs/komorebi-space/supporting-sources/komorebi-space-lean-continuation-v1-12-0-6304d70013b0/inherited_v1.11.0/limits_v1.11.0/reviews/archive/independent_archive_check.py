#!/usr/bin/env python3
"""Read-only independent verification of the actual v1.11.0 delivery ZIP.

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

RELEASE = 'Komorebi_Space_Lean_Continuation_v1.11.0'
PARENT = 'Komorebi_Space_Monograph_v1.10.0'
PARENT_SHA = 'df099ee00bf5487b2f9b108f4209e6951c9e18b79494e3f4682dd779cb0ed704'
PDF_SHA = '8118e4871a705f67295f0fb2e1038466e0015420e1716a37cc33669ef6af30cb'
PROJECT = 'limits_v1.11.0/'
RUN = PROJECT + 'integration/runs/clean_limits_01/'
ROOT_DOCUMENTS = ['README.md', 'PROGRESS_LEDGER.md', 'PROGRESS_LEDGER.json',
                  'VERIFICATION_SUMMARY.json', 'FORMAL_COVERAGE.json', 'NEXT_RESEARCH_BLOCK.md']
COMPILED_ENDINGS = ('.olean', '.olean.private', '.olean.server', '.ilean', '.pyc', '.o', '.a', '.so')
AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULES = {'KomorebiSpace.RegularizationLimits', 'KomorebiSpace.RegularizationStrongLimit',
               'KomorebiSpace.RegularizationNoiseLimits'}


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def digest(stream):
    result = hashlib.sha256()
    while block := stream.read(2 ** 20):
        result.update(block)
    return result.hexdigest()


def file_digest(path):
    insist(path.is_file() and not path.is_symlink(), f'Not an ordinary file: {path}')
    with path.open('rb') as stream:
        return digest(stream)


def path_is_safe(name):
    return (bool(name) and not name.startswith('/') and '\\' not in name and ':' not in name
            and all(ord(c) >= 32 and ord(c) != 127 for c in name)
            and all(p not in ('', '.', '..') for p in name.split('/')))


def is_excluded(relative):
    return any(p in {'build', '__pycache__'} for p in relative.split('/')) or relative.endswith(COMPILED_ENDINGS)


def filesystem_inventory(root, filtered=False):
    insist(root.is_dir() and not root.is_symlink(), f'Not an ordinary directory: {root}')
    found = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        base = Path(folder)
        dirs[:] = sorted(d for d in dirs if not filtered or d not in {'build', '__pycache__'})
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
        seen = set()
        for entry in self.zip.infolist():
            name = entry.filename
            insist(name not in seen, f'Duplicate ZIP member: {name}')
            seen.add(name)
            clean = name[:-1] if entry.is_dir() else name
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


def verify(work, archive_path, report):
    checks = report['checks']
    a = Archive(archive_path, RELEASE)
    report.update(archive=str(archive_path), archive_sha256=a.sha256,
                  archive_bytes=archive_path.stat().st_size, payload_files=len(a.files) - 1,
                  total_archive_files_with_manifest=len(a.files), manifest_sha256=a.files['SHA256SUMS.txt'])
    checks.append('Actual ZIP has safe unique regular-file paths, correct CRC, and complete SHA-256 manifest.')
    expanded = archive_path.with_suffix('')
    insist(filesystem_inventory(expanded) == a.files, 'Expanded release differs from actual ZIP')
    parent = Archive(work / 'output' / (PARENT + '.zip'), PARENT)
    insist(parent.sha256 == PARENT_SHA and len(parent.files) == 4828, 'Wrong predecessor archive identity/count')
    insist(a.subset('inherited_v1.10.0/') == parent.files, 'Predecessor files not preserved byte-for-byte')
    pdf = 'inherited_v1.10.0/publication/Komorebi_Space_Monograph_v1.10.0.pdf'
    insist(a.files.get(pdf) == PDF_SHA, 'Historical v1.10.0 PDF identity changed')
    insist(all(not n.lower().endswith('.pdf') or n.startswith('inherited_v1.10.0/') for n in a.files),
           'Newly relabeled PDF outside inherited history')
    insist(not any(is_excluded(n) for n in a.files), 'Compiled/build/cache payload present')
    report.update(parent_archive_sha256=parent.sha256, parent_files_preserved=4828,
                  historical_pdf_sha256=a.files[pdf], new_pdf_claimed=False)
    checks.append('All 4,828 pinned predecessor files preserved; historical PDF identity unchanged; no new PDF or compiled objects.')
    insist(a.subset(PROJECT) == filesystem_inventory(work / 'limits_v1.11.0', filtered=True),
           'Current project evidence omitted, changed, or added during packaging')
    for name in ROOT_DOCUMENTS:
        insist(a.files[name] == a.files[PROJECT + name], f'Root release document differs: {name}')
    expected_top = set(ROOT_DOCUMENTS) | {'SHA256SUMS.txt', 'formal', 'limits_v1.11.0', 'inherited_v1.10.0'}
    insist({n.split('/')[0] for n in a.files} == expected_top, 'Unexpected/missing top-level release content')
    checks.append('Current project evidence retained and all six root release documents match its accepted copies.')

    rec = a.json(RUN + 'receipt.json')
    post = a.json(RUN + 'postflight.json')
    summary = a.json('VERIFICATION_SUMMARY.json')
    ledger = a.json('PROGRESS_LEDGER.json')
    coverage = a.json('FORMAL_COVERAGE.json')
    receipt_sha, post_sha = a.files[RUN + 'receipt.json'], a.files[RUN + 'postflight.json']
    insist(rec['status'] == post['status'] == summary['status'] == coverage['status'] == 'PASS', 'Non-PASS acceptance evidence')
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
    inherited_production = {n: h for n, h in parent_source.items() if n.startswith('KomorebiSpace/') and n.endswith('.lean')}
    insist(len(inherited_production) == 148 and all(source.get(n) == h for n, h in inherited_production.items()),
           'An inherited production module changed in the current formal tree')
    inventory_name = PROJECT + 'integration/assemblies/' + Path(rec['assembly_path']).name + '/inventory.json'
    inventory = a.json(inventory_name)
    insist(a.files[inventory_name] == rec['inventory_sha256'] == post['inventory_sha256'] == summary['inventory_sha256'],
           'Assembly hash mismatch')
    insist(inventory['project_file_sha256'] == source, 'Assembly source inventory differs')
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
    insist(helpers['postflight_sha256'] == a.files[PROJECT + 'integration/postflight/validate.py'] == post['validator_sha256'],
           'Exact reviewed postflight identity differs')
    insist(a.files[PROJECT + 'reviews/reviewed_helpers.json'] == post['review_manifest_sha256'], 'Postflight review manifest mismatch')
    for name, value in helpers['reviewed_new_source_sha256'].items():
        insist(source['KomorebiSpace/' + name] == value, 'Review/source identity mismatch: ' + name)
    for name, value in helpers['reviewed_new_control_source_sha256'].items():
        insist(a.files[PROJECT + 'formal/tests/' + name] == value, 'Review/control identity mismatch: ' + name)
    evidence = ledger['acceptance_evidence_sha256']
    insist(evidence == summary['acceptance_evidence_sha256'], 'Summary/ledger acceptance evidence mismatch')
    required = {'reviews/WR08_WR09_WR16_MATH_AUDIT.md', 'reviews/VERIFIER_REVIEW.md', 'reviews/reviewed_helpers.json',
                'reviews/PACKAGING_SCRIPT_REVIEW.md', 'records/FINAL_AUDIT_SIGNOFF.json', 'formal/tests/control_manifest.json'}
    insist(required <= evidence.keys(), 'Required final review missing from accepted evidence')
    for name, value in evidence.items():
        insist(a.files[PROJECT + name] == value, 'Changed acceptance evidence: ' + name)
    signoff = a.json(PROJECT + 'records/FINAL_AUDIT_SIGNOFF.json')
    insist(signoff['status'] == 'PASS' and signoff['formal_receipt_sha256'] == receipt_sha and signoff['postflight_sha256'] == post_sha,
           'Final coordinator signoff does not bind the accepted replay')
    for name, value in signoff['review_sha256'].items():
        insist(a.files[PROJECT + name] == value, 'Changed signed-off review: ' + name)
    packaging_sha = a.files[PROJECT + 'packaging/package_release.py']
    insist(packaging_sha in a.read(PROJECT + 'reviews/PACKAGING_SCRIPT_REVIEW.md').decode(), 'Exact packaging script not reviewed')
    checks.append('All helpers and final acceptance reviews retain their exact reviewed identities.')

    commands = rec['commands']
    insist(len(commands) == post['command_count'] == summary['recorded_commands'] == 231, 'Unexpected final command count')
    labels = [c['label'] for c in commands]
    insist(len(set(labels)) == len(labels) and labels == rec['exact_command_labels'] == post['exact_command_labels'], 'Command inventory/order mismatch')
    insist({c['log']: c['log_sha256'] for c in commands} == post['command_log_sha256'], 'Postflight command logs differ')
    for c in commands:
        insist(c['passed'] is True and c['timeout'] is False, 'Failed/timed out command: ' + c['label'])
        insist(path_is_safe(c['log']) and a.files[RUN + c['log']] == c['log_sha256'], 'Changed command log: ' + c['label'])
        if c['expected_rejection']:
            insist(c['exit_code'] != 0, 'Negative command unexpectedly succeeded: ' + c['label'])
            log = a.read(RUN + c['log']).decode('utf-8')
            insist(c['required_markers'] and all(marker in log for marker in c['required_markers']), 'Required rejection diagnostic missing: ' + c['label'])
        else:
            insist(c['exit_code'] == 0, 'Positive command failed: ' + c['label'])
    controls = a.json('formal/control_manifest.json')['controls']
    insist(controls == rec['controls'] == inventory['controls'], 'Control manifests differ')
    counts = dict(Counter(c['kind'] for c in controls))
    insist(len(controls) == summary['control_files'] == 39 and counts == summary['controls'] == {'positive': 12, 'negative': 25, 'policy': 2},
           'Unexpected positive/negative/policy control counts')
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
    insist(len(production) == rec['production_modules'] == summary['production_modules'] == 151 and len(roots) == 3, 'Production/root count mismatch')
    compiled = production + roots
    insist({n: source[n] for n in compiled} == rec['source_sha256'] and len(compiled) == rec['compile_targets'] == 154, 'Compilation target mismatch')
    insist(set(rec['new_modules']) == NEW_MODULES, 'Unexpected new module inventory')
    explicit = sum(len(re.findall(r'\b(?:theorem|lemma)\s+', strip_lean_comments(a.read('formal/' + n).decode()))) for n in compiled)
    insist(explicit == rec['explicit_theorem_lemma_count'] == summary['explicit_theorem_lemma_count'] == 1650, 'Explicit theorem total mismatch')
    report.update(recorded_commands=len(commands), controls=counts, control_files=len(controls),
                  production_modules=len(production), compile_targets=len(compiled), explicit_theorem_lemma_count=explicit)
    checks.append('All 231 recorded commands/log hashes/rejection markers and 39 controls agree; 151 modules plus three roots contain 1,650 explicit theorems.')

    audit = a.json(RUN + 'axioms.json')
    rows = audit['declarations']
    byname = {row['name']: row for row in rows}
    insist(len(byname) == len(rows) == audit['count'] == rec['axiom_declarations'] == post['axiom_declarations'] == summary['axiom_declarations'], 'Declaration census mismatch')
    insist(audit['unexpected'] == [] and all(r['unsafe'] is False and set(r['axioms']) <= AXIOMS for r in rows), 'Unsafe declaration/unapproved axiom')
    insist(sorted(set().union(*(set(r['axioms']) for r in rows))) == rec['axiom_union'] == sorted(AXIOMS), 'Axiom union mismatch')
    insist(a.files[RUN + 'axioms.json'] == rec['axiom_report_sha256'] == post['axiom_report_sha256'] == summary['axiom_report_sha256'], 'Axiom report hash mismatch')
    parent_rows = parent.json('budget_v1.10.0/integration/runs/clean_budget_01/axioms.json')['declarations']
    fields = ('name', 'kind', 'module', 'unsafe')
    def signature(row):
        return tuple(row[k] for k in fields) + (tuple(sorted(row['axioms'])),)
    insist(len(parent_rows) == rec['parent_declarations'] == summary['inherited_declarations'] == 4935, 'Parent declaration count mismatch')
    insist(all(r['name'] in byname and signature(r) == signature(byname[r['name']]) for r in parent_rows), 'Inherited declaration changed/missing')
    baseline = a.json('formal/parent_declarations.json')
    insist(sorted(map(signature, baseline['declarations'])) == sorted(map(signature, parent_rows)), 'Copied parent declaration catalogue is not the pinned predecessor catalogue')
    parent_run = 'budget_v1.10.0/integration/runs/clean_budget_01/'
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
        insist(namespaces == [module], 'Public declaration scan requires the observed single module namespace')
        public.extend((module + '.' + name, kind) for kind, name in re.findall(r'^\s*(theorem|lemma|def)\s+(\S+)', text, re.M))
    theorems = sum(kind in {'theorem', 'lemma'} for _, kind in public)
    insist(theorems == summary['new_explicit_theorems'] == 31 and len(public) == summary['new_named_public_declarations'] == 33, 'New explicit/public declaration counts differ')
    insist(all(name in byname and byname[name]['kind'] == ('definition' if kind == 'def' else 'theorem') for name, kind in public), 'A new named declaration lacks the expected export')
    type_sha = a.files[RUN + 'new_declarations.json']
    insist(type_sha == summary['new_declarations_sha256'], 'Accepted complete type report hash mismatch')
    math = a.read(PROJECT + 'reviews/WR08_WR09_WR16_MATH_AUDIT.md').decode()
    for value in [receipt_sha, a.files[RUN + 'axioms.json'], type_sha] + [source[m.replace('.', '/') + '.lean'] for m in sorted(NEW_MODULES)]:
        insist(value in math, 'Final mathematical review lacks required source/export/type/receipt hash')
    insist(not re.search(r'Primary verdict[^\n]*(?:incomplete|provisional|pending)', math[:2500], re.I), 'Mathematical review still carries a provisional primary verdict')
    report.update(axiom_declarations=len(rows), inherited_declarations_preserved=len(parent_rows),
                  new_exported_declarations=len(new), new_explicit_theorems=theorems,
                  new_named_public_declarations=len(public), new_declarations_sha256=type_sha,
                  axiom_report_sha256=a.files[RUN + 'axioms.json'], acceptance_evidence_sha256=evidence,
                  reviewed_helper_sha256=actual_helpers, postflight_validator_sha256=post['validator_sha256'])
    checks.append('All 4,935 inherited declaration signatures are preserved; all new declarations have full types; 31 explicit theorems and 33 public declarations are present and final mathematical review binds their exact evidence.')

    complete = [f'WR{i:02}' for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 16]]
    written = ['WR10', 'WR11', 'WR12', 'WR15']
    insist(coverage['complete'] == ledger['complete_formal_groups'] == complete and coverage['partial'] == ledger['partial_formal_groups'] == [], 'Complete/partial coverage mismatch')
    insist(coverage['written_only'] == ledger['open_formal_groups'] == written, 'Written-only coverage mismatch')
    insist(coverage['formal_receipt_sha256'] == receipt_sha, 'Coverage refers to a different receipt')
    report.update(complete_formal_groups=complete, partial_formal_groups=[], written_only_formal_groups=written)
    checks.append('Coverage is exactly 12 complete groups, zero partial groups, and WR10–WR12/WR15 written-only.')

    delivery_path = archive_path.parent / 'Komorebi_Space_Lean_Delivery_Verification_v1.11.0.json'
    delivery = json.loads(delivery_path.read_text())
    insist(delivery['status'] == 'PASS' and delivery['archive_sha256'] == a.sha256 and delivery['archive_bytes'] == archive_path.stat().st_size, 'External delivery record describes another archive')
    for key in ('manifest_sha256', 'formal_receipt_sha256', 'postflight_sha256', 'axiom_report_sha256'):
        insist(delivery[key] == report[key], 'Delivery binding mismatch: ' + key)
    insist(delivery['acceptance_evidence_sha256'] == evidence and delivery['packaging_script_sha256'] == packaging_sha, 'Delivery review/script evidence mismatch')
    insist(delivery['type_audit_sha256'] == evidence['reviews/WR08_WR09_WR16_MATH_AUDIT.md'], 'Delivery mathematical audit mismatch')
    for key, expected in [('payload_files', len(a.files)-1), ('total_archive_files_with_manifest', len(a.files)),
                          ('parent_files_preserved_including_manifest', 4828), ('command_count', 231), ('control_count', 39),
                          ('production_modules', 151), ('compile_targets', 154), ('axiom_declarations', len(rows)), ('new_axiom_declarations', len(new))]:
        insist(delivery[key] == expected, 'Delivery count mismatch: ' + key)
    insist(delivery['new_pdf_claimed'] is False and delivery['compiled_objects_included'] is False and delivery['portable_runtime_included'] is False, 'Incorrect delivery scope claims')
    progress = archive_path.parent / 'Komorebi_Space_Lean_Progress_v1.11.0.md'
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
    output = args.report or work / 'output/Komorebi_Space_Lean_Independent_Archive_Review_v1.11.0.json'
    report = {'schema': 'komorebi-space-independent-archive-review-v1', 'status': 'FAIL',
              'reviewer': '/root/limits_archive_audit', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'checker_sha256': file_digest(Path(__file__).resolve()), 'checks': [],
              'independence': 'Independent standard-library implementation; packaging/replay helpers were neither imported nor executed.',
              'scope': 'Actual archive identities, complete ancestry, accepted source/evidence binding, counts, and published coverage.',
              'limitations': ['No second Lean compilation or runtime-cache rehash; those operations are covered by the bound independently reviewed postflight.',
                              'This review checks final mathematical audit identity and bindings, not a new proof audit.',
                              'Inherited declaration preservation compares name, kind, module, unsafe flag and axiom sets; it is not a proof-expression identity check.']}
    try:
        verify(work, archive, report)
        report['status'] = 'PASS'
    except Exception as error:
        report['failure'] = f'{type(error).__name__}: {error}'
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    insist(not output.resolve().is_relative_to(work / 'limits_v1.11.0') and not output.resolve().is_relative_to(archive.with_suffix('')),
           'Review report must remain outside the frozen project and archive tree')
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': report['status'], 'checks_passed': len(report['checks']),
                      'report': str(output), 'failure': report.get('failure')}, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
