#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,datetime
r=Path(__file__).resolve().parents[1]
specs=[('positive_diagonal','accept'),('reject_zero_parameter_index','reject'),('reject_zero_noise_schedule','reject'),('reject_wrong_prefix_norm','reject'),('reject_admitted_proof','reject'),('reject_project_axiom','policy-reject')]
results=[]
for name,expect in specs:
 f=r/'controls'/f'{name}.lean';cmd=[str(r/'scripts/lean_env.sh'),'lake','env','lean','-j1','-DwarningAsError=true','-DautoImplicit=false',str(f)]
 p=subprocess.run(cmd,cwd=r/'lean',text=True,capture_output=True)
 log=r/'logs'/f'control_{name}.log';log.write_text(p.stdout+p.stderr)
 policy_rejected='DeliberatePolicyControl.forbiddenInput' in p.stdout
 passed=(p.returncode==0 if expect=='accept' else p.returncode!=0 if expect=='reject' else p.returncode==0 and policy_rejected)
 results.append({'name':name,'expected':expect,'exit_code':p.returncode,'passed':passed,'policy_rejected':policy_rejected if expect=='policy-reject' else None,'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'command':cmd,'log':str(log.relative_to(r))})
 print(name,p.returncode,'PASS' if passed else 'FAIL',flush=True)
out={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Targeted diagnostic controls for the new diagonal formalization; not a replacement for the parent 44-control historical audit.','all_expected_outcomes':all(x['passed'] for x in results),'controls':results}
(r/'records/DIAGONAL_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
raise SystemExit(0 if out['all_expected_outcomes'] else 1)
