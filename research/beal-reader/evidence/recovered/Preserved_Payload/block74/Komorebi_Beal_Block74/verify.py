#!/usr/bin/env python3
"""Rebuild Block74 finite checks. Not a proof of the inherited arithmetic hypotheses."""
from __future__ import annotations
import argparse,copy,datetime as dt,hashlib,io,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESULTS=['work74/verification/trace_probe74.json','work74/verification/independent74.json']

def require(x,msg):
    if not x:raise ValueError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inside(root,s):
    p=Path(s);require(not p.is_absolute() and '..' not in p.parts,'Unsafe relative path')
    r=(root/p).resolve();require(r.is_relative_to(root.resolve()),'Path escape');return r

def integrity(root):
    d=json.loads((root/'MANIFEST.json').read_text());payload=d['payloads']
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual==set(payload)|{'MANIFEST.json'},'Payload member set changed')
    for p,h in payload.items():require(sha(inside(root,p))==h,'Payload hash changed: '+p)
    pred=next((root/'predecessor').glob('*.zip'));r=json.loads((root/'work74/source_records/INHERITED_INPUTS.json').read_text())
    require(sha(pred)==r['predecessor_sha256'],'Predecessor bytes changed')
    with zipfile.ZipFile(pred) as z:
        for x in r['sources']:
            b=z.read(x['archive_member']);require(hashlib.sha256(b).hexdigest()==x['sha256'],'Pinned source changed')
            require((root/x['copy']).read_bytes()==b,'Pinned copy changed')
    return {'payload_hashes':len(payload),'pinned_immediate_source_leaves':len(r['sources']),'predecessor_sha256':sha(pred)}

def evidence_record(root):
    d=json.loads((root/'work74/verification/COMPUTATION_MANIFEST.json').read_text())
    require(d['schema_version']==2 and d['run']['status']=='completed' and d['run']['exit_status']==0,'Bad execution record')
    require(set(d['execution_artifacts'])=={a['path'] for a in d['input_artifacts']},'Bad input set')
    require(set(d['declared_results'])==set(RESULTS),'Bad declared result set')
    for a in d['input_artifacts']:
        require(a['sha256']==a['sha256_after']==sha(inside(root,a['path'])),'Changed execution input')
    for a in d['outputs']:require(a['sha256']==sha(inside(root,a['path'])),'Changed recorded output')
    require(d['mathematics']['non_claims'] and d['run']['runtime_seconds']>=0,'Missing proof scope')
    return {'schema':2,'validation':'explicit project-local field/hash checks, not an installed plugin-validator run','passed':True}

def run(argv,cwd,timeout=90):
    st=time.perf_counter()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    try:
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
        return {'argv':argv,'exit_status':p.returncode,'status':'completed','runtime_seconds':time.perf_counter()-st,'stdout':p.stdout}
    except subprocess.TimeoutExpired as e:
        s=e.stdout or '';s=s.decode(errors='replace') if isinstance(s,bytes) else s
        return {'argv':argv,'exit_status':None,'status':'timeout','runtime_seconds':time.perf_counter()-st,'stdout':s}

def science(root,tmp):
    dst=tmp/'scratch';shutil.copytree(root,dst);record=evidence_record(dst)
    expected={p:sha(dst/p) for p in RESULTS}
    for p in RESULTS:(dst/p).unlink()
    a=run([sys.executable,'-B','work74/computations/trace_probe74.py','--output',RESULTS[0]],dst)
    require(a['exit_status']==0,'Primary did not complete: '+str(a))
    b=run([sys.executable,'-B','work74/computations/independent74.py','--certificate',RESULTS[0],'--output',RESULTS[1]],dst)
    require(b['exit_status']==0,'Separate checker did not complete: '+str(b))
    for p,h in expected.items():require(sha(dst/p)==h,'Regenerated output mismatch: '+p)
    cert=json.loads((dst/RESULTS[0]).read_text())
    mutations=[
      ('invented_actual_traces',lambda d:d['status'].__setitem__('actual_joint_word_traces_computed',True),'/status/actual_joint_word_traces_computed'),
      ('false_pattern_elimination',lambda d:d['status'].__setitem__('patterns_eliminated',8),'/status/patterns_eliminated'),
      ('erased_product_trace_signal',lambda d:d['controls']['same_individual_traces'].__setitem__('U1V_trace_mod343',2),'/controls/same_individual_traces/U1V_trace_mod343'),
      ('wrong_unit_count',lambda d:d['unit_basis'].__setitem__('unit_residues_checked',2304),'/unit_basis/unit_residues_checked'),
      ('wrong_leading_digit',lambda d:d['matrix_family']['examples'][0].__setitem__('leading',[0,0]),'/matrix_family/examples/0/leading/0'),
      ('dropped_depth',lambda d:d['controls']['wrong_depth_denominator'].__setitem__('delta',49),'/controls/wrong_depth_denominator/delta'),
      ('false_cyclotomic_kernel',lambda d:d['cyclotomic_cocycle_model'].__setitem__('H1_dimension',1),'/cyclotomic_cocycle_model/H1_dimension')]
    neg=[]
    for name,change,field in mutations:
        d=copy.deepcopy(cert);change(d);fp=tmp/'altered.json';fp.write_text(json.dumps(d));op=tmp/'bad_output.json'
        if op.exists():op.unlink()
        j=run([sys.executable,'-B','work74/computations/independent74.py','--certificate',str(fp),'--output',str(op)],dst)
        require(j['exit_status'] not in (0,None) and 'CERTIFICATE_MISMATCH '+field in j['stdout'],'Wrong mutation handling: '+name)
        require(not op.exists(),'Rejected certificate left scientific output')
        neg.append({'name':name,'rejected':True,'field':field,'execution':j})
    original=(dst/'README.md').read_bytes();(dst/'README.md').write_bytes(original+b'\nALTERED\n')
    j=run([sys.executable,'-B','verify.py','--integrity-only'],dst)
    require(j['exit_status'] not in (0,None) and 'Payload hash changed: README.md' in j['stdout'],'Payload corruption not rejected')
    neg.append({'name':'payload','rejected':True,'execution':j});(dst/'README.md').write_bytes(original)
    integrity(dst)
    return {'results_deleted_and_regenerated':RESULTS,'result_sha256':expected,'record_validation':record,'primary':a,'separate':b,'negative_controls':neg,'finite_counts':{'matrix_family':cert['matrix_family']['cases'],'unit_residues':cert['unit_basis']['unit_residues_checked'],'residue_pairs':cert['residue_reconstruction']['cases'],'patterns_eliminated':0}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path);p.add_argument('--integrity-only',action='store_true');p.add_argument('--replay-predecessor',action='store_true');a=p.parse_args()
    if a.report and a.report.resolve().is_relative_to(ROOT):p.error('Report must be outside immutable package')
    st=time.perf_counter();r={'schema':'beal.block74.execution.v1','status':'RUNNING','started_at':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Block74 finite checks; optional immediate Block73 default run is not a full historical replay','environment':{'python':sys.version,'platform':platform.platform(),'bytecode_disabled':True},'resources':{'scientific_command_timeout_seconds':90,'predecessor_timeout_seconds':180,'memory_limit_bytes':None},'proof_boundary':['Actual joint traces not numerically calculated.','Eight patterns remain.','Inherited geometry conditional.','No new Lean or independent mathematical review.']};code=0
    try:
        r['integrity_before']=integrity(ROOT)
        if not a.integrity_only:
            with tempfile.TemporaryDirectory(prefix='beal74_') as td:
                tmp=Path(td);r['scientific_replay']=science(ROOT,tmp)
                if a.replay_predecessor:
                    dest=tmp/'previous';dest.mkdir()
                    with zipfile.ZipFile(next((ROOT/'predecessor').glob('*.zip'))) as z:
                        for n in z.namelist():inside(dest,n)
                        z.extractall(dest)
                    roots=list(dest.glob('*/verify.py'));require(len(roots)==1,'Ambiguous predecessor')
                    pr=tmp/'Block73.json';job=run([sys.executable,'-B','verify.py','--report',str(pr)],roots[0].parent,180)
                    require(job['exit_status']==0 and pr.exists(),'Immediate predecessor failed')
                    data=json.loads(pr.read_text());require(data['status']=='PASS_DECLARED_CHECKS','Predecessor nonpass')
                    r['immediate_predecessor']={'full_historical_chain':False,'execution':job,'report':data}
        r['integrity_after']=integrity(ROOT);r['status']='PASS_INTEGRITY_ONLY' if a.integrity_only else 'PASS_DECLARED_CHECKS'
    except Exception as e:
        r['status']='FAILED';r['error']=type(e).__name__+': '+str(e);code=1;print(r['error'],file=sys.stderr)
    r['runtime_seconds']=time.perf_counter()-st;r['exit_status']=code
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(r['status'],f'{r["runtime_seconds"]:.3f}s');return code
if __name__=='__main__':raise SystemExit(main())
