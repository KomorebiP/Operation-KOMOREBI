#!/usr/bin/env python3
"""Reproduce finite assertions; an exit-code PASS is not a universal proof."""
from pathlib import Path
import hashlib,json,platform,shutil,subprocess,sys,time
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
P=R/'predecessor/komorebi_pnp_restoration_transport'
OUT=R/'results';LOG=R/'logs';OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def predecessor_check():
    seal=json.loads((P/'ARTIFACT_SEAL.json').read_text())
    for name,h in seal['files'].items():assert sha(P/name)==h,('predecessor drift',name)
    return len(seal['files'])
tracked=[R/'RESEARCH_NOTE.md',R/'README.md',R/'AUDIT.md',R/'GAP_LEDGER.md',*sorted((R/'checks').glob('*.py'))]
before={str(p.relative_to(R)):sha(p) for p in tracked}
manifest={'started_utc':now(),'status':'RUNNING','python':sys.version,'platform':platform.platform(),'arithmetic':'exact Boolean/GF2/integer','finite_scope':'specified in research note and result JSON','universal_proof_status':'written and self-reviewed, not formally verified','inputs_before':before,'runs':[],'predecessor_archive_sha256':'8af5cebdfca147f9643b936f1921267d644d0d7e59e79891241b8eaf54a86cde'}
try:
    manifest['predecessor_sealed_files']=predecessor_check()
    stage=OUT/'isolated_predecessor_clique';(stage/'checks').mkdir(exist_ok=True,parents=True);(stage/'results').mkdir(exist_ok=True)
    checker=stage/'checks/verify_clique_endpoint.py';shutil.copyfile(P/'checks/verify_clique_endpoint.py',checker)
    assert sha(checker)==sha(P/'checks/verify_clique_endpoint.py')
    commands=[('predecessor_restoration',[sys.executable,str(P/'checks/verify_restoration_transport.py'),'--out',str(OUT/'predecessor_replay')]),
              ('predecessor_clique',[sys.executable,str(checker)]),
              ('cut_comparison',[sys.executable,str(R/'checks/verify_cut_comparison.py')]),
              ('clique_packets',[sys.executable,str(R/'checks/verify_clique_packets.py')])]
    for name,argv in commands:
        t=time.perf_counter()
        completed=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=40)
        log=LOG/(name+'_final.log');log.write_text(completed.stdout+completed.stderr)
        manifest['runs'].append({'name':name,'argv':argv,'timeout_seconds':40,'exit_code':completed.returncode,'elapsed_seconds':time.perf_counter()-t,'log':str(log.relative_to(R)),'log_sha256':sha(log)})
        if completed.returncode:raise RuntimeError(name+' failed: '+completed.stderr[-1000:])
    assert json.loads((OUT/'predecessor_replay/verification.json').read_text())==json.loads((P/'results/verification.json').read_text())
    assert json.loads((stage/'results/clique_endpoint.json').read_text())==json.loads((P/'results/clique_endpoint.json').read_text())
    assert predecessor_check()==manifest['predecessor_sealed_files']
    after={str(p.relative_to(R)):sha(p) for p in tracked};assert before==after
    manifest['inputs_after']=after
    products=[OUT/'cut_comparison.json',OUT/'clique_packets.json',OUT/'predecessor_replay/verification.json',stage/'results/clique_endpoint.json']
    manifest['scientific_outputs']={str(p.relative_to(R)):sha(p) for p in products}
    manifest['status']='PASS'
except Exception as e:
    manifest['status']='FAILED';manifest['failure']=repr(e);raise
finally:
    manifest['finished_utc']=now();(R/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'runs':[(x['name'],x['elapsed_seconds']) for x in manifest['runs']]},indent=2))
