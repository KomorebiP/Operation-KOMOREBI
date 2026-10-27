#!/usr/bin/env python3
"""Read-only bundle integrity and project-local dependency checks; does not run Lean."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def inspect_project() -> dict:
    errors: list[str] = []
    formal = ROOT / 'formal_release'
    conf = json.loads((formal / 'checks/modules.json').read_text())
    modules = conf['modules']
    sources = {p.relative_to(formal / 'lean').as_posix(): p
               for p in (formal / 'lean').rglob('*.lean')}
    expected = {m.replace('.', '/') + '.lean' for m in modules}
    if set(sources) != expected:
        errors.append('Production Lean source inventory differs from checks/modules.json.')
    objects = 0
    project_imports = 0
    for name, path in sources.items():
        obj = formal / 'build' / Path(name).with_suffix('.olean')
        if not obj.is_file():
            errors.append(f'Missing compiled object: {obj.relative_to(ROOT)}')
        else:
            objects += 1
        for mod in re.findall(r'^\s*import\s+(PaperX(?:II)?\.[\w.]+)', path.read_text(), re.M):
            project_imports += 1
            if mod.replace('.', '/') + '.lean' not in sources:
                errors.append(f'Missing local Lean import {mod} in {name}')
    python_count = 0
    for path in ROOT.rglob('*.py'):
        if path.relative_to(ROOT).parts[0] == 'build':
            continue
        python_count += 1
        try:
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        except (SyntaxError, UnicodeError) as e:
            errors.append(f'Python syntax error: {path.relative_to(ROOT)}: {e}')
    paper = formal / 'paper'
    tex = paper / 'Paper_XII_Revised_Formalization_Complete_v0.17.0.tex'
    text = tex.read_text()
    figures = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text)
    for name in figures:
        if not any((folder / name).is_file() for folder in [paper, paper / 'figures']):
            errors.append(f'Missing manuscript graphic {name}')
    bibs = re.findall(r'\\bibliography\{([^}]+)\}', text)
    for group in bibs:
        for name in group.split(','):
            if not (paper / (name.strip() + '.bib')).is_file():
                errors.append(f'Missing bibliography {name}')
    if not tex.with_suffix('.bbl').is_file():
        errors.append('Missing supplied manuscript .bbl fallback.')
    appendix = ROOT / 'visual_appendix'
    if not (appendix / 'source/pages.tex').is_file():
        errors.append('Missing appendix source/pages.tex')
    pages = (appendix / 'source/pages.tex').read_text()
    graphics = re.findall(r'\\vfig(?:\[[^\]]*\])?\{([^}]+)\}', pages)
    for name in graphics:
        if not (appendix / 'graphics' / (name + '.tex')).is_file():
            errors.append(f'Missing appendix TikZ source {name}')
    pairs = [
        (ROOT / 'pdfs/Paper_XII_Manuscript.pdf', tex.with_suffix('.pdf')),
        (ROOT / 'pdfs/Paper_XII_Manuscript.pdf', appendix / 'original/Paper_XII_v0.17.0.pdf'),
        (ROOT / 'pdfs/Paper_XII_Visual_Appendix.pdf', appendix / 'Paper_XII_Visual_Appendix.pdf'),
        (ROOT / 'pdfs/Paper_XII_With_Visual_Appendix.pdf', appendix / 'Paper_XII_With_Visual_Appendix.pdf'),
    ]
    for left, right in pairs:
        if sha(left) != sha(right):
            errors.append(f'PDF baseline mismatch: {left.name}')
    origins = json.loads((ROOT / 'provenance/SOURCE_ORIGINS.json').read_text())
    preserved = 0
    for source in origins:
        for item in source['files']:
            p = ROOT / item['bundle_path']
            if not p.is_file() or sha(p) != item['sha256']:
                errors.append(f'Original source member changed: {item["bundle_path"]}')
            else:
                preserved += 1
    return {
        'status': 'FAIL' if errors else 'PASS',
        'scope': 'Packaging integrity and project-local dependencies only; not a Lean replay.',
        'registered_production_modules': len(modules),
        'compiled_production_objects': objects,
        'project_local_import_references': project_imports,
        'python_files_syntax_checked': python_count,
        'manuscript_figure_references_resolved': len(figures),
        'appendix_generated_figure_references_resolved': len(graphics),
        'unchanged_inherited_archive_members': preserved,
        'errors': errors,
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, help='Write a JSON report in addition to stdout.')
    args = ap.parse_args()
    manifest_path = ROOT / 'BUNDLE_MANIFEST_SHA256.json'
    if not manifest_path.is_file():
        print('FAIL: BUNDLE_MANIFEST_SHA256.json is missing.', file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())
    errors = []
    for name, expected in manifest['files'].items():
        p = (ROOT / name).resolve()
        if not p.is_relative_to(ROOT.resolve()):
            errors.append(f'Unsafe manifest path: {name}')
        elif not p.is_file():
            errors.append(f'Missing: {name}')
        elif sha(p) != expected:
            errors.append(f'Changed: {name}')
    report = inspect_project()
    report['manifest_files_checked'] = len(manifest['files'])
    report['errors'] = errors + report['errors']
    report['status'] = 'FAIL' if report['errors'] else 'PASS'
    rendered = json.dumps(report, indent=2) + '\n'
    print(rendered, end='')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as e:
        print(f'FAIL: {e}', file=sys.stderr)
        raise SystemExit(2)
