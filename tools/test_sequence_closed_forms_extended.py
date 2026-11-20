"""Independent exact regression checks for the extended closed-form collection.

Author: Komorebi P.
The tests exercise finite domains and do not certify historical priority.
"""
import sys
import unittest
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_closed_forms import (falling, rising, exact_det,
                                   weighted_hankel)
from sequence_closed_forms_extended import (
    sparse_finite, sparse_hyper, weighted_jet_even, weighted_jet,
    hankel_4f3, weighted_hankel_closed, meixner_pollaczek_integer,
    extended_catalogue, extended_families, append_proved_representations,
    bernoulli_number, four_block_tangent_bernoulli,
    four_block_reciprocal_euler, beta_transfer_hankel,
    beta_split_weights, beta_split_factorial_moment,
    weighted_first_regular_hyper)


def seed(n,d,c=1):
    def moment(k):
        if k<0 or k%2:
            return 0
        m=k//2
        return falling(m,d)*comb(2*m,m)
    return moment(n)+c*n*moment(n-1)


def direct_hankel(N,d,c,lam=0):
    moments=[seed(n,d,c) for n in range(2*N-1)]
    if lam:
        moments=[sum(comb(n,j)*lam**(n-j)*moments[j]
                     for j in range(n+1)) for n in range(2*N-1)]
    return exact_det([[moments[i+j] for j in range(N)] for i in range(N)])


def poly_power_coefficients(base, degree):
    values=[1]
    for _ in range(degree):
        output=[0]*(len(values)+len(base)-1)
        for i,x in enumerate(values):
            for j,y in enumerate(base):
                output[i+j]+=x*y
        values=output
    return values


class ClosedFormsExtendedTests(unittest.TestCase):
    def test_sparse_hypergeom_and_sparse_finite_independently(self):
        for p,q in ((2,3),(2,5),(3,5),(4,6),(2,2),(5,2)):
            for r in (-2,-1,F(1,2),1,3):
                for u,v in ((1,1),(0,1),(1,0),(-2,3),(2,-1)):
                    for n in range(28):
                        actual=sparse_hyper(n,p,q,r,u,v)
                        finite=sparse_finite(n,p,q,r,u,v)
                        self.assertEqual(actual,finite,(p,q,r,u,v,n))
        for n in range(28):
            self.assertEqual(sparse_hyper(n,2,5,1),sparse_finite(n,2,5,1))

    def test_sparse_coefficients_have_independent_derivative_recurrence(self):
        p,q,r,u,v=2,5,F(1,2),3,-2
        values=[sparse_hyper(n,p,q,r,u,v) for n in range(45)]
        self.assertEqual(values[0],1)
        for n in range(1,len(values)):
            rhs=u*(n+(r-1)*p)*(values[n-p] if n>=p else 0)
            rhs+=v*(n+(r-1)*q)*(values[n-q] if n>=q else 0)
            self.assertEqual(n*values[n],rhs)

    def test_hankel_4f3_against_direct_integer_determinants(self):
        for c in (-2,-1,0,1,2):
            for n in range(14):
                self.assertEqual(hankel_4f3(n,c),direct_hankel(n,0,c))
                self.assertEqual(direct_hankel(n,0,c,lam=3),
                                 direct_hankel(n,0,c))
        self.assertEqual([hankel_4f3(n,1) for n in range(9)],
                         [1,1,1,-14,-100,56,6112,58304,320448])

    def test_jet_transform_vs_independently_shifted_seed(self):
        for d in range(5):
            for lam in (-1,0,1,2):
                for c in (-2,0,1,3):
                    for n in range(2*d+16):
                        expected=sum(comb(n,j)*lam**(n-j)*seed(j,d,c)
                                     for j in range(n+1))
                        self.assertEqual(weighted_jet(n,d,lam,c),expected,
                                         (d,lam,c,n))

    def test_jet_generating_function_and_order_two_recurrence(self):
        for d in range(5):
            bound=2*d+32
            alpha=F(2*d+3,2)
            B=[F(1)]
            for n in range(1,bound+1):
                rhs=2*(n-1+alpha)*B[n-1]
                if n>=2:
                    rhs+=3*(n-2+2*alpha)*B[n-2]
                B.append(rhs/n)
            a_d=factorial(2*d)//factorial(d)
            kernel=[F(1),F(2*d-1),F(-2*d-4)]
            for n in range(bound+1):
                actual=weighted_jet(n,d)
                j=n-2*d
                expected=a_d*sum(kernel[k]*B[j-k]
                                 for k in range(3) if j-k>=0)
                self.assertEqual(actual,expected,(d,n))
                if n>=2*d+2:
                    A=n*(n-2*d)+2*n-2*d-1
                    lhs=(n-2*d)*(n*(n-2*d)-5)*actual
                    rhs=((2*n-2*d-6)*A+3*(n-1)*(n-2*d-1))*weighted_jet(n-1,d)
                    rhs+=3*(n-1)*(A-3)*weighted_jet(n-2,d)
                    self.assertEqual(lhs,rhs,(d,n))
        self.assertEqual([weighted_jet(n,0) for n in range(7)],
                         [1,2,5,16,47,146,447])
        self.assertEqual([weighted_jet(n,1) for n in range(9)],
                         [0,0,2,12,48,200,750,2772,9912])

    def test_weighted_hankel_closed_against_direct_bareiss(self):
        for d in range(4):
            for c in (-2,-1,0,1,2):
                for N in range(2*d+8):
                    expected=direct_hankel(N,d,c)
                    self.assertEqual(weighted_hankel_closed(N,d,c),expected,
                                     (d,c,N))
        self.assertEqual([weighted_hankel_closed(N,1,1) for N in range(8)],
                         [1,0,0,-8,1680,-271488,-2874880,1840174080])
        self.assertEqual([weighted_hankel_closed(N,2,1) for N in range(8)],
                         [1,0,0,0,0,248832,-57644421120,-289931282841600])

    def test_hankel_initial_singular_blocks(self):
        for d in range(5):
            a_d=factorial(2*d)//factorial(d)
            for c in (-1,0,1):
                self.assertEqual(weighted_hankel_closed(0,d,c),1)
                for N in range(1,2*d+1):
                    self.assertEqual(weighted_hankel_closed(N,d,c),0)
                self.assertEqual(weighted_hankel_closed(2*d+1,d,c),
                                 (-1)**d*a_d**(2*d+1))

    def test_weighted_rational_denominator_recurrence(self):
        for d,c in ((0,1),(1,1),(2,1),(2,0)):
            a_d=factorial(2*d)//factorial(d)
            rho=(-1)**(d+1)*2*a_d
            K=(d+1)*(d+2)
            denominator=[1,4*rho,
                         6*rho*rho+(2*d+1)**2*c*c*rho*rho,
                         4*rho**3,rho**4]
            coefficients=poly_power_coefficients(denominator,K+1)
            order=4*(K+1)
            values=[weighted_hankel_closed(n,d,c)
                    for n in range(order+11)]
            for N in range(order+1,order+11):
                self.assertEqual(sum(coefficients[j]*values[N-j]
                                     for j in range(order+1)),0,
                                 (d,c,N))

    def test_explicit_weighted_zero_geometry_polynomials(self):
        for c in range(-4,5):
            self.assertEqual(weighted_hankel_closed(4,1,c),
                             48*(27*c**4+6*c*c+2))
            self.assertEqual(weighted_hankel_closed(6,2,c),
                             -14929920*(25*c*c+2)*(125*c**4+20*c*c-2))

    def test_meixner_integer_specializations_and_symmetry(self):
        expected=[1,2,3,-2,-31,-30,715,2510,-30015]
        self.assertEqual(meixner_pollaczek_integer(1,2,9),expected)
        for s in (1,2,3,4):
            positive=meixner_pollaczek_integer(s,2)
            negative=meixner_pollaczek_integer(s,-2)
            for n,value in enumerate(positive):
                self.assertEqual(negative[n],(-1)**n*value)
            for n in range(1,len(positive)-1):
                self.assertEqual(positive[n+1],
                                 2*positive[n]-n*(n+s-1)*positive[n-1])

    def test_four_block_euler_convolution(self):
        from sequence_atlas import reciprocal
        from sequence_formula_catalogue import tangent
        for n in range(8):
            T4=tangent(4,8)[n]
            T2=tangent(2,16)[2*n+1]
            self.assertEqual(2**(2*n+1)*T4,T2)
        for power in (1,2,3):
            four=reciprocal(4,power,8)
            two=reciprocal(2,power,15)
            for n in range(8):
                numerator=sum((-1)**j*comb(4*n,2*j)*two[j]*two[2*n-j]
                              for j in range(2*n+1))
                self.assertEqual(numerator,4**n*four[n])

    def test_beta_moment_hankel_product_and_splitter(self):
        from sequence_closed_forms import beta_weights
        for a,b in ((1,1),(2,1),(1,3)):
            for L in range(2,6):
                weights=beta_weights(L,a,b)
                self.assertEqual(sum(weights),rising(a+b,L))
                for ell in range(L+1):
                    lhs=sum(falling(k,ell)*weights[k] for k in range(L+1))
                    rhs=F(falling(L,ell)*rising(a,ell)*rising(a+b,L),
                          rising(a+b,ell))
                    self.assertEqual(lhs,rhs,(a,b,L,ell))
            mu=[F(rising(a,n),rising(a+b,n)) for n in range(12)]
            for N in range(1,5):
                matrix=[[mu[i+j] for j in range(N)] for i in range(N)]
                determinant=F(1)
                for k in range(N):
                    pivot=matrix[k][k]
                    if pivot==0:
                        raise AssertionError('positive beta moment pivot vanished')
                    determinant*=pivot
                    for i in range(k+1,N):
                        factor=matrix[i][k]/pivot
                        for j in range(k,N):
                            matrix[i][j]-=factor*matrix[k][j]
                product=F(1)
                for j in range(N):
                    product*=F(factorial(j)*rising(a,j)*rising(b,j),
                               rising(a+b,N+j-1))
                self.assertEqual(determinant,product)

    def test_paper_card_calculators_with_exact_source_normalizations(self):
        from sequence_atlas import reciprocal
        from sequence_formula_catalogue import tangent
        self.assertEqual([bernoulli_number(n) for n in range(5)],
                         [F(1),F(-1,2),F(1,6),F(0),F(-1,30)])
        for n in range(8):
            self.assertEqual(four_block_tangent_bernoulli(n),tangent(4,8)[n])
            for power in (1,2,3):
                self.assertEqual(four_block_reciprocal_euler(n,power),
                                 reciprocal(4,power,8)[n])
        for a,b in ((1,1),(2,1),(1,3)):
            for N in range(5):
                self.assertEqual(beta_transfer_hankel(a,b,N),
                                 F(1) if N==0 else beta_transfer_hankel(a,b,N))
            for n in range(9):
                weights=beta_split_weights(n,a,b)
                self.assertEqual(sum(weights),1)
                for ell in range(n+1):
                    actual=sum(falling(k,ell)*weights[k] for k in range(n+1))
                    self.assertEqual(actual,beta_split_factorial_moment(n,ell,a,b))
        for d in range(5):
            for c in (-2,-1,0,1,2):
                self.assertEqual(weighted_first_regular_hyper(d,c),
                                 weighted_hankel_closed(2*d+2,d,c))

    def test_catalogue_variants_and_family_sources_are_scoped(self):
        records=extended_catalogue()
        self.assertEqual(len(records),11)
        self.assertEqual(len({r['id'] for r in records}),11)
        self.assertTrue(all(len(r['terms'])==24 for r in records))
        self.assertEqual(len(extended_families()),1)
        self.assertEqual(records[0]['oeis'],'A163865')
        from sequence_closed_forms import closed_form_catalogue
        from sequence_formula_catalogue import expanded_catalogue
        all_entries=expanded_catalogue()
        self.assertEqual(len(all_entries),2205)
        self.assertEqual(len({r['id'] for r in all_entries}),len(all_entries))
        by_id={x['id']:x for x in all_entries}
        self.assertEqual(len(by_id['KFOR-CF-W-0-1']['formulas']),3)
        self.assertEqual(len(by_id['KFOR-T-04']['formulas']),3)
        self.assertEqual(by_id['KFOR-CF-JET-01']['terms'][:8],
                         ['0','0','2','12','48','200','750','2772'])


if __name__=='__main__':
    unittest.main()
