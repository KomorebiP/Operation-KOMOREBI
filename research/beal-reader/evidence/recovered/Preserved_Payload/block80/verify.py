#!/usr/bin/env python3
"""Replay Block80 finite assertions, pinned provenance, and negative controls.
This is not a proof assistant and does not evaluate an actual arithmetic affine origin.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,io,json,os,shutil,subprocess,sys,tempfile,time,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESULTS=['primary80.json','independent80.json','independent80_extra.json','target_evaluator80.json']
PREHASH='54fc40812f5590f3215c8c643ceedbd3c49ca13b58854fadb6bb3088fa8da40e'

def check(v,msg):
    if not v:raise ValueError(msg)
def digest(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return digest(Path(p).read_bytes())
def load(path):return json.loads(Path(path).read_text())
def safe_names(z):
    names=z.namelist();check(len(names)==len(set(names)),'duplicate ZIP member')
    for n in names:
        p=Path(n);check(not p.is_absolute() and '..' not in p.parts,'unsafe archive member')
    return names

def integrity(root):
    m=load(root/'MANIFEST.json');excluded={'MANIFEST.json'}
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    check(actual==set(m['payload'])|excluded,'unexpected/missing payload file')
    for name,h in m['payload'].items():check(filehash(root/name)==h,'payload checksum: '+name)
    return len(m['payload'])

def provenance(root):
    pins=load(root/'work80/source_records/INHERITED_INPUTS.json')
    pre=root/'predecessor'/pins['predecessor'];raw=pre.read_bytes()
    check(digest(raw)==PREHASH==pins['sha256'],'predecessor bytes changed')
    seen=0;maxdepth=max(e['depth_in_predecessor'] for e in pins['leaves'])
    for depth in range(maxdepth+1):
        z=zipfile.ZipFile(io.BytesIO(raw));names=safe_names(z);ah=digest(raw)
        for e in pins['leaves']:
            if e['depth_in_predecessor']==depth:
                check(e['archive_sha256']==ah,'nested ancestor checksum')
                check(e['member'] in names,'pinned member missing')
                b=z.read(e['member']);check(digest(b)==e['sha256'],'source leaf changed')
                check((root/e['copy']).read_bytes()==b,'copied source is not exact');seen+=1
        if depth<maxdepth:
            ps=[n for n in names if n.endswith('.zip') and 'predecessor/' in n]
            check(len(ps)==1,'ambiguous predecessor chain');raw=z.read(ps[0])
    return {'pinned_leaves':seen,'archive_levels_inspected':maxdepth+1,'predecessor_sha256':PREHASH}

def invoke(argv,cwd,timeout=120):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    t=time.monotonic();p=subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
    check(p.returncode==0,'command failed: '+str(argv)+'\n'+p.stdout+'\n'+p.stderr)
    return {'argv':argv,'runtime_seconds':round(time.monotonic()-t,6),'exit_status':p.returncode,'stdout':p.stdout,'stderr':p.stderr}

def scientific_checks(d):
    check(d['status']=='PASS_FINITE_ASSERTIONS','bad result status')
    for lab,p in d['patterns'].items():
        kdim=2 if lab=='C' else 3
        check(p['homogeneous_dimension_over_k']==kdim,'incorrect tangent dimension')
        check(p['rank']==10-kdim,'incorrect rank')
        check(p['affine_obstruction_dimension_over_k']==5+kdim,'incorrect affine dimension')
        check(not p['actual_affine_target_computed'] and not p['particular_cochain_computed'],'invented arithmetic origin')
        check(p['common_semilinear_bound_if_nonempty']==7**kdim,'wrong same-frame bound')
    check(d['local_phi_log_w']==[0,5],'lost local unit witness')

def same(a,b):check(a==b,'scientific outputs disagree')

def negative_controls(root,expected,evalmodule):
    passed=[]
    def rejected(label,fn):
        try:fn()
        except (ValueError,ArithmeticError,KeyError,AssertionError):passed.append(label)
        else:raise ValueError('negative control accepted: '+label)
    def changed(mut):
        v=copy.deepcopy(expected);mut(v);return v
    rejected('wrong_self_conductor_value',lambda:same(changed(lambda d:d['beta_uniformizer_rows_over_Q']['197'].__setitem__(0,(d['beta_uniformizer_rows_over_Q']['197'][0]+1)%7)),expected))
    rejected('lost_degree_two_column',lambda:same(changed(lambda d:d['residue_data'].pop('307')),expected))
    rejected('unconverted_beta_inertia',lambda:same(changed(lambda d:d['residue_data']['197'].__setitem__('beta_inertia_scale',1)),expected))
    rejected('false_affine_origin',lambda:scientific_checks(changed(lambda d:d['patterns']['A'].__setitem__('actual_affine_target_computed',True))))
    rejected('old_C_dimension_promoted',lambda:scientific_checks(changed(lambda d:d['patterns']['C'].__setitem__('homogeneous_dimension_over_k',4))))
    rejected('phi_local_witness_erased',lambda:scientific_checks(changed(lambda d:d.__setitem__('local_phi_log_w',[0,0]))))
    rejected('invalid_target_encoding',lambda:evalmodule.evaluate({'pattern':'A','kind':'synthetic','basis':evalmodule.BASIS,'provenance':'negative control','target':[0]*14+[49]},expected))
    target=expected['patterns']['A']['synthetic_nonimage_target']
    actual=evalmodule.evaluate({'pattern':'A','kind':'synthetic','basis':evalmodule.BASIS,'provenance':'nonimage control','target':target},expected)
    rejected('nonimage_target_declared_solved',lambda:check(actual['linear_target_in_image'],'nonimage retained'))
    with tempfile.TemporaryDirectory(prefix='beal80_tamper_') as tmp:
        altered=Path(tmp)/'package';shutil.copytree(root,altered)
        p=altered/'work80/verification/primary80.json';p.write_bytes(p.read_bytes()+b' ')
        rejected('modified_payload',lambda:integrity(altered))
    check(len(passed)==9,'negative-control coverage')
    return passed

def replay(predecessor=False):
    started=datetime.now(timezone.utc).isoformat();begin=time.monotonic()
    cnt=integrity(ROOT);pins=provenance(ROOT);runs=[]
    scientific=[ROOT/'work80/computations'/n for n in ['build_inputs.py','primary80.py','independent80.py','evaluate_target.py']]
    input_paths=scientific+sorted((ROOT/'work80/inputs').glob('*'))
    before={str(p.relative_to(ROOT)):filehash(p) for p in input_paths}
    expected={n:load(ROOT/'work80/verification'/n) for n in RESULTS}
    with tempfile.TemporaryDirectory(prefix='beal80_rebuild_') as td:
        scratch=Path(td)/'package'
        shutil.copytree(ROOT/'work80',scratch/'work80')
        for n in RESULTS:(scratch/'work80/verification'/n).unlink()
        (scratch/'work80/inputs/finite_inputs.json').unlink()
        for script,args in [('build_inputs.py',[]),('primary80.py',[]),('independent80.py',[]),('evaluate_target.py',['--self-test'])]:
            runs.append(invoke([sys.executable,'-B','work80/computations/'+script]+args,scratch))
        check((scratch/'work80/inputs/finite_inputs.json').read_bytes()==(ROOT/'work80/inputs/finite_inputs.json').read_bytes(),'rebuilt fixture mismatch')
        for n in RESULTS:same(load(scratch/'work80/verification'/n),expected[n])
    same(expected['primary80.json'],expected['independent80.json']);scientific_checks(expected['primary80.json'])
    sp=importlib.util.spec_from_file_location('block80_target_eval',ROOT/'work80/computations/evaluate_target.py')
    em=importlib.util.module_from_spec(sp);sp.loader.exec_module(em)
    controls=negative_controls(ROOT,expected['primary80.json'],em)
    manifest_check=invoke([sys.executable,'-B','work80/computations/validate_manifest_v1.py','work80/verification/COMPUTATION_MANIFEST.json','--root','.'],ROOT)
    previous=None
    if predecessor:
        pre=next((ROOT/'predecessor').glob('*.zip'))
        with tempfile.TemporaryDirectory(prefix='beal80_predecessor_') as td:
            d=Path(td)
            with zipfile.ZipFile(pre) as z:safe_names(z);z.extractall(d)
            candidates=list(d.rglob('verify.py'));check(len(candidates)==1,'predecessor verifier ambiguity')
            pr=candidates[0].parent;out=d.parent/(d.name+'_report.json')
            try:
                run=invoke([sys.executable,'-B','verify.py','--report',str(out)],pr,timeout=120)
                previous={'invocation':run,'report':load(out)}
                check(previous['report']['status']=='PASS_DECLARED_CHECKS','predecessor status failed')
            finally:out.unlink(missing_ok=True)
    after={str(p.relative_to(ROOT)):filehash(p) for p in input_paths};check(before==after,'input changed during execution')
    return {'status':'PASS_DECLARED_CHECKS','version':'8.0.0','started_at':started,'runtime_seconds':round(time.monotonic()-begin,6),'exit_status':0,
      'proof_status':'written proofs with inherited and classical inputs; not Lean or independent mathematical review',
      'payload_count':cnt,'provenance':pins,'scientific_runs':runs,'scientific_results_regenerated':RESULTS,
      'fixture_regenerated':True,'project_v1_manifest_validation':manifest_check,'negative_controls_rejected':controls,'immediate_predecessor':previous,
      'full_historical_chain_replayed':False,'input_hashes_before':before,'input_hashes_after':after,
      'results':{'bare_restricted_primitive':'existence proved in notes, not pointwise computed',
                 'actual_affine_targets_computed':False,'patterns_eliminated':0,
                 'tangent_dimensions':[3,3,2,3],'affine_obstruction_dimensions':[8,8,7,8]}}

def main():
    pa=argparse.ArgumentParser(description=__doc__);pa.add_argument('--report',type=Path,required=True);pa.add_argument('--replay-predecessor',action='store_true');args=pa.parse_args()
    try:
        report=replay(args.replay_predecessor);args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['runtime_seconds'])
    except Exception as e:
        print('FAILED:',type(e).__name__,str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
