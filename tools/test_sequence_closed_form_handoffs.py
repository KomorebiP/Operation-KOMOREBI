"""Cross-check all curated closed-form calculator presets against exact source terms.

Author: Komorebi P.
The Python catalogue and browser BigInt engine are independent implementations.
Their finite equality is a regression test, not a claim of historical novelty.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from sequence_formula_catalogue import expanded_catalogue


class ExactCalculatorHandoffTests(unittest.TestCase):
    def test_all_closed_form_parameter_presets_match_retained_integer_windows(self):
        records=[row for row in expanded_catalogue()
                 if row.get('closed_form_collection')]
        self.assertEqual(len(records),35)
        cases=[]
        for row in records:
            self.assertIn('calculator',row,row['id'])
            values=row['terms']
            self.assertEqual(len(values),24)
            cases.append({
                'id':row['id'],
                'offset':row['offset'],
                'calculator':row['calculator'],
                'expected':values[:12],
            })
        self.assertEqual(len({case['id'] for case in cases}),35)
        runner=subprocess.run(
            ['node',str(ROOT/'tools/test_sequence_closed_form_handoffs.mjs')],
            input=json.dumps(cases,separators=(',',':')),text=True,
            capture_output=True,cwd=ROOT,check=False,
        )
        self.assertEqual(runner.returncode,0,runner.stderr or runner.stdout)
        report=json.loads(runner.stdout)
        self.assertEqual(report['records'],35)
        self.assertEqual(report['checked_integer_values'],420)
        self.assertTrue(report['all_exact'])
        self.assertEqual(len(report['modes']),8)


if __name__=='__main__':
    unittest.main()
