"""Independent fast controls for the new exact checker, not theorem proofs."""
import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'checks/check_degree_block02.py'
S=importlib.util.spec_from_file_location('degree_block02',P)
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class DegreeBlock02Controls(unittest.TestCase):
    def test_and_is_quadratic(self):
        self.assertEqual(M.degree(2,8),2)
    def test_and_complete_safe_degree(self):
        beta,star=M.safe_profiles(2)
        self.assertEqual((beta[8],star[8]),(2,2))
    def test_constants_and_zero_inputs(self):
        self.assertEqual(M.safe_profiles(0),([0,0],[0,0]))
    def test_every_primitive_is_involutive(self):
        state=M.variables(3);mask=(1<<8)-1
        for g in M.alphabet(3):
            self.assertEqual(M.execute((g,g),state,mask),state)
if __name__=='__main__':unittest.main()
