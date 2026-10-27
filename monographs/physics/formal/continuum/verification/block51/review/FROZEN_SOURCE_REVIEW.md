# Frozen-source semantic review

**Primary verdict: proved as written.** The four frozen modules implement
the scoped PHYS-CENT-51 target with the required objects, quantifiers,
domains, signs, constants, and Fourier transport. No weakened, vacuous, or
silently substituted theorem statement was found.

The exact source hashes, reviewed snapshot, root target-contract identity,
and selected pinned Mathlib source identities are recorded in
`FROZEN_SOURCE_REVIEW.json`. This report supersedes the preliminary
source-review snapshot for the accepted four-file revision. It does not
erase the historical mathematical audit or its manuscript clarification.

## Dependency and coverage map

| Target | Actual declarations | Review result |
|---|---|---|
| Bounded centered multiplier on the existing infinite space | `boundedModewiseOperator`, `centeredCoeffOperator`, `centeredCoeffOperator_apply`, `centeredCoeffOperator_norm_le` | Pass. Uniform modal action is lifted to the actual `CoeffL2`; evaluation and the intended bound require nonzero spacing. |
| Hermitian/self-adjoint action | `hilbertSymbol_symmetric`, `centeredCoeffOperator_symmetric`, `centeredCoeffOperator_selfAdjoint` | Pass. Symmetry holds under the existing complex inner-product convention and produces bounded self-adjointness. |
| Exact Clifford difference norm | `centered_mode_sub_eq_symbol`, `norm_centered_mode_sub_sq` | Pass. Mass cancels and the three spatial residuals remain in quadrature. |
| Full graph-domain convergence | `centered_mode_tendsto`, `centered_graph_tendsto` | Pass. The modal limit is two-sided; the global limit is `𝓝[≠] 0` on every vector in the maximal domain. |
| All nonreal resolvents | `shifted_isUnit`, `modalResolvent`, `continuumCoeffResolvent`, `centeredCoeffResolvent` | Pass. Existence follows from the actual self-adjoint spectrum theorem, not an assumed inverse. |
| Inverse and range-domain laws | `continuumCoeffResolvent_mem_domain`, `continuum_shift_resolvent`, `continuum_resolvent_shift`, and centered counterparts | Pass. Both inverse directions are proved; continuum range membership comes from `Hg=f+zg`. |
| Nonreal norm and graph-error bounds | `modalResolvent_norm_le`, coefficient norm bounds, `centered_resolvent_error_le` | Pass. The absolute imaginary part is retained and both half planes are covered. |
| Strong resolvent convergence | `centered_resolvent_tendsto` | Pass. Every coefficient vector and every nonreal complex parameter, in the two-sided punctured limit. |
| Exact third spatial moment | `thirdOrderWeight`, `HasThirdOrderMoment`, `thirdOrderMoment`, `HasThirdOrderMoment.mem_continuumDiracDomain` | Pass. Finiteness is actual summability; the same hypothesis supplies a valid continuum-domain witness. |
| Global generator rate | `sinQuot_cubic_bound`, `centered_generator_quadratic_bound` | Pass. The coefficient is exactly `h²/6`; mass is unrestricted and the original infinite space remains unchanged. |
| Noncommutative propagator estimate | `modal_interpolation_hasDerivAt`, `modal_perturbation_bound`, `centered_propagator_quadratic_bound` | Pass. The differentiated product preserves operator order. No cross-commutation premise occurs. All real times are covered. |
| Compact time | `centered_propagator_compactTime_bound` and physical counterpart | Pass. The statement is uniform over `t ∈ [-T,T]` and explicitly includes `T ≥ 0`. |
| Actual physical torus transport | `physical_centered_graph_tendsto`, physical inverse/domain/norm/error/limit lemmas, and physical rate lemmas | Pass. All use the existing surjective Fourier isometry and actual physical Hamiltonian domain. |

## Critical proof checks

The graph-limit dominator is `2‖Hf(n)‖`, whose square is summable because
`f` belongs to the actual maximal domain. This valid bound includes every
real mass and introduces no higher regularity assumption. Continuity of
the filled sine quotient is proved through `sinc`, so the result does not
quietly inherit only the predecessor's positive-spacing limit.

The resolvent construction uses `Ring.inverse` only with a separately proved
unit property for `A-zI`. The modal lower bound derives from the imaginary
part of `⟪v,(A-z)v⟫`; the absolute value prevents a hidden upper-half-plane
restriction. The global inverse lives in the maximal continuum domain
because its Hamiltonian coefficients equal those of `f+zg`. The resolvent
identity has the correct `(H-H_h)` order and sign.

The third-order moment is the homogeneous spatial sixth-power weight from
the manuscript. It is not an arbitrary auxiliary norm or a finite truncation.
The implementation requires its summability before comparing infinite sums.
The elementary bound `x²≤1+x⁶` proves domain membership. A totalized `tsum`
alone is never used as evidence that the moment is finite.

The interpolation `U_A(t-s)U_B(s)` differentiates to
`i U_A(t-s)(A-B)U_B(s)`. Each Hamiltonian is commuted only with its own
exponential, where appropriate. The mean-value inequality on all of the
real line gives `|t|`; it does not impose nonnegative time or conceal a
commutation assumption. Squared modal bounds are summed using the actual
convergent moment series.

The pinned Mathlib leaves inspected directly include the global real sine
remainder `Real.abs_sub_sin_le`, real spectrum of a self-adjoint element,
and the norm mean-value theorem used by the modal argument. Their types
match the uses made in these modules.

## Zero-spacing conventions

`centeredCoeffOperator m 0` is deliberately the auxiliary zero bounded
operator. The actual centered modal symbol has continuum fill at zero and
cannot be lifted there to an everywhere-defined bounded Hamiltonian.

`centeredCoeffResolvent m 0 z hz` instead uses the continuum modal inverse,
and the centered propagator at zero agrees with continuum evolution. These
are compatible choices for their separate families, but they are not the
resolvent or evolution of the auxiliary bounded zero operator at zero.
Every inverse identity involving `centeredCoeffOperator` explicitly retains
`h ≠ 0`. Every graph limit is punctured. No false zero-spacing identification
was found.

## Evidence and acceptance boundary

The reviewer read the four frozen source files and the producer's successful
strict compilation receipts. The reviewer did not execute a second Lean
run. Root's fresh compilation, all-declaration recursive axiom audit,
positive and negative controls, kernel replay, and exact delivery binding
remain distinct acceptance evidence. This report does not predeclare their
outcomes.

The constant `1/6` is retained in the proved bounds. There is no separate
formal theorem asserting that no smaller uniform constant is possible.
The compact-time interface proves a pointwise uniform bound over the
interval, which is the contract's requested uniform form; it is not a
separate Lean statement about a particular totalized supremum operator.

## Remaining gap and safe conclusion

No semantic gap remains in the reviewed PHYS-CENT-51 statements. Release
acceptance still depends on the separate fresh verification gate and its
unchanged-source binding. Abstract unbounded spectral-functional-calculus
linkage, sampled-lattice comparison, interactions, historical whole-physics
verification, and cosmological production remain outside this result.

Review provenance: independent subagent source audit, tied to the four
frozen hashes. The report makes no claim of independent empirical
confirmation or use of a second proof assistant.
