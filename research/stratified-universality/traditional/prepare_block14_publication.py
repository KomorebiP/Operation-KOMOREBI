from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEN = ROOT / 'generated'
GEN.mkdir(exist_ok=True)

theorem_rows = [
    ('Resolved source', 'Additive-Karoubi envelope', 'Literal finite packet objects and profile-indexed realization source', r'\cref{thm:additive-karoubi-envelope}'),
    ('Typed atlas', 'Bridge passports and obstruction separation', 'Reversible overlaps are separated from directional loss', r'\cref{sec:strata-bridges-obstructions}'),
    ('Finite assembly', 'Profiled atlas assembly', 'Bilimit, theorem transport, groupoid core, and global directional functors', r'\cref{thm:atlas-assembly}'),
    ('Native normalization', 'Certified stratum atlases', 'Complete local coordinates on declared semantic slices', r'Part II'),
    ('Higher coherence', 'Normalizer-induced coherence', 'Unique semantic normalizers force all certified overlap cycles to commute', r'\cref{thm:block13-normalizer-coherence}'),
    ('Invariant descent', 'Certified invariant-descent theorem', 'Coherent local invariants descend through effective object and morphism gluing', r'\cref{thm:block13-certified-invariant-descent}'),
    ('Global completeness', 'Tagged componentwise invariant', 'The descended invariant reflects isomorphism on the five-component union', r'\cref{thm:block13-global-completeness,thm:block14-main}'),
    ('Lane transport', 'Finite profiled Universal Lane Transport Theorem', 'Exact block transport, refinement, selection, residuals, conditional fold loss, and certified descent', r'\cref{thm:block15-universal-lane-transport,thm:block15-lane-descent}'),
    ('Twisted transport', 'Holonomy-Twisted Universal Lane Transport Theorem', 'Matrix-local-system synthesis, base-fiber invariant normal form, orbit coarsening, and orbital path algebra', r'\cref{thm:block16-holonomy-twisted-lane-transport,cor:block16-base-fiber-invariant-normal-form,thm:block16-orbit-descent,thm:block16-permutation-orbital-calculus}'),
]
lines = [
    r'\begin{table}[htbp]',
    r'\centering',
    r'\small',
    r'\caption{The publication theorem spine.  Section numbers are resolved by the final build; the logical order, rather than the numbering, is authoritative.}',
    r'\label{tab:block14-theorem-suite}',
    r'\begin{tabularx}{\textwidth}{@{}L{0.16\textwidth}L{0.22\textwidth}YL{0.14\textwidth}@{}}',
    r'\toprule',
    r'Stage & Principal result & Exact role in the proof & Location \\',
    r'\midrule',
]
for row in theorem_rows:
    lines.append(' & '.join(row) + r' \\')
lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}', '']
(GEN / 'block14_theorem_suite_table.tex').write_text('\n'.join(lines), encoding='utf-8')

scope_rows = [
    ('Digital--regular--linear--Mahler', 'Fixed-prime regular sequences with rational-mask and periodic subloci', 'Strict shortlex state, Cartier/mask data where defined, periodic linear data where defined', 'No all-radix or unrestricted functional/Newton-Mahler equivalence'),
    ('Continuous local', r'$C(\mathbb Z_p,\mathbb Z_p)$', 'Canonical Mahler coefficients and complete clopen branch packets', 'No universal local-analytic normal form or optimal mixed-radix tree'),
    ('Marked Fuss', r'$U=z+\alpha U^q$', r'Marked parameters $(q,\alpha)$, algebraic branch, recurrence, tree support and orbit data', 'Complete only on the marked nonlinear--algebraic--holonomic family'),
    ('Euler--multiplicative', 'Fixed Euler basis and prime-uniform multiplicative locus', 'Euler exponent, divisor ghost, common local factor, multiplicative function', 'No arbitrary product-grammar or additive--multiplicative equivalence'),
    ('Finite Galois', 'One finite semisimple Galois extension', 'Subgroup, fixed field, Reynolds projector, quotient and Mackey data', 'No modular/wild or nonneutral tensor reconstruction'),
]
lines = [
    r'\begin{landscape}',
    r'\begin{table}[htbp]',
    r'\centering',
    r'\scriptsize',
    r'\caption{Certified classification components and exact boundaries.}',
    r'\label{tab:block14-scope}',
    r'\begin{tabularx}{\linewidth}{@{}L{0.15\linewidth}L{0.23\linewidth}L{0.30\linewidth}Y@{}}',
    r'\toprule',
    r'Component & Semantic domain & Complete descended coordinates & Boundary \\',
    r'\midrule',
]
for row in scope_rows:
    lines.append(' & '.join(row) + r' \\')
lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}', r'\end{landscape}', '']
(GEN / 'block14_scope_table.tex').write_text('\n'.join(lines), encoding='utf-8')

stages = [
    ('Foundation', 'Typed resolved syntax, packet coordinates, preservation profiles, additive-Karoubi envelope'),
    ('Atlas typing', 'Normalized strata, representation groupoids, bridge passports, information loss, obstruction types'),
    ('Finite effectivity', 'Periodic and rational-mask heterogeneous atlases'),
    ('Digital normalization', 'Fixed-radix regular, automatic finite-orbit, and integral prime-power layers'),
    ('Product/local normalization', 'Euler--multiplicative and Newton-Mahler--polyphase atlases'),
    ('Holonomic, algebraic, nonlinear', 'Marked model-family minimality, collision, and tree signatures'),
    ('Symmetry', 'Finite Galois, Brauer, profinite, and neutral Tannakian slices'),
    ('Global synthesis', 'Authoritative bridge matrix, higher coherence, invariant descent, tagged completeness'),
    ('Lane transport', 'Complete finite-resolution analysis, synthesis, block transport, refinement, selection, residual accounting, and typed specializations'),
    ('Holonomy transport', 'Matrix local systems, exact twisted synthesis, base-fiber invariants, monodromy-orbit coarsening, and orbital composition'),
    ('Publication consolidation', 'Theorem spine, proof-order reorganization, scope compression, and source audit'),
]
lines = [
    r'\begin{longtable}{@{}L{0.27\textwidth}L{0.65\textwidth}@{}}',
    r'\caption{Development provenance retained after journal-facing reorganization.}\label{tab:block14-development-ledger}\\',
    r'\toprule',
    r'Stage & Mathematical contribution \\',
    r'\midrule',
    r'\endfirsthead',
    r'\toprule',
    r'Stage & Mathematical contribution \\',
    r'\midrule',
    r'\endhead',
]
for row in stages:
    lines.append(' & '.join(row) + r' \\')
lines += [r'\bottomrule', r'\end{longtable}', '']
(GEN / 'block14_development_ledger.tex').write_text('\n'.join(lines), encoding='utf-8')
print('Prepared consolidated publication tables through Block 16.')

# Journal-facing terminology normalization for generated tables.  Labels and file names
# retain their stable historical identifiers, while captions and cell text use thematic names.
range_replacements = {
    'Blocks 03--13': 'the certified atlas program',
    'Block 03--13': 'the certified atlas program',
    'Blocks 03--12': 'the certified native-stratum program',
    'Block 03--12': 'the certified native-stratum program',
    'Blocks 03--11': 'the preceding certified atlas program',
    'Block 03--11': 'the preceding certified atlas program',
    'Blocks 03--10': 'the preceding certified atlas program',
    'Block 03--10': 'the preceding certified atlas program',
    'Blocks 03--09': 'the preceding certified atlas program',
    'Block 03--09': 'the preceding certified atlas program',
}
name_replacements = {
    'Block 03': 'Periodic atlas',
    'Block 04': 'Rational-mask atlas',
    'Block 05': 'Fixed-radix regular atlas',
    'Block 06': 'Integral prime-power atlas',
    'Block 07': 'Product-multiplicative atlas',
    'Block 08': 'Local Mahler-polyphase atlas',
    'Block 09': 'Holonomic atlas',
    'Block 10': 'Algebraic atlas',
    'Block 11': 'Nonlinear tree atlas',
    'Block 12': 'Galois-Tannakian atlas',
    'Block 13': 'Global synthesis atlas',
    'Block 15': 'Finite lane-transport theorem',
    'Block 16': 'Holonomy-twisted lane theorem',
    'Work Package 0': 'the concordance stage',
    'Work Package 6': 'the global invariant milestone',
}
for tex_path in GEN.glob('*.tex'):
    content = tex_path.read_text(encoding='utf-8')
    for old, new in range_replacements.items():
        content = content.replace(old, new)
    for old, new in name_replacements.items():
        content = content.replace(old, new)
    content = content.replace('present block', 'present section')
    content = content.replace('preceding blocks', 'preceding sections')
    tex_path.write_text(content, encoding='utf-8')
print('Normalized generated table terminology for publication.')

# Small grammatical repairs after thematic replacement.
grammar_repairs = {
    'after Global synthesis atlas': 'for the certified global synthesis atlas',
    'proved in Global synthesis atlas': 'proved in the global synthesis section',
    'Global synthesis atlas total': 'Global synthesis suite total',
    'Global synthesis atlas exact checks': 'Global synthesis exact checks',
    'the certified Global synthesis atlas atlas': 'the certified global synthesis atlas',
    'the Global synthesis atlas matrix': 'the global synthesis matrix',
}
for tex_path in GEN.glob('*.tex'):
    content = tex_path.read_text(encoding='utf-8')
    for old, new in grammar_repairs.items():
        content = content.replace(old, new)
    tex_path.write_text(content, encoding='utf-8')
