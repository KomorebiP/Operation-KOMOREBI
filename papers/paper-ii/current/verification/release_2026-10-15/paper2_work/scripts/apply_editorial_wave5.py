from pathlib import Path
import hashlib,json,difflib
root=Path('/workspace/scratch/9f53d520971c');r=root/'release_package/Komorebi_Paper_II_Release_2026-10-15';b=root/'paper2_work/editorial_before_wave5';b.mkdir(exist_ok=True)
changes=[];originals={};sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def change(rel,before,after,why):
 p=r/rel;s=p.read_text();assert s.count(before)==1,(rel,s.count(before),before[:60])
 if rel not in originals:
  originals[rel]=s;backup=b/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(s)
 n=s.replace(before,after);p.write_text(n);changes.append({'source':rel,'before':before,'after':after,'reason':why,'before_sha256':sha(s),'after_sha256':sha(n)})
def setfile(rel,text,why):
 p=r/rel;s=p.read_text() if p.exists() else ''
 if rel not in originals:originals[rel]=s;backup=b/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(s)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);changes.append({'source':rel,'before':s,'after':text,'reason':why,'before_sha256':sha(s),'after_sha256':sha(text)})
for folder,stem in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]:
 rel=f'editable/{folder}/Paper_II_{stem}_Final.tex'
 change(rel,'\\KomorebiSetup','\\renewcommand{\\KomorebiEdition}{15 October 2026}\n\\KomorebiSetup','Current edition date, preserving house style.')
change('editable/traditional/Paper_II_Traditional_Final.tex','The Lean guide follows the preserved 25 row formal contract. Each guide records its own evidence and scope.','The Lean guide distinguishes the current formal development from the inherited 25-row walkthrough. Each guide records its evidence and scope.','Current versus historical guide boundary.')
change('editable/traditional/Paper_II_Traditional_Final.tex','The visual atlas and the separate Lean guide provide worked models and the complete formal contract crosswalk.','The visual atlas and the separate Lean guide provide worked models and separate current and inherited formal crosswalks.','Avoid equating old map with complete current scope.')
setfile('editable/traditional/chapters/07_scope.tex',r'''\section{Edition and proof scope}\label{sec:edition-scope}
The traditional article is a single edition organized by topic. The expanded branch supplies the written proofs of common refinements, complete filtered inversion, lattice gluing, rectangular Smith congruences, and analytic and multilevel defects. The canonical v1.2.1 release supplies the inherited specializations, finite graph construction, worked realizations, and three algorithm specifications.

\input{generated/current_scope.tex}

The inherited Lean contract has 25 rows: 21 canonical numbered items, one Smith-phase identity, and three algorithm specifications. It remains a dated source contract. The current correspondence separately records the exact present statements, proof targets, source hashes, and execution evidence. A row may use several declarations, and several source labels may refer to one written theorem; these are distinct counting units.

The original branch sources and historical reports remain preserved. The current editorial log records the hypothesis, notation, and endpoint clarifications, including the verified rectifiable-cycle citation. Current navigation metadata records printed pages and PDF destinations. Historical proof-preservation reports retain their original scope and date; they do not describe later edited proof text.

The visual guide gives exact worked models. The Lean guide opens with the current proof scope and then explains the inherited declaration-level contract. Illustrations and finite checks support understanding and implementation. Universal claims depend on their written proofs and the exact formal statements where coverage is recorded.

This monograph includes the twenty-four worked plates after this account of the proof scope. Their statement references use the printed pages of this volume. The separate visual guide contains the same models for readers who want to follow the examples on their own.
''','Current source and inherited provenance are described separately, with generated current status.')
setfile('editable/traditional/generated/current_scope.tex',r'''\textbf{Current verification snapshot (15 October 2026).} The current Lean project is \texttt{formal/current/}. New proof modules and their individual strict checks are recorded in the current correspondence. Aggregate replay and final source review remain pending. The general rectifiable-cycle representation and independence bridge for the canonical holomorphic functional calculus remains incomplete in Lean. The written theorem retains its full statement and the verified Conway reference.
''','Explicit provisional current status, pending runtime-generated evidence update.')
change('editable/traditional/chapters/03_weighted.tex','The formal contract does not assert convergence for every complete filtered algebra. Such an assertion needs a separately specified\ntopology and completeness theorem. The release proves the result in finite\nquotients above and the contraction specialization for complete normed rings.','The inherited finite-word contract proves the result in the finite quotients above and in the contraction specialization for complete normed rings. The complete filtered statement has its own separation and inverse-limit completeness hypotheses. Its current Lean coverage is recorded separately in the current correspondence.','Describe the inherited interface without denying later completed-filtered work.')
change('editable/traditional/chapters/04_arithmetic.tex','The formal theorem begins with the evaluated\ncertificate.','The inherited certificate theorem begins with the evaluated\ncertificate.','Scope this sentence to the actual older interface.')
change('editable/traditional/chapters/04_arithmetic.tex','In the Lean development this general form takes those\ncoordinate facts as explicit certificates supplied to the abstract product','In the inherited abstract Lean interface this general form takes those\ncoordinate facts as explicit certificates supplied to the abstract product','Keep supplied-certificate scope local to inherited interface.')
# Current guide front matter and explicit historical framing.
rel='editable/lean_guide/Paper_II_Lean_Guide_Final.tex'
change(rel,'A guide to the preserved formal contract, its declarations and boundaries, with exact source excerpts and reproducible static checks.','Current formal scope and evidence, followed by the inherited declaration-level walkthrough and exact source excerpts.','Current cover description.')
s=(r/rel).read_text();start=s.index('\\KomorebiOpeningNote{');end=s.index('\n\n\n\\tableofcontents',start)
change(rel,s[start:end],r'''\KomorebiOpeningNote{This guide separates the current formal development from the inherited 25-row contract. The current overview records exact source scope and verification status. The later walkthrough preserves the canonical source architecture, representative proofs, and historical evidence with their original boundaries.
\medskip
\input{generated/current_opening.tex}}''','Current overview replaces globally stale no-new-replay claim; historical evidence remains below.')
change(rel,'\\input{chapters/01_orientation.tex}','\\input{generated/current_release.tex}\n\\clearpage\n\\input{chapters/01_orientation.tex}','Add current status before historical tutorial.')
change(rel,'\\section{The complete contract of 25 rows}','\\section{The inherited contract of 25 rows}','Historical table title.')
change(rel,'\\input{generated/traditional_crosswalk.tex}','\\input{generated/current_traditional_crosswalk.tex}','Current navigation separate from preserved historical generated table.')
change(rel,'The source project remains unchanged. Editing this guide cannot by itself repair or strengthen a Lean theorem.','The historical source snapshot remains preserved. Current additions live in the separate current project and are indexed in the current correspondence. Editing this guide cannot by itself repair or strengthen a Lean theorem.','Avoid false current source-unchanged claim.')
change('editable/lean_guide/chapters/01_orientation.tex','\\section{What this guide verifies and teaches}','\\section{Reading the inherited formal walkthrough}','Historical framing for chapter.')
change('editable/lean_guide/chapters/01_orientation.tex','The formal component is version 1.1.1, preserved within canonical manuscript release 1.2.1.','The component described in this walkthrough is the historical version 1.1.1, preserved within canonical manuscript release 1.2.1. Current additions and their boundaries are recorded in Section~\\ref{sec:current-release}.','Explicit temporal and source scope.')
change('editable/lean_guide/chapters/01_orientation.tex','The main entry point is \\code{import KomorebiVerification.PaperII}. It imports the eight substantive modules but not the audit command.','In the historical snapshot, the main entry point is \\code{import KomorebiVerification.PaperII}. It imports the eight substantive modules but not the audit command.','Historical eight-module count.')
change('editable/lean_guide/chapters/05_defects.tex','Those additional written results remain ordinary proofs in this edition. The formal contract can be complete while the broader traditional theorem inventory has a different coverage boundary.','Those additional results are outside this inherited map. The current extension status, including its remaining analytic bridge, is recorded in Section~\\ref{sec:current-release}.','Remove obsolete current-edition boundary while preserving historical map scope.')
rel='editable/lean_guide/chapters/06_replay.tex'
change(rel,'\\section{Reproducing the formal project}','\\section{Reproducing the historical formal project}','Historical replay heading.')
change(rel,'Consequently this edition does not claim a fresh compiler replay, a fresh environment scan, or an identity chain from the source to the transcripts that the supplied artifacts do not contain.','Consequently the historical component alone does not establish a fresh compiler replay, a fresh environment scan, or an identity chain to missing transcripts. Current execution evidence is reported separately in Section~\\ref{sec:current-release}.','Keep historical missing-transcript limitation local.')
change(rel,'The guide\'s PDF build and visual review are new publication checks. They verify rendering, references, fonts, line overflow, page coverage, and consistency of the guide\'s data files. They do not add mathematical formalization coverage. The complete generated audit records \\code{lean_compiler_run: false} explicitly.','The historical guide audit records PDF and static source checks, including \\code{lean_compiler_run: false}. Current PDF checks and current Lean replay are separate evidence records. A document build verifies rendering and navigation; formal coverage depends on the current source types and their own compiler evidence.','Avoid conflating old static audit with new Lean checks.')
# Identical atlas prose in both current editions.
for rel in ['editable/traditional/visual_atlas.tex','editable/visual_guide/source/pages_final.tex']:
 change(rel,'% Exact worked exposition. The original manuscript and Lean sources are unchanged.','% Worked exposition inherited from the earlier edition; current navigation and scope are synchronized.','Correct source header scope.')
 change(rel,'Formal source: v1.2.1 / Lean component v1.1.1 / 25-row scoped contract','Formal evidence: current correspondence and the inherited 25-row contract','V24 current locator.')
 change(rel,'Its recorded Lean evidence is preserved unchanged. This guide adds explanatory models, not a new claim that every illustrative calculation has been formalized in Lean.','Its dated source and evidence remain preserved. Current proof additions have a separate correspondence and replay record. The visual models illustrate the mathematics; their finite checks have their own recorded ranges.','Current versus historical proof map distinction.')
 change(rel,'The new source contains \\textbf{118 named exact checks}.','The preserved model source contains \\textbf{118 named exact checks}.','Date finite checks accurately.')
 change(rel,'For the preserved final release, the Python suite was rerun in an isolated working directory:','The historical monograph report records an isolated Python replay:','Attribute inherited computations to their report.')
 change(rel,'These checks are not a fresh Lean build. The traditional companion integrates the expanded mathematics and records its local hypothesis corrections. The inherited 25-row formal contract retains its original scope.','These are finite computation records. Current Lean replay and source coverage are recorded separately. The inherited 25-row contract retains its original scope; the current correspondence identifies additional proofs and remaining bridges.','Keep current scope honest without stale no-new-compile statement.')
rel='editable/visual_guide/Paper_II_Visual_Guide_Final.tex'
change(rel,'The Lean guide provides the separate formal contract.','The Lean guide separates current formal coverage from the inherited contract.','Current guide navigation.')
change(rel,'separate theorem map. No new kernel compilation is claimed here.','current correspondence and the inherited theorem map. Each compiler claim belongs to its dated source-and-log record.','Evidence scope without obsolete global compiler claim.')
change(rel,'\\hypertarget{vpage#1}{}\\label{visual:#1}','\\hypertarget{vpage#1}{}\\phantomsection\\label{visual:#1}','Create exact current visual label anchors, matching integrated atlas fix.')
# Temporary generated current overview; refreshed from the current correspondence before building.
setfile('editable/lean_guide/generated/current_opening.tex',r'''\textbf{Current snapshot (15 October 2026).} New strict module checks and semantic reviews accompany the current project. Aggregate replay and final certification remain pending. The canonical general rectifiable holomorphic-calculus bridge remains incomplete.
''','Provisional current opening, to be regenerated from actual evidence.')
setfile('editable/lean_guide/generated/current_release.tex',r'''\section{Current formal scope and evidence}\label{sec:current-release}
The current project is \code{formal/current/}. Its correspondence records exact current source statements, proof targets, source hashes, and the evidence attached to each claim. The inherited 25-row source contract is preserved separately and is explained in the rest of this guide.

\input{generated/current_opening.tex}

The mathematical proof of the general holomorphic functional-calculus statement uses the verified rectifiable-cycle form of Conway's theorem. The current Lean contour-integral core and the canonical representation and independence bridge have distinct proof obligations. The remaining bridge must be proved before the full statement receives kernel coverage.

Current modules include exact refinement constructions, scalar and multigraded transfer identities, resultant constructions, polynomial and multilevel defects, and analytic integral identities. Each module's exact hypotheses and construction burden are recorded in the current correspondence. New finite sums and inverses marked \code{noncomputable} provide mathematical definitions, not an extracted executable solver.

\textbf{Reproduction.} Keep the current project's toolchain, dependency manifest, aggregate imports, strict compiler flags, and source hashes together. A per-module draft check certifies only its recorded source hash. Adapted production imports require a new whole-source replay. The final current receipt must identify the exact promoted sources and kernel audit; it cannot be inferred from the historical counts below.
''','Provisional current overview; detailed current table generated after map snapshot.')
# Initial navigation table copied, then refresh script updates from new traditional aux.
p=r/'editable/lean_guide/generated/current_traditional_crosswalk.tex';old=r/'editable/lean_guide/generated/traditional_crosswalk.tex';setfile(str(p.relative_to(r)),old.read_text(),'Separate current navigation table ready for actual current build refresh.')
report={'schema':'komorebi.paper_ii.editorial_wave5.v1','status':'APPLIED_CURRENT_STATUS_PROVISIONAL','changes':changes,'authoring_marker':'Already run exactly once before wave1.','formal_scope_status_changes':True,'scope_policy':'Only explicit current-versus-historical framing and pending state. No whole-release certification; actual correspondence and aggregate replay will drive subsequent generated status.'}
(root/'paper2_work/audit/editorial_wave5.json').write_text(json.dumps(report,indent=2)+'\n')
d=[]
for rel,old in originals.items():d.extend(difflib.unified_diff(old.splitlines(True),(r/rel).read_text().splitlines(True),fromfile=rel+' (before)',tofile=rel+' (after)'))
(root/'paper2_work/audit/editorial_wave5.diff').write_text(''.join(d))
print(json.dumps({'changes':len(changes),'files':len(originals)}))
