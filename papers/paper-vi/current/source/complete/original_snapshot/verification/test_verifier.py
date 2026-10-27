"""Negative controls exercise verification gates, including under optimized Python."""
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
import verify

class Gates(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        shutil.copytree(verify.ROOT/'formalization',self.root/'formalization',ignore=shutil.ignore_patterns('.lake'))
        (self.root/'verification').mkdir()
        shutil.copy(verify.ROOT/'verification/source_contract.json',self.root/'verification/source_contract.json')
        shutil.copy(verify.ROOT/'THEOREM_LEDGER.json',self.root/'THEOREM_LEDGER.json')
    def tearDown(self):self.temp.cleanup()
    def update_hash(self,rel):
        p=self.root/'verification/source_contract.json';c=json.loads(p.read_text())
        c['source_sha256'][rel]=hashlib.sha256((self.root/rel).read_bytes()).hexdigest();p.write_text(json.dumps(c))
    def test_valid_static_contract(self):self.assertEqual(verify.static_checks(self.root)['theorems'],len(verify.read_json(self.root/'verification/source_contract.json')['theorem_targets']))
    def test_corrupt_source_rejected(self):
        p=self.root/'formalization/lean/KomorebiPaperVI/Algebra.lean';p.write_text(p.read_text()+'\n-- modified\n')
        with self.assertRaises(verify.VerificationError):verify.static_checks(self.root)
    def test_placeholder_with_refreshed_hash_rejected(self):
        rel='formalization/lean/KomorebiPaperVI/Algebra.lean';p=self.root/rel
        p.write_text(p.read_text()+'\nexample : True := by sorry\n');self.update_hash(rel)
        with self.assertRaisesRegex(verify.VerificationError,'Forbidden'):verify.static_checks(self.root)
    def test_missing_audit_with_refreshed_hash_rejected(self):
        rel='formalization/lean/KernelAudit.lean';p=self.root/rel
        lines=p.read_text().splitlines();idx=next(i for i,s in enumerate(lines) if s.startswith('#print axioms'))
        del lines[idx];p.write_text('\n'.join(lines)+'\n');self.update_hash(rel)
        with self.assertRaisesRegex(verify.VerificationError,'Audit print'):verify.static_checks(self.root)
    def test_missing_import_with_refreshed_hash_rejected(self):
        rel='formalization/lean/KomorebiPaperVI.lean';p=self.root/rel
        p.write_text('\n'.join(p.read_text().splitlines()[1:])+'\n');self.update_hash(rel)
        with self.assertRaisesRegex(verify.VerificationError,'Root import'):verify.static_checks(self.root)
    def test_optimized_python_rejects_corrupt_source(self):
        p=self.root/'formalization/lean/lean-toolchain';p.write_text('leanprover/lean4:v0.0.0\n')
        command='import verify; from pathlib import Path; verify.static_checks(Path('+repr(str(self.root))+'))'
        result=subprocess.run([sys.executable,'-O','-c',command],cwd=verify.ROOT/'verification',capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Unexpected toolchain',result.stderr)

if __name__=='__main__':unittest.main()
