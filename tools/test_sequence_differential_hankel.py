"""Independent algebraic tests for arbitrary differential-order Hankel calculus.

Author: Komorebi P.
Tests use monomial differentiation, direct polynomial Chebyshev recursion,
independent rational Bareiss determinants and exact matrix rank.
"""
import sys
import unittest
from fractions import Fraction as F
from math import comb
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_differential_hankel import (
    chebyshev_derivative_polynomial, chebyshev_derivative_moment,
    derivative_monomial_moment, chebyshev_jet_gram_entry,
    chebyshev_jet_polynomials, chebyshev_jet_generators,
    first_nonzero_moment, structured_differential_hankel,
    algebraic_moment_generating_function, algebraic_moment_differential_equation,
    regularized_moment_ode, moments_from_algebraic_recurrence,
)
from sequence_polynomial_hankel import (
    structured_hankel_prefixes, power_to_falling,
)


def chebyshev(n):
    a,b=[2],[0,1]
    if n==0:return a
    if n==1:return b
    for _ in range(2,n+1):
        aa=a+[0]*(len(b)+1-len(a))
        shifted=[0]+b
        a,b=b,[shifted[k]-aa[k] for k in range(len(shifted))]
    return b


def derive(poly,k):
    p=list(poly)
    for _ in range(k):
        p=[p[j]*j for j in range(1,len(p))]
    return p


def multiply(p,q):
    if not p or not q:return []
    output=[0]*(len(p)+len(q)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(q):output[i+j]+=a*b
    return output


def direct_functional(poly,weights,operator):
    return sum(F(coeff)*derivative_monomial_moment(j,weights,operator)
               for j,coeff in enumerate(poly))


def direct_determinant(matrix):
    n=len(matrix)
    if n==0:return F(1)
    a=[[F(v) for v in row] for row in matrix]
    sign=1;previous=F(1)
    for k in range(n-1):
        if not a[k][k]:
            q=next((r for r in range(k+1,n) if a[r][k]),None)
            if q is None:return F(0)
            a[k],a[q]=a[q],a[k]
            sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                a[i][j]=(pivot*a[i][j]-a[i][k]*a[k][j])/previous
            a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def direct_hankel(weights,operator,n,lam=0):
    moments=[derivative_monomial_moment(k,weights,operator)
             for k in range(max(0,2*n-1))]
    if lam:
        moments=[sum(comb(m,k)*F(lam)**(m-k)*moments[k]
                     for k in range(m+1)) for m in range(len(moments))]
    return direct_determinant([[moments[i+j] for j in range(n)]
                               for i in range(n)])


def matrix_rank(matrix):
    a=[[F(v) for v in row] for row in matrix]
    if not a:return 0
    rank=0
    for col in range(len(a[0])):
        p=next((i for i in range(rank,len(a)) if a[i][col]),None)
        if p is None:continue
        a[rank],a[p]=a[p],a[rank]
        pivot=a[rank][col]
        for j in range(col,len(a[0])):a[rank][j]/=pivot
        for i in range(rank+1,len(a)):
            x=a[i][col]
            if x:
                for j in range(col,len(a[0])):a[i][j]-=x*a[rank][j]
        rank+=1
        if rank==len(a):break
    return rank


class DifferentialHankelTests(unittest.TestCase):
    def test_universal_algebraic_ogf_matches_independent_direct_moments(self):
        weights=([1],[0,1],[1,1],[2,-3,1],[0,0,1],
                 [1,0,2,-1],[0],
                 [F(1,3),F(-2,5),F(3,7)])
        operators=([1],[0,1],[1,2,1],[0,0,1],
                   [1,0,-2,3],[0],
                   [F(2,7),F(-3,8),0,F(1,5)])
        for a in weights:
            for c in operators:
                numerator,exponent_twice=algebraic_moment_generating_function(a,c)
                D=len(a)-1
                while D>0 and a[D]==0:D-=1
                R=len(c)-1
                while R>0 and c[R]==0:R-=1
                self.assertEqual(exponent_twice,2*(D+R)+1)
                self.assertLessEqual(len(numerator)-1,2*(D+R))
                beta=F(exponent_twice,2)
                series=[F(1)]
                for m in range(1,25):
                    series.append(series[-1]*4*(beta+m-1)/m)
                for n in range(42):
                    predicted=sum(
                        numerator[n-2*m]*series[m]
                        for m in range(n//2+1)
                        if 0<=n-2*m<len(numerator))
                    self.assertEqual(
                        predicted,derivative_monomial_moment(n,a,c),
                        (a,c,n))

    def test_universal_moment_first_order_ode(self):
        for a,c in (([1],[1]),([1,1],[1,2,1]),
                    ([0,1],[0,0,1]),([2,-3,1],[1,-2,3]),
                    ([F(1,2),F(2,3)],[F(3,4),0,F(-2,5)]),
                    ([1],[0,0,0]),([0],[1,2,3])):
            A,B=algebraic_moment_differential_equation(a,c)
            moments=[derivative_monomial_moment(n,a,c) for n in range(65)]
            for n in range(50):
                left=sum(
                    A[j]*(n-j+1)*moments[n-j+1]
                    for j in range(min(n+1,len(A)-1)+1))
                right=sum(
                    B[j]*moments[n-j]
                    for j in range(min(n,len(B)-1)+1))
                self.assertEqual(left,right,(a,c,n))
        numerator,power=algebraic_moment_generating_function(
            [1,1],[1,2,1])
        self.assertEqual(power,7)
        self.assertEqual(numerator,
                         (F(1),F(2),F(-8),F(-4),F(52),F(-16),F(-24)))

    def test_regularized_p_recursive_moments_agree_with_direct_definition(self):
        weights=([1],[0,1],[1,1],[2,-3,1],[0,0,1],
                 [1,0,2,-1],[0],
                 [F(1,3),F(-2,5),F(3,7)])
        operators=([1],[0,1],[1,2,1],[0,0,1],
                   [1,0,-2,3],[0],
                   [F(2,7),F(-3,8),0,F(1,5)])
        for a in weights:
            for c in operators:
                reconstructed=moments_from_algebraic_recurrence(a,c,91)
                self.assertEqual(len(reconstructed),91)
                for n,actual in enumerate(reconstructed):
                    self.assertEqual(actual,derivative_monomial_moment(n,a,c),
                                     (a,c,n))
                ell,A,B=regularized_moment_ode(a,c)
                if ell is None:
                    self.assertTrue(all(x==0 for x in reconstructed))
                    continue
                self.assertNotEqual(A[0],0)
                self.assertEqual(A[0],reconstructed[ell])
                D=len(a)-1
                while D>0 and a[D]==0:D-=1
                r=len(c)-1
                while r>0 and c[r]==0:r-=1
                self.assertLessEqual(len(A)-1,2*(D+r)-ell+2)
                for n in range(65):
                    t=lambda j: reconstructed[ell+j] if j>=0 else F(0)
                    lhs=sum(A[j]*(n-j+1)*t(n-j+1)
                            for j in range(min(n+1,len(A)-1)+1))
                    rhs=sum(B[j]*t(n-j)
                            for j in range(min(n,len(B)-1)+1))
                    self.assertEqual(lhs,rhs,(a,c,n,'regularized ODE'))
        self.assertEqual(
            moments_from_algebraic_recurrence([1,1],[1,2,1],10),
            [1,2,6,24,66,180,620,1120,4830,6300])
        self.assertEqual(regularized_moment_ode([0,1],[0,0,1])[0],4)
        self.assertEqual(regularized_moment_ode([1],[0,0])[0],None)

    def test_closed_chebyshev_products_at_all_parities(self):
        for d in range(4):
            a=[0]*d+[1]
            for k in range(7):
                p=chebyshev_derivative_polynomial(d,k)
                for n in range(29):
                    expected=direct_functional(derive(chebyshev(n),k),a,[1])
                    observed=chebyshev_derivative_moment(n,d,k)
                    self.assertEqual(observed,expected,(d,k,n,p))
                    if n and n%2!=k%2:
                        self.assertEqual(observed,0)
                    if n>0 and n>=k and n%2==k%2:
                        polynomial=sum(coefficient*n**(2*j+1)
                                       for j,coefficient in enumerate(p))
                        self.assertEqual(observed,polynomial)

    def test_weight_ladder_from_chebyshev_differential_equation(self):
        for k in range(7):
            for d in range(4):
                if d+k==0:continue
                for n in range(max(1,k),37):
                    if (n-k)%2:continue
                    x=chebyshev_derivative_moment(n,d,k)
                    y=chebyshev_derivative_moment(n,d+1,k)
                    self.assertEqual(4*(d+k)*y,(n*n-(k+2*d)**2)*x)

    def test_mixed_derivative_gram_factorization_and_rank(self):
        weights=([1],[0,1],[2,3],[1,-2,1],[0,0,1],
                 [F(1,2),F(2,3),F(-3,5)])
        operators=([1],[1,2],[1,0,1],[0,1,0,2],[1,2,-1,1],
                   [0,0,3],[2,0,-1,2])
        for a in weights:
            for c in operators:
                even,odd=chebyshev_jet_polynomials(tuple(map(F,a)),tuple(map(F,c)))
                rows,cols,diagonal=chebyshev_jet_generators(a,c,30)
                D=len(a)-1
                R=len(c)-1
                width=2*(D+R)
                self.assertTrue(all(len(row)==width for row in rows))
                for i in range(12):
                    for j in range(12):
                        expected=direct_functional(multiply(chebyshev(i),chebyshev(j)),a,c)
                        actual=chebyshev_jet_gram_entry(i,j,a,c)
                        self.assertEqual(actual,expected,(a,c,i,j))
                        if i==j:self.assertEqual(actual,diagonal[i])
                for i in range(18,30):
                    for j in range(14):
                        self.assertEqual(
                            sum(rows[i][k]*cols[j][k] for k in range(width)),
                            chebyshev_jet_gram_entry(i,j,a,c),(a,c,i,j))
                block=[[chebyshev_jet_gram_entry(i,j,a,c)
                        for j in range(14)] for i in range(18,30)]
                self.assertLessEqual(matrix_rank(block),width)

    def test_direct_exact_determinants_and_shift_invariance(self):
        cases=(
            ([1],[1,2,3]),([1,1],[1,2,1]),([0,1],[1,1,2]),
            ([2,-1,1],[1,-2,3,-1]),([1,0,1],[0,1,1]),
            ([0,0,1],[0,0,1]),([3,2],[1,0,0,1]),
            ([F(1,2),F(2,3)],[F(3,4),F(-1,2),F(2,5)]),
        )
        for a,c in cases:
            values=structured_differential_hankel(a,c,11)
            for n in range(12):
                self.assertEqual(values[n],direct_hankel(a,c,n),(a,c,n))
                self.assertEqual(values[n],direct_hankel(a,c,n,lam=2),
                                 (a,c,n,'binomial shift'))

    def test_initial_zero_block_including_missing_c0(self):
        for nu in range(4):
            for kappa in range(4):
                weights=[0]*nu+[2]
                operator=[0]*kappa+[3]
                first=first_nonzero_moment(weights,operator)
                ell=2*nu+kappa
                mass=F(3*2)*F(__import__('math').factorial(ell),
                              __import__('math').factorial(nu))
                self.assertEqual(first,(ell,mass))
                result=structured_differential_hankel(weights,operator,ell+2)
                self.assertEqual(result[:ell+1],[F(1)]+[F(0)]*ell)
                self.assertEqual(result[ell+1],
                                 (-1)**(ell*(ell+1)//2)*mass**(ell+1))
        self.assertIsNone(first_nonzero_moment([0],[1,2]))
        self.assertIsNone(first_nonzero_moment([1],[0,0]))
        self.assertEqual(structured_differential_hankel([0],[1],8),[1]+[0]*8)

    def test_first_order_specialization_agrees_with_previous_solver(self):
        for a in ([1],[0,1],[0,0,1],[2,-3,1],[1,2,3],
                  [F(1,2),F(-2,3),F(5,4)]):
            for c in (-2,-1,0,1,2):
                old=structured_hankel_prefixes(a,c,30)
                new=structured_differential_hankel(a,[1,c],30)
                self.assertEqual(new,old,(a,c))

    def test_parity_under_odd_derivative_sign_reversal(self):
        for a in ([1],[1,1],[0,0,1]):
            for c in ([1,2,3],[1,0,1,2],[0,1,0,-2]):
                opposite=[(-x if k%2 else x) for k,x in enumerate(c)]
                self.assertEqual(structured_differential_hankel(a,c,17),
                                 structured_differential_hankel(a,opposite,17))

    def test_long_prefixes_keep_small_schur_state(self):
        for a,c,N in (([1],[1,2,1],130),
                      ([0,1],[1,1,1],120),
                      ([2,3],[0,1,0,1],95)):
            values=structured_differential_hankel(a,c,N)
            self.assertEqual(len(values),N+1)
            for n in range(7):
                self.assertEqual(values[n],direct_hankel(a,c,n))


if __name__=='__main__':
    unittest.main()
