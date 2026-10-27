#!/usr/bin/env python3
"""Build the source-mapped guide; this script does not execute Lean."""
from pathlib import Path
import csv, json, re, hashlib, argparse
from collections import Counter

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--upstream', required=True, type=Path, help='Extracted frozen v2.0.0 source directory')
UP = parser.parse_args().upstream.resolve()
if not (UP / 'manuscript').is_dir():
    raise SystemExit('Extract the preserved v2.0.0 source ZIP, then pass its root with --upstream.')
CORE = HERE / 'inspected_source/StratifiedFoundationsCore.lean'
NS = 'Komorebi.StratifiedFoundations.'

def esc(s):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))

def code(s): return r'\texttt{\seqsplit{' + esc(s) + '}}'

source = CORE.read_text()
decls=[]
for i,line in enumerate(source.splitlines(),1):
    m=re.match(r'(?:@\[[^]]+\]\s*)?(?:noncomputable\s+)?(def|theorem|lemma|structure)\s+(\w+)',line)
    if m:
        name=m[2]; qual=NS + ('ProjectorFamily.' if i<142 and name!='ProjectorFamily' else '') + name
        decls.append({'kind':m[1],'name':name,'qualified_name':qual,'file':'inspected_source/StratifiedFoundationsCore.lean','line':i,'evidence':'SOURCE_INSPECTED_NOT_FRESHLY_COMPILED'})

clause_maps = [
 ('L1','Exact analysis and synthesis','thm:block15-universal-lane-transport',['synthesisLinear_analysisLinear','analysisLinear_synthesisLinear','laneEquiv'],'Finite module normalization; resolved laneSpace, not unrestricted function space.'),
 ('L2','Unique transfer blocks','thm:block15-universal-lane-transport',['transferBlock_reconstruction','transferBlock_ext'],'Ambient corner blocks Q_j T P_i; categorical Hom-to-split-block bijection requires additional category layer.'),
 ('L3','Composition and finite path contraction','thm:block15-universal-lane-transport',['transferBlock_comp','transferBlock_comp_matrix'],'Two-step finite contraction is inspected; iterated address-path expansion needs induction.'),
 ('L4','Projector-sum refinement','thm:block15-universal-lane-transport',['transferBlock_refinement'],'One declared source and target refinement step, with fibre-sum hypotheses.'),
 ('L5','Boolean selectors and named residuals','thm:block15-universal-lane-transport',['select_idempotent','select_inter','select_add_residual'],'Selector endomorphisms on module morphisms; masks retain exact ambient blocks.'),
 ('L6','Support and residual propagation','thm:block15-universal-lane-transport',['select_comp_of_supported','selected_composition_residual_identity'],'Support containment and exact three-term residual identity; no equality-of-support claim.'),
 ('L7','Additive profile-preserving realization','thm:block15-universal-lane-transport',[],'Historical v0.7 report describes CategoryCore; no matching declaration body inspected here.'),
 ('L8','Fold loss','thm:block15-universal-lane-transport',['fold_eq_iff_sub_mem_ker','ker_eq_bot_of_leftInverse'],'Linear fold kernel and supplied-left-inverse criterion inspected; construction of injectivity/left inverse from globally typed Q_e and r_e hypotheses is not mapped.'),
 ('RES','Complete resolution change','prop:block15-certified-coarsening',['changeResolution_symm','changeResolution_trans'],'Object-level prerequisite/analogue inspected; the Hom/block coarsening map and its multiplication compatibility are not declaration-mapped here.'),
 ('H1-H5','Holonomy-twisted compatible sections','thm:block16-holonomy-twisted-lane-transport',[],'Reported v0.7 GroupoidLocalSystemCore/CategoricalAtlasCore coverage; ambient Hom coherence explicitly assumed.'),
 ('BASE','Base-fiber invariant normal form','cor:block16-base-fiber-invariant-normal-form',[],'Reported v0.7 local-system coverage; no source body inspected in this edition.'),
 ('ORBIT','Finest globally labeled coarsening','thm:block16-orbit-descent',[],'Reported v0.7 HolonomyFiniteCore coverage; object and pair orbits must remain distinct.'),
 ('PAIR','Permutation orbital calculus','thm:block16-permutation-orbital-calculus',[],'Reported v0.7 orbit basis and path-count coverage; no inspected declaration map.'),
 ('CYC','Rational cyclotomic Fourier lanes','prop:block16-rational-cyclotomic-orbit-lanes',[],'Partial recorded v0.7 coverage. Classical Möbius formula and cyclotomic factor/CRT identification remain explicit formalization obligations.'),
]
byname={x['name']:x for x in decls}
mapping=[]
for clause,title,label,names,boundary in clause_maps:
    actual=[byname[n] for n in names]
    mapping.append({'id':clause,'manuscript_label':label,'manuscript_component':title,'lean_declarations':[a['qualified_name'] for a in actual],'source_lines':[a['line'] for a in actual],'source_file':str(CORE.relative_to(HERE)) if actual else '', 'evidence_class':'SOURCE_INSPECTED' if actual else 'RECORDED_RELEASE_ONLY','fresh_compile':'NOT_RUN','scope_boundary':boundary})

# Traverse only the controlling v2 manuscript input graph. Images and release
# siblings do not contribute theorem environments to this inventory.
seen=set(); statements=[]
def visit(p):
    p=p.resolve()
    if p in seen:return
    seen.add(p);text=p.read_text()
    for m in re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary|conjecture)\}(?:\[([^\n]*?)\])?',text):
        end=text.find('\\end{'+m[1]+'}',m.end())
        block=text[m.end():end if end>=0 else len(text)]
        lm=re.search(r'\\label\{([^}]+)\}',block)
        label=lm[1] if lm else ''
        statements.append({'environment':m[1],'title':m[2] or '', 'label':label,'source_file':str(p.relative_to(UP)),'source_line':text.count('\n',0,m.start())+1,'inventory_source_edition':'FROZEN_ORIGINAL_FORMAL_FOUNDATIONS_v2.0.0_2026-09-23','lean_mapping_status':'NOT_ESTABLISHED_IN_THIS_GUIDE','fresh_compile':'NOT_RUN'})
    for m in re.finditer(r'\\input\{([^}]+)\}',text):
        q=p.parent/m[1]
        if not q.suffix:q=q.with_suffix('.tex')
        if q.is_file():visit(q)
visit(UP/'manuscript/Komorebi_Stratified_Universality_Formal_Foundations_v2.0.0.tex')
for row in statements:
    ms=[x for x in mapping if x['manuscript_label']==row['label']]
    if ms:row['lean_mapping_status']='PARTIAL_NORMALIZED_SOURCE_AND_OR_RECORDED_RELEASE';row['clause_ids']=';'.join(x['id'] for x in ms)

old=json.loads((UP/'release_v2.0.0/Komorebi_Theorem_Concordance_v0.4.json').read_text())
inherited_components=[]
for x in old['concordance']:
    y=dict(x);y['hypothesis_source_edition']='INHERITED_v0.4_FROZEN_ORIGINAL_NOT_CANONICAL_FINAL_HYPOTHESES';y['lean_mapping_status']='NO_COMPONENT_LEVEL_CORRESPONDENCE_ESTABLISHED';y['fresh_compile']='NOT_RUN';inherited_components.append(y)
final_path=HERE.parent/'traditional/Komorebi_Theorem_Concordance_Final_2026-10-06.json'
final=json.loads(final_path.read_text())
assert [(x['id'],x['status']) for x in final['concordance']]==[(x['id'],x['status']) for x in old['concordance']], 'Final component IDs/statuses differ from frozen source'
components=[]
for x in final['concordance']:
    y=dict(x);y['hypothesis_source_edition']='FINAL_PUBLICATION_EDITION_2026-10-06';y['hypothesis_source_file']='traditional/Komorebi_Theorem_Concordance_Final_2026-10-06.json';y['publication_amendment']=y.get('publication_amendment','');y['lean_mapping_status']='NO_COMPONENT_LEVEL_CORRESPONDENCE_ESTABLISHED';y['fresh_compile']='NOT_RUN';components.append(y)

metadata={
 'edition':'2026-10-06 final guide',
 'claim':'Source-mapped guide with historical release evidence; no whole-manuscript Lean certificate',
 'fresh_lean_execution':'NOT_RUN: Lean and Lake absent from PATH; checked ZIP bytes unavailable after HTTP 502',
 'standalone_source':{'name':'StratifiedFoundationsCore.lean','lines':602,'bytes':len(CORE.read_bytes()),'sha256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'counts':dict(Counter(d['kind'] for d in decls)),'identity':'Earlier standalone source, not one of seven v0.7 production modules'},
 'recorded_release':{'name':'Stratified_Foundations_Lean_Normalization_v0.7.0_Checked','date_utc':'2026-09-09T05:58:45.182163+00:00','source_files':7,'theorem_lemma_declarations':183,'lean_version':'4.34.0-rc2','lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib_commit':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','evidence':'README and AUDIT read; source ZIP and individual logs not recovered'},
 'manuscript_inventory':{'source_edition':'FROZEN_ORIGINAL_FORMAL_FOUNDATIONS_v2.0.0_2026-09-23','input_graph_files':len(seen),'statement_environments':len(statements)},
 'component_concordances':{'canonical':'Component_Status_Concordance.csv','canonical_hypothesis_source':'traditional/Komorebi_Theorem_Concordance_Final_2026-10-06.json','inherited':'Component_Status_Concordance_Inherited_v0.4.csv','inherited_scope':'frozen original hypotheses; not canonical final-edition scope','components':len(components),'ids_and_statuses_preserved':True},
 'correspondences':mapping}
(HERE/'Lean_Concordance.json').write_text(json.dumps(metadata,indent=2)+'\n')
def writecsv(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:('; '.join(map(str,v)) if isinstance(v,list) else v) for k,v in r.items()})
writecsv('Lean_Concordance.csv',mapping)
writecsv('Inspected_Declaration_Inventory.csv',decls)
writecsv('Manuscript_Result_Inventory.csv',statements)
writecsv('Component_Status_Concordance.csv',components)
writecsv('Component_Status_Concordance_Inherited_v0.4.csv',inherited_components)

body=r'''
\section{What this guide certifies}
This companion connects the finite transport and descent statements of
\emph{Stratified Universality for Resolved Representations} to the actual
formalization evidence recovered for this edition. It gives a declaration-level
map for the inspected module normalization and a separately labeled map for
the recorded categorical, holonomy, and cyclotomic release.

The complete written monograph is not claimed to be Lean-complete. The word
``formal'' in its title refers to explicit mathematical structures and proofs.
Lean evidence applies to the precisely named models and declarations, with
their hypotheses. Mathematical completion of a written theorem and completion
of its Lean translation are separate statements.

\begin{scopebox}
\textbf{Edition status.} One complete standalone Lean source was inspected.
The v0.7 release README and audit were read. The two matching ZIP transfers
failed with HTTP 502. Lean and Lake were absent from PATH, so no fresh Lean
compilation or axiom inspection was executed for this final edition.
\end{scopebox}

\section{Three evidence levels}
\begin{enumerate}
\item \textbf{Inspected source.} The complete 602-line
\texttt{StratifiedFoundationsCore.lean} contains 30 theorem declarations,
12 definitions, two structures, and 18 \texttt{\#check} commands. These are
textual source counts. The declaration bodies and hypotheses were inspected.
\item \textbf{Recorded release checks.} The v0.7 audit records seven production
sources, 183 theorem/lemma declarations, warning-as-error passes, zero
\texttt{sorry}, \texttt{admit}, or custom axiom declarations, and representative
standard-foundation axiom reports. Those are historical recorded checks.
Their complete source archive and compiler logs were not recovered here.
\item \textbf{Unestablished correspondence.} The v2 semantic and doctrine
chapters, the broader atlas claims, and all other components without an
inspected declaration map remain unmapped in this guide. This does not
assert that no formalization exists elsewhere.
\end{enumerate}

The source inventory, declaration concordance, and component status register
are included as CSV and JSON files. A row with no Lean declaration is a
coverage boundary, not a proposed certificate.

\section{Source identity and reconstruction}
The main monograph source archive contains TeX, exact Python validators,
figures, audit records, and publication material. Its inspected file tree
contains no \texttt{.lean}, \texttt{lean-toolchain}, \texttt{lakefile}, or
\texttt{.olean} file. The Lean normalization is a separate release.

The individually indexed standalone Core was available through a complete
text read. Its attempted byte transfer also returned HTTP 502. The included
copy was reconstructed from that complete read; a terminal line feed was
restored to match the authoritative size of 22,747 bytes. Its local digest
is recorded in the provenance JSON. Matching a published byte count is not
an independent upstream hash authentication.

This standalone Core is \emph{not} silently identified with any of the seven
production modules in the v0.7 audit. The latter names
\texttt{AbelianCore}, \texttt{CategoricalAtlasCore}, \texttt{CategoryCore},
\texttt{CyclotomicGaloisCore}, \texttt{GroupoidLocalSystemCore},
\texttt{HolonomyFiniteCore}, and \texttt{ModulePolynomialCore}.

\section{The module normalization}
The inspected namespace is
\texttt{Komorebi.StratifiedFoundations}. Its basic structure is
\texttt{ProjectorFamily R M I}, over a commutative ring \(R\), an additive
commutative group \(M\), an \(R\)-module structure, and a finite index type.
It supplies linear endomorphisms \(P_i\) satisfying
\[
 P_i^2=P_i,\qquad P_iP_j=0\ (i\ne j),\qquad \sum_iP_i=1_M.
\]
These identities are fields of the declared structure. The subsequent
theorems quantify over every such family; they do not discover a projector
family for an arbitrary represented object.

The monograph's finite transport theorem is stated in an additive
idempotent-complete category with chosen splittings. The inspected Core
specializes that theorem to modules and uses fixed submodules of projectors
as the coordinate objects. This is a meaningful normalization, but it is
not a declaration-level proof at the full category-theoretic generality.

\subsection{Why the coordinate type matters}
The exact coordinate target is
\[
 \operatorname{Lane}(P)
 =\{c:I\to M\mid P_i(c_i)=c_i\text{ for every }i\}.
\]
The unrestricted type \(I\to M\) would contain coordinates outside their
lanes. Synthesis and analysis are inverse only on the resolved target.
The definitions \texttt{laneSpace}, \texttt{analysisLinear},
\texttt{synthesisLinear}, and \texttt{laneEquiv} implement this restriction.

\section{L1: exact analysis and synthesis}
Analysis sends \(x\) to \((P_ix)_i\); synthesis adds the coordinates.
The source proves both inverse laws:
\[
 \mathsf S\mathsf A(x)=x,\qquad
 \mathsf A\mathsf S(c)=c\quad(c\in\operatorname{Lane}(P)).
\]
The first law is completeness. For the second, apply \(P_j\) to the finite
sum; orthogonality removes all terms except \(j\), whose lane condition
returns \(c_j\). The resulting \texttt{laneEquiv} is a linear equivalence.

\texttt{synthesize\_analyze} is a convenient earlier function-level lemma.
The stronger normalized inverse pair is
\texttt{synthesisLinear\_analysisLinear} and
\texttt{analysisLinear\_synthesisLinear}.

\section{L2: exact transfer blocks}
For projector families \(P\) on \(M\), \(Q\) on \(N\), and a linear map
\(T:M\to N\), the source defines
\[
 T_{ji}=Q_jTP_i.
\]
\texttt{transferBlock\_reconstruction} proves
\[
 T=\sum_{j,i}Q_jTP_i.
\]
\texttt{transferBlock\_ext} says two maps are equal if every ambient corner
block agrees. These statements retain their full finite index types and
module hypotheses.

The printed category theorem uses typed split-lane blocks
\(\pi_jT\iota_i:M_i\to N_j\). An ambient corner is the same block inserted
back into the ambient source and target. Showing equality of the two
formulations requires the chosen splitting maps and their identities;
they must not be erased in a categorical correspondence.

\section{L3: composition and path contraction}
For \(U:N\to L\), a third projector family \(S\), and source/target
addresses \(i,k\), the source proves
\[
 S_kUTP_i=\sum_j(S_kUQ_j)(Q_jTP_i).
\]
The declaration \texttt{transferBlock\_comp\_matrix} is the morphism-level
two-step contraction. The finite path law for a longer chain follows by
repeated contraction in the written theorem. A future fully explicit Lean
map for arbitrary chain length should supply the induction and the address
product type; this guide does not invent that declaration.

Cancellation can make a composite block zero even when individual paths
are supported. Thus support propagation gives a containment result,
not equality of support sets.

\section{L4: refinement}
The structure \texttt{Refines} supplies a declared address map and the
identity that every coarse projector is the finite sum of its fine
descendants. \texttt{transferBlock\_refinement} proves
\[
 Q_aTP_i
 =\sum_{\rho_Y(b)=a}\sum_{\rho_X(j)=i}Q'_bTP'_j.
\]
This is one exact refinement step. The full finite resolution system also
needs identity maps and compatibility of successive address maps. Those
are additional data, not consequences of cardinality comparisons.

\section{L5: selectors and exact residuals}
A Boolean source-target mask \(E\) keeps the ambient blocks whose addresses
belong to \(E\):
\[
 \operatorname{Sel}_E(T)=\sum_{(j,i)\in E}Q_jTP_i,
 \qquad R_E(T)=T-\operatorname{Sel}_E(T).
\]
The inspected source proves that a retained block is unchanged, a discarded
block is zero, selectors are idempotent, and two selectors compose by
intersection. The exact reconstruction law is
\[
 \operatorname{Sel}_E(T)+R_E(T)=T.
\]
The residual is retained mathematical data. Discarding blocks does not become
lossless merely because the retained blocks have convenient labels.

\section{L6: propagation through composition}
The support relation \texttt{composeSupport} is existential composition:
\[
 (F\circ E)(k,i)\iff\exists j,\ F(k,j)\land E(j,i).
\]
\texttt{select\_comp\_of\_supported} proves that a composite lies in this
support relation when both factors satisfy their selected-support contracts.

For retained maps \(T_0,U_0\), the exact residual identity is
\[
 UT-U_0T_0=(U-U_0)T_0+U_0(T-T_0)+(U-U_0)(T-T_0).
\]
The declaration \texttt{composition\_residual\_identity} proves the general
linear-map identity, and \texttt{selected\_composition\_residual\_identity}
specializes it to selectors. The residual-residual term is required.

No norm, tolerance, probability, or convergence claim follows from this
algebraic identity without further hypotheses.

\section{L7 and L8: realization and fold loss}
The v0.7 report records an additive-category layer, including split-lane
Hom/block equivalence and additive-functor realization. Its declaration
bodies were not inspected here, so L7 has report-level coverage only.

The standalone Core gives two exact fold statements for a linear map
\(\Phi:A\to B\):
\[
 \Phi(x)=\Phi(y)\iff x-y\in\ker\Phi,
\]
and
\[
 L\Phi=1_A\Longrightarrow\ker\Phi=0.
\]
The declarations are \texttt{fold\_eq\_iff\_sub\_mem\_ker} and
\texttt{ker\_eq\_bot\_of\_leftInverse}. A zero kernel proves injectivity;
it does not, over an arbitrary ring, automatically supply a chosen linear
left inverse. The monograph's sufficient split-lossless criterion uses globally typed
selectors and supplied retractions. Constructing its injectivity or left
inverse from those hypotheses is not declaration-mapped here.

\section{Complete resolution change}
The inspected \texttt{changeResolution} is
\(\mathsf A_Q\mathsf S_P\), a linear equivalence between two complete
resolved coordinate spaces on the same ambient module. Its inverse is the
reversed change, and successive changes compose strictly. These are the
declarations \texttt{changeResolution\_symm} and
\texttt{changeResolution\_trans}.

This is an object-level prerequisite or analogue of the printed
Hom/block coordinate coarsening. The latter uses both source and target
splittings and intertwines matrix multiplication; that full map is not
declaration-mapped here.

This construction retains all ambient information in each complete
resolution. A noninjective fold or a selector deletion is governed by its
kernel or residual instead.

\section{Recorded holonomy and categorical coverage}
The v0.7 README records the following finite normalization layers:
\begin{itemize}
\item multi-chart additive local systems and compatible sections;
\item base-fiber loop-fixed normal form;
\item categorical realization of H2--H5 under ambient Hom coherence;
\item finite holonomy orbit descent, pair-orbit coordinate expansion,
and exact orbital path-count multiplication;
\item finite permutation-module equivalence between pair-orbit coordinates
and equivariant homomorphisms.
\end{itemize}
The report names \texttt{CoherentHomPair} as an explicit coherence package.
Deriving it from a complete category-valued pseudofunctor/descent-object
layer remains a reported open formalization obligation.

Object-address orbits and source-target pair orbits answer different
questions. The former classify globally labeled projector-sum coarsenings.
The latter classify invariant matrix positions and equivariant support
selectors. Transitive object action can still have several pair orbits.

\section{Recorded cyclotomic coverage and remaining identifications}
The v0.7 report records exact additive-order classification of cyclic unit
orbits, actual primitive Fourier idempotents in the group algebra, complete
orthogonal orbit sums, coefficientwise rationality, literal descent to
\(\mathbb Q[C_n]\), and integral Ramanujan character sums. The audit's
representative axiom examples include
\texttt{primitiveFourierIdempotent\_sum},
\texttt{galoisOrbitProjector\_coeff\_mem\_rational\_range},
\texttt{rationalOrbitProjector\_sum\_divisors},
\texttt{exists\_int\_ramanujanOrbitSum}, and
\texttt{rationalOrbitProjector\_eq\_inv\_smul\_integralRamanujanElement}.
These names are recorded audit examples, not declaration bodies inspected
in this edition.

The same release explicitly leaves the following identifications open:
\begin{enumerate}
\item the certified integral orbit sum with
\(c_q(\ell)=\sum_{d\mid\gcd(q,\ell)}d\,\mu(q/d)\);
\item the associated classical Ramanujan normal form;
\item the factor identification
\(\mathbb Q[C_n]\widetilde E_q\cong\mathbb Q(\zeta_q)\) and full
cyclotomic product decomposition in the printed formulation.
\end{enumerate}
The existence of rational orthogonal projectors is already a strong finite
formal result. It does not supply these further identifications by naming
the coefficient a Ramanujan sum.

\section{The v2 semantic extension: a precise translation plan}
The behavioral quotient chapters contain written results and exact finite
validators. No matching Lean declaration body was established for those
chapters during this edition. The following is a formalization plan,
not executable checked Lean code.

\subsection{Behavioral kernels}
In a module slice, represent observations as linear maps and continuations
as a monoid action by module endomorphisms. Define
\[
 N=\bigcap_{m,j}\ker(o_j\rho(m)).
\]
The module intersection exists independently of a possibly infinite product
of observations. Prove invariance using the action multiplication law, then
use the quotient universal property. The direction of the coarsest-quotient
factorization is from any exact surjective representation \(Z\) to \(X/N\).

\subsection{Task combination and bridge loss}
For two task kernels, the joint task uses intersection. Their common
coarsening uses the sum only in the linear setting with the stated task
interpretation. A task-compatible bridge satisfies
\(f(N_X)\subseteq N_Y\), enabling the quotient map
\(\overline f:X/N_X\to Y/N_Y\). Its exact loss and failure of target coverage
are separate objects:
\[
 \ker\overline f=f^{-1}(N_Y)/N_X,
 \qquad\operatorname{coker}\overline f=Y/(N_Y+f(X)).
\]
The formal translation must prove the quotient identifications and maps,
not merely define these expressions and assume exactness.

\subsection{Carrier gates and admissibility}
For set-valued carrier semantics, the factorization gate uses kernel pairs:
\(\kerpair(s)\subseteq\kerpair(t)\). Equality of residual functions and
linear dependence of residual functions must remain distinct relations.
The v2 relation-module construction is the explicit bridge between them.

Admissibility monotonicity is an infimum theorem. Formalizing nonattainment
requires the declared topology and compactness hypotheses. An arbitrary
Hausdorff space need not turn compactness into sequential compactness;
the final traditional edition instead uses an attained positive minimum
on each compact conditioned sublevel.
No placeholder proof is supplied here for these analytic results.

\section{Reading the manuscript registers}
The final-edition component concordance retains 75 stable rows: 52 internally proved,
12 classical imports or reinterpretations, two conditionally proved,
six conjectural, and three framework/definition components. This register
uses the amended final source's hypotheses, including finite branch/history
aggregation, empty conventions, and corrected support and metric scope.
The separate inherited v0.4 table preserves the original hypotheses as
historical evidence. It is not the canonical final-edition scope.
These registers track mathematical status and source selection, not a count of
Lean-certified statements or a completion percentage.

The separate manuscript result inventory records theorem, lemma,
proposition, corollary, and conjecture environments in the frozen original
v2.0.0 input graph. Its 242 rows preserve original labels and source coordinates,
not amended final-edition statement text. Environment
counts differ from component counts because one component can gather
several results and one theorem can contain multiple clauses.

The later September 24 Blocks 17--26 checksum manifest lists Markdown,
Python, and JSON material, with no Lean entries. Its ZIP bytes were not
recovered. Consequently it contributes no additional Lean coverage claim
in this guide and is not silently substituted for the controlling v2 paper.

\section{Reproducing the recorded Lean checks}
The recorded v0.7 pins are Lean 4.34.0-rc2, Lean commit
\texttt{6a10ac8c22beadecabdbb0919c2b50214762f91d}, and Mathlib commit
\texttt{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. Use the actual recovered
v0.7 project and its dependency files when available; do not manufacture a
project lock from these prose pins alone.

In its pinned portable environment, the release's recorded check command is:
\begin{lstlisting}
lake env lean -DwarningAsError=true <source>
\end{lstlisting}
Here \texttt{<source>} must be replaced by one actual source path from the
release audit. An explicit example, once that module has been recovered, is:
\begin{lstlisting}
lake env lean -DwarningAsError=true src/CyclotomicGaloisCore.lean
\end{lstlisting}
The standalone inspected Core can separately be checked in a compatible
project using:
\begin{lstlisting}
lake env lean -DwarningAsError=true StratifiedFoundationsCore.lean
\end{lstlisting}
Its compatibility with the v0.7 pin has not been freshly tested here.

Retain compiler exit codes, complete logs, source digests, the toolchain and
Mathlib revision, and declaration-level \texttt{\#print axioms} output.
An audit name without a recovered statement is report-level evidence.
A successful \texttt{\#check} establishes elaboration only in the executed
environment; an unexecuted \texttt{\#check} line in a source is not a pass.

The recorded standard axiom union is
\texttt{propext}, \texttt{Classical.choice}, and \texttt{Quot.sound} for the
representative examples. No universal axiom coverage is inferred from
representative checks. Placeholder scanning is supplementary to compilation
and the declaration-level axiom audit.

\section{Verification boundaries for this edition}
The final edition separately replays the principal exact Python validators.
That execution checks finite arithmetic formulas and implementation cases.
It is separate from Lean proof checking and does not upgrade unmapped
semantic or analytic results to a formal certificate.

No dependencies were installed and no compiler result was invented for this
guide. The attempted transfers failed with HTTP 502. The source read and the
historical audit read succeeded. The included reconstructed source preserves
that distinction in its provenance. The guide supplies a usable theorem
map and a reproduction route while preserving the written paper's actual
mathematical statements.

\clearpage
\appendix
\section{Clause-level concordance}
The table uses stable manuscript labels. ``Inspected'' always means an
inspected declaration body with no fresh compiler run. ``Recorded'' refers
to the separate historical v0.7 evidence.
'''
table=[r'\begin{longtable}{p{.075\textwidth}p{.35\textwidth}p{.49\textwidth}}',r'\toprule Clause & Manuscript target & Inspected declarations or evidence boundary\\\midrule\endhead']
for x in mapping:
    target=esc(x['manuscript_component'])+r'\par\small '+code(x['manuscript_label'])
    d=(r'\textbf{Inspected.}\par '+r'\par '.join(code(n.removeprefix(NS)) for n in x['lean_declarations'])) if x['lean_declarations'] else r'\textbf{Recorded only.}'
    table.append(esc(x['id'])+' & '+target+' & '+d+r'\par\small '+esc(x['scope_boundary'])+r'\\\addlinespace')
table.append(r'\bottomrule\end{longtable}')
body+='\n'.join(table)
body+=r'''
\section{Inspected declaration inventory}
All entries below occur in the included standalone Core. The source location
is a reading coordinate, not a compiler certificate. The namespace prefix is
\texttt{Komorebi.StratifiedFoundations}; declarations in the first projector
namespace additionally use \texttt{ProjectorFamily}.
'''
table=[r'\begin{longtable}{p{.1\textwidth}p{.1\textwidth}p{.7\textwidth}}',r'\toprule Line & Kind & Declaration\\\midrule\endhead']
for d in decls:table.append(str(d['line'])+' & '+esc(d['kind'])+' & '+code(d['qualified_name'].removeprefix(NS))+r'\\\addlinespace')
table.append(r'\bottomrule\end{longtable}')
body+='\n'.join(table)
body+=r'''
\section{Files accompanying the guide}
\begin{description}[style=nextline]
\item[Lean\_Concordance.csv / .json] Clause-level correspondences, evidence
classes, exact scope boundaries, and execution status.
\item[Inspected\_Declaration\_Inventory.csv] Every declaration found in the
included standalone Core, with namespace and source location.
\item[Manuscript\_Result\_Inventory.csv] The 242 statement environments in the
frozen original v2.0.0 source graph, with original labels and reading coordinates.
\item[Component\_Status\_Concordance.csv] The canonical 75-row final-edition
component table, with amended hypotheses and publication-amendment notes.
\item[Component\_Status\_Concordance\_Inherited\_v0.4.csv] The original 75-row
table with inherited hypotheses, explicitly historical rather than canonical.
\item[Recorded\_v0.7\_Audit\_Evidence.json] The complete readable historical
audit record, with source identity and evidence level.
\item[inspected\_source/] The reconstructed complete Core and provenance
record. No compiled artifact or fabricated project lock is included.
\end{description}

\section{Evidence sources}
\begin{enumerate}
\item Komorebi P., \emph{Stratified Universality for Resolved Representations:
Profiled Lane Transport, Semantic Quotients, Carrier Change, and Certified
Descent}, Formal Foundations v2.0.0, September 23, 2026. Controlling TeX,
theorem sections, exact validators, and component concordance.
\item Komorebi P., \texttt{StratifiedFoundationsCore.lean}, indexed standalone
source, September 9, 2026. Complete 602-line read; reconstructed local copy.
\item Komorebi P., \emph{Stratified Foundations Lean Normalization v0.7.0},
\texttt{README.md} and \texttt{AUDIT.json}, September 9, 2026. Readable
historical verification and scope records; archive bytes unavailable here.
\item Komorebi P., \texttt{Komorebi\_Stratified\_Blocks17\_26\_SHA256SUMS.txt},
September 24, 2026. Later companion manifest only; archive not inspected.
\end{enumerate}
'''
preamble=r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.85in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,amsmath,amssymb,amsthm}
\usepackage{booktabs,longtable,array,enumitem,xcolor,seqsplit}
\usepackage{listings,tcolorbox,fancyhdr,titlesec,hyperref}
\definecolor{Navy}{HTML}{17324D}
\definecolor{Teal}{HTML}{2F7A78}
\definecolor{Pale}{HTML}{E7F0F6}
\hypersetup{colorlinks=true,linkcolor=Navy,urlcolor=Teal,pdfauthor={Komorebi P.},pdftitle={Stratified Universality: Lean Guide and Formalization Concordance}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Stratified Universality: Lean Guide}\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{Navy}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries\color{Navy}}{\thesubsection}{.6em}{}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlist{itemsep=3pt,topsep=4pt}
\lstset{basicstyle=\small\ttfamily,breaklines=true,columns=fullflexible,backgroundcolor=\color{Pale},frame=single,framerule=0pt,xleftmargin=6pt,xrightmargin=6pt}
\newtcolorbox{scopebox}{colback=Pale,colframe=Navy,boxrule=.5pt,arc=0pt}
\newcommand{\kerpair}{\operatorname{KerPair}}
\allowdisplaybreaks
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\vspace*{1.0in}
{\large\color{Teal}\textsc{Operation Komorebi}}\par\vspace{.35in}
{\Huge\bfseries\color{Navy}Stratified Universality}\par\vspace{.2in}
{\LARGE Lean Guide and\par Formalization Concordance}\par\vspace{.45in}
{\large Komorebi P.}\par\vspace{.18in}
{\large Final Edition\quad October 6, 2026}\par\vspace{.6in}
\begin{scopebox}
An exact source map for finite module transport, recorded categorical and
holonomy formalization, and the remaining semantic correspondence work.
\end{scopebox}
\vfill
Included with the traditional paper, visual guide, source files, and
Markdown documentation. No whole-monograph Lean certificate is claimed.
\end{titlepage}
\hypersetup{pageanchor=true}
\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage
'''
body=re.sub(r'\\texttt\{([^{}]+)\}', lambda m: r'\texttt{\seqsplit{' + m[1] + '}}', body)
(HERE/'Stratified_Universality_Lean_Guide.tex').write_text(preamble+body+'\n\\end{document}\n')

# A text companion with the full machine-readable clause table linked by name.
md='''# Stratified Universality: Lean Guide and Formalization Concordance

Komorebi P. | Final edition, October 6, 2026

The PDF gives the full explanation and translation plan. This Markdown
companion records the exact evidence boundaries and correspondence register.

## Edition status

- A complete 602-line standalone `StratifiedFoundationsCore.lean` was inspected.
- Its textual inventory is 30 theorems, 12 definitions, two structures and 18
  `#check` commands. These are source counts, not fresh compiler results.
- The historical v0.7 README and AUDIT report seven modules and 183 theorem/lemma
  declarations with warning-as-error passes, no placeholders or custom axioms,
  and representative standard-foundation axiom reports.
- Those seven modules are not silently identified with the standalone Core.
- Lean and Lake were absent from PATH. No fresh Lean compilation or axiom check
  was executed for this edition.
- Matching ZIP materialization failed with HTTP 502. The standalone source was
  reconstructed from its complete read, restoring a terminal LF to match the
  published 22,747-byte size. No upstream hash authentication was available.

## Scope

The inspected source assumes a commutative ring, additive commutative module,
finite index types, and a complete orthogonal projector family. Its exact lane
space is the fixed-submodule coordinate space, not the unrestricted function
space. It proves module normalizations of L1-L6 and part of L8. The full typed
additive-category statement has separate recorded release coverage.

The semantic quotients and doctrine chapters are written results with exact
finite validators, but no declaration-level Lean correspondence was established
for them here. The broader atlas has explicit coherence/effectivity hypotheses.
This guide does not claim whole-manuscript Lean completion.

## Clause concordance

| Clause | Manuscript target | Evidence | Exact boundary |
|---|---|---|---|
'''
for x in mapping:md+=f"| {x['id']} | `{x['manuscript_label']}` | {x['evidence_class']} | {x['scope_boundary']} |\n"
md+='''
## Inspected declarations

| Line | Kind | Qualified declaration |
|---:|---|---|
'''
for d in decls:md+=f"| {d['line']} | {d['kind']} | `{d['qualified_name']}` |\n"
md+='''
## Recorded v0.7 boundary

The v0.7 record reports finite categorical transport, compatible local-system
sections, base-fiber loop invariants, finite holonomy orbits, pair-orbit
intertwiner coordinates, and cyclotomic rational projector descent. Its source
bodies and logs were not recovered in this edition. Recorded axiom examples
are historical evidence, not fresh execution.

The recorded open identifications are the classical Möbius formula for the
integral Ramanujan coefficients, the corresponding classical normal form,
the cyclotomic factor/CRT decomposition, and derivation of `CoherentHomPair`
from a full category-valued pseudofunctor/descent-object layer.

The later Blocks17-26 manifest lists Markdown, Python and JSON only. The ZIP
was unread and supplies no further Lean coverage claim.

## Reproduction

Recorded pins: Lean `4.34.0-rc2`, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Use the actual recovered project and dependency lock. Once a source is available:

```bash
lake env lean -DwarningAsError=true src/CyclotomicGaloisCore.lean
```

For the standalone Core in a compatible project:

```bash
lake env lean -DwarningAsError=true StratifiedFoundationsCore.lean
```

Its compatibility with the v0.7 pin has not been tested here. Retain exit codes,
logs, source hashes, actual revision pins and declaration-level axiom reports.
An unexecuted `#check` is not a compiler pass.

## Included registers

- `Lean_Concordance.csv` and `.json`: exact clause mappings and boundaries.
- `Inspected_Declaration_Inventory.csv`: all inspected declarations.
- `Manuscript_Result_Inventory.csv`: 242 statement environments in the frozen
  original v2.0.0 source graph, retaining original coordinates rather than
  amended final statement text.
- `Component_Status_Concordance.csv`: canonical 75-row final-edition component
  table, from `traditional/Komorebi_Theorem_Concordance_Final_2026-10-06.json`,
  with amended hypotheses, publication-amendment notes and unchanged IDs/statuses.
- `Component_Status_Concordance_Inherited_v0.4.csv`: historical 75-row table
  preserving the original hypotheses. It does not define final-edition scope.
- `Recorded_v0.7_Audit_Evidence.json`: complete readable historical audit data,
  with source identity and an explicit historical-evidence classification.
- `inspected_source/`: the reconstructed standalone source and provenance.

To regenerate the guide text and registers from the preserved frozen source,
extract that archive and run `python3 lean/build_guide.py --upstream PATH`, where
`PATH` is its extracted root. This generation command does not execute Lean.

The full guide supplies explanations of analysis/synthesis, transfer blocks,
refinement, selectors, residual propagation, fold kernels, complete resolution
change, recorded holonomy/cyclotomic coverage, and an explicitly unverified
translation plan for the semantic and doctrine extension.
'''
(HERE/'Stratified_Universality_Lean_Guide.md').write_text(md)
print(json.dumps({'inventory_files':len(seen),'statement_environments':len(statements),'standalone_source_counts':dict(Counter(d['kind'] for d in decls)),'clause_rows':len(mapping)},indent=2))
