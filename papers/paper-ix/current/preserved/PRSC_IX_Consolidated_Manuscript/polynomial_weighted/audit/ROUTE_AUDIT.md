# Independent weighted lifting audit

Reviewer: independent boundary and route audit agent. Author: Komorebi P.

## Exact claim and current verdict

The target is `polynomial_weighted/TARGET_CONTRACT.json`: for prime `p`, a finite square polynomial system `F` over the actual ring `Z_p`, a base point `a` in `Z_p^d`, natural numbers `s,r` with `r > 2s`, and an integral matrix `A` satisfying

\[
A\,DF(a)=DF(a)\,A=p^sI,
\]

the residual hypothesis `F(a) in p^r Z_p^d` implies exactly one zero in `a+p^(s+1) Z_p^d`, and its displacement is in `p^(r-s) Z_p^d`. The written inverse formulation additionally specifies that `DF(a)` is invertible over `Q_p` and `p^s DF(a)^(-1)` is integral.

**Primary verdict: proved as written.** The final raw theorem `PolynomialWeightedLift.exists_unique_weighted_root` and the entire five-module proof chain have now been read independently. The full coefficient domain, actual derivative, original root equation, uniqueness ball, and refined precision match the target. The final module passed its development compilation (`dev/lift/attempt_02.log`, exit 0 reported and source hash reconciled below). The fresh cumulative release gate also passed, and its source, log, compiled-file and axiom-closure evidence has been independently reconciled below.

## Dependency graph

1. Actual polynomial partial derivatives define `J=DF(a)`.
2. Integral matrix multiplication preserves coordinatewise divisibility, and the certificate `JA=p^sI` makes multiplication by `A` injective.
3. An identity of actual polynomials gives
   \[
   F(a+p^{s+1}u)=F(a)+p^{s+1}Ju+p^{2s+2}Q(u),\qquad Q(0)=0.
   \]
4. Applying `A` and using `AJ=p^sI` gives
   \[
   A F(a+p^{s+1}u)=p^{2s+1}\bigl(c+u+pH(u)\bigr),
   \]
   where `H=AQ`, `H(0)=0`, and `AF(a)=p^(2s+1)c`.
5. Every integral polynomial system is nonexpanding for the supremum p-adic metric. Thus `u -> -c-pH(u)` is a strict contraction of the complete space `Z_p^d`.
6. Banach's fixed point theorem yields a unique `u`. Nonzero scalar cancellation and injectivity of `A` identify its fixed point equation with the original equation `F(a+p^(s+1)u)=0`.
7. For `k=r-(2s+1)`, the constant `c` lies in `p^k Z_p^d`. The identity `H(0)=0` and polynomial congruence imply by induction that a fixed point is divisible by `p^n` for every `n<=k`. Multiplying by `p^(s+1)` gives `s+1+k=r-s` digits of displacement precision.

All polynomial, matrix and precision leaves are internal proof obligations. The fixed point existence leaf is the exact local Mathlib theorem described below. No finite experiment is used to establish the universal lifting claim.

## Obligation matrix

| Obligation | Status at route review | Reason |
|---|---|---|
| Coefficients and base point are arbitrary p-adic integers | Passed in target and inspected component definitions | `MvPolynomial (Fin d) Z_p` and `Fin d -> Z_p`, without integer truncation hypotheses. |
| The derivative is the actual polynomial Jacobian | Passed in inspected inverse component | `jacobian F a` is evaluated `pderiv`, rather than a separately assumed linear map. |
| Both matrix directions have a purpose | Passed | `AJ` normalizes the linear term, `JA` supplies injectivity of `A`. |
| Polynomial remainder exists before the evaluation point is chosen | Passed in inspected Taylor component | `exists_scaled_remainder` constructs one polynomial `Q` and `exists_eval_scaled_remainder` quantifies over every `u`. |
| Constant term of the remainder vanishes | Passed | Explicit `eval 0 Q=0`, needed for arbitrary retained precision. |
| Strict depth and integer subtraction | Passed in final theorem | `r>2s` gives `r>=2s+1` and `r-s>=s+1`. |
| Contraction and completeness | Passed in inspected contraction component | Actual polynomial congruence/norm proof, with complete finite product of `Z_p`. |
| Uniqueness throughout the claimed large ball | Passed | An arbitrary original root `z` is represented by shift coordinates using only the large-ball divisibility assumption; unique fixed-point coordinates give `z=b`. The stronger precision bound is not assumed for competing roots. |
| Full original root equation, rather than preconditioned equation only | Passed | `precondition_root_iff` and nonzero scalar cancellation give an actual equivalence between `F(shiftedPoint w)=0` and the fixed-point equation. |
| Translation of the written `Q_p` inverse hypothesis | Passed in inspected inverse component | `integral_inverse_iff_certificate` under `IsUnit` for the rational matrix. |
| Dimension zero, `s=0`, `r=2s+1`, `p=2` | Passed route check | No division by dimension or by 2. The minimal depth has `k=0`, so refined precision equals the large ball. |
| General rationally rank-deficient singular systems | Out of scope | The effective inverse certificate excludes them. |
| Sharp residual threshold and displacement depth | Passed in independent Lean controls | See below. |

## Decisive independent controls

`controls/PolynomialWeightedControls.lean` has two definitions and nine theorems. It passed with the pinned Lean 4.34.0-rc2 runtime, one thread, warnings as errors, and default heartbeat limits.

* `squarePlusThree` is the actual polynomial `X^2+3` over `Z_2`. At `a=1`, its residual is exactly `4` and derivative exactly `2`. The scalar certificate `A=1` has `s=1`. Thus the residual depth is exactly `r=2=2s`.
* `boundary_no_mod_eight` exhausts the eight elements of `ZMod 8` with kernel-checked `decide`. `boundary_no_padic_root` maps an alleged actual p-adic root through `PadicInt.toZModPow 3` to contradict that theorem. The finite check is used only after this exact reduction.
* For `F(X)=p^s X`, perturbation by `p^M` has the actual root `-p^(M-s)` when `s<=M`. The displacement is divisible by `p^(M-s)` and is not divisible by the next power. This includes every `M>2s` in the target regime and proves that a uniform extra displacement digit would be false.

The first clean control log is `dev/controls/attempt_03.log` (exit 0, empty diagnostic output). A direct existence-form corollary `boundary_no_root` was then requested by the gate author, added without changing the previous claims, and passed in `dev/controls/attempt_04.log` (exit 0, empty diagnostic output). Attempt 01 failed to normalize a ring-hom numeral and a p-adic power numeral. Attempt 02 failed the unnecessary sequence-focus linter under warnings as errors. Both were corrected without changing any control's mathematical claim. No false counterexample or changed theorem hypothesis was used to obtain the clean result.

Control command:

```text
LD_PRELOAD=<kit>/compat/app_path.so TMPDIR=/dev/shm \
python3 polynomial_weighted/scripts/check_low_memory.py \
  --kit <kit> --threads 1 --timeout 240 \
  --import-dir /dev/shm/paper9_weighted_build \
  --output /dev/shm/paper9_weighted_build/PolynomialWeightedControls.olean \
  polynomial_weighted/controls/PolynomialWeightedControls.lean
```

## Exact local source checks

Pinned Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

* `Mathlib/Topology/MetricSpace/Contracting.lean`: `ContractingWith` means a Lipschitz bound with constant strictly below one. `fixedPoint`, `fixedPoint_isFixedPt`, and `fixedPoint_unique` require a nonempty complete metric space. The inspected section is the metric-space theorem, so no infinite-distance exceptional case is omitted.
* `Mathlib/NumberTheory/Padics/PadicIntegers.lean`: `PadicInt.completeSpace` comes from the closed unit ball of `Q_p`; `nonarchimedean` is the maximum bound; `norm_lt_one_iff_dvd` supplies strict contraction for multiplication by `p`.
* `Mathlib/LinearAlgebra/Matrix/NonsingularInverse.lean`: `isUnit_iff_isUnit_det`, `mul_nonsing_inv`, and `nonsing_inv_mul` identify the actual nonsingular inverse under matrix invertibility. `mulVec_injective_iff_isUnit` applies to finite square matrices over the field `Q_p` and makes the effective certificate imply rational nonsingularity.
* The original written bridge was read in full through sections 1–4 and the relevant parameter/obstruction context. Its later first-order displacement and parameter claims are not being certified by this weighted lifting block.

The local primary source copies were available, so no internet source retrieval was required. No novelty claim is made.

## Final raw-proof review

The final theorem has been inspected directly, rather than inferred from a title or a dashboard:

* `PolynomialWeightedNormalization.exists_normalization` applies the proved Taylor identity to the actual preconditioned system. Its constant is constructed as `p^(r-(2s+1)) D`, so its claimed precision is explicit. All exponent identities use `r>2s`.
* `PolynomialWeightedLift.exists_root_of_normalization` proves the original-root/fixed-point equivalence at every shift coordinate. It then proves existence, refined precision, and uniqueness for every original root in the full large ball. The normalization hypothesis belongs only to this helper.
* `PolynomialWeightedLift.exists_weighted_root_certificate` constructs the normalization from the actual polynomial and actual Jacobian. No remainder estimate, contraction property, or pre-existing root is assumed in this theorem.
* `PolynomialWeightedLift.exists_weighted_root` uses `bounded_inverse_iff_certificate`, which includes the equivalence of rational nonsingularity and the explicit integral inverse bound with the effective certificate. The chosen denominator exponent `s` is unchanged.
* `PolynomialWeightedLift.exists_unique_weighted_root` asserts unique existence with the predicate consisting only of the original root equation and depth-`s+1` ball membership. A separate universal implication gives depth `r-s` for every root in that ball.

The algebraic signs are consistent: normalization `C+u+pQ(u)=0` becomes `u=-C-pQ(u)` by choosing the fixed-point data `c=-C`, `H=-Q`. The large ball parametrization is surjective by divisibility witnesses, so no integral root in that ball is omitted. Nonzero powers of `p` are cancelled only in integral domains. The strict-depth counterexample and the exact linear displacement control remain compatible with the final contract.

## Frozen source and source-leaf hashes

The exact reviewed bytes are recorded in `audit/REVIEWED_SOURCES.json`. In particular, the main theorem hash is `8b30f4b2015e6f12cabdb123972ef5b40378034c5c3b8f7947336a2307148845`, matching the author's freeze notice. Controls hash is `88fea6bc068832ba84339af00cd98b0f9b458219dd3df71c1578f445cb7fdf04`.

## Final release reconciliation

`audit/reconcile_review.py --gate-dir /dev/shm/paper9_weighted_fresh_01` passed. The fresh report is `PASS`: all 50 checks passed in 189.611 seconds. Its SHA256 is `d019246cfe16174093f0dd6756699e64f2eea4bb8c7f67793de1bac34a5599ea`.

The independent reconciliation matched all 47 inventoried source/contract/control files, 205 compiled output files, and all 50 run logs. It re-parsed the actual axiom-audit compiler output independently and matched all 304 declaration closures, using only `propext`, `Classical.choice`, and `Quot.sound` (or subsets). All 25 inherited mathematical source files remained byte-identical to their recorded baseline hashes. The current positive compilation set has 41 modules: 30 mathematical modules, three control support modules and eight statement-contract modules. Its declarations total 246 theorems, 54 definitions and four abbreviations. These are counts for this gate, not the number of distinct theorems across all historical Paper IX releases.

The five new mathematical modules contain 37 theorems and seven definitions. The two new expanded contract modules were read directly and match the actual polynomial Jacobian and rational inverse target without adding normalization or contraction hypotheses. Six intentionally invalid control files were rejected with the expected type-mismatch diagnostics; their associated positive controls provide the actual mathematical counterexamples.

The exact reconciliation result and hashes are in `audit/reconciliation.json`; `audit/REVIEWED_SOURCES.json` pins that record and the report. No additional compilation was run by this reconciliation, and no independent Lean kernel implementation is claimed. There is no mathematical gap in the stated weighted lifting target identified by this review. General singular lifting, weighted parameter deformations, first-order root-motion remainders, analyticity, and global descent remain outside this theorem. Metadata or agreement among agents does not replace raw proof inspection.
