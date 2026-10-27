#!/usr/bin/env python3
"""Small synthetic fixtures for the Block19 snapshot and comparison tools.

These deliberately fake fixture receipts are confined to TemporaryDirectory;
they test orchestration contracts, never serve as Lean execution evidence.
"""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def h(b):return hashlib.sha256(b).hexdigest()
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.project=self.root/'project';(self.project/'scripts').mkdir(parents=True)
        (self.project/'source.txt').write_text('exact source bytes\n')
        (self.project/'scripts/verify.py').write_text(
            'from pathlib import Path\nimport hashlib\nROOT=Path(__file__).resolve().parents[1]\n'
            'def source_pins():\n return {"source.txt":hashlib.sha256((ROOT/"source.txt").read_bytes()).hexdigest()}\n')
        self.tool=load('fixture_freeze19',ROOT/'release/build_scripts/freeze19.py')
        self.tool.ROOT=self.project
        self.old_argv=sys.argv
        sys.argv=['freeze19','--fresh',str(self.root/'fresh'),'--archive',str(self.root/'snapshot.zip'),
                  '--receipt',str(self.root/'snapshot.json')]
    def tearDown(self):sys.argv=self.old_argv;self.temp.cleanup()
    def run_freeze(self):
        with contextlib.redirect_stdout(io.StringIO()):self.tool.main()
    def test_exact_snapshot_and_extract(self):
        self.run_freeze()
        record=json.loads((self.root/'snapshot.json').read_text())
        self.assertEqual(record['status'],'PASS')
        self.assertEqual(record['source_count'],1)
        self.assertEqual((self.root/'fresh/source.txt').read_bytes(),(self.project/'source.txt').read_bytes())
        with zipfile.ZipFile(self.root/'snapshot.zip') as z:self.assertEqual(z.namelist(),['source.txt'])
    def test_existing_archive_refused(self):
        (self.root/'snapshot.zip').write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):self.run_freeze()
        self.assertEqual((self.root/'snapshot.zip').read_bytes(),b'preserve')
    def test_existing_receipt_refused(self):
        (self.root/'snapshot.json').write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):self.run_freeze()
    def test_nonempty_fresh_refused(self):
        (self.root/'fresh').mkdir();(self.root/'fresh/kept.txt').write_text('preserve')
        with self.assertRaises(FileExistsError):self.run_freeze()
        self.assertEqual((self.root/'fresh/kept.txt').read_text(),'preserve')
    def test_compiled_input_refused(self):
        (self.project/'source.olean').write_bytes(b'not a real object')
        p=self.project/'scripts/verify.py';p.write_text(p.read_text().replace('source.txt','source.olean'))
        with self.assertRaises(ValueError):self.run_freeze()

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.tool=load('fixture_compare19',ROOT/'scripts/compare_rebuild.py');self.tool.ROOT=self.root
        self.source=b'exact fixture input\n';(self.root/'MachineTheory.lean').write_bytes(self.source)
        dump(self.root/'MODULES.json',['MachineTheory'])
        self.keys=['lean_version','dependency_revisions','preserved_predecessor_files','authored_declaration_count',
             'authored_theorem_count','source_results_formalized','source_results_not_formalized','axiom_audited_declarations',
             'compiled_theorem_constants_including_generated','actual_axiom_union','negative_controls',
             'matched_upstream_artifacts','imported_module_count_including_audit_tools','per_command_timeout_seconds',
             'lean_internal_memory_limit_MiB','separate_OS_memory_cap','external_dependency_rebuild','runtime_adapter']
        for label in ['final','fresh']:
            base=self.root/label;(base/'objects').mkdir(parents=True)
            (base/'objects/MachineTheory.olean').write_bytes(b'fixture object')
            (base/'Audit.lean').write_bytes(b'fixture audit')
            report={k:'same fixture value' for k in self.keys}
            report.update(status='PASS',input_sha256_before={'MachineTheory.lean':h(self.source)},
                input_sha256_after={'MachineTheory.lean':h(self.source)},total_seconds=0.01,
                local_object_sha256={'MachineTheory.olean':h(b'fixture object')},
                steps=[{'name':'fixture','exit_code':0,'expected_success':True,'passed':True,'timed_out':False}])
            dump(base/'report.json',report)
            for name in ['source_inventory.json','environment_constants.json','axioms.json','dependency_artifacts.json',
                         'preservation.json','core24_exact.json','core25_exact.json','core32_exact.json','checker_import_preservation.json']:
                dump(base/name,{'synthetic_fixture':True})
        self.snapshot(self.source)
        self.old_argv=sys.argv
        sys.argv=['compare','--final',str(self.root/'final'),'--fresh',str(self.root/'fresh'),
                  '--snapshot',str(self.root/'source.zip'),'--out',str(self.root/'result.json')]
    def tearDown(self):sys.argv=self.old_argv;self.temp.cleanup()
    def snapshot(self,data,extra=None):
        with zipfile.ZipFile(self.root/'source.zip','w') as z:
            z.writestr('MachineTheory.lean',data)
            if extra:z.writestr(extra,b'extra')
    def run_compare(self):
        with contextlib.redirect_stdout(io.StringIO()):return self.tool.main()
    def test_identical_fixture_passes(self):self.assertEqual(self.run_compare(),0)
    def test_snapshot_changed_source_rejected(self):
        self.snapshot(b'changed')
        self.assertEqual(self.run_compare(),1)
        self.assertFalse(json.loads((self.root/'result.json').read_text())['comparisons']['snapshot_matches_primary_inputs'])
    def test_snapshot_extra_source_rejected(self):
        self.snapshot(self.source,'extra.lean');self.assertEqual(self.run_compare(),1)
    def test_snapshot_compiled_input_rejected(self):
        self.snapshot(self.source,'extra.olean');self.assertEqual(self.run_compare(),1)
    def test_production_object_change_rejected(self):
        (self.root/'fresh/objects/MachineTheory.olean').write_bytes(b'changed')
        self.assertEqual(self.run_compare(),1)

if __name__=='__main__':unittest.main()
