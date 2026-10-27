#!/usr/bin/env python3
"""Rebuild Block72's declared finite assertions. This is not a Lean proof checker."""
from __future__ import annotations
import argparse, copy, datetime as dt, hashlib, io, json, os, platform, shutil
import subprocess, sys, tempfile, time, zipfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESULTS=['work72/verification/higher_seven72.json','work72/verification/independent_higher_seven72.json']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(cond,msg):
    if not cond:raise ValueError(msg)
def safe(root,name):
    p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'Unsafe path '+name)
    out=(root/p).resolve();need(out.is_relative_to(root.resolve()),'Escaping path '+name);return out

def integrity(root):
    m=json.loads((root/'MANIFEST.json').read_text());payloads=m['payloads']
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    need(actual==set(payloads)|{'MANIFEST.json'},'Payload member set differs')
    for n,h in payloads.items():need(sha(safe(root,n))==h,'Payload hash changed: '+n)
    pred=next((root/'predecessor').glob('*.zip'))
    sources=json.loads((root/'work72/source_records/INHERITED_INPUTS.json').read_text())
    need(sha(pred)==sources['predecessor_sha256'],'Predecessor bytes changed')
    cache={():pred.read_bytes()};maxdepth=1
    for row in sources['sources']:
        prefix=()
        for link in row.get('archive_chain',[]):
            nxt=prefix+(link,)
            if nxt not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[prefix])) as z:cache[nxt]=z.read(link)
            prefix=nxt
        with zipfile.ZipFile(io.BytesIO(cache[prefix])) as z:data=z.read(row['archive_member'])
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'Inherited source changed: '+row['archive_member'])
        need(safe(root,row['copy']).read_bytes()==data,'Source copy changed: '+row['copy'])
        maxdepth=max(maxdepth,len(prefix)+1)
    frozen=json.loads((root/'work72/inputs/B71_B70_refinement70.json').read_text())
    expected=Counter({(7,6,1):2,(21,6,1):2,(28,6,1):2,(42,6,1):2})
    need(Counter(tuple(t['alpha']) for t in frozen['survivors'])==expected,'Frozen eight coefficients differ')
    return {'payload_count':len(payloads),'predecessor_sha256':sha(pred),
            'source_leaves':len(sources['sources']),'deepest_archive_level':maxdepth,'frozen_patterns':8}

def execute(argv,cwd,timeout=300):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    t=time.perf_counter()
    try:
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
        return {'argv':argv,'status':'completed','exit_status':p.returncode,'runtime_seconds':time.perf_counter()-t,'stdout':p.stdout}
    except subprocess.TimeoutExpired as e:
        s=e.stdout or '';s=s.decode(errors='replace') if isinstance(s,bytes) else s
        return {'argv':argv,'status':'timeout','exit_status':None,'runtime_seconds':time.perf_counter()-t,'stdout':s}

def checks(root,tmp):
    dst=tmp/'scratch';shutil.copytree(root,dst)
    record=json.loads((dst/'work72/verification/COMPUTATION_MANIFEST.json').read_text())
    for row in record['input_artifacts']:
        need(row['sha256']==row['sha256_after']==sha(dst/row['path']),'Computation input hash mismatch')
    job=execute([sys.executable,'-B','work72/computations/validate_v1_record.py','work72/verification/COMPUTATION_MANIFEST.json','--root',str(dst)],dst)
    need(job['exit_status']==0,'Project-local v1 manifest check failed: '+str(job))
    expected={n:sha(dst/n) for n in RESULTS}
    for n in RESULTS:(dst/n).unlink()
    primary=execute([sys.executable,'-B','work72/computations/higher_seven72.py','--output',RESULTS[0]],dst)
    need(primary['exit_status']==0,'Primary scientific run failed: '+str(primary))
    secondary=execute([sys.executable,'-B','work72/computations/independent_higher_seven72.py','--certificate',RESULTS[0],'--output',RESULTS[1]],dst)
    need(secondary['exit_status']==0,'Independent scientific run failed: '+str(secondary))
    for n in RESULTS:need(sha(dst/n)==expected[n],'Regenerated result differs: '+n)
    data=json.loads((dst/RESULTS[0]).read_text())
    tweaks=[
      ('omega_coordinate',lambda x:x['coordinate_tables'][1].__setitem__('omega_H_coordinate',4),'coordinate_tables'),
      ('matrix_action',lambda x:x['compatible_root_matrices']['2'][0].__setitem__(0,2),'compatible_root_matrices'),
      ('false_elimination',lambda x:x.__setitem__('bounded_augmented_lifts',0),'bounded_augmented_lifts'),
      ('false_lift_count',lambda x:x.__setitem__('accepted_local_lifts',0),'accepted_local_lifts'),
      ('uniformizer_omission',lambda x:x['negative_controls'].__setitem__('uniformizer_term_may_be_dropped_mod49_for_c1',True),'negative_controls'),
      ('unsupported_window',lambda x:x['precision_controls'][0].__setitem__('last_certain_j',7),'precision_controls'),
      ('invented_global_lift',lambda x:x['negative_controls'].__setitem__('global_depth1_line_lifts_mod49',True),'negative_controls'),
      ('false_root',lambda x:x['sample_local_roots'][0].__setitem__(2,0),'sample_local_roots'),
    ]
    negative=[]
    for label,change,key in tweaks:
        bad=copy.deepcopy(data);change(bad);p=tmp/'tampered.json';p.write_text(json.dumps(bad));out=tmp/'bad_output.json'
        if out.exists():out.unlink()
        j=execute([sys.executable,'-B','work72/computations/independent_higher_seven72.py','--certificate',str(p),'--output',str(out)],dst)
        need(j['exit_status'] not in (None,0) and 'CERTIFICATE_MISMATCH' in j['stdout'] and key in j['stdout'],
             'Tamper not rejected as intended: '+label+' '+str(j))
        negative.append({'name':label,'rejected':True,'expected_key':key,'execution':j})
    text=(dst/'README.md').read_bytes();(dst/'README.md').write_bytes(text+b'\nDELIBERATE CORRUPTION\n')
    j=execute([sys.executable,'-B','verify.py','--integrity-only'],dst)
    need(j['exit_status'] not in (None,0) and 'Payload hash changed: README.md' in j['stdout'],'Payload tamper not rejected')
    negative.append({'name':'payload','rejected':True,'execution':j});(dst/'README.md').write_bytes(text)
    integrity(dst)
    return {'outputs_deleted_and_regenerated':RESULTS,'output_hashes':expected,'primary':primary,
            'independent':secondary,'project_local_v1_validation':job,'negative_controls':negative,
            'finite_summary':{k:data[k] for k in ['unit_coordinate_cases','period_cases','rational_A_mod343_cases',
             'lambda_pair_cases','higher_lift_input_count','accepted_local_lifts','bounded_augmented_lifts',
             'valuation_gauge_cases','local_root_certificates','new_frobenius_point_counts']}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path);p.add_argument('--integrity-only',action='store_true');p.add_argument('--replay-predecessor',action='store_true');a=p.parse_args()
    if a.report and a.report.resolve().is_relative_to(ROOT):p.error('Report must be outside immutable package')
    t=time.perf_counter();r={'schema':'beal.block72.execution.v1','started_at':dt.datetime.now(dt.timezone.utc).isoformat(),
      'status':'RUNNING','environment':{'python':sys.version,'platform':platform.platform(),'bytecode_disabled':True},
      'scope':'Block72 declared finite assertions. Optional immediate predecessor is not the full history.',
      'proof_boundary':['Inherited analytical/global claims are not certified by these finite runs.','No new Lean or independent mathematical reviewer.','All eight bounded patterns remain.'],
      'resources':{'per_new_command_wall_seconds':300,'memory_limit':None,'randomness':False}}
    code=0
    try:
        r['integrity']=integrity(ROOT)
        if not a.integrity_only:
            with tempfile.TemporaryDirectory(prefix='beal72_') as td:
                tmp=Path(td);r['scientific_replay']=checks(ROOT,tmp)
                if a.replay_predecessor:
                    target=tmp/'predecessor';target.mkdir();pred=next((ROOT/'predecessor').glob('*.zip'))
                    with zipfile.ZipFile(pred) as z:
                        for n in z.namelist():safe(target,n)
                        z.extractall(target)
                    roots=list(target.glob('*/verify.py'));need(len(roots)==1,'Wrong predecessor root')
                    path=tmp/'Block71_Replay.json';job=execute([sys.executable,'-B','verify.py','--report',str(path)],roots[0].parent,600)
                    need(job['exit_status']==0 and path.exists(),'Immediate predecessor failed')
                    pr=json.loads(path.read_text());need(pr['status']=='PASS_DECLARED_CHECKS','Unexpected predecessor status')
                    r['immediate_predecessor']={'execution':job,'report':pr,'full_historical_chain':False}
        r['integrity_after']=integrity(ROOT);r['status']='PASS_INTEGRITY_ONLY' if a.integrity_only else 'PASS_DECLARED_CHECKS'
    except Exception as e:
        code=1;r['status']='FAILED';r['error']=type(e).__name__+': '+str(e);print(r['error'],file=sys.stderr)
    r['runtime_seconds']=time.perf_counter()-t;r['exit_status']=code
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(r['status'],f'{r["runtime_seconds"]:.3f}s');return code
if __name__=='__main__':raise SystemExit(main())
