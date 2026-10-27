#!/usr/bin/env python3
"""Bounded archival computation replay. Does not invoke Lean or GPU timing."""
from __future__ import annotations
import argparse, hashlib, importlib.util, inspect, io, json, os, platform, re
import shutil, sys, tempfile, unittest, warnings
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
C = ROOT/'source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix'
S = ROOT/'source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package'
P = C/'original_snapshot'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p, name):
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def static():
    sys.path.insert(0,str(P/'scripts'))
    import verify
    inventory=json.loads((P/'verification/theorem_inventory.json').read_text())
    summary=json.loads((P/'verification/sixth_final/SUMMARY.json').read_text())
    rows={r['module']:r for r in summary['modules']}
    assert set(rows)==set(verify.MODULES)==set(inventory)
    report=[];theorems=constructions=0
    for name in verify.MODULES:
        row=rows[name];source=P/row['source'];log=P/'verification/sixth_final'/row['log']
        assert sha(source)==row['sha256']
        assert sha(log)==row['log_sha256']
        text=verify.without_comments(source.read_text())
        forbidden=re.findall(r'\b(?:sorry|admit|axiom|unsafe)\b',text)
        assert not forbidden,(name,forbidden)
        count=len(re.findall(r'\btheorem\s+\w+',text))
        assert count==row['theorem_declarations']
        audits=re.findall(r'^#print axioms ([\w.]+)',text,re.M)
        assert len(audits)==len(set(audits))
        assert set(audits)==set(inventory[name])
        parsed=verify.parse_axiom_audits(log.read_text())
        assert parsed==row['axiom_audits']
        assert set(parsed)==set(inventory[name])
        assert all(set(ax)<=verify.ALLOWED_AXIOMS for ax in parsed.values())
        declared=verify.CONSTRUCTIONS.get(name,set())
        assert set(row['construction_audits'])==declared
        assert set(re.findall(r'\btheorem\s+(\w+)',text))=={n.rsplit('.',1)[-1] for n in set(audits)-declared}
        assert verify.dependency_sources(P,name)==row['dependency_source_sha256']
        assert row['pass'] and row['exit_code']==0
        report.append(dict(module=name,source_sha256=sha(source),log_sha256=sha(log),theorems=count,construction_audits=len(declared)))
        theorems+=count;constructions+=len(declared)
    for key,path in [('runner_sha256',P/'scripts/check_low_memory.py'),('verifier_sha256',P/'scripts/verify.py'),('inventory_sha256',P/'verification/theorem_inventory.json')]:
        assert summary[key]==sha(path)
    controls=[]
    for row in summary['negative_controls']:
        assert sha(P/row['source'])==row['sha256']
        assert sha(P/'verification/sixth_final'/row['log'])==row['log_sha256']
        assert row['pass'] and row['exit_code']==row['expected_exit_code']==1
        controls.append(row['name'])
    assert (theorems,constructions,len(report))==(392,66,40)
    ledger=json.loads((P/'verification/coverage_ledger.json').read_text())
    assert sum(r['proof']=='complete' for r in ledger['records'])==56
    assert all(r['lean_status']=='checked' for r in ledger['records'] if r['proof']=='complete')
    assert sum(r['proof']=='external' for r in ledger['records'])==4
    return dict(status='PASS',scope='Fresh static comparison of source, metadata, inherited compiler-log bytes and recorded axiom inventory. No new Lean compilation or independent proof-kernel checking.',modules=report,theorem_declarations=theorems,construction_audits=constructions,audited_names=theorems+constructions,inherited_negative_controls=controls,inherited_completed_utc=summary['updated_utc'],unavailable=['Lean','Lake','portable pinned Mathlib kit','compiled local interfaces'])

def test_functions():
    sys.path[:0]=[str(S),str(S/'legacy')]
    rows=[];allwarn=[];figures=[]
    paths=sorted((S/'legacy/tests').glob('test_*.py'))+[S/'verification/test_strengthened.py']
    with tempfile.TemporaryDirectory(prefix='paper_viii_test_figures_') as temp:
        for index,path in enumerate(paths):
            mod=load(path,'archival_test_'+str(index))
            for name,func in sorted(vars(mod).items()):
                if not name.startswith('test_') or not inspect.isfunction(func):continue
                args=inspect.signature(func).parameters
                assert list(args) in [[],['tmp_path']],(path,name,str(args))
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('always')
                    func(**({'tmp_path':Path(temp)} if args else {}))
                allwarn.extend(dict(test=name,category=w.category.__name__,message=str(w.message)) for w in ws)
                rows.append(dict(file=str(path.relative_to(ROOT)),test=name,status='PASS',runner='Direct unchanged Python function invocation; pytest unavailable'))
        for path in sorted(Path(temp).iterdir()):figures.append(dict(name=path.name,bytes=path.stat().st_size,sha256=sha(path)))
    assert len(rows)==34
    return dict(status='PASS',test_functions=len(rows),tests=rows,generated_historical_figure_files=figures,warnings=allwarn,scope='Direct invocation of unchanged 23 baseline plus 11 strengthened test functions, including a real temporary Path for the single fixture. This did not run pytest, benchmark hardware, or a Lean compiler. Generated charts replot stored benchmark rows.')

def unit():
    sys.path.insert(0,str(P/'scripts'))
    suite=unittest.defaultTestLoader.discover(str(P/'scripts'),pattern='test_*.py')
    buf=io.StringIO();result=unittest.TextTestRunner(stream=buf,verbosity=2).run(suite)
    print(buf.getvalue())
    assert result.wasSuccessful()
    assert result.testsRun==43
    return dict(status='PASS',tests_run=result.testsRun,scope='Verifier and metadata software regressions, including bounded mirror tests. Does not invoke Lean.',log=buf.getvalue())

def integrity():
    failures=[];results=[]
    for root,name,manifest in [(C,'complete','MANIFEST.json'),(P,'snapshot','MANIFEST_SHA256.json')]:
        data=json.loads((root/manifest).read_text())
        for rel,item in data['files'].items():
            p=root/rel
            if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:failures.append(name+':'+rel)
        results.append(dict(manifest=name,checked=len(data['files'])))
    lines=(S/'MANIFEST.sha256').read_text().splitlines();count=0
    for line in lines:
        if not line.strip():continue
        h,rel=line.split(maxsplit=1);rel=rel.lstrip('*')
        if sha(S/rel)!=h:failures.append('strengthened:'+rel)
        count+=1
    results.append(dict(manifest='strengthened',checked=count))
    assert not failures,failures
    return dict(status='PASS',manifests=results,scope='Byte consistency with archived manifests, not authenticity signature or proof evidence.')

def numeric(mode,out):
    if mode=='original':
        sys.path.insert(0,str(S));mod=load(S/'verification/run_full_verification.py','archived_full_verification')
        result=mod.run();assert result['status']=='passed';return result
    if mode=='sixth':
        mod=load(P/'scripts/run_sixth_regressions.py','archived_sixth');result=mod.run();assert result['pass'];return result
    if mode=='fifth':
        mod=load(P/'scripts/run_fifth_regressions.py','archived_fifth')
        saved=sys.argv;sys.argv=[str(P/'scripts/run_fifth_regressions.py'),'--out',str(out)]
        try: assert mod.main()==0
        finally:sys.argv=saved
        return json.loads(out.read_text())
    if mode=='structured':
        mod=load(P/'scripts/run_structured_regressions.py','archived_structured');mod.OUT=out.parent/'structured_results'
        assert mod.main()==0
        return json.loads((mod.OUT/'SUMMARY.json').read_text())
    raise ValueError(mode)

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['integrity','static','test-functions','unit','original','sixth','fifth','structured']);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.mode=='integrity':r=integrity()
    elif args.mode=='static':r=static()
    elif args.mode=='test-functions':r=test_functions()
    elif args.mode=='unit':r=unit()
    else:r=numeric(args.mode,args.out)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS',args.mode)
    print(json.dumps({k:v for k,v in r.items() if k not in ['modules','cases','tests','warnings','log','generated_historical_figure_files']},indent=2))
if __name__=='__main__':main()
