import PaperX.ArithmeticCertificateExample
import Mathlib.Topology.Algebra.Group.Units

/-! The actual quadratic Galois quotient and characters trivial on its kernel.
The kernel is defined by its action on a square root of minus one.
No claim about arithmetic inertia or period invariants is made here. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.QuadraticGalois

open PaperX.CompletionExamples PaperX.ArithmeticCertificateExample

abbrev quotientMap : Field.absoluteGaloisGroup ℚ →* C2 := absoluteQuadraticCharacter

theorem quotientMap_surjective : Function.Surjective quotientMap := by
  intro g
  have hc : ∀ a : C2, a = 1 ∨ a = generator := by decide +kernel
  rcases hc g with rfl | rfl
  · exact ⟨1, map_one quotientMap⟩
  · exact quadraticCharacter_hits_generator

theorem quotientMap_eq_one_iff (σ : Field.absoluteGaloisGroup ℚ) :
    quotientMap σ = 1 ↔ (show GQ from σ) imaginary = imaginary := by
  have hg : generator ≠ (1 : C2) := by decide +kernel
  change quadraticValue (show GQ from σ) = 1 ↔ (show GQ from σ) imaginary = imaginary
  by_cases h : (show GQ from σ) imaginary = imaginary
  · simp [quadraticValue, h]
  · simp [quadraticValue, h, hg]

/-- These are actual Galois characters trivial on the specified arithmetic kernel. -/
def Packet (B : Type*) [CommRing B] :=
  {χ : Field.absoluteGaloisGroup ℚ →* Bˣ // quotientMap.ker ≤ χ.ker}

variable {B C : Type*} [CommRing B] [CommRing C]

/-- Descent is derived from the actual surjective quotient, not supplied as an input. -/
def descentEquiv : Packet B ≃ (C2 →* Bˣ) :=
  quotientMap.liftOfSurjective quotientMap_surjective

@[simp] theorem descent_comp (χ : Packet B) :
    (descentEquiv χ).comp quotientMap = χ.val :=
  congrArg Subtype.val (descentEquiv.left_inv χ)

@[simp] theorem descent_symm_val (ψ : C2 →* Bˣ) :
    (descentEquiv.symm ψ).val = ψ.comp quotientMap := rfl

theorem packet_continuous [TopologicalSpace B] (χ : Packet B) : Continuous χ.val := by
  rw [← descent_comp χ]
  exact (continuous_of_discreteTopology (f := descentEquiv χ)).comp
    absoluteQuadraticCharacter_continuous

theorem packet_finite_image (χ : Packet B) : Set.Finite (Set.range χ.val) := by
  apply (Set.finite_range (descentEquiv χ)).subset
  rintro _ ⟨σ, rfl⟩
  exact ⟨quotientMap σ, congrArg (fun ψ : Field.absoluteGaloisGroup ℚ →* Bˣ => ψ σ)
    (descent_comp χ)⟩

def mapPacket (f : B →+* C) (χ : Packet B) : Packet C :=
  ⟨(Units.map f.toMonoidHom).comp χ.val, by
    intro σ hσ
    change Units.map f.toMonoidHom (χ.val σ) = 1
    rw [show χ.val σ = 1 from χ.property hσ, map_one]⟩

@[simp] theorem mapPacket_apply (f : B →+* C) (χ : Packet B)
    (σ : Field.absoluteGaloisGroup ℚ) :
    ↑((mapPacket f χ).val σ) = f (χ.val σ) := rfl

theorem mapPacket_id (χ : Packet B) : mapPacket (RingHom.id B) χ = χ := by
  apply Subtype.ext
  ext σ
  rfl

theorem mapPacket_comp {D : Type*} [CommRing D]
    (f : B →+* C) (g : C →+* D) (χ : Packet B) :
    mapPacket g (mapPacket f χ) = mapPacket (g.comp f) χ := by
  apply Subtype.ext
  ext σ
  rfl

theorem descent_map (f : B →+* C) (χ : Packet B) :
    descentEquiv (mapPacket f χ) = (Units.map f.toMonoidHom).comp (descentEquiv χ) := by
  apply MonoidHom.ext
  intro g
  obtain ⟨σ, rfl⟩ := quotientMap_surjective g
  have h₁ := congrArg (fun ψ : Field.absoluteGaloisGroup ℚ →* Cˣ => ψ σ)
    (descent_comp (mapPacket f χ))
  have h₂ := congrArg (fun ψ : Field.absoluteGaloisGroup ℚ →* Bˣ => ψ σ)
    (descent_comp χ)
  change descentEquiv (mapPacket f χ) (quotientMap σ) =
    Units.map f.toMonoidHom (descentEquiv χ (quotientMap σ))
  rw [show descentEquiv (mapPacket f χ) (quotientMap σ) = (mapPacket f χ).val σ from h₁,
    show descentEquiv χ (quotientMap σ) = χ.val σ from h₂]
  rfl

end PaperX.QuadraticGalois
