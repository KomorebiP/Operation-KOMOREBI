import PaperIRelease.PacketPureRank
import PaperIRelease.PacketAggregation

set_option autoImplicit false
set_option linter.unnecessarySimpa false
noncomputable section

namespace Komorebi.PaperIRelease

open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics
open PacketAggregation

universe u
variable {𝕜 X I J : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X]
variable [Fintype I] [Fintype J] [DecidableEq J]

theorem groupedRange_preserved (P : LinearProjectorFamily 𝕜 X I)
    (σ : I → J) (C : J) :
    P.Preserves (LinearMap.range ((groupedFamily P σ).proj C)) := by
  intro i x hx
  obtain ⟨y, rfl⟩ := hx
  change P.proj i (groupedProjection P σ C y) ∈ _
  rw [proj_groupedProjection]
  by_cases hi : σ i = C
  · rw [ite_eq_left hi]
    simpa only [hi] using original_mem_grouped P σ i ⟨P.proj i y, ⟨y, rfl⟩⟩
  · rw [ite_eq_right hi]
    exact Submodule.zero_mem _

/-- The original packets restricted to the grouped range. Indices outside
the group give zero maps; deleting those zero maps preserves the pure rank. -/
def localPacketFamily (P : LinearProjectorFamily 𝕜 X I) (σ : I → J) (C : J) :
    LinearProjectorFamily 𝕜 (LinearMap.range ((groupedFamily P σ).proj C)) I :=
  P.restrictTo _ (groupedRange_preserved P σ C)

theorem local_packetPure_iff (P : LinearProjectorFamily 𝕜 X I)
    (σ : I → J) (C : J) (x : LinearMap.range ((groupedFamily P σ).proj C)) :
    PacketPure (localPacketFamily P σ C) x ↔ PacketPure P (x : X) := by
  constructor
  · intro hx a ha b hb
    apply hx
    · intro h
      exact ha (congrArg Subtype.val h)
    · intro h
      exact hb (congrArg Subtype.val h)
  · intro hx a ha b hb
    apply hx
    · intro h
      exact ha (Subtype.ext h)
    · intro h
      exact hb (Subtype.ext h)

/-- With nonzero original packets, the only zero local projectors are the
indices outside the group. Thus zero removal gives exactly `P|_C`. -/
theorem local_proj_zero_iff (P : LinearProjectorFamily 𝕜 X I)
    (hP : ∀ i, P.proj i ≠ 0) (σ : I → J) (C : J) (i : I) :
    (localPacketFamily P σ C).proj i = 0 ↔ σ i ≠ C := by
  constructor
  · intro hzero hi
    apply hP i
    ext x
    have hx : P.proj i x ∈ LinearMap.range ((groupedFamily P σ).proj C) := by
      simpa only [hi] using original_mem_grouped P σ i ⟨P.proj i x, ⟨x, rfl⟩⟩
    have hh := congrArg (fun f ↦ f ⟨P.proj i x, hx⟩) hzero
    have hval := congrArg Subtype.val hh
    change P.proj i (P.proj i x) = 0 at hval
    rwa [P.idempotent] at hval
  · intro hi
    apply LinearMap.ext
    intro x
    apply Subtype.ext
    obtain ⟨y, hy⟩ := x.property
    change P.proj i (x : X) = 0
    rw [← hy]
    change P.proj i (groupedProjection P σ C y) = 0
    simpa only [ite_eq_right hi] using proj_groupedProjection P σ i C y

theorem groupedProjection_mem_algebra
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I)
    (hPA : ∀ i, P.proj i ∈ A) (σ : I → J) (C : J) :
    (groupedFamily P σ).proj C ∈ A := by
  classical
  change (∑ i with σ i = C, P.proj i) ∈ A
  exact A.sum_mem (fun i _ ↦ hPA i)

abbrev localCornerAlgebra (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (P : LinearProjectorFamily 𝕜 X I) (hPA : ∀ i, P.proj i ∈ A)
    (σ : I → J) (C : J) :=
  packetCornerAlgebra A ((groupedFamily P σ).proj C)
    (groupedProjection_mem_algebra A P hPA σ C) ((groupedFamily P σ).idempotent C)

/-- Local cardinal minimum under the genuine grouped corner action. -/
def localPureSeedRank (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (P : LinearProjectorFamily 𝕜 X I) (hPA : ∀ i, P.proj i ∈ A)
    (σ : I → J) (C : J) : Cardinal.{u} :=
  packetPureSeedRank (localCornerAlgebra A P hPA σ C) (localPacketFamily P σ C)

/-- A pure vector has either its whole value or zero in a grouped packet. -/
theorem pure_grouped_fixed_or_zero (P : LinearProjectorFamily 𝕜 X I)
    (σ : I → J) (C : J) {x : X} (hx : PacketPure P x) :
    (groupedFamily P σ).proj C x = x ∨ (groupedFamily P σ).proj C x = 0 := by
  classical
  by_cases hx0 : x = 0
  · simp [hx0]
  have hsome : ∃ i, P.proj i x ≠ 0 := by
    by_contra hn
    apply hx0
    rw [← P.complete x]
    apply Finset.sum_eq_zero
    intro i _
    by_contra hi
    exact hn ⟨i, hi⟩
  obtain ⟨i, hi⟩ := hsome
  have hxi := packetPure_mem_range P hx hi
  have hxgroup : x ∈ LinearMap.range ((groupedFamily P σ).proj (σ i)) :=
    original_mem_grouped P σ i ⟨x, hxi⟩
  by_cases hC : C = σ i
  · left
    rw [hC]
    exact (groupedFamily P σ).proj_eq_self_of_mem_range _ hxgroup
  · right
    obtain ⟨y, rfl⟩ := hxgroup
    exact (groupedFamily P σ).orthogonal hC y

/-- Removing zero projectors has no effect on which vectors are packet pure. -/
theorem packetPure_discardZeros_iff (P : LinearProjectorFamily 𝕜 X I) (x : X) :
    PacketPure P.discardZeros x ↔ PacketPure P x := by
  constructor
  · intro hx i hi j hj
    have hi0 : P.proj i ≠ 0 := by intro h; exact hi (by rw [h]; rfl)
    have hj0 : P.proj j ≠ 0 := by intro h; exact hj (by rw [h]; rfl)
    exact congrArg Subtype.val (hx (x := ⟨i, hi0⟩) (y := ⟨j, hj0⟩) hi hj)
  · intro hx i hi j hj
    exact Subtype.ext (hx hi hj)

theorem packetPureSeedRank_discardZeros
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    packetPureSeedRank A P.discardZeros = packetPureSeedRank A P := by
  apply le_antisymm
  · obtain ⟨S, hS, hc⟩ := exists_pure_generating_set_card_eq A P
    rw [← hc]
    exact packetPureSeedRank_le_card ⟨hS.1, fun x hx ↦
      (packetPure_discardZeros_iff P x).mpr (hS.2 x hx)⟩
  · obtain ⟨S, hS, hc⟩ := exists_pure_generating_set_card_eq A P.discardZeros
    rw [← hc]
    exact packetPureSeedRank_le_card ⟨hS.1, fun x hx ↦
      (packetPure_discardZeros_iff P x).mp (hS.2 x hx)⟩

end Komorebi.PaperIRelease
