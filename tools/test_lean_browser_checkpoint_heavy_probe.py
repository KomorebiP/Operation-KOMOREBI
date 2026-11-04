from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import lean_checkpoint_heavy_probe as probe


class HeavyProbeBoundaries(unittest.TestCase):
    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'keep.txt'
            marker.write_text('retained')
            with patch.object(probe, 'verify_runtime') as verify:
                with self.assertRaisesRegex(ValueError, 'new output'):
                    probe.build(root / 'runtime', root)
                verify.assert_not_called()
            self.assertEqual(marker.read_text(), 'retained')

    def test_output_is_outside_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(probe, 'verify_runtime') as verify:
                with self.assertRaisesRegex(ValueError, 'outside the runtime'):
                    probe.build(root, root / 'nested')
                verify.assert_not_called()
            self.assertFalse((root / 'nested').exists())

    def test_each_changed_original_is_rejected_before_output(self):
        for index, (module, _) in enumerate(probe.ORIGINALS):
            with self.subTest(module=module), tempfile.TemporaryDirectory() as tmp:
                changed = list(probe.ORIGINALS)
                changed[index] = (module, '0' * 64)
                output = Path(tmp) / 'probe'
                with patch.object(probe, 'verify_runtime', return_value={}), patch.object(probe, 'ORIGINALS', changed):
                    with self.assertRaisesRegex(ValueError, 'original Conventions source changed'):
                        probe.build(Path(tmp) / 'runtime', output)
                self.assertFalse(output.exists())

    def test_changed_library_is_rejected(self):
        repo = Path(probe.__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module, _ = probe.LIBRARIES[0]
            asset = 'lean-mathlib/sources/' + module.replace('.', '/') + '.lean'
            path = root / asset
            path.parent.mkdir(parents=True)
            path.write_bytes(b'changed')
            row = dict(module=module, asset=asset, source='changed', sha256=probe.sha(b'changed'), size=7)
            with self.assertRaisesRegex(ValueError, 'source library changed'):
                probe.pinned_inputs(repo, root, dict(mathlib_source_modules={module: row}))


if __name__ == '__main__':
    unittest.main()
