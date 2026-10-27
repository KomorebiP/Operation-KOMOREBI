import PaperXI.HeisenbergRepresentation
import PaperXI.HeisenbergForm
import Mathlib.RepresentationTheory.Irreducible

/-! Transport of the coordinate Heisenberg group and actual representations.
The lift preserves the alternating cocycle in every characteristic. Its use
as the nondegenerate Heisenberg extension requires odd characteristic.
No coordinates on an abstract symplectic space are asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergTransport

open Heisenberg

variable {K X Y Z : Type*} [Field K]
variable [AddCommGroup X] [Module K X] [AddCommGroup Y] [Module K Y]
variable [AddCommGroup Z] [Module K Z]

/-- The position and frequency coordinates together. -/
def vector (a : Element K X) : X × Module.Dual K X := (a.position, a.frequency)

@[simp] theorem vector_mul (a b : Element K X) : vector (a * b) = vector a + vector b := rfl

/-- Preservation of the actual alternating form, with the manuscript's sign. -/
def PreservesForm (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y)) : Prop :=
  ∀ v w, HeisenbergForm.form (e v) (e w) = HeisenbergForm.form v w

theorem preservesForm_refl : PreservesForm (LinearEquiv.refl K (X × Module.Dual K X)) :=
  fun _ _ => rfl

theorem PreservesForm.symm
    {e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y)}
    (he : PreservesForm e) : PreservesForm e.symm := by
  intro v w
  simpa using (he (e.symm v) (e.symm w)).symm

theorem PreservesForm.trans
    {e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y)}
    {f : (Y × Module.Dual K Y) ≃ₗ[K] (Z × Module.Dual K Z)}
    (he : PreservesForm e) (hf : PreservesForm f) : PreservesForm (e.trans f) := by
  intro v w
  exact (hf (e v) (e w)).trans (he v w)

/-- Lift an arbitrary form-preserving coordinate linear equivalence, fixing
the central coordinate. The map need not preserve either polarization. -/
def liftIsometry
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (he : PreservesForm e) : Element K X ≃* Element K Y where
  toFun a := ⟨(e (vector a)).1, (e (vector a)).2, a.central⟩
  invFun a := ⟨(e.symm (vector a)).1, (e.symm (vector a)).2, a.central⟩
  left_inv a := by
    apply Element.ext
    · exact congrArg Prod.fst (e.symm_apply_apply (vector a))
    · exact congrArg Prod.snd (e.symm_apply_apply (vector a))
    · rfl
  right_inv a := by
    apply Element.ext
    · exact congrArg Prod.fst (e.apply_symm_apply (vector a))
    · exact congrArg Prod.snd (e.apply_symm_apply (vector a))
    · rfl
  map_mul' a b := by
    apply Element.ext
    · exact congrArg Prod.fst (e.map_add (vector a) (vector b))
    · exact congrArg Prod.snd (e.map_add (vector a) (vector b))
    · change a.central + b.central + (2 : K)⁻¹ * HeisenbergForm.form (vector a) (vector b) =
        a.central + b.central + (2 : K)⁻¹ * HeisenbergForm.form (e (vector a)) (e (vector b))
      rw [he]

@[simp] theorem liftIsometry_vector
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (he : PreservesForm e) (a : Element K X) :
    vector (liftIsometry e he a) = e (vector a) := rfl

@[simp] theorem liftIsometry_central
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (he : PreservesForm e) (a : Element K X) :
    (liftIsometry e he a).central = a.central := rfl

@[simp] theorem liftIsometry_centralElement
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (he : PreservesForm e) (z : K) :
    liftIsometry e he (centralElement z) = centralElement z := by
  apply Element.ext
  · change (e 0).1 = 0
    simp
  · change (e 0).2 = 0
    simp
  · rfl

@[simp] theorem liftIsometry_refl :
    liftIsometry (LinearEquiv.refl K (X × Module.Dual K X)) preservesForm_refl =
      MulEquiv.refl (Element K X) := by
  ext a <;> rfl

@[simp] theorem liftIsometry_symm
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (he : PreservesForm e) :
    (liftIsometry e he).symm = liftIsometry e.symm he.symm := by
  ext a <;> rfl

@[simp] theorem liftIsometry_trans
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y))
    (f : (Y × Module.Dual K Y) ≃ₗ[K] (Z × Module.Dual K Z))
    (he : PreservesForm e) (hf : PreservesForm f) :
    (liftIsometry e he).trans (liftIsometry f hf) =
      liftIsometry (e.trans f) (he.trans hf) := by
  ext a <;> rfl

section Pullback

variable {k G H W : Type*} [Field k] [Group G] [Group H]
variable [AddCommGroup W] [Module k W]

/-- Pull back an actual representation through a group equivalence. -/
def pullback (e : G ≃* H) (σ : Representation k H W) : Representation k G W :=
  σ.comp e.toMonoidHom

@[simp] theorem pullback_apply (e : G ≃* H) (σ : Representation k H W) (g : G) :
    pullback e σ g = σ (e g) := rfl

@[simp] theorem pullback_refl (σ : Representation k G W) :
    pullback (MulEquiv.refl G) σ = σ := by
  ext
  rfl

theorem pullback_trans {J : Type*} [Group J] (e : G ≃* H) (f : H ≃* J)
    (σ : Representation k J W) :
    pullback e (pullback f σ) = pullback (e.trans f) σ := rfl

@[simp] theorem pullback_symm (e : G ≃* H) (σ : Representation k G W) :
    pullback e (pullback e.symm σ) = σ := by
  ext g
  simp

/-- Surjectivity of the group equivalence identifies all stable subspaces. -/
def pullbackSubrepresentationEquiv (e : G ≃* H) (σ : Representation k H W) :
    Subrepresentation (pullback e σ) ≃o Subrepresentation σ where
  toFun S := ⟨S.toSubmodule, fun h _ hv => by
    simpa using S.apply_mem_toSubmodule (e.symm h) hv⟩
  invFun S := ⟨S.toSubmodule, fun g _ hv => S.apply_mem_toSubmodule (e g) hv⟩
  left_inv _ := Subrepresentation.toSubmodule_injective rfl
  right_inv _ := Subrepresentation.toSubmodule_injective rfl
  map_rel_iff' := Iff.rfl

theorem pullback_irreducible_iff (e : G ≃* H) (σ : Representation k H W) :
    Representation.IsIrreducible (pullback e σ) ↔ Representation.IsIrreducible σ :=
  (pullbackSubrepresentationEquiv e σ).isSimpleOrder_iff

theorem pullback_irreducible (e : G ≃* H) (σ : Representation k H W)
    [Representation.IsIrreducible σ] : Representation.IsIrreducible (pullback e σ) :=
  (pullback_irreducible_iff e σ).mpr inferInstance

/-- Transport scalar action on a parameterized subgroup through an actual
group equivalence. In particular this accepts a supplied extension lift. -/
theorem pullback_scalar_action {C : Type*} (e : G ≃* H)
    (cG : C → G) (cH : C → H) (he : ∀ z, e (cG z) = cH z)
    (σ : Representation k H W) (ψ : C → k)
    (hσ : ∀ z, σ (cH z) = ψ z • LinearMap.id) (z : C) :
    pullback e σ (cG z) = ψ z • LinearMap.id := by
  rw [pullback_apply, he, hσ]

end Pullback

section CentralAction

variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- Central action is preserved by a coordinate group equivalence fixing
the parameterized central subgroup. -/
theorem pullback_central_action
    (e : Element K X ≃* Element K Y)
    (he : ∀ z, e (centralElement z) = centralElement z)
    (σ : Representation ℂ (Element K Y) W) (ψ : AddChar K ℂ)
    (hσ : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) (z : K) :
    pullback e σ (centralElement z) = ψ z • LinearMap.id := by
  rw [pullback_apply, he, hσ]

end CentralAction

end PaperXI.HeisenbergTransport
