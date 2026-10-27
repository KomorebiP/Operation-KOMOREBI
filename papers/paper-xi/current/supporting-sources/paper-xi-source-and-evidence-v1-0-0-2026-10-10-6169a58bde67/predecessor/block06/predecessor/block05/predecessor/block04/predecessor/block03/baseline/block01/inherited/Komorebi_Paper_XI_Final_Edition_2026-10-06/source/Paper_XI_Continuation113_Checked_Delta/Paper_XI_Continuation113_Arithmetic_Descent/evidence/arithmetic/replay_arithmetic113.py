#!/usr/bin/env python3
"""Reproduce only the arithmetic113 checks and pin their actual outputs."""
from pathlib import Path
import subprocess,json,hashlib,sys,platform,datetime,time
root=Path(__file__).resolve().parents[2]
d=root/'evidence/arithmetic'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=['cyclotomic_check113.py','self_twist113.py','central_twist113.py','central_normalization_check113.py','replay_arithmetic113.py']
before={p:h(d/p) for p in inputs}
runs=[('cyclotomic_check113.py',[],'cyclotomic_result113.json'),('self_twist113.py',[],'self_twist_result113.json'),('central_twist113.py',['0'],'central_twist_result113.json'),('central_twist113.py',['1'],'corrected_central_twist_result113.json'),('central_twist113.py',['2'],'opposite_central_twist_result113.json'),('central_normalization_check113.py',[],'central_normalization_result113.json')]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter();records=[]
for script,args,out in runs:
 argv=[sys.executable,str(d/script),*args];tt=time.perf_counter()
 p=subprocess.run(argv,capture_output=True,text=True,cwd=root,timeout=30)
 (d/out).write_text(p.stdout);(d/(out+'.stderr.txt')).write_text(p.stderr)
 records.append({'argv':argv,'exit_status':p.returncode,'runtime_seconds':time.perf_counter()-tt,'output':out,'sha256':h(d/out)})
 if p.returncode:raise RuntimeError(records[-1])
after={p:h(d/p) for p in inputs};assert before==after
result_paths=[d/out for _,_,out in runs]
for p in result_paths:assert json.loads(p.read_text()).get('all_checks_pass',json.loads(p.read_text()).get('all_assertions_pass',True))
# Meaningful comparison, separately from process exit status.
a0=json.loads((d/'central_twist_result113.json').read_text());a1=json.loads((d/'corrected_central_twist_result113.json').read_text());a2=json.loads((d/'opposite_central_twist_result113.json').read_text())
assert a0['uniformizer_commutator_H_character']=='1/3' and not a0['remaining_scalar_is_one']
assert a1['uniformizer_commutator_H_character']=='0' and a1['remaining_scalar_is_one']
assert a2['uniformizer_commutator_H_character']=='2/3' and not a2['remaining_scalar_is_one']
receipt={'started_at':started,'runtime_seconds':time.perf_counter()-t,'input_hashes_before':before,'input_hashes_after':after,'runs':records,'all_processes_pass':True,'scalar_sequence':['zeta3','1','zeta3^2'],'interpretation':'Original central-type obstruction and a distinct explicit correction, subject to the source-backed group reduction; no AI occurrence claim.'}
(d/'replay_receipt113.json').write_text(json.dumps(receipt,indent=2)+'\n')
outputs=[{'path':str(p.relative_to(root)),'sha256':h(p)} for p in result_paths+[d/p for p in inputs]+[d/'replay_receipt113.json']]
m={'schema_version':1,'claim_id':'PaperXI.Arithmetic113.CyclotomicOccurrenceDiscriminator','repository':{'commit':None,'dirty':True},'command':'python evidence/arithmetic/replay_arithmetic113.py','environment':{'software':[sys.version,'fractions.Fraction (standard library); subprocess per-step timeout30s'],'hardware':platform.platform()},'mathematics':{'assertion_tested':'Exact field witnesses, original theta self-twist, nontrivial central-type scalar, explicit wild correction, retained central character','coefficient_domain':'Exact Q[X]/Phi_9(1+X), 3x3 field matrices, and exact roots of unity; no floating arithmetic','conventions':'psi_F=psi_Q3(Tr_F/Q3(-)/3); theta^g(h)=theta(g^-1 h g); v_L(pi)=1; v_a(M)=min(v_L(M_ij)+i-j)','inputs':[p+' SHA256 '+before[p] for p in inputs],'bounds':{'cyclotomic_checks':16,'diagonal_self_twist_candidates':27,'principal_unit_generators':6,'norm_kernel_unit_generators':3,'log_degree_inclusive':26,'correction_coefficients':[0,1,2],'eta_dimension':3,'eta_generators':2},'non_claims':['Not a proof of occurrence for corrected theta in AI(chi), original H5, or Claim16.2.','No Lean certificate.','No unrestricted packet realization or correction uniqueness.','The finite-to-group and all-intertwiner reductions are separate ordinary proofs.']},'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':started,'runtime_seconds':receipt['runtime_seconds'],'exit_status':0},'outputs':outputs,'checks':['Exact rational cyclotomic character witnesses','Original and all corrected six-generator theta intertwiners','Actual eta commutator and cube phases','All27 deep stratum candidates','Central scalars zeta3,1,zeta3^2 with coefficient0,1,2','Direct group commutator audit independent of averagingS','Explicit corrected uniformizer value preserving F× character','Execution inputs hashed before and after with equality'],'result':'All declared exact finite assertions pass. Original central-type scalar is nontrivial; displayed wild correction cancels it and preserves the original central-character compatibility.','residual_risks':['Legacy version1 schema; auxiliary receipt contains actual argv and input before/after hashes.','No git repository revision.','No full source replay of external BK/BH representation theory.','The corrected AI inducing-character identification remains unproved.']}
(d/'computation_manifest113.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'all_checks_pass':True,'runtime_seconds':receipt['runtime_seconds'],'scalar_sequence':receipt['scalar_sequence']}))
