# Paper IX: continuous dyadic isometric bijections

**Author: Komorebi P. — 8 September 2026.**

The continuous-isometry item from the previous checklist is now proved in Lean. Each of the four normalized dyadic packets extends uniquely to an isometric bijection of the dyadic integers. The original coefficient sequences extend to continuous injective maps with exactly specified images and distance scaling.

The cumulative package preserves all prior completion, sharp-tower, exact-period and shared-correction results. The current checked and unchecked entries are in [REMAINING_CHECKLIST.md](REMAINING_CHECKLIST.md).

## The actual packet theorem

Set
\[
U_j(n)=E_{4n}^{(4,j)}=j!C_{4,j}(n),\qquad
(d_0,d_1,d_2,d_3)=(1,1,5,3),\qquad 0\le j<4.
\]
There is a unique isometric bijection
\[
\boxed{G_j:\mathbb Z_2\longrightarrow\mathbb Z_2}
\]
such that, for every natural packet index \(n\),
\[
\boxed{G_j(n)=\frac{U_j(n)-j!}{2^{d_j}}.}
\]
Rational expressions are embedded in \(\mathbb Q_2\), and the proof establishes that these normalized values lie in \(\mathbb Z_2\). The defining identity is checked against the actual coefficient functions and their recurrence-derived exact displacement theorem.

For all \(x,y\in\mathbb Z_2\),
\[
|G_j(x)-G_j(y)|_2=|x-y|_2,\qquad G_j(0)=0.
\]
Every target \(z\in\mathbb Z_2\) has exactly one preimage. The inverse is included in the Lean `IsometryEquiv` object. Uniqueness holds among **all continuous maps** with the prescribed natural values; a competing map need not be assumed an isometry.

This is a metric theorem. The maps need not preserve addition. Actual checked values include
\[
G_0(1)=-1,\qquad G_0(2)=34,\qquad G_0^{-1}(34)=2,
\]
and Lean proves that \(G_0\) is not additive.

## Original coefficients and exact images

Define
\[
\widetilde U_j(x)=j!+2^{d_j}G_j(x).
\]
Lean proves that \(\widetilde U_j\) is continuous and injective, agrees with \(U_j(n)\) at every natural packet index, and satisfies
\[
\boxed{|\widetilde U_j(x)-\widetilde U_j(y)|_2
       =2^{-d_j}|x-y|_2.}
\]
Its image is exactly \(j!+2^{d_j}\mathbb Z_2\), and every point of that image has a unique preimage.

| Address \(j\) | Gain \(d_j\) | Exact image of \(\widetilde U_j\) |
|---|---:|---|
|0|1|\(1+2\mathbb Z_2\)|
|1|1|\(1+2\mathbb Z_2\)|
|2|5|\(2+32\mathbb Z_2\)|
|3|3|\(6+8\mathbb Z_2\)|

The original address-zero map never attains zero. This is a checked control against inadvertently claiming surjectivity of the unnormalized map onto all of \(\mathbb Z_2\).

The interpolation variable is the **packet index**. Natural input \(n\) gives the original Euler coefficient at degree \(4n\); the external statement contract checks this correspondence explicitly.

## Why the extension is onto

The generic theorem is proved for every prime \(p\). If \(f:\mathbb N\to\mathbb Z_p\) satisfies
\[
d(f(m),f(n))=d(m,n)
\]
where the right-hand distance is computed after embedding the natural numbers in \(\mathbb Z_p\), then \(f\) extends uniquely to an isometric bijection \(\mathbb Z_p\to\mathbb Z_p\).

The proof uses the natural-cast range as a subspace of \(\mathbb Z_p\). Its induced metric is essential: this is not an extension from the usual discrete metric on \(\mathbb N\). Density and completeness give the continuous extension, and equality on a dense product gives exact distance preservation everywhere.

Surjectivity is derived from compactness. For a self-isometry of a compact metric space, two sufficiently late iterates of any point are arbitrarily close. Cancelling the common isometric iterate shows that a positive iterate returns arbitrarily close to the point. The image is therefore dense. It is also compact and closed, hence is the whole space. Lean formalizes this argument before applying it to \(\mathbb Z_p\).

For the actual four packets, the prior exact law
\[
v_2(U_j(n+T)-U_j(n))=v_2(T)+d_j\qquad(T>0)
\]
removes precisely the normalization factor. Equal rows and reversed row order are handled separately, yielding a rational norm identity for every pair of natural inputs. No convergence estimate, surjectivity premise or interpolation identity is assumed for these packets.

## New Lean modules

All active sources are in `strengthening/formalization/`.

| Module | Role |
|---|---|
| `CompactSelfIsometry.lean` | Every self-isometry of a compact metric space is surjective |
| `DensePadicIsometry.lean` | Unique isometric extension for every prime \(p\) |
| `RationalPadicEmbedding.lean` | Rational norm identity gives integral samples with the required metric |
| `DyadicPacketRational.lean` | Exact normalization of the actual \(N=4\) coefficients |
| `DyadicFourIsometry.lean` | Actual bijections, continuous uniqueness, original images and distance scaling |
| `DyadicIsometryControls.lean` | Forward and inverse values, failure of additivity and original-image boundary |

The main declarations are `DyadicFourIsometry.existsUnique_isometry`, `unique_continuous`, `unique_preimage`, `originalExtension_nat`, `originalExtension_dist`, `unique_original_preimage` and `originalExtension_range`, under namespace `KomorebiPaperIX`.

## Validation and reproduction

The combined replay passed all **38 gates in 146.828 seconds**, including three statement contracts and eleven rejected invalid proofs. The current gate record is `strengthening/verification/continuation_verification.json`. It compiles the prior sixteen dyadic modules and these six modules together, audits every explicit declaration, and runs all old and new statement contracts and invalid-proof controls. The independent mathematical audit is `isometry/INDEPENDENT_PROOF_AUDIT.md`.

The six new modules contain 46 named theorems/supporting lemmas and eight definitions, including six boundary controls. Together the 22-module continuation has 246 explicit declaration audits. These counts describe the proof inventory, not independent discoveries. Only `propext`, `Classical.choice` and `Quot.sound` are permitted. Warnings are treated as errors.

The observed run freshly compiles all 22 continuation modules. It revalidates and reuses the earlier checked baseline build, and reuses the pinned Mathlib cache. The independent shared-correction block retains its previous passing replay and is not rebuilt in this block. Development logs preserve corrected numeral-coercion and simplification failures.

Reproduce the full preserved baseline/native work and the current dyadic continuation with the pinned Linux kit:

```sh
python3 replay_exact_periods.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run
```

The existing wrapper reads the updated active source inventory, so this command includes the new isometry modules. To include the independent shared-correction block as well:

```sh
python3 replay_shared_correction.py --all --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_full_run
```

These full wrappers are supplied for reproduction; the observed run reused the checked baseline as described above. The runtime is Lean 4.34.0-rc2 with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. No dependencies are downloaded by the wrappers.

## What remains

The next clear formalization block is the multivariable polynomial Taylor/lifting criterion for a fixed presentation, followed by its shared-Jacobian application. Unrestricted native Conjectures 13.2/13.3 still require precise definitions and additional invariance and descent arguments. Exact higher differences, other least-period families and general affine Mahler-kernel valuations remain research questions. The continuous \(N=4\) isometry is now checked off in `REMAINING_CHECKLIST.md`.
