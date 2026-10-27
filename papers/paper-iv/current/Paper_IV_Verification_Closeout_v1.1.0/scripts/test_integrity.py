#!/usr/bin/env python3
"""Adversarial tests of distribution verification. No Lean theorem claims."""
import json
from pathlib import Path
import sys, tempfile, unittest
from verify_release import verify_manifest, sha

class IntegrityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  (self.root/'sample.txt').write_text('unchanged')
  self.manifest={'files':[{'path':'sample.txt','bytes':9,'sha256':sha(self.root/'sample.txt')}]}
  (self.root/'MANIFEST.json').write_text(json.dumps(self.manifest))
 def tearDown(self):self.temp.cleanup()
 def test_positive(self):self.assertEqual(verify_manifest(self.root,self.manifest)['files'],1)
 def test_changed(self):
  (self.root/'sample.txt').write_text('corrupted')
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_missing(self):
  (self.root/'sample.txt').unlink()
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_unexpected(self):
  (self.root/'extra').write_text('extra')
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_unsafe_path(self):
  self.manifest['files'][0]['path']='../sample.txt'
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_absolute_path(self):
  self.manifest['files'][0]['path']='/sample.txt'
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_duplicate_member(self):
  self.manifest['files']*=2
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_symlink(self):
  (self.root/'link.txt').symlink_to(self.root/'sample.txt')
  self.manifest['files'][0]['path']='link.txt'
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_forbidden_font(self):
  (self.root/'sample.txt').rename(self.root/'sample.otf');self.manifest['files'][0]['path']='sample.otf'
  with self.assertRaises(ValueError):verify_manifest(self.root,self.manifest)
 def test_empty_manifest(self):
  with self.assertRaises(ValueError):verify_manifest(self.root,{'files':[]})

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityTests))
 report={'status':'PASS' if result.wasSuccessful() else 'FAILED','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
