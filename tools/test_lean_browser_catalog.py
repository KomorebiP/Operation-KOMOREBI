import hashlib
import unittest
from lean_browser_catalog import plans,tactic_umbrella


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


if __name__=='__main__':unittest.main()
