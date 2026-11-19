"""Independent exact regression checks for Closed Forms II and III.

Author: Komorebi P. No third-party dependencies.
"""
import json
import sys
import unittest
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from sequence_closed_forms import (COUNT,rising,falling,sparse_coefficients,
    padovan_powers,four_block,weighted_moments,weighted_hankel,
    beta_moments,beta_determinants,closed_form_catalogue,closed_form_families)


class ClosedFormsTests(unittest.TestCase):
    def test_all_curated_records_and_family_definitions(self):
        records=closed_form_catalogue()
        self.assertEqual(len(records),24)
        self.assertEqual(len({r['id'] for r in records}),24)
        self.assertEqual(len(closed_form_families()),8)
        families={r['id'] for r in closed_form_families()}
        self.assertEqual({r['closed_form_family'] for r in records},
                         families-{'GF-CF-BINOMIAL-JETS','GF-CF-ENTIRE-SCALING'})
        for row in records:
            self.assertEqual(len(row['terms']),COUNT)
            self.assertEqual(len(row['formulas']),2)
            self.assertTrue(all(str(int(x))==x for x in row['terms']))
            self.assertIn('historical priority unassessed',row['status'])
            self.assertTrue(row['source'].endswith('IDENTITIES.md'))
        self.assertTrue((ROOT/'research/sequence-closed-forms/IDENTITIES.md').exists())
        self.assertEqual([r['id'] for r in records if r['kind']=='Padovan power'],
                         ['KFOR-CF-PAD-1','KFOR-CF-PAD-2'])

    def test_sparse_against_independent_finite_binomial_sum(self):
        from sequence_closed_forms import sparse_coefficients
        cases=[(2,3,1,1,1),(2,3,1,1,2),(2,5,1,1,1),
               (3,5,1,2,1),(2,3,2,1,3),(3,4,1,-1,2)]
        for p,q,u,v,r in cases:
            actual=sparse_coefficients(p,q,u,v,r)
            for n in range(COUNT):
                direct=sum(Q(rising(r,i+j)*u**i*v**j, factorial(i)*factorial(j))
                           for i in range(n//p+1) for j in range(n//q+1)
                           if p*i+q*j==n)
                self.assertEqual(actual[n],direct,(p,q,u,v,r,n))

    def test_padovan_and_convolution(self):
        base=padovan_powers(1)
        self.assertEqual(base[:12],[1,0,0,1,0,1,1,1,2,2,3,4])
        self.assertEqual(base[3:], [base[n-2]+base[n-3] for n in range(3,COUNT)])
        sq=[sum(base[k]*base[n-k] for k in range(n+1)) for n in range(COUNT)]
        self.assertEqual(padovan_powers(2),sq)

    def test_four_block_against_independent_formal_logarithm(self):
        for a in (-2,-1,0,1,2,3):
            actual=four_block(a,6)
            self.assertEqual(actual[0],6*a*a-4*a+1)
            self.assertEqual(actual[1],1260*a**4-1680*a**3+952*a*a-272*a+34)
            # Compute -log(V_a) from the formal series; no recurrence is used.
            v=[Q(0)]
            for m in range(1,7):
                A=1-4*m*a+2*m*(4*m-1)*a*a
                v.append(Q((-1)**m*A,factorial(4*m)))
            power=[Q(1)]+[Q(0)]*6
            logarithm=[Q(0)]*7
            for r in range(1,7):
                power=[sum(power[k]*v[n-k] for k in range(n+1)) for n in range(7)]
                for m in range(1,7):
                    logarithm[m]+=Q((-1)**r,r)*power[m]
            independent=[logarithm[m]*factorial(4*m) for m in range(1,7)]
            self.assertEqual(actual,independent)
        self.assertEqual(four_block(0,4),[1,34,11056,14873104])

    def test_weighted_hankel_initial_blocks_and_shift(self):
        self.assertEqual(weighted_hankel(0,0,6),[1,1,2,4,8,16])
        for d in range(3):
            expected=(-1)**d*(factorial(2*d)//factorial(d))**(2*d+1)
            for c in (0,1,-2):
                rows=weighted_hankel(d,c,2*d+2)
                self.assertEqual(rows[0],1)
                self.assertEqual(rows[1:2*d+1],[0]*(2*d))
                self.assertEqual(rows[2*d+1],expected)
        # Binomial translation of moments preserves a Hankel determinant.
        from sequence_closed_forms import exact_det
        moments=weighted_moments(0,1,11)
        shifted=[sum(comb(n,k)*3**(n-k)*moments[k] for k in range(n+1))
                 for n in range(11)]
        for n in range(1,6):
            original=exact_det([[moments[i+j] for j in range(n)] for i in range(n)])
            translated=exact_det([[shifted[i+j] for j in range(n)] for i in range(n)])
            self.assertEqual(original,translated)

    def test_beta_binomial_normalization_and_determinant_product(self):
        cases=[(4,1,1),(5,1,2),(6,2,1),(7,2,3)]
        for L,a,b in cases:
            terms=beta_moments(L,a,b)
            self.assertEqual(terms[0],rising(a+b,L))
            self.assertEqual(terms[1],rising(a+b,L)*Q(L*a,a+b))
            self.assertTrue(all(isinstance(x,int) for x in terms))
        for L,a,b in ((4,1,1),(6,2,1)):
            actual=beta_determinants(L,a,b)
            normalizer=rising(a+b,L)
            for N in range(L+2):
                product=Q(1)
                for j in range(N):
                    product*=Q(factorial(j)*rising(a,j)*rising(b,j)*
                               falling(L,j)*rising(a+b+L,j),rising(a+b,N+j-1))
                self.assertEqual(actual[N],product*normalizer**N)
            self.assertTrue(all(v==0 for v in actual[L+2:]))

    def test_catalogue_source_index_semantics(self):
        from sequence_library import source_degree
        for row in closed_form_catalogue():
            index=row['offset']
            actual=source_degree(row,index)
            self.assertEqual(actual,4*index-1 if row['closed_form_family']=='GF-CF-FOUR-BLOCK' else index)
            self.assertGreaterEqual(actual,0)
        self.assertEqual(four_block(1,1),[3])


if __name__=='__main__':
    unittest.main()
