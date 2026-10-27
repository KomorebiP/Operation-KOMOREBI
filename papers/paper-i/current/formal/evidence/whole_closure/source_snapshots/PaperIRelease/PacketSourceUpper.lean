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

/-- Corner generators in a family of grouped packets generate globally if
those whole packets propagate through every invariant submodule. The graph
theorem supplies this propagation condition for the actual source SCCs. -/
theorem packetPureSeedRank_le_sum_local_of_generation
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) (σ : I → J) (D : Set J)
    (hwhole : ∀ H : Submodule A X,
      (∀ C ∈ D, LinearMap.range ((groupedFamily P σ).proj C) ≤ H.restrictScalars 𝕜) → H = ⊤) :
    packetPureSeedRank A P ≤
      Cardinal.sum (fun C : D ↦ localPureSeedRank A P hPA σ C.val) := by
  classical
  let B (C : D) := localCornerAlgebra A P hPA σ C.val
  let V (C : D) := LinearMap.range ((groupedFamily P σ).proj C.val)
  choose S hS hcard using fun C : D ↦
    exists_pure_generating_set_card_eq (B C) (localPacketFamily P σ C.val)
  let seeds : Set X := ⋃ C : D, Subtype.val '' S C
  let H : Submodule A X := Submodule.span A seeds
  have hgroup (C : D) (x : V C) : (x : X) ∈ H := by
    have hx : x ∈ Submodule.span (B C) (S C) := by rw [(hS C).1]; trivial
    refine Submodule.span_induction
      (p := fun (x : V C) _ ↦ (x : X) ∈ H) ?_ ?_ ?_ ?_ hx
    · intro y hy
      exact Submodule.subset_span (Set.mem_iUnion.mpr ⟨C, ⟨y, hy, rfl⟩⟩)
    · exact H.zero_mem
    · intro x y _ _ hx hy
      exact H.add_mem hx hy
    · intro a y _ hy
      obtain ⟨b, hb⟩ := corner_action_ambient A ((groupedFamily P σ).proj C.val)
        (groupedProjection_mem_algebra A P hPA σ C.val)
        ((groupedFamily P σ).idempotent C.val) a
      rw [hb y]
      exact H.smul_mem b hy
  have hgen : PureGenerates A P seeds := by
    constructor
    · apply hwhole H
      intro C hC x hx
      exact hgroup ⟨C, hC⟩ ⟨x, hx⟩
    · intro x hx
      obtain ⟨C, y, hy, rfl⟩ := Set.mem_iUnion.mp hx
      exact (local_packetPure_iff P σ C.val y).mp ((hS C).2 y hy)
  calc
    packetPureSeedRank A P ≤ #seeds := packetPureSeedRank_le_card hgen
    _ ≤ Cardinal.sum (fun C : D ↦ #(Subtype.val '' S C : Set X)) :=
      Cardinal.mk_iUnion_le_sum_mk
    _ ≤ Cardinal.sum (fun C : D ↦ #(S C)) :=
      Cardinal.sum_le_sum _ _ (fun _ ↦ Cardinal.mk_image_le)
    _ = _ := by simp only [hcard, B, localPureSeedRank]

end Komorebi.PaperIRelease
