from pathlib import Path
import json,hashlib,re
root=Path('/workspace/scratch/9f53d520971c')
draft=root/'paper2_work/transfer'
stage=root/'paper2_work/transfer_promoted/KomorebiVerification/PaperII'
stage.mkdir(parents=True,exist_ok=True)
modules={
 'ReleaseTransferMatrix':'transfer_matrix_check02',
 'ReleaseTransferScalar':'transfer_check04',
 'ReleaseTransferMultigraded':'transfer_multi_check02',
 'ReleaseTransferMultigradedRational':'transfer_multirat_check03',
 'ReleaseTransferConsequences':'transfer_consequences_check02',
}
sha=lambda b:hashlib.sha256(b).hexdigest()
records=[]
for mod,check in modules.items():
 src=draft/f'{mod}.lean'; b=src.read_bytes(); j=json.loads((root/'paper2_work'/check/'CHECK.json').read_text())
 assert j['status']=='PASS' and j['source_sha256']==sha(b)
 text=b.decode()
 assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b',text)
 adapted=re.sub(r'^import (ReleaseTransfer\w+)\s*$',r'import KomorebiVerification.PaperII.\1',text,flags=re.M)
 dest=stage/src.name;dest.write_text(adapted)
 records.append({'module':mod,'draft_source':str(src.relative_to(root)),
  'draft_sha256':sha(b),'strict_check':f'paper2_work/{check}/CHECK.json',
  'strict_check_sha256':sha((root/'paper2_work'/check/'CHECK.json').read_bytes()),
  'check_elapsed_seconds':j['elapsed_seconds'],
  'staged_source':str(dest.relative_to(root)),
  'staged_sha256':sha(dest.read_bytes()),
  'production_target':f'formal/current/KomorebiVerification/PaperII/{mod}.lean',
  'adaptation':'Bare local ReleaseTransfer imports qualified as KomorebiVerification.PaperII; no proof or theorem-body changes.',
  'production_verification':'Pending root whole-source replay of adapted exact hashes.'})
report={
 'schema':'komorebi.paper_ii.transfer_closure.v1','date':'2026-10-15',
 'scope':'Generic scalar and multigraded semantic transfer rationality, independent walk coefficient bridge, endpoint weights, recurrences and reduced scalar denominator.',
 'verdict':'All five exact draft modules strict Lean PASS; adapted nested import stage ready for root integration and exact whole-source replay.',
 'baseline':'paper2_work/baseline_compile/REPLAY.json',
 'runtime':'Lean 4.34.0-rc2, pinned mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; imported objects trusted, not independently rebuilt.',
 'checks':records,
 'leaf_import':'import KomorebiVerification.PaperII.ReleaseTransferConsequences',
 'production_modified':False,
 'semantic_contract':{
  'coefficients':'Arbitrary commutative ring R for scalar products, matrix inverse and formal-series identities. Nontrivial R is added only for polynomial denominator nonvanishing. Field K is added only for RatFunc reduced denominator.',
  'scalar_walks':'Old genuine unrestricted ExactWalk list subtype with source/target and positive integer weight; products retain every edge occurrence. Reuses proved actual-walk first-edge equivalences, never assumes coefficient recurrence.',
  'multigraded_walks':'Actual unrestricted list subtype with full Finsupp vector sum fixed to n. Every edge vector is nonzero. Total degree gives a finite embedding into scalar ExactWalk and is used only for finiteness; coefficients retain full vectors.',
  'endpoint_weights':'Arbitrary u,v:V→R contracted as sum_i sum_j u_i * coefficient_ij * v_j; equivalent to displayed u_i v_j product by ring commutativity.',
  'rationality':'The independently defined semantic series matrix satisfies (I−A)S=1. Polynomial determinant Q has constant coefficient1, whose invOfUnit constructs the scalar inverse. Adjugate identities give two-sided inverse and identify S with rational matrix, then Q Z=P.',
  'recurrence':'Generic Q Z=P gives convolution recurrence whenever P.coeff n=0; degree theorem uses Polynomial.degree : WithBot Nat. P=0 and n=0 are included. Scalar endpoint specialization also supplied.',
  'reduced_denominator':'Over Field K, endpointRationalFunction is the explicit numerator/determinant RatFunc. Its reduced denominator divides Q; scalar_endpoint_unique ties Q Z=P to the independently defined series.',
  'empty_and_parallel':'No nonempty vertex/edge assumption. List walks permit loops/repeated edges and parallel edges are separately indexed by E.'},
 'manuscript_mapping':[
  {'label':'thm:transfer_rationality','declarations':['ReleaseTransferScalar.coefficient_firstEdge','ReleaseTransferScalar.seriesMatrix_eq_rationalMatrix','ReleaseTransferScalar.endpoint_coeff','ReleaseTransferScalar.endpoint_rationality','ReleaseTransferConsequences.scalar_denominator_ne_zero','ReleaseTransferConsequences.scalar_endpoint_unique','ReleaseTransferConsequences.reduced_denominator_dvd']},
  {'label':'cor:path_recurrence','declarations':['ReleaseTransferConsequences.recurrence_of_coefficient_zero','ReleaseTransferConsequences.recurrence_of_degree_lt','ReleaseTransferConsequences.zero_numerator_recurrence','ReleaseTransferScalar.endpoint_recurrence']},
  {'label':'cor:multigraded_series','declarations':['ReleaseTransferMultigraded.firstEdgeEquiv','ReleaseTransferMultigraded.coefficient_firstEdge','ReleaseTransferMultigraded.seriesMatrix_eq_rationalMatrix','ReleaseTransferMultigraded.endpoint_coeff','ReleaseTransferMultigraded.endpoint_rationality','ReleaseTransferConsequences.multigraded_denominator_ne_zero','ReleaseTransferConsequences.multigraded_endpoint_unique']}],
 'unsuccessful_checks':[
  {'runs':['transfer_matrix_check01'],'reason':'Strict unused-section-variable lint; repaired by explicit omit.'},
  {'runs':['transfer_check01','transfer_check02','transfer_check03'],'reason':'Finite subtype transport elaboration, strict deprecation/unused simp lints and definitional simplification issues; repaired without changing theorem scope.'},
  {'runs':['transfer_multi_check01'],'reason':'Missing noncomputable section and ambiguous Subtype.val congrArg; repaired.'},
  {'runs':['transfer_multirat_check01','transfer_multirat_check02'],'reason':'Only strict unused-section-variable lints; repaired with explicit omit.'},
  {'runs':['transfer_consequences_check01'],'reason':'Antidiagonal finite-sum rewrite required tuple-form API; repaired.'}],
 'failed_objects':'Never used as accepted dependency roots; each dependent check imports only accepted PASS roots.',
 'independent_review':'Requested from defects_models agent; pending separate report.',
 'remaining':['Root production integration and strict whole-source replay with adapted hashes.','Root axiom/dependency audit and release scope synchronization.','Independent source semantic review pending.'],
 'not_claimed':['No Paper II whole-release completion claim.','No full filtered packet or canonical analytic calculus claim from these modules.','No production source hash is certified by a draft receipt.'],
}
(root/'paper2_work/audit/transfer_closure.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'paper2_work/audit/transfer_closure.txt').write_text('Transfer branch: all five draft modules strict Lean PASS.\n\nLeaf import: '+report['leaf_import']+'\n\nAdapted nested modules are staged at paper2_work/transfer_promoted/KomorebiVerification/PaperII/. Root exact source replay remains required.\n\n'+ '\n'.join(f"{x['module']}: {x['strict_check']}\n  draft {x['draft_sha256']}\n  staged {x['staged_sha256']}" for x in records)+'\n')
print(json.dumps({'status':'PASS_DRAFTS_STAGED','modules':len(records),'leaf':report['leaf_import'],'report':'paper2_work/audit/transfer_closure.json'}))
