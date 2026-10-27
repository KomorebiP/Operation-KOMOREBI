# Independent proof audit: Paper X, Block 20

The normalized target is an algebraic inverse theorem. In every unital, possibly
noncommutative rational algebra, the finite nilpotent exponential and the finite
unipotent logarithm are inverse on their respective loci. In characteristic-zero
linear representations, this recovers a globally nilpotent operator from one
nonzero unipotent sample, recovers both components of supplied reconstructed data,
and restricts actual intertwiners to the actual inertia-fixed monodromy kernels.

**Primary verdict: proved as written.** Raw mathematical review and the final
independent compilation of all ten new modules passed at their stated algebraic
scope. This audit does not certify the five full arithmetic claims.

## Exact claim and conventions

For an associative unital ring `A` with `Algebra ℚ A`, write

\[
\operatorname{Exp}(a)=\sum_{j<d}\frac{a^j}{j!},\qquad
L(u)=\sum_{j<d}\frac{(-1)^{j+1}}j(u-1)^j.
\]

The first formula uses any `d` with `a^d = 0`; the second uses any `d` with
`(u-1)^d = 0`. In Lean the coefficient for `j=0` in the logarithm is exactly zero,
because division by zero in ℚ is zero. The definitions choose the nilpotency class,
and theorems prove independence from any larger valid annihilating exponent.
No interpretation is assigned to the definitions away from these loci.

The source proves `L(Exp(a)) = a` and `Exp(L(u)) = u`. It also proves equality of
the complete sets of annihilating exponents, hence equality of nilpotency classes.
The equivalence of the two loci is a **set equivalence**. It is not a group
isomorphism or an exponential product formula for noncommuting arguments.

For a field `K` of characteristic zero and an arbitrary `K`-vector space `V`,
`expN N t = Exp(t • N)` and `recoverN t U = t⁻¹ • L(U)`. The rational algebra
structure on `End_K(V)` is induced by the canonical map `ℚ → K`; the displayed
polynomial is also proved with coefficients in `K` itself. If `N^d=0` and `t≠0`,

\[
N=t^{-1}\sum_{j<d}\frac{(-1)^{j+1}}j
       \bigl(\exp(tN)-1\bigr)^j.
\]

No finite-dimensionality assumption is used here. Nilpotence is global per
operator: a single finite exponent kills that operator on the entire space.
The results do not assert the corresponding statements for merely locally
nilpotent operators without a common exponent.

For reconstruction, `D` and `E` have the same coefficient field `K`, group `G`,
unit-valued character `ν`, and twisted cocycle `t`, with

\[
r(g)N=\nu(g)Nr(g),\qquad
t(gh)=t(g)+\nu(g)t(h),\qquad
\rho(g)=\exp(t(g)N)r(g).
\]

Under a common supplied sample `u` with `r_D(u)=r_E(u)=1` and `t(u)≠0`, a
`K`-linear map intertwines the reconstructed actions if and only if it intertwines
both original actions and both monodromy operators. The map need not be invertible,
and the two spaces and nilpotence orders may differ.

`FiniteSampleRecovery` derives that common sample from weaker finite-action
hypotheses. If `ν(u)=1`, `t(u)≠0`, and both original action values have finite order,
positive orders `d,e` give the sample `u^(d*e)`. Its cocycle value is
`(d*e : K) * t(u)`, which is nonzero. Finite actual image of each original action
on a subgroup containing `u` supplies finite order. Neither the subgroup nor the
ambient group is assumed finite. The finite-image hypotheses are about actual
representation values, not labels assigned to a local packet.

For a reconstructed linear equivalence, restriction gives an actual equivalence
between `ker N ∩ V^H`. A normal subgroup and finite-dimensional spaces are added
for the characteristic-polynomial conclusion concerning the actual restricted
action of the supplied element `φ`. No arithmetic meaning of `G`, `H`, or `φ`
is asserted by those types.

## Dependency graph

1. Mathlib's finite nilpotent exponential and rational-scalar map identities
   supply the exponential definition, nilpotence of `Exp(a)-1`, and naturality.
2. Mathlib's formal power-series substitution and formal exp/log inverse
   identities are evaluated at a nilpotent constant. `NilpotentSeries` proves
   that this evaluation is precisely a finite sum.
3. `CommutativeLogarithm` proves both inverse identities in a commutative rational
   algebra. `NilpotentLogarithm` applies them inside the singleton-generated
   commutative subalgebra and transports the equalities to the ambient ring.
4. `LogarithmicRecovery` uses a common maximum of two annihilating exponents to
   prove naturality for rectangular linear maps. Scalar cancellation gives
   sample recovery, intertwiner equivalence, and exact fixed-space equality.
5. `GeneralReconstructionRecovery` evaluates an intertwiner at the common sample,
   then cancels inverse exponentials to recover the original action. Existing
   `WeilMorphisms` restricts the resulting actual maps to independently defined
   fixed kernels and conjugates their restricted operators.
6. `LogarithmTruncation` independently factors a polynomial without a constant
   term as `a*b`, with `b` commuting with `a`. This preserves every supplied
   annihilating exponent, then the inverse identities prove equality of classes.
7. `FiniteSampleRecovery` derives finite orders from finite image using a collision
   of positive powers and cancellation by a unit. It then constructs the common
   positive power and applies the general intertwiner equivalence.
8. `GeneralLogarithmExamples` supplies every affine chain length, including zero,
   a sixth-order example, the formerly failing quartic case, and a zero-parameter
   failure. `GeneralRecoveryBoundary` supplies the separate missing-original-action
   counterexample.

All leaves in this graph are checked project/Mathlib theorem dependencies or
explicit hypotheses. The numerical experiment is not a proof leaf. No analytic
convergence assertion or external unformalized arithmetic theorem is used.

## Obligation matrix

| Obligation | Result | Decisive evidence |
|---|---|---|
| Finite logarithm has the intended coefficients | Passed | `log_eq_sum`, explicit `j=0` case, and `log_polynomial` |
| Ambient endomorphism rings need not commute | Passed | Final hypotheses are `Ring A`, `Algebra ℚ A`; commutativity occurs only in the singleton-generated subalgebra |
| Formal substitution has legitimate inputs | Passed | Nilpotent constant coefficients give `HasSubst`; evaluation reduces to finite sums |
| Both exp/log inverse directions | Passed | `NilpotentLogarithm.log_exp`, `exp_log`, and `nilpotentEquiv` |
| Original cutoff and exact nilpotency class retained | Passed | Zero-constant-term factorization and the two power-vanishing equivalences |
| Canonical scalar action and nonzero normalization | Passed | Algebra induced by `ℚ → K`; field-coefficient polynomial identity; `t ≠ 0` retained |
| Unequal dimensions and nilpotence orders | Passed | Common maximum in the proof; nonzero 2-to-3 dimensional audit application |
| Zero ring, exponent zero, and zero module | Passed | No hidden nontriviality assumptions; separate compiled boundary applications |
| Infinite-dimensional module permitted | Passed | Separate unrestricted `End_ℚ(ℕ → ℚ)` application |
| Reconstruction uses the correct factor order | Passed | Inherited definition is `exp(tN) * r`; recovery cancels that factor |
| Common sample derived from finite original action | Passed | Positive `d*e`, characteristic-zero nonvanishing, and unit cancellation from actual group actions |
| Local invariant spaces are actual subspaces | Passed | `fixedKernel = ker N ⊓ inertiaFixed`; actual restricted linear equivalence |
| Characteristic polynomial has its needed hypotheses | Passed | Finite dimensions, normal `H`, actual restricted action, same coefficient field |
| Zero sample may be omitted | Failed; counterexample proved | `general_zero_parameter_recovery_fails` |
| Original sample action may be arbitrary | Failed; counterexample proved | `identical_reconstruction_different_monodromy` |
| Arbitrary arithmetic attachment or coefficient/period comparison | Out of scope | No theorem instantiates the missing arithmetic structures |

## Boundary interpretation

The old quadratic logarithm fails on a chain of length four, while the full finite
logarithm now recovers it. Chains of length six are also recovered and have
`N^5 ≠ 0`, `N^6 = 0`. Thus the new statement really exceeds the predecessor's
cubic restriction.

The new absorbed-action construction replaces `(r,N)` by `(ρ,0)`. Reconstruction
then gives the same `ρ`, even at a nonzero cocycle sample, but monodromy differs.
The source separately proves that the absorbed original action at that sample
is nontrivial. This is an algebraic counterexample in the declared `Datum` class.
The absorbed action may have infinite unipotent inertia. It is **not** a
counterexample to uniqueness for attached arithmetic Weil–Deligne data satisfying
additional finite-inertia requirements. The finite-image recovery theorem gives
the corresponding positive result under its explicit sample and norm hypotheses.

## Verification and provenance

Final evidence is recorded in `checks/logarithm_audit/compile.json` and
`LOGARITHM_PROOF_AUDIT_SOURCES.json`. The independent runner recompiles each new
module into a temporary cache, links only established predecessor objects, and
then checks the separate boundary applications against the newly compiled
objects. Temporary proof objects are discarded. The runner requires warnings
to be errors and requires unchanged hashes for every new source.

The accepted run compiled all ten production sources and the separate audit
application file successfully. All ten source hashes were unchanged throughout
that run and match the source manifest. The manifest also pins the 32-file
internal project dependency closure and eight directly inspected Mathlib source
files; hashing that closure is provenance, not a claim to have reaudited every
predecessor proof.

The separate boundary file checks an arbitrary noncommutative rational algebra,
the zero ring at exponent zero, preservation of that zero cutoff, a zero module,
an unrestricted infinite-dimensional module, and a nonzero inclusion between
two- and three-dimensional chains with nilpotence orders two and three. Printed
transitive axioms are restricted to `propext`, `Classical.choice`, and `Quot.sound`.

Reproduce with:

```sh
python3 checks/logarithm_audit/run.py /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/logarithm_audit/source_manifest.py /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Two intermediate audit runs were not accepted as final evidence. The first
resolved the `PaperX` namespace to the temporary cache and could not find a
predecessor object. Linking the predecessor objects explicitly repaired the
runner. The next run compiled all then-current nine modules and the boundary
file, but its source-stability guard detected an edit to a production source
during compilation. It was rejected and repeated after a source freeze. The
failure records are retained. Neither event was treated as a successful stable
verification. A transient execution transport failure also required a retry.

Primary source checks used the pinned local Mathlib source files for nilpotent
exponentials, formal logarithms and substitution, rational algebra structures,
singleton-generated commutative subalgebras, and finite element orders. No theorem
was accepted from a web snippet or merely from a mathematical name. The entire
cumulative rebuild and archive replay are separate release checks; this audit
does not claim to have independently rebuilt all predecessor modules.

## Remaining implication and strongest safe statement

The general finite logarithm, nonzero-sample extraction, recovered original
intertwiners, and finite-original-image sample reduction are established at their
declared algebraic scope. This removes the cubic extraction restriction and,
under finite original image, derives triviality at a suitable powered sample.

It still does not construct an attached Weil–Deligne representation for an
arbitrary arithmetic Galois representation, prove existence and normalization
of the intended arithmetic cocycle/sample, identify coefficient-field transports,
or prove Hodge–Tate and period comparisons. The five full arithmetic claims must
retain their partial status. The next claim-level check should instantiate the
finite-image sample theorem with the manuscript's actual local groups and its
actual tame character, before promoting any arithmetic ledger entry.
