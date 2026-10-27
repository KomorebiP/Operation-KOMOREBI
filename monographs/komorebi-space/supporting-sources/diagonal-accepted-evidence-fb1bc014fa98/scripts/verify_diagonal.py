#!/usr/bin/env python3
"""Replay the strict diagonal-source checks and the targeted diagnostic controls.

First provision lean/lean-toolchain and lean/lake-manifest.json and run
`lake exe cache get` and `lake build KomorebiSpaceDiagonal` from lean/.
Use --native on an ordinary host with the pinned Lean/Lake on PATH.
This script intentionally does not replay the parent publication's 44 controls.
"""
from pathlib import Path
import argparse
import collections
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native', action='store_true')
args = parser.parse_args()
prefix = [] if args.native else [str(root / 'scripts/lean_env.sh')]
modules = [
    'KomorebiSpace.DiagonalDefinitions',
    'KomorebiSpace.DiagonalSeriesBounds',
    'KomorebiSpace.InfiniteDiagonalModel',
    'KomorebiSpace.DiagonalNoisyRate',
    'KomorebiSpace.MonotoneBudgetAsymptotic',
    'KomorebiSpace.DiagonalAsymptotic',
    'KomorebiSpace.DiagonalTheorems',
    'KomorebiSpaceDiagonal',
]
strict = ['lake', 'env', 'lean', '-j1', '-DwarningAsError=true', '-DautoImplicit=false']
runs = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(label, command, source=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = sha(source) if source else None
    tick = time.monotonic()
    result = subprocess.run(command, cwd=root / 'lean', capture_output=True, text=True)
    log = root / 'logs' / ('final_' + label + '.log')
    log.write_text(result.stdout + result.stderr)
    item = dict(label=label, command=command, cwd=str(root / 'lean'),
                started_utc=started, duration_seconds=time.monotonic()-tick,
                exit_code=result.returncode, log=str(log.relative_to(root)),
                log_sha256=sha(log))
    if source:
        item.update(source=str(source.relative_to(root)),
                    source_sha256_before=before, source_sha256_after=sha(source))
    runs.append(item)
    print(label, 'exit', result.returncode, flush=True)
    (root / 'records/FINAL_REPLAY.json').write_text(json.dumps(runs, indent=2)+'\n')
    if result.returncode or (source and before != sha(source)):
        raise SystemExit('Verification stopped; inspect ' + str(log))
    return result.stdout

version = run('compiler_version', prefix + ['lean', '--version'])
if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:
    raise SystemExit('Wrong compiler identity')
for module in modules:
    relative = Path(module.replace('.', '/') + '.lean')
    source = root / 'lean' / relative
    output = Path('.lake/build/lib/lean') / relative.with_suffix('.olean')
    (root / 'lean' / output.parent).mkdir(parents=True, exist_ok=True)
    run(module, prefix + strict + ['-o', str(output), str(relative)], source)

inventory_text = run('inventory', prefix + strict + [str(root / 'audit/DiagonalInventory.lean')],
                     root / 'audit/DiagonalInventory.lean')
rows = [json.loads(line) for line in inventory_text.splitlines() if line.startswith('{')]
count_line = next(line for line in inventory_text.splitlines() if line.startswith('AUDIT_DECLARATION_COUNT='))
assert len(rows) == int(count_line.split('=')[1]) and rows
allowed = {'propext', 'Classical.choice', 'Quot.sound'}
assert all(set(row['axioms']) <= allowed and not row['unsafe'] and not row['axiom_declaration'] for row in rows)
counts = collections.Counter(row['module'] for row in rows)
sources = {}
for module in modules:
    source = root / 'lean' / Path(module.replace('.', '/') + '.lean')
    declarations = re.findall(r'^[ \t]*(?:@\[[^\n]*?\]\s*)*(?:(?:noncomputable|private|protected)\s+)*(theorem|lemma|def|abbrev|instance|structure)\s+([^\s({:]+)', source.read_text(), re.M)
    sources[module] = dict(path=str(source.relative_to(root)), sha256=sha(source),
        explicit_source_declarations=[dict(kind=k, name=n) for k, n in declarations],
        exported_declarations=counts[module])
inventory = dict(scope='Every environment declaration attributed by Lean module provenance to the seven new production modules and the new import entrypoint, including generated helpers.',
    declarations=sorted(rows, key=lambda row: (row['module'], row['name'])), source_modules=sources,
    total_exported=len(rows), all_axioms_permitted=True, no_unsafe_or_axiom_declarations=True,
    evidence_log='logs/final_inventory.log', evidence_log_sha256=sha(root/'logs/final_inventory.log'))
(root / 'records/DIAGONAL_DECLARATIONS.json').write_text(json.dumps(inventory, indent=2)+'\n')
control_command = [sys.executable, str(root / 'scripts/run_controls.py')]
if args.native:
    control_command.append('--native')
run('controls', control_command, root / 'scripts/run_controls.py')
print('All diagonal replay checks and expected control outcomes passed.', flush=True)
