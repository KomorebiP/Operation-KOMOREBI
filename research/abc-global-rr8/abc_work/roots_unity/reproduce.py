#!/usr/bin/env python3
"""Reproduce six bounded roots-of-unity contracts with v2 evidence records."""
import datetime,hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
PACKAGE=WORK.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=HERE/'computation_records'
    records.mkdir(exist_ok=True)
    specs=[
        ('padic','PROOF.md','results.json',{'p_n':[[5,2],[17,8],[97,16],[257,128]],'depths':[1,12]}),
        ('characters','PROOF_NOTE.md','verification.json',{'conductor_q':[1,100],'conductor_t':[-100,200],'shell_primes':[3,5,7,11],'shell_e':[1,4],'order_A':[2,10],'order_primes':[3,5,7,11,13],'order_e':[1,3],'joint_pairs':[[3,5],[3,7],[3,11],[5,7]],'joint_depths':[1,2],'negative_control':[2,1,1093,2,728]}),
        ('cyclotomic','PROOF_NOTE.md','verification.json',{'prescribed_n_p':[[2,5],[3,7],[5,11],[6,13],[8,17]],'depths':[1,10],'fixed_base_control':[2,1,182,1093],'other_tests':'Finite Fourier and resultant grids specified in verify.py and recorded result.'}),
        ('torsion_distance','TRANSFER_REPORT.md','results.json',{'p':[5,101],'n':2,'Hensel_depth':[1,20]}),
        ('auxiliary','PROOF.md','results.json',{'minimum_height_M':[1,100],'basis_A':[2,10],'basis_D':[1,6],'basis_B':'1<=B<A,gcd(A,B)=1'}),
        ('order_budget','ORDER_BUDGET.md','order_budget_verification.json',{'A':[2,10],'B':'1<=B<A,gcd(A,B)=1','n':[1,12],'additional_A_B_n':[[48,1,3],[10200,1,3],[8,1,9]],'power_three_s':[0,12]})
    ]
    base=WORK/'routes/global/PROOF_NOTE.md'
    for name,proof,result,bounds in specs:
        route=HERE/'routes'/('cyclotomic' if name=='order_budget' else name)
        verifier=route/('verify_order_budget.py' if name=='order_budget' else 'verify.py')
        inputs=[verifier,route/proof,HERE/'reproduce.py',base]
        before={p:sha(p) for p in inputs}
        output=route/result
        declared=[str(output.relative_to(WORK))]
        command=[sys.executable,str(verifier)]
        cwd=route if name in ('cyclotomic','order_budget') else PACKAGE
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
            'schema_version':2,'claim_id':'ABC-RR3-'+name,
            'repository':{'commit':'unavailable; parent archive f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469','dirty':True},
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
