# Actual group actions induce honest scalar lifts

The module `formalization/PaperXI/ActualScalarLift113.lean` constructs the
scalar-pushout action required by `CyclicDefect113` from an actual group
automorphism. It does not assume a section phase, its multiplication law, or
its cyclic norm. All three follow from the same original character and actual
action.

## Precise input and output

Let G be a group, D a normal subgroup, A an abelian group, and
q : G → A a homomorphism with literal kernel D. Supply a normalized section
t : A → G, with q(t(a)) = a and t(1) = 1. Supply the original character
θ : D → C×, invariant under G-conjugation.

Suppose α is an automorphism of G and β an automorphism of A with
q(α(g)) = β(q(g)). The module derives the homomorphism α_D : D → D from this
equality and the exact kernel. The remaining character hypothesis is exactly
θ(α_D(d)) = θ(d). It is an invariance hypothesis about the actual character,
not about a phase function or a scalar-cocycle comparison.

Using the preceding continuation's definitions, put

λ(g) = θ(g t(q(g))⁻¹),
c(a,b) = λ(t(a)t(b)),
ℓ(a) = λ(α(t(a))).

The expressions inside θ are literal elements of D. The new theorems derive

λ(α(g)) = λ(g) ℓ(q(g)),

c(a,b) ℓ(ab) = ℓ(a) ℓ(b) c(β(a),β(b)).

The proof of the first identity writes g as its D-valued section residue
times t(q(g)), applies α, and uses preservation of the original θ. The second
identity follows by applying the first to t(a)t(b) and using the existing
section multiplication identity.

Consequently

L(z,a) = (z ℓ(a), β(a))

is an actual automorphism of the scalar pushout extension E_c. It fixes all
complex scalars and covers β. Its explicit inverse is

L⁻¹(z,a) = (z / ℓ(β⁻¹(a)), β⁻¹(a)).

The actual pushout homomorphism Q(g) = (λ(g),q(g)) satisfies

Q(d) = (θ(d),1),  Q(t(a)) = (1,a),  L(Q(g)) = Q(α(g)).

If αⁿ = 1, the module proves both βⁿ = 1 and Lⁿ = 1. The second proof uses
the intertwining equality on Q(G) and the fact that every pushout element is
a scalar times Q(t(a)). No independent phase-period assumption remains.
`CyclicDefect113.ScalarLift.norm_eq_one` now gives the norm-one phase identity
as a direct consequence.

## Export inventory

There are 15 explicit declarations, comprising 4 definitions and 11 theorems.

- `actualPushout`, `actualPushout_section`, `actualPushout_subgroup`
- `quotient_action_power`, `quotient_power_eq_one`
- `subgroupMap`
- `actualPhase`, `actualPhase_one`, `sectionScalar_action`, `actualPhase_mul`
- `actualLift`, `actualLift_phase`, `actualLift_intertwines`
- `actualLift_power_intertwines`, `actualLift_power_eq_one`

The theorem `quotient_power_eq_one` takes the section, quotient action
compatibility, and αⁿ = 1. It has no subgroup or character assumptions.
The remaining action theorems retain θ and the specified q, t, α, β.

## Scope and remaining arithmetic obligation

No finiteness assumption is needed for this adapter. In the intended
application, it can be instantiated on the actual finite quotient of J¹ by
ker(θ), with the original action descending to that quotient. The existence
of this arithmetic quotient, its correct labels, its compatible character,
and its full action remain prerequisites.

The construction supplies the honest scalar lifts needed by the coprime
cyclic cochain correction. It does not produce a simple stratum, prove that
arbitrary break packets have a common arithmetic realization, identify a
prescribed β-extension, prove original H5, or close Claim 16.2. Paper XI's
overall count remains 65/66.

## Verification and failures retained

Final source SHA-256:
`9dca2abac60d683f19c4b2bd2bd257b8f18e5b5f459cf39df9948de4ccf41ce0`.

Attempt 04 compiled with warnings treated as errors. All 15 exports were
checked with `#print axioms`, and the completed module passed independent
`leanchecker`. The only reported axioms were `Classical.choice`, `Quot.sound`,
and `propext`. The imported baseline objects were reused and were not rebuilt.

Receipts, source snapshots, and logs are under `evidence/actual_adapter`.
`ACTUAL_ADAPTER_AUDIT113.json` records the module and object hashes and the
audit exit codes.

Attempt 01 failed on a dependent rewrite of subgroup membership, after which
Lean dropped parameters in subsequent malformed declarations. It also
exposed two insufficiently unfolded scalar projection goals. Attempt 02
resolved these issues but an induction inherited the unrelated αⁿ = 1
hypothesis, and a local cocycle abbreviation prevented one simplification.
Attempt 03 compiled after separating the scalar-fixing induction and making
the relevant cocycle expression explicit. Attempt 04 added and checked the
derived quotient-period theorems. These were implementation failures, not
counterexamples to the mathematical statements. All attempt logs are retained.
