# Independent audit: polynomial uniqueness and coefficient perturbations

**Primary verdict: proved as written.**

This verdict concerns the three frozen Lean modules
`PolynomialPadicUnique.lean`, `PolynomialCoefficientPerturbation.lean`, and
`PolynomialRootStability.lean`, together with the exact statement contracts
compiled in `replay_01`. It does not promote the broader written weighted
perturbation theorem, rationally invertible singular Jacobians, first-order
motion formulas, or analytic parameter charts to Lean-checked status.

The audit was performed by a separate agent that read the actual definitions,
proof terms, prior lift-count and existence APIs, contracts, controls, source
records, and final gate logs. The audit did not edit any mathematical source.
The proof-audit workflow was used, with a literature check of the newly used
pinned Mathlib leaves and a conservative self-review of this document.

## 1. Normalized claims and scope

Write \(R=\mathbb Z_p\), let \(p\) be any prime, and write
\(\rho_n:R\to\mathbb Z/p^n\mathbb Z\) for the actual residue ring map.
For an integer polynomial system
\(F\in\mathbb Z[X_1,\ldots,X_d]^e\) and \(x\in\mathbb Z^d\), the reduced
Jacobian in the source is the actual linear map

\[
A_x:\mathbb F_p^d\longrightarrow\mathbb F_p^e,
\qquad
(A_xt)_i=\sum_{k=1}^{d}
\left(\frac{\partial F_i}{\partial X_k}(x)\bmod p\right)t_k.
\]

Lean uses coordinates `Fin d` and `Fin e`, indexed from zero. Mathematical
indices in this document are indexed from one. Divisibility of vectors is
always componentwise. All roots below are roots in the actual product
\(R^d\), evaluated through the canonical coefficient map \(\mathbb Z\to R\).

### A. Genuine local uniqueness

If \(e=d\), \(L\ge1\), and \(A_x\) is surjective, then any two exact roots
\(a,b\in x+p^LR^d\) of \(F\) are equal. This comparison theorem does not
assume a chosen lifting sequence, a chosen limit, or a lower-root hypothesis
on \(x\). When also \(F(x)\equiv0\pmod{p^L}\), the separate existence
theorem supplies a root, so there is exactly one root in that ball.

These are `padic_root_unique` and `exists_unique_padic_root`.
Surjectivity is the literal hypothesis; because source and target have the
same finite dimension over \(\mathbb F_p\), it is the usual invertibility
condition. No unrelated matrix or invertibility of an output Jacobian is
silently substituted for \(A_x\).

### B. Actual coefficient perturbations

For arbitrary \(c\in\mathbb Z\) and
\(F,H\in\mathbb Z[X_1,\ldots,X_d]^e\), define

\[
G=F+cH.
\]

The source proves the integer evaluation, partial derivative, and p-adic
evaluation identities directly from this polynomial definition. For any
natural modulus \(q\), if \(q\mid c\), then the actual reduced Jacobian of
\(G\) equals that of \(F\) at the same point. Congruent integer points modulo
\(q\) give the corresponding equality at different points. If
\(q^L\mid c\) and \(q^L\mid F(x)\), then \(q^L\mid G(x)\).

For prime \(p\), \(L\ge1\), \(p^L\mid c\), and surjective \(A_x\), a lower
root of \(F\) modulo \(p^L\) therefore produces an exact root of \(G\) in
\(x+p^LR^d\). This existence statement allows rectangular systems.

### C. Nearby roots at the full perturbation precision

If \(M\ge1\), \(p^M\mid c\), \(A_x\) is surjective, and an arbitrary exact
root \(a\) of \(F\) satisfies \(a\equiv x\pmod p\), then

\[
\exists b\in R^d:\qquad G(b)=0,
\qquad b-a\in p^MR^d.
\]

This is `exists_nearby_perturbed_root`. It permits \(e\ne d\) and makes no
uniqueness claim in the rectangular case. The root \(a\) is any exact root
with the indicated initial residue, not merely the limit previously chosen
by an existence construction.

### D. Square systems: every nearby perturbed root and unique existence

Suppose additionally \(e=d\), \(M\ge L\ge1\), and
\(a,b\in x+p^LR^d\) satisfy \(F(a)=0\) and \(G(b)=0\). Then

\[
b-a\in p^MR^d.
\]

This is `perturbed_roots_congruent`. In particular there exists exactly one
perturbed root in the original residue ball, and it retains the full
perturbation precision around the original root. The formal
`exists_unique_nearby_perturbed_root` theorem packages exact vanishing,
membership in the original ball, and the displacement bound in its unique
existential. Uniqueness among all roots in that ball follows from the
separate `padic_root_unique` theorem for \(G\), while
`perturbed_roots_congruent` shows the displacement condition is automatic.

Finally, `exists_root_and_unique_perturbation` starts only from
\(F(x)\equiv0\pmod{p^L}\), initial Jacobian surjectivity, and the coefficient
divisibility. It constructs an original exact root \(a\) and the uniquely
determined perturbed root \(b\) with all these conclusions. Its outer
existential is written as \(\exists a\), not \(\exists!a\); uniqueness of
that original root is supplied by the independently checked theorem A.

## 2. Dependency graph and decisive proof steps

The arrows below follow the actual source. No dependency points back to its
own desired conclusion.

1. **Internal finite polynomial theory:** actual integer polynomial Taylor
   divisibility gives the correction equation. Correction digits are
   bijective with actual residue lifts. Finite linear algebra gives exactly
   \(p^{d-e}\) lift classes at a surjective reduced Jacobian.
2. **Pinned Mathlib residue theory:** `PadicInt.ker_toZModPow` identifies the
   kernel with \((p^n)\). `MvPolynomial.hom_eval₂` shows that taking residues
   commutes with evaluating the original polynomial.
3. **Internal root truncation:** `truncInt` takes the canonical integer
   representative of \(\rho_n(a)\). It retains precision \(p^n\), and an
   exact root gives an actual integer root modulo \(p^n\). Faithfulness of
   integer divisibility is derived from the same residue maps.
4. **Internal one-step uniqueness:** an exact root in an integer residue
   ball determines an element of the actual next-level lift subtype. For a
   square smooth system this subtype has cardinality
   \(p^{d-d}=1\). `Nat.card_eq_one_iff_unique` gives `Subsingleton`, so the
   next residues of any two roots agree.
5. **Internal all-level uniqueness:** assume the roots agree modulo
   \(p^{L+n}\), truncate one of them at that level, and place both exact
   roots over this same integer representative. The representative is
   congruent to \(x\) modulo \(p\), so its reduced Jacobian equals
   \(A_x\). Step 4 raises their agreement to \(p^{L+n+1}\).
   `PadicInt.ext_of_toZModPow` then identifies the two p-adic vectors.
6. **Internal coefficient identities:** differentiating \(F+cH\) gives
   \(DF+cDH\). Since \(p\mid c\), reduction gives the same actual
   Jacobian. Since \(p^L\mid c\), the lower-root congruence is preserved.
7. **Prior internal existence:** the compatible integer tower and its
   actual p-adic limit produce a perturbed root. Only the initial reduced
   Jacobian is assumed surjective. Subsequent surjectivity, convergence,
   and exact polynomial vanishing are conclusions of the imported proofs.
8. **Internal full-precision stability:** truncate an arbitrary original
   root at level \(M\), apply step 7 there, and subtract the two precision
   congruences. This proves existence of a root within \(p^M\) of the
   original root, even in the rectangular case.
9. **Internal comparison of arbitrary square roots:** the root constructed
   in step 8 lies in the original ball because \(M\ge L\). Step 6 supplies
   the actual surjective Jacobian of \(G\). Step 5 for \(G\) identifies an
   arbitrary root in that ball with the constructed one. No uniqueness
   hypothesis is assumed here.

The potentially delicate use of `Nat.card` is sound: the value one implies
both nonemptiness and subsingletonness for any type. The proof does not
confuse the cardinality of a residue quotient with the infinitely many
integer representatives of each residue.

## 3. Obligation matrix

| Obligation | Status | Evidence and exact boundary |
|---|---|---|
| Actual polynomial input and output | Passed | `MvPolynomial` over integers, actual `pderiv`, and `eval₂` into \(\mathbb Z_p\). |
| Jacobian derived from the given system | Passed | `digitJacobian` is the sum of evaluated partial derivatives. The perturbation identities expand this sum. |
| Arbitrary roots in the uniqueness theorem | Passed | Only exact vanishing and ball membership are assumed. Canonical truncation supplies the finite lift classes. |
| No circular appeal to uniqueness | Passed | One-step uniqueness comes from finite cardinality; full uniqueness comes from induction and residue separation. |
| Output smoothness | Passed | The equality of reduced Jacobians is derived, both after moving the point and after changing coefficients. |
| All prime numbers, including two | Passed | All universal root theorems use only `Fact (Nat.Prime p)`. No odd-prime hypothesis or division by two occurs. |
| \(M=L\) and \(L=1\) | Passed | All inequalities are non-strict. The only positivity needed is \(L\ge1\), hence \(M\ge1\). |
| \(c=0\), negative \(c\), and arbitrary multiples of \(p^M\) | Passed | \(c\) is an arbitrary integer with a divisibility hypothesis, never a positive integer or a nonzero unit. |
| Zero-dimensional systems | Passed | `d` and `e` are unrestricted naturals. For the square \(d=e=0\) system the vector type has one element. Rectangular hypotheses still include surjectivity and exact vanishing. |
| General natural modulus in algebraic identities | Passed | The Jacobian and lower-root perturbation identities allow all \(q\); p-adic existence remains restricted to prime \(p\). |
| Retained displacement \(p^M\) | Passed | Derived around any smooth exact root by truncation at \(M\), not merely at initial precision \(L\). |
| A uniform extra digit \(p^{M+1}\) | Refuted as an extension | The checked dyadic example \(F=X\), \(G=X-2\), \(a=0\), \(b=2\) has \(M=L=1\), but \(4\nmid b-a\). |
| Global uniqueness | Refuted as an extension | \(X^2-1\) over \(\mathbb Z_3\) has roots \(1\) and \(-1\) in different residue balls, with invertible Jacobian at \(1\). |
| Rectangular uniqueness | Refuted as an extension | \(F(X,Y)=X\) has a surjective Jacobian and distinct roots \((0,0)\), \((0,2)\) in the same dyadic residue ball. |
| Arbitrary p-adic polynomial coefficients | Out of scope | Coefficients of \(F,H\) and the scalar \(c\) are integers. Only the root coordinates are arbitrary p-adic integers. |
| Weighted inverse loss \(s>0\) | Not addressed | The actual reduced Jacobian is surjective here. No rational inverse with denominators is constructed in this block. |
| First-order root motion and error estimate | Not addressed | No inverse-Jacobian displacement formula is asserted by these modules. |
| Analytic or continuous parameter chart | Not addressed | Pointwise existence with a precision bound is proved. A parameter-to-root map and its regularity are not constructed here. |

## 4. Source verification

The exact new external mathematical leaves were checked in the authorized
local source tree of Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`:

| Source | Exact declarations or identities used | Translation checked |
|---|---|---|
| `Mathlib/NumberTheory/Padics/RingHoms.lean` | `toZModPow`, `ker_toZModPow`, `ext_of_toZModPow` | Prime \(p\), all \(n\ge0\), the actual quotient maps, and separation of actual p-adic integers. |
| `Mathlib/SetTheory/Cardinal/Finite.lean` | `Nat.card_eq_one_iff_unique` | Cardinality one of the actual lift subtype implies subsingletonness and nonemptiness. |
| `Mathlib/Algebra/MvPolynomial/Eval.lean` | `hom_eval₂`, `eval₂_comp` | Coefficients \(\mathbb Z\), values \(\mathbb Z_p\), and residues \(\mathbb Z/p^n\mathbb Z\). |
| `Mathlib/Algebra/MvPolynomial/PDeriv.lean` | `pderiv_C_mul` | The scalar \(c\) is constant with respect to every variable. |

Exact source hashes, stable revision links, hypotheses, and notation
translations are recorded in `audit/mathlib_source_records.json`. The eight
previous source hashes from the tower audit were also checked against the
same pinned tree. Existing project-local sources were sufficient; no fresh
web lookup or external novelty claim was needed.

The earlier written seed-lifting and weighted perturbation results motivate
this block but are not unchecked premises of these Lean proofs.

## 5. Fresh gate and independent reconciliation

The fresh gate completed with **PASS** in **93.457 seconds**:

| Item | Verified value |
|---|---:|
| Formalization modules | 17 |
| Positive control support modules | 1 |
| Statement contract files | 3 |
| Theorems in the statement contracts | 7 |
| Negative control files | 3 |
| Total gate steps, including compiler version and axiom audit | 26 |
| Explicit declaration axiom audits | 159 |
| Audited theorems | 126 |
| Audited definitions | 29 |
| Audited abbreviations | 4 |
| New declarations in the three mathematical modules | 24: 21 theorems and 3 definitions |
| Source and control hashes independently reconciled | 24 |
| Compiled output hashes independently reconciled | 105 |
| Preserved prior formalization modules, byte-for-byte | 14 |

The gate uses Lean `4.34.0-rc2`, warnings as errors, a fresh output directory,
one compiler thread, and a 240-second timeout per source. It recompiles every
project module in the current dependency closure, every contract, and the
positive control support. Only the pinned compiler and precompiled Mathlib
dependencies are reused.

All 159 axiom closures are subsets of
`propext`, `Classical.choice`, and `Quot.sound`. There are no admitted proofs,
custom axioms, `unsafe` proof constructions, `native_decide`, or unlimited
heartbeat settings in the audited sources. These are universal kernel
checked statements, not bounded numerical experiments.

The independent script `audit/reconcile_verification.py` does not import the
builder's source-audit or verification scripts. It recomputes source,
inventory, script, log, and compiled-output hashes; scans declarations;
checks every logged return code; reparses every explicit axiom closure;
and verifies that the 14 prior modules remain unchanged. It reports PASS in
`audit/reconciliation.json`.

Commands checked:

```text
python3 polynomial_deformation/scripts/verify_polynomial_deformation.py --kit /workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2 --output polynomial_deformation/replay_01
python3 polynomial_deformation/audit/reconcile_verification.py
```

Frozen report SHA-256:
`b34e50a34d4feaa8473f099b5a9bb8f3240e27000b3825c40fc6cf973330783b`.

Frozen inventory SHA-256:
`e6eb19c65eb4b3a0dd7596f59960d79e829a6fddbceea7390ed8ed9569b1ce03`.

Frozen mathematical source hashes:

| Module | SHA-256 |
|---|---|
| `PolynomialPadicUnique` | `51a734f436ec118fd39cf20ad228eedaffe5225eeb989b5a1040deb701c0f4cd` |
| `PolynomialCoefficientPerturbation` | `fbb6841c84bf08cd074cd3ecdb40ef9fec4cc65708272abd0fd034f7ccbc5198` |
| `PolynomialRootStability` | `77eb7db2cc0e93d3f57f0248cf7e19f30932416441caa369f625f15a2869a2db` |

Each negative control fails with exit code one and a genuine mathematical
type mismatch, after its imports and positive counterexample support
compile. The failures are not missing-module errors or timeouts. These
controls deliberately try to inhabit false propositions with checked
counterexample terms. Their force comes from the positive counterexamples;
they do not constitute an exhaustive mutation test of every hypothesis.

Earlier development failures were retained and inspected. They included a
reversed divisibility equivalence, an evaluation rewrite that did not match,
a warnings-as-errors `letI` style issue, and a coefficient-cast simplification
goal. These were implementation failures rather than evidence for a stronger
mathematical theorem. The final frozen sources correct them, and the fresh
gate has no such errors. Empty or earlier successful development logs were
not substituted for the fresh final replay.

## 6. Remaining gap and strongest safe statement

There is no remaining implication gap in the normalized claims A–D above.
The strongest safe statement of this block is: for finite integer polynomial
systems, a smooth root modulo a prime determines nearby exact p-adic roots
under coefficient perturbations; arbitrary original exact roots admit
perturbed roots with full coefficient precision; and in a square smooth
residue ball both the root and its perturbation are unique.

This resolves the formal local square-root uniqueness item and the smooth
integer-coefficient nearby-root stability item. It does not resolve the
entire deformation program. The nearest additional claim requiring a new
proof is a defined parameter-to-root map, followed by its compatibility and
regularity, or the weighted \(s>0\) singular-modulo-\(p\) case. Neither follows
merely by renaming this block's surjectivity hypothesis.

No further optional replay is needed for the frozen sources. A later source
change should receive a new inventory and fresh gate. The trust boundary
remains the pinned Lean kernel, the listed standard axioms, and the pinned
precompiled Mathlib; this is not a second independent kernel implementation.

Self-review: this audit document and its mathematical displays were reread
against the exact source contracts. No mathematical source was changed. No
unresolved notation, hypothesis, or scope discrepancy remains in this audit.
