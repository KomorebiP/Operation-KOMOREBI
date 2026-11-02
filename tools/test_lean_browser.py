import hashlib
import json
from pathlib import Path
import posixpath
import tempfile
from types import SimpleNamespace
import unittest

from lean_browser import BASE, PAGE, WORKSPACES, build, verify, verify_runtime, action
from prepare_lean_wasm import UPSTREAM, LEAN, MATHLIB, pack


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
        def write(path,text):
            p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
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
        (runtime/'SOURCE.json').write_text(json.dumps(dict(upstream=UPSTREAM,lean=LEAN,mathlib=MATHLIB,files=files,bytes=sum(f['size'] for f in files.values()))))
        return SimpleNamespace(site=site,lean_works={k:list(v.values()) for k,v in works.items()}),list(records.values()),runtime

    def test_receipt_bound_sources_and_local_execution_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);reader,records,runtime=self.fixture(out)
            self.assertEqual(build(reader,runtime)['workspaces'],3)
            self.assertEqual(verify(out,dict(files=records))['source_identity'],'PASS')
            data=json.loads((out/BASE/'examples.json').read_bytes())
            self.assertEqual(len(data['examples'][-1]['files']),2)

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


if __name__=='__main__':unittest.main()
