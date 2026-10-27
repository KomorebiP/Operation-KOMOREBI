# Independent audit: finite polynomial lift counts

**Normalized claim and verdict: proved as written.** For a fixed finite list of integer polynomials, a prime modulus, positive depth, and an actual lower root, the formalization counts distinct next-level residue classes by the actual reduced Jacobian and actual residual obstruction. It also constructs the correction-digit torsor and identifies the earlier integer-module obstruction with the finite-field cokernel. This audit was performed by a separate agent that did not author the five core modules or their proofs.

## Claim card

Let \(d,e\in\mathbb N\), let \(p\) be prime, let \(L\ge1\), and let
\[
F\in\mathbb Z[X_1,\ldots,X_d]^e,\qquad
x\in\mathbb Z^d,\qquad F(x)\equiv0\pmod{p^L}.
\]
The residual \(r=F(x)/p^L\) is an integer vector. Set
\[
b=r\bmod p,\qquad
A=DF(x)\bmod p:\mathbb F_p^d\longrightarrow\mathbb F_p^e,
\qquad \rho=\dim_{\mathbb F_p}\operatorname{im}A.
\]
Define
\[
\mathcal L_{x,L}=\{y\in(\mathbb Z/p^{L+1}\mathbb Z)^d:
 y\equiv x\pmod{p^L},\ F(y)=0\},\qquad
\mathcal O=\mathbb F_p^e/\operatorname{im}A.
\]
Then
\[
\#\mathcal L_{x,L}=\begin{cases}p^{d-\rho},&[b]=0,\\0,&[b]\ne0,\end{cases}
\qquad \#\mathcal O=p^{e-\rho}.
\]
The correction fiber \(\mathcal T=\{t\in\mathbb F_p^d:b+At=0\}\), when nonempty, carries an explicit `AddTorsor` structure for \(\ker A\), acting by translation. It is explicitly equivalent to \(\mathcal L_{x,L}\). A chosen correction gives an equivalence \(\mathcal L_{x,L}\simeq\ker A\). The sources do not separately install an `AddTorsor` instance on `ActualLifts` itself.

The residue parametrization and polynomial digit bridge work for every positive natural modulus \(q\), including composite moduli and \(q=1\). The residue parametrization alone permits \(L=0\); the polynomial Taylor application requires \(L\ge1\). Prime-field rank formulas have an explicit `[Fact (Nat.Prime p)]` assumption. Zero variables and zero equations are permitted.

## Dependency graph

1. **Internal proof:** `PolynomialTaylor.taylor_dvd` uses induction on the actual `MvPolynomial`, proving the remainder is divisible by the square of the step. `taylor_step_dvd` uses \(2L\ge L+1\).
2. **Internal proof:** `PolynomialObstruction.next_level_iff_digit` derives the correction equation from that Taylor remainder and the actual residual. It assumes no liftability or Jacobian-surjectivity oracle.
3. **Internal proof:** `PolynomialDigitBridge.reduction_jacobian` equates the reduced integer Jacobian with the finite-ring linear map whose entries are evaluated formal partial derivatives.
4. **Internal proof:** `ResidueLiftDigits.digitEquivResidue` proves injectivity and surjectivity of \(t\mapsto x+q^L\widetilde t\pmod{q^{L+1}}\). `next_modulus_dvd_val_sub_shift` relates canonical and shifted integer representatives.
5. **Internal proof:** `PolynomialLiftCounts.digit_residue_solution_iff` combines polynomial congruence with Taylor transport. `digitEquivLifts` restricts the full residue equivalence to the actual polynomial solution subtype.
6. **Internal proof:** `FiniteFiberCounts` constructs translation, subtraction, torsor laws, unique translation, and the chosen-point kernel equivalence. Its quotient-class test handles the sign \(b+At=0\) correctly.
7. **Internal proof:** `IntegerFiniteCokernel` proves integer reduction is onto, identifies the two images after scalar restriction, and gives a quotient equivalence preserving every residual class.
8. **Pinned Mathlib theorems plus internal assembly:** finite-vector-space cardinality, rank-nullity, and quotient dimension yield the two formulas. `finite_polynomial_lift_count` derives the residual from the lower-root hypothesis rather than requiring an unexplained residual premise.

The dependencies are acyclic. No finite experiment is used as a universal proof.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Counted objects are actual next-modulus residues | Passed | `ActualLifts` is a subtype of `Fin d → ZMod (q^(L+1))`, with both lower-residue and original-polynomial predicates. |
| No integer representative overcount | Passed | `digitEquivResidue` is proved injective and surjective. |
| Canonical representative convention is harmless | Passed | `eval_dvd_of_dvd` and `next_modulus_dvd_val_sub_shift` establish equal polynomial congruences. |
| Jacobian is the actual derivative | Passed | Entry formula uses `MvPolynomial.pderiv`; reduction commutes with the displayed map. |
| Residual sign and normalization | Passed | Exact premise is `evalSystem F x = q^L • r`; digit condition is `reduction r + A t = 0`. |
| Prime-field assumptions and dimension order | Passed | Lift exponent uses domain dimension \(d\); obstruction exponent uses target dimension \(e\); both subtract actual range dimension. |
| Finiteness is not inferred from `Nat.card` alone | Passed | For prime \(p\), the ambient residue spaces, their subtypes, and quotients are finite. |
| Freeness and transitivity are proved | Passed | Explicit torsor structure, inverse translation identities, and `translate_exists_unique`. |
| Original obstruction is counted | Passed | `obstructionEquiv` is integer-linear and `obstructionEquiv_class` preserves the distinguished class. |
| Zero dimensions, empty and singular fibers | Passed | Universal types impose no positive-dimension or nonsingularity assumptions; the empty branch is explicit. |
| General presentation invariance | Out of scope | Fixed presentation only; adding a zero equation can change the raw cokernel. |
| Infinite compatible lift or p-adic root | Out of scope | No inverse-limit theorem is included in this block. |
| Independent kernel implementation | Out of scope | The supplied pinned Lean kernel and cached Mathlib are trusted dependencies. |

## Small cases and restriction checks

The compiled controls give one actual lift for \(F=X\), \(q\) actual lifts for the zero equation over a fixed lower residue, two lifts of \(X^2\) over the even root modulo two, and zero lifts of \(X^2-2\) over that same lower root. Thus identical zero Jacobians can have different lift counts when their residual classes differ. The zero equation has four unrestricted roots modulo four but only two above the even lower residue.

The following additional examples were checked directly from the definitions as explanatory mathematics, not added as Lean controls:

- At \(L=0\), \(F=X^2\), \(p=2\), \(x=0\), the Jacobian is zero but only zero is a root modulo two. The positive-depth count cannot be extended to that level.
- Multiplication by two on \(\mathbb Z/4\mathbb Z\) has kernel \(\{0,2\}\), of size two. A general power-of-four formula based on vector-space rank is inappropriate.
- For \(d=0\), there is one candidate lift and it survives exactly when all constant residuals vanish modulo \(p\). For \(e=0\), every one of the \(p^d\) correction digits survives and the obstruction has one element.
- The asymmetric example \(F=(X,0)\), \(d=1,e=2\), has one lift over zero and obstruction size \(p\), confirming the different dimension roles.

## Source and computation checks

The local primary source is Mathlib at revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, in the pinned Lean `4.34.0-rc2` kit. This audit read the definitions/proofs of `AddTorsor`, `ZMod.intCast_surjective`, the residue-cast divisibility theorem, quotient scalar restriction, `LinearMap.finrank_range_add_finrank_ker`, `Submodule.finrank_quotient`, and `Module.natCard_eq_pow_finrank`. The coefficient, finite-generation and scalar hypotheses specialize correctly to the stated finite prime-field maps. No external novelty or priority claim was investigated or made.

The fresh verification record reports **PASS in 52.489 seconds**: **9 source modules**, **3 statement-contract modules**, **3 mathematical negative controls**, **17 gates**, and **106 explicit declaration audits** (76 theorems, 26 definitions, 4 abbreviations). Every project module in this block and its three project dependencies was freshly compiled; precompiled Mathlib was reused. Warnings were errors. All audited declarations use only `propext`, `Classical.choice`, and `Quot.sound`.

The expanded polynomial contract states the actual lower-root hypothesis, actual nested residue subtype, original polynomial evaluation, actual Jacobian rank, and original obstruction quotient. Separate contracts expose the Jacobian entry formula, full residue equivalence and its forward map, kernel translation, and generic fiber counts. All three negative controls failed with the intended mathematical `Type mismatch`: zero versus two lifts, two versus one lift, and four versus two unrestricted roots. None failed because of missing imports, unknown constants, or timeouts.

Independent reconciliation reread and checked **9 module sources**, **3 contracts**, **3 negative controls**, **8 exact matches with reviewed development/prior source files**, **17 raw log hashes and exit expectations**, **60 compiled-output hashes**, and **106 complete axiom-closure records**. The verifier, source scanner, runner, and inventory hashes also match. See `audit/RECONCILIATION.json` and `audit/reconcile.py`.

Verification report SHA256:
`c4446c5fd8ead020d9eb01c14fa8f635a01d7ef8fb59d265e965544e8ffc1238`

Frozen inventory SHA256:
`233c9c2e4b6a196c9b0103896bf818ba89637888c6852e0346c065b4fab366dc`

The observed commands were the fresh `scripts/verify_polynomial_counts.py` gate with the pinned kit and a new output directory, followed by `python3 polynomial_counts/audit/reconcile.py` for independent record reconciliation. Raw development failures are retained separately and are not hidden by the final successful build.

## Remaining gap and strongest safe statement

There is no remaining gap in the displayed fixed-presentation, one-step prime-field count theorem or its digit torsor and actual residue equivalences. `POLYNOMIAL_LIFT_COUNTS.md` and the new count entry in the cumulative checklist match the source, including the distinction between the explicit digit torsor and chosen-point equivalence for actual residue lifts.

Lifting through an infinite tower, arbitrary presentation invariance, native Conjectures 13.2/13.3, and the separate valuation refinements remain outside this theorem. A next block may impose surjectivity of the reduced Jacobian, prove it persists along the fixed residue class, and then construct compatible lifts through all levels. That further implication is not claimed here.
