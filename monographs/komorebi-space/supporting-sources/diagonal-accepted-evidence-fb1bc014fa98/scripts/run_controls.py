#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,datetime,re,argparse
r=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--native',action='store_true',help='Use the pinned Lean/Lake installation on PATH without this host\'s compatibility wrapper.')
args=parser.parse_args()
prefix=[] if args.native else [str(r/'scripts/lean_env.sh')]
specs=[('positive_diagonal','accept'),('positive_sharp_asymptotic','accept'),('reject_zero_parameter_index','reject'),('reject_zero_noise_schedule','reject'),('reject_wrong_prefix_norm','reject'),('reject_wrong_asymptotic_constant','reject'),('reject_admitted_proof','reject'),('reject_project_axiom','policy-reject')]
results=[]
for name,expect in specs:
 f=r/'controls'/f'{name}.lean';cmd=prefix+['lake','env','lean','-j1','-DwarningAsError=true','-DautoImplicit=false',str(f)]
 p=subprocess.run(cmd,cwd=r/'lean',text=True,capture_output=True)
 log=r/'logs'/f'control_{name}.log';log.write_text(p.stdout+p.stderr)
 axiom_groups=re.findall(r'depends on axioms: \[([^\]]*)\]',p.stdout)
 observed_axioms={a.strip() for group in axiom_groups for a in group.split(',') if a.strip()}
 foreign_axioms=sorted(observed_axioms-{'propext','Classical.choice','Quot.sound'})
 policy_rejected=bool(foreign_axioms)
 passed=(p.returncode==0 if expect=='accept' else p.returncode!=0 if expect=='reject' else p.returncode==0 and policy_rejected)
 results.append({'name':name,'expected':expect,'exit_code':p.returncode,'passed':passed,'policy_rejected':policy_rejected if expect=='policy-reject' else None,'observed_axioms':sorted(observed_axioms),'foreign_axioms':foreign_axioms,'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'command':cmd,'log':str(log.relative_to(r))})
 print(name,p.returncode,'PASS' if passed else 'FAIL',flush=True)
out={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Targeted diagnostic controls for the new diagonal formalization; not a replacement for the parent 44-control historical audit.','all_expected_outcomes':all(x['passed'] for x in results),'controls':results}
(r/'records/DIAGONAL_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
raise SystemExit(0 if out['all_expected_outcomes'] else 1)
