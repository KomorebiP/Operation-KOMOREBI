# Paper IX: compatible polynomial towers with prescribed parameters

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
