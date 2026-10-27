# Paper IX: unique p-adic roots and coefficient perturbations

**Komorebi P. — 8 September 2026.**

This cumulative release adds Lean proofs of uniqueness for square polynomial systems and stability of their roots under coefficient perturbations. It also proves nearby-root existence for rectangular smooth systems. The stated Nishibuchi Conjecture 3.9 and all earlier checked Paper IX results remain preserved.

## Main theorem

Let \(p\) be prime, \(M\ge L\ge1\), and
\[
F,H\in\mathbb Z[X_1,\ldots,X_d]^d,
\qquad x\in\mathbb Z^d,
\qquad F(x)\equiv0\pmod{p^L}.
\]
Suppose the actual reduced Jacobian
\[
DF(x)\bmod p:\mathbb F_p^d\longrightarrow\mathbb F_p^d
\]
is surjective. Then \(F\) has exactly one root \(a\) in \(x+p^L\mathbb Z_p^d\). For every integer \(c\) divisible by \(p^M\), the polynomial system
\[
G=F+cH
\]
also has exactly one root \(b\) in that ball, and
\[
\boxed{b\equiv a\pmod{p^M}.}
\]
The theorem includes \(G=F+p^MH\), \(p=2\), and \(M=L\). The congruence is a lower bound on precision; the roots may coincide or agree to higher precision.

For rectangular systems \(F,H\in\mathbb Z[X_1,\ldots,X_d]^e\), a surjective reduced Jacobian gives a corresponding nearby existence theorem: every exact root \(a\equiv x\pmod p\) has an exact root \(b\) of \(F+cH\) with \(b-a\in p^M\mathbb Z_p^d\), whenever \(M\ge1\) and \(p^M\mid c\).

## What the new proofs establish

1. Canonical integer representatives of arbitrary p-adic roots are actual polynomial roots at every finite precision.
2. In the square case, the checked one-child count forces any two roots in the same smooth residue ball to agree at every precision, hence to be equal.
3. The actual perturbation \(F+cH\) preserves the lower root and the reduced Jacobian at the required depths. These identities are derived from its coefficients and partial derivatives.
4. Truncating an original root at depth \(M\) supplies a lower root from which to lift the perturbed system. This proves the full displacement bound.
5. Square uniqueness identifies the constructed nearby root with every perturbed root in the original ball.

The three new mathematical modules contain **24 declarations: 21 theorems and 3 definitions**. Inherited declarations, statement contracts, and control lemmas have separate counts in the verification report.

## Evidence and reproduction

The fresh gate passed **26 checks in 93.457 seconds**: 17 mathematical modules, one positive-control module, three contract files containing seven theorem contracts, three rejected invalid extensions, and **159 explicit declaration audits**. The latter comprise 126 theorems, 29 definitions and four abbreviations, including inherited support and contracts.

The authoritative new report is `polynomial_deformation/verification/polynomial_deformation_verification.json`. The replay compiles all required active project modules from source into a fresh directory, treats warnings as errors, checks expanded statement contracts, and audits every inventoried declaration's axiom dependencies. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed.

The pinned runtime is Lean `4.34.0-rc2` with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The separately supplied portable kit is required. Project compiled outputs are rebuilt; the pinned Mathlib cache is reused.

Run the new block:

```sh
python3 replay_paper9_deformation.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run
```

To replay all preserved active blocks first, add `--all`. The current observed run covers the new block and its dependencies. Earlier blocks retain their recorded evidence; they were not all rerun during this block.

## Contents

| Location | Purpose |
|---|---|
| `REMAINING_CHECKLIST.md` | Current proved/open status and notation |
| `polynomial_deformation/` | New proofs, contracts, controls, fresh verification, independent audit, and development logs |
| `research/perturbation/Paper_IX_Perturbation_Deformation_Bridge.md` | Recovered seed-lifting connection and written proofs of weighted nonlinear lifting and parameter charts |
| `polynomial_towers/`, `polynomial_counts/`, `polynomial_lifting/` | Previous tower, obstruction, torsor, and exact-count blocks |
| `strengthening/`, `shared_correction/`, `native/` | Sharp dyadic towers, exact periods and isometries, shared corrections, and native progress |
| `manuscript/`, `baseline/` | Historical Paper IX manuscripts and the unchanged original source archive |
| `historical/` | Previous release summaries, audits and manifests |
| `MANIFEST.json`, `PACKAGE_COMPLETENESS.json` | Exact distributed-file hashes and coverage of prior cumulative archives |

The prior perturbation note is preserved verbatim as a historical checkpoint. Its statement that its proofs were not yet newly formalized describes its creation time. This release formalizes the unit-Jacobian uniqueness and coefficient-stability part; the root checklist gives the current status.

## Boundaries and next work

The three controls reject global uniqueness across residue balls, uniqueness for rectangular smooth systems, and an unjustified extra digit in the perturbation bound.

The next clear formalization is the continuous rectangular root graph: choose an invertible Jacobian minor, specialize the remaining coordinates as parameters, and use the newly checked root stability to pass to arbitrary p-adic parameters. The written weighted proof also supplies a route for Jacobians singular modulo \(p\) but invertible over \(\mathbb Q_p\). General p-adic coefficient interfaces, weighted contraction, and the first-order displacement remainder are not Lean-checked by this block.

General singular towers, native presentation invariance and global/completed descent, remaining historical edge identities, exact higher differences, additional least-period families, general Mahler-kernel valuations, and arbitrary-row exact tails remain as listed in the checklist. The main historical manuscript has not yet been consolidated with every continuation.

The archive covers the known local Paper IX collection and earlier cumulative releases by uncompressed-file hashes. It excludes the separate portable runtime, reproducible compiled outputs and caches, repeated cumulative ZIP containers, and the full external Nishibuchi paper. Two older edge manuscripts remain partial recovered windows, and the Annals TeX is identified as reconstructed text.
