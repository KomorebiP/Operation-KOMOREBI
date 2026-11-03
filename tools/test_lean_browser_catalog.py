import hashlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from lean_browser_catalog import plans,tactic_umbrella,runtime_library
from prepare_lean_wasm import MATHLIB,MATHLIB_SOURCE_SHA256,source_library,validate_source_library


class CatalogTests(unittest.TestCase):
    def fixture(self):
        raws={'paper/lean/Demo/Main.lean':b'import Demo.Helper\nimport Mathlib.Tactic\nexample : value = 1 := rfl\n',
              'paper/lean/Demo/Helper.lean':b'import Std\ndef value : Nat := 1\n',
              'other/lean/Demo/Helper.lean':b'import Std\ndef value : Nat := 2\n'}
        catalog=dict(sources=[dict(id='main',path='paper/lean/Demo/Main.lean',work='paper',label='Paper',url='read/main.html')],
                     inputs={p:dict(work=p.split('/')[0],sha256=hashlib.sha256(raw).hexdigest(),size=len(raw)) for p,raw in raws.items()})
        return catalog,raws

    def test_dependencies_stay_in_the_selected_edition_and_precede_the_main_file(self):
        catalog,raws=self.fixture();entries,inputs=plans(catalog,raws.__getitem__,{'Mathlib.Tactic.Ring'})
        entry=entries[0]
        self.assertEqual([f['path'] for f in entry['files']],['paper/lean/Demo/Helper.lean','paper/lean/Demo/Main.lean'])
        self.assertEqual(entry['files'][0]['module'],'Demo.Helper')
        self.assertTrue(entry['tactics']);self.assertEqual(entry['issues'],[])
        self.assertNotIn('other/lean/Demo/Helper.lean',inputs)

    def test_unavailable_imports_cycles_and_changed_bytes_are_not_ready_routes(self):
        for replacement in (b'import Mathlib.Unavailable\n',b'import Demo.Main\n',b'changed source'):
            catalog,raws=self.fixture();path='paper/lean/Demo/Helper.lean';raws[path]=replacement
            if replacement!=b'changed source':catalog['inputs'][path].update(sha256=hashlib.sha256(replacement).hexdigest(),size=len(replacement))
            entries,_=plans(catalog,raws.__getitem__,set())
            self.assertTrue(entries[0]['issues'])

    def test_tactic_compatibility_contains_only_available_imports(self):
        source=tactic_umbrella({'Mathlib.Tactic.Ring','Mathlib.Tactic.Ring.Basic','Mathlib.Data.Set.Basic'})
        self.assertEqual([line for line in source.splitlines() if line.startswith('import ')],['import Mathlib.Tactic.Ring'])
        self.assertNotIn('axiom ',source);self.assertNotIn('theorem ',source)

    def library(self):
        members={'Mathlib/Tactic/Pilot.lean':b'public import Mathlib.Pilot.Helper\n',
                 'Mathlib/Pilot/Helper.lean':b'import Std\r\n-- exact original bytes\r\n',
                 'Mathlib/Pilot/Unused.lean':b'import Std\n'}
        available={'Std','Mathlib.Tactic.Ring'}
        sources=source_library(members,available,['Mathlib.Tactic.Pilot','Mathlib.Pilot.Helper','Mathlib.Pilot.Unused'])
        return members,available,sources

    def test_library_fallback_follows_only_needed_exact_sources_before_the_retained_files(self):
        catalog,raws=self.fixture();path='paper/lean/Demo/Helper.lean'
        raws[path]=b'import Mathlib.Tactic.Pilot\ndef value : Nat := 1\n'
        catalog['inputs'][path].update(size=len(raws[path]),sha256=hashlib.sha256(raws[path]).hexdigest())
        members,available,sources=self.library()
        entries,_=plans(catalog,raws.__getitem__,available,sources)
        self.assertEqual(entries[0]['library'],['Mathlib.Pilot.Helper','Mathlib.Tactic.Pilot'])
        self.assertEqual(entries[0]['issues'],[])
        self.assertNotIn('Mathlib.Tactic.Pilot',tactic_umbrella(available))
        self.assertEqual(sources['Mathlib.Pilot.Helper']['source'].encode(),members['Mathlib/Pilot/Helper.lean'])
        entries,_=plans(catalog,raws.__getitem__,available)
        self.assertIn('Unavailable browser import: Mathlib.Tactic.Pilot',entries[0]['issues'])

    def test_library_fallback_rejects_changed_bytes_provenance_and_open_import_closures(self):
        _,available,sources=self.library()
        for field,value in [('source','changed'),('size',0),('revision','0'*40),('url','https://example.com/source'),('imports',[])]:
            bad=copy.deepcopy(sources);bad['Mathlib.Tactic.Pilot'][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'identity|imports changed'):
                validate_source_library(bad,available)
        bad=copy.deepcopy(sources);del bad['Mathlib.Pilot.Helper']
        with self.assertRaisesRegex(ValueError,'Unavailable.*Mathlib.Pilot.Helper'):validate_source_library(bad,available)
        with self.assertRaisesRegex(ValueError,'shadowed'):validate_source_library(sources,available|{'Mathlib.Tactic.Pilot'})
        with self.assertRaisesRegex(ValueError,'cycle'):
            source_library({'Mathlib/A.lean':b'import Mathlib.B\n','Mathlib/B.lean':b'import Mathlib.A\n'},available,['Mathlib.A','Mathlib.B'])

    def test_library_runtime_record_binds_exact_local_assets_and_pinned_archive(self):
        _,available,sources=self.library()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);files={}
            for record in sources.values():
                path=root/record['asset'];path.parent.mkdir(parents=True,exist_ok=True);raw=record['source'].encode();path.write_bytes(raw)
                files[record['asset']]=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            runtime=dict(mathlib=MATHLIB,mathlib_source_sha256=MATHLIB_SOURCE_SHA256,
                         mathlib_modules=sorted(available),mathlib_source_modules=sources,files=files)
            self.assertEqual(runtime_library(root,runtime),(sources,available))
            runtime['mathlib_source_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'Unpinned'):runtime_library(root,runtime)
            runtime['mathlib_source_sha256']=MATHLIB_SOURCE_SHA256
            (root/sources['Mathlib.Pilot.Helper']['asset']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'asset mismatch'):runtime_library(root,runtime)


if __name__=='__main__':unittest.main()
