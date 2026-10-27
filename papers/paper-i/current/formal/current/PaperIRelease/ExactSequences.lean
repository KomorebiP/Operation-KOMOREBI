import KomorebiVerification.SeedRankOperations

/-!
# Generator bounds for actual exact sequences

The upper bound uses an arbitrary ring and unrestricted modules. Exactness is
the literal equality of the image of the first map with the kernel of the
second. No splitting, finite-dimensionality, or supplied generating family
for the middle module is assumed.
-/

set_option autoImplicit false
set_option linter.unnecessarySimpa false

namespace Komorebi.PaperIRelease

open Cardinal Set
open Komorebi.SeedRankBasics Komorebi.SeedRankOperations

universe u

variable {A L M N : Type u} [Ring A]
variable [AddCommGroup L] [Module A L]
variable [AddCommGroup M] [Module A M]
variable [AddCommGroup N] [Module A N]

/-- Lift generators of the quotient and adjoin images of generators of the
kernel. This proves the generator bound for every right exact sequence. -/
theorem seedRank_le_add_of_exact
    (f : L →ₗ[A] M) (g : M →ₗ[A] N)
    (hexact : LinearMap.range f = LinearMap.ker g)
    (hg : Function.Surjective g) :
    seedRank A M ≤ seedRank A L + seedRank A N := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A L
  obtain ⟨t, ht, htCard⟩ := exists_generating_set_card_eq_seedRank A N
  let lift : t → M := fun j ↦ Classical.choose (hg (j : N))
  have hlift (j : t) : g (lift j) = (j : N) := Classical.choose_spec (hg (j : N))
  let v : s ⊕ t → M := Sum.elim (fun i ↦ f (i : L)) lift
  let p : Submodule A M := Submodule.span A (Set.range v)
  have hfmem (x : L) : f x ∈ p := by
    have hx : x ∈ Submodule.span A s := by rw [hs]; trivial
    refine Submodule.span_induction
      (p := fun x _ ↦ f x ∈ p) ?_ ?_ ?_ ?_ hx
    · intro x hxs
      exact Submodule.subset_span ⟨Sum.inl ⟨x, hxs⟩, rfl⟩
    · simpa using p.zero_mem
    · intro x y _ _ hx hy
      simpa using p.add_mem hx hy
    · intro a x _ hx
      simpa using p.smul_mem a hx
  have hmap : p.map g = ⊤ := by
    apply top_unique
    rw [← ht]
    apply Submodule.span_le.mpr
    intro y hy
    exact ⟨lift ⟨y, hy⟩,
      Submodule.subset_span ⟨Sum.inr ⟨y, hy⟩, rfl⟩, hlift ⟨y, hy⟩⟩
  have hgen : FamilyGenerates A M v := by
    change p = ⊤
    apply top_unique
    intro x _
    have hx : g x ∈ p.map g := by rw [hmap]; trivial
    obtain ⟨y, hy, hgy⟩ := hx
    have hdiff : x - y ∈ LinearMap.range f := by
      rw [hexact]
      change g (x - y) = 0
      rw [map_sub, hgy, sub_self]
    obtain ⟨z, hz⟩ := hdiff
    have hdmem : x - y ∈ p := by rw [← hz]; exact hfmem z
    simpa using p.add_mem hdmem hy
  have hbound := seedRank_le_mk_of_familyGenerates A M hgen
  simpa [Cardinal.mk_sum, hsCard, htCard] using hbound

/-- Paper I's two cardinal bounds for an actual short exact sequence. The
upper bound in fact needs only exactness in the middle and surjectivity. -/
theorem shortExact_seedRank_bounds
    (f : L →ₗ[A] M) (g : M →ₗ[A] N)
    (_hf : Function.Injective f)
    (hexact : LinearMap.range f = LinearMap.ker g)
    (hg : Function.Surjective g) :
    seedRank A N ≤ seedRank A M ∧
      seedRank A M ≤ seedRank A L + seedRank A N :=
  ⟨seedRank_le_of_surjective_semilinear g hg,
    seedRank_le_add_of_exact f g hexact hg⟩

/-- The canonical submodule/quotient exact sequence, without any finiteness
restriction on the ring, submodule, or ambient module. -/
theorem submodule_quotient_seedRank_bounds (K : Submodule A M) :
    seedRank A (M ⧸ K) ≤ seedRank A M ∧
      seedRank A M ≤ seedRank A K + seedRank A (M ⧸ K) :=
  shortExact_seedRank_bounds K.subtype K.mkQ K.subtype_injective
    (by rw [K.range_subtype, K.ker_mkQ]) K.mkQ_surjective

end Komorebi.PaperIRelease

#print axioms Komorebi.PaperIRelease.seedRank_le_add_of_exact
#print axioms Komorebi.PaperIRelease.shortExact_seedRank_bounds
#print axioms Komorebi.PaperIRelease.submodule_quotient_seedRank_bounds
