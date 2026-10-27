from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];p=root/'monograph/Constructive_Repair.tex';s=p.read_text(encoding="utf-8")
if '\\label{app:rational-register}' in s: raise SystemExit('Evidence appendix already present; no duplicate insertion performed')
reg=json.loads((root/'docs/theorem_registry.json').read_text(encoding="utf-8"))['theorems'];v=json.loads((root/'evidence/verification/current/verification.json').read_text(encoding="utf-8"));idx=json.loads((root/'evidence/export_index.json').read_text(encoding="utf-8"));demo=json.loads((root/'evidence/one_command_demo/result.json').read_text(encoding="utf-8"))
assert v['status']=='PASS' and demo['status']=='KERNEL_CHECKED_OPTIMAL_REPAIR'
roles={
'checkRepair_sound':'An accepted rational coefficient table repairs the fixed original residual family.',
'annihilator_kills_residual':'An annihilator of both correction ranges annihilates every successfully repaired residual.',
'separator_sound':'A nonzero detected residual rules out a correction by that fixed menu.',
'checkSeparator_sound':'The Boolean separating-row checker is sound.',
'checkOptimal_sound':'A successful menu with separators for all cheaper admissible menus is globally minimum cost within the declared menu.',
'checkNoRepair_sound':'Separators for every admissible subset certify rejection in that finite universe.',
'dimension_certificate_right_inverse':'Every competing repair supplies an explicit right inverse of the detected added map.',
'width_le_of_right_inverse':'A rectangular rational map with a right inverse has at least as many source as target coordinates.',
'dimension_certificate_lower_bound':'The matrix identities imply the lower bound against every competing rational augmentation.',
'checkDimension_sound':'A successful repair and a lower certificate certify attained minimum dimension.',
'checkRank_sound':'A factorization and an identity minor certificate prove the declared exact rank.',
'split_constructs_repair':'The split and residual factorization explicitly construct the correction coefficients.',
'split_correctable_iff':'The complete detector vanishes exactly when the original rational matrix equation is solvable.',
'checkOptimalConstruction_sound':'Four matrix identities construct an attaining repair and prove its minimum added dimension.',
'constructed_repair_in_legal_image':'An additional image identity certifies that the constructed directions are legal.',
'decodeCell_zero':'A typed rational cell with denominator zero is rejected.',
'decodeCell_nonzero':'A cell with nonzero denominator decodes to the stated rational value.',
'decodeCell_sound':'Successful cell decoding entails a nonzero denominator and the correct value.',
'checkWireMatrix_sound':'The finite matrix validity check certifies all denominators.',
'decodeWireMatrix_cell':'Matrix decoding agrees pointwise with successful cell decoding.'}
parts=[r'\chapter{Rational bridge declaration register}\label{app:rational-register}',
 r'The twenty general declarations below supplement the unchanged original register. All source paths are relative to the release root. The full machine-readable register in \code{docs/theorem_registry.json} includes every concrete case and every named rejection theorem as well.',
]
for mod in ['RationalCertificates','ConstructiveMatrix','Wire']:
    parts += ['\\section{'+mod+'}',r'Source: \nolinkurl{lean/KomorebiRepair/'+mod+r'.lean}.']
    for x in reg:
        if x['module']==mod:
            name=x['name'].removeprefix('KomorebiRepair.')
            role=roles[x['name'].split('.')[-1]]
            parts.append('\\record{'+name+'}{'+str(x['line'])+'}{'+role+'}')
parts += [r'\section{Concrete exported problems}',
 r'Each row below denotes one original problem and its separately supplied certificate. Every case has six named proofs: \code{input_encoding_valid}, \code{certificate_encoding_valid}, \code{certificate_checked}, \code{original_equations_checked}, \code{output_matches_construction}, and \code{optimal}. The last theorem quantifies over every competing rational augmentation, not only the candidates tested by Python.',
 r'\begin{longtable}{@{}lrrrrrp{1.75in}@{}}',r'\toprule Case & $m$ & $n$ & $s$ & $d$ & $t$ & Example class\\ \midrule\endhead']
for x in idx:
    inp=json.loads((root/x['input']).read_text(encoding="utf-8"));c=json.loads((root/x['certificate']).read_text(encoding="utf-8"))
    label=x['label'].replace('_',' ')
    parts.append(f"{x['namespace']} & {inp['D']['rows']} & {inp['D']['cols']} & {inp['R']['cols']} & {c['d']} & {c['t']} & {label}\\\\")
parts += [r'\bottomrule\end{longtable}',
 r'The input and certificate sources are grouped in \code{Generated/Inputs00.lean} through \code{Inputs03.lean}, and \code{Generated/Certificates00.lean} through \code{Certificates03.lean}. Groups contain six cases each. The JSON index gives the exact original input hash for each row.',
 r'\section{Menu and corruption examples}',
 r'The eight \code{RationalMenus} declarations check the two-entry optimum, restricted rejection, invalid data, and zero- and one-rank certificates. Six further named proofs in \code{RejectedCertificates.lean} establish that deliberately corrupted checks return false. Their companion invalid files attempt to use these false equalities as true equalities and are required to fail for the intended type mismatch.',
 r'\chapter{Fresh verification and executable use}\label{app:fresh}',
 r'\section{The v0.3.0 execution}',
 r'The runtime was recovered from the previously supplied archive parts and its joined checksum was matched before extraction. The compiler reports Lean \code{4.34.0-rc2}; the actual Mathlib checkout has revision \code{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. The combined project was rebuilt from its own source files after removing its previous object files. The dependency cache was retained.',
 r'\begin{center}\begin{tabularx}{\linewidth}{@{}Xr@{}}\toprule Fresh check & Result\\\midrule',
 r'Proof modules compiled and individually replayed & 23 / 23\\',
 r'Named theorem dependencies audited & 227 / 227\\',
 r'Unchanged original declarations & 49\\',
 r'New general certificate and decoding declarations & 20\\',
 r'New concrete declarations & 158\\',
 r'Exported original problems with optimality proofs & 24 / 24\\',
 r'Paired corruption rejection controls & 6 / 6\\',
 r'Separate forbidden-axiom policy control & 1 / 1\\',
 r'Lean input echoes compared with original JSON & 24 / 24\\',
 r'New Python unit tests & 34 / 34\\',
 r'Exact matrix cases with independent SymPy ranks & 264 / 264\\',
 r'Inherited Python unit tests rerun & 20 / 20\\',
 r'Inherited exact audit case records reproduced & 3,307\\',
 r'\bottomrule\end{tabularx}\end{center}',
 r'The 158 new concrete declarations consist of 144 input/certificate proofs for the 24 original problems, eight menu/rank examples, and six rejection examples. These are coverage counts, not counts of independent discoveries. The general theorems and the concrete proofs have separately labeled entries in the source registry.',
 r'Every audited dependency set is contained in \{\code{propext}, \code{Classical.choice}, \code{Quot.sound}\}. No added assumption, placeholder or native-decision axiom is accepted. The module replay invokes the same Lean kernel, not an independently implemented proof checker. It does not re-prove all imported Mathlib declarations.',
 r'\section{The single-command example}',
 r'The release includes \code{scripts/certify_one.py}. Given an original JSON input and the pinned offline kit, it constructs a certificate in a new local directory, emits the input separately from the witness, compiles the generic modules and the concrete proof, audits all relevant axioms, replays the modules, and compares a Lean-decoded echo with the original numeric data.',
 r'\begin{Verbatim}[fontsize=\small,breaklines=true]',
 'export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2',
 'python scripts/certify_one.py examples/corpus/Case001_input.json --output /tmp/my-repair',
 r'\end{Verbatim}',
 r'This exact workflow was executed on the fractional example. It ended with \code{KERNEL_CHECKED_OPTIMAL_REPAIR} and $t=1$. It requires no network access or publication service. An existing output directory is refused so that previous evidence is not silently overwritten. The large compiler and dependency kit are not duplicated in the small source handoff.',
 r'\section{Failures and their corrections}',
 r'The first compilation attempt with a broad tactic import was interrupted. The implemented modules use the required direct imports. Plain \code{decide} did not reduce the first rational matrix fixture, so the producer now emits \code{decide +kernel}. The typed validity predicate initially lacked a reducible decidability path and was corrected. An ambiguous corruption diagnostic was replaced by paired rejection proofs. In the final control, the false checker result is itself proved before an invalid true result is rejected.',
 r'The development snapshots and logs remain in \code{evidence/development}. Interrupted and superseded runs are not counted as successful checks. The final clean record under \code{evidence/verification/current} governs this edition.',
 r'\section{Remaining boundaries}',
 r'The new code is a standalone extension. It has not been integrated into the authoritative Komorebi Python library or Paper III source tree. A production rational-menu exporter, full formalization of the JSON parser, and a formal connection of the matrix rank-difference formula to the earlier quotient API remain separate tasks. The current free-augmentation exporter, certificate soundness, attaining construction, and finite literal proofs are complete within their stated rational matrix scope.',
 r'The construction does not establish unrestricted nonlinear repair, integral or arithmetic realization, or a universal semantic theorem for Komorebi Space. It does not alter Conjecture 66. Its purpose is narrower and operational: allow an untrusted numerical search to submit exact witnesses that are checked against the original problem.'
]
extra='\n\n'.join(parts)+'\n'
s=s.replace('\\backmatter',extra+'\n\\backmatter',1)
s=s.replace('\\begin{thebibliography}{9}','\\begin{thebibliography}{9}\n\\bibitem{bridge}\nKomorebi P. \\emph{Constructive Repair v0.3.0: Exact Rational Certificate Bridge}. Python producer, Lean certificate modules, fixed-input records, fresh compilation and same-kernel replay evidence, 19 October 2026.\n')
p.write_text(s, encoding="utf-8")
print('Monograph lines',len(s.splitlines()))
