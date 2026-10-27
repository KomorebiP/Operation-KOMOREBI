import PaperX.QuadraticLocalCompletion
import PaperX.PadicQuadraticSplitting
import PaperX.QuadraticGaloisInertia

/-! Explicit local arithmetic conditions and their simultaneous completion.
The arithmetic prime is independent of the coefficient prime. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticLocalArithmetic
open PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
open PaperX.QuadraticLocalGalois PaperX.QuadraticLocalPackets
open PaperX.QuadraticLocalCompletion PaperX.QuadraticArithmeticCompletion
open PaperX.QuadraticGaloisInertia PaperX.PadicQuadraticSplitting

variable (p : ℕ) [Fact p.Prime]
variable {B : Type*} [CommRing B]

theorem localQuotient_trivial_iff_mod_four :
    localQuotient ℚ_[p] = 1 ↔ p % 4 = 1 := by
  rw [localQuotient_trivial_iff, root_iff_mod_four_eq_one]

theorem localQuotient_surjective_of_not_split (hp : p % 4 ≠ 1) :
    Function.Surjective (localQuotient ℚ_[p]) :=
  localQuotient_surjective ℚ_[p] (fun h => hp ((root_iff_mod_four_eq_one p).mp h))

theorem locallyTrivial_iff_mod_four (χ : Packet B) :
    LocallyTrivial ℚ_[p] χ ↔ p % 4 = 1 ∨ χ = ofRoot (oneRoot B) := by
  rw [locallyTrivial_iff, root_iff_mod_four_eq_one]

theorem nonsplit_localCharacter_injective (hp : p % 4 ≠ 1) :
    Function.Injective (localCharacter ℚ_[p] (B := B)) :=
  localCharacter_injective ℚ_[p] (fun h => hp ((root_iff_mod_four_eq_one p).mp h))

/-- The sign character's local behavior is determined at every actual prime. -/
theorem sign_locallyTrivial_iff :
    LocallyTrivial ℚ_[p] (ofRoot (negativeRoot ℤ_[2])) ↔ p % 4 = 1 := by
  rw [locallyTrivial_iff_mod_four]
  exact or_iff_left dyadic_packets_distinct.symm

/-- Modulo four is sufficient uniformly in the arithmetic prime. -/
theorem dyadic_trivial_iff_mod_four (χ : Packet ℤ_[2]) :
    χ = ofRoot (oneRoot ℤ_[2]) ↔
      mapPacket (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) χ =
        ofRoot (oneRoot (ZMod 4)) := by
  constructor
  · rintro rfl
    exact mapPacket_oneRoot _
  · intro h
    rcases dyadic_packet_classification χ with hχ | hχ
    · exact hχ
    · have hn := dyadic_packets_separated_mod_four
      rw [mapPacket_oneRoot] at hn
      exact False.elim (hn (hχ ▸ h).symm)

theorem dyadic_local_detection_mod_four (χ : Packet ℤ_[2]) :
    LocallyTrivial ℚ_[p] χ ↔
      LocallyTrivial ℚ_[p]
        (mapPacket (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) χ) := by
  rw [locallyTrivial_iff_mod_four, locallyTrivial_iff_mod_four,
    dyadic_trivial_iff_mod_four]
  rfl

theorem sign_not_locallyTrivial_three :
    ¬ LocallyTrivial ℚ_[3] (ofRoot (negativeRoot ℤ_[2])) := by
  rw [sign_locallyTrivial_iff]
  decide +kernel

theorem sign_not_locallyTrivial_two :
    ¬ LocallyTrivial ℚ_[2] (ofRoot (negativeRoot ℤ_[2])) := by
  rw [sign_locallyTrivial_iff]
  decide +kernel

/-- Residual local triviality is insufficient in dyadic coefficient characteristic. -/
theorem sign_residual_locallyTrivial_three :
    LocallyTrivial ℚ_[3]
      (mapPacket (PadicInt.toZMod : ℤ_[2] →+* ZMod 2)
        (ofRoot (negativeRoot ℤ_[2]))) := by
  rw [← dyadic_packets_same_residual, mapPacket_oneRoot]
  exact oneRoot_locallyTrivial ℚ_[3]

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- A split place does not distinguish the two distinct global characters. -/
theorem sign_locallyTrivial_five :
    LocallyTrivial ℚ_[5] (ofRoot (negativeRoot ℤ_[2])) := by
  rw [sign_locallyTrivial_iff]

/-- Actual odd-prime inertia triviality is weaker than local triviality. -/
theorem sign_inertiaTrivial_three : InertiaTrivial 3 (ofRoot (negativeRoot ℤ_[2])) :=
  inertiaTrivial_of_odd 3 (by decide) _

variable {R : Type} [CommRing R] (I : Ideal R)
variable {S : Type*} (prime : S → ℕ) [∀ s, Fact (prime s).Prime]

/-- The finite conditions are explicit arithmetic equations. Their limit satisfies
all selected local restrictions and every odd-prime valuation inertia condition. -/
theorem arithmetic_local_completion_iff [IsAdicComplete I R] [TopologicalSpace R]
    (C : Conditions I) (finite : ∀ k, Finite (R ⧸ I ^ (k + 1))) :
    (∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ ∧
      (∀ s, LocallyTrivial ℚ_[prime s] χ) ∧
      (∀ (l : ℕ) (hl : Fact l.Prime), l ≠ 2 → @InertiaTrivial l hl R _ χ)) ↔
      ∀ k, ∃ χ, C.allowed k χ ∧
        ∀ s, prime s % 4 = 1 ∨ χ = ofRoot (oneRoot (R ⧸ I ^ (k + 1))) := by
  constructor
  · rintro ⟨χ, hc, hC, hL, _⟩
    have h := (local_completion_iff I (fun s => ℚ_[prime s]) C finite).mp
      ⟨χ, hc, hC, hL⟩
    intro k
    obtain ⟨ψ, hψ, hloc⟩ := h k
    exact ⟨ψ, hψ, fun s => (locallyTrivial_iff_mod_four (prime s) ψ).mp (hloc s)⟩
  · intro h
    have ho : ∀ k, ∃ χ, C.allowed k χ ∧ ∀ s, LocallyTrivial ℚ_[prime s] χ := by
      intro k
      obtain ⟨ψ, hψ, hloc⟩ := h k
      exact ⟨ψ, hψ, fun s => (locallyTrivial_iff_mod_four (prime s) ψ).mpr (hloc s)⟩
    obtain ⟨χ, hc, hC, hL⟩ :=
      exists_local_realization I (fun s => ℚ_[prime s]) C finite ho
    exact ⟨χ, hc, hC, hL, fun l hl hodd => @inertiaTrivial_of_odd l hl R _ hodd χ⟩

end PaperX.QuadraticLocalArithmetic
