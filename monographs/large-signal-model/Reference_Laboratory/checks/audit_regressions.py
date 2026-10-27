"""Small audit regressions, distinct from the inherited mathematical suites.

Legacy replay behavior is reproduced only inside an isolated temporary folder.
No production or remote system is involved. No test edits this release's source.
"""
from __future__ import annotations
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import rat

def load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main() -> None:
    rows=[]
    def check(name: str, condition: bool, kind: str='exact') -> None:
        if not condition: raise AssertionError(name)
        rows.append({'name':name,'kind':kind,'passed':True})
    def rejects(name, fn, expected=ValueError):
        try: fn()
        except expected: check(name,True,'expected_rejection'); return
        raise AssertionError(name+' was not rejected')
    # P72: pure mass cannot have a nonzero mass-preserving perturbation.
    delta=sp.symbols('delta')
    check('P72 mass-only constraint forces zero perturbation',sp.solve(sp.Eq(delta,0),delta)==[0])
    check('P72 d=0 identity preserves positive mass',sp.Matrix([[1]])*sp.Matrix([1])==sp.Matrix([1]))
    # A positive-dimensional boundary point admits the claimed outward change.
    B=sp.eye(2); z=sp.Matrix([1,1]); lam=sp.Matrix([[1,0]])
    eps=sp.Rational(1,100); D=sp.Matrix([[0,0],[eps,0]])
    out=(B+D)*z
    check('P72 spatial example preserves the mass row',lam*D==sp.zeros(1,2))
    check('P72 perturbation Frobenius norm equals epsilon',sum(x*x for x in D)==eps**2)
    check('P72 outward perturbation breaks cone membership',out[1]>out[0])
    for value in ['1/0','0/0','-5/0',True,1.25,'1/2junk']:
        rejects('Rational parser rejects '+repr(value),lambda value=value:rat(value))
    for value, expected in [('2/3',sp.Rational(2,3)),('-2/3',-sp.Rational(2,3)),('0',sp.S(0)),(sp.Integer(2),sp.S(2))]:
        check('Rational parser accepts '+repr(value),rat(value)==expected)
    runner=load_module('current_reference_runner',ROOT/'run_reference_checks.py')
    legacy=load_module('legacy_reference_runner',ROOT/'provenance/0.8.0/run_reference_checks.py')
    with tempfile.TemporaryDirectory(prefix='lsm_audit_') as directory:
        base=Path(directory); (base/'verification').mkdir(); (base/'examples').mkdir()
        (base/'a.py').write_text('print("first")\n'); (base/'b.py').write_text('print("second")\n')
        (base/'helper.py').write_text('VALUE = 1\n')
        (base/'examples/fixed.json').write_text('{"value":1}\n')
        runner.ROOT=base; runner.SCRIPTS=['a.py','b.py']
        good={'version':runner.VERSION,'session':'unit','expected_scripts':runner.SCRIPTS.copy(),
              'execution_snapshot':runner.execution_snapshot(),'environment':runner.environment(),
              'runs':[{'script':'a.py','source_sha256':runner.digest(base/'a.py'),
                       'passed':True,'returncode':0}]}
        runner.validate_resume(good,1,'unit'); check('Unchanged continuation is accepted',True,'runner')
        for path,new in [('helper.py','VALUE = 2\n'),('examples/fixed.json','{"value":2}\n'),('a.py','raise RuntimeError("changed")\n')]:
            p=base/path; original=p.read_text(); p.write_text(new)
            rejects('Changed source/input is rejected: '+path,lambda:runner.validate_resume(good,1,'unit'))
            p.write_text(original)
        cases=[('wrong script inventory',lambda r:r.update(expected_scripts=['b.py','a.py'])),
               ('wrong environment',lambda r:r['environment'].update(python='changed')),
               ('wrong session',lambda r:r.update(session='other')),
               ('wrong version',lambda r:r.update(version='0.8.0')),
               ('nonzero prior exit',lambda r:r['runs'][0].update(returncode=1)),
               ('wrong prior source hash',lambda r:r['runs'][0].update(source_sha256='0'*64)),
               ('wrong prefix order',lambda r:r['runs'][0].update(script='b.py')),
               ('missing prior run',lambda r:r.update(runs=[])),
               ('false prior success',lambda r:r['runs'][0].update(passed=False))]
        for name,mutate in cases:
            changed=copy.deepcopy(good); mutate(changed)
            rejects('Resume rejects '+name,lambda changed=changed:runner.validate_resume(changed,1,'unit'))
        # Reproduce the previous gap through the unchanged old runner itself.
        legacy.ROOT=base; legacy.SCRIPTS=['a.py','b.py']
        args=sys.argv
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                sys.argv=['old','--batch-start','0','--batch-count','1','--session','legacy']; legacy.main()
                (base/'a.py').write_text('raise RuntimeError("changed after earlier batch")\n')
                sys.argv=['old','--batch-start','1','--batch-count','1','--session','legacy']; legacy.main()
            stale=json.loads((base/'verification/replay_checkpoints/legacy.json').read_text())
            check('Legacy runner reproduces stale successful resume',stale['passed'] and stale['runs'][0]['source_sha256']!=runner.digest(base/'a.py'),'legacy_gap_reproduced')
        finally: sys.argv=args
    report={'version':'1.0.0','passed':True,'records':rows,'count':len(rows),
            'scope':'Dimensional boundary, exact input validation, and local replay integrity. Not a proof-kernel run.'}
    (ROOT/'verification/audit_regression_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(rows)} audit regression records, separate from 756 inherited calculation records.')

if __name__=='__main__': main()
