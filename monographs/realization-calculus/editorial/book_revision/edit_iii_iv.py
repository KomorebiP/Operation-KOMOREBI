from pathlib import Path
import json, hashlib, re, shutil
R=Path(__file__).resolve().parents[2]; S=R/'source_i_iv'; backup=S/'book_revision_before'
changes=[]; reviewed=[]
def edit(rel, pairs, transform=None):
 p=S/rel; preserved=backup/rel; before=(preserved if preserved.exists() else p).read_text(); after=before; local=[]
 for old,new in pairs:
  n=after.count(old)
  if not n: raise ValueError(f'Absent replacement in {rel}: {old[:100]}')
  after=after.replace(old,new); local.append({'old':old,'new':new,'count':n})
 if transform:
  after, extra=transform(after); local.extend(extra)
 reviewed.append(rel)
 if after!=before:
  b=backup/rel; b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists(): shutil.copy2(p,b)
  p.write_text(after)
  changes.append({'file':rel,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest(),'edits':local})
III='III/'; IV='IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/'
cover=[(r'\KomorebiKind\par\KomorebiEdition\par',r'\KomorebiKind\par')]
def plates(s,roman):
 # Exact prose references only: matches V followed by one or two digits as a word.
 pat=r'\bV([1-9][0-9]?)\b'; found=re.findall(pat,s)
 return re.sub(pat,lambda m:'Plate '+roman+'.'+m[1],s),([{'kind':'displayed_plate_reference','roman':roman,'count':len(found)}] if found else [])
edit(III+'manuscript/Paper_III_Traditional_Final.tex',cover+[
 ('Formal contract: Paper III v1.0.1.','Formal contract: finite algebraic core.'),
 ('Part I retains the finite v1.0.1 formal contract. Part II gives the strengthened nonlinear and analytic development with ordinary proofs. The release also verifies','Part I develops the finite algebraic core under its declaration-level formal contract. Part II gives the nonlinear and analytic development with ordinary proofs. The accompanying formal development verifies'),
 ('Formal coverage stays attached to the released declarations.','Formal coverage stays attached to the identified declarations.'),
 ('This release presents','The paper presents'),
 ('The accompanying release record gives the exact source and scope of each formal verification.','The companion Lean and evidence guide gives the exact source and scope of each formal verification.')],lambda s:plates(s,'III'))
edit(III+'manuscript/chapters/01_finite_coordinates.tex',[
 ('The finite release supplies','The finite algebraic core supplies'),
 ('The thirty original result environments and their proof bodies are retained.','The finite contract covers thirty result environments.'),
 ('The preserved v1.0.1 release records Lean v4.34.0-rc2','The finite algebraic formalization uses Lean v4.34.0-rc2'),
 ('The current release rebuilds the Paper III source at these exact pins and records fresh kernel replay and axiom checks.','The accompanying verification record includes compilation at these exact pins, kernel replay, and axiom checks.'),
 ('the released Paper III module','the identified Paper III module'),
 ('Final theorem denominator','Finite theorem denominator'),
 ('finite v1.0.1 contract','finite algebraic contract')])
edit(III+'manuscript/chapters/02_connections_obstructions.tex',[
 ('the released formal grammar','the finite formal grammar'),
 ('The release verification report records','The Lean and evidence guide records'),
 ('the version 1.0.1 kernel-backed surface','the finite algebraic kernel-backed surface')])
atlas_pairs=[
 ('The worked models originate in the finite algebraic v1.0.1 release. The final traditional paper also develops','The worked models illustrate the finite algebraic core. The main text also develops'),
 ("the finite formal release's scalar interface", "the finite formal contract's scalar interface"),
 ("The finite formal release's forms", "The finite formal contract's forms"),
 ('The release does not require pairwise annihilation','The general formal reconstruction statement does not require pairwise annihilation'),
 ('finite v1.0.1 Lean contract','finite algebraic Lean contract'),
 ('This guide preserves the 24 worked pages and 22 exact figures from the finite visual appendix. It updates their references to the final traditional paper and explains the relation to that paper\'s broader nonlinear and analytic material.',"The 24 worked plates and 22 exact figures connect finite models with the main text's broader nonlinear and analytic theory."),
 ('Finite Lean release & The finite declarations and the released Section 16 and 17 additions','Formal development & The finite declarations and the Section 16 and 17 additions'),
 ('records the current source scope','records the source scope'),
 ('Replay on 20 October 2026 passed all 124 exact checks','The recorded run passed all 124 exact checks'),
 ('The release also records 18,630','The computation record also contains 18,630'),
 ('Use a temporary copy to retain the delivered evidence unchanged. The full package preserves the finite release and its original formal sources separately.','Use a temporary copy to preserve the recorded evidence. The finite algebraic source distribution supplies the formal sources separately.')]
for rel in ['manuscript/visual_atlas.tex','guides/visual/source/pages_final.tex']:
 edit(III+rel,atlas_pairs,lambda s:plates(s,'III'))
edit(III+'guides/visual/Paper_III_Visual_Guide_Final.tex',cover,lambda s:plates(s,'III'))
for rel,rom in [(III+'manuscript/atlas-definitions.tex','III'),(III+'guides/visual/atlas-definitions.tex','III'),(IV+'traditional/atlas-definitions.tex','IV')]:
 edit(rel,[(r'{V#1. #2}',r'{Plate '+rom+r'.#1. #2}'),(r'\color{accent}V#1\quad',r'\color{accent}Plate '+rom+r'.#1\quad'),(r'{V\,--\,#1}',r'{Plate '+rom+r'.#1}')])
edit(III+'docs/Paper_III_Section17_Analytic_Closeout.tex',cover+[
 ('Paper III: Analytic Packet Jets and Release Evidence','Paper III: Analytic Packet Jets and Exact Composition'),
 ('OPERATION KOMOREBI','REALIZATION CALCULUS'),
 (r'{\normalsize Komorebi P. \quad 20 October 2026}\\[9pt]'+'\n'+r'{\small Final mathematical edition \quad $\cdot$ \quad Version 1.0.0}',r'{\normalsize Komorebi P.}'),
 ('The release includes fresh Lean verification','The accompanying formal development verifies'),
 ('verifies for multilinear reconstruction','verifies multilinear reconstruction'),
 ('They are not claimed as new Lean theorems in this release.','They are not included in the accompanying Lean formalization.'),
 (' Version 1.0.0 closes the technical manuscript release under these declared boundaries. No public reuse license is assigned by this supplement.','')])
edit(III+'guides/lean/Paper_III_Lean_Guide_Final.tex',cover+[
 ('A practical guide to the current release and the complete 41-row finite algebraic contract.','A guide to the finite algebraic core, its analytic continuation, and the complete 41-row finite contract.'),
 (r'\textbf{Evidence at this edition.} The release includes a fresh pinned compilation',r'\textbf{Formal evidence.} The verification record includes a pinned compilation'),
 ('The opening release chapter gives their exact scope.','The opening chapter gives their exact scope.'),
 ('Those older counts describe the finite baseline, not the larger current closure.','Those counts describe the finite baseline, not the enlarged ownership closure.'),
 ('authoritative v1.0.1 map','authoritative finite algebraic map'),
 ('The current release adds the continuation and packet calculus modules','The nonlinear and analytic continuation adds the packet calculus modules'),
 ('Current verification sources and receipts are under','Verification sources and receipts are under'),
 (' in the release root.',' in the formal source distribution.')])
edit(III+'guides/lean/chapters/00_current_release.tex',[
 ('The verified release','The formal core and analytic continuation'),
 ('Version 1.0.0 combines the finite algebraic development, exact nonlinear packet coordinates, and a new analytic packet interface. The original mathematical sources were restored in the exact pinned environment. The release then compiled the added packet modules, audited the compiled ownership boundary and transitive axioms, replayed the owned logical declarations into an environment initially containing only upstream dependencies, and exercised the rejection controls.','The formal development combines finite algebraic constructions, exact nonlinear packet coordinates, and an analytic packet interface. Its verification record includes compilation in the pinned environment, an audit of the compiled ownership boundary and transitive axioms, replay of the owned logical declarations into an environment initially containing only upstream dependencies, and rejection controls.'),
 ('Current source','Source module'),('The final evidence record','Compilation and kernel evidence'),
 ('the current ownership closure','the enlarged ownership closure'),('Reproduce the current result','Reproduce the formal verification'),
 ('so the delivered manifest and historical transcripts stay intact','so the recorded manifest and transcripts stay intact'),
 ('The source package preserves an October 16 visual claim of a larger closure as historical material, with its lack of matched source explicitly recorded.','An earlier visual account claimed broader formal coverage, but no matching Lean sources were recovered; that account remains historical material.'),
 (' Public reuse terms remain an author decision, recorded separately from technical verification.','')])
edit(III+'guides/lean/generated/current_receipts.tex',[('The final release compiled','The verification run compiled')])
edit(III+'guides/lean/chapters/01_orientation.tex',[
 ('The opening release chapter records the enlarged current development.','The opening chapter describes the finite core and its analytic continuation.'),
 ('The preserved report, dated 3 September 2026, records','The finite algebraic verification report records'),
 ('For this edition, a Python reader reconciled','A static reconciliation matches'),
 ('These are fresh static checks of the preserved evidence.','These are static checks of the preserved evidence.'),
 ('the opening release chapter separately records the current compiler and replay runs','the opening chapter separately records the compiler and replay runs'),
 ('finite v1.0.1 formal contract','finite algebraic formal contract'),
 ('A section of the final paper','A section of the main text')])
edit(III+'guides/lean/chapters/07_replay.tex',[
 ('This chapter explains the preserved finite release and its historical gates. For the current combined build and replay, use the opening release chapter and','This chapter explains the finite algebraic core and its verification gates. For the combined core and analytic continuation, use the opening chapter and'),
 ('The old namespace counts in the excerpts','The finite namespace counts in the excerpts'),
 ("The edition's verification boundary",'The formal verification boundary'),
 ('The current release chapter separately reports fresh compiler and kernel verification. Its PDF is newly compiled and inspected.','The opening chapter separately reports compiler and kernel verification.'),
 ('finite v1.0.1 contract','finite algebraic contract')])
edit(IV+'traditional/Paper_IV_Traditional_Final.tex',cover+[
 ('Released formal contract: Paper IV v1.0.0.','Formal contract: cyclic analytic theory.'),
 (r'\date{Modern Monograph, 8 October 2026}',r'\date{}'),
 (r'\renewcommand{\KomorebiEdition}{8 October 2026}',r'\renewcommand{\KomorebiEdition}{}'),
 ('The preserved Paper IV v1.0.0 release records full scoped Lean coverage of the sixty-eight theorem like manuscript results under their original hypotheses. This volume changes presentation and adds worked explanations. It does not create a new formal release.','The recorded formal contract covers all sixty-eight theorem-like manuscript results under their stated hypotheses. The formalization ledger identifies the corresponding declarations.'),
 ('Current finite computations support the worked models. The compiler and kernel evidence remains the preserved September release evidence.','Finite computations support the worked models. The companion Lean guide records the pinned-source replay, declaration-kind checks, axiom audit, and their limits.'),
 ('Formalization ledger for version 1.0.0','Formalization ledger'),
 ('The preserved v1.0.0 release was built with Lean 4 v4.34.0-rc2','The recorded formal verification used Lean 4 v4.34.0-rc2'),
 ('The historical warning fatal\nbuild and supplied kernel audit','The recorded build with warnings treated as errors\nand supplied kernel audit'),
 ('The declaration-level theorem map is authoritative for the preserved\nv1.0.0 contract. Its release records full scoped coverage of all 68\ntheorem like records:','The declaration-level theorem map is authoritative for the formal\ncontract. It records full scoped coverage of all 68\ntheorem-like records:'),
 ('genus zero products','genus-zero products'),('zero free domain','zero-free domain')],lambda s:plates(s,'IV'))
edit(IV+'traditional/atlas-pages.tex',[
 ('This guide accompanies the final traditional edition and the Lean guide. Its twenty-six worked pages preserve the mathematical models of the original visual appendix. Final references and evidence descriptions connect those models to the present edition.','These twenty-six worked plates connect explicit mathematical models with the main text and its Lean guide. Each evidence record states the scope of the model, computation, or formal result.'),
 ('Inherited formal record & The v1.0.0 sources, theorem map, dependency pins, saved axiom reports, and original review retain their own scope. The release reports a 68-result contract. No fresh Lean compilation is claimed here.','Formal record & The sources, theorem map, dependency pins, saved axiom reports, and mathematical review retain their own scope. The 68-result contract and its pinned-source replay are described in the Lean guide.'),
 ('Fresh isolated execution passed all','The recorded isolated execution passed all'),
 ('The fresh full suite reproduced','The full suite reproduced'),
 ('Fresh isolated model-driven regeneration reproduced all twenty-four editable TikZ files. Twenty-three remain identical to the original release. On V13, one label was moved down to clear the loop arrow. The mathematical labels and objects are unchanged.','Model-driven regeneration reproduced all twenty-four editable TikZ files. The mathematical labels and objects are preserved.'),
 ('Updated locators refer to the final traditional edition.','Locators refer to the main text.'),
 ('The source package preserves the formal release, proofread review, independent audit, exact certificates, and rebuild instructions. PDF assembly is a separate operation from mathematical verification.','Exact certificates and formal verification records accompany the source. Each retains its stated mathematical scope.')],lambda s:plates(s,'IV'))
edit(IV+'lean_guide/Paper_IV_Lean_Guide_Final.tex',cover+[
 ('distinguish preserved kernel evidence from current static checks','distinguish kernel verification from static reconciliation'),
 ('in the inherited v1.0.0 formal release','in the recorded formal contract'),
 ('This edition explains that release and reconciles its source, contract, theorem map, and saved kernel transcript. The formal execution evidence is dated 5 September 2026. No new Lean build was run for this companion edition.','This guide relates the source, contract, theorem map, and saved kernel transcript. The verification chapter records the pinned-source replay and its precise scope; static reconciliation remains a distinct form of evidence.'),
 ('Each entry is a full scoped result in v1.0.0.','Each entry is a full scoped result in the formal contract.'),
 ('source and the release contract','source and the formal contract')])
edit(IV+'lean_guide/chapters/01_orientation.tex',[
 ('The Lean release follows','The formal development follows'),
 ('Three levels of evidence','Formal verification and source reconciliation'),
 ('Meaning in this edition','Verified scope'),
 ('Inherited formal execution & The 5 September 2026 release reports a warning-fatal build of 3,521 jobs, 43 semantic checks, exact target-kind resolution, and the saved kernel audit.','Formal execution & The source contract is supported by the preserved aggregate build, 43 semantic checks, exact target-kind resolution, and kernel audit. The verification chapter records the separate pinned-source replay of all 118 production modules.'),
 ('Current static reconciliation &','Static reconciliation &'),
 (r'Current document build & XeLaTeX compiles the supplied guide sources. Layout and extracted text are checked. This step does not compile Lean. \\', '')])
edit(IV+'lean_guide/chapters/08_replay.tex',[
 ('The canonical release is v1.0.0, dated 5 September 2026. Its toolchain file specifies','The cyclic analytic formalization\'s toolchain file specifies'),
 ('Current checks for this guide','Static reconciliation'),
 ('No new Lean build was available for this companion edition. The 43 declarations in \\code{SemanticChecks.lean} remain source-level and inherited execution evidence here. They are not relabeled as 43 newly executed tests. The companion edition changes explanatory material and navigation, not the canonical Lean files.','The 43 declarations in \\code{SemanticChecks.lean} are supported by their source and preserved execution evidence. Static reconciliation does not relabel them as newly executed tests. The separate verification chapter records the production replay and compiler controls; the 119 mathematical source files remained unchanged.'),
 ('The new three-companion edition archive is not the original canonical release ZIP. Do not pass it to a gate that expects the original release\'s exact entry set.','Use the exact formal source archive for archive-entry checks. The collected book is a different artifact and does not have that archive\'s entry set.'),
 ('These are replay instructions, not commands claimed to have run in this companion edition.','These commands describe the inherited manual gate. For the verified warning policy and full production replay, use the procedure in the next chapter.')])
for rel in [III+'guides/lean/generated/traditional_crosswalk.tex',IV+'lean_guide/generated/traditional_crosswalk.tex']:
 edit(rel,[(('Final printed locator' if rel.startswith('III/') else 'Final traditional locator'),'Traditional-paper locator')])
(R/'editorial/book_revision/iii_iv_edit_log.json').write_text(json.dumps({'changes':changes,'reviewed_files':reviewed},indent=2))
print('Changed',len(changes),'files;',sum(len(x['edits']) for x in changes),'reviewed edit groups')
