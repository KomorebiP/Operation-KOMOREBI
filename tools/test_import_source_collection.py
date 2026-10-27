"""Small offline contracts for the source importer. No remote or Git writes."""
import hashlib
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

import import_source_collection as imp


class SourceImportTests(unittest.TestCase):
    def test_digest_has_declared_sorted_utf8_format(self):
        rows = [{"path": "z.txt", "sha256": "b" * 64}, {"path": "a.txt", "sha256": "a" * 64}]
        expected = hashlib.sha256(("a" * 64 + "  a.txt\n" + "b" * 64 + "  z.txt\n").encode()).hexdigest()
        self.assertEqual(imp.tree_digest(rows), expected)

    def test_filter_keeps_real_source_in_build_and_preserved(self):
        for path in ("compiled/proof.lean", "build/argument.tex", "preserved/record.json", ".env.example", ".env.sample"):
            self.assertIsNone(imp.omission_reason(path), path)
        for path in (".lake/packages/x.lean", "a/__pycache__/x.pyc", ".pytest_cache/state",
                     "formal_preservation/objects/sha256/abc", ".env.secret", "key.pem", "transfer.zip.003"):
            self.assertIsNotNone(imp.omission_reason(path), path)

    def test_traversal_rejected_even_outside_selected_prefix(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "source.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("good/a.txt", b"good")
                z.writestr("../escape", b"bad")
            with self.assertRaises(imp.ImportFailure):
                imp.select_zip(archive, "good")

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "source.zip"
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr(info, "../../escape")
            with self.assertRaises(imp.ImportFailure):
                imp.select_zip(archive)

    def test_prefix_extra_exact_bytes_and_expected_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            archive = base / "source.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("edition/source.txt", b"one\r\ntwo\r\n")
                z.writestr("edition/build/proof.lean", b"theorem sample : True := trivial\n")
                z.writestr("edition/.lake/ignored", b"cache")
                z.writestr("edition/old.zip", b"nested")
                z.writestr("LICENSE", b"license\n")
            component = {"id": "sample", "destination": "research/sample", "source": {
                "kind": "zip-url", "sha256": imp.sha256_file(archive), "prefix": "edition",
                "root_extra_files": ["LICENSE"]}}
            report = imp.prepare_component(component, base / "prepared", local_archive=archive, verify_expected=False)
            self.assertEqual(report["file_count"], 3)
            self.assertEqual((base / "prepared/source.txt").read_bytes(), b"one\r\ntwo\r\n")
            self.assertEqual(len(report["omissions"]), 2)
            component["expected"] = {"file_count": 3, "tree_sha256": "0" * 64}
            with self.assertRaises(imp.ImportFailure):
                imp.prepare_component(component, base / "bad-expected", local_archive=archive)

    def test_receipt_owns_exact_paths_and_adopts_identical_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            prepared = Path(temp) / "prepared"
            root.mkdir()
            prepared.mkdir()
            (prepared / "source.txt").write_bytes(b"source\n")
            h = hashlib.sha256(b"source\n").hexdigest()
            files = [{"path": "source.txt", "size": 7, "sha256": h, "mode": "100644"}]
            component = {"id": "sample", "destination": "monographs/sample", "source": {"kind": "zip-url"},
                         "expected": {"file_count": 1, "tree_sha256": imp.tree_digest(files)}}
            report = {"files": files, "component_sha256": imp._fingerprint(component)}
            imp._install_owned(component, prepared, report, root)
            child = root / "monographs/sample/continuation"
            child.mkdir()
            (child / "other.lean").write_text("independent child\n")
            imp._install_owned(component, prepared, report, root)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps(report))
            self.assertTrue(imp.receipt_matches(component, root, receipt))
            (root / "monographs/sample/source.txt").write_bytes(b"conflict\n")
            self.assertFalse(imp.receipt_matches(component, root, receipt))
            with self.assertRaises(imp.ImportFailure):
                imp._install_owned(component, prepared, report, root)
            self.assertEqual((child / "other.lean").read_text(), "independent child\n")


if __name__ == "__main__":
    unittest.main()
