#!/usr/bin/env python3
"""Prepare cumulative joint-deformation release documentation."""
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]/'output/PRSC_IX_Complete_Parameter_Towers.zip'
with zipfile.ZipFile(BASE) as archive:
    checklist=archive.read('PRSC_IX_Complete_Parameter_Towers/REMAINING_CHECKLIST.md').decode()

def replace_once(old,new):
    global checklist
    assert checklist.count(old)==1,old[:100]
    checklist=checklist.replace(old,new)

replace_once('**Current prescribed-parameter tower block: fresh verification PASS.**',
             '**Current joint coefficient and parameter deformation block: fresh verification PASS.**')
replace_once('**Compatible towers with prescribed parameter paths — current block.**',
             '**Compatible towers with prescribed parameter paths — preceding block.**')
replace_once('**Arbitrary prescribed p-adic endpoints and exact branching — current block.**',
             '**Arbitrary prescribed p-adic endpoints and exact branching — preceding block.**')
new=r'''- [x] **Simultaneous coefficient and parameter deformation — current block.** Let \(R=\mathbb Z_p\), \(F,H\in R[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\), \(a=(y_0,t_0)\), and \(F(a)=0\). Put \(J=D_YF(a)\), \(K=D_TF(a)\). If
  \[
  J\in\operatorname{GL}_e(\mathbb Q_p),\qquad p^sJ^{-1}\in M_e(R),\qquad M>2s,
  \]
  then for every \(v\in R^k\), setting \(\tau=t_0+p^Mv\) and \(G=F+p^MH\), there is exactly one \(y\in y_0+p^{s+1}R^e\) with \(G(y,\tau)=0\). It satisfies
  \[
  y-y_0\in p^{M-s}R^e,\qquad
  y-y_0=-p^MJ^{-1}\bigl(H(a)+Kv\bigr)+\varepsilon,
  \qquad\varepsilon\in p^{2M-3s}R^e.
  \]
  The proof constructs the actual augmented polynomial system, proves its two-sided inverse certificate with the same exponent \(s\), and imposes no hypothesis on the perturbed Jacobian. It covers all primes, arbitrary integral p-adic coefficients and centers, and zero finite dimensions. Actual dyadic controls detect an omitted or reversed parameter term. A parameter-only quadratic example attains error depth exactly \(2M-3s\), ruling out a uniform extra digit.

'''
replace_once('## Clear routes still awaiting formalization',new+'## Clear routes still awaiting formalization')
replace_once('| [ ] Next formalization | **Joint coefficient and parameter deformation.** | Apply weighted root motion to the actual augmented polynomial system. Prove its inverse bound and derive a first-order solved-coordinate displacement with a controlled remainder. |',
'| [ ] Next formalization | **Differentiability of the local parameter solution map.** | Construct the map on suitable open subsets of the fraction-field vector spaces and translate the quadratic response estimate into the Fréchet derivative \\(D_t y=-J^{-1}K\\). |')
replace_once('The first-order root-motion estimate is now checked for square systems.',
             'First-order root motion and simultaneous coefficient/parameter response are now checked for square solved systems with arbitrary integral p-adic coefficients and centers.')
start=checklist.index('## Suggested next block\n'); end=checklist.index('## Evidence locations\n',start)
checklist=checklist[:start]+r'''## Suggested next block

Formalize **Fréchet differentiability of the local parameter solution map**. The checked joint response theorem, specialized to parameter-only motion, supplies the candidate derivative \(-J^{-1}K\) and a quadratic error bound. A complete proof must construct the solution-map interface on suitable open subsets of \(\mathbb Q_p^k\) and verify the conversion to the differential definition. The derivative statement remains unformalized in this release. Analyticity remains a separate obligation.

The prescribed smooth towers and simultaneous coefficient/parameter deformation blocks are closed. General singular persistence, native presentation invariance and native descent remain research obligations. Manuscript consolidation and final cross-references also remain to be completed.

'''+checklist[end:]
replace_once('## Evidence locations\n','## Evidence locations\n\n- Current joint deformation: `polynomial_joint_motion/JOINT_DEFORMATION.md`, `polynomial_joint_motion/formalization/`, `polynomial_joint_motion/verification/polynomial_joint_motion_verification.json`, and `polynomial_joint_motion/audit/ROUTE_AUDIT.md`.\n')
replace_once('- Current prescribed-parameter towers:','- Previous prescribed-parameter towers:')
(ROOT/'docs/REMAINING_CHECKLIST.md').write_text(checklist)

readme=r'''# Paper IX: simultaneous coefficient and parameter deformation

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
'''
(ROOT/'docs/README.md').write_text(readme)
