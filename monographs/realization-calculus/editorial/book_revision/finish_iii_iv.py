from pathlib import Path
import json,re,hashlib,shutil
R=Path(__file__).resolve().parents[2];S=R/'source_i_iv';B=S/'book_revision_before';L=R/'editorial/book_revision/iii_iv_edit_log.json';log=json.loads(L.read_text())
def edit(rel,fn,note):
 p=S/rel;b=p.read_text();a=fn(b)
 if a==b: raise ValueError('no change '+rel)
 q=B/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if not q.exists():shutil.copy2(p,q)
 p.write_text(a);log['changes'].append({'file':rel,'before_sha256':hashlib.sha256(b.encode()).hexdigest(),'after_sha256':hashlib.sha256(a.encode()).hexdigest(),'edits':[{'note':note}]})
IV='IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/'
# Every removed page number is on a vpage locator naming a result or section.
for rel in ['III/manuscript/visual_atlas.tex','III/guides/visual/source/pages_final.tex',IV+'traditional/atlas-pages.tex']:
 def clean(s):
  out=[]
  for line in s.splitlines(keepends=True):
   if line.startswith(r'\vpage'):
    assert any(t in line for t in ['Section','Theorem','Lemma','Corollary','Proposition','Definition','Formalization target','Sections','Appendix'])
    line=re.sub(r' \(p\. [0-9]+\)','',line)
   out.append(line)
  return ''.join(out)
 edit(rel,clean,'Removed redundant parenthetical standalone page numbers from named visual result/section locators; link IDs and result numbering retained.')
# Remove typesetting instructions from the reading text; they remain in exact source history.
edit('III/guides/lean/Paper_III_Lean_Guide_Final.tex',lambda s:re.sub(r'\n\\code\{build.py\} is a compile-only XeLaTeX builder\..*?(?=\\end\{document\})','\n',s,flags=re.S),'Removed two document-production paragraphs (PDF builder/rendering/fonts) from the mathematical reading text; no Lean commands/excerpts removed.')
edit('III/guides/lean/chapters/07_replay.tex',lambda s:re.sub(r'\\subsection\{Rebuilding this guide\}.*?(?=\\subsection\{The formal verification boundary\})','',s,flags=re.S),'Removed guide-typesetting/static-table-generation subsection, including an opaque checkpoint path; formal replay commands and source identity evidence retained.')
edit(IV+'lean_guide/chapters/08_replay.tex',lambda s:re.sub(r'\\subsection\{Rebuild this guide without running Lean\}.*?(?=\\subsection\{Failure modes worth recognizing\})','',s,flags=re.S).replace('Choose a manuscript record in the next ledger.','Choose a manuscript record in the coverage ledger.'),'Removed guide-typesetting instructions and corrected the ledger locator after adding a verification chapter. Lean commands and declared proof scope retained.')
III_add=r'''
\subsection*{Mathematical and finite evidence}
The main text contains 98 result environments and two classical standard facts. Its finite and nonlinear coordinate arguments, the Section~17 analytic arguments, and the 59 later results plus two classical inputs have ordinary mathematical reviews under their stated hypotheses. The statement register identifies their status individually; these review counts do not assert complete Lean coverage.

The accompanying finite evidence records 18,630 exact assertions across three coordinate and calculus suites, 124 visual-model checks, and four rejected false controls. The computation audit specifies the tested ranges and repeated cases. These finite calculations support the examples and implementations; they do not replace the ordinary proofs or extend the formal contract.

The mathematical reading route is the main text, the analytic packet supplement, the 24 worked visual plates with 22 exact model figures, and this declaration-level guide. The supplement supplies the range-space, norm, Taylor, composition, and support arguments, including degenerate cases and the relation to the formal interface. The formal source distribution includes its exact sources, dependency pins, verification transcripts, mathematical reviews, computation scripts, statement register, and SHA-256 manifest.
'''
edit('III/guides/lean/chapters/00_current_release.tex',lambda s:s.replace(r'\subsection*{Reproduce the formal verification}',III_add+'\n'+r'\subsection*{Reproduce the formal verification}'),'Adapted the release record\'s unique mathematical inventory, finite-evidence totals/limits, and reader route into the formal companion; omitted dates, edition chronology, obsolete rights claims, standalone page counts, and PDF build chatter.')
new=IV+'lean_guide/chapters/09_verification_scope.tex';p=S/new
assert not p.exists()
p.write_text(r'''\section{Pinned-source verification and its scope}
\label{sec:verification_scope}
The 68-result formal core passed a pinned-source replay, declaration-kind resolution, a transitive axiom audit, and compiler controls. All 119 Lean source files and their mathematical hypotheses remained unchanged. The 151-row reviewed map covers the full scoped statements of the 68 theorem-like manuscript records. This verification checks the exact inherited statement contract; it does not supply a new line-by-line mathematical proof of that correspondence.

\subsection{Production compilation and proof evidence}
The replay compiled all 118 production modules into an initially empty project-object directory. Each module ran separately with one Lean worker. The cumulative receipt fingerprints every successful source and output object. The aggregate imports the completed production closure; the original audit source and a generated declaration-kind consumer were then executed.

The compiler's binary hash and commit were checked, and all nine external package Git revisions matched the dependency manifest. Cached external objects were reused. The record therefore does not claim a cold rebuild of Mathlib or an independently implemented proof kernel.

\begin{longtable}{p{.34\textwidth}p{.56\textwidth}}
\toprule Evidence & Recorded scope \\ \midrule\endhead
Production compilation & 118 of 118 modules; new project objects \\
Source preservation & All 119 Lean source files unchanged \\
Reviewed targets & 1,164 targets: 953 theorems and 211 constructions \\
Namespace audit & 2,234 declarations, including 1,999 theorem declarations \\
Compiler controls & Six accepted outcomes under explicit diagnostics \\
Verifier tests & 42 verification tests and 10 integrity tests \\
\bottomrule
\end{longtable}
Supporting and generated declarations contribute to these totals; the totals are not counts of independent discoveries.

The exact runtime is Lean \code{4.34.0-rc2}, commit \code{6a10ac8c22beadecabdbb0919c2b50214762f91d}, with Mathlib revision \code{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. The compiler's SHA-256 fingerprint is \code{e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550}. The permitted transitive axioms are \code{propext}, \code{Classical.choice}, and \code{Quot.sound}.

\subsection{Controls and their diagnostics}
A valid projector-idempotence application is accepted. An explicit false theorem, an admitted proof, an omitted premise, an injected custom axiom, and a definition presented as a theorem must produce their intended rejection diagnostics. A timeout, signal kill, missing import, or unrelated API error does not count as successful rejection.

The warning policy is material to this contract. The inherited \code{-E warning} setting accepted an isolated deliberately admitted proof with exit code 0. The verified replay instead uses \code{-DwarningAsError=true}, which rejected that fixture with exit code 1. The production mathematical sources were not weakened or edited.

The verifier tests use the recovered typed source contract and adversarial mutations of rows, targets, evidence labels, axiom reports, and process outcomes. A descendant-process cleanup fixture waits for explicit child readiness before applying a separate bounded execution deadline. An earlier timeout before readiness did not establish that the descendant had started and is retained as a failed check. The final 42-test suite passes.

The ten integrity tests cover changed bytes, missing files, unexpected files, duplicate records, unsafe paths, symlinks, prohibited font files, and positive and empty-manifest cases. The distribution manifest describes the actual 836-file preserved tree; it does not require the 73 excluded font files listed in an older manifest. The exact earlier unsaved fixture-control failure was not recovered, so the record makes no claim to reproduce that absent script. The replacement controls directly exercise the recovered checker's actual typed records and have their own fingerprints and receipts.

\subsection{Finite computations and their limits}
The finite computations were executed separately from Lean. Their domains overlap, so the following rows are not added into one total. They support the implementations and worked examples. Universal statements rely on proof terms under their declared hypotheses.

\begin{longtable}{p{.49\textwidth}p{.41\textwidth}}
\toprule Suite & Recorded result \\ \midrule\endhead
Exact algebra & 1,008 exact rational assertions \\
Visual examples & 147 symbolic, finite, and enclosure checks \\
Original tables & 981 of 981 rows checked \\
Strengthened-paper suite & 1,246 of 1,246 checks passed \\
Original-paper suite & 647 of 647 checks passed \\
Rational subset and brackets & 818 rational table rows; four bracket records \\
\bottomrule
\end{longtable}
The previously documented weakness of the strengthened numerical suite remains relevant: its historical acceptance of mutations limits what its passing total can establish. It does not replace the formal contract or the targeted compiler controls.

The recorded computation environment was Python 3.13.5, SymPy 1.14.0, mpmath 1.3.0, NumPy 2.3.5, pandas 2.2.3, and Matplotlib 3.10.8. These versions were detected during execution. All 836 files in the preserved baseline remained byte-identical before and after the finite replay; results and logs were written separately.

\subsection{Evidence files and reproduction}
The formal verification distribution retains compiler logs, generated consumers, fixtures, source hashes, and project output objects. The external runtime and dependency cache are separate requirements. The principal evidence records are:
\begin{itemize}
\item \code{verification/lean_primary/REPLAY.json} and \code{verification/lean_primary/AXIOM_REPORTS.json};
\item \code{verification/SOURCE_MAP_CHECK.json} and \code{verification/SOURCE_CONTRACT.json};
\item \code{verification/finite_primary/FINITE_REPLAY.json};
\item \code{verification/VERIFIER_TESTS.json} and \code{verification/INTEGRITY_TESTS.json}.
\end{itemize}
The following commands belong to that formal verification distribution, not to the collected book's typesetting directory:
\begin{Verbatim}[fontsize=\small,breaklines=true,breakanywhere=true]
python3 -B scripts/verify_release.py
python3 -B scripts/run_checks.py --mode finite --work /tmp/paper-iv-finite
bash Run-Replay.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 /tmp/paper-iv-full
\end{Verbatim}
Use a new writable working directory outside the frozen source. The first command checks stored evidence and file integrity; it does not rerun the kernel. Finite mode reruns the examples and verifier controls. Full mode additionally compiles every production module and repeats the formal audits. These commands do not download or install dependencies.

The complete replay targets Linux or WSL with Python 3.11 or newer, the pinned Lean runtime, and matching cached packages. The recorded run used a four-GiB container, one Lean worker, a 3,072-MiB Lean heap setting, and a 300-second per-command deadline. This is not a native-Windows or general cross-platform reproducibility claim. The archived offline runtime supplied the successful compiler and cache when network-based recovery was unavailable.

\subsection{Mathematical boundaries}
Imported standard fact 11.1 remains outside the 68-result contract. The core does not assert universal simplicity of all zeros, positivity of every reduced zero, a full displacement expansion, or a zeta functional equation. Eventual simplicity, branch choices, multiplicities, and nearest-pole asymptotics retain their stated hypotheses and ranges. The separately preserved visual reader includes a branch-sensitive clarification of reciprocal powers; no older editable source is substituted for that reader.
''')
log['changes'].append({'file':new,'new_file':True,'source':'Paper_IV_Verification_Closeout_v1.1.0.pdf, pp. 1–5','after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'edits':[{'note':'Adapted unique verification scope, control diagnostics, evidence totals, exact runtime identity and reproduction conditions into the formal companion. Omitted release chronology, reader page counts, next-paper task status and obsolete licence decision text.'}]})
edit(IV+'lean_guide/Paper_IV_Lean_Guide_Final.tex',lambda s:s.replace(r'\clearpage\input{chapters/08_replay}',r'\clearpage\input{chapters/08_replay}'+'\n'+r'\clearpage\input{chapters/09_verification_scope}'),'Included the verification-scope chapter after formal replay and before the manuscript coverage ledger.')
L.write_text(json.dumps(log,indent=2));print('Updated',len(set(x['file'] for x in log['changes'])),'files including one new chapter')
