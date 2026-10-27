"""Independent exact finite examples and low-order numerical caption checks.

No author figure module is imported. These witnesses do not prove the source
asymptotic theorems and do not certify floating-point interval arithmetic.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import math
import sys
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[1]


def bernoulli_numbers(degree):
    numbers = [F(1)]
    for n in range(1, degree+1):
        numbers.append(-sum(F(math.comb(n+1,j))*numbers[j]
                            for j in range(n))/F(n+1))
    return numbers


def bernoulli_poly(degree, x):
    numbers = bernoulli_numbers(degree)
    return sum(F(math.comb(degree,j))*numbers[j]*x**(degree-j)
               for j in range(degree+1))


def energy_stencil(depth):
    return sum((-1)**j*math.comb(2*depth,j)*float(zeta(4+2*j,1)/zeta(8+4*j,1))
               for j in range(2*depth+1))


def main():
    result = {}
    parent = 2**3*bernoulli_poly(4,F(2,3))
    children = [4**3*bernoulli_poly(4,x) for x in (F(1,3),F(5,6))]
    assert parent == F(52,405) and children == [F(416,405),F(-364,405)]
    assert sum(children) == parent
    result['Bernoulli_refinement_I06'] = {'exact':True,'parent':str(parent),
                                         'children':list(map(str,children))}
    a = F(1,2)
    binary_children = [4*bernoulli_poly(3,(a+j)/2) for j in range(2)]
    assert binary_children == [F(3,16),F(-3,16)]
    result['Bernoulli_Euler_I08'] = {'exact':True,
        'children':list(map(str,binary_children)),
        'unnormalized_low':str(sum(binary_children)),
        'unnormalized_high':str(binary_children[0]-binary_children[1])}
    triples = [3**7*bernoulli_poly(8,F(j,3)) for j in range(3)]
    assert triples == [F(-729,10),F(1093,30),F(1093,30)]
    detail = triples[0]-triples[1]
    assert detail == F(-328,3) and detail*detail == F(107584,9)
    result['cyclotomic_even_I10'] = {'exact':True,'children':list(map(str,triples)),
                                   'detail':str(detail),'norm':str(detail*detail)}
    packet_bounds = []
    for r in range(3):
        first = F(8**22,math.factorial(66+r))
        ratio = F(8,(67+r)*(68+r)*(69+r))
        packet_bounds.append(float(first/(1-ratio)))
    unmatched = float(F(8**22,math.factorial(65)))
    assert max(packet_bounds) < 1e-72 and unmatched < 1e-71
    result['I04_truncation_constants'] = {'analytic_geometric_tail_bounds':packet_bounds,
                                         'unmatched_row_bound':unmatched,
                                         'terms':22,'u_range':[0,8]}
    E0, E1, E2 = [energy_stencil(k) for k in range(3)]
    xi = E1/E0
    det = E0*E2-E1*E1
    pole, residue = 1/xi,-E0/xi
    assert abs(E0-105/math.pi**4)<1e-14
    assert abs(E1-.04780461034)<5e-12
    assert abs(det-.03026887920)<5e-12
    assert 0<xi<5/48<9/16 and residue<0
    result['low_order_positive_moments'] = {'arithmetic':'SciPy IEEE-754 double precision',
        'E0':E0,'E1':E1,'E2':E2,'H1_determinant':det,
        'one_node':xi,'one_node_pole':pole,'one_node_z_residue':residue}
    A = 3/(2**2.5*math.pi**1.5)
    result['source_asymptotic_constants'] = {'A':A,'cusp':2*math.sqrt(math.pi)*A,
        'role':'independent evaluation of stated constants, not an asymptotic proof'}
    result['all_passed'] = True
    output = ROOT/(sys.argv[1] if len(sys.argv)>1 else 'evidence/independent_arithmetic_run/results.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all_passed':True,'output':str(output.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
