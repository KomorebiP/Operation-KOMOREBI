#!/usr/bin/env python3
"""Reproduce the documented bounded Space examples, without source edits."""
from pathlib import Path
from fractions import Fraction as F
import datetime
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / sys.argv[1]
COMMANDS = []
CHECKS = []

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check(name, passed, detail):
    row = {'name':name, 'passed':bool(passed), 'detail':detail}
    CHECKS.append(row)
    if not passed:
        raise AssertionError(name + ': ' + detail)

def command(name, args, expected=0, diagnostic=None):
    argv = [sys.executable, '-B', *args]
    start = time.monotonic()
    run = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=120)
    stdout = OUT / (name + '.stdout')
    stderr = OUT / (name + '.stderr')
    stdout.write_text(run.stdout)
    stderr.write_text(run.stderr)
    row = {'name':name, 'argv':argv, 'cwd':str(ROOT),
           'seconds':time.monotonic()-start, 'exit_status':run.returncode,
           'expected_exit_status':expected, 'timeout_seconds':120,
           'stdout':stdout.relative_to(ROOT).as_posix(), 'stdout_sha256':digest(stdout),
           'stderr':stderr.relative_to(ROOT).as_posix(), 'stderr_sha256':digest(stderr),
           'required_diagnostic':diagnostic,
           'passed':run.returncode == expected and (diagnostic is None or diagnostic in run.stderr)}
    COMMANDS.append(row)
    (OUT/'commands.json').write_text(json.dumps(COMMANDS,indent=2)+'\n')
    check(name, row['passed'], 'Exact expected exit code and, for rejection, intended diagnostic.')
    return run.stdout

def main():
    protected = json.loads(command('protected_demo',['examples/protected_repair.py','--demo']))
    check('protected_archived_demo', protected == json.loads((ROOT/'examples/three_preservation_problems.json').read_text()),
          'All three demonstration records match the preserved reference JSON.')
    check('protected_outcomes', [x['certificate']['status'] for x in protected] == ['feasible','feasible','obstructed'],
          'Unique feasible, affine feasible, and obstructed inputs remain distinguished.')
    budget = json.loads(command('budgeted_demo',['examples/budgeted_repair.py']))
    check('budgeted_archived_demo', budget == json.loads((ROOT/'examples/budgeted_repair_demo.json').read_text()),
          'All five declared demonstration sections match the preserved reference JSON.')
    approximation = json.loads(command('approximation_demo',['examples/approximation_models.py','--depth','16','--steps','10']))
    check('approximation_domain', len(approximation['polynomial_path']) == len(approximation['burst_path']) == 10 and
          approximation['diagonal_model']['N'] == 16 and len(approximation['diagonal_model']['exact_prefix']) == 16,
          'The executed command uses the documented depth16 and steps10 bounds.')
    check('polynomial_telescoping', all(F(r['residual']) - F(1,r['n']+2) == F(r['step']) for r in approximation['polynomial_path']),
          'Ten adjacent reciprocal differences agree with the recorded movement exactly.')
    check('diagonal_reference', approximation['diagonal_model']['squared_correction_norm'] == 16 and
          approximation['diagonal_model']['infinite_residual_square_lower'] == '1/17' and
          approximation['diagonal_model']['infinite_residual_square_upper'] == '1/16',
          'The fixed depth16 finite energy and written analytic-tail endpoints are evaluated correctly; the infinite inequality is not proved by this run.')
    inexact = json.loads(command('inexact_demo',['examples/inexact_repair_certificate.py']))
    check('inexact_archived_demo', inexact == json.loads((ROOT/'examples/inexact_repair_demo.json').read_text()),
          'Four demonstration certificates match preserved reference JSON, including scaled basis and full protection.')
    raw = command('worked_generate',['examples/inexact_repair_certificate.py','--input','inputs/proposal.json'])
    record = json.loads(raw)
    certificate_path = OUT/'worked_certificate.json'
    certificate_path.write_text(json.dumps(record,indent=2)+'\n')
    verified = json.loads(command('worked_verify',['examples/inexact_repair_certificate.py','--verify',certificate_path.relative_to(ROOT).as_posix()]))
    check('worked_verify_status', verified == {'status':'PASS','scope':'Exact finite certificate recomputation'},
          'The serialized proposal certificate is accepted after exact recomputation.')
    expected = {'candidate':['3/4','-1/4'], 'protected_before':['1'], 'protected_after':['1'],
                'fit_residual':['3/4'], 'actual_candidate_residual':['3/4'],
                'normal_residual':['-1/8','-1/8'], 'normal_residual_norm_squared':'1/32',
                'objective':'11/16', 'dual_value':'21/32', 'duality_gap':'1/32',
                'duality_gap_identity_residual':'0', 'correction_error_norm_squared_upper':'1/32',
                'fitted_error_norm_squared_upper':'1/128',
                'coordinate_covector_norm_squared_not_a_Hilbert_certificate':'1/16'}
    for field, value in expected.items():
        check('worked_field_'+field, record['certificate'][field] == value,
              'Exact hand-computable value printed in WORKED_EXAMPLE.md.')
    # Orthogonal scalar calculation: J(t)=(t-1)^2+2t^2, so J'(t)=6t-2.
    optimum, proposal = F(1,3), F(1,4)
    J = lambda t:(t-1)**2 + 2*t*t
    check('worked_scalar_optimum', 6*optimum-2 == 0 and 2*(proposal-optimum)**2 == F(1,72),
          'The fixed quadratic has optimum1/3 and exact squared correction error1/72.')
    check('worked_scalar_bounds', 2*(proposal-optimum)**2 <= F(record['certificate']['correction_error_norm_squared_upper']) and
          (proposal-optimum)**2 == F(1,144) <= F(record['certificate']['fitted_error_norm_squared_upper']),
          'The two stated squared-error upper bounds hold for this exact fixed example.')
    check('worked_scalar_objective_gap', J(proposal) == F(11,16) and J(proposal)-J(optimum) == F(1,48) <= F(1,32),
          'The actual objective excess1/48 lies below the certificate gap1/32.')
    command('reject_protected_change',['examples/inexact_repair_certificate.py','--input','inputs/invalid_protected_proposal.json'],
            expected=2, diagnostic='The proposed correction changes protected data')
    tampered = json.loads(json.dumps(record))
    tampered['certificate']['objective'] = '0'
    tampered_path = OUT/'tampered_certificate.json'
    tampered_path.write_text(json.dumps(tampered,indent=2)+'\n')
    command('reject_tampered_objective',['examples/inexact_repair_certificate.py','--verify',tampered_path.relative_to(ROOT).as_posix()],
            expected=2, diagnostic='A certificate claim differs from exact recomputation')
    command('visual_finite_checks',['tools/run_visual_checks.py'])
    visual = json.loads((ROOT/'build/visual_checks/computation_manifest.json').read_text())
    check('visual_recorded_checks', bool(visual['checks']) and all(x['passed'] for x in visual['checks']) and visual['inputs_unchanged'],
          'All existing finite visual-check records passed, and their source hashes stayed fixed.')
    outputs = []
    for base in [OUT, ROOT/'build', ROOT/'source']:
        if not base.exists():continue
        for p in sorted(base.rglob('*')):
            if p.is_file() and p.name not in ['manifest.json','summary.json','stdout.txt','stderr.txt']:
                outputs.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
    summary = {'status':'PASS','assertion_tested':'The documented finite example entry points reproduce their preserved reference records; the worked rational certificate agrees with its explicit values and scalar invariants; two specified invalid records are rejected for their intended reasons; the original sixteen-scene visual checks pass at their declared bounds.',
               'interpretation':'Documented results reproduced with an orthogonal exact scalar check of the worked certificate. This is not an independent universal implementation validation.',
               'commands':COMMANDS,'checks':CHECKS,
               'counts':{'documented_example_commands':4,'worked_generation_and_verification_commands':2,
                         'intended_rejection_commands':2,'visual_wrapper_commands':1,
                         'command_contracts':len(COMMANDS),'audit_checks':len(CHECKS),
                         'visual_checks':len(visual['checks']),'visual_scenes':16,
                         'worked_expected_fields':len(expected)},
               'visual_bounds':visual['mathematics']['bounds'],
               'visual_check_details':visual['checks'],
               'non_claims':['No universal Python-to-Lean refinement or extraction.',
                             'No general algorithmic efficiency or floating-point certification claim.',
                             'Finite tail evaluations do not prove infinite convergence or nonexistence.',
                             'Plot grids and layout checks are not independent theorem counts.'],
               'outputs':outputs}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'status':summary['status'],'counts':summary['counts']},indent=2))

if __name__ == '__main__':
    main()
