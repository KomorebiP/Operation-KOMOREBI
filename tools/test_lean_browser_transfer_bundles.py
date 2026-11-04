import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import lean_transfer_bundles as transfer


class TransferRecordsTests(unittest.TestCase):
    def setUp(self):
        self.original={f'loose/Batteries/Test{i}.olean.gz':dict(size=20,sha256=str(i)*64,url='https://example.test/pinned/'+str(i)) for i in range(4)}
        self.catalog=dict(members=copy.deepcopy(self.original),unbundled=[],groups=[
            dict(file='transfers/'+'a'*64+'.bundle',size=80,sha256='a'*64,members=list(self.original))])
        self.raw=(json.dumps(self.catalog)+'\n').encode()
        p=patch.object(transfer,'read_catalog',side_effect=lambda:(self.catalog,self.raw));p.start();self.addCleanup(p.stop)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def record(self):
        plan,remote=transfer.records(self.original)
        return dict(files={},remote_files={**self.original,**remote},transfer_groups=plan)

    def test_optional_plan_preserves_original_member_records_without_local_binaries(self):
        record=self.record();transfer.verify(self.root,record)
        self.assertEqual({p:record['remote_files'][p] for p in self.original},self.original)
        self.assertFalse((self.root/'transfers').exists())

    def test_original_checksum_size_and_url_changes_cannot_be_authorized_by_new_records(self):
        for key,value in [('sha256','f'*64),('size',21),('url','https://example.test/changed')]:
            changed=copy.deepcopy(self.original);next(iter(changed.values()))[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'member identities'):transfer.records(changed)

    def test_oversized_misaddressed_and_miscounted_groups_rejected(self):
        original=copy.deepcopy(self.catalog)
        for field,value in [('size',1048577),('size',81),('file','transfers/'+'b'*64+'.bundle')]:
            self.catalog=copy.deepcopy(original);self.catalog['groups'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):transfer.records(self.original)

    def test_duplicate_unknown_and_missing_members_rejected(self):
        original=copy.deepcopy(self.catalog)
        for members in [[*list(self.original)[:3],next(iter(self.original))],['loose/Missing.gz',*list(self.original)[1:]],list(self.original)[:3]]:
            self.catalog=copy.deepcopy(original);self.catalog['groups'][0]['members']=members
            with self.subTest(members=members),self.assertRaises(ValueError):transfer.records(self.original)

    def test_deleted_plan_and_forged_group_records_rejected(self):
        record=self.record();record.pop('transfer_groups')
        with self.assertRaisesRegex(ValueError,'Unrecorded'):transfer.verify(self.root,record)
        record=self.record();record['remote_files'][self.catalog['groups'][0]['file']]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Pinned transfer'):transfer.verify(self.root,record)

    def test_self_rehashed_plan_cannot_reorder_member_ranges(self):
        record=self.record();record['transfer_groups']['groups'][0]['members']=list(reversed(record['transfer_groups']['groups'][0]['members']))
        with self.assertRaisesRegex(ValueError,'Pinned transfer'):transfer.verify(self.root,record)

    def test_binary_assets_cannot_be_copied_into_pages(self):
        record=self.record();(self.root/'transfers').mkdir()
        with self.assertRaisesRegex(ValueError,'Pinned transfer'):transfer.verify(self.root,record)

    def test_legacy_runtime_needs_no_transfer_plan(self):
        transfer.verify(self.root,dict(files={},remote_files=self.original))

    def test_transfer_url_allowlist_excludes_compiler_and_other_paths(self):
        for path in ['lean-wasm/lean.js','transfers/../bad.bundle','transfers/not-a-hash.bundle']:
            self.assertIsNone(transfer.asset_url(path))


class TransferCatalogPinTests(unittest.TestCase):
    def test_catalog_allows_only_checkout_line_ending_changes(self):
        path=Path(__file__).resolve().parents[1]/'manifests/lean-transfer-bundles.json';raw=path.read_bytes().replace(b'\r\n',b'\n')
        with patch.object(Path,'read_bytes',return_value=raw.replace(b'\n',b'\r\n')):self.assertEqual(transfer.read_catalog()[1],raw)
        with patch.object(Path,'read_bytes',return_value=raw+b' '):
            with self.assertRaisesRegex(ValueError,'catalog changed'):transfer.read_catalog()


if __name__=='__main__':unittest.main()
