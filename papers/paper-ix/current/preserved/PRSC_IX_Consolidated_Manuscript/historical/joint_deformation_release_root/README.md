# Paper IX: simultaneous coefficient and parameter deformation

**Author: Komorebi P. — 8 September 2026.**

This cumulative release proves the combined deformation theorem in Lean.
For \(R=\mathbb Z_p\), an actual root \(a=(y_0,t_0)\) of an integral
p-adic polynomial system \(F(Y,T)\), and derivative blocks
\(J=D_YF(a)\), \(K=D_TF(a)\), assume
\[
J\in\operatorname{GL}_e(\mathbb Q_p),\qquad p^sJ^{-1}\in M_e(R),\qquad M>2s.
\]
For every \(v\in R^k\), prescribe \(\tau=t_0+p^Mv\) and change the
coefficients to \(G=F+p^MH\). There is exactly one
\(y\in y_0+p^{s+1}R^e\) with \(G(y,\tau)=0\), and
\[
y-y_0\in p^{M-s}R^e,\qquad
\boxed{y-y_0=-p^MJ^{-1}\bigl(H(a)+Kv\bigr)+\varepsilon},
\qquad\varepsilon\in p^{2M-3s}R^e.
\]
The proof constructs actual augmented polynomial equations and transfers the
original inverse bound with the same exponent. The new Jacobian is not an
assumption. The result includes all primes and arbitrary integral p-adic
coefficients and centers. The solved block is square and invertible over the
fraction field; no general rank-deficient assertion is made.

## Evidence

The block adds **28 mathematical theorems and 6 definitions in four modules**.
The fresh cumulative gate rebuilds **49 mathematical modules**, seven positive
control modules and twelve theorem-contract modules. It audits **460 project
declaration axiom closures** and requires eleven invalid claims to be rejected:
**82 checks in total**. All 45 inherited mathematical modules are unchanged.
The exact results, source hashes, commands and logs are recorded in
`polynomial_joint_motion/verification/polynomial_joint_motion_verification.json`.

The new dyadic controls check both coefficient and parameter changes, detect
an omitted or reversed parameter term at the required error precision, and
show that parameter-only motion can attain the error bound without an extra digit.
Development proof-script failures and their repairs remain documented. The
independent proof audit is separate from the Lean compilation evidence.

- Mathematical exposition: `polynomial_joint_motion/JOINT_DEFORMATION.md`.
- Main formal theorem: `Komorebi.PolynomialJointDeformation.exists_joint_deformation`.
- Independent raw-source audit and hash reconciliation: `polynomial_joint_motion/audit/`.
- Complete proved/open checklist: `REMAINING_CHECKLIST.md`.
- Reproduction: `replay_paper9_joint_motion.py --kit PATH --output EMPTY_DIRECTORY`.

Reproduction uses the separately supplied pinned Lean 4.34.0-rc2 and Mathlib
runtime recorded by the verifier. The compatibility adapter restores executable
path discovery. Allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`.

## Preserved prior work

Every file in the preceding **1,768-file parameter-tower archive** is retained
with identical content. Replaced root documents are moved to a historical
folder; `PACKAGE_COMPLETENESS.json` records every old-to-new mapping.
The preceding archive SHA-256 is
`b0fc8d10e92ca89c6cbf4a67ed877d90606fb41fdfc46e0367841eb97e8eb35b`.

This includes the prescribed parameter towers, finite obstructions and exact
fibers, weighted nonlinear lifting and coefficient-only first-order motion,
continuous parameter charts, dyadic sharpenings and edge towers, and original
Nishibuchi completion. Earlier non-polynomial proofs retain their historical
verification; this gate recompiles the polynomial development. Historical
recovery limitations remain recorded.

## Remaining work

The next candidate block is Fréchet differentiability of the local parameter
solution map, with derivative \(-J^{-1}K\). The quadratic response estimate is
now checked, but the solution-map and differential interfaces remain to be
formalized. Analyticity, general singular persistence, native presentation
invariance and global/completed descent, sharper arithmetic, and manuscript
consolidation remain unfinished.

The original stated Nishibuchi conjecture retains its completed scope. This
release does not claim completion of the entire strengthening or native program.
