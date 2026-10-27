"""Release infrastructure and independent finite arithmetic tests; not mathematical proofs."""
import importlib.util,sys,json,unittest
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('verifier','verify.py');a=load('arithmetic','eleventh_regressions.py')
class ExtensionTests(unittest.TestCase):
 def test_inventory_exact(self):self.assertEqual(v.source_inventory(),json.loads((ROOT/'inventory.json').read_text()))
 def test_coverage_not_relabelled(self):self.assertEqual(v.validate_coverage(v.source_inventory()),{'lean_checked':24,'pending_lean':0,'classical_inputs':3,'conjectures':2,'manuscript_proved':24})
 def test_new_names(self):
  names={d['name'] for x in v.source_inventory()['modules'] for d in x['declarations']}
  self.assertIn('KomorebiPaperIX.NishibuchiCompletion.conjecture_3_9',names)
  self.assertIn('KomorebiPaperIX.DyadicFourCongruences.normalized_bound',names)
 def test_printed_contract(self):
  t=(ROOT/'contracts/ExternalStatement.lean.txt').read_text()
  for s in ['m∣p-1 ∨ m=2','Nat.lcm 2 (p-1)*p^r','n0≤r','PadicInt.subring p']:self.assertIn(s,t)
 def test_audit_good(self):self.assertEqual(v.parse_audits("'A' depends on axioms: [propext, Quot.sound]",{'A'}),{'A':['Quot.sound','propext']})
 def test_audit_placeholder(self):
  with self.assertRaises(ValueError):v.parse_audits("'A' depends on axioms: [sorryAx]",{'A'})
 def test_audit_custom_axiom(self):
  with self.assertRaises(ValueError):v.parse_audits("'A' depends on axioms: [assumed_conjecture]",{'A'})
 def test_audit_missing(self):
  with self.assertRaises(ValueError):v.parse_audits('',{'A'})
 def test_audit_duplicate(self):
  with self.assertRaises(ValueError):v.parse_audits("'A' does not depend on any axioms\n'A' does not depend on any axioms",{'A'})
 def test_control_rejects_bad_environment(self):self.assertFalse(v.control_passed(1,'error: unknown module X','false_equality'))
 def test_control_rejects_timeout(self):self.assertFalse(v.control_passed(124,'error: timed out','false_equality'))
 def test_control_must_fail(self):self.assertFalse(v.control_passed(0,'','false_equality'))
 def test_control_accepts_false_goal(self):self.assertTrue(v.control_passed(1,'error: unsolved goals\n⊢ False','false_equality'))
 def test_nested_comment_scanner(self):self.assertNotIn('sorry',v.stripped_source('/- one /- sorry -/ two -/\ndef f:=1'))
 def test_real_placeholder_scanner(self):self.assertTrue(v.FORBIDDEN.search(v.stripped_source('theorem bad : False := by sorry')))
 def test_unclosed_comment(self):
  with self.assertRaises(ValueError):v.stripped_source('/- never closed')
 def test_zero_precision(self):self.assertTrue(a.precision(2,F(0),10000))
 def test_rational_valuation(self):self.assertEqual(a.valuation(2,F(26,9)),1)
 def test_input_validation(self):
  for args in [(0,0,1),(4,4,1),(4,0,-1)]:
   with self.assertRaises(ValueError):a.coefficients(*args)
 def test_original_normalization(self):
  self.assertEqual(6*a.coefficients(4,3,2)[1],F(-6,35))
 def test_kernel_sample(self):
  from math import comb
  for n in range(15):self.assertEqual(F(1,comb(4*n+3,4*n)),F(3,(4*n+1)*(2*n+1)*(4*n+3)))
 def test_dyadic_period(self):
  seq=a.coefficients(4,1,20)
  for r in range(1,5):
   for n in range(r,10):self.assertTrue(a.precision(2,seq[n+2**(r-1)]-seq[n],r))
 def test_step_zero(self):self.assertEqual(a.delta(a.coefficients(4,1,4),0,3,2),0)
 def test_displacement_counterexample(self):self.assertNotEqual(4*(3+2**2),4*3+2**3)
 def test_endpoint_not_sharp_claim(self):
  c=json.loads((ROOT/'conjecture_contract.json').read_text())
  self.assertIn('optimal threshold',c['not_claimed']);self.assertIn('least period',c['not_claimed'])
if __name__=='__main__':unittest.main()
