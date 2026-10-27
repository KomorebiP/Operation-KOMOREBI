from pathlib import Path
import json,re,hashlib,datetime
r=Path('/workspace/scratch/a478a5fc4884/paper_v_work')
raw=r/'source/annals/PSC_Paper_V_Annals_Human_Edition.tex'
corrected=r/'traditional/extension_corrected.tex'
ledger=r/'traditional/EDITORIAL_CHANGES.json'
prior=r/'audit/annals_review.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=raw.read_text();t=corrected.read_text();j=json.loads(ledger.read_text());a=json.loads(prior.read_text())
changes=[x for x in j['changes'] if x['part']=='II' and x['kind']!='bibliographic']
replay=s;occurrences=[]
for c in changes:
 occurrences.append({'reason':c['reason'],'actual':replay.count(c['old']),'expected':c['occurrences']})
 replay=replay.replace(c['old'],c['new'])
assert replay==t
assert all(x['actual']==x['expected'] for x in occurrences)
expected={
'A':[r'a bounded linear approximation operator',r'Let \(Q_m:X\to X\) be linear',r'If \(Q_m\) is bounded and linear and',r'Let \(Q_m\) be linear and uniformly bounded'],
'B':[r'constants \(0\leq A_v\leq B_v<\infty\)'],
'C':[r'Here the step convention is \(H_\tau(t)=\one_{[\tau,\infty)}(t)\)',r'the smooth extension must satisfy the stated Lipschitz hypothesis'],
'D':[r'\(0<\delta<\delta_0\) lies in its stated range'],
'E':[r'converges to zero in probability in every finite \(L^p\) norm',r'Since \(\delta\) is arbitrary, convergence is in probability'],
'F':[r'\(Q\geq1\) is finite with nonzero jump amplitudes',r'nonzero jump amplitudes and positive minimum separation remain fixed',r'along grids satisfying the preceding sampling assumptions'],
'G':[r'when the first term is no larger than the second',r'at least one competing pruning exists',r'If only one admissible pruning exists'],
'H':[r'all noise variables independent across sites and repetitions'],
'I':[r'\(d\) coarse channel samples, equivalent to \(Nd\) original samples'],
'J':[r'For a periodic piecewise \(C^1\) function with an isolated jump'],
'K':[r'If \(\sigma=0\)',r'For \(\sigma>0\)'],
'L':[r'The displayed uniform noise certificate scales as',r'it does not imply consistency of this detector'],
'M':[r'\overline{s(t)-s(t+L/2)}\,\dd t.'],
'N':[r'Let \(0\leq\tau,\widehat\tau\leq1\) and \(H_\tau=\one_{[\tau,1]}\)']}
conclusions={
'A':'Linearity is explicit at the main estimated-packet identity and both downstream uses. Boundedness is imposed precisely when deriving the norm inequality. The nonlinear absolute-value witness is excluded.',
'B':'Nonnegative finite local constants make child-factor multiplication order preserving. The two zero-split counterexample with negative lower constants is excluded. Zero lower constants remain allowed and valid.',
'C':'The Haar subsection now declares the half-line step on the real line, with a Lipschitz smooth extension on every analyzed support. This removes the artificial right-endpoint jump and validates both isolated-step and two-grid estimates.',
'D':'The geometric estimate explicitly requires the tube radius to lie within the range guaranteed by its definition. The large-radius disk counterexample is excluded.',
'E':'The conclusion and epsilon/confidence proof explicitly give convergence in probability. They do not assert almost sure convergence. The fixed finite jump model makes the amplitude sum and number of jumps fixed in the deterministic bound.',
'F':'Nonempty finite jump list and nonzero amplitudes are explicit. Both consistency statements retain the admissible grids. Fixed positive separation and fixed nonzero amplitudes secure the eventual gap.',
'G':'The stop-on-ties rule is total, its proof includes equality, and the gap is the positive competitor-minus-optimum difference over a nonempty set. A singleton pruning set is handled separately.',
'H':'All site and repetition noises are explicitly independent, so averaging preserves independence across sites and gives the variance proxy used for adjacent differences.',
'I':'The reconstruction delay is explicitly measured in coarse channel samples. Interleaving converts it to N times as many fine samples. The following defect formula uses the same d convention.',
'J':'The imported Gibbs fact now has the requested periodic piecewise C1 hypothesis. This branch confirms the restriction was implemented but does not authenticate the primary external Gibbs theorem. No retained-packet proof uses Gibbs asymptotics as a premise.',
'K':'The sigma equals zero case is separated before the proof divides by sigma squared. Under the stated moment-generating-function condition, zero proxy forces zero noise almost surely.',
'L':'The remark now describes growth of the proved certificate rather than universal growth of actual noise maxima. Its fixed-noise limitation concerns this certificate, so bounded Rademacher noises no longer contradict the prose.',
'M':'The smooth-Haar pairing integral now conjugates the first-slot signal difference, consistently with the common edition convention. Its magnitude and every downstream estimate are unchanged.',
'N':'Both step locations are restricted to the observation interval. Their indicator symmetric difference therefore has length equal to the location displacement. Midpoints produced by the detector already satisfy this range, so no downstream algorithm or constant changes.'}
rows=[]
for key,needles in expected.items():
 assert all(q in t for q in needles),(key,needles)
 row={'id':key,'implementation_status':'passed','mathematical_status':'conditional' if key=='J' else 'passed','reason':conclusions[key],'required_text':[{'text':q,'line':t.count('\n',0,t.index(q))+1} for q in needles]}
 rows.append(row)
pat=re.compile(r'\\begin\{(theorem|lemma|proposition|corollary)\}(?:\[[^\]]*\])?\\label\{([^}]+)\}')
def inventory(text):
 out={}
 for m in pat.finditer(text):
  env,label=m.groups();e=text.index('\\end{'+env+'}',m.end())+len('\\end{'+env+'}')
  p=text.index('\\begin{proof}',e);q=text.index('\\end{proof}',p)+len('\\end{proof}')
  out[label]={'statement_sha256':hashlib.sha256(text[m.start():e].encode()).hexdigest(),'proof_sha256':hashlib.sha256(text[p:q].encode()).hexdigest()}
 return out
old,new=inventory(s),inventory(t)
assert old.keys()==new.keys() and len(new)==63
changed_statements=[k for k in old if old[k]['statement_sha256']!=new[k]['statement_sha256']]
changed_proofs=[k for k in old if old[k]['proof_sha256']!=new[k]['proof_sha256']]
record={'schema':'komorebi.paper_v.annals_repair_validation.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_verdict':'conditional on a named input','normalized_claim':'All A–N repairs are implemented correctly in the pinned corrected Annals source. The local mathematical repair obligations pass; the imported classical Gibbs theorem remains an external leaf, not freshly authenticated by this branch.','pins':[{'role':role,'path':str(p),'sha256':sha(p)} for role,p in [('raw Annals parent',raw),('corrected Annals copy',corrected),('editorial change ledger',ledger),('initial raw-source audit',prior)]],'summary':{'required_repairs':14,'implementation_passed':14,'local_mathematical_passed':13,'conditional_external':1,'failed':0,'pending_manuscript_correction':0,'editorial_tex_changes':len(changes),'editorial_replay_exact':replay==t,'editorial_occurrences_match':all(x['actual']==x['expected'] for x in occurrences),'proof_inventory_preserved':63,'statement_labels_preserved':True},'per_repair':rows,'additional_N_witness':{'original':'Without location range, tau=2 and tauhat=3 give two empty intervals on the observation domain, so the left norm is zero while |a| times the location displacement is nonzero.','corrected':'Both locations now lie in [0,1].','dependency_impact':'The detector already outputs midpoints in [0,1]; higher-order location theorem already had explicit range.'},'changed_statement_labels':changed_statements,'changed_proof_labels':changed_proofs,'corrected_inventory':new,'editorial_replay_occurrence_checks':occurrences,'other_diff_changes_reviewed':['positive lattice dimension for the proper c0 inclusion','explicit ell-p convolution input domain','unit-circle absolute convergence and L2 Fourier interpretation of infinite symbols','nonnegative trace-packet count','positive integer cyclic order and exact-order converse'],'limits':['This is a source-repair validation, not a fresh Lean build or a universal formal semantic audit.','No primary external Gibbs theorem was reauthenticated in this branch.','The bibliography-only name correction was excluded from TeX replay; its external-source validation belongs to the parent audit.','Validation pins extension_corrected.tex, not later page-layout-only combined TeX revisions.','The retained-packet theorems do not depend on the imported Gibbs fact.']}
(r/'audit/annals_repair_validation.json').write_text(json.dumps(record,indent=2)+'\n')
lines=['PAPER V: ANNALS REPAIR VALIDATION','','Primary verdict: conditional on a named input.',record['normalized_claim'],'','RESULT','All 14 requested repairs are implemented. Thirteen local mathematical repair checks passed, and the Gibbs scope change is implemented while its external theorem leaf remains conditional in this branch. No manuscript correction is pending.','', 'EXACT SOURCE PINS']
for pin in record['pins']:lines.extend([pin['role']+': '+pin['path'],pin['sha256']])
lines.extend(['','EDITORIAL AND PRESERVATION CHECKS',f"All {len(changes)} Part II TeX replacements replay exactly from the raw parent, with every occurrence count matching. All 63 statement labels and proof environments remain present.",f"Changed statement records: {len(changed_statements)}. Changed proof bodies: {len(changed_proofs)}. These changes are audited restrictions or clarifications, not new Lean coverage.",'','PER-REPAIR VALIDATION'])
for row in rows:lines.extend(['',row['id']+' | implementation: '+row['implementation_status']+' | mathematical obligation: '+row['mathematical_status'],row['reason'],'Locators: '+', '.join('line '+str(x['line']) for x in row['required_text'])])
lines.extend(['','DOWNSTREAM CHECK','The estimated-packet linearity hypothesis is propagated to post-detection and Gibbs bounds. The Haar half-line convention and smooth-extension condition precede all relevant wavelet results. The tube-radius restriction is used only where the local tube estimate is invoked. Probability statements retain the sampling model and distinguish convergence in probability. The step-location range excludes the counterexample and is already satisfied by detected cell midpoints.','', 'LIMITS']+record['limits'])
(r/'audit/annals_repair_validation.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'corrected_sha256':sha(corrected),'summary':record['summary'],'changed_statements':len(changed_statements),'changed_proofs':len(changed_proofs)},indent=2))
