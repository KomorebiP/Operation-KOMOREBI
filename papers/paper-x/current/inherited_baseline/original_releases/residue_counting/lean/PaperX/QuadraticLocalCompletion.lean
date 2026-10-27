import PaperX.QuadraticLocalPackets
import PaperX.QuadraticArithmeticCompletion

/-! Arithmetic local triviality is closed under completion for the fixed global
quadratic packet.  The local conditions are actual field-induced restrictions,
and their closure is proved rather than assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticLocalCompletion

open PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
open PaperX.QuadraticLocalPackets
open PaperX.QuadraticArithmeticCompletion

variable {R : Type} [CommRing R] (I : Ideal R)
variable (K : Type*) [Field K] [CharZero K]

theorem locallyTrivial_iff_reductions [IsHausdorff I R] (χ : Packet R) :
    LocallyTrivial K χ ↔
      ∀ n, LocallyTrivial K (mapPacket (Ideal.Quotient.mk (I ^ n)) χ) := by
  constructor
  · intro h n
    exact locallyTrivial_map K _ χ h
  · intro h
    by_cases hK : ∃ x : K, x ^ 2 = -1
    · exact locallyTrivial_of_square K hK χ
    · apply (locallyTrivial_iff_oneRoot K hK χ).mpr
      apply packet_ext I
      intro n
      rw [mapPacket_oneRoot]
      exact (locallyTrivial_iff_oneRoot K hK _).mp (h n)

/-- Positive precisions suffice, matching the finite admissible levels. -/
theorem locallyTrivial_iff_positive_reductions [IsHausdorff I R] (χ : Packet R) :
    LocallyTrivial K χ ↔
      ∀ k, LocallyTrivial K (mapPacket (Ideal.Quotient.mk (I ^ (k + 1))) χ) := by
  constructor
  · intro h k
    exact locallyTrivial_map K _ χ h
  · intro h
    apply (locallyTrivial_iff_reductions I K χ).mpr
    intro n
    have H := locallyTrivial_map K (Ideal.Quotient.factorPow I (Nat.le_succ n))
      (mapPacket (Ideal.Quotient.mk (I ^ (n + 1))) χ) (h n)
    have heq :
        mapPacket (Ideal.Quotient.factorPow I (Nat.le_succ n))
          (mapPacket (Ideal.Quotient.mk (I ^ (n + 1))) χ) =
          mapPacket (Ideal.Quotient.mk (I ^ n)) χ := by
      apply Subtype.ext
      ext σ
      change Ideal.Quotient.factorPow I (Nat.le_succ n)
          (Ideal.Quotient.mk (I ^ (n + 1)) (χ.val σ)) =
        Ideal.Quotient.mk (I ^ n) (χ.val σ)
      simp
    rwa [heq] at H

theorem reconstructed_locallyTrivial [IsAdicComplete I R] (x : Family I)
    (h : ∀ n, LocallyTrivial K (x.values n)) :
    LocallyTrivial K (reconstruct I x) := by
  apply (locallyTrivial_iff_reductions I K _).mpr
  intro n
  rw [reconstruct_reduces]
  exact h n

variable {S : Type*} (F : S → Type*) [∀ s, Field (F s)] [∀ s, CharZero (F s)]

/-- All specified local fields are imposed simultaneously.  The index set itself
need not be finite: it defines a subset of each finite coefficient level. -/
def withLocalTriviality (C : Conditions I) : Conditions I where
  allowed k χ := C.allowed k χ ∧ ∀ s, LocallyTrivial (F s) χ
  downward := by
    intro j k hjk χ hχ
    refine ⟨C.downward hjk χ hχ.1, ?_⟩
    intro s
    exact locallyTrivial_map (F s) _ χ (hχ.2 s)

theorem realizes_withLocalTriviality_iff [IsHausdorff I R]
    (C : Conditions I) (χ : Packet R) :
    Realizes I (withLocalTriviality I F C) χ ↔
      Realizes I C χ ∧ ∀ s, LocallyTrivial (F s) χ := by
  constructor
  · intro h
    refine ⟨fun k => (h k).1, ?_⟩
    intro s
    exact (locallyTrivial_iff_positive_reductions I (F s) χ).mpr
      (fun k => (h k).2 s)
  · rintro ⟨hC, hL⟩ k
    exact ⟨hC k, fun s => locallyTrivial_map (F s) _ χ (hL s)⟩

/-- Nonempty admissible finite levels produce an actual global character satisfying
every specified field restriction, without preselected coherent characters. -/
theorem exists_local_realization [IsAdicComplete I R] [TopologicalSpace R]
    (C : Conditions I) (finite : ∀ k, Finite (R ⧸ I ^ (k + 1)))
    (occupied : ∀ k, ∃ χ, C.allowed k χ ∧ ∀ s, LocallyTrivial (F s) χ) :
    ∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ ∧
      ∀ s, LocallyTrivial (F s) χ := by
  obtain ⟨χ, hc, hχ⟩ := exists_realization I (withLocalTriviality I F C) finite occupied
  exact ⟨χ, hc, (realizes_withLocalTriviality_iff I F C χ).mp hχ⟩

theorem local_completion_iff [IsAdicComplete I R] [TopologicalSpace R]
    (C : Conditions I) (finite : ∀ k, Finite (R ⧸ I ^ (k + 1))) :
    (∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ ∧
      ∀ s, LocallyTrivial (F s) χ) ↔
      ∀ k, ∃ χ, C.allowed k χ ∧ ∀ s, LocallyTrivial (F s) χ := by
  constructor
  · rintro ⟨χ, _, hC, hL⟩ k
    exact ⟨mapPacket (Ideal.Quotient.mk (I ^ (k + 1))) χ, hC k,
      fun s => locallyTrivial_map (F s) _ χ (hL s)⟩
  · exact exists_local_realization I F C finite

/-- One nonsplit field forces the completed member to be globally trivial. -/
theorem completion_forced_trivial (s : S) (hs : ¬ ∃ x : F s, x ^ 2 = -1)
    (χ : Packet R) (hχ : ∀ t, LocallyTrivial (F t) χ) :
    χ = ofRoot (oneRoot R) :=
  (locallyTrivial_iff_oneRoot (F s) hs χ).mp (hχ s)

end PaperX.QuadraticLocalCompletion
