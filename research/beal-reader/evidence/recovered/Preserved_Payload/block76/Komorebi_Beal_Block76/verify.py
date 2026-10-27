#!/usr/bin/env python3
"""Fresh finite replay and integrity controls. Not an arithmetic proof checker."""
from __future__ import annotations
import argparse,copy,datetime,hashlib,io,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
SCI=['work76/verification/image76.json','work76/verification/independent76.json']
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def safe(root,s):
    p=Path(s);need(not p.is_absolute() and '..' not in p.parts,'unsafe relative path')
    t=(root/p).resolve();need(t.is_relative_to(root.resolve()),'path escape');return t
def check_integrity(root):
    m=json.loads((root/'MANIFEST.json').read_text());need(m['schema']=='beal.block76.payload.v1','manifest schema')
    paths={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(paths==set(m['files'])|{'MANIFEST.json'},'payload member set changed')
    for f,h in m['files'].items():need(digest(safe(root,f))==h,'payload hash mismatch '+f)
    pins=json.loads((root/'work76/source_records/INHERITED_INPUTS.json').read_text());pred=root/'predecessor'/pins['predecessor']
    need(digest(pred)==pins['predecessor_sha256'],'predecessor changed')
    with zipfile.ZipFile(pred) as z:need(z.testzip() is None,'predecessor CRC')
    depth=1
    for item in pins['sources']:
        z=zipfile.ZipFile(pred)
        try:
            for child in item['archive_chain']:
                raw=z.read(child);z.close();z=zipfile.ZipFile(io.BytesIO(raw))
            raw=z.read(item['member'])
        finally:z.close()
        need(hashlib.sha256(raw).hexdigest()==item['sha256'],'inherited hash mismatch')
        need((root/item['copy']).read_bytes()==raw,'inherited copy mismatch')
        depth=max(depth,1+len(item['archive_chain']))
    ev=json.loads((root/'work76/verification/COMPUTATION_MANIFEST.json').read_text())
    # Explicit project-local legacy-schema check. Not the installed skill validator.
    need(ev['schema_version']==1 and ev['run']['exit_status']==0,'execution manifest')
    need(ev['mathematics']['non_claims'] and ev['run']['runtime_seconds']>=0,'manifest limits')
    for item in ev['input_artifacts']:
        need(item['sha256']==item['sha256_after']==digest(root/item['path']),'science source changed')
    for item in ev['outputs']:need(item['sha256']==digest(root/item['path']),'science output changed')
    return {'payload_hashes':len(m['files']),'pinned_source_leaves':len(pins['sources']),'archive_levels_traversed':depth,'predecessor_sha256':pins['predecessor_sha256'],'execution_record':'project-local schema-v1 validation only'}
def run(argv,cwd,seconds=120):
    t=time.monotonic()
    try:p=subprocess.run(argv,cwd=cwd,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=seconds)
    except subprocess.TimeoutExpired as e:raise TimeoutError('INCONCLUSIVE_TIMEOUT '+repr(argv)) from e
    return {'argv':argv,'exit_status':p.returncode,'runtime_seconds':round(time.monotonic()-t,6),'stdout':p.stdout}
def science(scratch,parent):
    before={f:(scratch/f).read_bytes() for f in SCI}
    expected=json.loads(before[SCI[0]])
    edits=[
      ('incorrect_first_layer_rank',['first_layer','nonzero_lower_seed_ranks',0,1],4),
      ('incorrect_second_layer_dimension',['second_layer','dimension'],5),
      ('incorrect_mod343_order',['cyclotomic_image_orders','1',2,'order'],7**12),
      ('incorrect_abelianization',['abelianization','orders','1'],2401),
      ('invented_pattern_exclusion',['proof_status','arithmetic_patterns_eliminated'],8),
      ('invented_labelled_trace',['proof_status','actual_labelled_mixed_trace_computed'],True),
      ('corrupt_commutator_certificate',['second_layer','commutator_hash'],'0'*64),
      ('false_full_first_kernel',['first_layer','allowed_counts','F7'],117649),
    ]
    negatives=[]
    for i,(label,path,value) in enumerate(edits):
        bad=copy.deepcopy(expected);node=bad
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        loc=parent/f'bad_{i}.json';loc.write_text(json.dumps(bad))
        negatives.append({'name':label,'certificate':str(loc),'expected_path':'/'+'/'.join(map(str,path))})
    incoming=parent/'negative_inputs.json';incoming.write_text(json.dumps(negatives));negative_report=parent/'negative_results.json'
    for f in SCI:(scratch/f).unlink()
    primary=run([sys.executable,'-B','work76/computations/image76.py','--output',SCI[0]],scratch)
    need(primary['exit_status']==0,'primary failed '+primary['stdout'])
    second=run([sys.executable,'-B','work76/computations/check76.py','--certificate',SCI[0],'--output',SCI[1],'--negative-set',str(incoming),'--negative-report',str(negative_report)],scratch)
    need(second['exit_status']==0,'separate checker failed '+second['stdout'])
    for f in SCI:need((scratch/f).read_bytes()==before[f],'scientific full-output mismatch '+f)
    neg=json.loads(negative_report.read_text());need(len(neg)==8 and all(i['rejected'] for i in neg),'negative audit failed')
    file=scratch/SCI[0];saved=file.read_bytes();file.write_bytes(saved+b' ');caught=False
    try:check_integrity(scratch)
    except ValueError as e:caught='payload hash mismatch' in str(e)
    finally:file.write_bytes(saved)
    need(caught,'corrupted payload accepted');neg.append({'name':'modified_payload','rejected':True})
    return {'primary':primary,'separate':second,'negative_controls':neg,'full_output_comparison':True,'counts':{'first_layer_seeds':expected['first_layer']['matrix_seeds'],'first_layer_identity_instances':expected['first_layer']['identity_instances'],'second_layer_commutators':expected['second_layer']['commutator_instances'],'derived_commutators':expected['abelianization']['derived_commutator_instances'],'power_instances':expected['power_propagation']['instances'],'mixed_trace_controls':expected['mixed_trace_controls']['instances'],'patterns_eliminated':0}}
def unpack(src,dst):
    dst.mkdir()
    with zipfile.ZipFile(src) as z:
        need(z.testzip() is None,'ZIP CRC');names=z.namelist();need(len(names)==len(set(names)),'duplicate member')
        for n in names:safe(dst,n)
        z.extractall(dst)
    roots=list(dst.iterdir());need(len(roots)==1 and roots[0].is_dir(),'ambiguous root');return roots[0]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path);ap.add_argument('--replay-predecessor',action='store_true');a=ap.parse_args()
    if a.report:need(not a.report.resolve().is_relative_to(ROOT),'report must be outside immutable package')
    start=time.monotonic();report={'schema':'beal.block76.execution.v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Block76 two finite programs and nine corruption controls; optional one immediate Block75 DEFAULT','environment':{'python':platform.python_version(),'platform':platform.platform(),'bytecode_disabled':True},'proof_boundary':['Universal image and field conclusions require the written proofs and named arithmetic inputs','No actual labelled Galois map constructed','Eight patterns remain','No new Lean or independent mathematical review']}
    try:
        report['integrity_before']=check_integrity(ROOT)
        with tempfile.TemporaryDirectory(prefix='beal76_verify_') as d:
            parent=Path(d);scratch=parent/'current';shutil.copytree(ROOT,scratch)
            report['scientific_replay']=science(scratch,parent)
            report['immediate_predecessor']={'run':False,'full_historical_chain':False}
            if a.replay_predecessor:
                pins=json.loads((ROOT/'work76/source_records/INHERITED_INPUTS.json').read_text())
                pred=unpack(ROOT/'predecessor'/pins['predecessor'],parent/'previous')
                rpt=parent/'Block75_Default.json';rec=run([sys.executable,'-B','verify.py','--report',str(rpt)],pred,180)
                need(rec['exit_status']==0 and rpt.is_file(),'predecessor failure '+rec['stdout'])
                parsed=json.loads(rpt.read_text());need(parsed['status']=='PASS_DECLARED_CHECKS','predecessor status')
                report['immediate_predecessor']={'run':True,'execution':rec,'report':parsed,'full_historical_chain':False}
        report['integrity_after']=check_integrity(ROOT);report['status']='PASS_DECLARED_CHECKS';report['exit_status']=0
    except Exception as e:
        report['status']='INCONCLUSIVE_TIMEOUT' if isinstance(e,TimeoutError) else 'FAILED';report['exit_status']=1;report['error']=str(e)
    report['runtime_seconds']=round(time.monotonic()-start,6)
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(report['status'],report['runtime_seconds'])
    if report['exit_status']:print(report.get('error','unknown error'),file=sys.stderr)
    return report['exit_status']
if __name__=='__main__':raise SystemExit(main())
