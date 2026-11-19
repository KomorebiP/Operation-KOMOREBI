"""Independent exact tests for the polynomial-weighted Hankel structure.

Author: Komorebi P.
Direct Chebyshev polynomial evaluation and Bareiss determinants are used as
independent oracles. No numerical root approximation is accepted as evidence.
"""
import sys
import unittest
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_polynomial_hankel import (
    power_to_falling, monomial_moment, chebyshev_even_moment,
    chebyshev_derivative_moment, chebyshev_gram_entry,
    chebyshev_transform_coefficients, semiseparable_generators,
    structured_hankel_prefixes, initial_nonsingular_formula,
)


def coefficients(poly):
    return [F(x) for x in poly]


def brute_chebyshev(size):
    seq=[[2], [0,1]]
    for n in range(2,size):
        shifted=[0]+seq[-1]
        previous=seq[-2]+[0]*(len(shifted)-len(seq[-2]))
        seq.append([shifted[k]-previous[k] for k in range(len(shifted))])
    return seq[:size]


def product(p,q):
    output=[F(0)]*(len(p)+len(q)-1)
    for i,x in enumerate(p):
        for j,y in enumerate(q):
            output[i+j]+=x*y
    return output


def derivative(p):
    return [p[k]*k for k in range(1,len(p))]


def functional(poly,weights,c=0):
    return sum(coefficient*monomial_moment(k,weights,c)
               for k,coefficient in enumerate(poly))


def bareiss(matrix):
    n=len(matrix)
    if n==0:return F(1)
    a=[[F(v) for v in row] for row in matrix]
    sign=1;previous=F(1)
    for k in range(n-1):
        if not a[k][k]:
            replacement=next((i for i in range(k+1,n) if a[i][k]),None)
            if replacement is None:return F(0)
            a[k],a[replacement]=a[replacement],a[k]
            sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                a[i][j]=(pivot*a[i][j]-a[i][k]*a[k][j])/previous
            a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def direct_hankel(weights,c,n,lam=0):
    terms=[monomial_moment(k,weights,c) for k in range(max(0,2*n-1))]
    if lam:
        terms=[sum(comb(m,k)*F(lam)**(m-k)*terms[k]
                   for k in range(m+1)) for m in range(len(terms))]
    return bareiss([[terms[i+j] for j in range(n)] for i in range(n)])


def exact_rank(matrix):
    if not matrix:return 0
    a=[[F(v) for v in row] for row in matrix]
    rows=len(a);cols=len(a[0]);rank=0
    for j in range(cols):
        pivot=next((i for i in range(rank,rows) if a[i][j]),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank]
        leading=a[rank][j]
        for k in range(j,cols):a[rank][k]/=leading
        for i in range(rank+1,rows):
            coeff=a[i][j]
            if coeff:
                for k in range(j,cols):a[i][k]-=coeff*a[rank][k]
        rank+=1
        if rank==rows:break
    return rank


class PolynomialHankelTests(unittest.TestCase):
    def test_power_basis_change_is_exact(self):
        for values in ([1],[0,1],[1,0,1],[7,-3,2,1],
                       [F(1,3),F(2,5),F(-3,7),F(1,11)]):
            a=power_to_falling(values)
            for m in range(0,18):
                original=sum(F(x)*m**k for k,x in enumerate(values))
                falling=sum(a[d]*(factorial(m)//factorial(m-d))
                            for d in range(min(m,len(a)-1)+1))
                self.assertEqual(original,falling)

    def test_algebraic_moment_generating_formula(self):
        # [z^(2m)] sum_d a_d (2d)!/d! z^(2d)
        #            * (1-4z^2)^(-d-1/2)
        cases=([1],[0,1],[0,0,1],[1,-2,3],
               [F(1,3),F(-2,5),F(3,7)])
        for a in cases:
            for m in range(29):
                coefficient=F(0)
                for d,weight in enumerate(a):
                    if m<d:continue
                    k=m-d
                    rising=F(1)
                    for j in range(k):
                        rising*=F(2*d+2*j+1,2)
                    coefficient+=(
                        F(weight)*F(factorial(2*d),factorial(d))*
                        F(4**k)*rising/factorial(k)
                    )
                self.assertEqual(
                    coefficient,monomial_moment(2*m,a,0),(a,m))
            for c in (-2,0,3):
                for m in range(14):
                    self.assertEqual(
                        monomial_moment(2*m+1,a,c),
                        F(c)*(2*m+1)*monomial_moment(2*m,a,0))

    def test_chebyshev_moments_and_derivatives_by_direct_expansion(self):
        poly=brute_chebyshev(35)
        for a in ([1],[0,1],[0,0,1],[1,-2,3],
                  [7,-3,2,-1,1],[F(1,2),F(-1,3),F(2,5)]):
            for k in range(0,35):
                if k%2==0:
                    expected=functional(poly[k],a)
                    self.assertEqual(chebyshev_even_moment(k,a),expected,(a,k))
                else:
                    expected=functional(derivative(poly[k]),a)
                    self.assertEqual(chebyshev_derivative_moment(k,a),expected,(a,k))

    def test_chebyshev_gram_and_quasiseparable_generators(self):
        poly=brute_chebyshev(29)
        examples=([1],[0,1],[2,3],[3,-2,1],[1,3,-2,1],[7,-3,2,-1,1])
        for a in examples:
            for c in (-2,0,1):
                rows,cols,diag=semiseparable_generators(a,c,27)
                width=2*len(a)
                self.assertTrue(all(len(row)==width for row in rows))
                self.assertTrue(all(len(col)==width for col in cols))
                for i in range(0,12):
                    for j in range(0,12):
                        term=product(poly[i],poly[j])
                        expected=functional(term,a,c)
                        self.assertEqual(chebyshev_gram_entry(i,j,a,c),
                                         expected,(a,c,i,j))
                for i in range(14,27):
                    for j in range(0,13):
                        linear=sum(rows[i][k]*cols[j][k]
                                   for k in range(width))
                        self.assertEqual(linear,chebyshev_gram_entry(i,j,a,c))
                block=[[chebyshev_gram_entry(i,j,a,c)
                        for j in range(0,13)] for i in range(14,27)]
                rank=exact_rank(block)
                bound=2*(len(a)-1) if c==0 else 2*len(a)
                self.assertLessEqual(rank,bound,(a,c,rank,bound))

    def test_exact_prefixes_agree_with_direct_hankel_determinants(self):
        cases=[([1],1),([0,1],1),([0,1],0),([0,0,1],1),
               ([0,0,0,1],-1),([1,1],2),([1,-1],0),
               ([2,3],0),([3,-2,1],1),([1,3,-2,1],-2),
               ([0,0,1,-1],2),([1,0,0,2],1),
               ([F(1,2),F(2,3),F(-3,5)],F(3,4))]
        for a,c in cases:
            outputs=structured_hankel_prefixes(a,c,13)
            for n,actual in enumerate(outputs):
                self.assertEqual(actual,direct_hankel(a,c,n),(a,c,n))
                self.assertEqual(actual,direct_hankel(a,c,n,lam=3),(a,c,n,'shift'))
                self.assertEqual(actual,structured_hankel_prefixes(a,-c,n)[n],
                                 (a,c,n,'parity'))

    def test_first_nonzero_prefix_and_adaptive_singular_lookahead(self):
        for d in range(0,6):
            a=[0]*d+[1]
            start=initial_nonsingular_formula(a)
            self.assertEqual(start[0],2*d+1)
            target=(-1)**d*(factorial(2*d)//factorial(d))**(2*d+1)
            self.assertEqual(start[1],target)
            values=structured_hankel_prefixes(a,1,2*d+7)
            self.assertEqual(values[:2*d+1],[F(1)]+[F(0)]*(2*d))
            self.assertEqual(values[2*d+1],target)
        self.assertIsNone(initial_nonsingular_formula([0,0,0]))
        self.assertEqual(structured_hankel_prefixes([0,0,0],1,8),
                         [1]+[0]*8)
        # Zero leading determinant after a previously invertible prefix.
        self.assertEqual(structured_hankel_prefixes([1,1],2,4),
                         [1,1,0,-256,44536])
        # Two consecutive zero leading minors followed by a recovery.
        self.assertEqual(structured_hankel_prefixes([1,-1],0,5),
                         [1,1,0,0,216,4464])

    def test_special_single_weight_family_agrees_with_original_chebyshev_formula(self):
        # Two independent root-free routes: the prior fixed-size polynomial
        # remainder theorem and the new bounded-rank Schur calculation.
        from sequence_closed_forms_extended import weighted_hankel_closed
        for d in range(5):
            weights=[0]*d+[1]
            for c in (-2,0,1,2):
                sequence=structured_hankel_prefixes(weights,c,40)
                for n,value in enumerate(sequence):
                    self.assertEqual(value,weighted_hankel_closed(n,d,c),
                                     (d,c,n))

    def test_high_order_exact_replay_without_large_hankel_matrices(self):
        for a,c,n in [([0,1],1,200),([0,0,1],1,200),
                      ([0,0,0,1],1,100),([2,-3,5],2,140)]:
            outputs=structured_hankel_prefixes(a,c,n)
            self.assertEqual(len(outputs),n+1)
            self.assertEqual(outputs[0],1)
            for k in (4,5,7,8,10,12):
                if k<=n:
                    self.assertEqual(outputs[k],direct_hankel(a,c,k))
        self.assertEqual(structured_hankel_prefixes([0,1],1,8),
                         [1,0,0,-8,1680,-271488,-2874880,1840174080,-87345205248])

    def test_no_positive_measure_for_nonconstant_weights_example(self):
        # P(m)=m+1 would have mass F_P[1]=1. Its moments grow
        # faster than 4^m, which violates the necessary support bound.
        a=[1,1]
        self.assertEqual(monomial_moment(0,a),1)
        self.assertGreater(monomial_moment(16,a),4**8)


if __name__=="__main__":
    unittest.main()
