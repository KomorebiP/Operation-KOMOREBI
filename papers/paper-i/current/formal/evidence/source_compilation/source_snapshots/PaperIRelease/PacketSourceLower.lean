import PaperIRelease.PacketLocalRank

set_option autoImplicit false
set_option linter.unnecessarySimpa false
noncomputable section

namespace Komorebi.PaperIRelease

open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics
open PacketAggregation

universe u
variable {𝕜 X I J : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X]
variable [Fintype I] [Fintype J] [DecidableEq J]

/-- Nonzero original seeds which actually lie in one grouped range.
Removing zero ensures that these sets are disjoint across different groups. -/
def localNonzeroSeeds (P : LinearProjectorFamily 𝕜 X I) (σ : I → J)
    (C : J) (S : Set X) : Set (LinearMap.range ((groupedFamily P σ).proj C)) :=
  {x | (x : X) ∈ S ∧ (x : X) ≠ 0}

/-- At a component with no incoming action, the original pure seeds inside
that component generate its genuine corner module. The hypothesis is the
literal no-incoming compression identity, later derived for source SCCs. -/
theorem localNonzeroSeeds_generate_of_compression
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) (σ : I → J) (C : J)
    (hcomp : ∀ a ∈ A, ∀ x, (groupedFamily P σ).proj C (a x) =
      (groupedFamily P σ).proj C (a ((groupedFamily P σ).proj C x)))
    {S : Set X} (hS : PureGenerates A P S) :
    PureGenerates (localCornerAlgebra A P hPA σ C) (localPacketFamily P σ C)
      (localNonzeroSeeds P σ C S) := by
  let Q := (groupedFamily P σ).proj C
  let π : X →ₗ[𝕜] LinearMap.range Q := Q.rangeRestrict
  let B := localCornerAlgebra A P hPA σ C
  let H : Submodule B (LinearMap.range Q) :=
    Submodule.span B (localNonzeroSeeds P σ C S)
  have hproj (x : X) : π x ∈ H := by
    have hx : x ∈ Submodule.span A S := by rw [hS.1]; trivial
    refine Submodule.span_induction (p := fun x _ ↦ π x ∈ H) ?_ ?_ ?_ ?_ hx
    · intro y hy
      rcases pure_grouped_fixed_or_zero P σ C (hS.2 y hy) with hfixed | hzero
      · by_cases hy0 : y = 0
        · simpa [hy0] using H.zero_mem
        · apply Submodule.subset_span
          change (groupedFamily P σ).proj C y ∈ S ∧ (groupedFamily P σ).proj C y ≠ 0
          rw [hfixed]
          exact ⟨hy, hy0⟩
      · have hz : π y = 0 := Subtype.ext hzero
        rw [hz]
        exact H.zero_mem
    · simpa using H.zero_mem
    · intro x y _ _ hx hy
      simpa using H.add_mem hx hy
    · intro a x _ hx
      let c : B := ⟨cornerCompression Q a.val, ⟨a.val, a.property, rfl⟩⟩
      have heq : π (a • x) = c • π x := by
        apply Subtype.ext
        exact hcomp a.val a.property x
      rw [heq]
      exact H.smul_mem c hx
  refine ⟨?_, ?_⟩
  · change H = ⊤
    apply top_unique
    intro x _
    have hx := hproj (x : X)
    have heq : π (x : X) = x :=
      Subtype.ext ((groupedFamily P σ).proj_eq_self_of_mem_range C x.property)
    rwa [heq] at hx
  · intro x hx
    exact (local_packetPure_iff P σ C x).mpr (hS.2 x hx.1)

/-- The nonzero seed subsets in distinct grouped packet ranges are disjoint,
expressed as an injection from their dependent sum into the original set. -/
def localNonzeroSeedsEmbedding (P : LinearProjectorFamily 𝕜 X I)
    (σ : I → J) (D : Set J) (S : Set X) :
    (Σ C : D, localNonzeroSeeds P σ C.val S) ↪ S where
  toFun z := ⟨(z.2.val : X), z.2.property.1⟩
  inj' := by
    rintro ⟨C, x⟩ ⟨E, y⟩ h
    have hxy : (x.val : X) = (y.val : X) := congrArg Subtype.val h
    have hCE : C = E := by
      apply Subtype.ext
      by_contra hne
      have hz : (groupedFamily P σ).proj C.val (x.val : X) = 0 := by
        rw [hxy]
        obtain ⟨z, hz⟩ := y.val.property
        rw [← hz]
        exact (groupedFamily P σ).orthogonal hne z
      rw [(groupedFamily P σ).proj_eq_self_of_mem_range C.val x.val.property] at hz
      exact x.property.2 hz
    subst E
    have hxy' : x = y := Subtype.ext (Subtype.ext hxy)
    subst y
    rfl

theorem sum_localNonzeroSeeds_card_le (P : LinearProjectorFamily 𝕜 X I)
    (σ : I → J) (D : Set J) (S : Set X) :
    Cardinal.sum (fun C : D ↦ #(localNonzeroSeeds P σ C.val S)) ≤ #S := by
  rw [← Cardinal.mk_sigma]
  exact Cardinal.mk_le_of_injective (localNonzeroSeedsEmbedding P σ D S).injective

/-- Cardinal lower bound from an actual family of source-compression
identities. Source SCCs provide these identities from graph reachability. -/
theorem sum_localPureSeedRank_le_of_compression
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) (σ : I → J) (D : Set J)
    (hcomp : ∀ C ∈ D, ∀ a ∈ A, ∀ x, (groupedFamily P σ).proj C (a x) =
      (groupedFamily P σ).proj C (a ((groupedFamily P σ).proj C x))) :
    Cardinal.sum (fun C : D ↦ localPureSeedRank A P hPA σ C.val) ≤
      packetPureSeedRank A P := by
  obtain ⟨S, hS, hcard⟩ := exists_pure_generating_set_card_eq A P
  rw [← hcard]
  calc
    _ ≤ Cardinal.sum (fun C : D ↦ #(localNonzeroSeeds P σ C.val S)) :=
      Cardinal.sum_le_sum _ _ (fun C ↦ packetPureSeedRank_le_card
        (localNonzeroSeeds_generate_of_compression A P hPA σ C.val (hcomp C.val C.property) hS))
    _ ≤ #S := sum_localNonzeroSeeds_card_le P σ D S

end Komorebi.PaperIRelease
