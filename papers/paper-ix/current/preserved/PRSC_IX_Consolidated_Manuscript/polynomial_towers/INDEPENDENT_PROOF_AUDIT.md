# Independent proof audit: compatible polynomial towers and p-adic roots

Author: independent audit agent for Komorebi P.  
Date: 2026-09-08  
Primary verdict: **proved as written**, within the fixed finite polynomial presentation and the explicit nonsingularity hypotheses below.

This review read the actual new proof sources, their Taylor and residue-count dependencies, the relevant pinned Mathlib statements, and the final verification evidence. It did not author or repair the proofs. Evidence reconciliation passed independently of the gate's own report writer. It uses the same Lean kernel and installed Mathlib dependencies, not an independently implemented proof kernel.

## Normalized claim

Let (d,e\in\mathbb N), (F=(F_1,\ldots,F_e)\in\mathbb Z[X_1,\ldots,X_d]^e), and (x\in\mathbb Z^d). For a positive natural base (q), define the actual residue-ring Jacobian

\[
J_q(x):(\mathbb Z/q\mathbb Z)^d\longrightarrow(\mathbb Z/q\mathbb Z)^e,
\qquad
J_q(x)t=\left(\sum_{k=1}^d(\partial_kF_i)(x)t_k\right)_{i=1}^e\pmod q.
\]

If (L\ge1), (F(x)\equiv0\pmod{q^L}), and (J_q(x)) is surjective, then there is **one** sequence (z_n\in\mathbb Z^d), defined for all (n\in\mathbb N), such that

\[
z_0=x,\qquad F(z_n)\equiv0\pmod{q^{L+n}},\qquad
z_{n+1}\equiv z_n\pmod{q^{L+n}}.
\]

The sequence retains all earlier residues, and (J_q(z_n)=J_q(x)) for every (n). These integer statements include composite (q) and the degenerate case (q=1).

If (q=p) is prime, there is an actual point (a\in\mathbb Z_p^d) such that

\[
z_n\longrightarrow a,\qquad
p^{L+n}\mid a_i-z_{n,i}\quad(\text{in }\mathbb Z_p),\qquad F(a)=0.
\]

In particular, (a\equiv x\pmod{p^L}). At every stage, the number of **distinct residue classes modulo (p^{L+n+1})** solving (F=0) and reducing to (z_n\pmod{p^{L+n}}) is exactly

\[
p^{d-e}.
\]

Surjectivity also proves (e\le d), so the exponent has its usual nonnegative dimension meaning. The original finite obstruction group has cardinality one. The generic completion module proves uniqueness of the limit of a fixed compatible sequence. It does not claim uniqueness among all roots in the initial residue class.

## Dependency graph

1. Integer multivariable polynomial induction proves a true Taylor remainder divisible by the square of the shift. The directional term uses `MvPolynomial.pderiv`.
2. For (L\ge1), (2L\ge L+1), so the remainder vanishes at the next precision. Exact residual factorization gives the equation (\bar r+J_q(x)t=0).
3. Surjectivity supplies a finite digit (t) with (J_q(x)t=-\bar r). Its integer representative gives an actual next polynomial solution (x+q^Lt).
4. Polynomial congruence applied to every formal partial derivative proves equality of the reduced Jacobian after this correction.
5. Natural-number recursion on the subtype of roots with surjective Jacobian constructs a single compatible tower, beginning with the exact supplied integer vector.
6. Telescoping adjacent differences gives all earlier-level congruences and a constant reduced Jacobian.
7. For prime (p), integer divisibility gives p-adic norm bounds. The resulting sequence is Cauchy. Completeness of the actual p-adic integers gives its limit, and closed norm bounds retain every residue.
8. Evaluation of the original polynomials after coefficient casting is continuous. Their integer residuals tend to zero by diverging divisibility precision. Uniqueness of limits gives (F(a)=0).
9. The earlier digit-to-residue equivalence counts actual next residue classes. Surjectivity forces rank (e), reducing the previously proved (p^{d-\operatorname{rank}J}) formula to (p^{d-e}).

Leaves 1–6 and the bridges in 8–9 are internal Lean proofs. Completeness, norm/divisibility identities, continuous polynomial evaluation, and finite-dimensional cardinality facts are pinned Mathlib results whose required forms were checked locally. No external conjecture or numerical experiment is a premise.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Actual polynomial system, coefficient ring and derivatives | Passed | `evalSystem`, `digitJacobian`, `padicEval`, plus the fully expanded capstone contract. |
| Correct residual sign | Passed | The chosen digit maps to minus the reduced residual, giving `reduction r + J t = 0`. |
| Taylor remainder rather than an assumed linearization | Passed | `taylor_dvd` is polynomial induction; `taylor_step_dvd` uses (2L\ge L+1). |
| One initial surjectivity hypothesis | Passed | Only the initial hypothesis is an input to `exists_compatible_tower`; later surjectivity is constructed. |
| One compatible sequence, not separate existential roots | Passed | Dependent `Nat.rec` selects the next state and retains its adjacency proof. |
| Initial integer point preserved exactly | Passed | `z 0 = x` is a conclusion proved by definitional equality. |
| Retention of lower and cross-level residues | Passed | `tower_pairwise_congruent` telescopes divisibility; `tower_initial_congruent` specializes to level zero. |
| Equality of actual reduced maps | Passed | `digitJacobian_eq` evaluates the formal derivative polynomials and proves equality coefficientwise. |
| Actual p-adic completion | Passed | `compatible_int_tower_cauchy` and `cauchySeq_tendsto_of_complete` produce a point of `ℤ_[p]`. |
| All precision bounds survive the limit | Passed | `le_of_tendsto` applies to eventually bounded norms; the norm/ideal equivalence returns p-adic divisibility. |
| Polynomial zero, not only limiting notation | Passed | `padicEval_intCast`, continuous evaluation, residual convergence to zero, and uniqueness of limits. |
| Count is of actual next residue classes | Passed | `ActualLifts` is a subtype of `ResidueFiber`; `digitEquivLifts` proves a bijection with valid correction digits. |
| Prime-field cardinality and dimension hypotheses | Passed | Count theorems require `Fact (Nat.Prime p)`; `smooth_dimension` separately proves (e\le d). |
| Composite and unit modulus scope | Passed | Integer tower requires only (q>0); p-adic completion and prime-field formulas are separate theorems. |
| Empty variable/equation sets | Passed | Finite function types and sums include dimension zero; impossible surjectivity when (e>d) is detected by the dimension theorem. |
| Uniqueness of all roots | Out of scope | The projection example explicitly refutes it for rectangular surjective Jacobians. |
| Arbitrary singular continuation | Out of scope | (X^2-5) at (p=2) lifts through modulus four but has no root modulo eight. |
| Independence under changes of presentation | Out of scope | The fixed polynomial list is retained throughout. |
| Global integral descent or native universal objects | Out of scope | Neither follows from a point of (mathbb Z_p^d). |
| Compilation, axioms and evidence hashes | Passed | Final fresh gate and independent reconciliation detailed below. |

## Counterexamples and boundaries

The checked positive controls prove the mathematical facts underlying all three rejected overstatements:

- (X^2-5): (1) is a root modulo two and four, but no integer is a root modulo eight. Therefore one successful singular step does not imply an infinite tower.
- (F(X_0,X_1)=X_0): the Jacobian is surjective, but ((0,0)) and ((0,2)) are distinct p-adic roots with the same residue modulo two. Surjectivity permits free coordinates.
- (X-2): zero is a nonsingular lower root modulo two, but its exact integer root is two, which does not retain residue zero modulo four. Only the prescribed initial precision is guaranteed.

The restriction (L\ge1) is substantive. A direct hand check gives (F(X)=X^2-X+1), (p=2), (x=0): the derivative at zero is a unit modulo two and every point is a root modulo (2^0=1), yet both possible residues evaluate to one modulo two. This boundary observation is not claimed as a new Lean declaration in this block.

A chosen tower and its unique limit do not establish a canonical choice of tower. Exact branching at each stage does not itself formalize the total number of descendants across several levels or a parametrization of all p-adic roots. These stronger statements remain separate tasks.

## Local source verification

The source scope was the project files and the authorized portable runtime, with Lean `4.34.0-rc2` and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. No search or novelty claim about the wider literature was made. This is a formal fixed-presentation lifting result; the audit does not assert a novel general Hensel theorem.

The following exact Mathlib leaves and their hypotheses were inspected in the pinned source:

| Source | Results used | Translation checked |
|---|---|---|
| `Mathlib/NumberTheory/Padics/PadicIntegers.lean` | `completeSpace`, `exists_pow_neg_lt`, `norm_int_le_pow_iff_dvd`, `norm_le_pow_iff_mem_span_pow` | Prime (p), actual closed unit ball in (mathbb Q_p), integer divisibility and p-adic principal ideals. |
| `Mathlib/Topology/UniformSpace/Cauchy.lean` | `cauchySeq_tendsto_of_complete` | Complete-space convergence is used only after the actual sequence is proved Cauchy. |
| `Mathlib/Topology/Algebra/MvPolynomial.lean` | `MvPolynomial.continuous_eval` | The target (mathbb Z_p) has the required topological commutative ring structure. |
| `Mathlib/Algebra/MvPolynomial/Eval.lean` | `eval_map`, `eval₂_comp` | Coefficients and integer coordinates are cast via `Int.castRingHom`; the original polynomial is retained. |
| `Mathlib/FieldTheory/Finiteness.lean` | `Module.natCard_eq_pow_finrank` | Applied to finite-dimensional modules over the actual field `ZMod p`. |
| `Mathlib/LinearAlgebra/FiniteDimensional/Lemmas.lean` | `finrank_range_add_finrank_ker` | Rank-nullity uses the finite-dimensional source. |
| `Mathlib/LinearAlgebra/Dimension/RankNullity.lean` | `Submodule.finrank_quotient` | Quotient dimension is codomain dimension minus image dimension. |
| `Mathlib/LinearAlgebra/Dimension/StrongRankCondition.lean` | `LinearMap.finrank_le_finrank_of_surjective` | Surjectivity yields the separate dimension bound (e\le d). |

## Verification and reconciliation

The final gate completed successfully in **78.188 seconds**:

- 14 project modules freshly compiled, including eight preceding dependency modules and six modules added for this block.
- Three statement-contract files, containing five explicit contract theorems.
- Three intended mathematical negative-control failures.
- 22 gate checks total.
- 127 explicit declaration axiom audits: 98 theorems, 25 definitions, four abbreviations. These totals include dependency declarations and contracts; they are not 127 new theorems.
- Only `propext`, `Classical.choice`, and `Quot.sound` occurred in the checked transitive axiom closures.
- Warnings were treated as errors. The runtime and precompiled Mathlib were reused; no project compiled file was reused in this fresh gate.

Final report: `verification/polynomial_towers_verification.json` in the release archive (original working run: `replay_01/polynomial_towers_verification.json`).  
SHA256: `c2bbba3610fadf3b21369558be05cac749258a7a94dc2a7394ce40e9fa4fe86a`

Frozen inventory SHA256: `5bd15c29bacbddbeee736ec471bd33b1748399b48f327f8c3dd1b47b5ac93e3e`

The independent reconciliation checked all **20 source and control hashes**, **85 compiled-output hashes**, **22 log hashes and exit expectations**, and **127 complete explicit axiom reports**. It also checked the verifier, runner and scanner hashes, source inventory coverage, command source/output paths, fresh-compilation flags, and runtime version pins. The build outputs were regular files with no symlinks.

Reproduction commands, from this directory:

```bash
python3 scripts/verify_polynomial_towers.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /path/to/new_tower_run
python3 audit/reconcile_verification.py /path/to/new_tower_run/polynomial_towers_verification.json --output audit/reconciliation.json
```

Reconciliation requires the completed build directory from the run being reconciled. The archive preserves the evidence and regeneration scripts; regenerated compiler outputs need not be distributed.

The final gate passed after earlier development compilation failures. Those were Lean proof elaboration, namespace/tactic and unfolding issues; their logs are retained. The independent audit found no remaining mathematical gap in the final statements. A final passing run does not erase or conceal the development failures.

## Exact remaining gap and strongest safe conclusion

There is **no remaining implication missing from the normalized claim above**. A fixed finite integer-polynomial system with a surjective initial reduced Jacobian now has a Lean-checked compatible infinite tower and an actual p-adic root retaining the supplied residue, with exactly (p^{d-e}) available next residue lifts at every stage.

The unresolved broader tasks are unrestricted singular towers, presentation-independent native obstruction objects, the specified global/native completion and descent claims, and any additional uniqueness or parametrization theorem. Proving uniqueness in the square invertible-Jacobian case is a sensible next strengthening, but is not part of this audit verdict.
