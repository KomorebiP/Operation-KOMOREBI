# Exact new theorem types — v0.5.0

These are exported from the accepted Lean environment. Noncomputable definitions and classical proof principles do not imply oracle-computability results.

## `RealizationBoundaries.seed_mem_endomorphismHull`
Source: `RealizationBoundaries/SeedGeneration.lean:26`
```text
∀ {G : Type u} [inst : AddGroup G] {S : Set G} {s : G}, s ∈ S → s ∈ RealizationBoundaries.endomorphismHull S
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.orbit_mem_endomorphismHull`
Source: `RealizationBoundaries/SeedGeneration.lean:30`
```text
∀ {G : Type u} [inst : AddGroup G] (S : Set G) (f : AddMonoid.End G) {s : G},
  s ∈ S → f s ∈ RealizationBoundaries.endomorphismHull S
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.endomorphismHull_le`
Source: `RealizationBoundaries/SeedGeneration.lean:35`
```text
∀ {G : Type u} [inst : AddGroup G] {S : Set G} {H : AddSubgroup G},
  S ⊆ ↑H → (∀ (f : AddMonoid.End G), ∀ x ∈ H, f x ∈ H) → RealizationBoundaries.endomorphismHull S ≤ H
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.endomorphismHull_invariant`
Source: `RealizationBoundaries/SeedGeneration.lean:43`
```text
∀ {G : Type u} [inst : AddGroup G] (S : Set G) (f : AddMonoid.End G) {x : G},
  x ∈ RealizationBoundaries.endomorphismHull S → f x ∈ RealizationBoundaries.endomorphismHull S
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.endomorphismHull_univ`
Source: `RealizationBoundaries/SeedGeneration.lean:51`
```text
∀ {G : Type u} [inst : AddGroup G], RealizationBoundaries.endomorphismHull Set.univ = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.endomorphismHull_empty`
Source: `RealizationBoundaries/SeedGeneration.lean:56`
```text
∀ {G : Type u} [inst : AddGroup G], RealizationBoundaries.endomorphismHull ∅ = ⊥
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.topologicalEndomorphismHull_le`
Source: `RealizationBoundaries/SeedGeneration.lean:67`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G] {S : Set G}
  {H : AddSubgroup G},
  IsClosed ↑H → RealizationBoundaries.endomorphismHull S ≤ H → RealizationBoundaries.topologicalEndomorphismHull S ≤ H
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.mem_coordinateKernel`
Source: `RealizationBoundaries/SeedGeneration.lean:79`
```text
∀ (H : AddSubgroup RealizationBoundaries.Ambient) (p : RealizationBoundaries.Prime) (x : ↥H),
  x ∈ RealizationBoundaries.coordinateKernel H p ↔ ↑x p = 0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.coordinateKernel_closed`
Source: `RealizationBoundaries/SeedGeneration.lean:82`
```text
∀ (H : AddSubgroup RealizationBoundaries.Ambient) (p : RealizationBoundaries.Prime),
  IsClosed ↑(RealizationBoundaries.coordinateKernel H p)
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.coordinate_obstruction`
Source: `RealizationBoundaries/SeedGeneration.lean:87`
```text
∀ (H : AddSubgroup RealizationBoundaries.Ambient) (p : RealizationBoundaries.Prime) (S : Set ↥H),
  (∀ s ∈ S, ↑s p = 0) →
    (∀ (f : AddMonoid.End ↥H) (x : ↥H), ↑x p = 0 → ↑(f x) p = 0) →
      RealizationBoundaries.endomorphismHull S ≤ RealizationBoundaries.coordinateKernel H p ∧
        RealizationBoundaries.topologicalEndomorphismHull S ≤ RealizationBoundaries.coordinateKernel H p
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.coordinateKernel_ne_top`
Source: `RealizationBoundaries/SeedGeneration.lean:97`
```text
∀ (H : AddSubgroup RealizationBoundaries.Ambient),
  RealizationBoundaries.finiteSupport ≤ H →
    ∀ (p : RealizationBoundaries.Prime), RealizationBoundaries.coordinateKernel H p ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_finite_seeds_missing`
Source: `RealizationBoundaries/SeedObstructions.lean:9`
```text
∀ (S : Set ↥RealizationBoundaries.finiteSupport), S.Finite → ∃ p, ∀ x ∈ S, ↑x p = 0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_seed_certificate`
Source: `RealizationBoundaries/SeedObstructions.lean:22`
```text
∀ (S : Set ↥RealizationBoundaries.finiteSupport),
  S.Finite →
    ∃ p,
      RealizationBoundaries.endomorphismHull S ≤
          RealizationBoundaries.coordinateKernel RealizationBoundaries.finiteSupport p ∧
        RealizationBoundaries.topologicalEndomorphismHull S ≤
            RealizationBoundaries.coordinateKernel RealizationBoundaries.finiteSupport p ∧
          RealizationBoundaries.coordinateKernel RealizationBoundaries.finiteSupport p ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_no_finite_endomorphism_seeds`
Source: `RealizationBoundaries/SeedObstructions.lean:31`
```text
∀ (S : Set ↥RealizationBoundaries.finiteSupport), S.Finite → RealizationBoundaries.endomorphismHull S ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_no_finite_topological_seeds`
Source: `RealizationBoundaries/SeedObstructions.lean:37`
```text
∀ (S : Set ↥RealizationBoundaries.finiteSupport), S.Finite → RealizationBoundaries.topologicalEndomorphismHull S ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.selector_outside_support_finite`
Source: `RealizationBoundaries/SeedObstructions.lean:45`
```text
∀ (T : Set RealizationBoundaries.Prime) (x : ↥(RealizationBoundaries.selectorGroup T)),
  (RealizationBoundaries.support ↑x \ T).Finite
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.omittedIndex_injective`
Source: `RealizationBoundaries/SeedObstructions.lean:56`
```text
∀ (a : ℕ → Bool), Function.Injective (RealizationBoundaries.omittedIndex a)
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_finite_seeds_missing`
Source: `RealizationBoundaries/SeedObstructions.lean:63`
```text
∀ (a : ℕ → Bool) (S : Set ↥(RealizationBoundaries.pairedGroup a)),
  S.Finite → ∃ n, ∀ x ∈ S, ↑x (RealizationBoundaries.primeAt (RealizationBoundaries.omittedIndex a n)) = 0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_seed_certificate`
Source: `RealizationBoundaries/SeedObstructions.lean:78`
```text
∀ (a : ℕ → Bool) (S : Set ↥(RealizationBoundaries.pairedGroup a)),
  S.Finite →
    ∃ p ∉ RealizationBoundaries.pairedSelector a,
      RealizationBoundaries.endomorphismHull S ≤
          RealizationBoundaries.coordinateKernel (RealizationBoundaries.pairedGroup a) p ∧
        RealizationBoundaries.topologicalEndomorphismHull S ≤
            RealizationBoundaries.coordinateKernel (RealizationBoundaries.pairedGroup a) p ∧
          RealizationBoundaries.coordinateKernel (RealizationBoundaries.pairedGroup a) p ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_no_finite_endomorphism_seeds`
Source: `RealizationBoundaries/SeedObstructions.lean:90`
```text
∀ (a : ℕ → Bool) (S : Set ↥(RealizationBoundaries.pairedGroup a)),
  S.Finite → RealizationBoundaries.endomorphismHull S ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_no_finite_topological_seeds`
Source: `RealizationBoundaries/SeedObstructions.lean:96`
```text
∀ (a : ℕ → Bool) (S : Set ↥(RealizationBoundaries.pairedGroup a)),
  S.Finite → RealizationBoundaries.topologicalEndomorphismHull S ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.generationCardinals_isLeast_aleph0`
Source: `RealizationBoundaries/GenerationRanks.lean:36`
```text
∀ {G : Type u} [inst : AddGroup G] [Countable G] [Infinite G] (hull : Set G → AddSubgroup G),
  hull Set.univ = ⊤ →
    (∀ (S : Set G), S.Finite → hull S ≠ ⊤) → IsLeast (RealizationBoundaries.generationCardinals hull) Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.generationRank_eq_aleph0`
Source: `RealizationBoundaries/GenerationRanks.lean:48`
```text
∀ {G : Type u} [inst : AddGroup G] [Countable G] [Infinite G] (hull : Set G → AddSubgroup G),
  hull Set.univ = ⊤ →
    (∀ (S : Set G), S.Finite → hull S ≠ ⊤) → RealizationBoundaries.generationRank hull = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ordinaryHull_le_endomorphismHull`
Source: `RealizationBoundaries/GenerationRanks.lean:53`
```text
∀ {G : Type u} [inst : AddGroup G] (S : Set G), AddSubgroup.closure S ≤ RealizationBoundaries.endomorphismHull S
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ordinaryTopologicalHull_le_endomorphism`
Source: `RealizationBoundaries/GenerationRanks.lean:57`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G] (S : Set G),
  RealizationBoundaries.ordinaryTopologicalHull S ≤ RealizationBoundaries.topologicalEndomorphismHull S
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.topologicalEndomorphismHull_univ`
Source: `RealizationBoundaries/GenerationRanks.lean:62`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G],
  RealizationBoundaries.topologicalEndomorphismHull Set.univ = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ordinaryTopologicalHull_univ`
Source: `RealizationBoundaries/GenerationRanks.lean:68`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G],
  RealizationBoundaries.ordinaryTopologicalHull Set.univ = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_endomorphismSeedRank`
Source: `RealizationBoundaries/GenerationRanks.lean:76`
```text
RealizationBoundaries.endomorphismSeedRank ↥RealizationBoundaries.finiteSupport = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_topologicalEndomorphismSeedRank`
Source: `RealizationBoundaries/GenerationRanks.lean:79`
```text
RealizationBoundaries.topologicalEndomorphismSeedRank ↥RealizationBoundaries.finiteSupport = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finiteSupport_ordinaryTopologicalRank`
Source: `RealizationBoundaries/GenerationRanks.lean:84`
```text
RealizationBoundaries.ordinaryTopologicalRank ↥RealizationBoundaries.finiteSupport = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_endomorphismSeedRank`
Source: `RealizationBoundaries/GenerationRanks.lean:97`
```text
∀ (a : ℕ → Bool), RealizationBoundaries.endomorphismSeedRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_topologicalEndomorphismSeedRank`
Source: `RealizationBoundaries/GenerationRanks.lean:101`
```text
∀ (a : ℕ → Bool),
  RealizationBoundaries.topologicalEndomorphismSeedRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_ordinaryTopologicalRank`
Source: `RealizationBoundaries/GenerationRanks.lean:106`
```text
∀ (a : ℕ → Bool), RealizationBoundaries.ordinaryTopologicalRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.finite_coordinate_interpolation`
Source: `RealizationBoundaries/Procyclic.lean:10`
```text
∀ (J : Finset RealizationBoundaries.Prime) (x : RealizationBoundaries.Ambient), ∃ n, ∀ p ∈ J, ↑n = x p
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ambient_cyclic_dense`
Source: `RealizationBoundaries/Procyclic.lean:24`
```text
Dense ↑(AddSubgroup.closure {1})
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ambient_topological_generator`
Source: `RealizationBoundaries/Procyclic.lean:40`
```text
RealizationBoundaries.ordinaryTopologicalHull {1} = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ordinaryTopologicalHull_empty`
Source: `RealizationBoundaries/Procyclic.lean:47`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G] [T2Space G],
  RealizationBoundaries.ordinaryTopologicalHull ∅ = ⊥
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ordinaryTopologicalRank_eq_one_of_generator`
Source: `RealizationBoundaries/Procyclic.lean:56`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G] [T2Space G]
  [Nontrivial G] (g : G),
  RealizationBoundaries.ordinaryTopologicalHull {g} = ⊤ → RealizationBoundaries.ordinaryTopologicalRank G = 1
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.topological_generator_transport`
Source: `RealizationBoundaries/Procyclic.lean:69`
```text
∀ {G : Type u} [inst : AddGroup G] [inst_1 : TopologicalSpace G] [inst_2 : IsTopologicalAddGroup G] {H : Type v}
  [inst_3 : AddGroup H] [inst_4 : TopologicalSpace H] [inst_5 : IsTopologicalAddGroup H] (e : G ≃ₜ+ H) (g : G),
  RealizationBoundaries.ordinaryTopologicalHull {g} = ⊤ → RealizationBoundaries.ordinaryTopologicalHull {e g} = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ambient_ordinaryTopologicalRank`
Source: `RealizationBoundaries/Procyclic.lean:91`
```text
RealizationBoundaries.ordinaryTopologicalRank RealizationBoundaries.Ambient = 1
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.completionGenerator_generates`
Source: `RealizationBoundaries/Procyclic.lean:98`
```text
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace),
  RealizationBoundaries.ordinaryTopologicalHull {RealizationBoundaries.completionGenerator W} = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.canonicalCompletion_ordinaryTopologicalRank`
Source: `RealizationBoundaries/Procyclic.lean:102`
```text
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace),
  RealizationBoundaries.ordinaryTopologicalRank ↑(RealizationBoundaries.CanonicalCompletion W).toProfinite.toTop = 1
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_seed_rank_separation`
Source: `RealizationBoundaries/Procyclic.lean:109`
```text
∀ (a : ℕ → Bool),
  RealizationBoundaries.endomorphismSeedRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0 ∧
    RealizationBoundaries.topologicalEndomorphismSeedRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0 ∧
      RealizationBoundaries.ordinaryTopologicalRank ↥(RealizationBoundaries.pairedGroup a) = Cardinal.aleph0 ∧
        RealizationBoundaries.ordinaryTopologicalRank
            ↑(RealizationBoundaries.CanonicalCompletion
                    (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a))).toProfinite.toTop =
          1
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.all_one_not_finiteSupport`
Source: `RealizationBoundaries/GenerationConsequences.lean:9`
```text
1 ∉ RealizationBoundaries.finiteSupport
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.all_one_not_pairedGroup`
Source: `RealizationBoundaries/GenerationConsequences.lean:17`
```text
∀ (a : ℕ → Bool), 1 ∉ RealizationBoundaries.pairedGroup a
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.all_one_infinite_order`
Source: `RealizationBoundaries/GenerationConsequences.lean:25`
```text
∀ (m : ℕ), 0 < m → m • 1 ≠ 0
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.paired_completionGenerator_not_in_eta_range`
Source: `RealizationBoundaries/GenerationConsequences.lean:30`
```text
∀ (a : ℕ → Bool),
  RealizationBoundaries.completionGenerator
      (RealizationBoundaries.selectorLine (RealizationBoundaries.pairedSelector a)) ∉
    Set.range (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of ↥(RealizationBoundaries.pairedGroup a)))
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.primeSeed_not_in_all_one_cyclic`
Source: `RealizationBoundaries/GenerationConsequences.lean:40`
```text
∀ (p : RealizationBoundaries.Prime), ↑(RealizationBoundaries.primeSeed p) ∉ AddSubgroup.closure {1}
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.all_one_cyclic_ne_top`
Source: `RealizationBoundaries/GenerationConsequences.lean:56`
```text
AddSubgroup.closure {1} ≠ ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ambient_single_endomorphism_generator`
Source: `RealizationBoundaries/GenerationConsequences.lean:61`
```text
RealizationBoundaries.endomorphismHull {1} = ⊤
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`

## `RealizationBoundaries.ambient_endomorphismSeedRank`
Source: `RealizationBoundaries/GenerationConsequences.lean:69`
```text
RealizationBoundaries.endomorphismSeedRank RealizationBoundaries.Ambient = 1
```
Axioms: `propext`, `Classical.choice`, `Quot.sound`
