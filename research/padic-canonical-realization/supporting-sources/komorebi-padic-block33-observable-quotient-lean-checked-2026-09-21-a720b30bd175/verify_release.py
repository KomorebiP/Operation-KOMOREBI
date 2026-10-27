#!/usr/bin/env python3
"""Read-only replay of retained evidence, hashes, scope, and audit completeness."""
from pathlib import Path
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    errors=[]; checks=0
    def ck(ok,msg):
        nonlocal checks; checks+=1
        if not ok:errors.append(msg)
    def data(name):return json.loads((ROOT/name).read_text())
    done=data('results/FINAL_RUN.json');ck(done['status']=='PASS','final plan incomplete')
    for phase in done.get('phases',[]):
        r=data(f'results/{phase}.json');log=ROOT/r['log']
        ck(r['pass'] and r['status']=='completed',phase+': not completed successfully')
        ck(r['exit_status']==r['expected_exit'],phase+': unexpected exit')
        ck(sha(log)==r['log_sha256'],phase+': changed log')
        ck(r['input_hashes']==r['input_hashes_after'],phase+': inputs changed during run')
        for path,digest in r['input_hashes_after'].items():
            ck((ROOT/path).is_file() and sha(ROOT/path)==digest,phase+': changed input '+path)
        if r.get('expected_diagnostic'):ck(r['expected_diagnostic'] in log.read_text().lower(),phase+': absent negative diagnostic')
    inventory=data('verification/theorem_inventory.json');names=inventory['names']; new=inventory['new_names']
    ck(len(names)==len(set(names))==inventory['total'],'declared inventory duplicate/count')
    env={}
    for line in (ROOT/'results/environment_axioms.log').read_text().splitlines():
        if not line.startswith('PROJECT_AXIOMS|'):continue
        parts=line.split('|');ck(len(parts)==4,'malformed environment audit row')
        if len(parts)!=4:continue
        _,name,module,axs=parts;ck(name not in env,'duplicate environment name '+name)
        env[name]=(module,set(filter(None,axs.split(','))))
    allowed={'propext','Quot.sound','Classical.choice'}
    for name,(mod,axs) in env.items():ck(axs<=allowed,'unexpected axioms in '+name+': '+str(axs))
    for name in names:ck(name in env,'declared theorem absent from environment: '+name)
    inherited=data('PREDECESSOR_SOURCE_HASHES.json')
    for path,digest in inherited.items():
        if path=='lean/KomorebiPadic.lean':continue
        ck(sha(ROOT/path)==digest,'predecessor source changed '+path)
    pre=data('PREDECESSOR_ARCHIVE.json');ck(sha(ROOT/pre['path'])==pre['sha256'],'predecessor archive changed')
    sources=list((ROOT/'lean').rglob('*.lean'))
    for src in sources:
        rel=src.relative_to(ROOT/'lean').with_suffix('')
        for ext in ['.olean','.ilean']:
            target=ROOT/'compiled'/str(rel.with_suffix(ext))
            ck(target.is_file(),'missing compiled artifact '+str(rel)+ext)
    # Source-only forbidden declarations, ignoring line and nested block comments.
    for src in sources:
        text=src.read_text();out=[];i=0;depth=0
        while i<len(text):
            if text.startswith('/-',i):depth+=1;i+=2;continue
            if depth and text.startswith('-/',i):depth-=1;i+=2;continue
            if depth:i+=1;continue
            if text.startswith('--',i):
                end=text.find('\n',i);i=len(text) if end<0 else end;continue
            out.append(text[i]);i+=1
        code=''.join(out)
        ck(not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',code),'forbidden production token '+str(src))
    audit=data('results/audit_observable.json')
    ck(audit['status']=='PASS' and not audit['failures'],'finite audit failed')
    ck(audit['assertions']==sum(audit['counts'].values()),'finite audit count mismatch')
    build=(ROOT/'results/clean_build.log').read_text()
    jobs=re.findall(r'Build completed successfully \((\d+) jobs\)',build)
    ck(bool(jobs),'successful clean build marker missing')
    if (ROOT/'CHECKSUMS.json').exists():
        ledger=data('CHECKSUMS.json')
        for path,digest in ledger.items():ck((ROOT/path).is_file() and sha(ROOT/path)==digest,'checksum mismatch '+path)
    observed=sorted(set().union(*(axs for _,axs in env.values()))) if env else []
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,
      'scope':'Read-only retained evidence replay. This command does not execute Lean.',
      'source_theorems':len(names),'inherited_theorems':inventory['inherited'],'new_theorems':len(new),
      'environment_theorem_constants':len(env),'axiom_free_source_theorems':sum(not env[n][1] for n in names if n in env),
      'observed_axioms':observed,'production_modules':len(sources),'build_jobs':int(jobs[-1]) if jobs else None,
      'finite_assertions':audit['assertions'],'final_phases':len(done.get('phases',[]))}

if __name__=='__main__':
    try:r=verify()
    except Exception as e:r={'status':'FAIL','exception':repr(e)}
    print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
