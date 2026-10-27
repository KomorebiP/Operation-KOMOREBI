#!/usr/bin/env python3
"""Prepare cumulative prescribed-parameter tower release documentation."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1] / 'output/PRSC_IX_Complete_Prescribed_Parameters.zip'
with zipfile.ZipFile(BASE) as archive:
    checklist = archive.read('PRSC_IX_Complete_Prescribed_Parameters/REMAINING_CHECKLIST.md').decode()

def replace_once(old, new):
    global checklist
    assert checklist.count(old) == 1, old[:100]
    checklist = checklist.replace(old, new)

replace_once('**Current prescribed-parameter block: fresh verification PASS.**',
             '**Current prescribed-parameter tower block: fresh verification PASS.**')
replace_once('**Prescribed-parameter polynomial obstruction and exact fibers — current block.**',
             '**Prescribed-parameter polynomial obstruction and exact fibers — preceding block.**')
new = r'''- [x] **Compatible towers with prescribed parameter paths — current block.** Let \(q>0\), \(L\ge1\), \(F\in\mathbb Z[Y_1,\ldots,Y_m,T_1,\ldots,T_k]^e\), and \(F(x)\equiv0\pmod{q^L}\). Suppose the actual solved block \(J_x=D_YF(x)\bmod q\) is surjective. For every integer path with
  \[
  t(0)=\operatorname{free}(x),\qquad t(n+1)-t(n)\in q^{L+n}\mathbb Z^k,
  \]
  Lean constructs a single integer tower satisfying
  \[
  z(0)=x,\quad\operatorname{free}(z(n))=t(n),\quad
  F(z(n))\in q^{L+n}\mathbb Z^e,\quad
  z(n+1)-z(n)\in q^{L+n}\mathbb Z^{m+k}.
  \]
  The parameter equality is exact in integers. The full actual reduced Jacobian stays fixed, and every earlier residue is retained. Only initial solved-block surjectivity is assumed. Integer towers include positive composite bases and \(q=1\).

- [x] **Arbitrary prescribed p-adic endpoints and exact branching — current block.** For prime \(p\) and every \(\tau\in\operatorname{free}(x)+p^L\mathbb Z_p^k\), Lean constructs the integer parameter path, polynomial tower, and endpoint \(b\), with
  \[
  z(n)\to b,\quad F(b)=0,\quad\operatorname{free}(b)=\tau,\quad
  b-z(n)\in p^{L+n}\mathbb Z_p^{m+k}\quad(n\ge0).
  \]
  At every stage and for every prescribed next parameter digit \(v\), there are exactly \(p^{m-e}\) actual next-level residue lifts. Surjectivity proves \(e\le m\). If \(m=e\), every parameter has exactly one root in the initial ball, independent of all path and tower choices. The checked \(F(Y_1,Y_2,T)=Y_1\) example rules out extending this uniqueness to rectangular solved blocks. All prime statements include \(p=2\).

'''
replace_once('## Clear routes still awaiting formalization', new + '## Clear routes still awaiting formalization')
old = '| [ ] Next formalization | **Compatible towers with prescribed parameters.** | State sufficient hypotheses ensuring that each successive prescribed digit is admissible, construct compatible actual lifts, and pass to the p-adic limit. The one-step obstruction, fiber, and count are now checked. |'
replace_once(old, '| [ ] Next formalization | **Joint coefficient and parameter deformation.** | Apply weighted root motion to the actual augmented polynomial system. Prove its inverse bound and derive a first-order solved-coordinate displacement with a controlled remainder. |')
start = checklist.index('## Suggested next block\n')
end = checklist.index('## Evidence locations\n', start)
checklist = checklist[:start] + r'''## Suggested next block

Formalize simultaneous **coefficient and parameter deformation** in the square solved case. The existing weighted root-motion theorem can be applied to an augmented polynomial system once its actual inverse certificate is proved. This should yield a controlled first-order formula for the solved-coordinate response. It remains a proposed route in this release.

The prescribed smooth-tower block is now closed. General singular persistence, analytic regularity, native presentation invariance and native descent remain separate research obligations. Manuscript consolidation and final cross-references also remain to be completed.

''' + checklist[end:]
replace_once('## Evidence locations\n', '## Evidence locations\n\n- Current prescribed-parameter towers: `polynomial_parameter_towers/PRESCRIBED_PARAMETER_TOWERS.md`, `polynomial_parameter_towers/formalization/`, `polynomial_parameter_towers/verification/polynomial_parameter_towers_verification.json`, and `polynomial_parameter_towers/audit/ROUTE_AUDIT.md`.\n')
replace_once('- Current prescribed-parameter block:', '- Previous prescribed-parameter block:')
(ROOT/'docs/REMAINING_CHECKLIST.md').write_text(checklist)

readme = r'''# Paper IX: compatible polynomial towers with prescribed parameters

**Author: Komorebi P. — 8 September 2026.**

This cumulative release completes the prescribed smooth-tower block in Lean.
For an integer polynomial system with \(e\) equations, \(m\) solved coordinates,
\(k\) parameter coordinates, an initial root modulo \(q^L\), \(q>0\), \(L\ge1\),
and surjective actual solved Jacobian modulo \(q\), every compatible integer
parameter path lifts to a compatible polynomial solution tower. Its parameter
coordinates are kept exactly at every integer level.

For prime \(p\), every \(\tau\in\operatorname{free}(x)+p^L\mathbb Z_p^k\)
has a constructed integer path, solution tower \(z_n\), and endpoint \(b\) with
\[
z_0=x,\qquad F(z_n)\equiv0\pmod{p^{L+n}},\qquad z_n\to b,
\]
\[
F(b)=0,\qquad\operatorname{free}(b)=\tau,\qquad
b-z_n\in p^{L+n}\mathbb Z_p^{m+k}.
\]
The actual reduced Jacobian stays fixed. Every stage has exactly
\(p^{m-e}\) next-level residue lifts for every prescribed parameter digit.
When \(m=e\), the exact root with those parameters is unique in the initial
ball; the endpoint is independent of all path and tower choices. A checked
rectangular counterexample records the uniqueness boundary.

## Evidence

The block adds **24 mathematical theorems and one definition in six modules**.
The fresh cumulative gate rebuilds **45 mathematical modules**, six positive
control modules and eleven theorem-contract modules, then audits every
project declaration's axiom closure and requires nine negative controls to
be rejected: **74 checks in total**. All 39 inherited mathematical modules
are preserved byte for byte. Exact results and hashes are in
`polynomial_parameter_towers/verification/polynomial_parameter_towers_verification.json`.

- Mathematical exposition: `polynomial_parameter_towers/PRESCRIBED_PARAMETER_TOWERS.md`.
- Main formal theorem: `Komorebi.PolynomialPrescribedPadicTower.exists_prescribed_padic_root_with_tower`.
- Independent raw-source review and fresh-gate reconciliation: `polynomial_parameter_towers/audit/`.
- Detailed proved/open checklist: `REMAINING_CHECKLIST.md`.
- Reproduction: `replay_paper9_parameter_towers.py --kit PATH --output EMPTY_DIRECTORY`.

Reproduction uses the separately supplied pinned Lean 4.34.0-rc2 and Mathlib
runtime recorded by the verifier. The compatibility adapter only restores
executable-path discovery. Allowed axioms are `propext`, `Classical.choice`,
and `Quot.sound`; no placeholder proofs or custom axioms are admitted.

## Preserved prior work

Every file in the preceding 1,589-file prescribed-parameter archive is retained
with identical content, with replaced root documents moved to a historical
folder. `PACKAGE_COMPLETENESS.json` gives the exact old-to-new mapping. The
previous archive SHA-256 is
`c1d3ebbfbe08e66698fb485a453a1c039a56ba8b19dd6d771838875fad2ea854`.

This includes weighted nonlinear lifting and first-order root motion,
continuous parameter charts, finite prescribed obstructions and exact lift
fibers, dyadic sharpenings and edge towers, and the original Nishibuchi
completion. Earlier non-polynomial proofs retain their historical verification;
they are not recompiled in the present polynomial gate. Historical recovery
limitations remain recorded.

## Remaining work

The next proposed block is joint coefficient and parameter deformation with a
controlled first-order solved-coordinate formula. General singular persistence,
analytic regularity, native presentation invariance and global/completed descent,
further exact valuations and periods, and manuscript consolidation remain open.

The original stated Nishibuchi conjecture retains its completed scope. The
broader strengthening and native program are not claimed complete.
'''
(ROOT/'docs/README.md').write_text(readme)
