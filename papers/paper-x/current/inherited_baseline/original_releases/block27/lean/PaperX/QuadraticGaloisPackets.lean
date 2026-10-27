import PaperX.QuadraticGalois
import PaperX.QuadraticCharacters
import PaperX.QuadraticPacketBoundary

/-! A natural arithmetic interpretation of the quadratic coordinate ring.
The characters are actual absolute-Galois-group homomorphisms, specified by
triviality on the kernel of the quotient defined by a square root of minus one. -/
set_option autoImplicit false
noncomputable section
open scoped Classical
namespace PaperX.QuadraticGaloisPackets

open PaperX.QuadraticAlgebra PaperX.QuadraticGalois
open PaperX.CompletionExamples PaperX.ArithmeticCertificateExample

variable {B C : Type*} [CommRing B] [CommRing C]

def rootPacketEquiv : Root B ≃ Packet B :=
  QuadraticCharacters.characterEquiv.trans descentEquiv.symm

def ofRoot (x : Root B) : Packet B := rootPacketEquiv x

def rootOf (χ : Packet B) : Root B := rootPacketEquiv.symm χ

@[simp] theorem ofRoot_rootOf (χ : Packet B) : ofRoot (rootOf χ) = χ :=
  rootPacketEquiv.apply_symm_apply χ

@[simp] theorem rootOf_ofRoot (x : Root B) : rootOf (ofRoot x) = x :=
  rootPacketEquiv.symm_apply_apply x

@[simp] theorem ofRoot_val (x : Root B) :
    (ofRoot x).val = (QuadraticCharacters.ofRoot x).comp quotientMap := rfl

theorem ofRoot_apply_val (x : Root B) (σ : Field.absoluteGaloisGroup ℚ) :
    ((ofRoot x).val σ : B) = if quotientMap σ = 1 then 1 else x.val :=
  QuadraticCharacters.ofRoot_apply_val x (quotientMap σ)

theorem ofRoot_injective : Function.Injective (ofRoot (B := B)) :=
  rootPacketEquiv.injective

/-- Coefficient change of the arithmetic character is the actual point reduction. -/
theorem ofRoot_natural (f : B →+* C) (x : Root B) :
    mapPacket f (ofRoot x) = ofRoot (mapRoot f x) := by
  apply Subtype.ext
  apply MonoidHom.ext
  intro σ
  exact congrArg (fun ψ : C2 →* Cˣ => ψ (quotientMap σ))
    (QuadraticCharacters.map_ofRoot f x)

theorem rootOf_natural (f : B →+* C) (χ : Packet B) :
    rootOf (mapPacket f χ) = mapRoot f (rootOf χ) := by
  apply ofRoot_injective
  rw [ofRoot_rootOf, ← ofRoot_natural, ofRoot_rootOf]

variable (R : Type*) [CommRing R] [Algebra R B]

/-- This equivalence identifies actual arithmetic objects, not free-standing labels. -/
def pointPacketEquiv : (CoordinateRing R →ₐ[R] B) ≃ Packet B :=
  (pointEquiv R).trans rootPacketEquiv

@[simp] theorem pointPacketEquiv_apply (p : CoordinateRing R →ₐ[R] B) :
    pointPacketEquiv R p = ofRoot (pointEquiv R p) := rfl

variable [Algebra R C]

theorem pointPacketEquiv_natural (f : B →ₐ[R] C)
    (p : CoordinateRing R →ₐ[R] B) :
    pointPacketEquiv R (f.comp p) = mapPacket f.toRingHom (pointPacketEquiv R p) :=
  (ofRoot_natural f.toRingHom (pointEquiv R p)).symm

variable (B)

def oneRoot : Root B := ⟨1, by simp⟩

def negativeRoot : Root B := ⟨-1, by simp⟩

variable {B}

theorem oneRoot_character : (ofRoot (oneRoot B)).val = 1 := by
  apply MonoidHom.ext
  intro σ
  apply Units.ext
  change ((ofRoot (oneRoot B)).val σ : B) = 1
  rw [ofRoot_apply_val]
  simp [oneRoot]

theorem negativeRoot_character (σ : Field.absoluteGaloisGroup ℚ) :
    ((ofRoot (negativeRoot B)).val σ : B) =
      if (show GQ from σ) imaginary = imaginary then 1 else -1 := by
  rw [ofRoot_apply_val]
  by_cases h : quotientMap σ = 1
  · have hs := (quotientMap_eq_one_iff σ).mp h
    simp [h, hs]
  · have hs : ¬ (show GQ from σ) imaginary = imaginary := by
      intro hs
      exact h ((quotientMap_eq_one_iff σ).mpr hs)
    simp [h, hs, negativeRoot]

/-- The entire integral arithmetic packet has exactly the trivial and sign members. -/
theorem dyadic_packet_classification (χ : Packet ℤ_[2]) :
    χ = ofRoot (oneRoot ℤ_[2]) ∨ χ = ofRoot (negativeRoot ℤ_[2]) := by
  rcases (QuadraticPacketBoundary.dyadic_roots (rootOf χ).val).mp (rootOf χ).property with h | h
  · left
    rw [← ofRoot_rootOf χ]
    exact congrArg ofRoot (Subtype.ext h)
  · right
    rw [← ofRoot_rootOf χ]
    exact congrArg ofRoot (Subtype.ext h)

theorem dyadic_packets_distinct :
    ofRoot (oneRoot ℤ_[2]) ≠ ofRoot (negativeRoot ℤ_[2]) := by
  intro h
  exact QuadraticPacketBoundary.dyadic_signs_distinct
    (congrArg Subtype.val (ofRoot_injective h))

theorem dyadic_packets_same_residual :
    mapPacket (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) (ofRoot (oneRoot ℤ_[2])) =
      mapPacket (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) (ofRoot (negativeRoot ℤ_[2])) := by
  rw [ofRoot_natural, ofRoot_natural]
  apply congrArg ofRoot
  exact Subtype.ext QuadraticPacketBoundary.signs_same_mod_two

theorem dyadic_packets_separated_mod_four :
    mapPacket (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) (ofRoot (oneRoot ℤ_[2])) ≠
      mapPacket (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4)
        (ofRoot (negativeRoot ℤ_[2])) := by
  rw [ofRoot_natural, ofRoot_natural]
  intro h
  exact QuadraticPacketBoundary.signs_distinct_mod_four
    (congrArg Subtype.val (ofRoot_injective h))

/-- The nonlifting scalar is an actual character of G_Q at finite precision. -/
def threePacket : Packet (ZMod 8) :=
  ofRoot ⟨3, QuadraticPacketBoundary.three_root_mod_eight⟩

theorem threePacket_no_lift :
    ¬ ∃ χ : Packet (ZMod 16),
      mapPacket QuadraticPacketBoundary.reduceSixteen χ = threePacket := by
  rintro ⟨χ, hχ⟩
  apply QuadraticPacketBoundary.three_no_root_lift_mod_sixteen
  refine ⟨(rootOf χ).val, (rootOf χ).property, ?_⟩
  have h := congrArg rootOf hχ
  rw [rootOf_natural] at h
  change mapRoot QuadraticPacketBoundary.reduceSixteen (rootOf χ) =
    rootOf (ofRoot ⟨3, QuadraticPacketBoundary.three_root_mod_eight⟩) at h
  rw [rootOf_ofRoot] at h
  exact congrArg Subtype.val h

end PaperX.QuadraticGaloisPackets
