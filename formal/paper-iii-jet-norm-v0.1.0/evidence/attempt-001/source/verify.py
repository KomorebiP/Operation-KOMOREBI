#!/usr/bin/env python3
"""Cold-check the jet-norm companion against an existing, exact Mathlib cache.

No dependency checkout or cache is modified. Own objects and all diagnostics go
to a new external directory. Git and the matching sibling leanchecker are required.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parent
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO/'tools'))
from verify_lean_companion import (ALLOWED_AXIOMS, FORBIDDEN_DIAGNOSTICS,
    diagnostics_match, explicit_declarations, inventory_names, parse_axioms, source_inventory)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--mathlib', type=Path, required=True)
    parser.add_argument('--git', default='git')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()
    lean, mathlib, output = args.lean.resolve(), args.mathlib.resolve(), args.output.resolve()
    if output.exists() or output.is_relative_to(PROJECT):
        parser.error('Use a new evidence directory outside the companion')
    output.mkdir(parents=True)
    objects = output/'objects'
    objects.mkdir()
    config = json.loads((PROJECT/'verification.json').read_bytes())
    report = {'schema': 1, 'status': 'RUNNING', 'scope': config['scope'],
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'own_objects_initially_empty': True, 'checks': [],
              'verifier_sha256': digest(__file__),
              'shared_verifier_sha256': digest(REPO/'tools/verify_lean_companion.py')}
    env = os.environ.copy()
    for key in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME']:
        env.pop(key, None)
    env['PATH'] = str(lean.parent)+os.pathsep+env.get('PATH', '')
    deps = [mathlib/'.lake/build/lib/lean', *sorted((mathlib/'.lake/packages').glob('*/.lake/build/lib/lean'))]
    env['LEAN_PATH'] = os.pathsep.join(map(str, [objects, *deps]))
    env['LEAN_NUM_THREADS'] = '1'
    report['LEAN_PATH'] = env['LEAN_PATH']

    def save():
        (output/'run.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

    def run(name, command, cwd=PROJECT, expected=0, required=None, forbidden=(), errors=None):
        start = time.monotonic()
        try:
            result = subprocess.run(list(map(str, command)), cwd=cwd, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=args.timeout)
            text, code = result.stdout.decode('utf-8', errors='replace'), result.returncode
        except subprocess.TimeoutExpired as error:
            raw = error.stdout or b''
            text = raw.decode('utf-8', errors='replace') if isinstance(raw, bytes) else raw
            code = None
        log = output/(name+'.log')
        log.write_text(text, encoding='utf-8', newline='\n')
        passed = code == expected and diagnostics_match(text, required, forbidden, errors)
        report['checks'].append({'name': name, 'command': list(map(str, command)),
            'cwd': str(cwd), 'exit_code': code, 'expected_exit_code': expected,
            'passed': passed, 'seconds': time.monotonic()-start,
            'log': log.name, 'log_sha256': digest(log)})
        save()
        print(('PASS ' if passed else 'FAIL ')+name, flush=True)
        if not passed:
            raise RuntimeError(name+': '+text[-3500:])
        return text

    def compile_source(relative, name=None, expected=0, required=None):
        source = snapshot/relative
        obj = objects/Path(relative).with_suffix('.olean')
        obj.parent.mkdir(parents=True, exist_ok=True)
        return run(name or Path(relative).stem,
            [lean, '-j1', '-M4096', '-DwarningAsError=true', '-DautoImplicit=false',
             '-DrelaxedAutoImplicit=false', '-DmaxHeartbeats=4000000', '-o', obj, relative],
            cwd=snapshot, expected=expected, required=required,
            forbidden=FORBIDDEN_DIAGNOSTICS if expected else ('warning:',),
            errors=1 if expected else None)

    save()
    try:
        source_inventory(PROJECT, config)
        names = inventory_names(config)
        mapping = json.loads((PROJECT/'CLAIM_MAP.json').read_bytes())
        for pathkey, hashkey in [('source_file', 'source_file_sha256'), ('source_register', 'source_register_sha256')]:
            if digest(REPO/mapping[pathkey]) != mapping[hashkey]:
                raise RuntimeError('Changed manuscript or statement-register binding')
        support = mapping['reused_prerequisites']
        if [r['copy'] for r in support] != config['support_sources']:
            raise RuntimeError('Reused source inventory differs from claim map')
        for binding in support:
            if (digest(PROJECT/binding['copy']) != binding['sha256']
                    or digest(REPO/binding['original']) != binding['sha256']):
                raise RuntimeError('Reused source differs from the original edition')
        paths = sorted({*config['production'], *config['support_sources'], *config['audit_sources'],
                        'verification.json', 'CLAIM_MAP.json',
                        'lakefile.toml', 'lake-manifest.json', 'lean-toolchain', 'verify.py',
                        *[c['path'] for c in config['positive_controls']+config['setup_controls']+config['negative_controls']]})
        snapshot = output/'source'
        snapshot.mkdir()
        report['source_sha256'] = {}
        for path in paths:
            dest = snapshot/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT/path, dest)
            report['source_sha256'][path] = digest(dest)
        report['compiler'] = run('compiler', [lean, '--version'], required='6a10ac8c22beadecabdbb0919c2b50214762f91d').strip()
        report['compiler_sha256'] = digest(lean)
        if '4.34.0-rc2' not in report['compiler']:
            raise RuntimeError('Wrong compiler version')
        manifest = json.loads((PROJECT/'lake-manifest.json').read_bytes())
        report['dependencies'] = []
        for dep in manifest['packages']:
            folder = mathlib if dep['name']=='mathlib' else mathlib/'.lake/packages'/dep['name']
            head = run('pin_'+dep['name'], [args.git, '-C', folder, 'rev-parse', 'HEAD']).strip()
            run('clean_'+dep['name'], [args.git, '-C', folder, 'diff', '--quiet', 'HEAD', '--'])
            if head != dep['rev']:
                raise RuntimeError('Wrong dependency pin: '+dep['name'])
            report['dependencies'].append({'name': dep['name'], 'revision': head, 'tracked_clean': True})
        for relative in config['support_sources']+config['production']:
            compile_source(relative)
        owned = compile_source('audit/OwnedAudit.lean', 'owned_declarations', required='OWNED_AUDIT_PASS')
        report['owned_inventory'] = [json.loads(line.removeprefix('OWNED '))
                                     for line in owned.splitlines() if line.startswith('OWNED ')]
        report['reused_source_bindings'] = support
        audit = snapshot/'AxiomAudit.lean'
        audit.write_text('import '+config['library']+'\n'+''.join('#print axioms '+n+'\n' for n in names), encoding='utf-8')
        text = compile_source('AxiomAudit.lean', 'production_axioms')
        rows = parse_axioms(text)
        if ({r['name'] for r in rows} != set(names) or len(rows)!=len(names)
                or any(set(r['axioms'])-ALLOWED_AXIOMS for r in rows)):
            raise RuntimeError('Production axiom inventory mismatch')
        report['axioms'] = rows
        checker = lean.with_name('leanchecker.exe' if os.name=='nt' else 'leanchecker')
        run('kernel_replay', [checker, '--verbose', config['library']], cwd=snapshot)
        for control in config['positive_controls']:
            compile_source(control['path'])
        positive_names = [row['name'] for control in config['positive_controls']
                          for row in explicit_declarations(PROJECT, control['path'])]
        control_audit = ''.join('import '+c['path'].removesuffix('.lean').replace('/', '.')+'\n'
                                for c in config['positive_controls'])
        control_audit += ''.join('#print axioms '+n+'\n' for n in positive_names)
        (snapshot/'ControlAxiomAudit.lean').write_text(control_audit, encoding='utf-8')
        control_rows = parse_axioms(compile_source('ControlAxiomAudit.lean', 'positive_control_axioms'))
        if ({r['name'] for r in control_rows} != set(positive_names)
                or len(control_rows)!=len(positive_names)
                or any(set(r['axioms'])-ALLOWED_AXIOMS for r in control_rows)):
            raise RuntimeError('Positive-control axiom inventory mismatch')
        report['positive_control_axioms'] = control_rows
        for control in config['setup_controls']:
            compile_source(control['path'])
        for control in config['negative_controls']:
            compile_source(control['path'], expected=1, required=control['diagnostic'])
        for path, sha in report['source_sha256'].items():
            if digest(PROJECT/path)!=sha or digest(snapshot/path)!=sha:
                raise RuntimeError('Source changed during verification: '+path)
        report.update(status='PASS', theorem_count=sum(r['kind']=='theorem' for r in config['declarations']),
            audited_declarations=len(names), negative_controls_rejected=len(config['negative_controls']),
            axiom_union=sorted({a for r in rows for a in r['axioms']}),
            owned_declarations=len(report['owned_inventory']),
            kernel_scope='Fresh companion modules and four unchanged retained prerequisite modules replayed with the same official Lean kernel against pinned imported environments; not an independent kernel or a fresh replay of the entire sixteen-module Paper III core.')
    except Exception as error:
        report.update(status='FAIL', error=str(error))
        print('FAILED: '+str(error), flush=True)
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
