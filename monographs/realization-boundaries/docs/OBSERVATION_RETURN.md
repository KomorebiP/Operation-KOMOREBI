# Reconstruction and categorical closure return

Base checkpoint: checked v0.6.0 archive, SHA-256
`032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Owned production source: `RealizationBoundaries/ObservationSystems.lean`.
Source SHA-256: `831fb20150c9783023a6e2450cbbefd3bd5d997dff0b2804d549fe332e2a4020`.

## Exact new mathematical contracts

* `official_completion_map_injective` uses Mathlib's official multiplicative
  `ProfiniteGrp.profiniteCompletion`. For arbitrary groups G and H, residual
  finiteness of H alone makes its action on Hom(G,H) injective. No abelian,
  continuity, countability, or residual-finiteness assumption on G is imposed.
* `residuallyFiniteCompletion_faithful` packages this as a `Functor.Faithful`
  instance on the full category of all residually finite groups.
* `pairedCompletionFunctor` is an actual functor from the induced full additive
  source category with all groups G_a and all abstract homomorphisms, to their
  actual canonical profinite completions. It is faithful and
  `pairedCompletionFunctor_not_full` proves it is not full.
* `boundaryCompletionFunctor_not_reflects_isomorphisms` proves failure of
  reflection on the enlarged full category consisting of the zero-subspace
  preimage (literally equal to D by the checked parent theorem) and every G_a.
  Its witness is the actual inclusion `bottomToPaired a`; its completion is
  proved equal to `commonCompletionEquiv` as a continuous additive map.
* `coordinateIndexFunctor_initial` proves categorical initiality of the actual
  finite-coordinate quotient-kernel subsystem in all finite quotient kernels.
  This is genuine inverse-system cofinality, not only a cardinal comparison.
* `coordinateObservationIso` constructs the natural isomorphism between that
  reindexed all-finite-quotient diagram and the common source-free diagram of
  finite coordinate groups, with the actual coordinate restriction maps.
* `FiniteObservation` stores a nonempty cofiltered finite-group diagram and no
  source group or named source points. `CommonCofinalObservation` requires a
  common nonempty cofiltered index, two categorically initial functors, and a
  natural isomorphism after reindexing. Every invariant of pro-object
  isomorphism must respect these certified comparisons.
* `no_unmarked_observation_decoder` excludes arbitrary decoders invariant under
  these actual cofinal comparisons from recovering every G_a. No computability
  or finite-description restriction is imposed. This closes the printed 9.1
  contract using the actual finite-quotient systems, not replacement completion
  inputs. It does not purport to implement every morphism of a universal Pro
  category; that extra infrastructure is unnecessary for the no-decoder result.

The printed three clauses of 9.3 and the exact no-decoder assertion of 9.1 are
therefore covered by these declarations and the accepted parent counterexamples.

## Verification

Pinned kit: `/workspace/scratch/ea498747acd5/runtime/parts/Komorebi_Portable_Lean_4.34.0-rc2`.
The compatibility preload was used with the unchanged project check script.
`ObservationSystems_014.json` records the final successful compiler run, exit
zero, warning-as-error and autoImplicit false, 3.66 seconds. Kernel replay of the
same final module exited zero; output is in
`verification/development/ObservationSystems_kernel_replay_final.log`.
These are development checks. Root's clean full verification must supply the
accepted integrated receipt. Earlier failed intermediate compilations remain in
the development evidence and are not claimed as accepted checks.

## Dependency hashes

* ClassificationConsequences.lean: `766a5d143fa6580de926dedef8a0d82f8f84aeb777cc2462d211670d7d9cba93`
* CompletionReflection.lean: `f46509bd9217931cb4f9c0347a09cbd07a6d1250a460f0617e0aa0809b12332a`
* ProfiniteCompletion.lean: `5333f11109f1a309db0b9749d017221e9839c902dd29fb56c307ab497863482c`
* FiniteQuotients.lean: `4c48fffef4ed0db07ff506afe0aea5338cc646431114ce8c9acf8d4ab032df8e`

## Additional exact closure of 3.2

Independent review identified that the original new subgroup module proved
uniqueness from all finite observations but did not explicitly package existence
for a compatible family of finite patterns. `ObservationPatternClosure.lean`
now defines actual compatible finite prime patterns, recovers the selector from
singleton patterns, proves each finite pattern is exactly its restriction, and
proves existence and uniqueness of the selector and resulting actual subgroup.
Its local compiler check passed with warning-as-error; root should include the
module in integrated verification and record the final hash.

## Subgroup topology addition

`SubgroupTopology.lean` now covers the unnumbered topology paragraph following
3.1. Its topology on the actual subgroup lattice is independently defined as the
initial topology of its actual membership function into `Bool^D`, with Bool
discrete. It is not pulled back from the spectrum classification. Forward
continuity follows by restricting each vector's membership question to its
actual finite support. Inverse continuity follows by evaluation at the actual
prime seeds. Both `Prime → Bool` and the printed `N → Bool` Cantor
parametrizations are supplied, using the actual increasing prime enumeration.

Source hash: `9d98d12b54b64d74bcde97cff3e6d2c42b592c79b43807d28a95d6719d91b4e6`.
The final local warning-as-error check passed, exit zero, 2.50 seconds. This is
self-review of the additional source, not independent review. Production source
is now frozen for root's integrated checks.

The coherent-pattern source hash is
`88220bfb2aa1cc68570a4ef322dcc785647e29165dc87eb28a7734a3f32a1991`.

Kernel replays of both additional sources exited zero:
`ObservationPatternClosure_kernel_replay.log` and
`SubgroupTopology_kernel_replay.log` in the development evidence directory.
