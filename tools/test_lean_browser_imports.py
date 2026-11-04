from pathlib import Path
import unittest
from unittest.mock import patch

from lean_browser_imports import (PAPER_I_PATH,PAPER_I_IMPORTS,PAPER_I_SOURCE,
    checked_original,validate_profile,profile_definition)


class BrowserImportProfileTests(unittest.TestCase):
    def test_unqualified_generated_profile_changes_are_rejected(self):
        with patch('lean_browser_imports.PAPER_I_SOURCE',PAPER_I_SOURCE+'\naxiom forged : False\n'):
            with self.assertRaisesRegex(ValueError,'repeat browser qualification'):
                profile_definition()

    def test_retained_import_body_cannot_be_silently_replaced(self):
        root=Path(__file__).resolve().parents[1]
        original=(root/PAPER_I_PATH).read_bytes()
        self.assertEqual(checked_original(original),original)
        with self.assertRaisesRegex(ValueError,'exact retained'):
            checked_original(original+b'\naxiom forged : False\n')
        with self.assertRaisesRegex(ValueError,'unavailable'):
            validate_profile(root,set(PAPER_I_IMPORTS)-{PAPER_I_IMPORTS[0]})

    def test_profile_imports_must_remain_in_the_pinned_original_ancestry(self):
        root=Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError,'ancestry'):
            validate_profile(root,PAPER_I_IMPORTS,{})
        members={'Mathlib/LinearAlgebra/FreeAlgebra.lean':
            b'import Mathlib.LinearAlgebra.Projection\nimport Mathlib.Analysis.SpecialFunctions.Complex.Log\n'}
        result=validate_profile(root,PAPER_I_IMPORTS,members)
        self.assertEqual(result['source'],PAPER_I_SOURCE)


if __name__=='__main__':unittest.main()
