"""Local safety tests. No live GitHub requests or writes occur."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import create_private_repo as upload
import check_github_ready as check

class UploadSafety(unittest.TestCase):
    def test_expected_destination(self):
        self.assertEqual(upload.validate_destination('KomorebiP/komorebi-math'),'KomorebiP/komorebi-math')
    def test_reject_other_owner(self):
        with self.assertRaises(upload.PreparationError): upload.validate_destination('other/komorebi-math')
    def test_reject_urls_paths_and_flags(self):
        for value in ['https://github.com/KomorebiP/repo','KomorebiP/../x','KomorebiP/-x','KomorebiP/a b','KomorebiP/x.git']:
            with self.subTest(value=value),self.assertRaises(upload.PreparationError): upload.validate_destination(value)
    def test_private_create_only(self):
        argv=upload.private_create_command(upload.DEFAULT_REPOSITORY)
        self.assertIn('--private',argv)
        self.assertNotIn('--public',argv)
        self.assertNotIn('--license',argv)
    def test_push_main_only_no_force(self):
        argv=upload.push_command()
        self.assertEqual(argv[-1],'HEAD:refs/heads/main')
        self.assertFalse(any(x in argv for x in ['--force','--mirror','--all','--tags']))
    def test_owner_id_must_match(self):
        with self.assertRaises(upload.PreparationError): upload.require_owner({'login':'KomorebiP','id':1})
    def test_public_remote_rejected(self):
        meta={'owner':{'login':upload.OWNER,'id':upload.OWNER_ID},'full_name':upload.DEFAULT_REPOSITORY,'private':False}
        with self.assertRaises(upload.PreparationError): upload.require_private_repository(meta,upload.DEFAULT_REPOSITORY)
    def test_empty_private_remote_accepted(self):
        meta={'owner':{'login':upload.OWNER,'id':upload.OWNER_ID},'full_name':upload.DEFAULT_REPOSITORY,'private':True}
        upload.require_private_repository(meta,upload.DEFAULT_REPOSITORY)
        upload.require_empty([])
    def test_existing_history_rejected(self):
        with self.assertRaises(upload.PreparationError): upload.require_empty([{'name':'main'}])
    def test_invalid_branch_listing_rejected(self):
        with self.assertRaises(upload.PreparationError): upload.require_empty(None)
    def test_nonpseudonymous_history_rejected(self):
        with self.assertRaises(upload.PreparationError): upload.require_identity_history('Name\0address@example.invalid\0Name\0address@example.invalid\n')
    def test_expected_identity_accepted(self):
        upload.require_identity_history('\0'.join([upload.AUTHOR,upload.EMAIL,upload.AUTHOR,upload.EMAIL])+'\n')
    def test_dry_run_makes_no_subprocess_call(self):
        with patch.object(sys,'argv',['create_private_repo.py']), patch.object(upload,'invoke') as inv, patch('builtins.print'):
            self.assertEqual(upload.main(),0)
            inv.assert_not_called()
    def test_missing_cli_fails_before_remote(self):
        with patch.object(upload.shutil,'which',side_effect=lambda name:'/usr/bin/git' if name=='git' else None), patch.object(upload,'invoke') as inv:
            with self.assertRaises(upload.PreparationError): upload.execute(upload.DEFAULT_REPOSITORY)
            inv.assert_not_called()

class WorkflowSafety(unittest.TestCase):
    pin='a'*40
    pins={'actions/checkout':{'sha':pin}}
    good='permissions:\n  contents: read\njobs:\n  check:\n    timeout-minutes: 5\n    steps:\n      - uses: actions/checkout@' + pin + '\n        with:\n          persist-credentials: false\n'
    def test_readonly_pinned(self): self.assertEqual(check.workflow_errors(self.good,self.pins),[])
    def test_mutable_pin_rejected(self): self.assertTrue(check.workflow_errors(self.good.replace(self.pin,'v7'),self.pins))
    def test_privileged_trigger_rejected(self): self.assertTrue(check.workflow_errors('on: pull_request_target\n'+self.good,self.pins))
    def test_write_permission_rejected(self): self.assertTrue(check.workflow_errors(self.good.replace('contents: read','contents: write'),self.pins))
    def test_ignored_failure_rejected(self): self.assertTrue(check.workflow_errors(self.good+'    continue-on-error: true\n',self.pins))
    def test_generated_receipts_not_sealed(self):
        self.assertTrue(check.is_generated(Path('padic/results/fresh/REPLAY.json')))
        self.assertFalse(check.is_generated(Path('padic/results/.gitkeep')))
        self.assertFalse(check.is_generated(Path('padic/evidence/block34_recorded_build.log')))

if __name__=='__main__': unittest.main()
