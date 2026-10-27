# Absolute Frobenius existence: inventory and implementation

Status: proved in the actual ideal model; no valuation-model conversion is claimed.

## Exact objects

- `Qbar = AlgebraicClosure ℚ`.
- `GQ = Gal(Qbar/ℚ)`, definitionally the actual `Field.absoluteGaloisGroup ℚ`.
- `IntegralClosure = integralClosure ℤ Qbar`, with its inherited actual Galois action.
- A decomposition group is `MulAction.stabilizer GQ Q` for an actual maximal ideal
  `Q` of `IntegralClosure`. The action on ideals uses the `Pointwise` scope.

`AbsoluteIntegralFrobenius.exists_frobenius_at p Q` proves, for a rational prime p
and every actual maximal Q above (p), existence of an actual absolute Galois
σ stabilizing Q such that

    mk_Q (σ • x) = (mk_Q x)^p

for every algebraic integer x. The binder is the subgroup subtype, so stabilizer
membership is part of the constructed object. `exists_frobenius p` additionally
constructs Q. No hypothesis supplies an absolute Frobenius element or the
surjectivity of the decomposition-group residue action.

## Inputs found and used

All sources below are the pinned project-local Mathlib checkout
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

1. `RingTheory/Invariant/Profinite.lean`,
   `Ideal.Quotient.stabilizerHom_surjective_of_profinite`.
   This is the already-proved abstract residue-surjectivity theorem. It requires
   a profinite group acting continuously on a discrete ring, the fixed-ring
   predicate, and a prime ideal over the base ideal. Its assumptions were
   instantiated, not retained as new hypotheses.
2. `FieldTheory/Galois/IsGaloisGroup.lean`,
   `IsGaloisGroup.of_isGalois`, and
   `RingTheory/IsGaloisGroup/Basic.lean`,
   `IsGaloisGroup.of_isFractionRing`.
   These identify the fixed ring in the integral closure with ℤ. The latter
   theorem does not require the group or extension to be finite.
3. `RingTheory/Localization/Integral.lean`,
   `integralClosure.isFractionRing_of_algebraic`, and
   `IsFractionRing.comap_isAlgebraic_iff`.
   These supply the fraction-field and algebraicity instances for the actual
   integral closure, with injectivity derived from characteristic zero.
4. `FieldTheory/KrullTopology.lean`,
   `stabilizer_isOpen_of_isIntegral`, and
   `Topology/Algebra/MulAction.lean`,
   `continuousSMul_iff_stabilizer_isOpen`.
   These prove continuity of the actual action on the discrete integral closure.
5. `FieldTheory/Galois/Profinite.lean` supplies compactness of the actual Galois
   group, together with the existing Krull-topology group/disconnection instances.
6. `Ideal.exists_maximal_ideal_liesOver_of_isIntegral` and
   `Int.ideal_span_isMaximal_of_prime` construct the actual maximal ideal Q.

## Residue Frobenius construction

The implementation does not need a separate theorem identifying the residue
field with a named algebraic closure of F_p. Characteristic p is proved from
`Q.LiesOver (span {p})` and the nontrivial quotient field. The p-power map is
injective in that characteristic. To prove surjectivity, lift a residue element
to an algebraic integer b, choose y in Qbar with y^p=b, and apply
`IsIntegral.of_pow` to show y is an algebraic integer. Its residue is a p-th root.
This proves `PerfectRing (IntegralClosure ⧸ Q) p`.

`frobeniusEquiv` then gives the residue ring automorphism. Its compatibility with
the actual base quotient ℤ/(p) follows from preservation of integer casts. The
profinite residue-surjectivity theorem lifts this automorphism to the actual
decomposition group.

The alternative `FiniteField.frobeniusAlgEquivOfAlgebraic` route was inventoried
but not needed. No external theorem was inserted as an axiom.

## Verification and failures

- Production source: `lean/PaperX/AbsoluteIntegralFrobenius.lean`.
- Source SHA256: `5b65258e7664f6905c4164cfeaa35f8af0270fe78696c047601724c16422b8ed`.
- Proof object SHA256: `d3659d6375722266cdb7ef062ecb6fc96bd258721e87b7f873ca46d175d58262`.
- Production compiler: pinned Lean 4.34.0-rc2, `-DwarningAsError=true`.
- `frobenius_existence_attempt3.log` is the successful empty compiler log.
- The actual p=2 existence fixture in `frobenius_existence_api.lean` passes.
- `frobenius_existence_api.log` prints the exact public theorem signatures and
  checks all ten substantive named declaration dependencies. They use only
  `Classical.choice`, `Quot.sound`, and `propext`.
- Six theorem declarations, one named definition, three public abbreviations,
  three named supporting instances. Two anonymous local topology instances are
  also present; the cumulative project audit controls the authoritative count.

Initial probes failed on missing algebraicity/compactness instances, one guessed
argument name, and guessed APIs. Those were resolved by the actual APIs above.
Production attempts initially failed on the orientation of the `LiesOver`
equality, an unusable inferred characteristic instance, explicit arguments of
`mem_integralClosure_iff`, and the generic `map_intCast` name. The final proof
uses local explicit characteristic/perfectness instances. The first consumer
fixture lacked `open scoped Pointwise`; adding that scope resolved its ideal
action instance. Failed logs are retained alongside the passing logs.

## Exact remaining scope

This establishes existence of arithmetic Frobenius elements above individual
rational primes in the actual absolute ideal-decomposition model. It does not
establish arbitrary finite-quotient Frobenius coverage (Chebotarev). The separate
cyclotomic recognition theorem is needed to identify their restrictions with
the prime samples used by the restricted separator.

The prior valuation-ring model on `AlgebraicClosure ℚ_[p]` can be pulled back as
a valuation subring of Qbar using `ValuationSubring.comap` along the existing
closure embedding. Transferring residue characteristic and identifying this
valuation decomposition group with the actual ideal model has not been proved
in this module. This conversion is unnecessary for the present ideal-model
Frobenius existence theorem and is not silently assumed.
