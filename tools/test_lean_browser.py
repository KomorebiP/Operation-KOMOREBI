import hashlib
import json
from pathlib import Path
import posixpath
import tempfile
from types import SimpleNamespace
import unittest
import zipfile

from lean_browser import BASE, PAGE, WORKSPACES, build, verify, verify_runtime, action
from prepare_lean_wasm import UPSTREAM, LEAN, MATHLIB, pack, mathlib_closure,mathlib_closures,mathlib_sources
from lean_workspaces import mathlib_seeds,mathlib_seed_groups
from lean_browser_imports import PAPER_I_PATH,PAPER_I_IMPORTS


class LeanBrowserTests(unittest.TestCase):
    def fixture(self,out):
        root=Path(__file__).resolve().parents[1];records={};works={}
        for _,_,work,files in WORKSPACES:
            for module,path in files:
                raw=(root/path).read_bytes()
                r=dict(repository_path=path,work=work,sha256=hashlib.sha256(raw).hexdigest(),
                       url='read/'+module+'.html',file_url='files/'+module+'.lean')
                records[path]=r
                dest=out/r['file_url'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
                works.setdefault(work,{})[path]=r
        raw=(root/PAPER_I_PATH).read_bytes()
        r=dict(repository_path=PAPER_I_PATH,work='paper-i',sha256=hashlib.sha256(raw).hexdigest(),
               url='read/paper-i/imports.html',file_url='files/paper-i-imports.lean')
        records[PAPER_I_PATH]=r;works.setdefault('paper-i',{})[PAPER_I_PATH]=r
        dest=out/r['file_url'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        def write(path,text):
            p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
        site=SimpleNamespace(root=root,output=out,revision='a'*40,search=[],
             rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),write=write,
             page=lambda path,title,body:write(path,body),read_source=lambda r:(root/r['repository_path']).read_bytes())
        runtime=out/'fixture-runtime';runtime.mkdir()
        files={}
        for name in ['lean-wasm/lean.js','lean-wasm/lean.wasm.gz','lean-wasm/core-layer.json',
                     'lean-lib/Lean-layer.json','lean-lib/Std-layer.json','lean-lib/Batteries-layer.json',
                     'lean-mathlib/real-analysis-layer.json']:
            raw=b'packaging test fixture';p=runtime/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(raw)
            files[name]=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        groups=mathlib_seed_groups(root)
        for key in groups:
            name='lean-mathlib/workspaces/'+key+'.json';p=runtime/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'{}')
            files[name]=dict(size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        (runtime/'SOURCE.json').write_text(json.dumps(dict(upstream=UPSTREAM,lean=LEAN,mathlib=MATHLIB,files=files,bytes=sum(f['size'] for f in files.values()),mathlib_modules=sorted(set(mathlib_seeds(root))|set(PAPER_I_IMPORTS)),workspace_modules=groups)))
        from lean_execution import identity
        catalog=dict(sources=[dict(id=identity(p),path=p,work=r['work'],label=r['work'],url=r['url']) for p,r in records.items()],
                     inputs={p:dict(sha256=r['sha256'],size=(root/p).stat().st_size,work=r['work']) for p,r in records.items()})
        bundle=out/'downloads/komorebi-lean-runner.zip';bundle.parent.mkdir()
        with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('CATALOG.json',json.dumps(catalog))
            for p in records:archive.writestr('inputs/'+p,(root/p).read_bytes())
        (out/'lean').mkdir(exist_ok=True)
        (out/'lean/run.json').write_text(json.dumps(dict(bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bundle_bytes=bundle.stat().st_size)))
        return SimpleNamespace(site=site,lean_works={k:list(v.values()) for k,v in works.items()}),list(records.values()),runtime

    def test_receipt_bound_sources_and_local_execution_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);reader,records,runtime=self.fixture(out)
            self.assertEqual(build(reader,runtime)['workspaces'],len(WORKSPACES))
            from check_reader_site import Page
            class WorkspacePage(Page):
                def __init__(self,text):
                    self.controls={};super().__init__(text)
                def handle_starttag(self,tag,attrs):
                    super().handle_starttag(tag,attrs)
                    values=dict(attrs)
                    for name in values:
                        if name.startswith('data-local-'):self.controls[name]=values
            page=WorkspacePage((out/PAGE).read_text(encoding='utf-8'))
            for control in page.inputs:
                self.assertTrue(control.get('id') in page.labels or control.get('aria-label'))
            self.assertTrue({'data-local-draft-status','data-local-result-note','data-local-diagnostics'}<=page.controls.keys())
            editor=page.controls['data-local-code']
            self.assertIn('readonly',editor)
            self.assertIn(editor['aria-describedby'],page.ids)
            self.assertEqual(page.controls['data-local-diagnostics']['aria-label'],'Go to a diagnostic in the source')
            self.assertEqual(verify(out,dict(files=records))['source_identity'],'PASS')
            data=json.loads((out/BASE/'examples.json').read_bytes())
            self.assertEqual(len(next(e for e in data['examples'] if e['id']=='proof-path-recovery')['files']),2)
            paper=next(e for e in data['examples'] if e['id']=='paper-i-projector-core')
            self.assertTrue(paper['files'][0]['generated'])
            self.assertEqual(paper['files'][0]['syntaxCheck'],'frontend')
            self.assertEqual(paper['import_profile']['original_path'],PAPER_I_PATH)
            self.assertIn('does not check the entire paper',(out/PAGE).read_text(encoding='utf8'))
            example_file=out/BASE/'examples.json'
            original=example_file.read_bytes()
            paper['files'][0]['text']+='\naxiom forged : False\n'
            example_file.write_text(json.dumps(data),encoding='utf8')
            with self.assertRaises(AssertionError):verify(out,dict(files=records))
            example_file.write_bytes(original)
            catalog=out/BASE/'catalog.json';value=json.loads(catalog.read_bytes())
            value['entries'][0]['library']=['Mathlib.Unrequested'];catalog.write_text(json.dumps(value))
            with self.assertRaises(AssertionError):verify(out,dict(files=records))

    def test_changed_runtime_and_source_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);reader,records,runtime=self.fixture(out)
            (runtime/'lean-wasm/lean.js').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'checksum'):verify_runtime(runtime)
            reader.lean_works['paper-x'][0]['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'identity'):build(reader,runtime)

    def test_packs_roundtrip_offsets_and_checksums(self):
        import gzip
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);inputs=[('A.olean',b'a'*20),('A.ir',b'b'*30)]
            manifest=pack(inputs,out,'test',dict(leanCommit=LEAN))
            result=[]
            for p in manifest['packs']:
                data=(out/p['file']).read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),p['sha256'])
                raw=gzip.decompress(data)
                result.extend((e['path'],raw[e['offset']:e['offset']+e['bytes']]) for e in p['entries'])
            self.assertEqual(result,inputs)

    def test_links_only_prepared_workspaces(self):
        site=SimpleNamespace(rel=lambda target,page:target)
        self.assertIn('paper-x-residual',action(site,'index.html',source=WORKSPACES[0][3][0][1]))
        self.assertEqual(action(site,'index.html',source='unsupported.lean'),'')
        self.assertIn('?file=',action(site,'index.html',source='retained.lean',retained=True))

    def test_remote_assets_must_use_the_pinned_public_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            _,_,runtime=self.fixture(Path(tmp))
            path=runtime/'SOURCE.json';data=json.loads(path.read_bytes())
            record=data['files'].pop('lean-wasm/lean.js')
            record['url']='https://raw.githubusercontent.com/live-codes/browser-lean/'+UPSTREAM+'/public/lean-wasm/lean.js'
            data['remote_files']={'lean-wasm/lean.js':record};path.write_text(json.dumps(data))
            verify_runtime(runtime)
            record['url']='https://example.com/unpinned.js';path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Unpinned'):verify_runtime(runtime)

    def test_workspace_imports_cannot_outgrow_the_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);reader,_,runtime=self.fixture(out)
            path=runtime/'SOURCE.json';data=json.loads(path.read_bytes());data['mathlib_modules']=[]
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Missing browser Mathlib imports'):build(reader,runtime)
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);reader,_,runtime=self.fixture(out)
            path=runtime/'SOURCE.json';data=json.loads(path.read_bytes())
            data['files'].pop('lean-mathlib/workspaces/proof-path-compression.json')
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Missing workspace Mathlib imports'):build(reader,runtime)
        from unittest.mock import patch
        from lean_workspaces import RECOVERY
        with patch('lean_workspaces.WORKSPACES',[('broken','Broken','proof-path-theory',[('ProofPath.Recovery',RECOVERY)])]):
            with self.assertRaisesRegex(ValueError,'must precede'):mathlib_seeds(Path(__file__).resolve().parents[1])

    def test_mathlib_archive_closure_follows_public_imports_and_ignores_comments(self):
        import io,tarfile
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'sources.tar.gz'
            with tarfile.open(path,'w:gz') as archive:
                for name,text in [('A','public import Mathlib.B\n-- import Mathlib.Missing\n'),('B','import Lean\n')]:
                    raw=text.encode();entry=tarfile.TarInfo('snapshot/Mathlib/'+name+'.lean');entry.size=len(raw)
                    archive.addfile(entry,io.BytesIO(raw))
            self.assertEqual(mathlib_closure(path,['Mathlib.A']),{'Mathlib.A','Mathlib.B','Lean'})
            self.assertEqual(mathlib_closures(path,{'small':['Mathlib.B'],'larger':['Mathlib.A']}),
                             {'small':{'Mathlib.B','Lean'},'larger':{'Mathlib.A','Mathlib.B','Lean'}})
            with self.assertRaisesRegex(ValueError,'archive checksum'):
                mathlib_sources(path,'0'*64)


if __name__=='__main__':unittest.main()
