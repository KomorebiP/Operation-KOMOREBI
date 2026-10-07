#!/usr/bin/env python3
"""Build the editorial companion from the unchanged frozen PSC-I records.
Set PSC_PYTHON to an interpreter with SymPy. Uses pdflatex and pdfinfo.
"""
from pathlib import Path
import json, os, re, sys, hashlib, subprocess, collections, platform
ROOT=Path(__file__).resolve().parent
SOURCE_ROOT=Path(os.environ.get('PSC_SOURCE_ROOT',str(ROOT/'source' if (ROOT/'source').is_dir() else ROOT.parents[1]/'source'))).resolve()
PKG=SOURCE_ROOT/'machine_v1.0.1'
OUT=ROOT/'build';OUT.mkdir(exist_ok=True)
EX=ROOT/'examples';EX.mkdir(exist_ok=True)
PY=os.environ.get('PSC_PYTHON',sys.executable)
def js(f): return json.loads((PKG/f).read_text())
records=js('kir/PSC_I.records.v1.json')['records']; by={r['stable_id']:r for r in records}
source=(PKG/'source/PSC_I_authoritative_source.tex').read_text()
source_lines=source.splitlines()
ast=[json.loads(x) for x in (PKG/'kir/statement_ast.ndjson').read_text().splitlines() if x.strip()]
actions=js('actions/action_registry.json')['actions']; typed=js('kir/core_typed_signatures.json')['records']
maps=js('evidence/lean/attached_v0.2.0/PSC_I_LEAN_RECORD_MAP.json')['mappings']
labels={}
for r in records:
 start=r['source']['statement_start_line']-1; end=r['source']['statement_end_line']
 for label in re.findall(r'\\label\{([^}]+)\}','\n'.join(source_lines[max(0,start-3):end])): labels[label]=r['stable_id']
def esc(s):
 return str(s).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('$',r'\$').replace('#',r'\#').replace('_',r'\_').replace('{',r'\{').replace('}',r'\}')
def code(s): return r'\nolinkurl{'+str(s)+'}'
def link(rid): return r'\hyperref[rec:'+rid+']{'+code(rid)+'}'
def math_source(text):
 def ref(m):
  ids=m.group(1).split(',')
  return ', '.join(link(labels[z.strip()]) if z.strip() in labels else code('SOURCE:'+z.strip()) for z in ids)
 return re.sub(r'\\(?:c|C|eq)?ref\{([^}]+)\}',ref,text)
def listing(s):
 if not isinstance(s,str):s=json.dumps(s,indent=2,ensure_ascii=True)
 return '\n\\begin{lstlisting}\n'+s+'\n\\end{lstlisting}\n'
def filelist(f): return r'\lstinputlisting{'+str(f.relative_to(ROOT))+'}\n'
def run(args,name,cwd=PKG):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
 (OUT/(name+'.stdout.txt')).write_text(p.stdout);(OUT/(name+'.stderr.txt')).write_text(p.stderr)
 return {'name':name,'command':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
results=[]
results.append(run([PY,'runtime/verify_release.py'],'current_release_gate'))
results.append(run([PY,'runtime/exact_fixture_suite.py'],'current_exact_fixtures'))
results.append(run([PY,'runtime/nonzero_packet_regression.py'],'current_nonzero_packet_regression'))
if any(r['returncode'] for r in results):raise SystemExit('Frozen release verification failed; inspect build logs')
# The worked examples are API executions, not new theorem tests.
commands=[('packet_validation',['execute','VALIDATE_PACKET_SYSTEM','tests/packet_input.json']),('packet_analysis',['execute','ANALYZE_PACKETS','tests/analyze_input.json']),('blockification',['execute','BLOCKIFY_OPERATOR','tests/blockify_input.json']),('dependencies',['deps','PSC-I-T-BLOCK-INTERTWINING','--transitive']),('transport_finite',['transport','PSC-I-T-BLOCK-MULTIPLICATION','profiles/packet_linear.json']),('transport_countable',['transport','PSC-I-T-COUNTABLE-UNCONDITIONAL-PACKETS','profiles/packet_linear.json'])]
example_outputs={}
for name,args in commands:
 r=run([PY,'runtime/machine_api.py',*args],'example_'+name);results.append(r)
 if r['returncode']:raise SystemExit(name)
 example_outputs[name]=json.loads(r['stdout']);(EX/(name+'.json')).write_text(r['stdout'])
P=[[[1,-1],[0,0]],[[0,1],[0,1]]]
extras={'reconstruction':('RECONSTRUCT_OPERATOR',example_outputs['blockification']),
'composition':('COMPOSE_TRANSFER_BLOCKS',{'projectors':P,'S':[[11,13],[17,19]],'T':[[2,3],[5,7]]}),
'intertwining':('LOWER_INTERTWINER',{'P':P,'Q':[[[1,-2],[0,0]],[[0,2],[0,1]]],'T':[[2,3],[5,7]],'S':[[7,3],[5,2]],'U':[[1,1],[0,1]]})}
for name,(action,payload) in extras.items():
 inp=EX/(name+'_input.json');inp.write_text(json.dumps(payload,indent=2)+'\n')
 r=run([PY,'runtime/machine_api.py','execute',action,str(inp)],'example_'+name);results.append(r)
 if r['returncode']:raise SystemExit(name)
 example_outputs[name]=json.loads(r['stdout']);(EX/(name+'.json')).write_text(r['stdout'])
versions=run([PY,'-c','import sys,sympy; print(sys.version); print("SymPy="+sympy.__version__)'],'python_environment');results.append(versions)
# Frozen archive-byte preservation audit. The source archive remains an input, never rewritten.
import zipfile
archive=Path(os.environ.get('PSC_MACHINE_ARCHIVE',str((ROOT/'provenance' if (ROOT/'provenance').is_dir() else SOURCE_ROOT/'provenance')/'PSC_I_FINAL_MACHINE_RELEASE_v1.0.0.zip')))
audit=[]
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  if i.is_dir():continue
  rel=Path(*Path(i.filename).parts[1:]);orig=z.read(i);now=(SOURCE_ROOT/'machine_v1.0.0'/rel).read_bytes()
  audit.append({'path':str(rel),'sha256':hashlib.sha256(now).hexdigest(),'unchanged':orig==now})
assert all(x['unchanged'] for x in audit)
(OUT/'frozen_payload_integrity.json').write_text(json.dumps({'files':len(audit),'all_unchanged':True,'entries':audit},indent=2)+'\n')
(OUT/'validation_results.json').write_text(json.dumps({'date':'2026-10-05','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'frozen_payload_unchanged':True,'current_runs':results,'earlier_environment_failure':{'command':'python runtime/verify_release.py','failure':'EXECUTE_BLOCKIFY=FAIL caused by ModuleNotFoundError: sympy','resolution':'Used an existing environment containing SymPy. No frozen source or runtime was modified.'},'fresh_lean_replay':'NOT_RUN_BY_THIS_COMPANION_BUILD'},indent=2)+'\n')
# Document source.
preamble=r'''\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=23mm,headheight=15pt]{geometry}
\usepackage{microtype,amsmath,amssymb,amsthm,mathtools}
\usepackage{booktabs,longtable,array,tabularx,enumitem,fancyhdr,xcolor,listings,needspace}
\usepackage{titlesec}
\usepackage{xurl}
\usepackage[unicode,breaklinks]{hyperref}
\definecolor{teal}{HTML}{174C53}
\definecolor{pale}{HTML}{F1F5F5}
\hypersetup{pdftitle={Paper I: Machine-Native Final Companion},pdfauthor={Komorebi P.},colorlinks=true,linkcolor=teal,urlcolor=teal}
\titleformat{\section}{\Large\bfseries\color{teal}}{\thesection}{0.7em}{}
\titleformat{\subsection}{\large\bfseries\color{teal}}{\thesubsection}{0.7em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{teal}}{\thesubsubsection}{0.7em}{}
\setcounter{tocdepth}{2}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.45em}
\setlist{itemsep=0.18em,topsep=0.4em}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small PSC I \enspace Machine-native companion}\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,breakatwhitespace=false,columns=fullflexible,keepspaces=true,showstringspaces=false,backgroundcolor=\color{pale},frame=single,rulecolor=\color{teal!25},framerule=0.3pt,xleftmargin=1mm,xrightmargin=1mm,aboveskip=0.6em,belowskip=0.6em}
\allowdisplaybreaks\emergencystretch=3em\sloppy
\newcommand{\bbk}{\Bbbk}\newcommand{\A}{\mathcal A}\newcommand{\B}{\mathcal B}\newcommand{\Ccal}{\mathcal C}\newcommand{\Pcal}{\mathcal P}\newcommand{\Qcal}{\mathcal Q}\newcommand{\Rcal}{\mathcal R}\newcommand{\Scal}{\mathcal S}
\newcommand{\Hull}{\operatorname{Hull}}\newcommand{\srank}{\operatorname{srank}}\newcommand{\psrank}{\operatorname{psrank}}\newcommand{\End}{\operatorname{End}}\newcommand{\Hom}{\operatorname{Hom}}\newcommand{\im}{\operatorname{im}}\newcommand{\Ker}{\operatorname{Ker}}\newcommand{\Jac}{\operatorname{Jac}}\newcommand{\Irr}{\operatorname{Irr}}\newcommand{\Span}{\operatorname{span}}\newcommand{\alg}{\operatorname{alg}}\newcommand{\Reach}{\operatorname{Reach}}\newcommand{\Supp}{\operatorname{Supp}}\newcommand{\id}{\mathrm{id}}\newcommand{\cl}[1]{\overline{#1}}
\newcommand{\field}[2]{\noindent\textbf{#1.} #2\par}
\begin{document}
\begin{titlepage}
\vspace*{22mm}
{\color{teal}\large OPERATION KOMOREBI\par}
\vspace{10mm}
{\Huge\bfseries Projector-Resolved\\[3mm]Seed Calculus I\par}
\vspace{10mm}
{\LARGE Machine-native paper\par}
\vspace{5mm}
{\Large Records, semantics, executable actions,\\and evidence contracts\par}
\vspace{18mm}
{\large Komorebi P.\par}
\vspace{3mm}
Final editorial edition \enspace 5 October 2026\\
Companion to corrected machine interface v1.0.1
\vfill
\rule{\textwidth}{0.6pt}\par
108 source-linked records \enspace / \enspace 69 attached source proofs\\
20 typed signatures \enspace / \enspace 8 runtime actions\\
Full record catalog and reproducible exact examples
\end{titlepage}
\section*{Edition statement}\addcontentsline{toc}{section}{Edition statement}
This volume presents the machine representation of Paper I as a mathematical object that can be inspected, queried, and executed. It accompanies the traditional paper and the Lean guide. The canonical machine object remains the JSON entrypoint and its versioned payload. The PDF is the readable specification and catalog of that object.

The editorial edition is final for this release. This means its terminology, package paths, runtime description, examples, and record catalog have been reconciled with the v1.0.1 interface. It does not mean every record has a formal proof certificate. The release contains 108 records, including definitions and boundaries, and 69 source proof bodies. Twenty records have explicit typed signatures. Eight records have mappings to the attached historical Lean tranche, with differing degrees of source agreement.

The traditional final edition integrates the expanded 108-record core with worked models and visual material from the corrected traditional lineage. The machine source is the expanded core with two explicit nonzero-packet hypotheses added after the scoped audit. Its new SHA-256 digest identifies this corrected core. The original v1.0.0 payload is preserved separately as provenance. Added traditional examples are not silently inserted into the KIR. Stable identifiers join the core across the companions. A shared identifier alone is not a proof of statement equivalence.

The current documented release gate, exact finite fixture suite, and narrow zero-packet regression were replayed successfully for this edition. No fresh Lean compilation is claimed by this companion build. The separate Lean guide records its own formal verification scope.

\textbf{How to use this volume.} Read Sections 1--3 for mathematical and evidence semantics. Sections 4--6 give the executable contracts and an exact worked example. Section 7 describes release reproduction. Appendix A reproduces every canonical source statement and every attached proof body, with source locators and machine metadata. Later appendices give signatures, action coverage, operation vocabulary, and the historical Lean map.
\clearpage\tableofcontents\clearpage
\section{The mathematical object behind the interface}
\subsection{Operator systems, generated hulls, and seed rank}
A seed problem consists of an acting algebra, a module, and a family of seed vectors. The algebra must be fixed before the generation question is asked. For a unital algebra $A$ acting on a module $M$ and a finite seed family $S=\{s_1,\ldots,s_r\}$, the algebraic generated hull is
\[
\Hull_A(S)=\sum_{j=1}^{r}As_j.
\]
A one-seed system is cyclic. Seed rank measures the minimum cardinality of a generating family, under the regime declared in the source. Enlarging the acting algebra changes the question. Replacing algebraic span by a closure changes it again. The machine record therefore keeps the acting regime and hypotheses beside the statement.

Paper I begins with typed operator grammars and their realizations, then passes through free presentations, generator number, packet coordinates, block algebras, transfer graphs, and realization. The resulting record graph covers the whole expanded foundation. It is not limited to the finite matrix examples that the runtime executes.

For finite families of nonnegative integers, the ambient convention is $\max\varnothing=0$. The height of an empty finite poset is zero. A nonempty poset with no strict comparable pair also has height zero, so height counts strict steps. These conventions clarify the empty cases without adding stable records.

The source separates algebraic, linear, and topological claims. A finite-dimensional matrix computation can exercise a linear identity. It cannot establish the countable Banach-space result or a generator formula over every division ring. Those claims retain their own source proofs and dependencies.
\subsection{Exact packet coordinates}
For a finite index set $I$, a packet system on $X$ consists of linear maps $P_\alpha$ satisfying
\[
P_\alpha^2=P_\alpha,\qquad
P_\beta P_\alpha=0\quad(\beta\ne\alpha),\qquad
\sum_{\alpha\in I}P_\alpha=I_X.
\]
The packet spaces are the ranges $X_\alpha=P_\alpha X$. Analysis and synthesis are
\[
\mathcal A_Px=(P_\alpha x)_{\alpha\in I},\qquad
\mathcal S_P((x_\alpha)_\alpha)=\sum_\alpha x_\alpha.
\]
Their inverse laws are exact. No orthogonality assumption is needed. This distinction is visible in the oblique two-dimensional example later in the paper.

Machine execution represents each packet as an ambient vector. It does not construct a basis of every range or replace the ambient representation by smaller coordinate arrays. This choice makes exact identities easy to compare with the source formulas while retaining the packet index structure.
\subsection{Transfer blocks and composition}
For an endomorphism $T$, the transfer block from packet $\alpha$ to packet $\beta$ is
\[
T_{\beta\alpha}=P_\beta TP_\alpha.
\]
Its source is $X_\alpha$ and its target is $X_\beta$. In the finite runtime it is stored as a full ambient matrix. Completeness gives
\[
T=\sum_{\alpha,\beta}T_{\beta\alpha},\qquad
(ST)_{\gamma\alpha}=\sum_\beta S_{\gamma\beta}T_{\beta\alpha}.
\]
The order matters: the rightmost factor acts first. The runtime uses the same convention. Its nested block array is indexed first by target and then by source.

The graph records source dependencies for these identities. It does not infer every implicit mathematical dependency. The packet-system hypotheses remain required even when a compact source statement inherits them from the surrounding section.
\subsection{Intertwining and reconstruction}
For packet systems $P$ on $X$ and $Q$ on $Y$, an intertwiner $U:X\to Y$ satisfies $UT=SU$. Resolving both sides yields
\[
\sum_\beta U_{\gamma\beta}T_{\beta\alpha}
=
\sum_\delta S_{\gamma\delta}U_{\delta\alpha},
\qquad U_{\gamma\alpha}=Q_\gamma UP_\alpha.
\]
All local equations together are equivalent to the global equation under the packet hypotheses. The runtime returns the global Boolean, every local residual, and the conjunction of the local Booleans. It provides the data needed to inspect agreement or failure in a concrete exact case.
\subsection{The boundary of finite execution}
Countable packet sums require a topology and a convergence condition. Quotient descent requires invariance. Coordinate transport requires a suitable invertible map. Packet-pure seed counts differ from unrestricted seed counts because one mixed-support seed can contribute to several source components. These are mathematical hypotheses, not formatting conventions.

The source records seven explicit boundaries. Their presence is part of the interface. Runtime action names do not imply that every associated theorem has an implementation, and metadata listing a boundary does not itself execute that boundary check.

\section{Canonical machine representation}
\subsection{Entrypoint and package identity}
The payload is located at \nolinkurl{source/machine_v1.0.1/}. Commands in this volume assume the working directory is that folder. The entrypoint is \nolinkurl{PSC_I.machine.json}. It points to the record collection, statement AST, dependency graph, action registry, evidence index, and release files.

The frozen source digest is:
\begin{lstlisting}
__MACHINE_SOURCE_HASH__
\end{lstlisting}
The digest identifies the corrected expanded TeX source. The only mathematical statement changes from v1.0.0 are explicit nonzero-packet assumptions in the adjoint-closed support-pattern corollary and the unweighted source-component-count corollary. Both require nonzero packets for their necessity or counting arguments. An unnumbered paragraph also declares empty-family and poset-height conventions. All proof bodies are unchanged. The two degenerate examples are retained in the patch regression. A reformatted PDF or an integrated traditional edition need not have that digest. Reusing the frozen machine evidence requires retaining its source identity or recording an explicit crosswalk to a changed source.
\subsection{Record identity and source provenance}
Each record has a stable ID, kind, title, source section, statement text, optional proof text, dependencies, semantic annotations, evidence coordinates, and fingerprint. The source locator includes statement and proof spans and their hashes. These fields make it possible to ask which statement was encoded and which proof text accompanied it.

There are 28 definitions, 28 theorems, 22 corollaries, 16 propositions, three lemmas, three classical inputs, seven boundaries, and one remark. The 69 theorem/proposition/corollary/lemma records have attached proof bodies. Definitions and boundary statements are not counted as proved theorems merely because they occupy records.

A record fingerprint provides a content identity under the release's generating convention. It is not a proof certificate. The release gate checks the source digest, ID count, graph, AST coverage, selected API behavior, and exact fixtures. It does not establish all mathematical content through independent formal reconstruction.
\subsection{Statement AST and typed signatures}
The statement AST has one entry per stable ID. The statuses are 20 \nolinkurl{TYPED_CORE}, 81 \nolinkurl{STRUCTURED_SYMBOLIC}, and seven \nolinkurl{TEXTUAL_SEMANTIC}. A typed-core record points to a signature declaring parameters, requirements where supplied, and a return description.

The AST segments statements into prose and mathematical surfaces. Some expressions are recognized as relations or direct-sum expressions. Others retain \nolinkurl{latex_expr} leaves. Even a typed-core record can contain these leaves. Consequently, ``typed core'' refers to the attached interface signature, not to a complete formal elaboration or a proof term.

The signature for block intertwining describes a logical equivalence between the global and local equations. Its source proof remains attached separately. The runtime can evaluate a finite instance. These are three different representations with three different evidentiary roles.
\subsection{Dependencies and closure}
The recorded graph contains 108 nodes and 97 internal edges. The release gate confirms that the recorded internal dependencies resolve and that the graph is acyclic. Direct dependencies are stored on each record. The API can also return a transitive closure.

Closure queries return sorted identifiers. They do not produce a proof order, carry out the proof, or resolve external classical inputs. A consumer can use the graph to inspect a prerequisite set and then obtain source statements and evidence for each record.
\subsection{Operation profiles and actions}
Each record carries source-derived operation metadata, with a transitive profile alongside the direct profile. The ontology distinguishes structural operations from hypothesis classes. These annotations support planning and inspection. They should not be interpreted as a verified extraction of every semantic operation used by an arbitrary proof.

The action registry contains 37 action names associated with 75 records. Eight names are implemented in the runtime. Other entries are marked planner-only or fixture-only. The source has broader mathematical scope than the executable subset.

\section{Evidence semantics and certification scope}
\subsection{Independent evidence coordinates}
The record evidence object separates source, KIR, Python, and Lean. The source coordinate identifies the authoritative source. The KIR coordinate records the release's validation status. Python evidence reports exact finite fixtures for 26 records. Lean evidence points to eight historical source mappings.

No coordinate upgrades another automatically. Exact arithmetic removes floating-point ambiguity from a finite computation. It does not quantify over arbitrary fields, modules, dimensions, or topological spaces. A mapped Lean declaration proves its own formal statement under its dependencies. Its relation to the source statement must still be read from the mapping.
\subsection{Historical Lean linkage}
The attached verification tranche records Lean 4.34.0-rc2 and a pinned Mathlib manifest. The map is dated 2 September 2026. Its eight mappings include definitions, generalized theorems, one-directional correspondence, and a related sufficient direction. The support-pattern algebra mapping is explicitly partial. It must not be counted as a full formal certificate for every direction of the source criterion.

A separate historical report records 35 of 35 obligations for manuscript v1.2.0. The frozen status marks that lineage as noncanonical for the current expanded source. The historical count and the eight explicit current-core mappings answer different questions.
\subsection{Current reproduction}
For this edition, the documented release verifier and exact fixture suite were run from the corrected payload. Both passed. The verification log is attached in the companion's \nolinkurl{build/} directory. All 65 files extracted from the original machine archive retain their original bytes.

An initial invocation used an interpreter without SymPy and failed when the blockification action imported that dependency. The successful replay used an existing environment containing SymPy. No runtime action implementation was changed to resolve that environment failure. The two audited statement corrections were applied separately and have their own provenance record.

No fresh Lean replay is attributed to this companion build. Historical reports remain historical. If the separate Lean guide performs a fresh replay, it should identify the exact Lean source and toolchain that were tested rather than rewriting this frozen status file.
\subsection{What PASS means}
A release-gate pass means the named package checks succeeded. A fixture pass means a concrete exact computation satisfied its assertion. A transport-gate pass means all operation flags that this runtime checked were accepted. None of these strings, taken alone, means that the entire 108-record foundation has been formally proved by the runtime.

The full source proof catalog is included so that a reader can inspect mathematical arguments beyond the runtime. Editorial reproduction of those arguments is not an adversarial proof audit or a new formal verification claim.

\section{Executable action contracts}
\subsection{Input and output conventions}
The API is a Python command that emits JSON on successful calls. Exact arithmetic actions use SymPy matrices. Integers and rational strings such as \nolinkurl{"3/7"} preserve rational values. JSON floating-point numbers should be avoided when the intended claim is an exact rational identity. Returned scalar entries are strings.

Payload shapes are conventional rather than comprehensively validated at the API boundary. Supply nonempty compatible square projector matrices and compatible operators or vectors. Malformed inputs can raise Python exceptions. The command parser does not present a universal structured-error contract.

Most computational actions do not call packet validation automatically. Validate the packet family before interpreting block or analysis output through the theorems. With invalid projectors, a matrix expression may still be computable while its theorem interpretation fails.
\subsection{The six exact finite actions}
\begin{longtable}{@{}p{0.29\textwidth}p{0.28\textwidth}p{0.36\textwidth}@{}}
\toprule Action & Payload & Returned information\\\midrule\endhead
\nolinkurl{VALIDATE_PACKET_SYSTEM} & \nolinkurl{projectors} & Idempotence, annihilation, completeness, and their conjunction.\\
\nolinkurl{ANALYZE_PACKETS} & \nolinkurl{projectors}, \nolinkurl{vector} & Ambient packet vectors and a reconstruction Boolean.\\
\nolinkurl{BLOCKIFY_OPERATOR} & \nolinkurl{projectors}, \nolinkurl{operator} & Target/source array of ambient transfer matrices.\\
\nolinkurl{RECONSTRUCT_OPERATOR} & \nolinkurl{blocks} & Sum of every supplied block. Compatibility with a packet family is not independently checked.\\
\nolinkurl{COMPOSE_TRANSFER_BLOCKS} & \nolinkurl{projectors}, \nolinkurl{S}, \nolinkurl{T} & Block-product array and equality with directly resolved $ST$.\\
\nolinkurl{LOWER_INTERTWINER} & \nolinkurl{P}, \nolinkurl{Q}, \nolinkurl{T}, \nolinkurl{S}, \nolinkurl{U} & Global equation, local equations, residuals, and local conjunction.\\\bottomrule
\end{longtable}
\subsection{The two semantic gate actions}
\nolinkurl{CHECK_REALIZATION_PROFILE} and \nolinkurl{TRANSPORT_THEOREM} share the same runtime gate. Their payload contains a record ID and a profile. The gate reads that record's direct \nolinkurl{action_required_operations} and checks the corresponding profile flags.

The accepted flags are true, \nolinkurl{VERIFIED}, or \nolinkurl{PRESERVED}. False and \nolinkurl{NOT_PRESERVED} produce a negative list. Other or missing values are unknown. Any negative or unknown required operation blocks the gate.

This v1.0.1 implementation does not evaluate the profile's \nolinkurl{verified_hypotheses}, does not use the transitive operation closure as its required set, and does not execute the returned boundary guards. It also does not construct a target theorem, a proof object, or an independently verified realization functor. The preservation flags are caller-supplied declarations.

Thus the action named \nolinkurl{TRANSPORT_THEOREM} is an operation-profile gate. A consumer must separately justify target hypotheses, source-to-target interpretation, and any constructions used by the proof. Unknown flags fail closed only within the operation list actually inspected by the function.
\subsection{Planner-only and fixture-only actions}
The full registry in Appendix C makes execution status explicit. A planner-only action can identify a mathematically meaningful next step without implementing it. A fixture-only association records that a finite check exercises related mathematics. Calling an unimplemented action through \nolinkurl{execute} exits with an unsupported-action error.

\section{An exact worked execution}
\subsection{Oblique packets and reconstruction}
Use
\[
P_0=\begin{pmatrix}1&-1\\0&0\end{pmatrix},\qquad
P_1=\begin{pmatrix}0&1\\0&1\end{pmatrix},\qquad
x=\begin{pmatrix}3\\5\end{pmatrix}.
\]
These are complementary idempotents but are not self-adjoint under the usual Euclidean inner product. The example therefore exercises the algebraic packet hypotheses without adding orthogonality.
\begin{lstlisting}
python runtime/machine_api.py execute VALIDATE_PACKET_SYSTEM tests/packet_input.json
python runtime/machine_api.py execute ANALYZE_PACKETS tests/analyze_input.json
\end{lstlisting}
'''
parts=[preamble,listing(example_outputs['packet_validation']),r'''The analysis output is exact:
''',listing(example_outputs['packet_analysis']),r'''
The two vectors $(-2,0)^t$ and $(5,5)^t$ sum to $x$. Each belongs to its own projector range. The runtime's zero-based packet indexing corresponds to the displayed $P_0,P_1$.
\subsection{Resolving and rebuilding an operator}
Take
\[
T=\begin{pmatrix}2&3\\5&7\end{pmatrix}.
\]
The command \nolinkurl{BLOCKIFY_OPERATOR} returns four ambient $2\times2$ matrices. In target/source order, they are
\[
T_{00}=\begin{pmatrix}-3&3\\0&0\end{pmatrix},\quad
T_{01}=\begin{pmatrix}0&-7\\0&0\end{pmatrix},\quad
T_{10}=\begin{pmatrix}5&-5\\5&-5\end{pmatrix},\quad
T_{11}=\begin{pmatrix}0&12\\0&12\end{pmatrix}.
\]
Their sum is $T$. The exact reconstruction API returns:
''',listing(example_outputs['reconstruction']),r'''
The input and output JSON files for this reconstruction are supplied in \nolinkurl{examples/}. The reconstruction action performs the block sum. Its interpretation as recovery of the original operator uses the validated packet system and the way those blocks were formed.
\subsection{Composing resolved operators}
Now set
\[
S=\begin{pmatrix}11&13\\17&19\end{pmatrix},\qquad
ST=\begin{pmatrix}87&124\\129&184\end{pmatrix}.
\]
The runtime forms the blocks of $S$ and $T$, then sums over the middle packet index. It compares the resulting array with the directly resolved product. The supplied worked output has \nolinkurl{equals_direct: true}. The full block arrays are retained in \nolinkurl{examples/composition.json}.

The comparison checks a concrete instance of the multiplication identity. The general identity follows from inserting the complete family between the factors, as in the source proof reproduced in Appendix A.
\subsection{An intertwining computation}
Let
\[
U=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
Q_i=UP_iU^{-1},\qquad
S'=UTU^{-1}=\begin{pmatrix}7&3\\5&2\end{pmatrix}.
\]
The target packets are $Q_0=\left(\begin{smallmatrix}1&-2\\0&0\end{smallmatrix}\right)$ and $Q_1=\left(\begin{smallmatrix}0&2\\0&1\end{smallmatrix}\right)$. The global identity is $UT=S'U$.

The recorded execution of \nolinkurl{LOWER_INTERTWINER} returns true for both the global identity and the conjunction of the four local equations. Each local residual is the zero matrix. One complete local result is:
''',listing(example_outputs['intertwining']['local_equations'][0]),r'''
This example deliberately changes packet coordinates as well as the operator. The complete input and four outputs are retained in \nolinkurl{examples/intertwining_input.json} and \nolinkurl{examples/intertwining.json}.
\subsection{Inspecting the dependency set}
The API exposes the dependencies used by the source-linked intertwining record:
\begin{lstlisting}
python runtime/machine_api.py deps PSC-I-T-BLOCK-INTERTWINING --transitive
\end{lstlisting}
''',listing(example_outputs['dependencies']),r'''
This is a dependency closure, not a newly generated proof. Reading each named record supplies its exact source statement, proof, and evidence coordinates.

\section{Transport profiles in use}
\subsection{Finite packet multiplication}
The packet-linear profile declares preservation of the direct operations required by packet multiplication. The command
\begin{lstlisting}
python runtime/machine_api.py transport PSC-I-T-BLOCK-MULTIPLICATION profiles/packet_linear.json
\end{lstlisting}
returns:
''',listing(example_outputs['transport_finite']),r'''
The pass is exactly a pass for the listed operation flags. In particular, it does not construct the target packet system or independently check a concrete functor's preservation laws.
\subsection{A countable result is blocked}
Using the same profile for the countable unconditional packet theorem returns:
''',listing(example_outputs['transport_countable']),r'''
The profile does not preserve the topological and completion operations required by this gate. A finite linear profile therefore cannot be used to pass this countable request.

The source theorem additionally requires a real or complex Banach space, unconditional reconstruction, and a uniform multiplier bound. These hypotheses remain visible in its statement. Supplying permissive operation flags would not prove those hypotheses. The richer source contract and the narrower executable gate must be kept distinct.
\subsection{Changing a profile without changing evidence}
A profile file is a declaration supplied to the runtime. Editing its flags changes the gate's output. It does not create mathematical preservation evidence. A downstream system that wants a transport certificate must retain the arguments or formal certificates justifying those flags and the target hypotheses.

The correct use is sequential: identify the exact record, inspect its source and dependency context, establish a target realization, justify the relevant preservation properties and hypotheses, then use the gate as an explicit consistency check. Its output can be attached to the resulting evidence record as one component.

\section{Reproduction and release maintenance}
\subsection{Documented payload checks}
From \nolinkurl{source/machine_v1.0.1/}, use an interpreter containing SymPy:
\begin{lstlisting}
python runtime/verify_release.py
python runtime/exact_fixture_suite.py
python runtime/nonzero_packet_regression.py
\end{lstlisting}
The first script checks entrypoint identity, record IDs, graph acyclicity and resolution, AST coverage, action-registry consistency, source hash, selected API queries and actions, structured transport response, and fixture replay. The second emits the detailed fixture results. The latter does not replace a theorem prover.
\subsection{Companion build}
From the machine companion directory, \nolinkurl{build_companion.py} replays these checks, captures the worked examples, verifies every frozen file against the original archive, generates the TeX, and builds the PDF. The environment variable \nolinkurl{PSC_PYTHON} can select a Python interpreter with SymPy. A TeX installation with the packages declared in the preamble is required for the PDF build.

The standalone source package includes a copy of the original machine release archive as provenance. The build accepts \nolinkurl{PSC_MACHINE_ARCHIVE} when that archive is stored elsewhere. The document source itself remains readable independently of the builder.
\subsection{A source change is a new evidence task}
If a source statement changes, its source and statement identity change. The KIR, AST, dependency annotations, operation profile, formal map, and tests must be reviewed for impact. A historical pass cannot be assigned to a new statement solely because the stable ID stayed the same.

For this release, v1.0.1 records the two narrow statement corrections and synchronized machine metadata. The v1.0.0 payload remains byte-for-byte unchanged in provenance. Editorial additions are outside the machine payload. The additional traditional models and visual appendix belong to the human companion until their own machine records are explicitly defined and mapped.
\subsection{Archived interfaces and current prose}
The earlier v0.8 machine-native PDF is retained as provenance in the collected materials. This volume replaces its editorial account for the corrected v1.0.1 interface. In particular, it describes the present runtime's exact transport-gate scope and preserves the mathematical records apart from the two disclosed corrections, without relabelling planner metadata as executed proof machinery.

\clearpage\appendix
\section{Complete source-linked record catalog}\label{app:catalog}
The following catalog is generated from the 108 frozen KIR records. Statements and attached proof bodies are reproduced from v1.0.1. Relative to v1.0.0, exactly two statements gain an explicit nonzero-packet assumption. No proof body is changed. Original source cross-references are linked to the matching stable record in this catalog. This rendering changes navigation, not the source statement or proof.

The evidence shorthand in each record is read literally. ``Mapped'' indicates that a historical Lean mapping exists. It does not collapse the distinctions in Appendix E. A source proof is written mathematical evidence. A typed signature is an interface description. A fixture exercises a bounded case.

''']
section=None
for i,r in enumerate(records,1):
 if r['section']!=section:
  section=r['section'];parts.append(r'\clearpage\subsection{Source section '+str(section)+': '+r['section_title']+'}\n')
 title=r['title']
 parts.append(r'\Needspace{8\baselineskip}\subsubsection*{'+str(i)+'. '+title+'}\n'+r'\phantomsection\label{rec:'+r['stable_id']+'}\n')
 parts.append(r'\field{Stable ID}{'+code(r['stable_id'])+'}\n')
 parts.append(r'\field{Kind and regime}{'+esc(r['kind'])+'; '+esc(', '.join(r.get('regimes',[])))+'}\n')
 parts.append(r'\textbf{Statement.}\par\n'.replace('\\n','\n')+math_source(r['statement_tex'])+'\n')
 if r.get('proof_tex'):parts.append('\n\\begin{proof}[Attached source proof]\n'+math_source(r['proof_tex'])+'\n\\end{proof}\n')
 deps=r.get('dependencies',[])
 parts.append(r'\field{Recorded dependencies}{'+('; '.join(link(x) for x in deps) if deps else 'None declared.')+'}\n')
 ext=r.get('external_dependencies',[])
 if ext: parts.append(r'\field{External dependencies}{'+esc('; '.join(ext))+'}\n')
 sig=r.get('typed_signature_status',''); py=r['evidence']['python']['status'];lm=r['evidence']['lean']['status']
 parts.append(r'\field{Evidence}{AST: '+code(r['statement_ast_status'])+'. Python: '+code(py)+'. Lean: '+code(lm)+'.}\n')
 acts=r.get('machine_actions',[])
 if acts:parts.append(r'\field{Actions}{'+'; '.join(code(a['action'])+' ('+code(a['execution_mode'])+')' for a in acts)+'}\n')
 ops=(r.get('proof_operation_profile') or {}).get('action_required_operations',[])
 if ops:parts.append(r'\field{Direct gate operations}{'+', '.join(code(x) for x in ops)+'}\n')
 guards=r.get('boundary_guards',[])
 if guards:parts.append(r'\field{Boundary metadata}{'+'; '.join(code(x) for x in guards)+'}\n')
 s=r['source'];loc=f"Statement lines {s['statement_start_line']}--{s['statement_end_line']}"
 if s.get('proof_start_line'):loc+=f"; proof lines {s['proof_start_line']}--{s['proof_end_line']}"
 parts.append(r'\field{Frozen source locator}{'+loc+'.}\n')
parts.append(r'''\clearpage\section{Typed core signatures}
These twenty signatures are reproduced from \nolinkurl{kir/core_typed_signatures.json}. Unicode mathematical characters are represented with standard JSON escapes in the listings. Their meanings are unchanged. The schema does not make these strings into independently checked proof terms.
''')
for rid,sig in typed.items():
 parts.append(r'\Needspace{7\baselineskip}\subsection*{'+by[rid]['title']+'}\n'+link(rid)+listing(sig))
parts.append(r'''\clearpage\section{Complete action registry}
The registry below contains all 37 action names. ``Implemented'' describes the frozen runtime dispatcher. It does not assert that all hypotheses of every linked source record are automatically validated. Record associations are links for inspection.
''')
for a in actions:
 parts.append(r'\Needspace{6\baselineskip}\subsection*{'+code(a['action'])+'}\n')
 parts.append(r'\field{Runtime implemented}{'+('Yes' if a['runtime_implemented'] else 'No')+'}\n')
 parts.append(r'\field{Modes}{'+', '.join(code(x) for x in a['execution_modes'])+'}\n')
 parts.append(r'\field{Records}{'+'; '.join(link(x) for x in a['records'])+'}\n')
parts.append(r'''\clearpage\section{Operation and hypothesis vocabulary}
The frozen ontology separates structural operations from hypothesis classes. These names form a controlled vocabulary for profiles and source-derived annotations. They are not a complete formal semantics for every mathematical construction named.
\begin{longtable}{@{}p{0.60\textwidth}p{0.31\textwidth}@{}}\toprule Name & Class\\\midrule\endhead
''')
for op,v in js('semantics/operation_ontology.json')['operations'].items():parts.append(code(op)+' & '+esc(v['class'])+'\\\\\n')
parts.append(r'\bottomrule\end{longtable}\clearpage\section{Historical Lean record map}'+'\n')
parts.append('This is the eight-entry mapping attached to the frozen machine release. The evidence descriptions and source-match categories are reproduced from that map. A fresh build performed elsewhere must be documented separately.\n')
for m in maps:
 parts.append(r'\Needspace{7\baselineskip}\subsection*{'+by[m['stable_id']]['title']+'}\n'+link(m['stable_id'])+'\n')
 parts.append(r'\field{Source match}{'+code(m['source_match'])+'}\n')
 parts.append(r'\field{Stored certificate status}{'+code(m['certificate_status'])+'}\n')
 parts.append(r'\field{Declarations}{'+'; '.join(code(x) for x in m['lean_declarations'])+'}\n')
 parts.append(esc(m['evidence'])+'\n')
parts.append(r'''\clearpage\section{Current verification receipt}
The following is the successful current run of the documented frozen release gate. The detailed exact-fixture output, command lines, interpreter versions, earlier missing-dependency explanation, and frozen-byte audit are retained in the build results.
'''+listing(results[0]['stdout'])+r'''\subsection*{Interpreter provenance}
'''+listing(versions['stdout'])+r'''\subsection*{Source and package preservation}
The companion's integrity audit compared each of the 65 original archived files with the copied payload. Every comparison passed. Generated Python bytecode caches, if any, are not part of the frozen release and are excluded from the delivered package.

\textbf{Proofreading scope.} The editorial prose, worked displays, generated links, tables, and record rendering were reviewed for local consistency. Source statements and proofs were reproduced from the corrected v1.0.1 records. The two audited nonzero-packet additions are the only mathematical-token changes relative to v1.0.0. This editorial review does not constitute a new mathematical proof audit.
\end{document}
''')
tex=''.join(parts).replace('\\n','\n') if False else ''.join(parts)
# Convert explicit newline markers without changing commands such as newcommand.
tex=re.sub(r'\\n(?![A-Za-z])',lambda m:'\n',tex)
tex=tex.replace('__MACHINE_SOURCE_HASH__',hashlib.sha256(source.encode()).hexdigest())
(ROOT/'Paper_I_Machine_Native_Final.tex').write_text(tex)
for n in range(3):
 p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','Paper_I_Machine_Native_Final.tex'],cwd=ROOT,capture_output=True,text=True)
 (OUT/f'pdflatex_pass{n+1}.txt').write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout[-5000:]);raise SystemExit('PDF build failed')
import shutil
shutil.copy2(OUT/'Paper_I_Machine_Native_Final.pdf',ROOT/'Paper_I_Machine_Native_Final.pdf')
print('Built',ROOT/'Paper_I_Machine_Native_Final.pdf')
