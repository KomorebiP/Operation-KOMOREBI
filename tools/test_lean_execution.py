import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from lean_runner import Collection, digest, diagnostics, execute, imports, prepare, safe_path, validate_workspace
from lean_execution import identity, verify


class LeanExecutionTests(unittest.TestCase):
    def fixture(self, extras=None, native=False):
        raws={'book/current/Selected.lean':b'import Example.Base\nexample : True := Example.proof\n',
              'book/current/Example/Base.lean':b'namespace Example\ntheorem proof : True := True.intro\nend Example\n'}
        raws.update(extras or {})
        if native:
            raws.update({'book/current/lean-toolchain':b'leanprover/lean4:v4.34.0-rc2\n',
                         'book/current/lakefile.toml':b'name = "Example"\n',
                         'book/current/lake-manifest.json':b'{"packages":[]}\n'})
        source='book/current/Selected.lean'
        catalog=dict(source_revision='a'*40,inputs={p:dict(work='paper',sha256=digest(raw)) for p,raw in raws.items()},
            sources=[dict(path=source,sha256=digest(raws[source]),work='paper',project='book/current' if native else None)],
            projects={'book/current':dict(files=list(raws),toolchain='leanprover/lean4:v4.34.0-rc2')} if native else {},
            fallback=dict(toolchain='leanprover/lean4:v4.34.0-rc2',mathlib='b'*40,lock={'packages':[]}))
        return Collection(catalog,lambda path:raws[path]),source,raws

    def test_local_imports_use_the_nearest_edition_and_preserve_every_byte(self):
        collection,source,raws=self.fixture({'book/history/Example/Base.lean':b'this historical edition is different'})
        plan=collection.plan(source)
        self.assertEqual(plan['files']['Example/Base.lean'],'book/current/Example/Base.lean')
        self.assertEqual(plan['mode'],'reconstructed-workspace')
        with tempfile.TemporaryDirectory() as temp:
            output=prepare(collection,source,Path(temp)/'run')
            record=json.loads((output/'RUN_INPUTS.json').read_bytes())
            self.assertEqual((output/'project/SelectedProof.lean').read_bytes(),raws[source])
            self.assertEqual((output/'project/Example/Base.lean').read_bytes(),raws['book/current/Example/Base.lean'])
            self.assertTrue(record['inputs']['lakefile.toml']['generated'])
            validate_workspace(output,record)
            (output/'project/Example/Base.lean').write_text('changed')
            with self.assertRaises(ValueError):validate_workspace(output,record)

    def test_retained_project_configuration_is_not_reconstructed(self):
        collection,source,raws=self.fixture({'book/current/helper.sh':b'#!/bin/sh\nexit 0\n'},native=True)
        collection.inputs['book/current/helper.sh']['mode']='100755'
        with tempfile.TemporaryDirectory() as temp:
            output=prepare(collection,source,Path(temp)/'run')
            record=json.loads((output/'RUN_INPUTS.json').read_bytes())
            self.assertEqual(record['mode'],'retained-project')
            self.assertEqual(record['target'],'Selected.lean')
            self.assertFalse(any(entry['generated'] for entry in record['inputs'].values()))
            for path,raw in raws.items():self.assertEqual((output/'project'/path.removeprefix('book/current/')).read_bytes(),raw)
            if os.name!='nt':self.assertEqual((output/'project/helper.sh').stat().st_mode&0o777,0o755)
            with self.assertRaises(FileExistsError):prepare(collection,source,output)

    def test_missing_and_ambiguous_imports_stop_preparation(self):
        collection,source,raws=self.fixture()
        collection.by_name.clear()
        self.assertIn('Missing local import',collection.plan(source)['issues'][0])
        collection,source,raws=self.fixture({'book/one/Example/Base.lean':b'one', 'book/two/Example/Base.lean':b'two'})
        collection.by_name[('paper','Base.lean')].remove('book/current/Example/Base.lean')
        self.assertIn('Ambiguous local import',collection.plan(source)['issues'][0])
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'must-not-exist'
            with self.assertRaises(ValueError):prepare(collection,source,target)
            self.assertFalse(target.exists())

    def test_import_routing_ignores_nested_comments_strings_and_handles_public_imports(self):
        text='''/- import Wrong.A /- import Wrong.B -/ still comment -/
public import Mathlib.Data.Nat.Basic -- import Wrong.C
import all Example.One
import Example.One Example.Two
def text := "import Wrong.D"
'''
        self.assertEqual(imports(text),['Mathlib.Data.Nat.Basic','Example.One','Example.Two'])
        with self.assertRaises(ValueError):imports('import Bad/Path\n')

    def test_identical_leaf_copies_are_equivalent_but_different_editions_are_not(self):
        raw=b'import Mathlib\nnamespace Example\nend Example\n'
        collection,source,_=self.fixture({'book/one/Example/Base.lean':raw,'book/two/Example/Base.lean':raw})
        collection.by_name[('paper','Base.lean')].remove('book/current/Example/Base.lean')
        self.assertEqual(collection.plan(source)['issues'],[])

    def test_setup_failure_cannot_be_reported_as_a_checked_file(self):
        collection,source,_=self.fixture()
        with tempfile.TemporaryDirectory() as temp:
            output=prepare(collection,source,Path(temp)/'run')
            with patch('lean_runner.subprocess.Popen',side_effect=FileNotFoundError('lake unavailable')):
                result=execute(output,timeout=1)
            self.assertEqual(result['status'],'setup_failed')
            self.assertIsNone(result['compiler_exit_code'])
            self.assertEqual([s['name'] for s in result['steps']],['version'])
            self.assertTrue((output/'RESULT.json').is_file())
            self.assertIn('lake unavailable',(output/'version.stderr.log').read_text())

    def test_only_selected_sources_are_accepted_and_paths_cannot_escape(self):
        collection,source,raws=self.fixture()
        with self.assertRaises(ValueError):collection.plan('book/current/Example/Base.lean')
        for path in ('../escape.lean','/absolute.lean','a/../escape.lean','C:/a.lean','a\\b.lean','a\n.lean'):
            with self.subTest(path=path),self.assertRaises(ValueError):safe_path(path)
        raws[source]+=b'-- modified\n'
        with self.assertRaises(ValueError):collection.read(source)

    def test_compiler_diagnostics_are_taken_from_lean_json_not_source_text(self):
        messages=diagnostics('build progress\n{"severity":"warning","data":"declaration uses sorry"}\nnot json\n{"severity":"error","data":"unsolved goals"}\n')
        self.assertEqual([m['severity'] for m in messages],['warning','error'])

    def test_web_server_export_keeps_the_selected_source_and_builds_imports_only(self):
        collection,source,raws=self.fixture()
        with tempfile.TemporaryDirectory() as temp:
            output=prepare(collection,source,Path(temp)/'run','KomorebiExample')
            self.assertEqual((output/'project/KomorebiExample.lean').read_bytes(),raws[source])
            config=json.loads((output/'project/leanweb-config.json').read_bytes())
            self.assertFalse(config['default'])
            self.assertEqual(config['examples'][0]['file'],'KomorebiExample.lean')
            self.assertIn('lake setup-file KomorebiExample.lean',(output/'project/leanweb-build.sh').read_text())
            record=json.loads((output/'RUN_INPUTS.json').read_bytes());validate_workspace(output,record)
            self.assertEqual(record['target'],'KomorebiExample.lean')
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):prepare(collection,source,Path(temp)/'run','bad-name;command')

    def test_publication_scope_is_the_displayed_lean_catalogue_not_unrelated_documents(self):
        source='paper/Main.lean';raw=b'example : True := True.intro\n';sha=digest(raw)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'lean').mkdir();(root/'downloads').mkdir()
            (root/'lean/index.json').write_text(json.dumps({'works':[{'files':[{'path':source}]}]}))
            archive=root/'downloads/komorebi-lean-runner.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('CATALOG.json',json.dumps({'source_revision':'a'*40,'inputs':{source:{'sha256':sha}}}))
                z.writestr('inputs/'+source,raw)
            data=dict(source_revision='a'*40,bundle_sha256=digest(archive.read_bytes()),source_files=1,
                      files=[dict(path=source,id=identity(source),sha256=sha)],build_runs_lean=False)
            (root/'lean/run.json').write_text(json.dumps(data))
            documents={'files':[dict(repository_path=source,sha256=sha),
                                dict(repository_path='unrelated/Other.lean',sha256='b'*64)]}
            self.assertEqual(verify(root,documents)['files'],1)
            documents['files']=documents['files'][1:]
            with self.assertRaises(AssertionError):verify(root,documents)


if __name__=='__main__':unittest.main()
