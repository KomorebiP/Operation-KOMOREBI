"""Replay the source-bound two-packet completion lemmas with the pinned Lean environment."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
LOCK = ROOT.parents[2] / 'formal/smith-chart-v0.1.0/dependency-lock.json'
LEAN_SHA256 = '37dfe799f69b990251f3b6bcff8a1c10c1afe2adcdecc5c580cc6726ffb63433'
SOURCE_REVISION = 'f8dbf83bb2a67139be7800768ce9a8be2109b28a'
ARCHIVE_PATH = 'research/smith-chart/SmithChart_Complete.zip'
ARCHIVE_SHA256 = '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
THEOREM_PATH = 'Smith_Chart_Research_2026-11-11/Smith_Chart_Extended_Seven_Reactive_Exact.md'
THEOREM_SHA256 = '3735cf4949c4da6426d2c132673775f5d0df9fea3e27071fa7d68176e0e51c5e'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEGATIVE_CONTROL = 'import SmithCompletion\nexample : SmithCompletion.Feasible (1/10) (1/2) := by\n  norm_num [SmithCompletion.Feasible, SmithCompletion.determinant, SmithCompletion.diagonalPlus, SmithCompletion.diagonalMinus, SmithCompletion.offDiagonal]\n'
NEGATIVE_POSITIVITY = 'import SmithCompletion\nexample : SmithCompletion.determinant (1/10) (1/2) = 0 := by\n  norm_num [SmithCompletion.determinant, SmithCompletion.diagonalPlus, SmithCompletion.diagonalMinus, SmithCompletion.offDiagonal]\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def capture(argv, *, cwd=None):
    return subprocess.check_output([str(x) for x in argv], cwd=cwd, stderr=subprocess.STDOUT)


def git_state(git, path):
    revision = capture([git, '-C', path, 'rev-parse', 'HEAD']).decode().strip()
    status = capture([git, '-C', path, 'status', '--porcelain', '--untracked-files=no']).decode().strip()
    return {'revision': revision, 'tracked_status': status}


def main():
    parser = argparse.ArgumentParser()
    for name in ('lean', 'mathlib', 'git', 'repo', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    lean, mathlib, git, repo, output = (getattr(args, name).resolve() for name in
                                        ('lean', 'mathlib', 'git', 'repo', 'output'))
    output.mkdir(parents=True, exist_ok=False)
    build = output / 'build'
    build.mkdir()
    names = ('SmithCompletion.lean', 'AxiomAudit.lean', 'replay.py')
    inputs = {name: digest((ROOT / name).read_bytes()) for name in names}
    inputs['dependency-lock.json'] = digest(LOCK.read_bytes())
    note = ROOT.parents[2] / 'docs/demonstrations/SMITH_SINGULAR_COMPLETION.md'
    inputs['SMITH_SINGULAR_COMPLETION.md'] = digest(note.read_bytes())
    lock = json.loads(LOCK.read_bytes())
    version = capture([lean, '--version']).decode().strip()
    if 'version 4.34.0-rc2' not in version or digest(lean.read_bytes()) != LEAN_SHA256:
        raise RuntimeError('Lean compiler differs from the pinned version')
    if digest((mathlib / 'lake-manifest.json').read_bytes()) != lock['mathlib_manifest_sha256']:
        raise RuntimeError('Mathlib manifest differs from the dependency lock')
    dependencies = {'mathlib': git_state(git, mathlib)}
    if dependencies['mathlib']['revision'] != lock['mathlib_revision']:
        raise RuntimeError('Mathlib revision differs from the dependency lock')
    for package in lock['packages']:
        name = package['name']
        dependencies[name] = git_state(git, mathlib / '.lake/packages' / name)
        if dependencies[name]['revision'] != package['rev']:
            raise RuntimeError('Dependency revision differs from the lock: ' + name)
    if any(value['tracked_status'] for value in dependencies.values()):
        raise RuntimeError('A pinned dependency has tracked modifications')
    archive = capture([git, '-C', repo, 'show', SOURCE_REVISION + ':' + ARCHIVE_PATH])
    if digest(archive) != ARCHIVE_SHA256:
        raise RuntimeError('Retained research archive differs from its source binding')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        if digest(z.read(THEOREM_PATH)) != THEOREM_SHA256:
            raise RuntimeError('Archived theorem note differs from its source binding')

    libraries = [mathlib / '.lake/build/lib/lean'] + [
        mathlib / '.lake/packages' / item['name'] / '.lake/build/lib/lean' for item in lock['packages']]
    imports = re.findall(r'(?m)^import\s+(Mathlib\.[A-Za-z0-9_.]+)\s*$',
                         (ROOT / names[0]).read_text(encoding='utf-8'))
    objects = {}
    for module in sorted(set(imports)):
        relative = Path(*module.split('.')).with_suffix('.olean')
        matches = [directory / relative for directory in libraries if (directory / relative).is_file()]
        if len(matches) != 1:
            raise RuntimeError('Expected one cached object for ' + module)
        objects[module] = {'path': matches[0], 'sha256': digest(matches[0].read_bytes())}
    for name in names[:2]:
        text = (ROOT / name).read_text(encoding='utf-8')
        if re.search(r'\b(?:sorry|admit)\b|^\s*(?:axiom|unsafe)\s', text, re.MULTILINE):
            raise RuntimeError('Placeholder or additional axiom in ' + name)
        shutil.copyfile(ROOT / name, build / name)
    (build / 'WrongFeasibility.lean').write_text(NEGATIVE_CONTROL, encoding='utf-8', newline='\n')
    (build / 'WrongDeterminant.lean').write_text(NEGATIVE_POSITIVITY, encoding='utf-8', newline='\n')
    env = os.environ.copy()
    env['LEAN_PATH'] = os.pathsep.join(str(path) for path in [build, *libraries])
    steps = []

    def run(name, arguments, expected_success):
        result = subprocess.run([str(lean), '-j1', '-DwarningAsError=true', *arguments], cwd=build,
                                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output / (name + '.stdout.txt')).write_bytes(result.stdout)
        (output / (name + '.stderr.txt')).write_bytes(result.stderr)
        steps.append({'name': name, 'arguments': arguments, 'exit_code': result.returncode,
                      'stdout_sha256': digest(result.stdout), 'stderr_sha256': digest(result.stderr)})
        if (result.returncode == 0) != expected_success:
            raise RuntimeError('Unexpected result for ' + name)
        return (result.stdout + result.stderr).decode('utf-8', errors='replace')

    run('compile', ['-o', 'SmithCompletion.olean', 'SmithCompletion.lean'], True)
    audit = run('axioms', ['AxiomAudit.lean'], True)
    wanted = re.findall(r'(?m)^#print axioms\s+(\S+)', (ROOT / names[1]).read_text(encoding='utf-8'))
    found = re.findall(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", audit)
    if [name for name, _ in found] != wanted:
        raise RuntimeError('Axiom audit output differs from the requested declarations')
    axioms = {name: [item.strip() for item in values.split(',') if item.strip()] for name, values in found}
    if any(not set(values) <= ALLOWED_AXIOMS for values in axioms.values()):
        raise RuntimeError('Unexpected axioms in a checked declaration')
    negative = run('wrong-feasibility', ['WrongFeasibility.lean'], False)
    if 'error:' not in negative:
        raise RuntimeError('The negative control did not report a proof error')
    negative = run('wrong-determinant', ['WrongDeterminant.lean'], False)
    if 'error:' not in negative:
        raise RuntimeError('The positivity negative control did not report a proof error')
    after = {name: digest((ROOT / name).read_bytes()) for name in names}
    after['dependency-lock.json'] = digest(LOCK.read_bytes())
    after['SMITH_SINGULAR_COMPLETION.md'] = digest(note.read_bytes())
    if inputs != after or any(digest(value['path'].read_bytes()) != value['sha256'] for value in objects.values()):
        raise RuntimeError('An input or imported object changed during replay')
    if dependencies != {'mathlib': git_state(git, mathlib), **{
        item['name']: git_state(git, mathlib / '.lake/packages' / item['name']) for item in lock['packages']}}:
        raise RuntimeError('A dependency changed during replay')
    receipt = {'status': 'PASS', 'lean': {'version': version, 'sha256': LEAN_SHA256},
               'input_sha256': inputs, 'dependencies': dependencies,
               'source_binding': {'revision': SOURCE_REVISION, 'archive': ARCHIVE_PATH,
                                  'archive_sha256': ARCHIVE_SHA256, 'theorem_note': THEOREM_PATH,
                                  'theorem_note_sha256': THEOREM_SHA256},
               'direct_mathlib_object_sha256': {name: value['sha256'] for name, value in objects.items()},
               'steps': steps, 'audited_axioms': axioms,
               'negative_controls': ['The false feasibility claim at (1/10,1/2) was rejected.',
                                     'The false zero-determinant claim at (1/10,1/2) was rejected.'],
               'limits': ['Uses pinned precompiled dependencies; transitive objects are not rebuilt or exhaustively hashed.',
                          'Source mapping and mathematical review are self-review.',
                          'Only the real quadratic zero-corner lemma, determinant formulas, saturated-packet criterion and two exact examples are formalized.']}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS: completion boundary lemmas, axiom audit, source binding, and negative controls')


if __name__ == '__main__':
    main()
