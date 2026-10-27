#!/usr/bin/env python3
"""Local filesystem/unit checks. These do not execute GitHub Actions or Lean."""
from pathlib import Path
import hashlib, json, sys, tempfile, unittest
SUPPORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SUPPORT/'ci'))
from verify_frozen_lean import checked_path, verify_manifest
from bootstrap_lake_kit import make_layout, safe_link
from create_draft_release import validate_assets, draft_command

class ManifestChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='ci-unit-',dir=Path(__file__).parent)
        self.root=Path(self.temp.name);(self.root/'payload.txt').write_bytes(b'checked\n')
        payload=self.root/'payload.txt'
        manifest={'files':{'payload.txt':{'bytes':payload.stat().st_size,'sha256':hashlib.sha256(payload.read_bytes()).hexdigest()}}}
        p=self.root/'MANIFEST.json';p.write_text(json.dumps(manifest));self.sha=hashlib.sha256(p.read_bytes()).hexdigest()
    def tearDown(self):self.temp.cleanup()
    def test_exact_bytes_pass(self):
        result=verify_manifest(self.root,self.sha);self.assertEqual(result['files_checked'],1);self.assertFalse(result['fresh_lean_execution'])
    def test_changed_payload_fails(self):
        (self.root/'payload.txt').write_bytes(b'changed\n')
        with self.assertRaisesRegex(ValueError,'Changed frozen'):verify_manifest(self.root,self.sha)
    def test_changed_manifest_fails(self):
        (self.root/'MANIFEST.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'manifest differs'):verify_manifest(self.root,self.sha)
    def test_extra_unlisted_payload_fails(self):
        (self.root/'extra.txt').write_text('extra')
        with self.assertRaisesRegex(ValueError,'inventory'):verify_manifest(self.root,self.sha)
    def test_generated_objects_do_not_change_frozen_payload(self):
        (self.root/'.build').mkdir();(self.root/'.build/generated.olean').write_bytes(b'generated')
        self.assertTrue(verify_manifest(self.root,self.sha)['passed'])
    def test_noncanonical_paths_fail(self):
        for name in ('../escape','/absolute','a\\b',''):
            with self.subTest(name=name),self.assertRaises(ValueError):checked_path(self.root,name)
    def test_symlink_escape_fails(self):
        external=self.root.parent/'outside-ci-test.tmp';external.write_text('outside')
        try:
            (self.root/'link').symlink_to(external)
            with self.assertRaisesRegex(ValueError,'leaves the project'):checked_path(self.root,'link')
        finally:external.unlink()

class AdapterLayoutChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='adapter-unit-',dir=Path(__file__).parent)
        self.root=Path(self.temp.name);self.prefix=self.root/'prefix';self.packages=self.root/'packages';self.packages.mkdir()
        for rel in ('bin/lean','bin/leanchecker','src/lean/LeanChecker.lean'):
            p=self.prefix/rel;p.parent.mkdir(parents=True,exist_ok=True);p.touch()
    def tearDown(self):self.temp.cleanup()
    def test_adapter_points_to_real_directories(self):
        kit=self.root/'kit';make_layout(kit,self.prefix,self.packages)
        self.assertEqual((kit/'toolchain').resolve(),self.prefix)
        self.assertEqual((kit/'workspace/.lake/packages').resolve(),self.packages)
    def test_missing_checker_fails(self):
        (self.prefix/'bin/leanchecker').unlink()
        with self.assertRaisesRegex(ValueError,'lacks bin/leanchecker'):make_layout(self.root/'kit',self.prefix,self.packages)
    def test_existing_directory_is_not_overwritten(self):
        target=self.root/'occupied';target.mkdir()
        with self.assertRaisesRegex(ValueError,'Refusing to replace'):safe_link(target,self.prefix)

class DraftAssetChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='draft-unit-',dir=Path(__file__).parent)
        self.root=Path(self.temp.name)
        (self.root/'Release_1.0.0.zip').write_bytes(b'unit asset bytes')
        h=hashlib.sha256((self.root/'Release_1.0.0.zip').read_bytes()).hexdigest()
        (self.root/'SHA256SUMS.txt').write_text(h+'  Release_1.0.0.zip\n')
        self.manifest={'version':'1.0.0','files':['Release_1.0.0.zip','SHA256SUMS.txt']}
        self.save()
    def save(self):(self.root/'assets.json').write_text(json.dumps(self.manifest))
    def tearDown(self):self.temp.cleanup()
    def test_checked_assets_are_accepted(self):self.assertEqual(len(validate_assets(self.root)),2)
    def test_changed_asset_is_rejected(self):
        (self.root/'Release_1.0.0.zip').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):validate_assets(self.root)
    def test_asset_path_escape_is_rejected(self):
        self.manifest['files']=['../outside.zip','SHA256SUMS.txt'];self.save()
        with self.assertRaises(ValueError):validate_assets(self.root)
    def test_other_version_is_rejected(self):
        self.manifest['version']='2.0.0';self.save()
        with self.assertRaisesRegex(ValueError,'exactly 1.0.0'):validate_assets(self.root)
    def test_command_is_static_draft_without_clobber(self):
        argv=draft_command('owner/repository','a'*40,validate_assets(self.root),self.root/'notes.md')
        self.assertEqual(argv[:4],['gh','release','create','v1.0.0'])
        self.assertIn('--draft',argv);self.assertNotIn('--clobber',argv)
        with self.assertRaises(ValueError):draft_command('owner/repo;echo x','a'*40,[],self.root/'notes.md')

if __name__=='__main__':unittest.main()
