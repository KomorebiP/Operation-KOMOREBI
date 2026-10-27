"""Run the finite checkpoint and actual OSL-Core 0.5 admission/quarantine path."""
from __future__ import annotations
from pathlib import Path
import json,sys,argparse
from semantic_interface import d4_fixture,make_certificate,emit_osl,checkpoint,restore,quotient_step,digest
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'OSL/core05/reference'
sys.path.insert(0,str(REF))
from osl_core import OSLRuntime
from osl_kernel import KernelVerifier
from osl_semantic_kernel import verify_semantic_independence

def run(output:Path)->dict:
    output.mkdir(parents=True,exist_ok=True)
    m=d4_fixture();c=make_certificate(m);saved=checkpoint(m,c,11)
    rows=[]
    for name,cert in [('accepted',c),('unverified',{})]:
        source=emit_osl(m,cert,11);p=output/(name+'.osl');p.write_text(source)
        r=OSLRuntime();r.run_text(source,filename=name+'.osl');state=r.state.snapshot()
        base=KernelVerifier().verify(r.audit_log,state,source=source)
        semantic=verify_semantic_independence(source,r.audit_log,state)
        row={'case':name,'source':source,'receipts':r.audit_log,'final_state':state,
             'base_checks_pass':base.get('independent_checks_pass') is True,
             'semantic_checks_pass':semantic.get('independent_checks_pass') is True}
        if not row['base_checks_pass'] or not row['semantic_checks_pass']:raise RuntimeError('OSL checks did not pass')
        (output/(name+'_trace.json')).write_text(json.dumps(row,sort_keys=True,indent=2)+'\n');rows.append(row)
    q=restore(m,c,saved);q_after=quotient_step(m,c,q,'f')
    result={'schema':'komorebi.osl-neuralese.finite-demo.v1','declared_states':16,'semantic_classes':8,
            'restored_class':q,'after_f_class':q_after,'certified_scope':c['scope'],
            'certificate':c,'checkpoint':saved,'osl_cases':[{'case':x['case'],'receipts':len(x['receipts']),
            'base_checks_pass':x['base_checks_pass'],'semantic_checks_pass':x['semantic_checks_pass']} for x in rows],
            'all_checks_pass':True,'learned_model_used':False,
            'boundary':'Complete finite transition table is supplied. This is not a learned Neuralese-to-OSL compiler.'}
    (output/'demo_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).parent/'examples');a=p.parse_args()
    print(json.dumps(run(a.output),sort_keys=True,indent=2))
