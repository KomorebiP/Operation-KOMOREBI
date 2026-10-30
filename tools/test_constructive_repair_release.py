"""Regression controls for the new distribution gate; no mathematical proof claim."""
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

import constructive_repair_release as R


class GateResults(unittest.TestCase):
    def log(self, system):
        names = sorted(R.SYMLINK_TESTS | R.WINDOWS_SKIPS)
        names += ["synthetic.Regression.test_" + str(i) for i in range(100-len(names))]
        return "\n".join("test_x ("+name+") ... "+(
            "skipped 'POSIX fixture'" if system=="Windows" and name in R.WINDOWS_SKIPS
            else "ok") for name in names)

    def acceptance(self):
        return {"status":"PASS","wheel_sha256":"a"*64,"source_sha256":{"x":"b"*64},
                "checks":{"release_test_count":{"pass":True,"detail":100},
                          "engine_test_count":{"pass":True,"detail":134},
                          "installed_problem_count":{"pass":True,"detail":72}}}

    def test_linux_runs_all_release_tests(self):
        result=R.release_test_results(self.log("Linux"),"Linux")
        self.assertEqual((result["run"],result["passed"],result["skipped"]),(100,100,[]))

    def test_windows_only_skips_named_posix_controls(self):
        result=R.release_test_results(self.log("Windows"),"Windows")
        self.assertEqual(result["passed"],97)
        self.assertEqual(set(result["skipped"]),R.WINDOWS_SKIPS)

    def test_linux_cannot_inherit_windows_skips(self):
        with self.assertRaisesRegex(ValueError,"skipped"):
            R.release_test_results(self.log("Windows"),"Linux")

    def test_partial_test_log_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"100"):
            R.release_test_results("\n".join(self.log("Linux").splitlines()[:-1]),"Linux")

    def test_symlink_control_must_pass(self):
        name=next(iter(R.SYMLINK_TESTS))
        bad=self.log("Windows").replace("("+name+") ... ok",
                                       "("+name+") ... skipped 'privilege missing'")
        with self.assertRaises(ValueError):
            R.release_test_results(bad,"Windows")

    def test_unrelated_skips_are_rejected(self):
        bad=self.log("Windows").replace(
            "(synthetic.Regression.test_0) ... ok",
            "(synthetic.Regression.test_0) ... skipped 'unexpected'")
        with self.assertRaises(ValueError):
            R.release_test_results(bad,"Windows")

    def test_acceptance_is_bound_to_actual_wheel(self):
        with self.assertRaisesRegex(ValueError,"different wheel"):
            R.check_acceptance(self.acceptance(),"c"*64)

    def test_failed_acceptance_check_is_rejected(self):
        data=self.acceptance()
        data["checks"]["release_test_count"]["pass"]=False
        with self.assertRaises(ValueError):
            R.check_acceptance(data,"a"*64)

    def test_coverage_mismatch_is_rejected(self):
        data=self.acceptance()
        data["checks"]["engine_test_count"]["detail"]=133
        with self.assertRaisesRegex(ValueError,"coverage"):
            R.check_acceptance(data,"a"*64)


class WheelGate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=R.native(self.temp.name)
        self.source=self.root/"source"
        package=self.source/"python/komorebi_repair"
        package.mkdir(parents=True)
        for name in ("__init__.py","__main__.py","api.py","cli.py"):
            (package/name).write_text("# fixture\n",encoding="utf-8")
        for name in ("repair_certificates.py","rational_menu.py","branch_menu.py"):
            (self.source/"python"/name).write_text("# fixture\n",encoding="utf-8")
        self.code=self.root/"LICENSE-CODE.txt"
        self.collection=self.root/"LICENSE-COLLECTION.md"
        self.readme=self.root/"README.md"
        for path,text in ((self.code,"code terms\n"),(self.collection,"collection terms\n"),
                          (self.readme,"Release instructions — Komorebi P.\n")):
            path.write_text(text,encoding="utf-8")
        self.wheel=self.root/"fixture.whl"

    def make(self, change=None, reverse=False):
        contents={name:(self.source/"python"/name).read_bytes()
                  for name in R.runtime_names(self.source)}
        prefix="komorebi_constructive_repair-1.0.0rc3.dist-info/"
        contents[prefix+"METADATA"]=(
            "Metadata-Version: 2.4\nName: komorebi-constructive-repair\n"
            "Version: 1.0.0rc3\nLicense-Expression: MIT\n\nRelease instructions — Komorebi P.\n").encode()
        contents[prefix+"licenses/LICENSE-CODE.txt"]=self.code.read_bytes()
        contents[prefix+"licenses/LICENSE-COLLECTION.md"]=self.collection.read_bytes()
        contents[prefix+"WHEEL"]=b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        if change:
            change(contents,prefix)
        if reverse:
            for name in contents:
                if name.endswith(("/METADATA","/WHEEL")):
                    contents[name]=contents[name].replace(b"\n",b"\r\n")
        rows=[]
        for name,data in sorted(contents.items(),reverse=reverse):
            digest=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            rows.append([name,"sha256="+digest,str(len(data))])
        record=prefix+"RECORD"
        rows.append([record,"",""])
        out=io.StringIO()
        csv.writer(out,lineterminator="\n").writerows(rows)
        contents[record]=out.getvalue().encode()
        with zipfile.ZipFile(self.wheel,"w") as z:
            for name in sorted(contents,reverse=reverse):
                info=zipfile.ZipInfo(name,(2025 if reverse else 2024,1,1,0,0,0))
                info.external_attr=(0o100666 if reverse else 0o100644)<<16
                z.writestr(info,contents[name])

    def check(self):
        return R.verify_wheel(self.wheel,self.source,self.code,self.collection,self.readme)

    def test_exact_runtime_and_current_metadata_pass(self):
        self.make()
        self.assertEqual(len(self.check()["runtime_files"]),7)

    def test_valid_record_does_not_hide_altered_runtime(self):
        self.make(lambda contents,prefix: contents.update({"branch_menu.py":b"changed\n"}))
        with self.assertRaisesRegex(ValueError,"Wheel/source"):
            self.check()

    def test_valid_record_does_not_hide_wrong_license(self):
        self.make(lambda contents,prefix: contents.update(
            {prefix+"licenses/LICENSE-CODE.txt":b"other terms\n"}))
        with self.assertRaisesRegex(ValueError,"license"):
            self.check()

    def test_old_readme_metadata_is_rejected(self):
        self.make(lambda contents,prefix: contents.update(
            {prefix+"METADATA":contents[prefix+"METADATA"].replace(
                b"Release instructions",b"Old undecided notice")}))
        with self.assertRaisesRegex(ValueError,"README"):
            self.check()

    def test_record_hash_corruption_is_rejected(self):
        self.make()
        with zipfile.ZipFile(self.wheel) as z:
            entries={name:z.read(name) for name in z.namelist()}
        record=next(n for n in entries if n.endswith("/RECORD"))
        entries[record]=entries[record].replace(b"sha256=",b"sha255=",1)
        with zipfile.ZipFile(self.wheel,"w") as z:
            for name,data in entries.items():
                z.writestr(name,data)
        with self.assertRaisesRegex(ValueError,"RECORD"):
            self.check()

    def test_platform_zip_metadata_and_record_order_normalize(self):
        self.make()
        R.normalized_wheel(self.wheel)
        first=self.wheel.read_bytes()
        self.make(reverse=True)
        R.normalized_wheel(self.wheel)
        self.assertEqual(first,self.wheel.read_bytes())
        self.check()

    def test_duplicate_wheel_entries_rejected(self):
        self.make()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with zipfile.ZipFile(self.wheel,"a") as z:
                z.writestr("branch_menu.py",b"duplicate")
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            R.normalized_wheel(self.wheel)


class ArchiveGate(unittest.TestCase):
    def test_escaping_archive_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=R.native(td)
            archive=root/"bad.zip"
            with zipfile.ZipFile(archive,"w") as z:
                info=zipfile.ZipInfo("bundle/../../outside.txt")
                info.create_system=3
                info.external_attr=0o100644<<16
                z.writestr(info,b"escape")
            with self.assertRaisesRegex(ValueError,"Unsafe"):
                R.extract_verified(archive,root/"extracted")
            self.assertFalse((root/"outside.txt").exists())

    def test_unlisted_distribution_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=R.native(td)
            (root/"listed.txt").write_bytes(b"original")
            R.write_manifest(root)
            (root/"unlisted.txt").write_bytes(b"extra")
            with self.assertRaisesRegex(ValueError,"inventory"):
                R.verify_bundle(root)

    def test_changed_distribution_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=R.native(td)
            (root/"listed.txt").write_bytes(b"original")
            R.write_manifest(root)
            (root/"listed.txt").write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                R.verify_bundle(root)


if __name__=="__main__":
    unittest.main()
