import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from reader_source_additions import extend_owned, CONFIG
from lean_reader import selected_paths, local_imports

ROOT=Path(__file__).resolve().parents[1]


class ReaderSourceAdditionsTests(unittest.TestCase):
    def fixture(self,root):
        raw=b'import Mathlib\ntheorem retained : True := by trivial\n'
        path='book/lean/New.lean';file=root/path;file.parent.mkdir(parents=True);file.write_bytes(raw)
        record='book/formalization/SOURCE_MANIFEST.json';file=root/record;file.parent.mkdir(parents=True)
        file.write_text(json.dumps(dict(schema=1,files=[dict(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())])),encoding='utf-8')
        config=dict(schema=1,sources=[dict(work='work',record='formalization/SOURCE_MANIFEST.json',record_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),paths=['lean/New.lean'])])
        file=root/CONFIG;file.parent.mkdir(parents=True);file.write_text(json.dumps(config),encoding='utf-8')
        return dict(components=[dict(id='work',destination='book')]),config,path

    def test_source_and_publication_tampering_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);registry,config,path=self.fixture(root);owned={}
            added=extend_owned(root,registry,owned)
            self.assertEqual(owned[path]['sha256'],hashlib.sha256((root/path).read_bytes()).hexdigest())
            self.assertEqual(owned[path]['source_record'],'book/formalization/SOURCE_MANIFEST.json')
            original=(root/path).read_bytes()
            (root/path).write_bytes(b'theorem changed : False := by sorry\n')
            with self.assertRaisesRegex(ValueError,'publication source changed'):extend_owned(root,registry,{})
            (root/path).write_bytes(original)
            (root/'book/formalization/SOURCE_MANIFEST.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'publication record changed'):extend_owned(root,registry,{})

    def test_unbound_unsafe_and_duplicate_selections_are_rejected(self):
        for paths in [['../outside.lean'],['lean/Unrecorded.lean'],['lean/New.lean','lean/New.lean']]:
            with self.subTest(paths=paths),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);registry,config,_=self.fixture(root)
                config['sources'][0]['paths']=paths;(root/CONFIG).write_text(json.dumps(config),encoding='utf-8')
                with self.assertRaises(ValueError):extend_owned(root,registry,{})

    def test_original_imports_are_preserved_and_conflicts_do_not_mutate_them(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);registry,_,path=self.fixture(root)
            original=extend_owned(root,registry,{})[path];original.pop('source_record');original.pop('source_record_sha256')
            owned={path:copy.deepcopy(original)};extend_owned(root,registry,owned)
            self.assertEqual(owned[path],original)
            conflict=copy.deepcopy(original);conflict['sha256']='0'*64
            owned={path:conflict};before=copy.deepcopy(owned)
            with self.assertRaisesRegex(ValueError,'original import'):extend_owned(root,registry,owned)
            self.assertEqual(owned,before)

    def test_current_production_modules_and_registers_are_available(self):
        registry=json.loads((ROOT/'manifests/browse-resources.json').read_bytes());owned={}
        for c in registry['components']:
            if c['id'] not in {'monographs-special-functions','realization-boundaries'}:continue
            receipt=json.loads((ROOT/('manifests/source-imports/'+c['id']+'.json')).read_bytes())
            owned.update({c['destination']+'/'+f['path']:{**f,'work':c['id']} for f in receipt['files']})
        extend_owned(ROOT,registry,owned)
        for work,count in [('monographs-special-functions',77),('realization-boundaries',67)]:
            component=next(c for c in registry['components'] if c['id']==work)
            self.assertEqual(len(list(selected_paths(component,owned))),count)
        total=0
        for n in range(1,21):
            base='monographs/special-functions/';path=base+f'formalization/Block{n:02d}/declarations.json'
            record=json.loads((ROOT/path).read_bytes());total+=record['count']
            self.assertIn(base+record['source'],owned)
            self.assertEqual(owned[base+record['source']]['sha256'],record['sha256'])
        self.assertEqual(total,497)

    def test_local_import_links_are_exact_and_malformed_inputs_stay_inspectable(self):
        rows=[dict(work='work',repository_path='book/Root.lean',url='read/root.html'),
              dict(work='work',repository_path='book/Example/Base.lean',url='read/base.html')]
        reader=SimpleNamespace(lean_works={'work':rows},site=SimpleNamespace(rel=lambda target,page:target))
        markup=local_imports(reader,rows[0],'/- import Hidden -/\nimport Example.Base\nimport Missing\n','read/root.html')
        self.assertIn('href="read/base.html"',markup)
        self.assertIn('Local imports (1)',markup)
        self.assertNotIn('Missing</code>',markup)
        self.assertEqual(local_imports(reader,rows[0],'import Bad/Path\n','read/root.html'),'')


if __name__=='__main__':unittest.main()
