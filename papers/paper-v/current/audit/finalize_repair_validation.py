from pathlib import Path
import hashlib,json,re,datetime

W=Path(__file__).resolve().parent.parent
O=W/'audit'; T=W/'traditional'
core0=W/'source/complete/original_snapshot/manuscript/Paper_V_Expanded_Lean_Checked.tex'
ext0=W/'source/annals/PSC_Paper_V_Annals_Human_Edition.tex'
core=T/'core_corrected.tex'; ext=T/'extension_corrected.tex'

def pin(p):
 return {'path':str(p.relative_to(W)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def records(p):
 text=p.read_text(); result=[]
 pattern=re.compile(r'\\begin\{(theorem|proposition|corollary|lemma)\}(.*?)\\end\{\1\}',re.S)
 for m in pattern.finditer(text):
  label=re.search(r'\\label\{([^}]+)\}',m.group())
  proof=re.search(r'\\begin\{proof\}(.*?)\\end\{proof\}',text[m.end():],re.S)
  if not label or not proof: raise ValueError('Missing result identity/proof: '+str(p))
  result.append({'label':label.group(1),'statement_sha256':hashlib.sha256(m.group().encode()).hexdigest(),'proof_sha256':hashlib.sha256(proof.group().encode()).hexdigest()})
 return result

delta=[]
for part,orig,cur,n in [('I',core0,core,20),('II',ext0,ext,63)]:
 a,b=records(orig),records(cur)
 if len(a)!=n or len(b)!=n:raise ValueError('Changed result inventory')
 if [r['label'] for r in a]!=[r['label'] for r in b]:raise ValueError('Changed result order or labels')
 rows=[]
 for old,new in zip(a,b):
  rows.append({'label':old['label'],'original':old,'corrected':new,'statement_changed':old['statement_sha256']!=new['statement_sha256'],'proof_changed':old['proof_sha256']!=new['proof_sha256']})
 delta.append({'part':part,'retained_records':n,'changed_statements':[r['label'] for r in rows if r['statement_changed']],'changed_proofs':[r['label'] for r in rows if r['proof_changed']],'records':rows})

changes=json.loads((T/'EDITORIAL_CHANGES.json').read_text())['changes']
replay=[]
for part,orig,cur in [('I',core0,core),('II',ext0,ext)]:
 txt=orig.read_text();used=[]
 for i,c in enumerate(changes):
  if c['part']!=part or c['kind']=='bibliographic':continue
  found=txt.count(c['old'])
  if found!=c['occurrences']:raise ValueError(f'Unexpected replacement occurrence at index {i}: {found}')
  txt=txt.replace(c['old'],c['new']);used.append(i)
 if txt!=cur.read_text():raise ValueError('Corrected copy differs from recorded replay: '+part)
 replay.append({'part':part,'changes':len(used),'ledger_indices':used,'exact_replay':'passed'})

manual=[
 {'id':'CORE-PROBABILITY','status':'passed','locator':'result:16','finding':'Ordinary probability now assumes measurable random node costs and a measurable joint good event.','justification':'Finitely many measurable comparisons determine the finite-tree selector. The preserved formal monotonicity theorem specializes to these measurable events without changing Lean source or coverage.','impact':'Only the probabilistic specialization is clarified; deterministic envelope, gap and selection estimates are unchanged.'},
 {'id':'A-TRANSFORM','status':'passed','locator':'Part II Section 4 symbol paragraph','finding':'Unit-circle absolute symbols, literal ell1 transforms, L2 Fourier almost-everywhere interpretation, and FIR nonzero-z summability domains are separated.','justification':'The incorrect unrestricted numerical evaluation is no longer claimed. Time-domain transfer remains a bounded ellp result.','impact':'Convolution transfer and Fourier filter-bank interpretation remain consistent with Part I result05.'},
 {'id':'A-ORDER','status':'passed','locator':'Part II thm:cyclic_mobius','finding':'N is a positive integer; the exact-order proof now supplies the missing necessity by evaluating the conjugate rotation at1/2.','justification':'If the kth power is identity, exp(2*pi*i*k/N)=1, hence N dividesk. Together with the Nth identity this gives orderN.','impact':'Only prose analytic exact-order conclusion strengthened; the Lean map still certifies cyclic composition rather than an extra exact-order target.'},
 {'id':'A-DIMENSION','status':'passed','locator':'Part II signal-seed section','finding':'Spatial dimension explicitly positive, convolution signal explicitly in ellp, and finite trace packet count Q explicitly nonnegative.','justification':'The claimed proper c0 inclusion has an infinite lattice; absolute convolution follows because ellp signals are bounded and the kernel is ell1.','impact':'No underlying formula changed.'},
]

guide_files=[W/'lean_guide/chapters'/x for x in ['05_edges.tex','06_trees.tex','07_cyclic_smith.tex']]+[W/'visual_guide/source/extensions.tex']
guide_review=[
 {'files':[str(p.relative_to(W)) for p in guide_files[:3]],'status':'passed','scope':'Full chapters05–07 read against selected Lean sources. Correct distinction between arbitrary-Q retained cancellation and linear estimated-packet splitting; extended Lp versus real-valued bounds; pointwise versus essential supremum; additive DP versus arbitrary objectives; abstract operation counters versus runtime; measurable-event probability; cyclic composition versus exact order; projective action versus totalized chart division. No corrective edit requested.'},
 {'files':[str(guide_files[-1].relative_to(W))],'status':'passed','scope':'All14 extension pages read, with focused hand reconstruction of pages 32, 36, 37, 38. Oblique projection produces(-2,1), norm sqrt(5); repeated-measurement bound2173/32000<2/25; Haar noise/background29/800 and lower jump71/800; two-grid condition29/200<1/4. Added positive lower bound and fixed positive noise qualifiers. This manual review is not the independent numerical-suite record.'}
]

child=json.loads((O/'annals_repair_validation.json').read_text())
report={'schema':'komorebi.paper_v.final_repair_validation.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_verdict':'conditional on a named input','final_copy_verdict':'All identified internal mathematical repairs are implemented and their corrected implications pass manual review. Imported classical analytic background, in particular the exact Gibbs theorem citation, remains a named background input rather than a newly authenticated theorem in this audit.','original_source_verdict':'The original combined sources are correct only after the restrictions, convention clarifications and proof completions recorded in SCOPED_MATHEMATICAL_AUDIT and annals_review. Original bytes remain preserved.','unresolved_internal_manuscript_repairs':0,'normalized_claim':'A final two-part Paper V retains20 core proof records and63 analytic proof records, with explicit corrected domains. The inherited formal coverage remains20 manuscript results and225 supporting targets;83 prose records are not83 independent or newly formalized theorems.','source_pins':[pin(p) for p in [core0,ext0,core,ext,T/'Paper_V_Traditional_Final.tex',T/'EDITORIAL_CHANGES.json']+guide_files],'manual_parent_checks':manual,'annals_validation':{'report':'annals_repair_validation.json','sha256':hashlib.sha256((O/'annals_repair_validation.json').read_bytes()).hexdigest(),'scope':'All14 repairs A–N independently rechecked by delegated reviewer. Local implementation checks pass; exact external Gibbs authentication remains conditional.'},'exact_source_replay':replay,'proof_record_preservation':delta,'guide_reviews':guide_review,'limits':['No fresh Lean compilation, kernel audit, or exhaustive225-target semantic re-audit is claimed.','Full20 core and full63 Annals raw prose bodies were read across the audit team; selected actual Lean definitions and interfaces were inspected. Reviewers can share errors.','Classical analytic background is not claimed as a new result, nor was its full source literature reauthenticated by this branch. Root separately recorded the bounded Gibbs bibliography check and retrieval failures.','No new numerical-suite counts arise from this report. Read the independently executed verification reports for tested ranges and failure controls.','The combined final TeX hash is a snapshot at this validation; later typesetting-only changes do not change the pinned corrected core and extension mathematical bodies.','No novelty, historical priority, unrestricted recovery, infinite-tree result, or universal sampling claim follows from these checks.']}
# Polish ordinary human-readable prose without changing code paths or identifiers.
for row in manual:
 for k in ['finding','justification','impact']:
  for a,b in {'Section4':'Section 4','result05':'result 05','at1/2':'at 1/2','dividesk':'divides k','orderN':'order N'}.items():row[k]=row[k].replace(a,b)
report['normalized_claim']=report['normalized_claim'].replace('retains20','retains 20').replace('and63','and 63').replace('remains20','remains 20').replace('and225','and 225').replace(';83','; 83').replace('not83','not 83')
for k in range(len(report['limits'])):
 report['limits'][k]=report['limits'][k].replace('exhaustive225','exhaustive 225').replace('Full20','Full 20').replace('full63','full 63')
report['annals_validation']['scope']=report['annals_validation']['scope'].replace('All14','All 14')
for g in guide_review:
 for a,b in {'chapters05':'chapters 05','All14':'All 14','pages32':'pages 32','produces(-2,1)':'produces (-2,1)','bound2173':'bound 2173','background29':'background 29','jump71':'jump 71','condition29':'condition 29'}.items():g['scope']=g['scope'].replace(a,b)
(O/'FINAL_REPAIR_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['PAPER V — FINAL MATHEMATICAL REPAIR VALIDATION','', 'Primary verdict: '+report['primary_verdict'],report['final_copy_verdict'],'',report['normalized_claim'],'','Unresolved internal manuscript repairs: 0.','No fresh Lean kernel run was performed.','','PARENT REVIEW ITEMS']
for x in manual:lines.extend([x['id']+' — '+x['status'],x['locator'],x['finding'],x['justification'],'Dependency impact: '+x['impact'],''])
lines.extend(['ANNALS REPAIRS',report['annals_validation']['scope'],'See annals_repair_validation.txt/json for all A–N source evidence.','','EXACT EDIT REPLAY'])
for r in replay:lines.append(f"Part {r['part']}: {r['changes']} recorded TeX edits replay exactly to the corrected source.")
lines.append('')
for d in delta:lines.append(f"Part {d['part']}: {d['retained_records']} records retained; {len(d['changed_statements'])} statement block(s) and {len(d['changed_proofs'])} proof bodies changed. Changed statements: {', '.join(d['changed_statements'])}. Changed proofs: {', '.join(d['changed_proofs'])}.")
lines.extend(['','COMPANION REVIEW'])
for g in guide_review:lines.extend(g['files']+[g['scope'],''])
lines.extend(['LIMITS']+report['limits']+['','SOURCE PINS'])
for p in report['source_pins']:lines.append(p['sha256']+'  '+p['path'])
(O/'FINAL_REPAIR_VALIDATION.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'verdict':report['primary_verdict'],'unresolved_internal_repairs':0,'replay':replay,'preservation':[{k:v for k,v in x.items() if k!='records'} for x in delta]},indent=2))
