#!/usr/bin/env python3
"""Freshly compile and kernel-check new113 modules over pinned110/111/112 objects."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import zipfile

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def without_comments(source):
    # Lean block comments nest. Preserve newlines and string literals so a
    # prose line beginning with 'theorem' cannot be mistaken for a declaration.
    out=[]; i=0; depth=0; string=False
    while i<len(source):
        if depth:
            if source.startswith('/-',i): depth+=1;out.extend('  ');i+=2
            elif source.startswith('-/',i): depth-=1;out.extend('  ');i+=2
            else: out.append('\n' if source[i]=='\n' else ' ');i+=1
        elif string:
            out.append(source[i])
            if source[i]=='\\' and i+1<len(source):
                i+=1;out.append(source[i])
            elif source[i]=='"': string=False
            i+=1
        elif source.startswith('/-',i): depth=1;out.extend('  ');i+=2
        elif source.startswith('--',i):
            while i<len(source) and source[i]!='\n': out.append(' ');i+=1
        else:
            if source[i]=='"': string=True
            out.append(source[i]);i+=1
    assert depth==0
    return ''.join(out)

def declarations(source):
    scopes=[]
    result=[]
    for line in without_comments(source).splitlines():
        ns=re.match(r'^namespace\s+(\S+)',line)
        sec=re.match(r'^(?:noncomputable\s+)?section(?:\s+(\S+))?\s*$',line)
        end=re.match(r'^end(?:\s+(\S+))?\s*$',line)
        if ns:
            scopes.append(('namespace',ns.group(1)))
        elif sec:
            scopes.append(('section',sec.group(1)))
        elif end:
            kind,label=scopes.pop()
            if end.group(1):
                assert label==end.group(1),(line,kind,label)
        m=re.match(r"^(?:@\[[^\n]+\]\s*)?(?:noncomputable\s+)?(theorem|lemma|def|abbrev|instance|structure)\s+([\w.']+)",line)
        if m:
            ns='.'.join(label for kind,label in scopes if kind=='namespace')
            result.append({'kind':m.group(1),'name':ns+'.'+m.group(2)})
    # A global anonymous noncomputable section may legitimately end at EOF.
    assert all(kind=='section' and label is None for kind,label in scopes)
    assert len(result)==len({d['name'] for d in result})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit',type=Path,required=True)
    parser.add_argument('--archives',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    kit=a.kit.resolve(); archive_root=a.archives.resolve()
    out=(root/a.out).resolve() if not a.out.is_absolute() else a.out.resolve()
    assert out.is_relative_to(root) and not out.exists()
    out.mkdir(parents=True)
    envmeta=json.loads((root/'ENVIRONMENT.json').read_text())
    base=json.loads((root/'REPLAY_BASE113.json').read_text())
    object_map=json.loads((root/'INHERITED_OBJECTS113.json').read_text())
    assert sha(root/'INHERITED_OBJECTS113.json')==base['inherited_objects_manifest_sha256']
    assert sha(kit/'toolchain/bin/lean')==envmeta['lean_sha256']
    actual_commit=subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    assert actual_commit==envmeta['mathlib_commit']
    objects=out/'objects'; objects.mkdir()
    for key,ar in base['archives'].items():
        path=archive_root/ar['filename']
        assert sha(path)==ar['sha256']
        with zipfile.ZipFile(path) as z:
            for target,r in object_map.items():
                if r['archive']!=key:
                    continue
                data=z.read(r['member'])
                assert hashlib.sha256(data).hexdigest()==r['sha256']
                dest=objects/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    sources={'PaperXI.'+p.stem:p for p in sorted((root/'formalization/PaperXI').glob('*.lean'))}
    before={str(p.relative_to(root)):sha(p) for p in sources.values()}
    pending={name:[imp for imp in re.findall(r'^import\s+(\S+)',p.read_text(),re.M) if imp in sources] for name,p in sources.items()}
    order=[]
    while pending:
        ready=sorted(name for name,deps in pending.items() if all(d in order for d in deps))
        assert ready,'New module import cycle'
        for name in ready:
            order.append(name);del pending[name]
    env=os.environ.copy()
    env['LD_PRELOAD']=str(kit/'compat/app_path.so')
    env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
    env['LEAN_PATH']=':'.join(map(str,[objects]+sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))))
    lean=[str(kit/'toolchain/bin/lean'),'-j1','-DmaxHeartbeats=3000000','-DwarningAsError=true']
    receipt={'status':'RUNNING','source_hashes':before,'inherited_object_files':len(object_map),
             'baseline_modules':len(object_map)//2,'inherited_modules_rebuilt':False,
             'external_mathlib_rebuilt':False,'environment':envmeta,'archives':base['archives'],
             'commands':[],'modules':[]}
    start=time.monotonic()
    def save():
        (out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    def run(argv,log):
        receipt['commands'].append(argv);save();t=time.monotonic()
        r=subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=180)
        (out/log).write_text(r.stdout+r.stderr)
        assert r.returncode==0,f'{log} exited {r.returncode}'
        return r.stdout+r.stderr,time.monotonic()-t
    save()
    try:
        for name in order:
            p=sources[name];target=objects/Path(name.replace('.','/'))
            _,compile_s=run(lean+['-o',str(target.with_suffix('.olean')),'-i',str(target.with_suffix('.ilean')),str(p)],p.stem+'_compile.log')
            ds=declarations(p.read_text())
            audit=out/(p.stem+'_Audit.lean')
            audit.write_text('import '+name+'\n'+''.join('#check '+d['name']+'\n#print axioms '+d['name']+'\n' for d in ds))
            txt,audit_s=run(lean+[str(audit)],p.stem+'_axioms.log')
            found=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",txt,re.S)
            empty=re.findall(r"'([^']+)' does not depend on any axioms",txt)
            assert {n for n,_ in found}|set(empty)=={d['name'] for d in ds}
            axioms={ax.strip() for _,body in found for ax in body.split(',') if ax.strip()}
            assert axioms<={'Classical.choice','Quot.sound','propext'}
            _,checker_s=run([str(kit/'toolchain/bin/leanchecker'),'--verbose',name],p.stem+'_leanchecker.log')
            receipt['modules'].append({'module':name,'source_sha256':sha(p),'fresh_compile':'PASS',
                'compile_seconds':compile_s,'axiom_check_seconds':audit_s,'leanchecker_seconds':checker_s,
                'leanchecker':'PASS','declarations':ds,'exports_audited':len(ds),'axioms':sorted(axioms),
                'objects':{ext:sha(target.with_suffix(ext)) for ext in ['.olean','.ilean']}})
            save();print(name+': PASS ('+str(len(ds))+' named exports)',flush=True)
        assert before=={str(p.relative_to(root)):sha(p) for p in sources.values()}
        assert all(sha(objects/path)==r['sha256'] for path,r in object_map.items())
        receipt.update(status='PASS',inherited_before_after_hashes_match=True,
                       fresh_module_count=len(order),exports_audited=sum(r['exports_audited'] for r in receipt['modules']))
    except BaseException as exc:
        receipt.update(status='FAIL',error=repr(exc))
    finally:
        receipt['seconds']=time.monotonic()-start;save()
    return 0 if receipt['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
