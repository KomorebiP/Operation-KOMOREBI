# Polynomial lifting block: independent proof audit

Author of release: Komorebi P.

Primary verdict: **proved as written** for the fixed finite polynomial presentation, positive depth, and one-step lifting statements specified below.

This reviewer independently read `PolynomialObstruction.lean`, `PolynomialRepresentative.lean`, `PolynomialShared.lean`, the relevant previous affine/shared quotient sources, and the new contracts and controls. The reviewer authored the separate Taylor module, so the review of that dependency is a self-audit, not an independent authorship check. The obstruction, representative, and simultaneous-lifting implementations were authored by other agents and were inspected directly.

## Normalized claim

Let \(d,e\) be natural numbers, \(q\ge1\), \(L\ge1\), and let
\(F=(F_1,\ldots,F_e)\) be an actual finite list of polynomials in
\(\mathbb Z[X_1,\ldots,X_d]\). Suppose \(F(x)\in q^L\mathbb Z^e\), and put
\(r=F(x)/q^L\in\mathbb Z^e\). The integer Jacobian is
\[
J_x(t)_i=\sum_k \partial_kF_i(x)t_k.
\]
Its reduced map is
\(\overline J_x:\mathbb Z^d\to(\mathbb Z/q\mathbb Z)^e\).
Define the finite quotient of underlying integer modules
\[
O_x=(\mathbb Z/q\mathbb Z)^e/\operatorname{im}\overline J_x,
\qquad o_x=[r\bmod q].
\]
Then
\[
o_x=0\iff \exists y\equiv x\pmod {q^L},\quad F(y)\equiv0\pmod {q^{L+1}}.
\]
Both the reduced Jacobian and the residual class are independent of the integer representative of the same residue vector modulo \(q^L\), under the explicit common-quotient identification in `representative_independence`.

For two actual polynomial lists \(F,G\) on the same variables, write \(\overline J_x,\overline K_x\) for the two reduced Jacobians and define
\[
C_x=\mathbb Z^d/(\ker\overline J_x+\ker\overline K_x).
\]
This is finite. Given corrections \(u,v\) that produce valid individual next-level lifts of \(F,G\), respectively,
\[
\exists y\equiv x\pmod {q^L}: F(y)\equiv G(y)\equiv0\pmod {q^{L+1}}
\iff [u]=[v]\text{ in }C_x.
\]
Each side's class is independent of its chosen individual lift. The final unconditioned theorem includes individual liftability on the right-hand side; it does not assume that arbitrary pairs of locally attainable targets have a common lift.

## Dependency graph

1. Actual `MvPolynomial.pderiv`, evaluation, and polynomial induction give the integral Taylor remainder
   \(a^2\mid F_i(x+at)-F_i(x)-aJ_x(t)_i\). This is an internal Lean proof, not a premise.
2. \(L+1\le2L\) for \(L\ge1\) makes that remainder vanish modulo \(q^{L+1}\).
3. Exact residual division and cancellation of nonzero \(q^L\) give
   \(F(x+q^Lt)\equiv0\pmod {q^{L+1}}\iff r+J_x(t)\equiv0\pmod q\).
4. The previously proved quotient criterion identifies residual class zero with an actual integer correction. The minus sign is handled by taking the negative of a range witness.
5. Every integer representative \(y\equiv x\pmod {q^L}\) has the form \(x+q^Lt\); this proves the criterion for actual representatives, not merely a restricted class of candidate corrections.
6. Evaluation congruence applies to the actual partial derivative polynomials, giving equality of the reduced Jacobians at representatives. Taylor transport gives \(r'\equiv r+J_x(s)\pmod q\), whose difference vanishes in the common cokernel.
7. For the pair, the already proved common-kernel quotient identity identifies equality of correction classes with existence of one correction having the required two images. Applying Step 3 to each block proves the simultaneous nonlinear lift criterion.

Leaves are internal Lean proofs or pinned Mathlib definitions/theorems. No external literature theorem, numerical experiment, or unproved arithmetic bridge is needed. No circular dependency was found.

## Obligation matrix

| Obligation | Status | Evidence and scope |
|---|---|---|
| Actual polynomial/Jacobian relationship | Passed | `jacobian` is the sum of evaluations of genuine `MvPolynomial.pderiv`; Taylor transport is derived. |
| Arbitrary degree and finite dimension | Passed | Universal polynomial induction; no degree or dimension bound. Empty variable/equation types are allowed. |
| Positive modulus and cancellation | Passed | \(q>0\) supplies \(q^L\ne0\); composite \(q\) and \(q=1\) are included. |
| Positive depth | Passed | \(L\ge1\) is explicit wherever Taylor reduction is used. |
| Exact residual existence and uniqueness | Passed | Derived from lower-level divisibility and integer cancellation, respectively. |
| Genuine finite obstruction | Passed | Quotient of a finite `Fin e → ZMod q`; the source of the reduced Jacobian may remain infinite. |
| Residual sign | Passed | Quotient membership permits a correction with the opposite sign; digit equation is \(r+J_xt=0\). |
| All same-residue representatives | Passed | `same_residue_iff` supplies an integer correction in both directions. |
| Representative independence | Passed | Same fixed presentation; common reduced map and literal equality in its quotient are exhibited. |
| Independent choices of individual lifts | Passed | Shared classes are unchanged when the corresponding reduced Jacobian image is unchanged. |
| Separate versus joint liftability | Passed | Joint theorem retains the shared class equality; explicit controls refute unconditional gluing. |
| Change of polynomial presentation | Out of scope | No claim of invariance under adding equations, generators, or presentation equivalences. |
| Infinite compatible lifting | Out of scope | Theorems decide one lift from \(q^L\) to \(q^{L+1}\), not an infinite sequence. |
| General native seed systems or adelic descent | Out of scope | No unrestricted native-category or global arithmetic reconstruction claim is made. |

## Decisive boundary checks

The checked `PolynomialControls` module proves three useful boundaries.

* **Depth zero:** for \(P=X^2,x=0,t=1\), the first-order remainder is \(1\), which is not divisible by \(2\). Thus the positive-depth condition cannot simply be deleted.
* **Singular lower root:** \(X^2-2\) vanishes at \(0\pmod2\), with zero Jacobian there, but no even integer makes it vanish modulo \(4\). The obstruction criterion does not automatically lift singular roots.
* **Individual lifts need compatibility:** \(X\) and \(X-2\) both vanish at the same lower residue \(0\pmod2\) and lift individually modulo \(4\), using \(0\) and \(2\). No single integer solves both equations modulo \(4\).

Two further elementary scope checks explain exclusions; these are explanatory calculations rather than claims of additional Lean declarations in this release.

* Adding a zero equation leaves the solution problem unchanged but adds a \(\mathbb Z/q\mathbb Z\) factor to the raw Jacobian cokernel. For example, \(F=(X)\) has zero cokernel, while \((X,0)\) has cokernel \(\mathbb Z/q\mathbb Z\). Therefore representative independence does not establish presentation-independent canonical obstruction groups.
* \(X^2-5\) has the odd root residue modulo \(2\) and a compatible lift modulo \(4\), but has no root modulo \(8\), since odd squares are \(1\pmod8\). One successful step does not imply indefinitely many successful steps.

## Coefficient domain and finite-field distinction

The formal quotients use integer modules with targets `Fin e → ZMod q`, and the shared source is `Fin d → ℤ`. This formulation deliberately covers composite moduli. When \(q=p\) is prime, the reduced Jacobian factors through \(\mathbb F_p^d\), and the usual finite-field interpretation is mathematically consistent with the definitions. This block does not separately formalize that change-of-scalars identification, a rank-nullity formula, or the lift count \(p^{d-\operatorname{rank}J}\). Those should not be included in its Lean completion count.

## Source and verification record

The local portable runtime pins were read directly:

* Lean `v4.34.0-rc2`.
* Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Reviewed frozen source hashes:

| Source | SHA256 |
|---|---|
| `PolynomialTaylor.lean` | `192667cea6c00131792d164ef6d802a689d4a34f8c465235a42d9319c57e699b` |
| `PolynomialObstruction.lean` | `ab0670c8d9c84aaf36e0e83f396c26f0514b8279f694d7b3653c3ab43410c653` |
| `PolynomialRepresentative.lean` | `68818904b747cd7b845877777458138ab0bed5938cf938a69b8e27acb5150fb2` |
| `PolynomialShared.lean` | `8df73989caf432acdf0b7278f95d0e3f0afa1e8804b77e56ff9b09e019ff0825` |

The development compile logs for these modules were inspected. The Taylor, obstruction, and shared source audit output uses only `propext`, `Classical.choice`, and `Quot.sound`. The representative compile is clean. The independent combined gate is maintained separately; its machine-readable report, rather than historical release aggregate metadata, is authoritative for final run counts.

The explicit Taylor contract expands the directional derivative. The obstruction contract exposes the actual polynomial evaluations, finite quotient, residual class, and same-residue lift quantifiers. The invalid controls attempt to use a negation as a positive result or separate witnesses as one shared witness; rejection validates the check pipeline, while the positive control theorems provide the actual mathematical counterexamples. These controls do not constitute an exhaustive proof audit by themselves.

The representative contract explicitly supplies one common reduced Jacobian before comparing classes in its quotient. The shared contract expands the actual two-block lift, separate corrections, and sum-of-kernels quotient. Both were independently read after completion. `POLYNOMIAL_LIFTING.md` was compared with all four contracts and the implementation; its notation, hypotheses, examples, and completion boundaries are consistent with the proofs. The prime-field cardinality statements there are explicitly listed as further formalizations.

### Final gate reconciliation

The independent check of `replay_01/polynomial_verification.json` and `computation_manifest.json` passed. It recomputed source, log, build-output, runner/verifier, inventory, and manifest-linked hashes; compared the complete inventory declaration set against the parsed axiom closure set; and checked the actual diagnostic logs and return codes for all gate entries.

* Nine project modules freshly compiled, including four unchanged prior dependencies and five new modules.
* Four exact statement contracts compiled.
* Three invalid-proof controls rejected with the expected type errors, with no import failure, unknown constant, panic, or timeout accepted as a rejection.
* Eighteen total gate entries passed in 66.708 seconds.
* Ninety-one explicit declaration audits: 69 theorem declarations, 18 definitions, four abbreviations. These include prior dependencies, supporting lemmas, control results, and contract declarations; they are not 91 new mathematical discoveries.
* All 16 inventoried Lean source/contract/control hashes, 18 log hashes, and 65 build-output hashes matched.
* All 91 closure entries use only `propext`, `Classical.choice`, and `Quot.sound`.
* The four prior dependency source copies were separately checked byte-for-byte against `shared_correction/formalization/`.
* Mathlib was reused from the pinned portable kit; it was not rebuilt in this gate. No project compiled artifact was reused.

Verification report SHA256: `b89333cdbf052619fd6c7ecb12104da730e8d4f9681c042030a1c1bc4b705936`.

Computation manifest SHA256: `56a946466e9a74fd7367f19a71525baaad9ee3cba3c2f0cfd27fc80e7df95607`.

No aggregate metadata from an older release was used to infer these counts. This review does not re-audit all older Paper IX results.

## Remaining gap and safe release statement

There is **no remaining mathematical gap in the scoped fixed-presentation one-step statements audited here**. General native 13.2 and 13.3 still require their own precise object categories, presentation-equivalence data, compatibility maps, and application arguments. Infinite lifting and global descent require additional theorems and hypotheses.

The strongest safe summary is: **all finite lists of integer multivariable polynomials admit the proved finite one-step obstruction at positive depth; that obstruction is independent of representatives within the fixed presentation; two such blocks sharing the same unknowns have the proved finite shared-correction criterion for actual simultaneous one-step lifts.**
