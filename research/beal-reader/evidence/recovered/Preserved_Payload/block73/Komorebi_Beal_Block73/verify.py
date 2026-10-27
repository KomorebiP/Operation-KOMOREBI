#!/usr/bin/env python3
"""Rebuild Block73 finite evidence. Not a Lean or global Diophantine proof checker."""
from __future__ import annotations
import argparse,copy,datetime as dt,hashlib,io,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESULTS=['work73/verification/deformation73.json','work73/verification/independent73.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(test,message):
    if not test:raise ValueError(message)
def safe(root,name):
    p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'Unsafe path')
    q=(root/p).resolve();need(q.is_relative_to(root.resolve()),'Escaping path');return q

def integrity(root):
    manifest=json.loads((root/'MANIFEST.json').read_text());payloads=manifest['payloads']
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    need(actual==set(payloads)|{'MANIFEST.json'},'Payload member set changed')
    for n,h in payloads.items():need(sha(safe(root,n))==h,'Payload hash changed: '+n)
    pred=next((root/'predecessor').glob('*.zip'));record=json.loads((root/'work73/source_records/INHERITED_INPUTS.json').read_text())
    need(sha(pred)==record['predecessor_sha256'],'Predecessor hash mismatch')
    cache={():pred.read_bytes()};depth=1
    for row in record['sources']:
        k=()
        for link in row['archive_chain']:
            nxt=k+(link,)
            if nxt not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[k])) as z:cache[nxt]=z.read(link)
            k=nxt
        with zipfile.ZipFile(io.BytesIO(cache[k])) as z:b=z.read(row['archive_member'])
        need(hashlib.sha256(b).hexdigest()==row['sha256'],'Inherited hash mismatch')
        need((root/row['copy']).read_bytes()==b,'Inherited copy mismatch');depth=max(depth,len(k)+1)
    d=json.loads((root/'work73/inputs/B72_B71_B70_refinement70.json').read_text())
    need(len(d['survivors'])==8,'Wrong frozen count')
    need(all(t['inertia'][t['columns'].index(883)] for t in d['survivors']),'Missing mandatory883 inertia')
    return {'payloads':len(payloads),'source_leaves':len(record['sources']),'deepest_archive_level':depth,'predecessor_sha256':sha(pred),'frozen_pattern_count':8}

def record_check(root):
    # Project-local v2 validation, explicitly not represented as running the plugin validator.
    m=json.loads((root/'work73/verification/COMPUTATION_MANIFEST.json').read_text())
    need(m['schema_version']==2 and m['run']['status']=='completed' and m['run']['exit_status']==0,'Invalid completed record')
    need(m['run']['runtime_seconds']>=0 and bool(m['mathematics']['non_claims']),'Missing scope')
    need(set(m['execution_artifacts'])=={x['path'] for x in m['input_artifacts']},'Bad execution input set')
    for a in m['input_artifacts']:need(a['sha256']==a['sha256_after']==sha(safe(root,a['path'])),'Changed recorded input')
    need(set(m['declared_results'])==set(RESULTS),'Bad declared results')
    for a in m['outputs']:need(sha(safe(root,a['path']))==a['sha256'],'Changed recorded output')
    for j in m['run']['commands']:need(j['exit_status']==0 and j['runtime_seconds']>=0,'Bad recorded scientific execution')
    return {'schema_version':2,'validator':'project-local field/hash checks','inputs_checked':len(m['input_artifacts']),'outputs_checked':len(m['outputs']),'passed':True}

def execute(args,cwd,limit=180):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    t=time.perf_counter()
    try:
        p=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=limit)
        return {'argv':args,'status':'completed','exit_status':p.returncode,'runtime_seconds':time.perf_counter()-t,'stdout':p.stdout}
    except subprocess.TimeoutExpired as e:
        s=e.stdout or '';s=s.decode(errors='replace') if isinstance(s,bytes) else s
        return {'argv':args,'status':'timeout','exit_status':None,'runtime_seconds':time.perf_counter()-t,'stdout':s}

def science(root,tmp):
    dst=tmp/'scratch';shutil.copytree(root,dst);record=record_check(dst)
    expected={p:sha(dst/p) for p in RESULTS}
    for p in RESULTS:(dst/p).unlink()
    primary=execute([sys.executable,'-B','work73/computations/deformation73.py','--output',RESULTS[0]],dst)
    need(primary['exit_status']==0,'Primary run failed: '+str(primary))
    secondary=execute([sys.executable,'-B','work73/computations/independent73.py','--certificate',RESULTS[0],'--output',RESULTS[1]],dst)
    need(secondary['exit_status']==0,'Separate run failed: '+str(secondary))
    for p,h in expected.items():need(sha(dst/p)==h,'Regenerated output differs: '+p)
    data=json.loads((dst/RESULTS[0]).read_text())
    mutations=[
     ('false_883_power',lambda x:x['arithmetic']['seventh_symbols'].__setitem__('7',[1,0]),'/arithmetic/seventh_symbols/7'),
     ('false_mod343_lift',lambda x:x['delayed_control'].__setitem__('mod343_extension_possible',True),'/delayed_control/mod343_extension_possible'),
     ('zero_tame_defect',lambda x:x['delayed_control'].__setitem__('tame_defect_mod343',[0,0,0,0]),'/delayed_control/tame_defect_mod343'),
     ('false_eight_elimination',lambda x:x['arithmetic'].__setitem__('patterns_eliminated',8),'/arithmetic/patterns_eliminated'),
     ('free_uniformizer',lambda x:x['arithmetic']['admissible_phi_7_pairs'].append([0,1]),'/arithmetic/admissible_phi_7_pairs'),
     ('all_shifts_lift',lambda x:x['tame'].__setitem__('accepted_upper_shifts',115248),'/tame/accepted_upper_shifts'),
     ('zero_valuation',lambda x:x['arithmetic'].__setitem__('fixed7_target_example_v3_c1_epsilon_minus',0),'/arithmetic/fixed7_target_example_v3_c1_epsilon_minus')]
    negatives=[]
    for name,alter,field in mutations:
        bad=copy.deepcopy(data);alter(bad);path=tmp/'bad.json';path.write_text(json.dumps(bad));out=tmp/'bad_out.json'
        if out.exists():out.unlink()
        j=execute([sys.executable,'-B','work73/computations/independent73.py','--certificate',str(path),'--output',str(out)],dst)
        need(j['exit_status'] not in (0,None) and 'CERTIFICATE_MISMATCH '+field in j['stdout'],'Mutation not properly rejected: '+name)
        need(not out.exists(),'Invalid certificate emitted a result')
        negatives.append({'name':name,'rejected':True,'expected_field':field,'execution':j})
    old=(dst/'README.md').read_bytes();(dst/'README.md').write_bytes(old+b'\nCORRUPTED\n')
    j=execute([sys.executable,'-B','verify.py','--integrity-only'],dst)
    need(j['exit_status'] not in (0,None) and 'Payload hash changed: README.md' in j['stdout'],'Payload corruption not rejected')
    negatives.append({'name':'payload','rejected':True,'execution':j});(dst/'README.md').write_bytes(old)
    integrity(dst)
    return {'results_deleted_and_regenerated':RESULTS,'result_hashes':expected,'primary':primary,'separate':secondary,
      'project_local_record_validation':record,'negative_controls':negatives,
      'finite_summary':{'adjoint':data['adjoint'],'tame':data['tame'],'local_packets':data['arithmetic']['local_positive_packet_checks'],'patterns_eliminated':data['arithmetic']['patterns_eliminated']}}

def main():
    a=argparse.ArgumentParser();a.add_argument('--report',type=Path);a.add_argument('--integrity-only',action='store_true');a.add_argument('--replay-predecessor',action='store_true');args=a.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):a.error('Report must be outside package')
    t=time.perf_counter();r={'schema':'beal.block73.execution.v1','status':'RUNNING','started_at':dt.datetime.now(dt.timezone.utc).isoformat(),
       'environment':{'python':sys.version,'platform':platform.platform(),'bytecode_disabled':True},
       'scope':'New Block73 finite assertions. Optional immediate Block72 default replay is not the full history.',
       'resources':{'per_scientific_command_wall_seconds':180,'immediate_predecessor_wall_seconds':300,'memory_limit_bytes':None},
       'proof_boundary':['Conditional on inherited actual geometry.','No pattern elimination.','No new Lean or independent mathematical review.']}
    code=0
    try:
        r['integrity_before']=integrity(ROOT)
        if not args.integrity_only:
            with tempfile.TemporaryDirectory(prefix='beal73_') as td:
                tmp=Path(td);r['scientific_replay']=science(ROOT,tmp)
                if args.replay_predecessor:
                    pred=next((ROOT/'predecessor').glob('*.zip'));target=tmp/'previous';target.mkdir()
                    with zipfile.ZipFile(pred) as z:
                        for n in z.namelist():safe(target,n)
                        z.extractall(target)
                    roots=list(target.glob('*/verify.py'));need(len(roots)==1,'Wrong predecessor root')
                    pr=tmp/'Block72.json';job=execute([sys.executable,'-B','verify.py','--report',str(pr)],roots[0].parent,300)
                    need(job['exit_status']==0 and pr.exists(),'Predecessor did not complete')
                    report=json.loads(pr.read_text());need(report['status']=='PASS_DECLARED_CHECKS','Predecessor nonpass')
                    r['immediate_predecessor']={'full_historical_chain':False,'execution':job,'report':report}
        r['integrity_after']=integrity(ROOT);r['status']='PASS_INTEGRITY_ONLY' if args.integrity_only else 'PASS_DECLARED_CHECKS'
    except Exception as e:
        r['status']='FAILED';r['error']=type(e).__name__+': '+str(e);code=1;print(r['error'],file=sys.stderr)
    r['runtime_seconds']=time.perf_counter()-t;r['exit_status']=code
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(r['status'],f'{r["runtime_seconds"]:.3f}s');return code
if __name__=='__main__':raise SystemExit(main())
