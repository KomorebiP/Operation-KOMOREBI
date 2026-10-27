#!/usr/bin/env python3
"""Exact bounded examples for Paper XI publication Block 03. Standard library only."""
from __future__ import annotations
import argparse,itertools as it,json,math,unittest
from fractions import Fraction as Q
from pathlib import Path

def heis(a,b,p):
 u,v,w=a;x,y,z=b;return((u+x)%p,(v+y)%p,(w+z+u*y)%p)
def op(a,p):
 u,v,w=a;return(tuple((s+u)%p for s in range(p)),tuple((w+v*s)%p for s in range(p)))
def compose(a,b,p):
 r,x=a;s,y=b;return(tuple(s[r[k]] for k in range(p)),tuple((x[k]+y[r[k]])%p for k in range(p)))
def permul(a,b):return tuple(a[b[i]] for i in range(len(a)))
def inv(a):return tuple(a.index(i) for i in range(len(a)))
class ExactChecks(unittest.TestCase):
 def test_01_heisenberg_phase_law(self):
  for p in (3,5):
   es=list(it.product(range(p),repeat=3))
   for a,b in it.product(es,repeat=2):self.assertEqual(compose(op(a,p),op(b,p),p),op(heis(a,b,p),p))
 def test_02_balanced_center(self):
  for p in (3,5,7):
   kernel=[(a,b) for a,b in it.product(range(p),repeat=2) if (a+b)%p==0]
   self.assertEqual(kernel,[(a,(-a)%p) for a in range(p)]);self.assertEqual(p**6//len(kernel),p**5)
 def test_03_repeated_plane_is_not_independent(self):
  X=op((1,0,0),3);Z=op((0,1,0),3)
  self.assertNotEqual(compose(X,Z,3),compose(Z,X,3));self.assertNotEqual(3%9,0)
 def test_04_projective_radical_dimension(self):
  for p in (3,5):
   A=list(it.product(range(p),repeat=3));b=lambda x,y:(x[0]*y[1]-x[1]*y[0])%p
   R=[x for x in A if all(b(x,y)==0 for y in A)]
   self.assertEqual(len(R),p);self.assertEqual(len(A)//len(R),p*p);self.assertEqual(Q(len(R)*p*p,len(A)),1)
 def test_05_clifford_orbit_factor(self):
  orbit={1,(-1)%3};self.assertEqual(len(orbit),2);self.assertEqual(len(orbit)*1*1,2);self.assertNotEqual(1*1,2)
 def test_06_solvable_not_all_subgroups_admissible(self):
  G=set(it.permutations(range(3)));e=(0,1,2);H={e,(1,0,2)};subs=[];gs=sorted(G)
  for mask in range(64):
   K={gs[i] for i in range(6) if mask>>i&1}
   if e in K and all(permul(a,b) in K for a,b in it.product(K,repeat=2)):subs.append(K)
  normal=lambda K,L:all(permul(permul(g,h),inv(g)) in K for g in L for h in K)
  self.assertEqual([K for K in subs if H<K],[G]);self.assertFalse(normal(H,G))
  A={e,(1,2,0),(2,0,1)};self.assertTrue(normal(A,G));self.assertEqual((len(A),len(G)//len(A)),(3,2))
 def test_07_inertia_fixed_space(self):
  for n,j in it.product(range(1,9),range(7)):
   fixed=sum(j==0 for _ in range(n));self.assertEqual(n-fixed,0 if j==0 else n)
 def test_08_cyclic_extensions(self):
  for d in range(2,8):
   roots=[Q(1,5*d)+Q(j,d) for j in range(d)]
   self.assertTrue(all((d*x-Q(1,5)).denominator==1 for x in roots));self.assertEqual(len({x%1 for x in roots}),d)
 def test_09_central_normalization(self):
  for n,d in it.product(range(1,10),repeat=2):self.assertEqual(len({n*x%d for x in range(d)}),d//math.gcd(n,d))
  self.assertEqual({3*x%2 for x in range(2)},{0,1});self.assertEqual({3*x%3 for x in range(3)},{0})
 def test_10_corner_complete_profile_spectrum(self):
  actual={(c*d%3,a*b%3,b*c%3,c*(a-h)%3,b*(d-h)%3) for a,b,c,d in it.product((1,2),repeat=4) for h in range(3)}
  predicted={(u,v,w,r,s) for u,v,w in it.product((1,2),repeat=3) for r,s in it.product(range(3),repeat=2) if (r+u-w*(s+v))%3==0}
  self.assertEqual(actual,predicted);self.assertEqual(len(actual),24);self.assertEqual(2**3*3**2,72)
  self.assertIn((1,1,1,2,2),actual);self.assertNotIn((1,1,1,1,2),actual)
  four={(c*d%3,a*b%3,b*c%3,c*a%3,b*d%3) for a,b,c,d in it.product((1,2),repeat=4)}
  self.assertNotIn((1,1,1,2,2),four)
 def test_11_general_binder_support(self):
  for h in range(1,101):
   if h%3==0:continue
   a=4*h;S={k*a%9 for k in (0,2,4,6)}
   self.assertFalse(S&{(s+a)%9 for s in S})
   paths={s for s in S if (s-2*a)%9 in S}
   self.assertEqual(paths,{k*a%9 for k in (2,4,6)});self.assertEqual({s%3 for s in paths},{0,1,2})
 def test_12_symmetric_break_not_unsymmetric_break(self):
  for p,m in ((3,1),(3,5),(5,2),(5,3)):self.assertLess(Q(m)+Q(m,p),2*m)
  self.assertEqual(Q(20,3)*9,60);self.assertNotEqual(Q(20,3)*9,180)
 def test_13_compact_roots_not_surjective_reduction(self):
  roots={k:[x for x in range(2**k) if (x*x-17)%2**k==0] for k in range(1,13)}
  self.assertTrue(all(roots.values()));self.assertIn(3,roots[3]);self.assertIn(5,roots[3])
  images={x%8 for x in roots[4]};self.assertNotIn(3,images);self.assertNotIn(5,images);self.assertEqual(images,{1,7})
 def test_14_joint_not_separate_solvability(self):
  for k in range(1,8):
   xs=range(3**k);A={x for x in xs if x%3**k==0};B={x for x in xs if (x-1)%3**k==0}
   self.assertTrue(A);self.assertTrue(B);self.assertFalse(A&B)
 def test_15_uniformizer_correction(self):
  self.assertEqual((3*Q(1,9)+Q(2,3))%1,0);self.assertNotEqual(Q(2,3)%1,0)
  self.assertEqual([a for a,x in enumerate([Q(1,3),Q(0),Q(2,3)]) if x==0],[1])
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExactChecks))
 report={'status':'passed' if result.wasSuccessful() else 'failed','methods':result.testsRun,'scope':'Bounded finite and exact-rational models. No arithmetic realization or fresh Lean certification.','negative_controls':['noncommuting repeated plane','S3 non-subnormal C2','rank-divisible descent ambiguity','forbidden corner profile','non-surjective root reduction','separate constraints','wrong uniformizer normalization'],'failures':[(str(t),x) for t,x in result.failures+result.errors]}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(not result.wasSuccessful())
if __name__=='__main__':main()
