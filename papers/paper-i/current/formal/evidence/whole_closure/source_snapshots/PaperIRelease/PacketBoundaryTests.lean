import PaperIRelease.ExactSequences
import PaperIRelease.PacketExactSequence
import PaperIRelease.PacketTopology

/-! Boundary assertions for the new exact-sequence and packet-descent block. -/

set_option autoImplicit false

namespace Komorebi.PaperIRelease.PacketBoundaryTests

open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
open Komorebi.SeedRankBasics

universe u v w

section General

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Ring R] [AddCommGroup M] [Module R M] [Fintype ι]

theorem all_preserve_bot (P : LinearProjectorFamily R M ι) : P.Preserves ⊥ := by
  intro i x hx
  have hx0 : x = 0 := hx
  simp [hx0]

theorem all_preserve_top (P : LinearProjectorFamily R M ι) : P.Preserves ⊤ := by
  intro i x _
  trivial

theorem restriction_to_zero_is_zero (P : LinearProjectorFamily R M ι) (i : ι) :
    (P.restrictTo ⊥ (all_preserve_bot P)).proj i = 0 := by
  apply Subsingleton.elim

theorem quotient_by_whole_is_zero (P : LinearProjectorFamily R M ι) (i : ι) :
    (P.descendTo ⊤ (all_preserve_top P)).proj i = 0 := by
  apply Subsingleton.elim

theorem whole_quotient_has_no_nonzero_packets
    (P : LinearProjectorFamily R M ι) :
    IsEmpty (P.descendTo ⊤ (all_preserve_top P)).NonzeroIndex :=
  ⟨fun i ↦ i.property (quotient_by_whole_is_zero P i.val)⟩

theorem zero_restriction_has_no_nonzero_packets
    (P : LinearProjectorFamily R M ι) :
    IsEmpty (P.restrictTo ⊥ (all_preserve_bot P)).NonzeroIndex :=
  ⟨fun i ↦ i.property (restriction_to_zero_is_zero P i.val)⟩

theorem whole_submodule_packet_exact
    (P : LinearProjectorFamily R M ι) (i : ι) :
    LinearMap.range (P.packetInclusion ⊤ (all_preserve_top P) i) =
      LinearMap.ker (P.packetQuotientMap ⊤ (all_preserve_top P) i) :=
  P.packet_sequence_exact ⊤ (all_preserve_top P) i

theorem zero_submodule_packet_exact
    (P : LinearProjectorFamily R M ι) (i : ι) :
    LinearMap.range (P.packetInclusion ⊥ (all_preserve_bot P) i) =
      LinearMap.ker (P.packetQuotientMap ⊥ (all_preserve_bot P) i) :=
  P.packet_sequence_exact ⊥ (all_preserve_bot P) i

end General

/-- The exact-sequence rank theorem applies to a countably generated free
integer module, so no hidden finite-dimensional instance is being used. -/
theorem infinite_free_quotient_bounds (K : Submodule ℤ (ℕ →₀ ℤ)) :
    seedRank ℤ ((ℕ →₀ ℤ) ⧸ K) ≤ seedRank ℤ (ℕ →₀ ℤ) ∧
      seedRank ℤ (ℕ →₀ ℤ) ≤ seedRank ℤ K + seedRank ℤ ((ℕ →₀ ℤ) ⧸ K) :=
  submodule_quotient_seedRank_bounds K

/-- A nontrivial family exists on a zero module even with no indices. -/
def emptyFamily : LinearProjectorFamily ℤ (Fin 0 → ℤ) (Fin 0) where
  proj i := Fin.elim0 i
  idempotent i := Fin.elim0 i
  orthogonal := by intro i; exact Fin.elim0 i
  complete x := Subsingleton.elim _ _

theorem empty_family_packet_exact :
    Function.Injective (emptyFamily.packetCoordinateInclusion ⊥
      (all_preserve_bot emptyFamily)) ∧
      LinearMap.range (emptyFamily.packetCoordinateInclusion ⊥
        (all_preserve_bot emptyFamily)) =
        LinearMap.ker (emptyFamily.packetCoordinateQuotient ⊥
          (all_preserve_bot emptyFamily)) ∧
      Function.Surjective (emptyFamily.packetCoordinateQuotient ⊥
        (all_preserve_bot emptyFamily)) :=
  emptyFamily.packetCoordinate_shortExact ⊥ (all_preserve_bot emptyFamily)

/-- The first coordinate line is preserved by the packet projections, but
not by the coordinate swap. -/
def horizontal : Submodule ℤ (ℤ × ℤ) := LinearMap.ker (LinearMap.snd ℤ ℤ ℤ)

def swapEnd : Module.End ℤ (ℤ × ℤ) := (LinearEquiv.prodComm ℤ ℤ ℤ).toLinearMap

/-- A concrete obstruction: without invariance an ambient operator need not
admit any quotient operator intertwining with the quotient map. -/
theorem coordinate_swap_cannot_descend :
    ¬ ∃ U : Module.End ℤ ((ℤ × ℤ) ⧸ horizontal),
      U.comp horizontal.mkQ = horizontal.mkQ.comp swapEnd := by
  rintro ⟨U, hU⟩
  have hz : horizontal.mkQ (1, 0) = 0 :=
    (Submodule.Quotient.mk_eq_zero horizontal).mpr (by rfl)
  have h : horizontal.mkQ (0, 1) = 0 := by
    have hpoint := congrArg (fun f : (ℤ × ℤ) →ₗ[ℤ] (ℤ × ℤ) ⧸ horizontal ↦
      f (1, 0)) hU
    change U (horizontal.mkQ (1, 0)) = horizontal.mkQ (0, 1) at hpoint
    simpa [hz] using hpoint.symm
  have hmem := (Submodule.Quotient.mk_eq_zero horizontal).mp h
  change (1 : ℤ) = 0 at hmem
  exact one_ne_zero hmem

/-- The quotient norm estimate includes the degenerate zero quotient. -/
theorem whole_quotient_projector_norm_zero
    {𝕜 : Type u} {X : Type v} {ι : Type w}
    [NontriviallyNormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
    [Fintype ι] (P : LinearProjectorFamily 𝕜 X ι)
    (hP : ∀ i, Continuous (P.proj i)) (i : ι) :
    ‖P.quotientProjectorCLM hP ⊤ (all_preserve_top P) i‖ = 0 := by
  have hzero : P.quotientProjectorCLM hP ⊤ (all_preserve_top P) i = 0 :=
    Subsingleton.elim _ _
  rw [hzero, norm_zero]

/-- In the zero-submodule case the constructed bounded equivalence is still
the literal quotient map on every source-packet representative. -/
theorem zero_submodule_bounded_equiv_mk
    {𝕜 : Type u} {X : Type v} {ι : Type w}
    [NontriviallyNormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
    [Fintype ι] (P : LinearProjectorFamily 𝕜 X ι)
    (hP : ∀ i, Continuous (P.proj i)) (i : ι)
    (x : LinearMap.range (P.proj i)) :
    (P.packetQuotientEquivL hP ⊥ (all_preserve_bot P) i (Submodule.Quotient.mk x) :
      X ⧸ (⊥ : Submodule 𝕜 X)) = (⊥ : Submodule 𝕜 X).mkQ (x : X) := rfl

end Komorebi.PaperIRelease.PacketBoundaryTests

#print axioms Komorebi.PaperIRelease.PacketBoundaryTests.infinite_free_quotient_bounds
#print axioms Komorebi.PaperIRelease.PacketBoundaryTests.empty_family_packet_exact
#print axioms Komorebi.PaperIRelease.PacketBoundaryTests.coordinate_swap_cannot_descend
#print axioms Komorebi.PaperIRelease.PacketBoundaryTests.whole_quotient_projector_norm_zero
