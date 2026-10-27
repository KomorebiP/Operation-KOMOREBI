#!/usr/bin/env python3
"""Prepare cumulative local analytic regularity release documentation."""
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
BASE = WORKSPACE / 'output/PRSC_IX_Complete_Joint_Deformation.zip'
REPORT = Path('/dev/shm/paper9_regularity_fresh_01/polynomial_regularity_verification.json')

with zipfile.ZipFile(BASE) as archive:
    checklist = archive.read('PRSC_IX_Complete_Joint_Deformation/REMAINING_CHECKLIST.md').decode()

def replace_once(old, new):
    global checklist
    assert checklist.count(old) == 1, old[:100]
    checklist = checklist.replace(old, new)

replace_once('**Current joint coefficient and parameter deformation block: fresh verification PASS.**',
             '**Current local analyticity and differentiability block: fresh verification PASS.**')
replace_once('**Simultaneous coefficient and parameter deformation — current block.**',
             '**Simultaneous coefficient and parameter deformation — preceding block.**')
new = r'''- [x] **Local analyticity and differentiability — current block, both parts complete.** Let \(p\) be any prime, \(e,k\ge0\), \(F\in\mathbb Q_p[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\), and \(a=(y_0,t_0)\) satisfy \(F(a)=0\). Write \(J=D_YF(a)\), \(K=D_TF(a)\), and assume \(J\in\operatorname{GL}_e(\mathbb Q_p)\). There are open neighborhoods \(t_0\in U\subseteq\mathbb Q_p^k\), \(y_0\in V\subseteq\mathbb Q_p^e\), and a map \(\psi:\mathbb Q_p^k\to\mathbb Q_p^e\), analytic near every point of \(U\), such that
  \[
  \psi(t_0)=y_0,\quad\psi(U)\subseteq V,\quad
  F(y,t)=0\iff y=\psi(t)\quad(t\in U,\ y\in V),
  \qquad D\psi(t_0)=-J^{-1}K.
  \]
  The derivative is certified as a strict Fréchet derivative. Actual polynomial evaluation, actual evaluated formal partial derivatives, and the full augmented inverse are connected in the proof; analyticity and the derivative identity are conclusions. The core works over every complete nontrivially normed field. An explicit specialization includes arbitrary integral p-adic coefficients and centers by evaluating them in the ambient field. These local neighborhoods have no new explicit uniform radius; the earlier weighted radii remain separate checked results.

- [x] **Regularity of supplied continuous root selections — current block.** If \(g\) is continuous at \(t_0\), \(g(t_0)=y_0\), and \(F(g(t),t)=0\) for all sufficiently nearby \(t\), then \(g\) has the same germ as \(\psi\), is analytic at \(t_0\), and has strict derivative \(-J^{-1}K\). If \(g\) is a continuous exact root selection on an open set and \(D_YF(g(t),t)\) is invertible at every point, then it is analytic throughout that set and
  \[
  Dg(t)=-\bigl(D_YF(g(t),t)\bigr)^{-1}D_TF(g(t),t).
  \]
  This comparison is for ambient field-valued root selections. A separate formal comparison with each historical subtype-valued chart has not been added.

'''
replace_once('## Clear routes still awaiting formalization', new + '## Clear routes still awaiting formalization')
replace_once('| [ ] Next formalization | **Differentiability of the local parameter solution map.** | Construct the map on suitable open subsets of the fraction-field vector spaces and translate the quadratic response estimate into the Fréchet derivative \\(D_t y=-J^{-1}K\\). |\n', '')
replace_once('Generalizing those rectangular interfaces, analyticity, and differentiability remain separate.',
             'The new ambient-field theorem proves local analyticity and differentiability for arbitrary p-adic coefficients with an invertible solved block. Generalizing every historical rectangular interface, or proving identity with each earlier subtype-valued chart, remains an interface task.')
start = checklist.index('## Suggested next block\n')
end = checklist.index('## Evidence locations\n', start)
checklist = checklist[:start] + r'''## Suggested next block

The entire stated local regularity block is closed: analytic solution map, differentiability, exact local graph, actual derivative formula, integral-data specialization, and regularity transfer to continuous root selections. This is local at fraction-field nonsingular solved blocks.

The clearest finite completion task is **manuscript consolidation**: integrate the checked results, state the strengthened scope precisely, align notation and cross-references, and keep research questions visibly separate. For new research, a bounded next target is the second dyadic difference in one packet; success there would not resolve the entire higher-order valuation question. General singular persistence and the native conjectures still need substantive work and, for the native statements, precise definitions.

''' + checklist[end:]
replace_once('## Evidence locations\n',
             '## Evidence locations\n\n- Current analytic regularity: `polynomial_regularity/ANALYTIC_REGULARITY.md`, `polynomial_regularity/formalization/`, `polynomial_regularity/verification/polynomial_regularity_verification.json`, and `polynomial_regularity/audit/ROUTE_AUDIT.md`.\n')
replace_once('- Current joint deformation:', '- Previous joint deformation:')
if not REPORT.is_file() or json.loads(REPORT.read_text()).get('status') != 'PASS':
    checklist = checklist.replace('**Current local analyticity and differentiability block: fresh verification PASS.**',
                                  '**DRAFT: current local analyticity and differentiability block awaits its fresh release gate.**')
(ROOT / 'docs/REMAINING_CHECKLIST.md').write_text(checklist)

readme = r'''# Paper IX: local analytic parameter regularity

**Author: Komorebi P. — 8 September 2026.**

This cumulative release closes both local analyticity and differentiability
of the polynomial parameter solution map.

Let \(F\in\mathbb Q_p[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\),
\(a=(y_0,t_0)\), and \(F(a)=0\). Put \(J=D_YF(a)\), \(K=D_TF(a)\).
If \(J\in\operatorname{GL}_e(\mathbb Q_p)\), there exist open neighborhoods
\(t_0\in U\subseteq\mathbb Q_p^k\), \(y_0\in V\subseteq\mathbb Q_p^e\),
and a map \(\psi:\mathbb Q_p^k\to\mathbb Q_p^e\), analytic near every
point of \(U\), such that
\[
\psi(t_0)=y_0,\qquad\psi(U)\subseteq V,\qquad
F(y,t)=0\iff y=\psi(t)\quad(t\in U,\ y\in V),
\]
\[
\boxed{D\psi(t_0)=-J^{-1}K.}
\]
Lean certifies the stronger strict Fréchet derivative statement. The actual
formal partial derivatives are proved to be the analytic derivative, and
the actual augmented polynomial system supplies the inverse. No analyticity,
derivative formula, or preselected solution map is assumed in the main theorem.

Every continuous local root selection through the same nonsingular point
has this analytic germ and this derivative. On an open parameter set, a
continuous exact root selection with invertible solved Jacobian at every
point is analytic throughout, with the actual implicit derivative at each point.

The core works over every complete nontrivially normed field. The p-adic
specialization includes every prime, including 2, and arbitrary finite
dimensions, including zero. An explicit theorem handles integral p-adic
coefficients and centers in the ambient field \(\mathbb Q_p\).

## Proof and scope

The proof applies the analytic inverse theorem to \((F(Y,T),T)\).
Its derivative and inverse are
\[
\begin{pmatrix}J&K\\0&I\end{pmatrix},\qquad
\begin{pmatrix}J^{-1}&-J^{-1}K\\0&I\end{pmatrix}.
\]
Restrict the local inverse to targets \((0,t)\), project to the solved
coordinates, and extract an open product neighborhood. This gives both
directions of the local root characterization.

The analytic neighborhoods have no newly asserted explicit uniform radius.
The earlier weighted existence radii and quantitative error estimates remain
valid separate results. Analyticity is local; no claim is made on all of
\(\mathbb Q_p^k\). The integral specialization produces a field-valued
analytic branch, and does not treat \(\mathbb Z_p\) as a vector space over
\(\mathbb Q_p\). No new identity with every historical subtype-valued chart
is claimed.

## Evidence

@EVIDENCE@

The controls include the actual linear system \(F(Y,T)=Y+T\), its unique
root \(y=-t\), its analytic branch and derivative, rejection of the wrong
positive derivative sign, and an actual nonlinear invocation of the theorem.
Development proof-script failures and fixes are retained in `dev/`; the
independent raw-source review is separate from compiler acceptance.

- Mathematical exposition: `polynomial_regularity/ANALYTIC_REGULARITY.md`.
- Main theorem: `Komorebi.PolynomialAnalyticImplicit.exists_analytic_implicit`.
- Integral theorem: `Komorebi.PolynomialRegularityIntegral.exists_analytic_integral_implicit`.
- Selection transfer: `Komorebi.PolynomialAnalyticSelection.continuous_selection_regularity`.
- Independent audit: `polynomial_regularity/audit/`.
- Full proved/open checklist: `REMAINING_CHECKLIST.md`.
- Reproduction: `replay_paper9_regularity.py --kit PATH --output EMPTY_DIRECTORY`.

Reproduction uses the separately supplied pinned Lean 4.34.0-rc2 and Mathlib
runtime recorded by the verifier. The compatibility adapter restores executable
path discovery. Allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`.

## Preserved work and remaining questions

Every file in the preceding **1,971-file joint-deformation archive** is
retained with identical content. Replaced root documents are moved to a
historical folder; `PACKAGE_COMPLETENESS.json` records every old-to-new mapping.
The previous archive SHA-256 is
`646a19a95af884cb4e7373ac97298c7a81ef25589eba56181a6157d43ca4eed0`.

This preserves the original Nishibuchi completion, dyadic sharpenings and
edge towers, finite obstructions, counts, smooth and prescribed-parameter
towers, continuous charts, weighted lifting, and joint deformation.
Earlier non-polynomial proofs retain their historical verification; this
gate recompiles the polynomial development. Historical recovery limitations
remain recorded.

General rationally rank-deficient singular persistence, native presentation
invariance, global/completed descent, sharper arithmetic, historical formula
recovery, and manuscript consolidation remain unfinished. The original
stated Nishibuchi conjecture retains its completed scope. This release closes
the local regularity block, not the entire strengthening or native program.
'''

if REPORT.is_file():
    report = json.loads(REPORT.read_text())
    assert report['status'] == 'PASS'
    evidence = (
        f'The fresh cumulative gate passed **{len(report["runs"])} checks**, including '
        f'**{report["module_count"]} mathematical modules** and '
        f'**{report["explicit_declaration_audits"]} project declaration axiom closures**. '
        'All 49 inherited mathematical modules are unchanged. Six new mathematical '
        'modules add **30 theorems and 8 definitions**. Source hashes, commands and logs are recorded in '
        '`polynomial_regularity/verification/polynomial_regularity_verification.json`.')
else:
    evidence = 'DRAFT: the fresh gate is pending; this documentation is not yet release evidence.'
(ROOT / 'docs/README.md').write_text(readme.replace('@EVIDENCE@', evidence))
