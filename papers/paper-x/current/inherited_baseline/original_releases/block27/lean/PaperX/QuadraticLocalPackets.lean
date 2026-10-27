import PaperX.QuadraticLocalGalois
import PaperX.QuadraticGaloisPackets

/-! Actual restriction of the fixed global arithmetic packet.  A local condition
is triviality after the field-induced absolute-Galois-group map.  Its arithmetic
description is proved, and is valid over arbitrary commutative coefficient rings. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticLocalPackets

open PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
open PaperX.QuadraticLocalGalois

variable (K : Type*) [Field K] [CharZero K]
variable {B C : Type*} [CommRing B] [CommRing C]

def localCharacter (χ : Packet B) : Field.absoluteGaloisGroup K →* Bˣ :=
  χ.val.comp (restriction K).toMonoidHom

def LocallyTrivial (χ : Packet B) : Prop := localCharacter K χ = 1

theorem localCharacter_descent (χ : Packet B) :
    localCharacter K χ = (descentEquiv χ).comp (localQuotient K) := by
  rw [localCharacter, ← descent_comp χ]
  rfl

theorem localCharacter_continuous [TopologicalSpace B] (χ : Packet B) :
    Continuous (localCharacter K χ) :=
  (packet_continuous χ).comp (restriction K).continuous

theorem localCharacter_natural (f : B →+* C) (χ : Packet B) :
    localCharacter K (mapPacket f χ) =
      (Units.map f.toMonoidHom).comp (localCharacter K χ) := rfl

theorem locallyTrivial_map (f : B →+* C) (χ : Packet B)
    (h : LocallyTrivial K χ) : LocallyTrivial K (mapPacket f χ) := by
  change localCharacter K (mapPacket f χ) = 1
  rw [localCharacter_natural, show localCharacter K χ = 1 from h]
  ext σ
  exact map_one _

theorem mapPacket_oneRoot (f : B →+* C) :
    mapPacket f (ofRoot (oneRoot B)) = ofRoot (oneRoot C) := by
  rw [ofRoot_natural]
  apply congrArg ofRoot
  apply Subtype.ext
  exact map_one f

theorem oneRoot_locallyTrivial : LocallyTrivial K (ofRoot (oneRoot B)) := by
  change (ofRoot (oneRoot B)).val.comp (restriction K).toMonoidHom = 1
  rw [oneRoot_character]
  rfl

theorem locallyTrivial_of_square (h : ∃ x : K, x ^ 2 = -1) (χ : Packet B) :
    LocallyTrivial K χ := by
  change localCharacter K χ = 1
  rw [localCharacter_descent, (localQuotient_trivial_iff K).mpr h]
  apply MonoidHom.ext
  intro σ
  exact map_one (descentEquiv χ)

/-- A nonsplit field sees the entire fixed global quadratic packet. -/
theorem localCharacter_injective (h : ¬ ∃ x : K, x ^ 2 = -1) :
    Function.Injective (localCharacter K (B := B)) := by
  intro χ ψ heq
  apply descentEquiv.injective
  apply MonoidHom.ext
  intro c
  obtain ⟨σ, rfl⟩ := localQuotient_surjective K h c
  have H := congrArg (fun f : Field.absoluteGaloisGroup K →* Bˣ => f σ) heq
  simpa only [localCharacter_descent, MonoidHom.comp_apply] using H

/-- The local condition is an actual arithmetic disjunction, with no reducedness,
domain, or characteristic restriction on the coefficient ring. -/
theorem locallyTrivial_iff (χ : Packet B) :
    LocallyTrivial K χ ↔ (∃ x : K, x ^ 2 = -1) ∨ χ = ofRoot (oneRoot B) := by
  constructor
  · intro hχ
    by_cases hK : ∃ x : K, x ^ 2 = -1
    · exact Or.inl hK
    · right
      apply localCharacter_injective K hK
      exact hχ.trans (oneRoot_locallyTrivial K).symm
  · rintro (hK | rfl)
    · exact locallyTrivial_of_square K hK χ
    · exact oneRoot_locallyTrivial K

theorem locallyTrivial_iff_oneRoot (h : ¬ ∃ x : K, x ^ 2 = -1) (χ : Packet B) :
    LocallyTrivial K χ ↔ χ = ofRoot (oneRoot B) := by
  rw [locallyTrivial_iff]
  exact or_iff_right h

end PaperX.QuadraticLocalPackets
