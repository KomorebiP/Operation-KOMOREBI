#!/usr/bin/env python3
"""Bounded prose and reading-reference edits for the collected book."""
from pathlib import Path
import json,re,hashlib,shutil
ROOT=Path(__file__).resolve().parent
BOOK=ROOT.parent
BACKUP=ROOT/'book_edit_baseline'
JOURNAL=[]
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,s,reason):
 old=p.read_text()
 if s==old:return
 target=BACKUP/p.relative_to(ROOT)
 if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 p.write_text(s)
 JOURNAL.append({'path':str(p.relative_to(ROOT)),'reason':reason,'before_sha256':sha(old),'after_sha256':sha(s)})
def replace(p,a,b,reason='Publication prose and reference clarity'):
 s=p.read_text()
 if a not in s:raise ValueError(f'Pattern missing in {p}: {a[:85]}')
 write(p,s.replace(a,b),reason)
def para(p,start,new):
 s=p.read_text();items=s.splitlines(keepends=True);hits=[i for i,x in enumerate(items) if x.startswith(start)]
 if len(hits)!=1:raise ValueError((p,start,len(hits)))
 items[hits[0]]=new+'\n'
 write(p,''.join(items),'Rewrite administrative paragraph as mathematical reading guidance')
def main(n,role='traditional'):
 return ROOT/n/'editable'/role/('Paper_'+n+'_'+{'traditional':'Traditional','visual_guide':'Visual_Guide','lean_guide':'Lean_Guide'}[role]+'_Final.tex')

# Reading introductions describe the subject and its actual formal scope.
p=main('V')
replace(p,'Reading this edition','Reading this chapter')
para(p,'The two branches of Paper V answer', 'This chapter develops signal calculus in two complementary parts. Part I gives twenty results on exact coordinates, filtering, adaptive selection and packet error. Part II develops lattice coordinates, stable banks, singular packets and separated jump recovery, with E-prefixed section numbers. The two parts share constructions but use them under different hypotheses.')
para(p,'The inherited September 2026 release records', 'The formal companion maps all twenty Part I results to 225 supporting Lean theorem targets across 23 proof modules. Part II has ordinary written proofs and is outside that twenty-result formal map. Exact examples and numerical studies have their own stated scopes. The formal companion and source records distinguish kernel verification, finite checks and numerical replay.')
replace(p,'the precise released formal contract','the precise formal contract')
replace(p,'Part I: The released formal core','Part I: The formal core')
replace(p,'The preserved September 2026 release integrates a Lean formalization','The accompanying formal development gives a Lean formalization')
replace(p,'the simple two-class estimator supplied with the release','the supplied two-class estimator')
replace(p,'The release visualizes the weight but does not prove optimality.','The illustration displays the weight but does not prove optimality.')
replace(p,'Appendix~\\ref{sec:formalization} records it result by result. The September 2026 release records a rerun of the numerical experiments. The current final-edition checks are distinguished in the opening reading note.','Section~\\ref{sec:formalization} records it result by result. Numerical replay has a separate record and does not enlarge the formal theorem scope.')
replace(p,'September 2026 checks and numerical conventions','Recorded checks and numerical conventions')
replace(p,'Pinned environment and rerunning the release','Pinned environment and reproduction')
para(p,'Across the available Papers I--V manuscripts', 'Historical cross-paper declaration counts are retained in the source records. The relevant formal denominator here is the twenty scoped Part I results. Supporting declarations, reused results and proofs in the broader written development have distinct roles.')

p=main('VI')
replace(p,'Reading this edition','Reading this chapter')
para(p,'Paper VI has several substantial source branches.', 'This chapter studies transfer semigroups in three complementary settings. Part I establishes the finite formal core. Part II develops bounded refinement towers, probabilistic conditioning and analytical realizations. Part III gives additional results on product-topology limits, reversible coarse dynamics, filtering, perturbation and operator substitution. Their hypotheses distinguish the constructions even where the underlying identities overlap.')
para(p,'The formal denominator is exactly', 'The formal companion covers exactly the thirty-three scoped results of Part I. Its 341 supporting Lean theorem declarations lie in 47 proof modules. The wider namespace audit includes definitions and generated declarations. Formal coverage does not automatically extend to Parts II or III. The companion supplies the exact targets, assumptions and specialization boundaries.')
para(p,'The current checks, historical compiler evidence', 'The worked atlas follows the mathematical development through exact finite models and analytical examples. Calculations illustrate stated ranges and assumptions. Their computational records remain distinct from both the written proofs and the formal declarations.')
para(p,'The final mathematical audit makes explicit', 'Contour winding, positive memory decay, finite moment closure and eventual absorption each require the hypotheses stated with their results. When the spaces vary along a refinement system, summability must be read in the specified ambient setting.')
replace(p,'The complete released 33-result formal core','The thirty-three-result formal core')
replace(p,'the exact released formal contract','the exact formal contract')
replace(p,'The released formal core','The formal core')
replace(p,'The finite numerical release verifies their Gaussian orthogonality through quadrature.','The numerical study checks their Gaussian orthogonality through quadrature.')
replace(p,'All calculations in this release were run on CPU.','The recorded calculations were run on CPU.')
replace(p,'The full implementation, tests, tables, figure-generation code, and exact numerical record are included with the release rather than embedded in the typeset paper.','The source corpus contains the implementation, tests, tables, figure-generation code and numerical records.')

p=main('VII')
replace(p,'Reading this edition','Reading this chapter')
para(p,'The original finite item numbers keep', 'The finite results use the prefix I. The bounded development uses II, and the supplementary constructions use III. This local numbering distinguishes their hypotheses and provides stable references throughout the chapter. Some constructions appear in more than one setting because the ambient spaces and conclusions differ.')
para(p,'The selected archived formal checkpoint covers', 'The formal companion covers nineteen scoped manuscript items through 323 supporting Lean theorem declarations in twenty-five modules. The bounded development in Part II is outside that nineteen-item contract. The companion states the exact hypotheses, source declarations and verification provenance.')
replace(p,'Corrected finite quantum seed calculus','Finite quantum seed calculus')
replace(p,'Mathematical proof completions and retained derivations','Bundle constructions and complementary derivations')
p=ROOT/'VII/editable/traditional/parts/01_finite_core.tex'
para(p,'The original manuscript reports CPU experiments', 'The numerical study reports CPU experiments and a suite of 22 tests. The values below come from the accompanying numerical record. They are separate from the 323 supporting declarations in the formal companion. A displayed floating-point residual of zero describes the reported computation and does not independently prove equality in exact arithmetic.')
p=ROOT/'VII/editable/traditional/parts/03_supplement_01.tex'
para(p,'The proof of the general block inverse was reused', 'The general block inverse uses the same finite identity as the Schur--Feshbach construction in Chapter VI. Its formal specialization and the counterexample above are included in the Chapter VII source. The identity is read with both stated invertibility assumptions.')
replace(p,'\\subsection{Provenance and limits}','\\subsection{Relation to memory and limits}')

p=main('VIII')
replace(p,'Reading this edition','Reading this chapter')
para(p,'All seven retrieved mathematical source parts', 'The main argument keeps its local section and item numbers. Appendices A--F give the additional constructions and proofs for exact semantics, compilation, structured transforms, scheduling and small-core recompression. These developments make assumptions and intermediate objects explicit when a shorter main-text argument leaves them implicit.')
para(p,'The selected v0.6.0 formal checkpoint records', 'The formal companion covers all 56 finite manuscript-proved items under their stated hypotheses. Its 392 supporting theorem declarations span 40 modules, including 19 reused quantum-packet declarations. The 66 construction audits and four classical inputs are tracked separately. The companion supplies the declaration map and the provenance of the recorded compiler evidence.')
para(p,'The historical pending statements in Appendices A--E', 'Appendices A--F complete the finite development under its stated hypotheses. Three broader targets remain open: unrestricted discovery, compilation with nonlocal overlapping models, and a packet-native communication theorem for a specified architecture. The exact examples and visual atlas illustrate finite mathematics. They add no hardware performance claim and do not replace the proofs.')
replace(p,'All six supplementary proof developments follow as Appendices A--F.','Six supplementary proof developments follow as Appendices A--F.')
p=ROOT/'VIII/editable/traditional/parts/01_manuscript.tex'
replace(p,'The release contains a small reference implementation','The source corpus contains a small reference implementation')
replace(p,'The strengthened release records','The accompanying verification record reports')
replace(p,'Verification layers in the strengthened release.','Verification layers for the supplied implementation.')

# Explicit plate labels replace opaque V32-like shorthand; destinations stay fixed.
active=json.loads((BOOK/'editorial/book_revision/v_viii_active_sources.json').read_text())
for key,paths in active.items():
 n=key.split('_')[0]
 for name in paths:
  p=Path(name)
  if any(x in p.parts for x in ['graphics','visual_graphics','generated']):continue
  s=p.read_text();t=s
  t=re.sub(r'\bV(?:--)?([0-9]+)\b',lambda m:'Plate '+n+'.'+m[1],t)
  t=t.replace('V#1','Plate '+n+'.#1').replace(r'V\,--\,#1','Plate '+n+'.#1')
  t=t.replace('The labels Plate '+n+'.1 through Plate '+n+'.','Plates '+n+'.1 through '+n+'.')
  t=t.replace('The identifiers Plate '+n+'.1--Plate '+n+'.','Plates '+n+'.1--'+n+'.')
  t=re.sub(r'Plate '+n+r'\.(\d+) to Plate '+n+r'\.(\d+)',lambda m:'Plates '+n+'.'+m[1]+'--'+n+'.'+m[2],t)
  t=t.replace('Visual pages','Plates')
  if t!=s:write(p,t,'Expand visual-plate shorthand using chapter-qualified labels; preserve anchors and mathematics')

# Named mathematical references replace version-only pointers in both atlas presentations.
for rel in ['VII/editable/traditional/monograph_atlas.tex','VII/editable/visual_guide/source/pages.tex']:
 p=ROOT/rel
 replace(p,'saved v0.6.0 supplement, pp. 2--4.','Part III, Sections III.16--III.18 (range-bundle construction).')
 replace(p,'The v0.6.0 supplement proves','The range-bundle construction in Part III proves')
 replace(p,'Saved formal scope: v0.6.0 ledger and completion supplement.','Formal scope: the nineteen-result correspondence in the Lean companion.')
 replace(p,'This is the corrected hypothesis set recorded in the formal release.','These are the hypotheses used in the formal companion.')
 replace(p,'The formal release records this limit of the diagnostic.','The formal companion makes this limit of the diagnostic explicit.')
 replace(p,'Saved Lean release &','Formal companion &')
 para(p,'The saved formal checkpoint is v0.6.0:', 'The formal companion records 323 supporting theorem declarations in 25 modules for nineteen scoped finite items. The range-bundle construction and the finite examples have the distinct hypotheses stated in their respective treatments. Source and verification records identify the evidence for each claim.')
for rel in ['VII/editable/traditional/monograph_atlas.tex','VII/editable/visual_guide/source/extended_pages.tex']:
 p=ROOT/rel
 replace(p,'The saved v0.6.0 ledger lists 19 finite items with their recorded hypotheses.','The formal correspondence lists nineteen finite items with their stated hypotheses.')
for rel in ['VIII/editable/traditional/atlas_sources/pages.tex','VIII/editable/visual_guide/source/pages.tex']:
 p=ROOT/rel
 replace(p,'The sixth release constructs','The small-core recompression construction in Appendix F constructs')
 para(p,'The preserved v0.6.0 release records', 'The formal companion covers 56 finite manuscript-proved items through 392 supporting theorem declarations in 40 modules. Nineteen declarations are reused foundation results. The 66 construction audits are counted separately. Compiler records and source identities are provided with the formal companion.')
 replace(p,'The release verification report records','The verification report records')

# Reading introductions to the formal companions identify evidence without host-relative claims.
for n in ['V','VI','VII','VIII']:
 p=main(n,'lean_guide')
 s=p.read_text()
 if n=='V':s=s.replace('Kernel execution evidence is inherited from the v1.1.0 release dated 6 September 2026. No new Lean build was run for this companion edition.','Kernel execution evidence comes from the recorded formal-core build. Its toolchain, source identities and replay instructions appear in the reproduction section. This reading guide does not claim a new kernel execution.')
 if n=='VI':s=s.replace('Kernel execution evidence is inherited from the v0.5.0 release dated 6 September 2026. This edition reconciles source bytes, declaration locations, saved axiom records, and current finite computations. No fresh Lean compilation was run.','Kernel execution evidence comes from the recorded thirty-three-result formal-core build. Source identities, declaration locations, axiom records and finite computations are tracked separately. This reading guide does not claim a new kernel execution.')
 if n=='VII':s=s.replace('Kernel execution evidence is inherited from the v0.6.0 release dated 6 September 2026. This edition checks the correspondence between the source files, declaration locations, saved axiom records, and printed excerpts. It also describes the finite computations recorded on 9 October 2026. The present proofreading pass did not rerun those computations or compile Lean.','Kernel execution evidence comes from the recorded nineteen-result formal-core build. The guide identifies the source files, declaration locations, saved axiom records and printed excerpts. Finite computations and their dates are documented in the reproduction section. This reading guide does not claim a new kernel execution.')
 if n=='VIII':s=s.replace('The preserved run completed on 6 September 2026. It records successful cumulative compilation and axiom audits. This documentation edition freshly checks source identity, saved logs, declaration names, exact excerpts, and PDF construction. Lean and Lake are unavailable on this host; there is no new kernel execution in this edition.','The recorded formal run contains successful cumulative compilation and axiom audits. Source identities, saved logs, declaration names and exact excerpts identify the scope of that evidence. The reproduction section supplies the toolchain and replay procedure. This reading guide does not claim a new kernel execution.')
 write(p,s,'Replace dated opening narrative and host-relative claims with precise evidence references')
p=ROOT/'VI/editable/lean_guide/generated/result_ledger.tex'
replace(p,'Complete scoped statement (inherited v0.5.0 ledger).','Complete scoped statement in the formal-core correspondence.')
p=ROOT/'VII/editable/lean_guide/chapters/reading.tex'
para(p,'The source base is the unchanged v0.6.0 snapshot.', 'The formal source distinguishes three constructions that should not be conflated. Orthogonal syndrome data permit direct recovery. General positive Gram data require spectral reduction and a necessity proof. The range-bundle construction supplies local charts and global manifold curvature. This guide follows the resulting declarations and makes their differing assumptions explicit.')

(BOOK/'editorial/book_revision/v_viii_edit_journal.json').write_text(json.dumps(JOURNAL,indent=2)+'\n')
print(json.dumps({'changes':len(JOURNAL),'files':len({x['path'] for x in JOURNAL})}))
