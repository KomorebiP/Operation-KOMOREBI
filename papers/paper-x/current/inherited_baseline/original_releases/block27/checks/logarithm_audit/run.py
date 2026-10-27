"""Rebuild the audited sources with isolated new proof objects, then discard them."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'checks'))
from lean_env import lean_env

NEW_MODULES = set(json.loads((ROOT/'provenance.json').read_text())['new_modules'])
MODULES = []
ACTIVE = set()

def visit(module):
    if module in MODULES:
        return
    assert module not in ACTIVE, 'Cycle in new-module imports'
    ACTIVE.add(module)
    source = (ROOT/'lean/PaperX'/f'{module}.lean').read_text()
    for dependency in re.findall(r'^import PaperX\.(\w+)', source, re.M):
        if dependency in NEW_MODULES:
            visit(dependency)
    ACTIVE.remove(module)
    MODULES.append(module)

for module in sorted(NEW_MODULES):
    visit(module)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    kit = Path(sys.argv[1]).resolve()
    lean, env = lean_env(kit)
    before = {m: sha(ROOT / 'lean/PaperX' / (m + '.lean')) for m in MODULES}
    records = []
    with tempfile.TemporaryDirectory(prefix='logarithm-audit-', dir=ROOT) as tmp:
        cache = Path(tmp)
        (cache / 'PaperX').mkdir()
        # Lean resolves the namespace directory as a unit; make predecessor
        # objects visible here rather than relying on a second PaperX path.
        for obj in (ROOT/'build/PaperX').glob('*.olean'):
            if obj.stem not in MODULES:
                (cache/'PaperX'/obj.name).symlink_to(obj)
        env['LEAN_PATH'] = str(cache) + os.pathsep + env['LEAN_PATH']
        for m in MODULES:
            cmd = [lean, '-DwarningAsError=true', '-o', str(cache / 'PaperX' / (m + '.olean')),
                   str(ROOT / 'lean/PaperX' / (m + '.lean'))]
            start = time.monotonic()
            p = subprocess.run(cmd, cwd=ROOT/'lean', env=env, text=True, capture_output=True, timeout=240)
            logfile = OUT / (m + '.log')
            logfile.write_text(p.stdout + p.stderr)
            records.append({'module':m, 'exit_code':p.returncode,
                            'seconds':round(time.monotonic()-start, 4),
                            'source_sha256':before[m], 'log':str(logfile.relative_to(ROOT)),
                            'log_sha256':sha(logfile)})
            if p.returncode:
                (OUT/'compile.json').write_text(json.dumps({'passed':False,'compilations':records},indent=2)+'\n')
                raise SystemExit(p.returncode)
        probe = OUT / 'BoundaryApplications.lean'
        p = subprocess.run([lean, '-DwarningAsError=true', str(probe)], cwd=ROOT/'lean', env=env,
                           text=True, capture_output=True, timeout=240)
        logfile = OUT/'BoundaryApplications.log'
        logfile.write_text(p.stdout+p.stderr)
        records.append({'module':'BoundaryApplications', 'exit_code':p.returncode,
                        'source_sha256':sha(probe), 'log':str(logfile.relative_to(ROOT)),
                        'log_sha256':sha(logfile)})
        if p.returncode:
            (OUT/'compile.json').write_text(json.dumps({'passed':False,'compilations':records},indent=2)+'\n')
            raise SystemExit(p.returncode)
    after = {m: sha(ROOT / 'lean/PaperX' / (m + '.lean')) for m in MODULES}
    if before != after:
        changes = {m:{'before':before[m], 'after':after[m]} for m in MODULES if before[m] != after[m]}
        (OUT/'compile.json').write_text(json.dumps({'passed':False, 'source_hashes_unchanged':False,
          'failure':'An audited source changed during compilation', 'changes':changes,
          'compilations':records},indent=2)+'\n')
        raise SystemExit('An audited source changed during compilation')
    axioms = set()
    for group in re.findall(r'depends on axioms: \[(.*?)\]', logfile.read_text()):
        axioms.update(x.strip() for x in group.split(','))
    assert axioms <= {'propext','Classical.choice','Quot.sound'}
    result = {'passed': True, 'scope':f'{len(MODULES)} new sources rebuilt into isolated temporary proof objects; boundary applications imported those objects. Predecessor proof objects were linked from the established build. The temporary objects were discarded after checking.',
              'source_hashes_unchanged':True, 'lean_binary_sha256':sha(lean),
              'compilations': records, 'printed_boundary_axioms':sorted(axioms),
              'no_full_predecessor_rebuild_claim':True}
    (OUT/'compile.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'production_sources':len(MODULES),'boundary_applications':1}))

if __name__ == '__main__':
    main()
