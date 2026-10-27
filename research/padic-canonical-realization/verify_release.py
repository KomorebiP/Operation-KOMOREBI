#!/usr/bin/env python3
"""Read-only replay of frozen execution evidence, completeness, and archive checksums."""
from pathlib import Path
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
from evidence_parser import parse_declared,parse_environment,strip_comments,selftest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    errors=[];checks=0
    def ck(c,m):
        nonlocal checks;checks+=1
        if not c:errors.append(m)
    def data(p):return json.loads((ROOT/p).read_text())
    selftest();done=data('results/FINAL_RUN.json');ck(done['status']=='PASS','final run incomplete')
    for phase in done.get('phases',[]):
        r=data(f'results/{phase}.json');log=ROOT/r['log']
        ck(r['pass'] and r['status']=='completed',phase+': incomplete')
        ck(r['exit_status']==r['expected_exit'],phase+': exit')
        ck(sha(log)==r['log_sha256'],phase+': log changed')
        ck(r['input_hashes']==r['input_hashes_after'],phase+': input changed during run')
        for p,h in r['input_hashes_after'].items():ck((ROOT/p).is_file() and sha(ROOT/p)==h,phase+': source changed '+p)
        if r.get('expected_diagnostic'):ck(r['expected_diagnostic'] in log.read_text().lower(),phase+': wrong negative diagnostic')
    inv=data('verification/theorem_inventory.json');names=inv['names'];ck(len(names)==len(set(names))==inv['total'],'declared inventory')
    declared=parse_declared((ROOT/'results/declared_axioms.log').read_text())
    env=parse_environment((ROOT/'results/environment_axioms.log').read_text());allowed={'propext','Quot.sound','Classical.choice'}
    ck(set(declared)==set(names),'declared audit missing or extra names')
    for n in names:
        ck(n in env,'declared constant absent from environment '+n)
        if n in env and n in declared:ck(env[n][1]==declared[n],'axiom routes disagree '+n)
    for n,(mod,axs) in env.items():ck(axs<=allowed,'unexpected axioms '+n+':'+str(axs))
    inherited=data('PREDECESSOR_SOURCE_HASHES.json')
    for p,h in inherited.items():
        if p!='lean/KomorebiPadic.lean':ck(sha(ROOT/p)==h,'predecessor source changed '+p)
    import zipfile
    pre=data('PREDECESSOR_ARCHIVE.json');ck(sha(ROOT/pre['path'])==pre['sha256'],'predecessor archive hash')
    with zipfile.ZipFile(ROOT/pre['path']) as z:
        prefix=z.namelist()[0].split('/')[0]+'/'
        oldroot=z.read(prefix+'lean/KomorebiPadic.lean').decode()
        ck((ROOT/'lean/KomorebiPadic.lean').read_text()=='import KomorebiPadic.ResidualMinimalityExamples\n'+oldroot,'root changed beyond one new import')
    sources=list((ROOT/'lean').rglob('*.lean'));source_count=0
    for src in sources:
        code=strip_comments(src.read_text());source_count+=len(re.findall(r'\btheorem\s+[A-Za-z_]',code))
        ck(not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',code),'forbidden production construct '+str(src.relative_to(ROOT)))
        rel=src.relative_to(ROOT/'lean').with_suffix('')
        for ext in ['.olean','.ilean']:ck((ROOT/'compiled'/rel.with_suffix(ext)).is_file(),'missing artifact '+str(rel)+ext)
    ck(source_count==inv['total'],'source theorem syntax count differs from inventory')
    audit=data('results/audit_residual.json');ck(audit['status']=='PASS' and not audit['failures'],'finite audit')
    ck(audit['assertions']==sum(audit['counts'].values()),'finite assertion tally')
    jobs=re.findall(r'Build completed successfully \((\d+) jobs\)',(ROOT/'results/clean_build.log').read_text());ck(bool(jobs),'no final build success marker')
    if (ROOT/'CHECKSUMS.json').exists():
        for p,h in data('CHECKSUMS.json').items():ck((ROOT/p).is_file() and sha(ROOT/p)==h,'checksum '+p)
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,
      'scope':'Read-only evidence replay, not a new Lean execution.','production_modules':len(sources),
      'declared_theorems':len(names),'new_theorems':inv['new'],'inherited_theorems':inv['inherited'],
      'environment_theorem_constants':len(env),'axiom_free_declared':sum(not declared.get(n,{'missing'}) for n in names),
      'observed_axioms':sorted(set().union(*(a for _,a in env.values()))) if env else [],
      'build_jobs':int(jobs[-1]) if jobs else None,'fresh_assertions':audit['assertions'],'final_phases':len(done.get('phases',[]))}
if __name__=='__main__':
    try:r=verify()
    except Exception as e:r={'status':'FAIL','exception':repr(e)}
    print(json.dumps(r,indent=2));raise SystemExit(r['status']!='PASS')
