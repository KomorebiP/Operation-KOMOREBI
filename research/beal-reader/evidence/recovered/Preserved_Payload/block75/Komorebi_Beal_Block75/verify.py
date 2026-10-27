#!/usr/bin/env python3
"""Replay Block75's declared finite assertions. No theorem or history inflation."""
from __future__ import annotations
import argparse,copy,datetime,hashlib,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCI=['work75/verification/integral75.json','work75/verification/independent75.json']
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')

def need(condition: bool, message: str) -> None:
    if not condition: raise ValueError(message)

def hash_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def safe(root: Path, name: str) -> Path:
    p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'unsafe path '+name)
    out=(root/p).resolve();need(out.is_relative_to(root.resolve()),'path escape');return out

def integrity(root: Path) -> dict:
    m=json.loads((root/'MANIFEST.json').read_text())
    need(m['schema']=='beal.block75.payload.v1','manifest schema')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(actual==set(m['files'])|{'MANIFEST.json'},'payload member set changed')
    for p,h in m['files'].items():need(hash_file(safe(root,p))==h,'payload hash mismatch '+p)
    pins=json.loads((root/'work75/source_records/INHERITED_INPUTS.json').read_text())
    pred=root/'predecessor'/pins['predecessor']
    need(hash_file(pred)==pins['predecessor_sha256'],'predecessor bytes changed')
    with zipfile.ZipFile(pred) as z:
        need(z.testzip() is None,'predecessor CRC failure')
        for row in pins['sources']:
            raw=z.read(row['member'])
            need(hashlib.sha256(raw).hexdigest()==row['sha256'],'pinned source hash mismatch')
            need((root/row['copy']).read_bytes()==raw,'copied source mismatch')
    # This is the declared project-local v1 evidence check, not the plugin validator.
    ev=json.loads((root/'work75/verification/COMPUTATION_MANIFEST.json').read_text())
    need(ev['schema_version']==1 and ev['run']['exit_status']==0,'science manifest status')
    need(ev['run']['runtime_seconds']>=0 and ev['mathematics']['non_claims'],'science manifest content')
    for row in ev['input_artifacts']:
        need(row['sha256']==row['sha256_after']==hash_file(safe(root,row['path'])),'execution input changed')
    for row in ev['outputs']:
        need(hash_file(safe(root,row['path']))==row['sha256'],'science output hash changed')
    return {'payload_hashes':len(m['files']),'immediate_pinned_source_leaves':len(pins['sources']),'predecessor_sha256':pins['predecessor_sha256'],'project_local_v1_execution_record':'validated as declared, not full plugin schema-v2'}

def run(cmd: list[str], cwd: Path, seconds: int=120) -> dict:
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,cwd=cwd,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=seconds)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError('INCONCLUSIVE_TIMEOUT: '+' '.join(cmd)) from exc
    return {'argv':cmd,'exit_status':p.returncode,'runtime_seconds':round(time.monotonic()-start,6),'stdout':p.stdout}

def unpack(archive: Path, target: Path) -> Path:
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();need(len(names)==len(set(names)),'duplicate archive entries')
        for name in names:safe(target,name)
        z.extractall(target)
    roots=[p for p in target.iterdir() if p.is_dir()]
    need(len(roots)==1,'ambiguous archive root');return roots[0]

def scientific(scratch: Path) -> dict:
    expected={p:(scratch/p).read_bytes() for p in SCI}
    for p in SCI:(scratch/p).unlink()
    a=run([sys.executable,'-B','work75/computations/integral75.py','--output',SCI[0]],scratch)
    need(a['exit_status']==0,'primary finite check failed '+a['stdout'])
    b=run([sys.executable,'-B','work75/computations/independent75.py','--certificate',SCI[0],'--output',SCI[1]],scratch)
    need(b['exit_status']==0,'separate finite check failed '+b['stdout'])
    for p in SCI:need((scratch/p).read_bytes()==expected[p],'complete scientific output mismatch '+p)
    cert=json.loads(expected[SCI[0]])
    edits=[('wrong_curve_composition_sign',['geometry','curve_map_composite_y_multiplier'],1),
           ('wrong_norm_minus_one_count',['norm_minus_one','49','count'],55),
           ('invented_actual_intertwiner',['status','actual_intertwiner_numerically_computed'],True),
           ('invented_labelled_trace',['status','actual_joint_word_traces_computed'],True),
           ('false_eight_pattern_exclusion',['status','patterns_eliminated'],8),
           ('ordinary_descent_shortcut',['controls','ordinary_descent_trace_mod343'],[2,0]),
           ('changed_mixed_trace_packet',['positive_packets','examples',0,'delta_mod343'],[0,0]),
           ('wrong_stable_endpoint',['lattice_segment','node_data',0,'invariant_lines'],[0,49])]
    negatives=[]
    with tempfile.TemporaryDirectory(prefix='beal75_bad_') as td:
        td=Path(td)
        for label,path,value in edits:
            bad=copy.deepcopy(cert);node=bad
            for p in path[:-1]:node=node[p]
            node[path[-1]]=value
            incoming=td/'altered.json';out=td/'invalid_output.json'
            incoming.write_text(json.dumps(bad));out.unlink(missing_ok=True)
            rec=run([sys.executable,'-B','work75/computations/independent75.py','--certificate',str(incoming),'--output',str(out)],scratch)
            marker='CERTIFICATE_MISMATCH /'+'/'.join(map(str,path))
            need(rec['exit_status']!=0 and marker in rec['stdout'] and not out.exists(),'corruption not rejected: '+label)
            negatives.append({'name':label,'rejected':True,'expected_mismatch':marker,'execution':rec})
    # Test package integrity on a changed scientific file, then restore exact bytes.
    p=scratch/SCI[0];saved=p.read_bytes();p.write_bytes(saved+b' ')
    caught=False
    try:integrity(scratch)
    except ValueError as exc:caught=('payload hash mismatch' in str(exc))
    finally:p.write_bytes(saved)
    need(caught,'modified payload accepted')
    negatives.append({'name':'modified_payload','rejected':True})
    return {'primary':a,'separate':b,'negative_controls':negatives,
            'finite_counts':{'positive_packets':cert['positive_packets']['cases'],'nonrational_intertwiner_packets':cert['positive_packets']['nonrational_intertwiner_cases'],'all_linear_maps':2401,'coefficient_directions':2304,'lattice_line_tests':2200,'patterns_eliminated':0},
            'complete_output_comparison':True}

def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path);ap.add_argument('--replay-predecessor',action='store_true');args=ap.parse_args()
    if args.report:need(not args.report.resolve().is_relative_to(ROOT),'report must be outside immutable package')
    start=time.monotonic();out={'schema':'beal.block75.execution.v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Block75 new finite assertions and nine corruption controls; optional immediate Block74 default only','environment':{'python':platform.python_version(),'platform':platform.platform(),'bytecode_disabled':True},'proof_boundary':['Conditional G1-G4 universal proofs','No actual C or labelled mixed trace numerically constructed','Eight patterns remain','No new Lean or independent mathematical reviewer']}
    try:
        out['integrity_before']=integrity(ROOT)
        with tempfile.TemporaryDirectory(prefix='beal75_verify_') as td:
            parent=Path(td);scratch=parent/'current';shutil.copytree(ROOT,scratch)
            out['scientific_replay']=scientific(scratch)
            if args.replay_predecessor:
                pins=json.loads((ROOT/'work75/source_records/INHERITED_INPUTS.json').read_text())
                pr=unpack(ROOT/'predecessor'/pins['predecessor'],parent/'prior')
                rpt=parent/'Block74_Current_Replay.json'
                rec=run([sys.executable,'-B','verify.py','--report',str(rpt)],pr,180)
                need(rec['exit_status']==0 and rpt.is_file(),'immediate predecessor execution failed')
                pd=json.loads(rpt.read_text());need(pd['status']=='PASS_DECLARED_CHECKS','predecessor result status')
                out['immediate_predecessor']={'execution':rec,'report':pd,'full_historical_chain':False}
            else:out['immediate_predecessor']={'run':False,'full_historical_chain':False}
        out['integrity_after']=integrity(ROOT);out['status']='PASS_DECLARED_CHECKS';out['exit_status']=0
    except Exception as exc:
        out['status']='INCONCLUSIVE_TIMEOUT' if isinstance(exc,TimeoutError) else 'FAILED'
        out['error']=str(exc);out['exit_status']=1
    out['runtime_seconds']=round(time.monotonic()-start,6)
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'],out['runtime_seconds'])
    if out['exit_status']:print(out.get('error','unknown failure'),file=sys.stderr)
    return out['exit_status']
if __name__=='__main__':raise SystemExit(main())
