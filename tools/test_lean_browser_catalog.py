import hashlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from lean_browser_catalog import plans,tactic_umbrella,runtime_library,validate_order,verify as verify_catalog
from prepare_lean_wasm import MATHLIB,MATHLIB_SOURCE_SHA256,SOURCE_MODULES,source_library,validate_source_library


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
        self.assertEqual(entry['order'],[{'file':0},{'file':1}])
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
        self.assertEqual(entries[0]['order'],[{'library':'Mathlib.Pilot.Helper'},{'library':'Mathlib.Tactic.Pilot'},{'file':0},{'file':1}])
        self.assertEqual(entries[0]['issues'],[])
        self.assertNotIn('Mathlib.Tactic.Pilot',tactic_umbrella(available))
        self.assertEqual(sources['Mathlib.Pilot.Helper']['source'].encode(),members['Mathlib/Pilot/Helper.lean'])
        entries,_=plans(catalog,raws.__getitem__,available)
        self.assertIn('Unavailable browser import: Mathlib.Tactic.Pilot',entries[0]['issues'])

    def test_library_fallbacks_wait_for_the_first_retained_importer(self):
        catalog,raws=self.fixture();path='paper/lean/Demo/Main.lean'
        raws[path]=b'import Demo.Helper\nimport Mathlib.Tactic.Pilot\nexample : value = 1 := rfl\n'
        catalog['inputs'][path].update(size=len(raws[path]),sha256=hashlib.sha256(raws[path]).hexdigest())
        _,available,sources=self.library();entries,_=plans(catalog,raws.__getitem__,available,sources)
        self.assertEqual(entries[0]['order'],[{'file':0},{'library':'Mathlib.Pilot.Helper'},{'library':'Mathlib.Tactic.Pilot'},{'file':1}])
        # A second importer uses the same checked module, rather than executing
        # its source and any commands with effects a second time.
        helper='paper/lean/Demo/Helper.lean';raws[helper]=b'import Mathlib.Tactic.Pilot\ndef value : Nat := 1\n'
        catalog['inputs'][helper].update(size=len(raws[helper]),sha256=hashlib.sha256(raws[helper]).hexdigest())
        entries,_=plans(catalog,raws.__getitem__,available,sources)
        self.assertEqual(entries[0]['order'],[{'library':'Mathlib.Pilot.Helper'},{'library':'Mathlib.Tactic.Pilot'},{'file':0},{'file':1}])

    def test_source_order_rejects_skipped_repeated_invalid_or_unselected_final_steps(self):
        entry=dict(files=[{},{}],library=['Mathlib.Pilot.Helper'],order=[{'file':0},{'library':'Mathlib.Pilot.Helper'},{'file':1}])
        validate_order(entry)
        invalid=[[],[{'file':0},{'file':1}],entry['order']+[{'file':1}],
                 [{'file':0},{'library':'Mathlib.Pilot.Helper'},{'file':2}],
                 [{'file':False},{'library':'Mathlib.Pilot.Helper'},{'file':1}],
                 [{'file':0},{'library':'Mathlib.Missing'},{'file':1}],
                 [{'file':0},{'file':1},{'library':'Mathlib.Pilot.Helper'}],
                 [{'file':0,'library':'Mathlib.Pilot.Helper'},{'file':1}],
                 [{'file':0},{'other':0},{'library':'Mathlib.Pilot.Helper'},{'file':1}]]
        for order in invalid:
            with self.subTest(order=order),self.assertRaisesRegex(ValueError,'source order'):
                validate_order({**entry,'order':order})

    def test_catalogue_verification_binds_order_and_module_names_to_the_receipt_graph(self):
        from test_lean_browser import LeanBrowserTests
        from lean_browser import build
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);reader,records,runtime=LeanBrowserTests().fixture(root)
            build(reader,runtime);documents=dict(files=records);verify_catalog(root,documents)
            path=root/'lean/browser/catalog.json';catalog=json.loads(path.read_bytes())
            entry=next(e for e in catalog['entries'] if len(e['files'])>1)
            original=entry['files'][0]['module'];entry['files'][0]['module']='Changed.Module'
            path.write_text(json.dumps(catalog))
            with self.assertRaises(AssertionError):verify_catalog(root,documents)
            entry['files'][0]['module']=original;entry['order']=list(reversed(entry['order']))
            path.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError,'selected file is not last'):verify_catalog(root,documents)

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

    def test_finset_fallback_requires_the_evolving_frontend_and_preserves_import_plans(self):
        module='Mathlib.Tactic.Positivity.Finset';available={'Std'}
        self.assertIn(module,SOURCE_MODULES)
        sources=source_library({module.replace('.','/')+'.lean':b'import Std\n'},available,[module])
        self.assertEqual(sources[module]['syntaxCheck'],'frontend')
        catalog,raws=self.fixture();path='paper/lean/Demo/Helper.lean'
        raws[path]=('import '+module+'\ndef value : Nat := 1\n').encode()
        catalog['inputs'][path].update(size=len(raws[path]),sha256=hashlib.sha256(raws[path]).hexdigest())
        entries,_=plans(catalog,raws.__getitem__,available,sources)
        self.assertEqual(entries[0]['library'],[module])
        self.assertEqual(entries[0]['issues'],[])
        for value in (None,'full','unknown'):
            bad=copy.deepcopy(sources)
            if value is None:del bad[module]['syntaxCheck']
            else:bad[module]['syntaxCheck']=value
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'syntax-check requirement'):
                validate_source_library(bad,available)
        _,available,ordinary=self.library();ordinary['Mathlib.Tactic.Pilot']['syntaxCheck']='frontend'
        with self.assertRaisesRegex(ValueError,'syntax-check requirement'):
            validate_source_library(ordinary,available)

    def test_positivity_umbrella_orders_its_required_frontend_dependency_first(self):
        finset='Mathlib.Tactic.Positivity.Finset';umbrella='Mathlib.Tactic.Positivity'
        self.assertIn(umbrella,SOURCE_MODULES)
        members={finset.replace('.','/')+'.lean':b'import Std\n',
                 umbrella.replace('.','/')+'.lean':('public import '+finset+'\n').encode()}
        sources=source_library(members,{'Std'},[finset,umbrella])
        catalog,raws=self.fixture();path='paper/lean/Demo/Helper.lean'
        raws[path]=('import '+umbrella+'\ndef value : Nat := 1\n').encode()
        catalog['inputs'][path].update(size=len(raws[path]),sha256=hashlib.sha256(raws[path]).hexdigest())
        entries,_=plans(catalog,raws.__getitem__,{'Std'},sources)
        self.assertEqual(entries[0]['library'],[finset,umbrella])
        self.assertEqual(entries[0]['issues'],[])
        self.assertEqual(sources[entries[0]['library'][0]]['syntaxCheck'],'frontend')
        self.assertNotIn('syntaxCheck',sources[umbrella])
        self.assertNotIn(umbrella,tactic_umbrella({'Mathlib.Tactic.Ring'}))

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
