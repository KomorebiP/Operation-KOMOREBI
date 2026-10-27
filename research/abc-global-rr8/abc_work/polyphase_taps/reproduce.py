#!/usr/bin/env python3
"""Reproduce three bounded polyphase and tap contracts with v2 evidence records."""
import datetime,hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
PACKAGE=WORK.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=HERE/'computation_records'
    records.mkdir(exist_ok=True)
    specs=[('refinement', 'PROOF_NOTE.md', 'verification.json', {'grid_A': [2, 8], 'grid_B': '1<=B<A,gcd(A,B)=1', 'grid_n': [1, 12], 'M': 'all divisors of n', 'nested_radices': [2, 3, 5], 'nested_depth': [0, 3], 'phase_index': 'all residues', 'phase_t': [0, 24], 'contact_depth': '1 through birth+2; n0 excluded'}), ('taps', 'PROOF_NOTE.md', 'verification.json', {'gcd_A': [2, 8], 'B': '1<=B<A,gcd(A,B)=1', 'n': '1 through 12', 'other_tests': 'Exact listed gcd, half-order, moments, preserving tap and physical convolution grids in verify.py'}), ('multichannel', 'PROOF.md', 'results.json', {'p': 17, 'contact_A_power': 8, 'depths': [1, 8], 'matrix_entries': [-3, 3], 'matrix_dimension': [2, 2], 'matrix_filter': 'nonzero determinant', 'vectors_per_depth': 3})]
    base=WORK/'routes/global/PROOF_NOTE.md'
    for name,proof,result,bounds in specs:
        route=HERE/'routes'/('cyclotomic' if name=='order_budget' else name)
        verifier=route/('verify_order_budget.py' if name=='order_budget' else 'verify.py')
        inputs=[verifier,route/proof,HERE/'reproduce.py',base,WORK/'roots_unity/LATEST.md']
        before={p:sha(p) for p in inputs}
        output=route/result
        declared=[str(output.relative_to(WORK))]
        command=[sys.executable,str(verifier)]
        cwd=route if name=='refinement' else PACKAGE
        started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        tick=time.monotonic()
        run=subprocess.run(command,cwd=cwd,capture_output=True,text=True,timeout=120)
        runtime=time.monotonic()-tick
        log=records/(name+'.log')
        log.write_text(run.stdout+run.stderr)
        after={p:sha(p) for p in inputs}
        status='failed' if run.returncode else 'inputs-changed' if before!=after else 'completed' if output.is_file() else 'result-missing'
        data=json.loads(output.read_text()) if output.is_file() else {}
        outputs=[{'path':str(log.relative_to(WORK)),'sha256':sha(log),'kind':'log'}]
        if output.is_file():outputs.append({'path':declared[0],'sha256':sha(output),'kind':'result'})
        manifest={
            'schema_version':2,'claim_id':'ABC-RR4-'+name,
            'repository':{'commit':'unavailable; parent archive 557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302','dirty':True},
            'command':command,'working_directory':str(cwd),
            'environment':{'software':[{'name':'Python','version':platform.python_version()}],'hardware':platform.machine()+'; '+platform.platform()+'; available CPUs '+str(os.cpu_count())},
            'mathematics':{'assertion_tested':data.get('assertion_tested','Exact bounded identities and negative controls in route proof.'),'coefficient_domain':'Exact integers, modular rings, and rational numbers','conventions':'Odd valuation primes; positive coprime bases A>B>=1; roots represented by exact modular residues, never floating complex approximations.','inputs':[str(p.relative_to(WORK)) for p in inputs],'bounds':bounds,'non_claims':['No proof or disproof of unrestricted ABC.','No general distribution or uniform-height bound from finite examples.','No Lean compilation or historical priority assessment.']},
            'randomness':{'used':False,'generator':'none','seed':None},
            'run':{'started_at':started,'runtime_seconds':runtime,'exit_status':run.returncode,'status':status,'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'wall_timeout_seconds':120},
            'outputs':outputs,'declared_results':declared,
            'input_artifacts':[{'path':str(p.relative_to(WORK)),'sha256':before[p],'sha256_after':after[p]} for p in inputs],
            'checks':['Source inspected against the displayed finite contract.','Exact arithmetic and deterministic stated domains.','Execution inputs hashed before and after.'],
            'result':'Finite assertions passed in the stated domain.' if status=='completed' else 'Execution requires review: '+status,
            'residual_risks':['Universal mathematical claims rest on separate written proofs and reviews.','Code assertions are finite checks, not proof certificates.']
        }
        (records/(name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
        print(name+': '+status,flush=True)
        if status!='completed':return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
