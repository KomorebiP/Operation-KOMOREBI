#!/usr/bin/env python3
"""Reproduce all five finite contracts and emit checked v2 evidence records."""
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

WORK=Path(__file__).resolve().parent
PACKAGE=WORK.parent

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=WORK/'computation_records'
    records.mkdir(exist_ok=True)
    definitions=[
        ('counting','PROOF.md','results.json',{'primitive_c_max':600,'allocation_n_max':500,'local_primes':[2,3,5,7,11,13],'local_terms':20}),
        ('quadratic','PROOF.md','verification.json',{'telescoping_n_max':3000,'H':[20,50,100,200],'Q_max':300,'perfect_power_k':[2,8],'perfect_power_Q':[1,200],'perfect_power_u':[2,80],'perfect_power_h_max':100000}),
        ('counterexample','PROOF.md','results.json',{'fixed_Q_k':[0,4],'prime_multiplier_p':[5,7,11,13,17,19,23,29,31],'varying_Q_t':[1,2],'filter':'q^t>=rad(p+1)'}),
        ('derivative','DERIVATIVE_ROUTE.md','results.json',{'b_c_cap':[[36,37,12],[48,49,8],[80,81,10],[108,109,108]]}),
        ('global','PROOF_NOTE.md','verification.json',{'A':[2,10],'B':'1<=B<A, gcd(A,B)=1','n':[1,12],'negative_control':[2,1,182,1093]})
    ]
    for name,proof,result,bounds in definitions:
        route=WORK/'routes'/name
        inputs=[route/'verify.py',route/proof,WORK/'reproduce.py']
        if name in ('counterexample','derivative'):
            inputs.append(WORK/'base/ABC_Square_Kernel_Reverse_Realization_2026-10-25/abc_square_kernel_bridge_20261025/PROOF_NOTE.md')
        before={p:digest(p) for p in inputs}
        result_path=route/result
        declared=[str(result_path.relative_to(WORK))]
        started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        tick=time.monotonic()
        command=[sys.executable,str(route/'verify.py')]
        run=subprocess.run(command,cwd=route if name=='global' else PACKAGE,capture_output=True,text=True,timeout=120)
        elapsed=time.monotonic()-tick
        log=records/(name+'.log')
        log.write_text(run.stdout+run.stderr)
        after={p:digest(p) for p in inputs}
        changed=before!=after
        status='failed' if run.returncode else 'inputs-changed' if changed else 'completed' if result_path.is_file() else 'result-missing'
        outputs=[{'path':str(log.relative_to(WORK)),'sha256':digest(log),'kind':'log'}]
        if result_path.is_file():
            data=json.loads(result_path.read_text())
            outputs.append({'path':declared[0],'sha256':digest(result_path),'kind':'result'})
        else:
            data={}
        manifest={
            'schema_version':2,'claim_id':'ABC-RR2-'+name,
            'repository':{'commit':'unavailable: content-addressed archive checkpoint f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59','dirty':True},
            'command':command,
            'working_directory':str(route if name=='global' else PACKAGE),
            'environment':{'software':[{'name':'Python','version':platform.python_version()}],'hardware':platform.machine()+'; '+platform.platform()+'; available CPUs '+str(os.cpu_count())},
            'mathematics':{'assertion_tested':data.get('assertion_tested',data.get('interpretation','Exact finite consistency checks as specified in route proof.')),'coefficient_domain':'Exact integers and rational numbers','conventions':'rad(1)=1; ordered positive primitive triples; no random sampling; quality 1/10 checked with integer powers where specified.','inputs':[str(p.relative_to(WORK)) for p in inputs],'bounds':bounds,'non_claims':['No proof or disproof of unrestricted ABC.','No asymptotic theorem is inferred from finite examples.','No Lean kernel verification or historical novelty assessment.']},
            'randomness':{'used':False,'generator':'none','seed':None},
            'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':run.returncode,'status':status,'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'wall_timeout_seconds':120},
            'outputs':outputs,'checks':['Source reviewed against the stated finite contract.','Input hashes observed before and after execution.','Exact arithmetic and deterministic bounded domains.'],
            'result':'Finite assertions passed in the stated domain.' if status=='completed' else 'Execution requires review: '+status,
            'residual_risks':['Written universal proofs require mathematical review independently of these finite computations.','Base checkpoint uses a content hash instead of a Git revision.'],
            'input_artifacts':[{'path':str(p.relative_to(WORK)),'sha256':before[p],'sha256_after':after[p]} for p in inputs],
            'declared_results':declared
        }
        (records/(name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
        print(name+': '+status,flush=True)
        if status!='completed':
            return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
