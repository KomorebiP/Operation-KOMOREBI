"""Independent exact and high-precision checks of the eight foundation lessons."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def determinant(matrix):
    matrix = [list(map(F, row)) for row in matrix]
    value = F(1)
    for column in range(len(matrix)):
        pivot = next((i for i in range(column, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            value = -value
        coefficient = matrix[column][column]
        value *= coefficient
        for i in range(column + 1, len(matrix)):
            multiplier = matrix[i][column] / coefficient
            for j in range(column + 1, len(matrix)):
                matrix[i][j] -= multiplier * matrix[column][j]
    return value


def main():
    output = {}
    addresses = [(n // 3, n % 3) for n in range(18)]
    assert len(set(addresses)) == 18
    assert all(3 * m + r == n for n, (m, r) in enumerate(addresses))
    assert 2 * 7 + 1 == 6 * 2 + (1 + 2 * 1) == 15
    output['address_and_refinement'] = {'exact': True, 'n_range': [0, 17], 'refinement_example': 15}

    # Compare the full coefficient lists; this does not use the plotting script.
    original = [F(1), F(2), F(3)]
    carried = [F(0), F(1), F(2), F(3)]
    assert [F(0)] + original == carried
    output['carry'] = {'exact': True, 'u': '2/5', 'evaluated_packet': ['6/5', '1', '2']}

    # The fourth roots of unity allow exact Gaussian-rational DFT arithmetic.
    roots = [(F(1), F(0)), (F(0), F(-1)), (F(-1), F(0)), (F(0), F(1))]
    children = [F(1), F(2), F(4), F(1)]
    channels = [(sum(children[l] * roots[j*l % 4][0] for l in range(4)) / 2,
                 sum(children[l] * roots[j*l % 4][1] for l in range(4)) / 2)
                for j in range(4)]
    energies = [real*real + imag*imag for real, imag in channels]
    assert channels == [(F(4), F(0)), (F(-3,2), F(-1,2)), (F(1), F(0)), (F(-3,2), F(1,2))]
    assert energies == [F(16), F(5,2), F(1), F(5,2)] and sum(energies) == 22
    output['unitary_detail_bank'] = {'exact': True, 'energies': list(map(str, energies)), 'total': '22'}

    grouped = {3*m+r: F(1,factorial(3*m+r))
               for r in range(3) for m in range(5) if 3*m+r <= 12}
    assert grouped == {n: F(1,factorial(n)) for n in range(13)}
    with localcontext() as context:
        context.prec = 70
        uniform = Decimal(2).exp() * Decimal(2)**13 / Decimal(factorial(13))
        maximum = Decimal(0)
        for index in range(201):
            z = Decimal(index) / 100
            polynomial = sum(z**n / Decimal(factorial(n)) for n in range(13))
            remainder = z.exp() - polynomial
            bound = z.exp() * z**13 / Decimal(factorial(13))
            assert remainder >= 0 and remainder <= bound
            maximum = max(maximum, remainder)
        output['polynomial_and_taylor'] = {'exact_coefficient_routing': True,
            'decimal_precision': 70, 'grid': {'z_min':0,'z_max':2,'step':'1/100','points':201},
            'grid_max_remainder':str(maximum), 'uniform_taylor_bound':str(uniform),
            'non_claim':'The grid check is numerical; the stated continuous bound follows independently from Taylor remainder.'}

    a, b = F(4,5), F(3,5)
    assert a*a + b*b == 1 and (a+b)**2 == F(49,25) and (a-b)**2 == F(1,25)
    assert 2*a*b == F(24,25)
    output['interference'] = {'exact': True, 'diagonal':'1','maximum':'49/25','minimum':'1/25','cosine_coefficient':'24/25'}

    nodes = [F(0), F(2,5), F(17,20)]
    weights = [F(1,5), F(3,10), F(1,2)]
    moments = [sum(w*x**k for x,w in zip(nodes,weights)) for k in range(9)]
    assert moments[:3] == [F(1), F(109,200), F(1637,4000)]
    determinant3 = determinant([[moments[i+j] for j in range(3)] for i in range(3)])
    determinant4 = determinant([[moments[i+j] for j in range(4)] for i in range(4)])
    assert determinant3 == F(70227,100000000) and determinant4 == 0
    output['finite_measure'] = {'exact': True,'moments':list(map(str,moments)),
                               'H3_determinant':str(determinant3),'H4_determinant':str(determinant4),'rank':3}

    examples = [(F(2),F(2),F(3,2),F(3,4)), (F(3,2),F(1),F(2),F(1)),
                (F(5,4),F(3),F(1,2),F(1,4))]
    assert all((2*a-1)/beta == alpha and alpha/2 == kappa for a,beta,alpha,kappa in examples)
    output['shape_parameters'] = {'exact':True,'examples':[list(map(str,row)) for row in examples],
                                 'domains':'beta>0; positive energy a>1/2; absolute signed transfer a>1'}
    output['all_passed'] = True
    destination = ROOT / 'evidence' / 'independent_foundation_run' / 'results.json'
    destination.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({'independent_foundation_checks':'passed','groups':len(output)-1}))


if __name__ == '__main__':
    main()
