import json
from pathlib import Path
import tempfile
import unittest

from lean_download_plan import download_plan


class DownloadPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.record=dict(files={},remote_files={})
        self.add('lean-wasm/lean.js',10,remote=True)
        self.add('lean-wasm/lean.wasm.gz',20,remote=True)
        self.add('lean-wasm/core-lib/core.pack',30,remote=True)
        self.add('shared/base.pack',40,remote=True)
        self.add('loose/Batteries/A.olean.gz',50,remote=True)
        self.add('lean-mathlib/modules/pilot.pack',60)
        self.write('lean-wasm/core-layer.json',{'packs':[{'file':'core.pack'}]})
        for root in ['Lean','Std','Batteries']:
            self.write('lean-lib/'+root+'-layer.json',{'packs':[{'file':'../shared/base.pack'}],
                'loose':[{'file':'../loose/Batteries/A.olean.gz'}]})
        self.write('lean-mathlib/workspaces/pilot.json',{'packs':[{'file':'modules/pilot.pack'},{'file':'../shared/base.pack'}]})
        (self.root/'SOURCE.json').write_bytes(b'{}')

    def add(self,name,size,remote=False):
        self.record['remote_files' if remote else 'files'][name]={'size':size}

    def write(self,name,value):
        raw=json.dumps(value).encode();path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        self.add(name,len(raw))

    def test_paths_follow_worker_pack_base_and_deduplicate_shared_and_loose_assets(self):
        plan=download_plan(self.root,self.record,'workspaces/pilot.json')
        expected={'lean-wasm/lean.js','lean-wasm/lean.wasm.gz','lean-wasm/core-layer.json','lean-wasm/core-lib/core.pack',
                  'lean-lib/Lean-layer.json','lean-lib/Std-layer.json','lean-lib/Batteries-layer.json','shared/base.pack',
                  'loose/Batteries/A.olean.gz','lean-mathlib/workspaces/pilot.json','lean-mathlib/modules/pilot.pack'}
        records={**self.record['remote_files'],**self.record['files']}
        self.assertEqual(plan,{'files':len(expected)+1,'bytes':sum(records[name]['size'] for name in expected)+2})

    def test_no_mathlib_plan_omits_that_manifest_and_its_exclusive_packs(self):
        with_mathlib=download_plan(self.root,self.record,'workspaces/pilot.json')
        without=download_plan(self.root,self.record)
        self.assertEqual(with_mathlib['files']-without['files'],2)
        self.assertEqual(with_mathlib['bytes']-without['bytes'],60+self.record['files']['lean-mathlib/workspaces/pilot.json']['size'])

    def test_unrecorded_asset_fails_instead_of_understating_the_plan(self):
        del self.record['files']['lean-mathlib/modules/pilot.pack']
        with self.assertRaisesRegex(ValueError,'unrecorded assets'):
            download_plan(self.root,self.record,'workspaces/pilot.json')

    def test_engine_escape_path_rejected(self):
        self.write('lean-lib/Lean-layer.json',{'packs':[{'file':'../../../escape.pack'}]})
        with self.assertRaisesRegex(ValueError,'relative source path'):download_plan(self.root,self.record)

    def test_local_asset_record_has_same_priority_as_service_worker(self):
        self.record['remote_files']['lean-mathlib/modules/pilot.pack']={'size':999999}
        original=download_plan(self.root,self.record,'workspaces/pilot.json')
        self.record['remote_files']['lean-mathlib/modules/pilot.pack']['size']=1
        self.assertEqual(download_plan(self.root,self.record,'workspaces/pilot.json'),original)


if __name__=='__main__':unittest.main()
