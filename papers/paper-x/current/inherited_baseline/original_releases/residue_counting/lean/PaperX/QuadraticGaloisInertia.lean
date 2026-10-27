import PaperX.QuadraticLocalGalois
import PaperX.QuadraticPadicInertia
import PaperX.QuadraticLocalPackets

/-! Actual inertia restrictions of the fixed global quadratic packet.
The quantified inertia groups are the residue-action kernels inside the
valuation decomposition groups. Local domination is explicitly inhabited. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticGaloisInertia
open PaperX.QuadraticGalois PaperX.QuadraticLocalGalois
open PaperX.QuadraticPadicInertia PaperX.QuadraticLocalPackets

variable (p : ℕ) [Fact p.Prime]
variable {B C : Type*} [CommRing B] [CommRing C]

/-- The inclusion into the actual local absolute Galois group. -/
def decompositionInclusion (A : ValuationSubring (LocalClosure p)) :
    A.decompositionSubgroup ℚ_[p] →* Field.absoluteGaloisGroup ℚ_[p] :=
  (A.decompositionSubgroup ℚ_[p]).subtype

theorem quotient_on_inertia (hodd : p ≠ 2)
    (A : ValuationSubring (LocalClosure p))
    (h : ∀ x : ℤ_[p], integralMap p x ∈ A)
    (σ : A.decompositionSubgroup ℚ_[p]) (hσ : σ ∈ A.inertiaSubgroup ℚ_[p]) :
    localQuotient ℚ_[p] (decompositionInclusion p A σ) = 1 :=
  (localQuotient_eq_one_iff ℚ_[p] _).mpr
    (inertia_fixes_square_neg_one p hodd A h _ (localRoot_sq ℚ_[p]) σ hσ)

theorem packet_on_inertia (hodd : p ≠ 2) (χ : Packet B)
    (A : ValuationSubring (LocalClosure p))
    (h : ∀ x : ℤ_[p], integralMap p x ∈ A)
    (σ : A.decompositionSubgroup ℚ_[p]) (hσ : σ ∈ A.inertiaSubgroup ℚ_[p]) :
    localCharacter ℚ_[p] χ (decompositionInclusion p A σ) = 1 := by
  apply χ.property
  exact quotient_on_inertia p hodd A h σ hσ

/-- Triviality on every actual inertia subgroup above the integral coefficient ring. -/
def InertiaTrivial (χ : Packet B) : Prop :=
  ∀ (A : ValuationSubring (LocalClosure p))
    (_h : ∀ x : ℤ_[p], integralMap p x ∈ A)
    (σ : A.decompositionSubgroup ℚ_[p]), σ ∈ A.inertiaSubgroup ℚ_[p] →
      localCharacter ℚ_[p] χ (decompositionInclusion p A σ) = 1

theorem inertiaTrivial_of_odd (hodd : p ≠ 2) (χ : Packet B) : InertiaTrivial p χ :=
  packet_on_inertia p hodd χ

theorem inertiaTrivial_map (f : B →+* C) (χ : Packet B)
    (hχ : InertiaTrivial p χ) : InertiaTrivial p (mapPacket f χ) := by
  intro A h σ hσ
  rw [localCharacter_natural, MonoidHom.comp_apply, hχ A h σ hσ, map_one]

/-- The inertia statement is nonvacuous: a locally dominating valuation exists. -/
theorem exists_dominating_inertia_trivial (hodd : p ≠ 2) :
    ∃ (A : ValuationSubring (LocalClosure p))
      (h : ∀ x : ℤ_[p], integralMap p x ∈ A),
      IsLocalHom ((integralMap p).codRestrict A.toSubring h) ∧
      ∀ (χ : Packet B) (σ : A.decompositionSubgroup ℚ_[p]),
        σ ∈ A.inertiaSubgroup ℚ_[p] →
          localCharacter ℚ_[p] χ (decompositionInclusion p A σ) = 1 := by
  obtain ⟨A, h, hl⟩ := exists_dominating_valuation p
  exact ⟨A, h, hl, fun χ σ hσ => packet_on_inertia p hodd χ A h σ hσ⟩

end PaperX.QuadraticGaloisInertia
