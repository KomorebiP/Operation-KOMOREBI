"""Cross-language rational Hankel recurrence and common-kernel regression.

Author: Komorebi P. Existing Schur/direct determinants are independent checks.
"""
import json
from pathlib import Path
import subprocess
import unittest
from sequence_rational_hankel import (
    linear_hankel_determinants, linear_hankel_generating_function, canonical_kernel,
)
from sequence_differential_hankel import structured_differential_hankel

ROOT=Path(__file__).resolve().parents[1]


class LinearHankelBridgeTests(unittest.TestCase):
    def test_integer_grid_signed_degenerate_and_large_indices(self):
        fixtures=[]
        parameters=[(a,b) for a in range(-3,4) for b in range(-3,4)]
        parameters += [(-12,-12),(-12,12),(12,-12),(12,12)]
        for a,b in parameters:
            values=linear_hankel_determinants(a,b,256)
            self.assertEqual(values[:33],structured_differential_hankel([a,b],[1],32))
            numerator,denominator=linear_hankel_generating_function(a,b)
            fixtures.append(dict(a=a,b=b,values=list(map(str,values)),
                                 numerator=list(map(str,numerator)),
                                 denominator=list(map(str,denominator))))
        kernels=[]
        for a,c in [([1],[1]),([1,1],[1,2,1]),([0,1],[0,0,1]),
                    ([1,-2,3,-1],[0,1,0,2]),([0],[1,2])]:
            numerator,pole=canonical_kernel(a,c)
            kernels.append(dict(a=a,c=c,numerator=list(map(str,numerator)),pole=pole))
        run=subprocess.run(['node',str(ROOT/'tools/test_sequence_linear_hankel_bridge.mjs')],
            input=json.dumps(dict(fixtures=fixtures,kernels=kernels)),text=True,cwd=ROOT,
            capture_output=True,timeout=90)
        self.assertEqual(run.returncode,0,run.stderr or run.stdout)
        self.assertEqual(json.loads(run.stdout),
                         dict(cases=53,exact_values=53*257,kernel_cases=5,all_exact=True))


if __name__=='__main__':
    unittest.main()
