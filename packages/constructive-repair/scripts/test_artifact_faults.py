#!/usr/bin/env python3
"""Fault-inject a disposable extracted release and require scoped gate failures.

The extracted copy is not the original artifact. The manifest is deliberately
refreshed after each mutation: source-bound receipts must catch more than an
ordinary checksum mismatch. These tests do not simulate a signed trust root.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zipfile


def h(data):return hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    result={'status':'RUNNING','archive_sha256':h(a.archive.read_bytes()),'controls':[],'checks':[]}
    def save(): (out/'artifact_faults.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    try:
        extract=out/'extracted';extract.mkdir()
        with zipfile.ZipFile(a.archive) as z:
            names=z.namelist()
            if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP member')
            for name in names:
                p=PurePosixPath(name)
                if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('Unsafe member')
            if z.testzip() is not None:raise ValueError('ZIP CRC failure')
            z.extractall(extract)
        dirs=list(extract.iterdir())
        if len(dirs)!=1 or not dirs[0].is_dir():raise ValueError('Expected one package root')
        root=dirs[0]
        manifest=(root/'MANIFEST.json').read_bytes();checksums=(root/'SHA256SUMS.txt').read_bytes()
        def gate(label):
            env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
            p=subprocess.run([sys.executable,str(root/'scripts/release_gate.py')],cwd=root,env=env,
                             capture_output=True,text=True,encoding='utf-8',timeout=90)
            (out/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
            return p.returncode,p.stdout+p.stderr
        rc,txt=gate('baseline_gate')
        if rc!=0:raise ValueError('Unmodified artifact did not pass: '+txt)
        result['checks'].append({'name':'baseline_gate','pass':True})
        def reseal():
            m=json.loads(manifest)
            for rec in m['files']:
                data=(root/rec['path']).read_bytes();rec['bytes']=len(data);rec['sha256']=h(data)
            mb=(json.dumps(m,indent=2)+'\n').encode('utf-8');(root/'MANIFEST.json').write_bytes(mb)
            lines=[r['sha256']+'  '+r['path'] for r in m['files']]+[h(mb)+'  MANIFEST.json']
            (root/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        def control(label,path,mutate,expected):
            p=root/path;original=p.read_bytes()
            try:
                p.write_bytes(mutate(original));reseal();rc,txt=gate(label)
                okay=rc==2 and expected in txt
                result['controls'].append({'name':label,'pass':okay,'expected_diagnostic':expected,
                                           'manifest_refreshed':True,'log':label+'.log'})
                save()
                if not okay:raise ValueError('Incorrect rejection '+label+': '+txt)
            finally:
                p.write_bytes(original);(root/'MANIFEST.json').write_bytes(manifest)
                (root/'SHA256SUMS.txt').write_bytes(checksums)
        def change_json(fn):
            def go(b):
                obj=json.loads(b);fn(obj);return (json.dumps(obj,indent=2)+'\n').encode('utf-8')
            return go
        formal='evidence/verification/current/verification.json'
        accepted='evidence/rc3/acceptance_run/acceptance.json'
        control('changed_runtime_source','python/branch_menu.py',lambda b:b+b'\n# altered\n','Wheel/source mismatch')
        control('stale_readme_acceptance','README.md',lambda b:b+b'\nChanged after acceptance.\n','Stale acceptance evidence')
        control('changed_proof','lean/KomorebiRepair/Basic.lean',lambda b:b+b'\n-- altered\n','Current proof differs')
        control('changed_snapshot','provenance/v0.2.0/lean/KomorebiRepair/Basic.lean',lambda b:b+b'\n-- altered\n','Historical snapshot changed')
        control('failed_formal_receipt',formal,change_json(lambda d:d.update(status='FAIL')),'Formal verification did not pass')
        control('missing_axiom_row',formal,change_json(lambda d:d['axioms'].pop(next(iter(d['axioms'])))),'Incomplete axiom inventory')
        control('forbidden_axiom',formal,change_json(lambda d:d['axioms'].__setitem__(next(iter(d['axioms'])),['sorryAx'])),'Disallowed theorem axiom')
        control('missing_replay',formal,change_json(lambda d:d.update(commands=[c for c in d['commands'] if c['label']!='replay_Basic'])),'Missing compilation or replay')
        control('duplicate_label',formal,change_json(lambda d:d['commands'].append(d['commands'][0])),'Duplicate verification command')
        control('wrong_accepted_wheel',accepted,change_json(lambda d:d.update(wheel_sha256='0'*64)),'Acceptance used a different wheel')
        control('latex_changed','monograph/Constructive_Repair.tex',lambda b:b+b'\n% changed\n','LaTeX source changed')
        control('pdf_changed','monograph/Constructive_Repair.pdf',lambda b:b+b'\n% changed\n','PDF changed')
        control('failed_document_check','monograph/build_receipt.json',change_json(lambda d:d.update(references_resolved=False)),'Monograph diagnostic check failed')
        control('unreviewed_publication_change','PUBLICATION_DECISION.json',change_json(lambda d:d.update(publication_authorized=True)),'Publication decision changed')
        rc,txt=gate('restored_gate')
        if rc!=0:raise ValueError('Restored artifact failed: '+txt)
        result['checks'].append({'name':'restored_gate','pass':True})
        result['status']='PASS';save();print(json.dumps({'status':'PASS','controls':len(result['controls'])}));return 0
    except Exception as exc:
        result.update(status='FAIL',error=str(exc));save();print(json.dumps(result));return 1
if __name__=='__main__':raise SystemExit(main())
