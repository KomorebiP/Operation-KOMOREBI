"""Focused tests for receipt-derived availability and preserved history."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import import_source_collection as importer
import update_source_navigation as nav


class NavigationTests(unittest.TestCase):
    def make_component(self, root, identifier, destination, name, data):
        relative=destination+'/'+name
        path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        row={'path':name,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'mode':'100644',
             'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()}
        component={'id':identifier,'destination':destination,'source':{'kind':'blob-tar','sha256':'0'*64,'size':1,'chunks':[]},
                   'expected':{'file_count':1,'tree_sha256':importer.tree_digest([row])}}
        receipt={'schema':1,'component':identifier,'destination':destination,'file_count':1,
                 'tree_sha256':importer.tree_digest([row]),'files':[row],'source':component['source'],
                 'component_sha256':importer._fingerprint(component)}
        receipt_path=root/'manifests/source-imports'/f'{identifier}.json'
        receipt_path.parent.mkdir(parents=True,exist_ok=True);receipt_path.write_text(json.dumps(receipt))
        return component

    def test_missing_receipt_is_not_available_and_added_primary_is_dynamic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            component=self.make_component(root,'new-primary','research/new-primary','paper.tex',b'body')
            (root/'manifests/source-imports/new-primary.json').unlink()
            state=nav.read_state(root,{'components':[component]}, {}, '2026-10-27')
            self.assertEqual(state['totals']['selected_primary_components'],1)
            self.assertEqual(state['totals']['available_components'],0)
            self.assertEqual(state['components'][0]['disposition'],'selected_source_pending_import')

    def test_nested_ownership_and_modified_source_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            parent=self.make_component(root,'parent','monographs/parent','paper.tex',b'parent')
            child=self.make_component(root,'parent-supporting-sources','monographs/parent/supporting-sources','old.tex',b'child')
            config={'components':[parent,child]}
            state=nav.read_state(root,config,{},'2026-10-27')
            self.assertEqual(state['totals']['unique_source_files'],2)
            self.assertEqual(state['totals']['available_primary_components'],1)
            self.assertEqual(state['totals']['available_supporting_components'],1)
            (root/'monographs/parent/paper.tex').write_bytes(b'changed')
            with self.assertRaises(importer.ImportFailure):nav.read_state(root,config,{},'2026-10-27')

    def test_historical_rows_and_existing_import_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'manifests').mkdir()
            old={'schema_version':1,'as_of':'2026-10-09','contributions':[
                {'id':'H-1','record_kind':'historical_contribution','title':'Historical result','disposition':'awaiting_source_reconciliation'},
                {'id':'KOM-PAPER-I','record_kind':'current_candidate','title':'Old Paper I','disposition':'imported','local_path':'papers/paper-i'}]}
            (root/'manifests/contributions.json').write_text(json.dumps(old))
            state={'as_of':'2026-10-27','totals':{},'components':[{'id':'paper-i','role':'primary','available':False}]}
            ledger,_=nav.current_ledger(root,state)
            self.assertEqual(ledger['contributions'][0],old['contributions'][0])
            self.assertEqual(ledger['contributions'][1]['local_path'],'papers/paper-i')
            self.assertEqual(ledger['contributions'][1]['disposition'],'imported')

    def test_relocated_history_links(self):
        text='[paper](../papers/paper-i/) [web](https://example.com/a)'
        got=nav.relocate_links(text,'docs/GITHUB_IMPORT_STATUS.md','docs/history/GITHUB_IMPORT_STATUS_2026-10-07.md')
        self.assertEqual(got,'[paper](../../papers/paper-i/) [web](https://example.com/a)')

if __name__=='__main__':unittest.main()
