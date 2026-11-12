"""Exact member regression and adversarial controls. Author: Komorebi P."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from deterministic_family import synthesize, MAX_DEGREE
from composition_certificate import verify_composition_certificate

if not __debug__:
    raise RuntimeError('Run with assertions enabled')


def main():
    inputs = sorted([ROOT/'family.json', ROOT/'frozen_targets.json', ROOT/'deterministic_family.py',
                     Path(__file__).resolve()] + list((ROOT/'kernel').glob('*.py')))
    before = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    fixture = json.loads((ROOT/'frozen_targets.json').read_bytes())
    family = json.loads((ROOT/'family.json').read_bytes())
    accepted = []
    first = None
    for row in fixture['targets']:
        result = synthesize(row['target'])
        assert result['status'] == 'CERTIFIED', (row['id'], result)
        check = verify_composition_certificate(result['certificate'], expected_target=row['target'], expected_budget=row['degree'])
        assert check['global_minimum_proved_by_degree'] and check['actual_storage'] == row['degree']
        assert check['resistors'] == row['degree'] + 1
        assert check['physical_branch_count'] == 2*row['degree']+1
        assert all(branch['type'] in {'g','h','c'} for branch in check['rebuilt_graph']['branches'])
        accepted.append({'id':row['id'],'degree':row['degree'],'physical_branches':check['physical_branch_count'],'status':'PASS'})
        if first is None:
            first = result
    controls = []
    def classified(name, target, expected, **kwargs):
        result = synthesize(target, **kwargs)
        assert result['status'] == expected, (name, result)
        controls.append({'name':name,'status':expected})
    base = deepcopy(fixture['targets'][0]['target'])
    common_scaled = {key:[str(-F(13,5)*F(v)) for v in values] for key,values in base.items()}
    classified('negative_common_representation_scale', common_scaled, 'CERTIFIED')
    for j in range(7):
        y = list(map(F, family['target_box']['center']))
        y[j] += 2*F(family['target_box']['radii'][j])
        classified('outside_core_coordinate_'+str(j), {'P':list(map(str,y[:4])),'Q':list(map(str,y[4:]+[F(1)]))}, 'OUTSIDE_CERTIFIED_FAMILY')
    classified('realizable_resistor_outside_family', {'P':['2'],'Q':['1']}, 'OUTSIDE_CERTIFIED_FAMILY')
    bad = deepcopy(base); bad['P'][0] = 1.0
    classified('floating_point_input', bad, 'INVALID_INPUT')
    bad = deepcopy(base); bad['Q'] = ['0']
    classified('zero_denominator', bad, 'INVALID_INPUT')
    bad = deepcopy(family); bad['preconditioner'][0] = deepcopy(bad['preconditioner'][1])
    classified('singular_family_preconditioner', base, 'INVALID_FAMILY_CERTIFICATE', family=bad)
    high = {'P':['1']+['0']*MAX_DEGREE+['1'], 'Q':['2']+['0']*MAX_DEGREE+['1']}
    classified('degree_resource_scope', high, 'UNKNOWN')
    for label, mutate in [('wrong_target',lambda c:c['target']['P'].__setitem__(0,str(F(c['target']['P'][0])+1))),
                          ('negative_leaf_parameter',lambda c:c['expression']['certificate']['center'].__setitem__(0,'-1'))]:
        bad = deepcopy(first['certificate']); mutate(bad)
        try:
            verify_composition_certificate(bad, expected_target=base, expected_budget=3)
        except ValueError:
            controls.append({'name':label,'status':'REJECTED'})
        else:
            raise AssertionError('Consumer accepted corrupted witness: '+label)
    after = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    assert before == after
    print(json.dumps({'status':'PASS','author':'Komorebi P.','frozen_exact_member_regressions':accepted,
        'controls':controls,'inputs_unchanged':True,'input_sha256':before,
        'scope':'Exact recognition of one certified family and replay of its witnesses; no general-target discovery or novelty claim'},indent=2))


if __name__ == '__main__':
    main()
