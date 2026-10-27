import Mathlib

/-!
# Algebraic seed-rank basics

This file formalizes the algebraic foundation of Paper I.  A set of seeds
generates a module when its submodule span is the whole module.  The seed rank
is the least cardinality of such a set; this is Mathlib's `Submodule.spanRank`
applied to the top submodule, so the zero module and infinitely generated
modules are covered without extra conventions.

For one seed, the presentation map is `a ↦ a • x`.  For a family of seeds,
it is the finite-linear-combination map from the free module `ι →₀ A`.
The first isomorphism theorem then gives the corresponding quotient
presentations.  We also prove monotonicity under surjective linear maps and
invariance under linear equivalence.
-/

set_option autoImplicit false

namespace Komorebi.SeedRankBasics

open Cardinal Set

universe u v w

section Semiring

variable (A : Type u) (M : Type v)
variable [Semiring A] [AddCommMonoid M] [Module A M]

/-- A set of seeds generates `M` when its `A`-linear span is all of `M`. -/
def Generates (s : Set M) : Prop :=
  Submodule.span A s = ⊤

/-- A family generates when its range is a generating set. -/
def FamilyGenerates {ι : Type w} (v : ι → M) : Prop :=
  Generates A M (Set.range v)

/-- A module is cyclic when one element generates it. -/
def Cyclic : Prop :=
  ∃ x : M, Generates A M {x}

/--
The seed rank is the least cardinality of a set whose `A`-span is `M`.

Because it is cardinal-valued, it remains meaningful for modules that are not
finitely generated.  In particular, the zero module has seed rank zero.
-/
noncomputable def seedRank : Cardinal :=
  (⊤ : Submodule A M).spanRank

/-- The natural-valued minimum used for finite-generation corollaries. -/
noncomputable def seedFinrank : ℕ :=
  (⊤ : Submodule A M).spanFinrank

theorem generates_univ : Generates A M Set.univ := by
  simp [Generates]

theorem generates_mono {s t : Set M} (hs : Generates A M s) (hst : s ⊆ t) :
    Generates A M t := by
  rw [Generates] at hs ⊢
  exact top_unique (hs ▸ Submodule.span_mono hst)

/-- Every generating set gives an upper bound for seed rank. -/
theorem seedRank_le_mk_of_generates {s : Set M} (hs : Generates A M s) :
    seedRank A M ≤ Cardinal.mk s := by
  rw [Generates] at hs
  rw [seedRank, ← hs]
  exact Submodule.spanRank_span_le_card s

/-- A minimum-cardinality generating set always exists. -/
theorem exists_generating_set_card_eq_seedRank :
    ∃ s : Set M, Generates A M s ∧ Cardinal.mk s = seedRank A M := by
  obtain ⟨s, hsCard, hsSpan⟩ :=
    Submodule.exists_span_set_card_eq_spanRank (⊤ : Submodule A M)
  exact ⟨s, hsSpan, hsCard⟩

/-- The universal one-seed presentation map, `a ↦ a • x`. -/
def oneSeedMap (x : M) : A →ₗ[A] M :=
  LinearMap.toSpanSingleton A M x

@[simp]
theorem oneSeedMap_apply (x : M) (a : A) :
    oneSeedMap A M x a = a • x := by
  rfl

/-- The image of the one-seed map is exactly the cyclic submodule it spans. -/
theorem range_oneSeedMap (x : M) :
    LinearMap.range (oneSeedMap A M x) = Submodule.span A {x} := by
  exact LinearMap.range_toSpanSingleton x

/-- A seed generates exactly when its presentation map is surjective. -/
theorem generates_singleton_iff_surjective (x : M) :
    Generates A M {x} ↔ Function.Surjective (oneSeedMap A M x) := by
  rw [Generates, ← range_oneSeedMap A M x, LinearMap.range_eq_top]

/-- Cyclicity is equivalently the existence of a surjective one-seed map. -/
theorem cyclic_iff_exists_surjective_oneSeedMap :
    Cyclic A M ↔
      ∃ x : M, Function.Surjective (oneSeedMap A M x) := by
  simp only [Cyclic, generates_singleton_iff_surjective]

/-- The multi-seed presentation map from the free module on the seed labels. -/
noncomputable def multiSeedMap {ι : Type w} (v : ι → M) : (ι →₀ A) →ₗ[A] M :=
  Finsupp.linearCombination A v

/-- Its image is exactly the span of the seed family. -/
theorem range_multiSeedMap {ι : Type w} (v : ι → M) :
    LinearMap.range (multiSeedMap A M v) =
      Submodule.span A (Set.range v) := by
  exact Finsupp.range_linearCombination (R := A) (v := v)

/-- A family generates exactly when its free-module presentation is onto. -/
theorem familyGenerates_iff_surjective {ι : Type w} (v : ι → M) :
    FamilyGenerates A M v ↔
      Function.Surjective (multiSeedMap A M v) := by
  rw [FamilyGenerates, Generates, ← range_multiSeedMap A M v,
    LinearMap.range_eq_top]

/-- A generating family bounds seed rank by the cardinality of its labels. -/
theorem seedRank_le_mk_of_familyGenerates {ι : Type w} {v : ι → M}
    (hv : FamilyGenerates A M v) :
    Cardinal.lift.{w} (seedRank A M) ≤ Cardinal.lift.{v} (Cardinal.mk ι) := by
  have hset := seedRank_le_mk_of_generates A M hv
  exact (Cardinal.lift_le.2 hset).trans
    (Cardinal.mk_range_le_lift (f := v))

/-- Seed rank zero characterizes the zero (subsingleton) module. -/
theorem seedRank_eq_zero_iff :
    seedRank A M = 0 ↔ Subsingleton M := by
  rw [seedRank, Submodule.spanRank_eq_zero_iff_eq_bot]
  constructor
  · intro h
    constructor
    intro x y
    have hx : x = 0 := by
      have hx' : x ∈ (⊥ : Submodule A M) := by
        rw [← h]
        trivial
      simpa using hx'
    have hy : y = 0 := by
      have hy' : y ∈ (⊥ : Submodule A M) := by
        rw [← h]
        trivial
      simpa using hy'
    exact hx.trans hy.symm
  · intro h
    apply le_antisymm
    · intro x _hx
      change x = 0
      exact @Subsingleton.elim M h x 0
    · exact bot_le

/-- Seed rank is below `aleph0` exactly when the module is finitely generated. -/
theorem seedRank_lt_aleph0_iff :
    seedRank A M < Cardinal.aleph0 ↔ Module.Finite A M := by
  rw [seedRank, Submodule.spanRank_finite_iff_fg]
  exact Module.finite_def.symm

/-- Cyclicity is the principality of the top submodule. -/
theorem cyclic_iff_top_isPrincipal :
    Cyclic A M ↔ (⊤ : Submodule A M).IsPrincipal := by
  constructor
  · rintro ⟨x, hx⟩
    exact ⟨x, hx.symm⟩
  · rintro ⟨x, hx⟩
    exact ⟨x, hx.symm⟩

/-- In a finite module, cardinal seed rank is the natural seed finrank. -/
theorem seedRank_eq_seedFinrank [Module.Finite A M] :
    seedRank A M = seedFinrank A M := by
  exact Module.Finite.fg_top.spanRank_eq_spanFinrank

/-- Finite, nonzero cyclic modules are exactly those of seed finrank one. -/
theorem cyclic_iff_seedFinrank_eq_one [Module.Finite A M] [Nontrivial M] :
    Cyclic A M ↔ seedFinrank A M = 1 := by
  rw [seedFinrank, Submodule.spanFinrank_eq_one_iff]
  simpa using cyclic_iff_top_isPrincipal A M

/-- For a finite nonzero module, cardinal seed rank one is exactly cyclicity. -/
theorem seedRank_eq_one_iff_cyclic [Module.Finite A M] [Nontrivial M] :
    seedRank A M = 1 ↔ Cyclic A M := by
  rw [seedRank_eq_seedFinrank A M]
  norm_cast
  exact (cyclic_iff_seedFinrank_eq_one A M).symm

end Semiring

section Functoriality

variable {A : Type u} {M N : Type v}
variable [Semiring A]
variable [AddCommMonoid M] [Module A M]
variable [AddCommMonoid N] [Module A N]

/-- Seed rank cannot increase under a surjective linear map. -/
theorem seedRank_le_of_surjective (f : M →ₗ[A] N)
    (hf : Function.Surjective f) :
    seedRank A N ≤ seedRank A M := by
  rw [seedRank, seedRank, ← LinearMap.range_eq_top.mpr hf]
  exact Submodule.spanRank_range_le f

/-- Seed rank is invariant under linear equivalence. -/
theorem seedRank_linearEquiv (e : M ≃ₗ[A] N) :
    seedRank A M = seedRank A N := by
  apply le_antisymm
  · exact seedRank_le_of_surjective e.symm.toLinearMap e.symm.surjective
  · exact seedRank_le_of_surjective e.toLinearMap e.surjective

end Functoriality

section QuotientPresentations

variable (A : Type u) (M : Type v)
variable [Ring A] [AddCommGroup M] [Module A M]

/-- Passing to a module quotient cannot increase seed rank. -/
theorem seedRank_quotient_le (p : Submodule A M) :
    seedRank A (M ⧸ p) ≤ seedRank A M := by
  exact seedRank_le_of_surjective p.mkQ p.mkQ_surjective

/-- First-isomorphism presentation for one seed, with its exact range. -/
noncomputable def oneSeedQuotientEquivRange (x : M) :
    (A ⧸ LinearMap.ker (oneSeedMap A M x)) ≃ₗ[A]
      LinearMap.range (oneSeedMap A M x) :=
  (oneSeedMap A M x).quotKerEquivRange

/--
The range-valued quotient equivalence is the canonical presentation map:
the class of `a` is sent to the range element represented by `a • x`.
This is the explicit glue between the first-isomorphism construction and the
formula used in the manuscript.
-/
@[simp]
theorem oneSeedQuotientEquivRange_apply_mk (x : M) (a : A) :
    (oneSeedQuotientEquivRange A M x) (Submodule.Quotient.mk a) =
      ⟨a • x, by
        exact ⟨a, rfl⟩⟩ := by
  rfl

/-- If `x` generates, its quotient presentation has codomain all of `M`. -/
noncomputable def oneSeedQuotientEquiv (x : M)
    (hx : Generates A M {x}) :
    (A ⧸ LinearMap.ker (oneSeedMap A M x)) ≃ₗ[A] M :=
  (oneSeedMap A M x).quotKerEquivOfSurjective
    ((generates_singleton_iff_surjective A M x).mp hx)

@[simp]
theorem oneSeedQuotientEquiv_apply_mk (x : M)
    (hx : Generates A M {x}) (a : A) :
    oneSeedQuotientEquiv A M x hx (Submodule.Quotient.mk a) = a • x := by
  rfl

/-- First-isomorphism presentation for an arbitrary seed family. -/
noncomputable def multiSeedQuotientEquivRange {ι : Type w} (v : ι → M) :
    ((ι →₀ A) ⧸ LinearMap.ker (multiSeedMap A M v)) ≃ₗ[A]
      LinearMap.range (multiSeedMap A M v) :=
  (multiSeedMap A M v).quotKerEquivRange

/--
The range-valued multi-seed quotient equivalence sends a coefficient family
to its represented finite linear combination.  This makes the free-module
presentation in the manuscript literal at the level of the compiled API.
-/
@[simp]
theorem multiSeedQuotientEquivRange_apply_mk {ι : Type w} (v : ι → M)
    (c : ι →₀ A) :
    (multiSeedQuotientEquivRange A M v) (Submodule.Quotient.mk c) =
      ⟨Finsupp.linearCombination A v c, by
        exact ⟨c, rfl⟩⟩ := by
  rfl

/-- A generating family presents `M` as a quotient of its free module. -/
noncomputable def multiSeedQuotientEquiv {ι : Type w} (v : ι → M)
    (hv : FamilyGenerates A M v) :
    ((ι →₀ A) ⧸ LinearMap.ker (multiSeedMap A M v)) ≃ₗ[A] M :=
  (multiSeedMap A M v).quotKerEquivOfSurjective
    ((familyGenerates_iff_surjective A M v).mp hv)

@[simp]
theorem multiSeedQuotientEquiv_apply_mk {ι : Type w} (v : ι → M)
    (hv : FamilyGenerates A M v) (c : ι →₀ A) :
    multiSeedQuotientEquiv A M v hv (Submodule.Quotient.mk c) =
      Finsupp.linearCombination A v c := by
  rfl

end QuotientPresentations

end Komorebi.SeedRankBasics

#print axioms Komorebi.SeedRankBasics.seedRank_le_of_surjective
#print axioms Komorebi.SeedRankBasics.seedRank_linearEquiv
#print axioms Komorebi.SeedRankBasics.oneSeedQuotientEquiv
#print axioms Komorebi.SeedRankBasics.multiSeedQuotientEquiv
#print axioms Komorebi.SeedRankBasics.cyclic_iff_seedFinrank_eq_one
