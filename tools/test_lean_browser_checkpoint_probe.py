from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import lean_checkpoint_probe as probe


class ProbeBuildBoundaries(unittest.TestCase):
    def test_existing_output_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'keep.txt'
            marker.write_text('retained')
            with patch.object(probe, 'verify_runtime') as verify:
                with self.assertRaisesRegex(ValueError, 'new output'):
                    probe.build(root / 'runtime', root)
                verify.assert_not_called()
            self.assertEqual(marker.read_text(), 'retained')

    def test_output_cannot_recursively_copy_its_own_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp)
            with patch.object(probe, 'verify_runtime') as verify:
                with self.assertRaisesRegex(ValueError, 'outside the runtime'):
                    probe.build(runtime, runtime / 'nested-probe')
                verify.assert_not_called()
            self.assertFalse((runtime / 'nested-probe').exists())

    def test_changed_original_source_stops_before_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'probe'
            with patch.object(probe, 'verify_runtime', return_value={}), patch.object(probe, 'SOURCE_SHA', '0' * 64):
                with self.assertRaisesRegex(ValueError, 'original Proof Path sources changed'):
                    probe.build(Path(tmp) / 'runtime', output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
