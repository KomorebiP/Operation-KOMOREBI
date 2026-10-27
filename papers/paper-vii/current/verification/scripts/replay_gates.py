#!/usr/bin/env python3
"""Replay available original gates in isolated copies; no dependency installation.

Source and downloads are read only. Static Lean checks authenticate stored
evidence, not a new kernel compilation. Numerical tests are invoked unchanged
as plain functions when pytest is absent, without synthesizing pytest.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, importlib.util, inspect, io, json, math
import os, platform, re, runpy, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
sys.dont_write_bytecode = True
COMPLETE = 'Paper_VII_Complete_v0.6.0_With_Visual_Appendix'
STRONG = 'PSC_Paper_VII_Strengthened_Annals_Edition_Final'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, x):
    p.write_text(json.dumps(x, indent=2, sort_keys=True)+'\n')

def hashes(p):
    return {str(f.relative_to(p)): {'sha256':sha(f),'bytes':f.stat().st_size}
            for f in sorted(p.rglob('*')) if f.is_file()}

def flatten(x, p=''):
    if isinstance(x,dict):
        for k,v in x.items(): yield from flatten(v,p+'/'+str(k))
    elif isinstance(x,list):
        for k,v in enumerate(x): yield from flatten(v,p+'/'+str(k))
    else: yield p,x

def command(argv, cwd, out, log, timeout=240):
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    t=time.monotonic()
    with (out/log).open('w') as h:
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=timeout)
    rec={'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log':log}
    if p.returncode: raise RuntimeError(rec)
    return rec

def import_path(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def static_formal(proof):
    v=import_path('original_verifier_for_static',proof/'scripts/verify.py')
    inv=json.loads((proof/'verification/theorem_inventory.json').read_text())
    rp=proof/'verification/final_finite_release_run/SUMMARY.json'
    old=json.loads(rp.read_text()); rows={r['module']:r for r in old['modules']}
    result={'scope':'Fresh static source and inherited report consistency only; no Lean invocation',
            'inherited_report_utc':old['started_utc'],'inherited_report_sha256':sha(rp),
            'modules':[],'controls':[], 'compiled_interfaces_present':False}
    assert set(inv)==set(v.MODULES)==set(rows)
    for name in v.MODULES:
        source=proof/'formalization'/(name+'.lean');row=rows[name]
        txt=v.without_comments(source.read_text())
        declarations=re.findall(r'\btheorem\s+(\w+)',txt)
        audits=set(re.findall(r'^#print axioms ([\w.]+)',txt,re.M))
        forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',txt)))
        log=rp.parent/row['log']; parsed=v.parse_axiom_audits(log.read_text())
        checks={'source_hash':sha(source)==row['sha256'],'log_hash':sha(log)==row['log_sha256'],
                'source_inventory':len(declarations)==len(inv[name]) and audits==set(inv[name]),
                'stored_axioms_equal_log':parsed==row['axiom_audits'],
                'audit_inventory':set(parsed)==set(inv[name]),
                'allowed_axioms':not ({a for xs in parsed.values() for a in xs}-v.ALLOWED_AXIOMS),
                'no_forbidden_tokens':not forbidden,
                'transitive_source_hashes':v.dependency_sources(proof,name)==row['dependency_source_sha256'],
                'stored_success':row['pass'] and row['exit_code']==0}
        assert all(checks.values()),(name,checks)
        result['modules'].append({'module':name,'theorems':len(declarations),'checks':checks})
    for row in old['negative_controls']:
        log=rp.parent/row['log'];text=log.read_text()
        checks={'source_hash':sha(proof/row['source'])==row['sha256'],
                'log_hash':sha(log)==row['log_sha256'],'stored_rejection':row['exit_code']==1 and row['pass'],
                'rejection_text':'error:' in text and ('sorry' if row['name']=='SorryPlaceholder' else 'decide') in text}
        assert all(checks.values())
        result['controls'].append({'name':row['name'],'checks':checks,'fresh_execution':False})
    result.update(module_count=len(result['modules']),theorem_count=sum(x['theorems'] for x in result['modules']),status='passed')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--downloads',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();source=args.source.resolve();downloads=args.downloads.resolve();out=args.out.resolve()
    if out==source or source in out.parents or out==downloads or downloads in out.parents:
        raise ValueError('Output must be outside preserved source and downloads')
    out.mkdir(parents=True,exist_ok=True)
    c=source/'complete'/COMPLETE;s=source/'strengthened'/STRONG
    before=hashes(source);write(out/'source_hashes_before.json',before)
    result={'scope':'Finite numerical/software/static/source-integrity audit; no fresh Lean kernel check',
            'environment':{'python':platform.python_version(),'platform':platform.platform()},'commands':[],
            'unavailable_gates':{'Lean_kernel':'lean/lake and portable pinned kit absent',
                'original_pytest_runner':'pytest absent; unchanged functions invoked directly',
                'original_SymPy_visual_examples':'SymPy/mpmath absent; no fallback presented as SymPy'}}
    archive=[]
    pairs=[('Paper_VII_Complete_v0.6.0_With_Visual_Appendix.zip',source/'complete',725),
           ('PSC_Paper_VII_Strengthened_Annals_Edition_Package.zip',source/'strengthened',59)]
    for name,base,expected_count in pairs:
        zpath=downloads/name
        with zipfile.ZipFile(zpath) as z:
            bad=z.testzip();members=[i for i in z.infolist() if not i.is_dir()]
            mismatches=[i.filename for i in members if not (base/i.filename).is_file() or
                hashlib.sha256(z.read(i)).hexdigest()!=sha(base/i.filename)]
        count=sum(p.is_file() for p in base.rglob('*'))
        assert bad is None and not mismatches and len(members)==count==expected_count
        archive.append({'archive':name,'sha256':sha(zpath),'archive_files':len(members),
            'extracted_files':count,'crc_test':'passed','all_member_bytes_match':True})
    result['archives']=archive
    result['commands'].append(command([sys.executable,str(c/'Run-PaperVII.py'),'verify'],c,out,'original_integrity.log'))
    static=static_formal(c/'original_snapshot');write(out/'static_formal_source_report.json',static)
    result['fresh_static_formal']=static
    with tempfile.TemporaryDirectory(prefix='paper_vii_finite_replay_') as td:
        tmp=Path(td);proof=tmp/'verifier';shutil.copytree(c/'original_snapshot/scripts',proof)
        result['commands'].append(command([sys.executable,'test_verifier.py'],proof,out,'original_verifier_regressions.log'))
        result['verifier_regression_tests']=16
        companion=tmp/'companion';shutil.copytree(c/'original_companion',companion)
        sys.path.insert(0,str(companion));tests=[];capture=io.StringIO()
        with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):
            for path in sorted((companion/'tests').glob('test_*.py')):
                module=runpy.run_path(str(path))
                for name,fn in sorted(module.items()):
                    if name.startswith('test_') and callable(fn):
                        assert not inspect.signature(fn).parameters
                        t=time.monotonic();fn();tests.append({'file':path.name,'function':name,
                            'status':'passed','seconds':time.monotonic()-t})
        sys.path.pop(0)
        write(out/'original_direct_test_functions.json',{'runner':'direct Python function invocation of unchanged source; no pytest',
            'source_test_files':5,'test_functions':len(tests),'tests':tests})
        (out/'original_direct_tests.log').write_text(capture.getvalue())
        from projector_quantum_calculus.experiments import run_experiments
        run_experiments(out/'original_numerical_results.json',out/'original_numerical_summary.csv')
        aa=dict(flatten(json.loads((c/'original_companion/results/numerical_results.json').read_text())))
        bb=dict(flatten(json.loads((out/'original_numerical_results.json').read_text())))
        records=[]
        for k,a in aa.items():
            b=bb.get(k)
            numeric=isinstance(a,(int,float)) and not isinstance(a,bool)
            close=math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-10) if numeric and isinstance(b,(int,float)) else a==b
            records.append({'field':k,'stored':a,'fresh':b,'numeric':numeric,'exact_equal':a==b,'within_comparison_tolerance':close})
        comparison={'numeric_fields':sum(r['numeric'] for r in records),'all_fields':len(records),
            'exactly_equal_fields':sum(r['exact_equal'] for r in records),
            'all_fields_within_comparison_tolerance':set(aa)==set(bb) and all(r['within_comparison_tolerance'] for r in records),
            'comparison_tolerance':{'absolute':1e-10,'relative':1e-8},'records':records}
        write(out/'original_stored_field_comparison.json',comparison)
        result['original_direct_tests']=len(tests)
        result['original_experiments']={k:v for k,v in comparison.items() if k!='records'}
        strong=tmp/'strengthened';shutil.copytree(s,strong)
        result['commands'].append(command([sys.executable,'verification/verify_paper_vii.py'],strong,out,'strengthened_original_suite.log'))
        new=json.loads((strong/'verification/verification_results.json').read_text())
        old=json.loads((s/'verification/verification_results.json').read_text())
        write(out/'strengthened_numerical_results.json',new)
        write(out/'strengthened_stored_comparison.json',{'exactly_equal':new==old,'fresh':new,'inherited':old})
        result['strengthened_finite_suite']={'checks':new['total_checks'],'groups':len(new['groups']),
            'status':new['status'],'stored_structural_result_exactly_equal':new==old,'seed':20260814}
    exact=Path(__file__).with_name('exact_rational_witnesses.py')
    if exact.exists():
        result['commands'].append(command([sys.executable,str(exact),'--out',str(out/'exact_rational_witnesses.json')],out,out,'independent_exact_witnesses.log'))
        result['independent_exact_witnesses']=json.loads((out/'exact_rational_witnesses.json').read_text())
    after=hashes(source);write(out/'source_hashes_after.json',after)
    assert before==after
    result.update(source_files_preserved=len(after),source_bytes_preserved=True,status='completed_with_explicit_unavailable_gates')
    result['artifact_hashes']={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ('manifest.json','stdout.txt','stderr.txt','results.json')}
    write(out/'results.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('fresh_static_formal','independent_exact_witnesses','artifact_hashes')},indent=2))

if __name__=='__main__':main()
