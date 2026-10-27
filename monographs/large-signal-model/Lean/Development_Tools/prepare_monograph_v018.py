from pathlib import Path
import hashlib,json
import fitz

base=Path('/workspace/scratch/ea498747acd5')
root=base/'work/Komorebi_LSM_Lean_0.18.0'
mono=base/'monograph_v018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((root/'RELEASE_COUNTS.json').read_text())
cp=json.loads((root/'CURRENT_CHECKPOINT.json').read_text())
cover=json.loads((root/'COVERAGE.json').read_text())
assert c['release']=='0.18.0' and c['complete_propositions']==66
assert cp['accepted_new_propositions']==list(range(58,66))
status=json.loads((base/'monograph_v017/source/FORMAL_STATUS.json').read_text())
with fitz.open(mono/'source/Original_Monograph.pdf') as doc:
 for n in range(58,66):
  matches=[(i,b) for i,p in enumerate(doc) for b in p.get_text('blocks') if b[4].startswith(f'P{n}.')]
  assert len(matches)==1,(n,matches)
  i,b=matches[0]
  candidates=[(j,z) for j in [i,i+1] for z in doc[j].get_text('blocks') if (j>i or z[1]>b[1]) and z[4].startswith('Formal coverage.')]
  j,z=min(candidates,key=lambda x:(x[0],x[1][1]))
  assert 'Not formalized in the archive.' in z[4],(n,z)
  e=cover['entries'][n-1]
  status['new_entries'].append({'id':n,'title':e['title'],'register_pdf_page':i+1,'coverage_pdf_page':j+1,'register_text':'Complete in the mapped scope.','guide_text':e['scope']})
status['new_entries'].sort(key=lambda e:e['id'])
groups=[
 ([11,23,24],'Ideal risk and grammar','Nested expectations decompose ideal risk. Summable grammar evidence controls tails. Prior splitting preserves whole-record evidence; predictive consistency also needs the joint-likelihood mixture.'),
 ([31,35,37],'Stochastic identification','Passive laws can miss interventions. Independent reset trials give simultaneous bounds. Observable completion retains experiment coverage, spectral separation and filtering margins.'),
 ([46,47,48,49],'Curved rotation and learning','The exact rotation requires a Lorentz cone; finite positive generators fail. Polygon approximation has a common-policy budget. Sequential learning retains conditional coverage, initial coverage and summable failures.'),
 ([50,51],'Matrix certificates','Injective matrix embeddings and positive congruences certify laws with exact mass and initial coverage. The rotation has an exact witness. Predictive base norm need not equal ambient trace norm.'),
 ([52,53],'Continuous instruments','Integrable positive operator densities and exact mass give consistent policy laws and positive-density updates. Reference changes preserve laws. Finite polynomial Gram identities certify the whole interval.'),
 ([54,55],'Moment identification','Correct supplied dimension and degree, with an invertible covered core, enable reconstruction. Without the degree restriction, positive rank-one laws share low moments while differing in total variation.'),
 ([56,57,58],'Cells and averaging','Exact bin laws require bin-measurable policies. Positive-cell posteriors average density-weighted updates. Congruence averaging retains covariance. Positive cell averages have base-norm resolution Lh, sharpened to Lh/3 for equal uniform intervals.'),
 ([59,60,61],'Comparison and realization','Common-cone, common-reference models admit full record-law budgets under one common history policy. Observable invertible template matching transports certificates. Realization retains true dimension, degree, domain and initial-state checks.'),
 ([62,63],'Oriented curved certificates','Quadratic Gram identities require mass orientation. Exact moments and initial coverage give all-horizon laws. Operator-only geometry discovery is a conditional proposal followed by full-family verification.'),
 ([64,65],'Positive polynomial approximation','Actual integral coefficients preserve cone positivity and exact mass without a true-degree assumption. The stated Lipschitz bias, fitted coefficient error and later correction budgets remain separate.'),
 ([66,68],'Sequential residual evidence','P66 remains partial for natural-number tests on standard Borel spaces, with recorded transport and rescaling restrictions. P68 gives lower discrepancy evidence conditional on the simultaneous residual event.'),
]
status['guide_entries']=[{'id':ids[0],'ids':ids,'label':', '.join('P'+str(n) for n in ids),'title':title,'guide_text':text} for ids,title,text in groups]
assert {n for g in status['guide_entries'] for n in g['ids']}=={e['id'] for e in status['new_entries']}
status.update(complete_count=66,partial_count=1,complete_ids=cp['complete_ids'],partial_ids=cp['partial_ids'],
 inventory_paragraph=f"The formal project contains {c['proof_modules']} proof modules and {c['proof_modules']+1} compilation targets including its root. Its inventory records {c['named_declarations']:,} named declarations and {c['named_theorems']:,} named theorems, comprising {c['supporting_theorems']:,} supporting theorems and {c['example_theorems']} theorems in dedicated example modules. These are different units from the 87 manuscript propositions.",
 theorem_cell=f"{c['named_theorems']:,} supporting and example theorems",rejection_cell=f"{c['negative_controls']} isolated checks",
 coverage_paragraph='The complete mappings are P1-P65 and P68. P66 has a partial mapping. The other 20 propositions retain written proofs without formal mappings. The additional scope notes conclude this appendix. Kernel acceptance is claimed only for the stated mapped scopes.',
 guide_boundary='All propositions P1-P65 and P68 have complete formal mappings. P66 remains partial in its stated sector. The other 20 propositions retain written proofs without formal mappings.',
 guide_spacing_pt=4,expected_verifier_stages=2*c['proof_modules']+c['negative_controls']+3,metadata_checks=113,inventory_pending=False)
report_path=root/'verification/current/report.json'
report=json.loads(report_path.read_text()) if report_path.exists() else {}
passed=report.get('passed') is True and report.get('complete') is True and report.get('release')=='0.18.0'
if passed:
 assert len(report['stages'])==status['expected_verifier_stages']
 status['execution_status']='PASS'
 status['execution_paragraph']=f"Fresh verification passed {len(report['stages'])} stages: {c['proof_modules']+1} compilation targets, one exact-example execution, one axiom audit, {c['proof_modules']} module kernel replays and {c['negative_controls']} isolated rejection controls. The permitted logical axioms are propext, Classical.choice and Quot.sound. Upstream libraries remain pinned dependencies and were not exhaustively rebuilt or replayed."
else:
 status['execution_status']='PENDING'
 status['execution_paragraph']='The current cumulative run is pending. Individual source compilation, axiom audits, kernel replays and internal scope reviews are recorded separately. This publication preparation does not claim that the cumulative run has passed.'
status['markdown_guide']='# Formal companion scope notes\n\n'+status['inventory_paragraph']+'\n\n'+status['execution_paragraph']+'\n\n'+''.join(f"## P{e['id']}. {e['title']}\n\n{e['guide_text']}\n\n" for e in status['new_entries'])+status['guide_boundary']+'\n'
(mono/'source/FORMAL_STATUS.json').write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n')
preparation={'accepted':passed,'parent_archive_sha256':'dc3e6a2877b94db1eba0e50334859cd1cf2f83171cca5b0e22ea60717556479b','parent_body_sha256':sha(base/'monograph_v017/source/FOUNDATIONS.md'),'counts':c,'checkpoint_sha256':sha(root/'CURRENT_CHECKPOINT.json'),'coverage_sha256':sha(root/'COVERAGE.json'),'formal_status_sha256':sha(mono/'source/FORMAL_STATUS.json'),'guide_word_count':sum(len((g['title']+' '+g['guide_text']).split())for g in status['guide_entries']),'proofreading_scope':'Current formal counts, mapped scope descriptions and register lines; mathematical body otherwise retains the predecessor corrections. Final render, source identity and visual checks are separate.'}
(mono/'review/FORMAL_COMPANION_PREPARATION.json').write_text(json.dumps(preparation,indent=2)+'\n')
print(json.dumps({'execution_status':status['execution_status'],'guide_word_count':preparation['guide_word_count'],'expected_stages':status['expected_verifier_stages']}))
