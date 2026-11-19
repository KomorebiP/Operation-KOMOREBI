"""Cross-language exact regression for higher-order differential Hankel moments.

Author: Komorebi P.
Python and JavaScript independently implement the bounded-state Chebyshev
Schur determinant. The browser also checks its prefix through size 12 by
direct integer Bareiss elimination of the defining monomial moment matrix.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from sequence_differential_hankel import structured_differential_hankel


class DifferentialHankelBridgeTests(unittest.TestCase):
    def check_examples(self, examples, size):
        fixtures=[]
        for label,a,c in examples:
            values=structured_differential_hankel(a,c,size)
            fixtures.append(dict(label=label,a=a,c=c,
                                 expected=list(map(str,values))))
        completed=subprocess.run(
            ['node',str(ROOT/'tools/test_sequence_differential_hankel_bridge.mjs')],
            input=json.dumps(fixtures,separators=(',',':')),text=True,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=ROOT,check=False,
            timeout=90,
        )
        self.assertEqual(completed.returncode,0,completed.stderr or completed.stdout)
        result=json.loads(completed.stdout)
        self.assertEqual(result,dict(cases=len(examples),
                                    exact_values=len(examples)*(size+1),
                                    all_exact=True))

    def test_python_schur_agrees_with_browser_bareiss_at_all_small_sizes(self):
        examples=[
            ('first_and_second_derivative',[1,1,0,0],[1,2,1,0]),
            ('singular_through_four',[0,1,0,0],[0,0,2,0]),
            ('signed_cubic_operator',[2,-3,1,0],[1,-2,3,-1]),
            ('pure_second_derivative',[1,0,0,0],[1,0,1,0]),
            ('nonzero_third_derivative',[0,0,1,0],[0,1,0,-2]),
            ('all_four_coefficients',[1,-1,2,1],[0,1,-2,3]),
            ('zero_weight',[0,0,0,0],[1,2,3,4]),
            ('zero_operator',[1,2,0,0],[0,0,0,0]),
            ('constant_unperturbed',[1,0,0,0],[1,0,0,0]),
        ]
        self.check_examples(examples,12)

    def test_python_schur_agrees_through_size_64_including_repeated_singular_pivots(self):
        examples=[
            ('default_large_window',[1,1,0,0],[1,2,1,0]),
            ('cubic_weight_and_operator',[12,-12,12,12],[12,-12,12,-12]),
            ('initial_zero_block_and_odd_pivots',[0,0,0,1],[0,0,0,2]),
            ('interior_singular_minor',[1,0,0,0],[1,2,1,0]),
        ]
        self.check_examples(examples,64)


if __name__=='__main__':
    unittest.main()
