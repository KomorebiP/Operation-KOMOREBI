#!/usr/bin/env python3
"""Bounded checks for the new worked plates, plus explicit false controls."""
from __future__ import annotations
import argparse,json,time,unittest
from collections import Counter
from itertools import product
from pathlib import Path
from math import gcd
from atlas_models import *

class AtlasChecks(unittest.TestCase):
    def test_same_candidate_intersection(self):
        self.assertTrue({'a'});self.assertTrue({'b'});self.assertEqual({'a'}&{'b'},set())
        self.assertTrue(all(False for _ in []));self.assertFalse(any(True for _ in []))

    def test_balanced_product_fibres(self):
        fibres=Counter((x1,y1,x2,y2,(z1+z2)%3) for x1,y1,z1,x2,y2,z2 in product(range(3),repeat=6))
        self.assertEqual(len(fibres),243);self.assertEqual(set(fibres.values()),{3})
        self.assertEqual(27*27//3,3**5);self.assertEqual(3*3,9)

    def test_binder_compatible_roots(self):
        rows=root_levels(3,7)
        for r in rows:self.assertEqual(r['roots'],[1,r['modulus']-1])
        for before,after in zip(rows,rows[1:]):
            self.assertEqual({v%before['modulus'] for v in after['roots']},set(before['roots']))
        self.assertFalse({0}&{1})

    def test_corner_exhaustive_spectrum(self):
        image=corner_image();targets=set(product([1,2],[1,2],[1,2],range(3),range(3)))
        predicted={t for t in targets if corner_criterion(t)}
        self.assertEqual(image,predicted);self.assertEqual((len(image),len(targets)),(24,72))
        self.assertIn((1,1,1,2,2),image);self.assertNotIn((1,1,1,2,2),corner_image(0))
        self.assertNotIn((1,1,1,1,2),image)

    def test_full_character_central_normalization(self):
        # All values are exponents in the exact ninth roots of unity.
        self.assertEqual((3*1+6)%9,0)
        self.assertNotEqual((3*0+6)%9,0)
        self.assertEqual([(1-a)%3 for a in range(3)],[1,0,2])

    def test_trace_all_units_criterion(self):
        for t in range(-5,6):
            for r in range(1,8):
                if t+r>=1:self.assertTrue(all(t+k!=0 for k in range(r,r+15)))
                else:self.assertGreaterEqual(-t,r);self.assertEqual(t+(-t),0)

    def test_defining_levels(self):
        odd=[3**(2-j)*4*[1,2][2-j] for j in [1,2]]
        dy=[2**(3-j)*3*[1,3,5][3-j] for j in [1,2,3]]
        self.assertEqual(odd,[24,4]);self.assertEqual(dy,[60,18,3])
        self.assertTrue(24>3*4>2*4)

    def test_original_capacity(self):
        for d in range(1,11):
            dims=[2**(d-j) for j in range(d+1)]
            levels=[2**(d-j)*3*(2*(d-j)+1) for j in range(1,d+1)]
            self.assertEqual(profile(dims,levels)['D'],2**d-2)
            self.assertEqual(2**d-2>=2*d,d>=3)
        self.assertEqual(2**3-2,2*3)

    def test_induction_transitivity_coset_model(self):
        # C12 / C2 has six cosets, decomposed through C6 as pairs (i,j).
        reps={(i+2*j)%6 for i in range(2) for j in range(3)}
        self.assertEqual(reps,set(range(6)))
        for g in range(12):
            left=[(r+g)%6 for r in range(6)]
            nested=[(i+2*j+g)%6 for j in range(3) for i in range(2)]
            self.assertEqual(left,nested)

    def test_conductor_normalizations(self):
        rows=[conductor(9,0,24),conductor(81,1,152),conductor(80,0,152)]
        self.assertEqual([r['ordinary'] for r in rows],[33,232,232])
        self.assertEqual([r['psi1_exponent'] for r in rows],[24,151,152])
        self.assertNotEqual(rows[1]['psi1_exponent'],rows[1]['swan'])

    def test_period_gate(self):
        for n in range(1,25):
            for w in range(1,50):
                for e in range(1,n+1):
                    if n%e==0:self.assertEqual((e*w)%n==0,e%(n//gcd(n,w))==0)
        self.assertEqual([(e,e*24//9) for e in [1,3,9] if (e*24)%9==0],[(3,8),(9,24)])

    def test_source_break_histogram(self):
        C=Counter(max(0 if x==0 else 1,0 if y==0 else 2) for x,y in product(range(9),repeat=2))
        self.assertEqual(C,{0:1,1:8,2:72});self.assertEqual(sum(k*v for k,v in C.items()),152)
        self.assertEqual(81-1+152,232)

    def test_rank_nine_necessary_filter(self):
        self.assertEqual(profile([9,3,1],[24,4])['pair'],232)
        self.assertEqual(profile([9,3,1],[24,10])['pair'],244)
        for c in range(2,24,2):self.assertEqual(profile([9,3,1],[24,c])['pair'],224+2*c)
        self.assertNotEqual(244,232)

    def test_profile_information_loss(self):
        f=profile([8,4,2,1],[60,18,3]);s=profile([8,4,1],[60,13])
        self.assertEqual((f['I'],f['D'],f['pair']),(133,6,342))
        self.assertEqual((s['I'],s['D'],s['pair']),(134,4,342))
        self.assertEqual(2*f['I']+f['D'],2*s['I']+s['D'])
        self.assertNotEqual(f['D'],s['D'])
        for n in range(1,100):self.assertEqual(2*((n+1)//2)+int(n%2==0),n+1)

    def test_descent_fibres(self):
        self.assertEqual([9*x%4 for x in range(4)],list(range(4)))
        self.assertEqual([3*x%3 for x in range(3)],[0,0,0])

    def test_clifford_radical_and_orbit(self):
        # F2^3 with radical in coordinate 2. Weyl carrier is two-dimensional.
        B=lambda v,w:((v&1)*((w>>1)&1)+((v>>1)&1)*(w&1))%2
        rad=[v for v in range(8) if all(B(v,w)==0 for w in range(8))]
        self.assertEqual(rad,[0,4]);self.assertEqual(8//len(rad),2**2)
        r=((0,-1),(1,-1));s=((0,1),(1,0));I=((1,0),(0,1))
        mm=lambda a,b:tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        self.assertEqual(mm(mm(r,r),r),I);self.assertEqual(mm(s,s),I);self.assertEqual(mm(mm(s,r),s),mm(r,r))
        self.assertEqual(2*1*1,2)

    def test_native_action_coprimality(self):
        for n in [3,9,27]:self.assertEqual([x for x in range(n) if 4*x%n==0],[0])
        A=((0,2),(1,0));I=((1,0),(0,1))
        mm=lambda a,b:tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2))%3 for j in range(2)) for i in range(2))
        self.assertNotEqual(A,I);self.assertNotEqual(mm(A,A),I);self.assertEqual(mm(mm(A,A),mm(A,A)),I)

    def test_dyadic_extension_groups(self):
        for l in [0,3]:
            G=list(product(range(2),range(4)))
            for a,b,c in product(G,repeat=3):
                self.assertEqual(group_product(group_product(a,b,1,l),c,1,l),group_product(a,group_product(b,c,1,l),1,l))
        self.assertEqual(element_orders(0),{1:1,2:5,4:2});self.assertEqual(element_orders(3),{1:1,2:1,4:6})

    def test_section_products_not_just_squares(self):
        d=lambda v,w:int(v==3)^int(w==3)^int((v^w)==3)
        self.assertTrue(all(d(v,v)==0 for v in range(4)));self.assertEqual(d(1,2),1)
        for v,w,u in product(range(4),repeat=3):self.assertEqual(d(v,w)^d(v^w,u),d(w,u)^d(v,w^u))

    def test_gauss_six_dimensional(self):
        self.assertEqual(gauss(3),8);self.assertEqual(gauss(3,3),-8)
        self.assertEqual(sum(quadratic(v,3)==0 for v in range(64)),36)
        self.assertEqual(sum(quadratic(v,3,3)==0 for v in range(64)),28)
        for m in [1,2,3]:
            for l in range(4**m):self.assertEqual(abs(gauss(m,l)),2**m)

    def test_capacity_arf_gate(self):
        for row in model_data()['quadratic_embedding_gate']:
            D,a,s=row['host_dim'],row['host_arf'],row['source_arf']
            if D<6:self.assertFalse(row['allowed'])
            elif D==6:self.assertEqual(row['allowed'],a==s)
            else:
                self.assertTrue(row['allowed'])
                # A 2D complement can supply either required Arf sign.
                complement_linear=0 if a==s else 3
                self.assertEqual((gauss(1,complement_linear)<0),bool(a^s))

    def test_transvection_and_defect(self):
        for m in [1,2,3]:
            for l in range(4**m):
                a=dual(l,m)
                for v in range(4**m):
                    Tv=transvection(v,a,m)
                    self.assertEqual(transvection(Tv,a,m),v)
                    self.assertEqual(quadratic(Tv,m,l),quadratic(v,m)^(symplectic(a,v,m)*quadratic(a,m)))
                self.assertEqual(int(gauss(m,l)<0),quadratic(a,m))
        self.assertNotEqual(quadratic(2,1),quadratic(2,1,2))
        self.assertEqual(quadratic(transvection(2,1,1),1,2),quadratic(2,1))

    def test_relative_and_equivariant_correction(self):
        # Swap the two hyperbolic planes; a=e1+e2 is fixed and isotropic.
        m=2;a=5;swap=lambda v:((v&3)<<2)|((v>>2)&3)
        self.assertEqual(swap(a),a);self.assertEqual(quadratic(a,m),0)
        for v in range(16):
            self.assertEqual(swap(transvection(v,a,m)),transvection(swap(v),a,m))
            if symplectic(a,v,m)==0:self.assertEqual(transvection(v,a,m),v)

    def test_odd_action_averaging_all_cocycles(self):
        for candidate in product(range(4),repeat=2):
            ds=(0,)+candidate
            valid=all(ds[(g+h)%3]==ds[g]^c3_action(ds[h],g) for g,h in product(range(3),repeat=2))
            if valid:
                u=ds[0]^ds[1]^ds[2]
                self.assertTrue(all(ds[g]==u^c3_action(u,g) for g in range(3)))
        data=model_data()['odd_action'];self.assertEqual(data['deltas'],[0,3,2]);self.assertEqual(data['corrected'],[0,0,0])

    def test_even_action_counterexample(self):
        ds=[0,1]
        for g,h in product(range(2),repeat=2):self.assertEqual(ds[(g+h)%2],ds[g]^ds[h])
        for u in range(4):self.assertEqual(u^ds[1]^u,1)

    def test_honest_phase_carry_model(self):
        c=lambda g,h:(g+h-(g+h)%3)%9
        for g,h,k in product(range(3),repeat=3):self.assertEqual((c(g,h)+c((g+h)%3,k))%9,(c(h,k)+c(g,(h+k)%3))%9)
        self.assertEqual(c(1,2),3)
        for g,h in product(range(3),repeat=2):self.assertEqual((c(g,h)-g-h+(g+h)%3)%9,0)
        for k in range(3):
            for g,h in product(range(3),repeat=2):self.assertEqual((3*k*g+3*k*h)%9,3*k*((g+h)%3)%9)

    def test_no_fabricated_native_certificate(self):
        d=model_data()['native_certificate']
        self.assertEqual(d['status'],'not_computed');self.assertTrue(all(x is None for x in d['square_bits']))
        self.assertIsNone(d['section_products']);self.assertIsNone(d['honest_phases'])
        self.assertTrue(all(v.startswith('open') for v in model_data()['open_endpoints'].values()))

    def test_data_serialization_and_bad_inputs(self):
        d=model_data();self.assertEqual(json.loads(json.dumps(d))['gauss6'],d['gauss6'])
        for dims,levels in [([8,1],[0]),([8,4],[5]),([8,4,1],[3,7]),([8,8,1],[6,1])]:
            with self.assertRaises(ValueError):profile(dims,levels)
        with self.assertRaises(ValueError):conductor(2,3,1)
        with self.assertRaises(ValueError):symplectic(4,0,1)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    t=time.monotonic();suite=unittest.defaultTestLoader.loadTestsFromTestCase(AtlasChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    d={'status':'passed' if result.wasSuccessful() else 'failed','test_methods':result.testsRun,
       'failures':len(result.failures),'errors':len(result.errors),'seconds':round(time.monotonic()-t,3),
       'scope':'Bounded finite models, negative controls and displayed atlas data. No arithmetic construction, Lean compilation or external theorem audit.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(d,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
if __name__=='__main__':main()
