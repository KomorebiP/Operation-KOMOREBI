from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
GEN = ROOT / 'generated'
GEN.mkdir(parents=True, exist_ok=True)
JSON_PATH = ROOT / 'Komorebi_Theorem_Concordance_v0.4.json'
data = json.loads(JSON_PATH.read_text(encoding='utf-8'))


def tex_escape(text: str) -> str:
    if text is None:
        return ''
    s = str(text)
    # Protect semantic unicode tokens with placeholders before generic escaping.
    repl = {
        '↔': '@@LEFTRIGHT@@',
        '→': '@@TO@@',
        '⇒': '@@RIGHTARROW@@',
        '≃': '@@SIMEQ@@',
        '∈': '@@IN@@',
        'Π': '@@PI@@',
        'Φ': '@@PHI@@',
        'α': '@@ALPHA@@',
        'β': '@@BETA@@',
        'γ': '@@GAMMA@@',
        'η': '@@ETA@@',
        'κ': '@@KAPPA@@',
        'Čech': '@@CECH@@',
        'Faà': '@@FAA@@',
        '–': '--',
        '—': '---',
        '§': '@@SECTION@@',
        '“': '``',
        '”': "''",
        '’': "'",
        '‘': "'",
        '×': '@@TIMES@@',
        '≤': '@@LEQ@@',
        '≥': '@@GEQ@@',
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    # Escape TeX text specials.
    s = s.replace('\\', r'\textbackslash{}')
    for a, b in [
        ('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
        ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]:
        s = s.replace(a, b)
    # Restore semantic tokens.
    restore = {
        '@@LEFTRIGHT@@': r'\(\leftrightarrow\)',
        '@@TO@@': r'\(\to\)',
        '@@RIGHTARROW@@': r'\(\Rightarrow\)',
        '@@SIMEQ@@': r'\(\simeq\)',
        '@@IN@@': r'\(\in\)',
        '@@PI@@': r'\(\Pi\)',
        '@@PHI@@': r'\(\Phi\)',
        '@@ALPHA@@': r'\(\alpha\)',
        '@@BETA@@': r'\(\beta\)',
        '@@GAMMA@@': r'\(\gamma\)',
        '@@ETA@@': r'\(\eta\)',
        '@@KAPPA@@': r'\(\kappa\)',
        '@@CECH@@': r'\v{C}ech',
        '@@FAA@@': r'Fa\`a',
        '@@SECTION@@': r'\S{}',
        '@@TIMES@@': r'\(\times\)',
        '@@LEQ@@': r'\(\leq\)',
        '@@GEQ@@': r'\(\geq\)',
    }
    for a, b in restore.items():
        s = s.replace(a, b)
    return s


def source_text(name: str) -> str:
    return r'\nolinkurl{' + name.replace('}', r'\}') + '}'


def hash_tex(h: str) -> str:
    return r'\texttt{\seqsplit{' + h + '}}'

status_macro = {
    'proved internally': r'\StatusInternal',
    'proved conditionally': r'\StatusConditional',
    'classical theorem imported and reinterpreted': r'\StatusClassical',
    'computationally verified only': r'\StatusComputed',
    'definition or framework only': r'\StatusFramework',
    'conjectural': r'\StatusConjectural',
    'superseded by a stronger edition': r'\StatusSuperseded',
    'externally validated or peer reviewed': r'\StatusExternal',
}

# Status summary table
status_order = [
    'proved internally',
    'classical theorem imported and reinterpreted',
    'proved conditionally',
    'definition or framework only',
    'conjectural',
]
row_count = int(data['summary']['row_count'])
lines = [r'\begin{table}[t]', r'\centering', rf'\caption{{Status distribution in the {row_count}-component theorem concordance.}}', r'\label{tab:status-summary}', r'\small', r'\begin{tabular}{@{}lr@{}}', r'\toprule', r'Classification & Components\\', r'\midrule']
for st in status_order:
    lines.append(f"{status_macro[st]} & {data['summary']['status_counts'][st]}\\\\")
lines += [r'\midrule', rf'\textbf{{Total}} & \textbf{{{row_count}}}\\', r'\bottomrule', r'\end{tabular}', r'\end{table}']
(GEN / 'status_summary_table.tex').write_text('\n'.join(lines) + '\n')

# Domain summary table
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Concordance coverage by mathematical domain.}', r'\label{tab:domain-summary}', r'\small', r'\begin{tabular}{@{}lr@{}}', r'\toprule', r'Domain & Components\\', r'\midrule']
for domain, count in data['summary']['domain_counts'].items():
    lines.append(f"{tex_escape(domain)} & {count}\\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(GEN / 'domain_summary_table.tex').write_text('\n'.join(lines) + '\n')

# Source edition ledger
lines = [
    r'\begingroup',
    r'\setlength{\tabcolsep}{3pt}',
    r'\begin{longtable}{@{}L{0.18\textwidth}L{0.22\textwidth}L{0.25\textwidth}L{0.29\textwidth}@{}}',
    r'\caption{Edition-control ledger. Full hashes are retained so later strengthened editions can supersede specific rows without losing provenance.}\label{tab:edition-ledger}\\',
    r'\toprule',
    r'Source family & Selected file & SHA-256 & Decision\\',
    r'\midrule',
    r'\endfirsthead',
    r'\toprule',
    r'Source family & Selected file & SHA-256 & Decision\\',
    r'\midrule',
    r'\endhead',
    r'\midrule',
    r'\multicolumn{4}{r}{\small Continued on next page}\\',
    r'\endfoot',
    r'\bottomrule',
    r'\endlastfoot',
]
for row in data['edition_control']:
    lines.append(f"{tex_escape(row['source'])} & {source_text(row['file'])} & {hash_tex(row['sha256'])} & {tex_escape(row['decision'])}\\\\[3pt]")
lines.append(r'\end{longtable}')
lines.append(r'\endgroup')
(GEN / 'edition_ledger.tex').write_text('\n'.join(lines) + '\n')

# Detailed concordance entries grouped by domain
by_domain: OrderedDict[str, list[dict]] = OrderedDict()
for row in data['concordance']:
    by_domain.setdefault(row['domain'], []).append(row)

lines = []
for domain, rows in by_domain.items():
    lines.append(r'\section{' + tex_escape(domain) + '}')
    for row in rows:
        st = status_macro.get(row['status'], tex_escape(row['status']))
        lines += [
            r'\begin{ConcordanceEntry}{' + tex_escape(row['id']) + r'}{' + tex_escape(row['proposed_component']) + r'}{' + st + r'}',
            r'\ConcordanceField{Strongest source}{' + source_text(row['strongest_source']) + r'}',
            r'\ConcordanceField{Exact theorem or section}{' + tex_escape(row['exact_theorem_or_section']) + r'}',
            r'\ConcordanceField{Hypotheses}{' + tex_escape(row['hypotheses']) + r'}',
            r'\ConcordanceField{Imported input}{' + tex_escape(row['imported_input']) + r'}',
            r'\ConcordanceField{Remaining obligation}{' + tex_escape(row['what_remains']) + r'}',
            r'\end{ConcordanceEntry}',
            '',
        ]
(GEN / 'concordance_entries.tex').write_text('\n'.join(lines) + '\n')

# Compact concordance index
lines = [
    r'\begin{longtable}{@{}L{0.09\textwidth}L{0.29\textwidth}L{0.22\textwidth}L{0.30\textwidth}@{}}',
    r'\caption{Compact index to the theorem concordance. The detailed hypotheses and obligations appear in Appendix~\ref{app:full-concordance}.}\label{tab:compact-concordance}\\',
    r'\toprule',
    r'ID & Component & Status & Strongest source\\',
    r'\midrule',
    r'\endfirsthead',
    r'\toprule',
    r'ID & Component & Status & Strongest source\\',
    r'\midrule',
    r'\endhead',
    r'\midrule',
    r'\multicolumn{4}{r}{\small Continued on next page}\\',
    r'\endfoot',
    r'\bottomrule',
    r'\endlastfoot',
]
for row in data['concordance']:
    st = status_macro.get(row['status'], tex_escape(row['status']))
    lines.append(f"{tex_escape(row['id'])} & {tex_escape(row['proposed_component'])} & {st} & {source_text(row['strongest_source'])}\\\\")
lines.append(r'\end{longtable}')
(GEN / 'compact_concordance.tex').write_text('\n'.join(lines) + '\n')

# Extension obligations after the Block 16 holonomy-twisted lane-transport milestone
obligations = [
    ('PO-01', 'Extend the profile-indexed resolved envelope', r'\StatusConditional', 'The additive-Karoubi core is proved. Add nonlinear, completion, monoidal, or integral doctrines only for newly selected strata and prove the corresponding profile-indexed universal property.'),
    ('PO-02', 'Freeze explicit finite atlases', r'\StatusInternal', 'Closed for the unit-periodic, rational-mask, fixed-radix regular, product-multiplicative, continuous local Newton--Mahler, marked binomial--Fuchsian, selected algebraic, marked nonlinear-tree, and finite semisimple Galois atlases, and assembled into the five-component certified Block 13 atlas. Every further enlargement must again declare its semantic domain, chart categories, overlap categories, and component tag.'),
    ('PO-03', 'Define morphisms and normalized subcategories', r'\StatusInternal', 'Closed for fixed-radix regular sequences, the canonical integral raw/saturated lattice record, fixed-basis Euler products, integral multiplicative functions, and continuous Newton--Mahler functions with complete branch packets. The marked binomial--Fuchsian holonomic chart, selected one-variable algebraic branch chart, marked polynomial fixed-point chart, finite semisimple subgroup chart, framed semilinear vector chart, and neutral Tannakian chart are closed; unrestricted holonomic, multivariate algebraic, unmarked nonlinear, semiring, cross-radix, unrestricted-product, modular, wild, and nonneutral enlargements remain separate passport obligations.'),
    ('PO-04', 'Type each bridge', r'\StatusInternal', 'Closed for the authoritative Block 13 matrix on the certified domains, including equivalences on named overlaps, fully faithful inclusions, directional losses, constructors, partial bridges, and explicit absent cells. Every extension must retain the same bridge passport and information-loss discipline.'),
    ('PO-05', 'Prove bridge naturality', r'\StatusInternal', 'Closed for digit sections, behavior quotients, Hankel factorization, Smith reduction, Euler logarithmic derivatives, local Dirichlet products, divisor-ghost inversion, Mahler analysis and synthesis, affine polyphase transport, mixed-radix composition, valuation certificates, coefficient/Ore translation, hypergeometric packet synthesis, the marked alias/cancellation ledger, packet-polynomial residue reduction, Weil-restriction degree transport, the algebraic collision ledger, diagonal packet Faà di Bruno profile compression, SCC elimination, marked tree-address transport, subgroup inclusion, Reynolds averaging, normal quotient compression, Hilbert-90 gauge trivialization, and projective Brauer boundary transport on the declared overlaps.'),
    ('PO-06', 'Prove higher coherence', r'\StatusInternal', 'Closed on every reversible cycle of the five-component certified atlas by the Block 13 normalizer-induced coherence theorem. Unframed vector descent retains intrinsic GL automorphisms, and broader atlases may have nontrivial comparison automorphisms or nonvanishing higher defects.'),
    ('PO-07', 'Prove object effectivity', r'\StatusInternal', 'Closed for the verified digital, regular, integral, fixed-Euler-basis, multiplicative, divisor-ghost, and continuous Newton--Mahler domains, the marked binomial--Fuchsian domain, the selected algebraic branch domain, the marked nonlinear-system domain, the finite subgroup/projector domain, and framed finite Galois vector descent by explicit normalization from the represented semantic object and retained generator or symmetry data.'),
    ('PO-08', 'Prove morphism effectivity', r'\StatusInternal', 'Closed for the verified atlases because their normalized fibers are contractible or discrete; the complete clopen local packet also glues equality morphisms by explicit piecewise synthesis; the marked holonomic, selected algebraic, and marked nonlinear fibers are discrete; finite Galois vector morphisms descend by fixed points and scalar extension. Unframed symmetry groupoids retain intrinsic automorphisms and require genuine groupoid descent.'),
    ('PO-09', 'Construct native comparison maps', r'\StatusInternal', 'Closed on the five certified components. Block 13 packages the digital-regular-mask-periodic, continuous Newton--Mahler, marked Fuss, Euler--multiplicative, and finite Galois native coordinates into coherent comparison families. Comparisons for unrestricted broad strata remain separate obligations.'),
    ('PO-10', 'Control isomorphism descent', r'\StatusInternal', 'Closed for the five-component certified atlas: normalized fibers are discrete or contractible, comparison cells are coherent, and compatible local isomorphisms descend. In broader atlases identify or kill holonomy, cokernel, Brauer, nonneutral tensor, or higher-coherence obstructions.'),
    ('PO-11', 'Broaden automatic and regular invariants', r'\StatusConditional', 'Fixed-radix field normalization, canonical integral saturation, Smith--Fitting reduction profiles, and compatible prime-power semantic towers are closed under the Block 06 hypotheses. Cross-radix comparison, arbitrary coefficient rings and semirings, and effective recognition from finite data remain open.'),
    ('PO-12', 'Normalize product and multiplicative strata', r'\StatusInternal', 'Closed for the fixed integral Euler basis, integral multiplicative functions, and the multiplicative divisor-ghost overlap. Minimal compilers, unrestricted product grammars, monoidal closure of the overlap, and any global Cauchy-Dirichlet equivalence remain open.'),
    ('PO-13', 'Broaden local Mahler theory', r'\StatusInternal', r'Closed for continuous \(\mathbb Z_p\)-valued functions, canonical Newton--Mahler coefficients, complete clopen and coefficient packets, finite-degree affine channels, sharp standard packet sizes, and principal-unit precision ladders. Exact higher kernel valuations, optimal mixed-radix trees, nonlinear local systems, state recognition, and a combined spectral--local signature remain open.'),
    ('PO-14', 'Broaden holonomic packet minimality', r'\StatusConditional', 'Canonical minimal Ore charts and the marked binomial--Fuchsian packet-order theorem are closed. General minimal multisection operators, canonical desingularization, monodromy-extension data, differential-module cyclicity, and a finite signature beyond the marked family remain open.'),
    ('PO-15', 'Broaden algebraic packet minimality', r'\StatusInternal', r'Finite selected-branch normalization, exact packet polynomial systems, the generic \(d^N\) Weil-restriction bound, and marked collision signatures are closed. Minimal multivariate system dimension, optimal symmetry-reduced degree bounds, ramified Puiseux passports, and universal branch-recognition algorithms remain open.'),
    ('PO-16', 'Broaden nonlinear and tree signatures', r'\StatusInternal', 'Closed for marked polynomial fixed points, complete packet jets, repeated-direction Faà di Bruno profile compression, address-preserving SCC reduction, and positive simply generated tree support and dominant-orbit signatures. Arbitrary mixed directions, coordinate-free minimum nonlinear system dimension, sign-canceling tree weights, unmarked generators, noncontractive global dynamics, and a universal operadic normal form remain open.'),
    ('PO-17', 'Extend modular, wild, and nonneutral symmetry', r'\StatusConditional', 'Finite semisimple Reynolds charts, framed Hilbert-90 descent, the projective Brauer obstruction, profinite finite-level reconstruction, and neutral Tannakian symmetry are closed. Derived fixed points, integral wild ramification, group-scheme torsion, nonneutral fiber functors, and gerbe-valued descent remain open.'),
    ('PO-18', 'Maintain theorem and edition provenance', r'\StatusConditional', 'Ongoing. Every new claim must cite the selected strongest edition, exact theorem, hypotheses, imported input, and superseded predecessor.'),
    ('PO-19', 'Separate internal proof from external validation', r'\StatusConditional', 'Ongoing. Keep direct proof, exact computation, imported classical theorem, conjecture, and independent peer review in distinct status fields.'),
    ('PO-20', 'Extend the global invariant beyond the certified spine', r'\StatusConditional', 'Work Package 6 is closed on the five-component finite atlas. Remaining targets are cross-radix comparison, semiring and all-ring normalization, unrestricted holonomic and multivariate algebraic invariants, unmarked nonlinear systems, modular and wild symmetry, nonneutral tensor descent, and any genuine bridges joining the current component tags.'),
    ('PO-21', 'Extend lane transport beyond the finite profiled theorem', r'\StatusConditional', 'The complete finite split-idempotent calculus and its finite nontrivial-address-holonomy extension are closed under their printed hypotheses. Complete matrices descend as matrix-local-system sections, monodromy orbits give the finest ordinary projector coarsening, and pair orbits govern compatible selectors. Infinite resolutions, non-split decompositions, noninvertible transitions, general nonlinear doctrines, higher-stack effectivity, historical novelty, and unrestricted atlas globalization remain separate obligations.'),
    ('PO-22', 'Recognize task quotients effectively', r'\StatusConditional', 'The fiberwise behavioral quotient and finite-dimensional stabilization theorems are proved. Effective recognition for infinite systems, symbolic query languages, enriched observations, and undecidable continuation grammars remains open.'),
    ('PO-23', 'Extend exact semantic loss beyond modules', r'\StatusConditional', 'The semantic diamond, bridge-loss sequence, and extension law are proved in module categories. Exact, regular, homological, semiring, topological, and higher-categorical analogues require their own quotient and exactness doctrines.'),
    ('PO-24', 'Classify carrier and observer comparison maps', r'\StatusConditional', 'Kernel factorization and the joint semantic completion are closed for algebraic carriers, and the relation module is closed over fields. Classification of lawful changes among noncommutative, measure-valued, completed, probabilistic, and nonlinear carriers remains open.'),
    ('PO-25', 'Control admissibility and attainment', r'\StatusConditional', 'Admissibility monotonicity and the completion/gap/escape trichotomy are proved. Effective optimal-geometry construction, attainment criteria, and conditioning rates remain doctrine-specific.'),
    ('PO-26', 'Build doctrine-level coherence only from certified cells', r'\StatusFramework', 'The doctrine-indexed task-fiber architecture is stated and several concrete lifting gates are proved. A complete double category, bicategory, or higher stack of doctrines is not yet constructed and must not be inferred from the fiberwise theorems.'),
]
lines = [
    r'\begin{longtable}{@{}L{0.07\textwidth}L{0.20\textwidth}L{0.17\textwidth}L{0.48\textwidth}@{}}',
    r'\caption{General extension obligations after the formal foundations v2.0 milestone.}\label{tab:proof-obligations}\\',
    r'\toprule',
    r'ID & Obligation & Current status & Remaining completion criterion\\',
    r'\midrule',
    r'\endfirsthead',
    r'\toprule',
    r'ID & Obligation & Current status & Remaining completion criterion\\',
    r'\midrule',
    r'\endhead',
    r'\midrule',
    r'\multicolumn{4}{r}{\small Continued on next page}\\',
    r'\endfoot',
    r'\bottomrule',
    r'\endlastfoot',
]
for oid, title, status, criterion in obligations:
    lines.append(f"{oid} & {title} & {status} & {criterion}\\\\[3pt]")
lines.append(r'\end{longtable}')
(GEN / 'proof_obligations.tex').write_text('\n'.join(lines) + '\n')

# Validation record
v = data['validation']['core_transfer_addendum_04']
lines = [
    r'\begin{table}[htbp]',
    r'\centering',
    r'\caption{Internal validation record for Core-Transfer Addendum 04.}',
    r'\label{tab:validation}',
    r'\small',
    r'\begin{tabularx}{\textwidth}{@{}L{0.27\textwidth}Y@{}}',
    r'\toprule',
    r'Check & Recorded result\\',
    r'\midrule',
    f"Package verifier & Overall pass: {str(v['package_verifier']['overall_pass']).lower()}; {v['package_verifier']['ledger_entries']} ledger entries; {v['package_verifier']['missing_files']} missing; {v['package_verifier']['extra_files']} extra; {v['package_verifier']['mismatched_files']} mismatched.\\\\",
    f"Exact theorem verifier & {v['theorem_verifier']['passed']} of {v['theorem_verifier']['total']} gates passed; arithmetic used {tex_escape(v['theorem_verifier']['arithmetic'])}.\\\\",
    f"Full unit-test attempt & {tex_escape(v['full_unittest_attempt']['reason'])}\\\\",
    f"Boundary & {tex_escape(v['boundary'])}\\\\",
    r'\bottomrule',
    r'\end{tabularx}',
    r'\end{table}',
]
(GEN / 'validation_table.tex').write_text('\n'.join(lines) + '\n')

print(f'Generated LaTeX components in {GEN}')

# Block 03 exact finite validation and named-example table
block03_path = GEN / 'block03_periodic_atlas_validation.json'
if block03_path.exists():
    b3 = json.loads(block03_path.read_text(encoding='utf-8'))
    enum = b3['enumeration']
    ranges = enum['prime_fields_and_max_period']
    range_text = ', '.join(f"$p={p}$ through period {t}" for p, t in sorted((int(k), int(v)) for k, v in ranges.items()))
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Exact finite validation of the Block 03 periodic heterogeneous atlas.}',
        r'\label{tab:block03-validation}',
        r'\small',
        r'\begin{tabularx}{\textwidth}{@{}L{0.28\textwidth}Y@{}}',
        r'\toprule',
        r'Check & Recorded result\\',
        r'\midrule',
        f"Enumerated normalized objects & {range_text}; {enum['primitive_unit_periodic_words']} primitive unit-periodic words.\\\\",
        f"Exact identities and automaton checks & {b3['checks']} checks; {len(b3['failures'])} failures.\\\\",
        f"Arithmetic model & {tex_escape(b3['arithmetic'])}.\\\\",
        f"Overall status & {'PASS' if b3['passed'] else 'FAIL'}.\\\\",
        r'Boundary & Finite enumeration validates the declared ranges and implementation formulas. It does not replace the symbolic proofs or establish unrestricted automatic-to-Mahler equivalence.\\',
        r'\bottomrule',
        r'\end{tabularx}',
        r'\end{table}',
    ]
    (GEN / 'block03_validation_table.tex').write_text('\n'.join(lines) + '\n')

    def coeff_poly(coeffs, var='z'):
        terms = []
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            if i == 0:
                term = str(c)
            elif i == 1:
                term = var if c == 1 else f"{c}{var}"
            else:
                term = f"{var}^{i}" if c == 1 else f"{c}{var}^{i}"
            terms.append(term)
        return '0' if not terms else '+'.join(terms)

    named_order = [
        ('even_indicator_F2', 'Even indicator'),
        ('alternating_unit_F3', 'Alternating unit'),
        ('period_three_F2', 'Period-three word'),
    ]
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Named exact examples in the heterogeneous periodic atlas.}',
        r'\label{tab:block03-examples}',
        r'\scriptsize',
        r'\begin{tabularx}{\textwidth}{@{}L{0.14\textwidth}L{0.09\textwidth}L{0.11\textwidth}L{0.15\textwidth}L{0.15\textwidth}L{0.09\textwidth}Y@{}}',
        r'\toprule',
        r'Example & Field / word & Minimal recurrence & Reduced OGF denominator & Reduced mask numerator & Kernel states & \shortstack[l]{Compiler\\bound}\\',
        r'\midrule',
    ]
    for key, label in named_order:
        row = b3['named_examples'][key]
        p = row['p']
        word = ''.join(str(v) for v in row['word'])
        m_high = row['minimal_recurrence_coefficients_high_to_low']
        # Convert high-to-low to a compact x-polynomial.
        m_low = list(reversed(m_high))
        m_txt = coeff_poly(m_low, 'x')
        q_txt = coeff_poly(row['reduced_ogf_denominator_coefficients_low_to_high'], 'z')
        r_txt = coeff_poly(row['mask_numerator_coefficients_low_to_high'], 'z')
        lines.append(
            f"{label} & $\\mathbb F_{p}$ / {word} & ${m_txt}$ & ${q_txt}$ & ${r_txt}$ & {row['p_kernel_states']} & {row['compiler_automaton_bound']}\\\\"
        )
    lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}']
    (GEN / 'block03_examples_table.tex').write_text('\n'.join(lines) + '\n')


# Block 04 exact finite validation and named-example table
block04_path = GEN / 'block04_rational_mask_atlas_validation.json'
if block04_path.exists():
    b4 = json.loads(block04_path.read_text(encoding='utf-8'))
    enum = b4['enumeration']
    ranges = enum['prime_fields_and_max_mask_degree']
    range_text = ', '.join(
        f"$p={p}$ with $\\deg A,\\deg B\\leq {d}$"
        for p, d in sorted((int(k), int(v)) for k, v in ranges.items())
    )
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Exact finite validation of the Block 04 rational-mask digital atlas.}',
        r'\label{tab:block04-validation}',
        r'\small',
        r'\begin{tabularx}{\textwidth}{@{}L{0.28\textwidth}Y@{}}',
        r'\toprule',
        r'Check & Recorded result\\',
        r'\midrule',
        f"Enumerated reduced unit masks & {range_text}; {enum['reduced_unit_masks']} masks in total.\\\\",
        f"Rational-collapse split & {enum['rational_collapse_masks']} collapse masks and {enum['noncollapse_masks']} genuinely nonrational mask series.\\\\",
        f"Exact identities and state checks & {b4['checks']} checks; {len(b4['failures'])} failures.\\\\",
        f"Arithmetic model & {tex_escape(b4['arithmetic'])}.\\\\",
        f"Overall status & {'PASS' if b4['passed'] else 'FAIL'}.\\\\",
        r'Boundary & Finite enumeration checks the compiler, reachable Cartier module, state hierarchy, examples, and collapse classification on the declared ranges. It does not replace the unbounded proofs or classify all automatic sequences.\\',
        r'\bottomrule',
        r'\end{tabularx}',
        r'\end{table}',
    ]
    (GEN / 'block04_validation_table.tex').write_text('\n'.join(lines) + '\n')

    named_order = [
        ('cantor_digit_indicator_F3', 'Cantor-digit indicator'),
        ('square_root_denominator_F3', 'Square-root denominator'),
        ('alternating_collapse_F3', 'Alternating collapse'),
        ('finite_transient_F2', 'Finite transient'),
    ]
    lines = [
        r'\begin{table}[htbp]',
        r'\centering',
        r'\caption{Named exact examples in the rational-mask digital atlas.}',
        r'\label{tab:block04-examples}',
        r'\scriptsize',
        r'\begin{tabularx}{\textwidth}{@{}L{0.18\textwidth}L{0.07\textwidth}L{0.17\textwidth}L{0.20\textwidth}L{0.09\textwidth}Y@{}}',
        r'\toprule',
        r'Example & Field & Reduced mask $A/B$ & First coefficients & $r_p/\kappa_p$ & \shortstack[l]{Collapse status /\\compiler bound}\\',
        r'\midrule',
    ]
    for key, label in named_order:
        row = b4['named_examples'][key]
        p = row['p']
        A = coeff_poly(row['A'], 'z')
        B = coeff_poly(row['B'], 'z')
        prefix = ''.join(str(x) for x in row['prefix'][:18])
        collapse = 'collapse' if row['collapse'] else 'non-collapse'
        lines.append(
            f"{label} & $\\mathbb F_{p}$ & $({A})/({B})$ & \\texttt{{\\seqsplit{{{prefix}}}}} & ${row['cartier_rank']}/{row['reachable_numerator_states']}$ & \\shortstack[l]{{{collapse}\\\\compiler\\\\bound ${row['ambient_state_bound']}$}}\\\\"
        )
    lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}']
    (GEN / 'block04_examples_table.tex').write_text('\n'.join(lines) + '\n')
