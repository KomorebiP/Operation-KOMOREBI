"""Fail closed when published source identity or availability records drift."""
import copy
import hashlib
import unittest
from import_source_collection import ImportFailure, _fingerprint, tree_digest
from check_source_receipts import check_records


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        raw=b'fixed source\n'
        self.f={'path':'Source.lean','sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'mode':'100644'}
        digest=tree_digest([self.f])
        c={'id':'a','destination':'research/a','expected':{'file_count':1,'tree_sha256':digest}}
        self.config={'components':[c]}
        self.receipts={'a':{'component':'a','destination':'research/a','component_sha256':_fingerprint(c),
            'files':[self.f],'file_count':1,'tree_sha256':digest}}
        self.state={'components':[{'id':'a','destination':'research/a','role':'primary','available':True,
            'disposition':'imported','file_count':1,'tree_sha256':digest}],
            'totals':{'selected_components':1,'available_components':1,'selected_primary_components':1,
                'available_primary_components':1,'selected_supporting_components':0,'available_supporting_components':0,
                'unique_source_files':1,'pending_components':0,'primary_components_by_group':{'research':1}}}
        self.tree={'research/a/Source.lean':{'sha':self.f['git_blob_sha1'],'mode':'100644'}}

    def run_check(self):return check_records(self.config,self.state,self.receipts,self.tree)
    def test_valid_source(self):self.assertEqual(self.run_check()['owned_source_files'],1)
    def test_changed_blob(self):
        self.tree['research/a/Source.lean']['sha']='0'*40
        with self.assertRaisesRegex(ImportFailure,'Published source mismatch'):self.run_check()
    def test_changed_mode(self):
        self.tree['research/a/Source.lean']['mode']='100755'
        with self.assertRaisesRegex(ImportFailure,'Published source mismatch'):self.run_check()
    def test_path_case_is_exact(self):
        self.tree['research/a/source.lean']=self.tree.pop('research/a/Source.lean')
        with self.assertRaisesRegex(ImportFailure,'Published source mismatch'):self.run_check()
    def test_duplicate_file_cannot_inflate_count(self):
        self.receipts['a']['files'].append(copy.deepcopy(self.f))
        with self.assertRaisesRegex(ImportFailure,'Duplicate receipt path'):self.run_check()
    def test_duplicate_component(self):
        self.config['components'].append(copy.deepcopy(self.config['components'][0]))
        with self.assertRaisesRegex(ImportFailure,'Duplicate component ID'):self.run_check()
    def test_receipt_bound_to_configuration(self):
        self.config['components'][0]['extra']='changed'
        with self.assertRaisesRegex(ImportFailure,'configuration binding'):self.run_check()
    def test_aggregate_digest_checked(self):
        self.receipts['a']['tree_sha256']='0'*64
        with self.assertRaisesRegex(ImportFailure,'Aggregate digest'):self.run_check()
    def test_availability_totals_checked(self):
        self.state['totals']['unique_source_files']=2
        with self.assertRaisesRegex(ImportFailure,'total mismatch'):self.run_check()


if __name__=='__main__':unittest.main()
