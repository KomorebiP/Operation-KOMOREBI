#!/usr/bin/env python3
"""Stage delivered Paper X sources without modifying or importing inherited objects."""
from pathlib import Path
import collections
import hashlib
import json
import re
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'restored/conditional_checked'
READERS = BASE.parent / 'paper_x_baseline/inner/Paper_X'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    s = path.read_text()
    depth = 0
    i = 0
    clean = []
    while i < len(s):
        if s[i:i+2] == '/-':
            depth += 1
            i += 2
            continue
        if depth and s[i:i+2] == '-/':
            depth -= 1
            i += 2
            continue
        if not depth:
            clean.append(s[i])
        i += 1
    out = []
    for line in ''.join(clean).splitlines():
        line = line.split('--', 1)[0]
        if re.match(r'^\s*(?:public\s+)?import\s+', line):
            out.extend(re.sub(r'^\s*(?:public\s+)?import\s+', '', line).split())
    return out

candidates = collections.defaultdict(list)
for path in ROOT.rglob('*.lean'):
    if any(k in path.parts for k in ['development', 'initial_drafts', 'upstream_exact',
                                    'probe_src', 'ported_src', 'compat_src', 'extracted_source']):
        continue
    roots = [i for i, part in enumerate(path.parts)
             if part in ['lean', 'source_snapshot', 'inherited_sources']]
    if not roots:
        continue
    suffix = path.parts[roots[-1] + 1:]
    if suffix[0] in ['PaperX', 'CebotarevDensity']:
        module = '.'.join((*suffix[:-1], Path(suffix[-1]).stem))
    elif suffix == ('HorizontalTransportCompletion.lean',):
        # The Sep14 checked continuation stored this module without its PaperX directory.
        module = 'PaperX.HorizontalTransportCompletion'
    else:
        continue
    candidates[module].append(path)

# A nearest delivered archive overrides its nested predecessor; the two changed
# modules are explicitly recorded in conflict_resolution below.
selected = {m: min(ps, key=lambda p: (len(p.parts), len(str(p)), str(p)))
            for m, ps in candidates.items()}
conflicts = []
for module, paths in sorted(candidates.items()):
    if len({sha(p) for p in paths}) > 1:
        conflicts.append({'module': module, 'selected': str(selected[module]),
                          'reason': 'Nearest checked successor source overrides nested predecessor.',
                          'variants': [{'path': str(p), 'sha256': sha(p)} for p in sorted(paths)]})

terminal = 'PaperX.ConditionalOccupiedSystemCompletion'
claims = json.loads((READERS / 'publication/CLAIM_RECORDS.json').read_text())
route_roots = sorted({'PaperX.' + m for c in claims for m in c['source_route']})

def closure(roots):
    seen = set()
    active = set()
    order = []
    missing = set()
    def visit(module):
        if module in seen:
            return
        if module not in selected:
            if module.startswith(('PaperX.', 'CebotarevDensity.')):
                missing.add(module)
            return
        if module in active:
            raise ValueError('Import cycle: ' + module)
        active.add(module)
        for dep in imports(selected[module]):
            visit(dep)
        active.remove(module)
        seen.add(module)
        order.append(module)
    for module in roots:
        visit(module)
    return order, sorted(missing)

for tag, roots in [('TERMINAL', [terminal]), ('PUBLICATION', sorted(set(route_roots + [terminal])))]:
    order, missing = closure(roots)
    records = []
    source_root = BASE / (tag.lower() + '_sources')
    for module in order:
        origin = selected[module]
        dest = source_root / Path(*module.split('.')).with_suffix('.lean')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, dest)
        records.append({'module': module, 'source': str(dest), 'origin': str(origin),
                        'source_relative': dest.relative_to(BASE).as_posix(),
                        'origin_restored_relative': origin.relative_to(ROOT).as_posix(),
                        'source_sha256': sha(origin), 'imports': imports(origin),
                        'duplicate_candidate_count': len(candidates[module]) - 1})
    report = {
        'scope': 'Exact delivered-source import closure; no inherited production proof object is seeded.',
        'selection_roots': roots, 'count': len(order), 'missing': missing,
        'source_root': str(source_root), 'modules': records,
        'all_candidate_modules': len(selected),
        'conflict_resolution': [c for c in conflicts if c['module'] in order],
        'excluded_scopes': ['later residual-system attempt', 'development and compiler fixtures'],
    }
    (BASE / (tag + '_SOURCE_MANIFEST.json')).write_text(json.dumps(report, indent=2) + '\n')
    (BASE / (tag + '_BUILD_ORDER.txt')).write_text('\n'.join(order) + '\n')
    print(json.dumps({'tag': tag, 'modules': len(order), 'missing': missing,
                      'source_root': str(source_root)}), flush=True)
