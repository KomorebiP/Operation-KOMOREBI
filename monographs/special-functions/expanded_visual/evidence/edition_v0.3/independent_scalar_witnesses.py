"""Exact finite scalar q-Racah collapse and shifted Askey-Wilson witnesses.

These checks use only fractions.Fraction, without importing the author code.
They do not establish a scalar-to-matrix recoupling parameter dictionary.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def shifted_factor(a, q, count):
    return math.prod((1-a*q**r for r in range(count)),start=F(1))


def racah(n, y, a, b, c, d, q):
    return sum(shifted_factor(q**(-n),q,r)*shifted_factor(a*b*q**(n+1),q,r)
               *shifted_factor(q**(-y),q,r)*shifted_factor(c*d*q**(y+1),q,r)
               /(shifted_factor(a*q,q,r)*shifted_factor(b*d*q,q,r)
                 *shifted_factor(c*q,q,r)*shifted_factor(q,q,r))*q**r
               for r in range(min(n,y)+1))


def aw(n, z, a, b, c, d, q):
    return sum(shifted_factor(q**(-n),q,r)*shifted_factor(a*b*c*d*q**(n-1),q,r)
               *shifted_factor(a*z,q,r)*shifted_factor(a/z,q,r)
               /(shifted_factor(a*b,q,r)*shifted_factor(a*c,q,r)
                 *shifted_factor(a*d,q,r)*shifted_factor(q,q,r))*q**r
               for r in range(n+1))


def shifted_operator(f,z,a,b,c,d,q):
    def coefficient(value):
        return math.prod((1-p*value for p in (a,b,c,d)),start=F(1)) / ((1-value**2)*(1-q*value**2))
    return (coefficient(z)*(f(q*z)-f(z))+coefficient(1/z)*(f(z/q)-f(z))
            +(1+a*b*c*d/q)*f(z))


def main():
    q,a,b,c,d = F(1,2),F(1,2),F(1,2),F(4),F(1)
    lattice = [q**(-y)+c*d*q**(y+1) for y in (0,1)]
    rows = [[racah(n,y,a,b,c,d,q) for y in (0,1)] for n in (0,1)]
    assert lattice == [F(3),F(3)] and rows == [[F(1),F(1)],[F(1),F(1)]]
    result = {'q_Racah_collapsed_lattice':{'exact':True,'q':'1/2','N':1,
        'parameters':list(map(str,(a,b,c,d))),'lattice':list(map(str,lattice)),
        'rows':[list(map(str,row)) for row in rows],
        'positive_orthogonality_obstruction':'The two rows have inner product w0+w1>0 for any positive weights.'}}
    q = F(7,10)
    parameters = (F(1,5),F(3,10),F(-1,4),F(2,5))
    points = [F(1,3),F(2,3),F(4,3),F(5,3)]
    checks = []
    for degree in range(6):
        f = lambda z,degree=degree:aw(degree,z,*parameters,q)
        eigenvalue = q**(-degree)+math.prod(parameters)*q**(degree-1)
        for point in points:
            residual = shifted_operator(f,point,*parameters,q)-eigenvalue*f(point)
            assert residual == 0
            checks.append({'degree':degree,'z':str(point),'exact_residual':'0'})
    result['Askey_Wilson_shifted_operator'] = {'exact':True,'q':str(q),
        'parameters':list(map(str,parameters)),
        'convention':'D f = A(z)(f(qz)-f(z)) + A(1/z)(f(z/q)-f(z)) + (1+abcd/q)f(z)',
        'eigenvalue':'q^(-n)+abcd*q^(n-1)',
        'degree_zero_eigenvalue':str(1+math.prod(parameters)/q),
        'checks':checks,'scope':'24 exact rational point witnesses, not a universal identity proof'}
    result['all_passed'] = True
    target = ROOT/'evidence'/'independent_scalar_run'/'results.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all_passed':True,'exact_Askey_Wilson_witnesses':len(checks)}))


if __name__ == '__main__':
    main()
