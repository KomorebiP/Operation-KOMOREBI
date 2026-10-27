from pathlib import Path
import json,re,shutil,hashlib
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/rhythm_review';B=E/'iii_iv_before';j=[]
SEMI='Replace an unnecessary prose semicolon with a grammatical sentence boundary; retain the same claims and proof order.'
HYPH='Use a natural prepositional phrase or unhyphenated noun phrase instead of a nonessential hyphenated modifier.'
RHY='Remove formulaic emphasis or editorial padding while retaining the mathematical statement and scope.'
def edit(f,changes):
 p=R/f;a=p.read_text();s=a
 for old,new,why in changes:
  assert old in s,(f,old)
  for m in re.finditer(re.escape(old),s):j.append({'file':f,'old':old,'new':new,'rationale':why,'line_before_at_step':s[:m.start()].count('\n')+1})
  s=s.replace(old,new)
 if s!=a:
  bp=B/f;bp.parent.mkdir(parents=True,exist_ok=True);assert not bp.exists();shutil.copy2(p,bp);p.write_text(s)
p='source_i_iv/III/manuscript/'
edit(p+'chapters/01_finite_coordinates.tex',[
 ('\\leanname{explicitWordExpansion_succ}; the two bridge equalities then yield','\\leanname{explicitWordExpansion_succ}. The two bridge equalities then yield',SEMI),
 ('\\leanname{LinearEquiv.trans}; the displayed formulas use the\nequivalent right-to-left function-composition notation','\\leanname{LinearEquiv.trans}. The displayed formulas use the\nequivalent right-to-left notation for function composition',SEMI+' '+HYPH),
 ('$J^X_{a\\leftarrow b}J^X_{b\\leftarrow a}=\\id$; interchanging $a$ and $b$','$J^X_{a\\leftarrow b}J^X_{b\\leftarrow a}=\\id$. Interchanging $a$ and $b$',SEMI),
 ('The matrix-product sum has exactly','The sum defining the matrix product has exactly',HYPH)])
edit(p+'chapters/02_connections_obstructions.tex',[
 ('global flatness trivializes both;\nit does not identify','global flatness trivializes both.\nIt does not identify',SEMI),
 ('\\cref{thm:J-cocycle}; apply \\cref{thm:defect-holonomy}.','\\cref{thm:J-cocycle}. Apply \\cref{thm:defect-holonomy}.',SEMI),
 ('uses the canonical cocycle twice; the second uses','uses the canonical cocycle twice. The second uses',SEMI),
 ('$J$ of \\cref{def:canonical-J}; \\cref{prop:set-naturality} makes that defect','$J$ of \\cref{def:canonical-J}. By \\cref{prop:set-naturality}, that defect is',SEMI),
 ('The input case is the agreement hypothesis;\nthe constant case is reflexive; the unary case applies the induction\nhypothesis to its child; and the binary case applies it independently to the','The input case is the agreement hypothesis.\nThe constant case is reflexive. The unary case applies the induction\nhypothesis to its child. The binary case applies it independently to the',SEMI),
 ('a dependent inductive typed tree; no such declaration','a dependent inductive typed tree. No such declaration',SEMI),
 ('preservation of input-slot order','preservation of the order of input slots',HYPH)])
edit(p+'chapters/04_correction_transport.tex',[
 ('$W(0)=I$; uniqueness of this bounded linear equation gives','$W(0)=I$. Uniqueness of this bounded linear equation gives',SEMI)])
for f in [p+'visual_atlas.tex','source_i_iv/III/guides/visual/source/pages_final.tex']:
 edit(f,[('Most importantly,','Conjugation also gives',RHY)])
l='source_i_iv/III/guides/lean/'
edit(l+'Paper_III_Lean_Guide_Final.tex',[
 ('Read source-exact proof excerpts','Read exact excerpts from the proofs',HYPH),
 ('A locator connects related presentations; it does not certify','A locator connects related presentations. It does not certify',SEMI)])
edit(l+'chapters/00_current_release.tex',[
 ('The product of input-projector norms','The product of norms of the input projectors',HYPH),
 ('identifies their status individually; these review counts','identifies their status individually. These review counts',SEMI),
 ('support the examples and implementations; they do not replace','support the examples and implementations. They do not replace',SEMI),
 ('no matching Lean sources were recovered; that account remains','no matching Lean sources were recovered. That account remains',SEMI),
 ('These boundaries leave a complete mathematical reading edition with a precisely identified formal core and continuation. ','',RHY)])
edit(l+'chapters/01_orientation.tex',[
 ('They do not replace a Lean execution; the opening chapter','They do not replace a Lean execution. The opening chapter',SEMI)])
edit(l+'chapters/07_replay.tex',[
 ('does not establish warning rejection; the recorded compiler controls','does not establish warning rejection. The recorded compiler controls',SEMI)])
edit('source_i_iv/III/docs/Paper_III_Section17_Analytic_Closeout.tex',[
 ("complex Fr\\'echet derivatives; the integral below","complex Fr\\'echet derivatives. The integral below",SEMI),
 ('only on the zero space; its coordinate product','only on the zero space. Its coordinate product',SEMI),
 ('directions are listed by increasing index; blocks may be listed','directions are listed by increasing index. Blocks may be listed',SEMI),
 ('multilinear outer jet; a zero outer jet','multilinear outer jet. A zero outer jet',SEMI),
 ('then $\\Y=0$; for $n\\ge1$','then $\\Y=0$. For $n\\ge1$',SEMI),
 ('The zero-space case follows','The case of the zero space follows',HYPH),
 ('the input-index sum has exactly one term','the sum over input indices has exactly one term',HYPH),
 ('the four block-count contributions','the four contributions for each block count',HYPH)])
v='source_i_iv/IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/'
edit(v+'traditional/Paper_IV_Traditional_Final.tex',[
 ('$1\\leq m\\leq N$; the excluded factor is','$1\\leq m\\leq N$. The excluded factor is',SEMI),
 ('$m\\geq0$; then','$m\\geq0$. Then',SEMI),
 ('\\cref{thm:large_zero_strings}; for $N=2$, use','\\cref{thm:large_zero_strings}. For $N=2$, use',SEMI),
 ('the pinned-source replay, declaration-kind checks','the replay using pinned sources, declaration-kind checks',HYPH)])
edit(v+'traditional/atlas-pages.tex',[
 ('its pinned-source replay','its replay using pinned sources',HYPH),
 ('Model-driven regeneration reproduced','Regeneration from the models reproduced',HYPH)])
edit(v+'lean_guide/Paper_IV_Lean_Guide_Final.tex',[
 ('the pinned-source replay and its precise scope','the replay using pinned sources and its precise scope',HYPH),
 ('A newer compatible-looking Mathlib revision','A newer, apparently compatible Mathlib revision',HYPH)])
edit(v+'lean_guide/chapters/01_orientation.tex',[
 ('the separate pinned-source replay of all','the separate replay using pinned sources for all',HYPH),
 ('A two-line proof of the final Hadamard identity','A proof of the final Hadamard identity in two lines',HYPH)])
edit(v+'lean_guide/chapters/02_algebra.tex',[
 ("over the source's commutative-semiring context","in the source's context of a commutative semiring",HYPH)])
edit(v+'lean_guide/chapters/03_analytic.tex',[
 ('the initial-data matrix is the identity','the matrix of initial data is the identity',HYPH),
 ('the corresponding solution-space realization','the corresponding realization of the solution space',HYPH),
 ('the analytic finite-algebra identity','the analytic identity in a finite algebra',HYPH),
 ('A bivariate formal-series addition law','A bivariate addition law for formal series',HYPH)])
edit(v+'lean_guide/chapters/05_products.tex',[
 ('the already-defined coefficients equal','the coefficients already defined equal',HYPH),
 ('backed by finite-compression convergence','backed by convergence of finite compressions',HYPH)])
edit(v+'lean_guide/chapters/08_replay.tex',[
 ('The complete nine-package revision table','The complete revision table for the nine packages',HYPH),
 ('the three-item permitted set','the permitted set of three axioms',HYPH),
 ('compiler controls; the 119 mathematical source files','compiler controls. The 119 mathematical source files',SEMI),
 ('its exact archive-entry checks can be included','its exact checks of archive entries can be included',HYPH),
 ('for archive-entry checks','for checks of archive entries',HYPH),
 ('those historical finite-test totals','those historical totals from finite tests',HYPH)])
edit(v+'lean_guide/chapters/09_verification_scope.tex',[
 ('passed a pinned-source replay','passed a replay using pinned sources',HYPH),
 ('the exact inherited statement contract; it does not supply','the exact inherited statement contract. It does not supply',SEMI),
 ('an initially empty project-object directory','an initially empty directory for project objects',HYPH),
 ('the completed production closure; the original audit source','the completed production closure. The original audit source',SEMI),
 ('contribute to these totals; the totals are not counts','contribute to these totals. The totals are not counts',SEMI),
 ('the actual 836-file preserved tree; it does not require','the actual 836-file preserved tree. It does not require',SEMI),
 ('before and after the finite replay; results and logs','before and after the finite replay. Results and logs',SEMI),
 ('stored evidence and file integrity; it does not rerun','stored evidence and file integrity. It does not rerun',SEMI),
 ('clarification of reciprocal powers; no older editable source','clarification of reciprocal powers. No older editable source',SEMI),
 ('a 300-second per-command deadline','a 300-second deadline for each command',HYPH),
 ('a native-Windows or general cross-platform reproducibility claim','a claim of reproducibility on native Windows or across platforms',HYPH)])
(E/'iii_iv_journal.json').write_text(json.dumps(j,indent=2)+'\n')
print('Edited',len({x['file'] for x in j}),'files;',len(j),'exact occurrence entries.')
