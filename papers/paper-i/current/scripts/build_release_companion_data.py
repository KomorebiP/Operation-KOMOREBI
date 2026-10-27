#!/usr/bin/env python3
"""Generate release-current companion tables from the reviewed coverage inventory.

This script does not invoke Lean and does not change status classifications.
"""
from pathlib import Path
import argparse, collections, hashlib, json, re

ROOT = Path(__file__).resolve().parent
if ROOT.name == 'scripts': ROOT = ROOT.parent
ap = argparse.ArgumentParser()
ap.add_argument('--coverage', required=True, type=Path)
ap.add_argument('--metadata', type=Path)
ap.add_argument('--publication-root', type=Path)
args = ap.parse_args()
if args.publication_root: ROOT = args.publication_root.resolve()
if args.metadata is None and (ROOT/'verification/COMPANION_EVIDENCE.json').exists():
    args.metadata = ROOT/'verification/COMPANION_EVIDENCE.json'
coverage = json.loads(args.coverage.read_text())
records = coverage['records']
assert len(records) == 108 and len({r['stable_id'] for r in records}) == 108
proofs = [r for r in records if r['kind'] in ('theorem','corollary','proposition','lemma')]
assert len(proofs) == 69
counts = collections.Counter(r['status'] for r in proofs)
meta = json.loads(args.metadata.read_text()) if args.metadata else {}
guide = ROOT/'editable/lean_guide/generated'
machine = ROOT/'editable/machine/generated'
guide.mkdir(exist_ok=True); machine.mkdir(exist_ok=True)
def esc(t):
    return ''.join({'⁻¹':r'\ensuremath{^{-1}}','⊗':r'\ensuremath{\otimes}','∘':r'\ensuremath{\circ}','↦':r'\ensuremath{\mapsto}','Φ':r'\ensuremath{\Phi}','→':r'\ensuremath{\to}','ℝ':r'\ensuremath{\mathbb{R}}','×':r'\ensuremath{\times}','≠':r'\ensuremath{\ne}','κ':r'\ensuremath{\kappa}','≥':r'\ensuremath{\ge}','Σ':r'\ensuremath{\Sigma}','∈':r'\ensuremath{\in}','∪':r'\ensuremath{\cup}','σ':r'\ensuremath{\sigma}','⊔':r'\ensuremath{\sqcup}','•':r'\ensuremath{\bullet}','’':"'",'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in re.findall('⁻¹|.', str(t), re.S))
def code(t): return r'\nolinkurl{'+str(t)+'}'
def href(rid): return r'\hyperref[rec:'+rid+']{'+code(rid)+'}'
labels = {}
for r in records:
    for label in re.findall(r'\\label\{([^}]+)\}',r['statement']): labels[label]=r['stable_id']
unresolved=set()
def source(t):
    t=re.sub(r'\\begin\{(?:definition|theorem|corollary|proposition|lemma|boundary|remark|classicalinput)\}(?:\[[^\n]*?\])?\s*','',t,count=1)
    t=re.sub(r'\s*\\end\{(?:definition|theorem|corollary|proposition|lemma|boundary|remark|classicalinput)\}\s*$','',t,count=1)
    t=re.sub(r'\\label\{[^}]+\}\s*','',t)
    def ref(m):
        ids=[z.strip() for z in m.group(1).split(',')]
        for z in ids:
            if z not in labels: unresolved.add(z)
        return ', '.join(href(labels[z]) if z in labels else code('SOURCE:'+z) for z in ids)
    return re.sub(r'\\(?:c|C|eq)?ref\{([^}]+)\}',ref,t)

lead = r'''\section{Current release: sources, scope, and evidence}\label{sec:release-current}

The release preserves one current statement inventory for all three companions. The traditional manuscript supplies the statements and proofs; the machine catalog reproduces those statements with stable identifiers and source locators; the formal correspondence map records the exact Lean support for each statement. The current release files are:

\begin{longtable}{p{.36\textwidth}p{.55\textwidth}}
\toprule File or directory & Purpose \\\midrule\endhead
\code{formal/current/} & Flat formal source closure, including the continuation modules and their earlier dependencies. \\
\code{formal/coverage/COVERAGE_108.json} & All 108 current statements, source proofs and hashes, declaration mappings, scopes, and record classifications. \\
\code{formal/evidence/} & Release compiler, replay, audit, identity, and boundary-check receipts, as indexed by the release verification record. \\
\code{editable/traditional/} & Current mathematical source, including the final clarification of the split-semisimple corollary. \\
\code{source/traditional_v1.3.1/} & Preserved historical source and evidence for the 35-row tutorial contract. \\
\bottomrule\end{longtable}

The current inventory has 69 proof-level records. Definitions, classical inputs, boundaries, and documentary records are listed separately in the map and are excluded from this proof-level count.
'''
lead += '\n\\begin{center}\\begin{tabular}{lrrr}\\toprule\nStatus & Covered & Partial & Not mapped\\\\\\midrule\nProof-level records & '+f"{counts['covered']} & {counts['partial']} & {counts['not_mapped']}"+r'\\\bottomrule\end{tabular}\end{center}'+'\n\n'
lead += r'''``Covered'' means a complete correspondence at the recorded scope. ``Partial'' includes substantive missing proofs and consequences not yet assembled from existing declarations. ``Not mapped'' means that this source closure has no established complete declaration for the record. These statuses are not a percentage of independent theorems: the records differ in scope and may share mathematical dependencies.

\subsection{The continuation beyond the historical contract}

The accepted Block 08 checkpoint, dated 12 October 2026, contains 54 production modules. It freshly compiled eight additions, authenticated 46 predecessor source/object pairs, and replayed the whole logical closure. Its 1,634 source-owned entries comprise 1,627 logical declarations and seven separately inventoried generated partial runtime helpers. The latter were not proof-replayed. The recorded transitive axiom set is limited to \code{propext}, \code{Classical.choice}, and \code{Quot.sound}. These are the quantities for that checkpoint, not a claim that all 54 source modules were freshly compiled by it.

The continuation proves the intrinsic primary quotient and generator count, the geometric formula, scalar extension, and the six-way cyclic criterion. It also proves noncommutative module-top reduction and the nonsplit semisimple formula, including actual compatible decompositions from the Wedderburn--Artin existence theorem. The final existence theorems do not take a desired rank equality or a compatible decomposition as an input. They are noncomputable mathematical constructions, not executable decomposition algorithms.

\begin{longtable}{p{.38\textwidth}p{.53\textwidth}}
\toprule Current source layer & Mathematical entry points \\\midrule\endhead
\code{PaperICompletion/}, \code{PaperICompletion3/} & Spectral certificates, invariant factors, primary seed formulas, and operator-level bridges. \\
\code{PaperICompletion4/} & Intrinsic primary decomposition, residue quotients, and the operator seed formula. \\
\code{PaperICompletion5/} & Linear primary eigenspaces, the geometric seed formula, and its cyclic criterion. \\
\code{PaperICompletion6/} & Scalar extension, one invariant factor, and the six-way cyclic criterion. \\
\code{PaperICompletion7/} & Nakayama, module-top reduction, and the local residue division-ring case. \\
\code{PaperICompletion8/} & Division-ring row generation, products, regular multiplicities, compatible presentations, and semisimple existence/formulas. \\
\bottomrule\end{longtable}

The original \code{KomorebiVerification/} modules remain the foundation for packet coordinates, transport, seed rank, matrix models, and bounded-packet analysis. Their explanations occupy the following tutorial sections. Current declarations may strengthen those earlier results; the original theorem signatures retain their own input boundaries.

\subsection{Release modules and presentation conventions}

The \code{PaperIRelease/} layer extends the preceding continuation. Its source files are grouped by mathematical construction:

\begin{longtable}{p{.40\textwidth}p{.51\textwidth}}
\toprule Source family & Construction \\\midrule\endhead
\code{GrammarAlgebra}, \code{GrammarTyped}, \code{GrammarModules}, \code{GrammarEquivalence}, \code{GrammarIdeal} & Typed realizations, module categories, comparison functors, and quotient-algebra presentations. \\
\code{SeedOperations}, \code{ExactSequences}, \code{ScalarExtension}, \code{PolynomialModule}, \code{PolynomialMonic} & Generator bounds, exact sequences, scalar extension, and canonical polynomial-module wrappers. \\
\code{PacketAggregation}, \code{PacketDescent}, \code{PacketExactSequence}, \code{PacketUniversal}, \code{TensorPackets} & Actual range packets, quotient and restriction maps, exactness, universal properties, and tensor constructions. \\
\code{AlgebraSupport}, \code{AlgebraPreorder}, \code{AlgebraQuotient}, \code{PacketCorners}, \code{BoundedStar} & Support algebras, diagonal and quotient structure, local actions, and bounded adjoints. \\
\code{GraphReachability}, \code{GraphSources}, \code{GraphSourceCount}, \code{PacketPureRank}, \code{PacketSourceRank} & Transfer reachability, source components, and packet-pure generator counts. \\
\code{TopologySeedRank}, \code{TopologyPresentations}, \code{TopologyCountablePackets}, \code{TopologyCategories} & Closed hulls, locally convex presentations, unconditional packets, and continuous categorical maps. \\
\code{CategoryPackets}, \code{CategoryUniversal}, \code{CategoryExport} & Packet-system categories, naturality, and preservation of equations under functors. \\
\bottomrule\end{longtable}

These are source-navigation entries. The current map supplies the exact declaration names and hypotheses, and the release receipt determines the accepted verification scope.

For the typed-grammar correspondence, the finite-vertex path algebra uses its standard vertex-and-arrow presentation: vertex idempotents are pairwise annihilating and sum to one, and each arrow lies in its target/source corner. The formal \code{PathAlgebra} names that presentation. \code{GrammarIdeal} takes an arbitrary two-sided ideal and constructs the comparison between the iterated ideal quotient and the combined presentation; its two comparison maps are proved inverse. Thus the presentation convention is explicit when reading the manuscript notation $kQ/I$. It is not an assumed module-category equivalence or a supplied conclusion about generators.

'''
if meta.get('guide_verification_tex'):
    lead += '\n' + meta['guide_verification_tex'] + '\n'
else:
    lead += r'''
\subsection{Release verification index}
The release's verification record identifies which current sources were compiled or replayed during release preparation. The preceding Block 08 quantities describe the accepted predecessor checkpoint. A PDF build does not update them or generate new formal evidence. Read the current evidence index before attributing any fresh verification to a declaration.
'''
lead += r'''
\subsection{Current proof-level correspondence index}
The following index is generated from the release map. The machine companion supplies the current source statements, and the JSON map supplies every declaration name and exact scope note. Every covered status must be read with that scope note before reusing a theorem.

{\small
\begin{longtable}{p{.67\textwidth}p{.23\textwidth}}
\toprule Stable record & Current status \\\midrule\endhead
'''
for r in proofs: lead += code(r['stable_id'])+' & '+esc(r['status'].replace('_',' '))+r' \\'+'\n'
lead += r'\bottomrule\end{longtable}}'+'\n'
(guide/'release_current.tex').write_text(lead)

machine_status = r'\subsection{Current formal correspondence and checks}'+'\n'
machine_status += f"The release map classifies the 69 proof-level records as {counts['covered']} covered, {counts['partial']} partial, and {counts['not_mapped']} not mapped. "
machine_status += r'''The classifications describe the complete current statements at their recorded scopes; they do not count independent theorems or executable actions. Every current statement, source proof, and correspondence scope is reproduced in Appendix A. The exact declaration lists are in \nolinkurl{formal/coverage/COVERAGE_108.json}.

'''
machine_status += meta.get('machine_verification_tex',r'Compiler and logical-replay receipts for release preparation are indexed under \nolinkurl{formal/evidence/}. The Lean guide identifies the current formal sources and distinguishes this evidence from preserved historical checks.')+'\n'
(machine/'release_verification.tex').write_text(machine_status)

catalog = [r'''\clearpage\appendix
\section{Complete current record catalog}\label{app:catalog}
This catalog is generated from the current traditional manuscript's 108 stable records. Every statement and attached proof comes from the release inventory. The current source locator and statement hash identify the exact wording. Cross-references are linked to stable records in this catalog.

The formal-status line reports the current reviewed correspondence map, not the older machine payload's eight-entry Lean map. Scope notes are part of each correspondence: ``partial'' is not a formal certificate for the complete source statement. The full declaration lists and source hashes are preserved in \nolinkurl{formal/coverage/COVERAGE_108.json}.

The executable runtime contracts and historical maps remain separate evidence for their stated scopes. Reproducing a source proof in this catalog does not give that proof a Lean certificate.
''']
previous_file=None
for r in records:
    loc=r['current_source']
    if previous_file!=loc['file']:
        title={'02_foundations.tex':'Foundations of seed generation','03_packets_and_graphs.tex':'Packets and transfer graphs','04_transport.tex':'Transport and realization'}[Path(loc['file']).name]
        prefix=r'\clearpage' if previous_file else ''
        previous_file=loc['file']
        catalog.append(prefix+r'\subsection{'+title+'}\n')
    catalog.append(r'\Needspace{12\baselineskip}\subsubsection*{'+str(r['ordinal'])+'. '+esc(r['title'])+'}\n'+r'\phantomsection\label{rec:'+r['stable_id']+'}\n')
    catalog.append(r'\field{Stable ID}{'+code(r['stable_id'])+'}\n')
    catalog.append(r'\field{Kind}{'+esc(r['kind'])+'}\n')
    catalog.append(r'\textbf{Statement.}\par'+'\n'+source(r['statement'])+'\n')
    if r.get('source_proof'): catalog.append('\n'+source(r['source_proof'])+'\n')
    catalog.append(r'\field{Current formal correspondence}{'+esc(r['status'].replace('_',' '))+'. '+esc(r['scope_and_remaining_work'])+'}\n')
    locator=code(loc['file'])+f"; statement lines {loc['statement_start_line']}--{loc['statement_end_line']}"
    if loc.get('proof_start_line'): locator+=f"; proof lines {loc['proof_start_line']}--{loc['proof_end_line']}"
    catalog.append(r'\field{Current source locator}{'+locator+'.}\n')
    catalog.append(r'\field{Statement SHA-256}{'+code(loc['statement_sha256'])+'}\n')
(machine/'release_catalog.tex').write_text(''.join(catalog))
assert not unresolved, f'Unresolved current source labels: {sorted(unresolved)}'
stamp = {'coverage_sha256':hashlib.sha256(args.coverage.read_bytes()).hexdigest(),'records':len(records),'proof_level_records':len(proofs),'proof_level_counts':dict(counts),'current_source_files':sorted({r['current_source']['file'] for r in records}),'unresolved_source_references':sorted(unresolved),'generation_is_not_formal_verification':True}
(guide/'release_data_identity.json').write_text(json.dumps(stamp,indent=2)+'\n')
(machine/'release_data_identity.json').write_text(json.dumps(stamp,indent=2)+'\n')
print(json.dumps(stamp,indent=2))
