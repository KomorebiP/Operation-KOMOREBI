#!/usr/bin/env python3
"""Audit selected freshly compiled Paper X modules without recompiling them.

The compilation receipt and source selection are separate required inputs.
This runner compiles only AuditCore verification tooling, verifies every direct
production import resolves to the supplied fresh object directory, and audits
all constants by owning module (including private/generated constants).
It does not establish manuscript/source semantic equivalence.
"""
from __future__ import annotations
import argparse
import collections
import json
import os
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
TOOLING = Path(__file__).resolve().parent / 'tooling'
sys.path.insert(0, str(TOOLING))
from audit_engine import (AuditError, audit_source, execute, parse_audit,
    parse_json, require_rejection, require_success, save_json,
    sha256, utc, KINDS, safe_relative, LEAN_SHA256)
from runtime_adapter import runtime_env, ADAPTER_SHA256

FLAGS = ['-j1', '-M6144', '-DwarningAsError=true']
MODULE = re.compile(r'[A-Za-z_][A-Za-z0-9_.]*')
DIGEST = re.compile(r'[0-9a-f]{64}')

def selection(path: Path) -> dict:
    data = parse_json(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 'paper_x.production_selection.v1':
        raise AuditError('Unsupported production selection schema')
    if not isinstance(data.get('scope'), str) or not data['scope'].strip():
        raise AuditError('Missing explicit selection scope')
    modules, targets = data.get('modules'), data.get('targets')
    if not isinstance(modules, list) or not modules or not isinstance(targets, list) or not targets:
        raise AuditError('Nonempty module and target lists required')
    names = set()
    for m in modules:
        if not isinstance(m, dict) or set(m) != {'module', 'source', 'source_sha256'}:
            raise AuditError('Malformed module selection')
        name = m['module']
        if not isinstance(name, str) or not MODULE.fullmatch(name) or name in names:
            raise AuditError('Invalid/duplicate selected module')
        names.add(name)
        if not isinstance(m['source'], str) or not Path(m['source']).is_absolute():
            raise AuditError('Selected source must have an absolute path')
        if not isinstance(m['source_sha256'], str) or not DIGEST.fullmatch(m['source_sha256']):
            raise AuditError('Malformed source pin')
    found = set()
    for t in targets:
        if not isinstance(t, dict) or set(t) != {'name', 'kind', 'owner'}:
            raise AuditError('Malformed target contract')
        if not isinstance(t['name'], str) or not t['name'] or t['name'] in found:
            raise AuditError('Invalid/duplicate target')
        found.add(t['name'])
        if t['kind'] not in KINDS or t['owner'] not in names:
            raise AuditError('Target kind/owner outside selected contract')
    return data

def pins(data: dict, objects: Path) -> list[dict]:
    records = []
    for m in data['modules']:
        src = Path(m['source'])
        obj = objects.joinpath(*m['module'].split('.')).with_suffix('.olean')
        if src.is_symlink() or obj.is_symlink() or not src.is_file() or not obj.is_file():
            raise AuditError('Missing/symlinked selected source/object: ' + m['module'])
        if sha256(src) != m['source_sha256']:
            raise AuditError('Selected source changed: ' + m['module'])
        records.append({**m, 'object': str(obj), 'object_sha256': sha256(obj),
                        'source_bytes': src.stat().st_size, 'object_bytes': obj.stat().st_size})
    return records

def verify_compilation_receipt(receipt: dict, receipt_path: Path, data: dict,
                               observed: list[dict]) -> None:
    """Bind every audited object to its successful fresh compile record."""
    count = len(data['modules'])
    if (receipt.get('status') != 'PASS' or receipt.get('complete') is not True
        or receipt.get('source_unchanged') is not True
        or type(receipt.get('production_objects_seeded')) is not int
        or receipt['production_objects_seeded'] != 0
        or receipt.get('compiler_sha256') != LEAN_SHA256):
        raise AuditError('Compilation receipt lacks complete fresh pinned-compiler acceptance')
    for field in ('expected_modules', 'compiled_modules', 'passed_modules'):
        if type(receipt.get(field)) is not int or receipt[field] != count:
            raise AuditError('Compilation receipt module count mismatch: '+field)
    if receipt.get('failed_modules') != [] or receipt.get('blocked_modules') != []:
        raise AuditError('Compilation failures or blocked modules remain')
    manifest = Path(receipt.get('source_manifest', ''))
    if (not manifest.is_absolute() or not manifest.is_file()
        or receipt.get('source_manifest_sha256') != data.get('production_manifest_sha256')
        or sha256(manifest) != data['production_manifest_sha256']):
        raise AuditError('Compilation receipt/source-selection manifest mismatch')
    rows = receipt.get('results')
    if not isinstance(rows, list) or len(rows) != count:
        raise AuditError('Incomplete compilation result list')
    by_name = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('module') in by_name:
            raise AuditError('Malformed/duplicate compilation result')
        by_name[row.get('module')] = row
    if set(by_name) != {m['module'] for m in observed}:
        raise AuditError('Audited and compiled module memberships disagree')
    for pinned in observed:
        row = by_name[pinned['module']]
        if (row.get('status') != 'PASS' or type(row.get('returncode')) is not int
            or row['returncode'] != 0 or row.get('timed_out') is not False
            or row.get('source_sha256') != pinned['source_sha256']):
            raise AuditError('Unsuccessful/mismatched compile record: '+pinned['module'])
        matches = []
        for output in row.get('outputs', []):
            p = receipt_path.parent / safe_relative(output['path'])
            if str(p.resolve()) == pinned['object']:
                matches.append(output)
        if len(matches) != 1 or matches[0].get('sha256') != pinned['object_sha256']:
            raise AuditError('Audited object differs from fresh compiler output: '+pinned['module'])

def verify_artifact_inventory(objects: Path, inventory: Path) -> list[dict]:
    """Authenticate auxiliary private/server/IR payloads as well as primary objects."""
    data = parse_json(inventory.read_text(encoding='utf-8'))
    rows = data.get('all_generated_files') if isinstance(data, dict) else None
    if (not isinstance(rows, list) or not rows or type(data.get('count')) is not int
        or data['count'] != len(rows)):
        raise AuditError('Invalid complete generated-artifact inventory')
    expected, checked = set(), []
    for row in rows:
        rel = safe_relative(row['path'])
        if rel.parts[0] != 'objects' or len(rel.parts) < 2:
            raise AuditError('Artifact inventory path outside objects')
        path = objects.joinpath(*rel.parts[1:])
        if row['path'] in expected or path.is_symlink() or not path.is_file():
            raise AuditError('Duplicate/missing/symlinked artifact')
        expected.add(row['path'])
        if path.stat().st_size != row['bytes'] or sha256(path) != row['sha256']:
            raise AuditError('Generated artifact changed: '+row['path'])
        checked.append({**row,'actual_path':str(path)})
    actual = {'objects/'+p.relative_to(objects).as_posix() for p in objects.rglob('*')
              if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise AuditError('Generated artifact inventory is not exact')
    return checked

def run(args) -> dict:
    work = args.work.resolve()
    if work.exists():
        raise AuditError('Choose a new output directory; evidence is append-only')
    work.mkdir(parents=True)
    report = {'schema':'paper_x.production_axiom_audit.v1', 'status':'RUNNING',
              'started_utc':utc(), 'paper_x_production_modules_audited':0,
              'scope':'owning-module census and transitive kernel-axiom policy; no semantic proof audit',
              'runner_sha256':sha256(Path(__file__)), 'commands':[],
              'compiler_fixture_modules_counted_as_production':0}
    save = lambda: save_json(work/'REPORT.json', report)
    save()
    try:
        data = selection(args.selection.resolve())
        report.update(selection=str(args.selection.resolve()), selection_sha256=sha256(args.selection),
                      selected_scope=data['scope'], selected_module_count=len(data['modules']),
                      selected_target_count=len(data['targets']))
        # Receipt is preserved, not accepted as replacement for the actual audit.
        receipt = parse_json(args.compile_receipt.read_text(encoding='utf-8'))
        if not isinstance(receipt, dict) or receipt.get('status') not in ('PASS', 'passed'):
            raise AuditError('A successful fresh production compilation receipt is required')
        report.update(compilation_receipt=str(args.compile_receipt.resolve()),
                      compilation_receipt_sha256=sha256(args.compile_receipt))
        objects = args.objects.resolve()
        before = pins(data, objects)
        verify_compilation_receipt(receipt, args.compile_receipt.resolve(), data, before)
        artifact_before = verify_artifact_inventory(objects, args.artifact_inventory)
        report.update(artifact_inventory=str(args.artifact_inventory.resolve()),
                      artifact_inventory_sha256=sha256(args.artifact_inventory),
                      production_artifacts_pinned=len(artifact_before), compiler_flags=FLAGS)
        save_json(work/'ALL_ARTIFACT_PINS_BEFORE.json', artifact_before)
        save_json(work/'SOURCE_OBJECT_PINS_BEFORE.json', before)
        common = work/'common'; common.mkdir()
        for source in ('AuditCore.lean', 'audit_engine.py', 'runtime_adapter.py'):
            shutil.copy2(TOOLING/source, common/source)
        report['tooling'] = {p.name:sha256(p) for p in common.iterdir()}
        lean, env = runtime_env(args.runtime.resolve(), [common, objects],
                               packages=[str(p.resolve()) for p in args.package_path])
        report.update(lean_sha256=sha256(lean), lean_path=env['LEAN_PATH'],
                      compatibility_adapter=env['LD_PRELOAD'], compatibility_adapter_sha256=ADAPTER_SHA256)
        def command(label, argv, timeout=args.timeout):
            r = execute(list(map(str, argv)), common, env, timeout, work/'logs'/(label+'.log'))
            report['commands'].append(r); save()
            return r, Path(r['log']).read_text(encoding='utf-8', errors='strict')
        r, text = command('compiler_version', [lean, '--version']); require_success(r)
        report['compiler_version'] = text.strip()
        r, text = command('compile_audit_tool', [lean, *FLAGS, '-o', 'AuditCore.olean', 'AuditCore.lean'])
        require_success(r)
        owners = [m['module'] for m in data['modules']]
        if args.batch_size < 1:
            raise AuditError('Positive owner batch size required')
        batches = [owners[i:i+args.batch_size] for i in range(0,len(owners),args.batch_size)]
        if [m for batch in batches for m in batch] != owners:
            raise AuditError('Owner partition is not an exact ordered cover')
        report['owner_batches'] = batches
        all_records, all_targets, resolutions, source_pins, type_pins = [], [], [], [], []
        type_output = []
        object_pins = {p['module']:p['object'] for p in before}
        for index, batch in enumerate(batches, 1):
            tag = f'batch_{index:02d}'
            targets = [t for t in data['targets'] if t['owner'] in batch]
            audit = common/(tag+'_AuditRun.lean')
            audit.write_text(audit_source(batch, targets), encoding='utf-8')
            source_pins.append({'path':str(audit),'sha256':sha256(audit)})
            r, text = command(tag+'_resolved_imports', [lean, '--deps', audit.name]); require_success(r)
            resolved = []
            for line in text.splitlines():
                p = Path(line.strip())
                if not p.is_absolute() or not p.is_file() or p.suffix != '.olean':
                    raise AuditError('Unexpected dependency output: '+line)
                resolved.append({'path':str(p.resolve()), 'sha256':sha256(p)})
            actual = {row['path'] for row in resolved}
            required = {object_pins[m] for m in batch} | {str((common/'AuditCore.olean').resolve())}
            if not required <= actual:
                raise AuditError('Production imports did not all resolve to selected fresh objects')
            resolutions.append({'batch':tag,'owners':batch,'resolved':resolved})
            save_json(work/'RESOLVED_IMPORTS.json', resolutions)
            r, text = command(tag+'_owned_declarations_and_axioms', [lean, *FLAGS, audit.name])
            part = parse_audit(r, text, batch, targets)
            save_json(work/(tag+'_OWNED_DECLARATIONS.json'), part)
            all_records.extend(part['records']); all_targets.extend(part['targets_resolved'])
            # Capture exact elaborated signatures with every implicit parameter.
            if targets:
                types = common/(tag+'_TargetTypes.lean')
                types.write_text('\n'.join(['import '+m for m in batch] + [
                    'set_option pp.all true', 'set_option format.width 180',
                    'set_option pp.maxSteps 1000000'] +
                    ['#check @'+t['name'] for t in targets])+ '\n', encoding='utf-8')
                r, text = command(tag+'_exact_target_types', [lean, *FLAGS, types.name]); require_success(r)
                if '⋯' in text:
                    raise AuditError('Target type pretty-printing was truncated')
                type_output.append(f'=== {tag} ===\n'+text)
                type_pins.append({'path':str(types),'sha256':sha256(types)})
            report['owner_batches_completed'] = index
            save()
        if len({row['name'] for row in all_records}) != len(all_records):
            raise AuditError('Declaration repeated between owner batches')
        if {t['name']:t for t in all_targets} != {t['name']:t for t in data['targets']}:
            raise AuditError('Combined target cover mismatch')
        parsed = {'status':'PASS','declarations':len(all_records),
            'theorems':sum(r['kind']=='theorem' for r in all_records),
            'targets':len(all_targets),'owners':owners,'records':all_records,
            'targets_resolved':all_targets,
            'axiom_union':sorted({a for r in all_records for a in r['axioms']})}
        save_json(work/'OWNED_DECLARATIONS.json', parsed)
        (work/'EXACT_TARGET_TYPES.txt').write_text('\n'.join(type_output),encoding='utf-8')
        # Deliberately invalid contracts must be rejected by the live compiler/auditor.
        controls = []
        chosen = data['targets'][0]
        for label, changed, diagnostic in [
            ('missing_target', {**chosen, 'name':'PaperXAuditDefinitelyAbsentTarget'}, 'P10_TARGET_MISSING'),
            ('wrong_kind', {**chosen, 'kind':'definition' if chosen['kind'] != 'definition' else 'theorem'}, 'P10_TARGET_KIND'),
            ('duplicate_target', chosen, 'P10_DUPLICATE_TARGET')]:
            tests = [changed, changed] if label == 'duplicate_target' else [changed]
            f = common/(label+'.lean'); f.write_text(audit_source([chosen['owner']], tests), encoding='utf-8')
            r, text = command('control_'+label, [lean, *FLAGS, f.name])
            require_rejection(r, text, diagnostic)
            controls.append({'name':label, 'status':'PASS', 'diagnostic':diagnostic,
                             'scope':'target-contract negative control, not a production theorem'})
        after = pins(data, objects)
        if before != after:
            raise AuditError('Selected production source/object bytes changed during audit')
        if sha256(args.compile_receipt) != report['compilation_receipt_sha256']:
            raise AuditError('Compilation receipt changed during audit')
        verify_compilation_receipt(receipt, args.compile_receipt.resolve(), data, after)
        artifact_after = verify_artifact_inventory(objects, args.artifact_inventory)
        if artifact_before != artifact_after or sha256(args.artifact_inventory) != report['artifact_inventory_sha256']:
            raise AuditError('Generated artifact bytes/inventory changed during audit')
        save_json(work/'ALL_ARTIFACT_PINS_AFTER.json', artifact_after)
        save_json(work/'SOURCE_OBJECT_PINS_AFTER.json', after)
        counts = collections.Counter(r['owner'] for r in parsed['records'])
        kinds = collections.Counter(r['kind'] for r in parsed['records'])
        report.update(status='PASS', finished_utc=utc(),
            paper_x_production_modules_audited=len(owners),
            declarations=parsed['declarations'], theorems=parsed['theorems'],
            explicit_targets_resolved=parsed['targets'], axiom_union=parsed['axiom_union'],
            per_owner_declarations=dict(sorted(counts.items())),
            owners_with_no_constants=[m for m in owners if not counts[m]],
            declaration_kinds=dict(sorted(kinds.items())),
            private_declarations=sum('_private' in r['name'] for r in parsed['records']),
            controls=controls, source_and_object_pins_unchanged=True,
            audit_source_pins=source_pins, exact_type_source_pins=type_pins,
            limitations=['Checks kernel axiom dependencies and target contracts, not manuscript/source semantic correspondence.',
                        'Uses the supplied pinned dependency objects; does not cold-build the dependency foundation.',
                        'No claim is made for unrecovered Oct16–17 sources or reported122-module/39-test figures.'])
    except BaseException as error:
        report.update(status='FAILED', finished_utc=utc(), error=f'{type(error).__name__}: {error}')
    save(); return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--selection', required=True, type=Path)
    parser.add_argument('--compile-receipt', required=True, type=Path)
    parser.add_argument('--artifact-inventory', required=True, type=Path)
    parser.add_argument('--objects', required=True, type=Path)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--package-path', action='append', default=[], type=Path)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--timeout', default=600, type=float)
    parser.add_argument('--batch-size', default=12, type=int,
                        help='Partition owning modules exactly once to bound interpreter memory.')
    options = parser.parse_args()
    try:
        result = run(options)
        print(json.dumps({k:result.get(k) for k in ('status','paper_x_production_modules_audited','declarations','theorems','explicit_targets_resolved','error')}))
        sys.exit(0 if result['status']=='PASS' else 1)
    except Exception as error:
        print('FAILED:', error, file=sys.stderr); sys.exit(1)
