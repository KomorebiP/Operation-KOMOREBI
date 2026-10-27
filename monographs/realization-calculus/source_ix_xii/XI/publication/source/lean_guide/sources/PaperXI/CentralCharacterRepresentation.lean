import PaperXI.CentralCharacterAction

/-! Reconstruction of the actual central-character representation from an
algebra action, with both action roundtrips. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralCharacter
open PaperXI.CentralExtension
variable {Z H A W : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]
variable [AddCommGroup W] [Module ℂ W]

/-- Reconstruct the actual group action from the central coordinate and
canonical quotient-basis operators. -/
def ofAlgebraAction (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) : Representation ℂ H W where
  toFun h := (ζ (coordinate D h) : ℂ) • φ (basis D ζ (D.q h))
  map_one' := by
    simp [basis]
  map_mul' h k := by
    rw [coordinate_mul, D.q.map_mul, ζ.map_mul, ζ.map_mul]
    simp only [Units.val_mul]
    rw [smul_mul_assoc, mul_smul_comm, ← map_mul φ (basis D ζ (D.q h)) (basis D ζ (D.q k)),
      TwistedAlgebra.basis_mul,
      map_smul]
    simp only [scalarCocycle_coeff, smul_smul, mul_assoc]

@[simp] theorem ofAlgebraAction_apply (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) (h : H) :
    ofAlgebraAction D ζ φ h =
      (ζ (coordinate D h) : ℂ) • φ (basis D ζ (D.q h)) := rfl

/-- The reconstructed action has the prescribed character on the distinguished central inclusion. -/
theorem ofAlgebraAction_central (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) (z : Z) :
    ofAlgebraAction D ζ φ (D.i z) = (ζ z : ℂ) • LinearMap.id := by
  simp [basis]
  rfl

/-- Section elements recover the original canonical basis operators. -/
@[simp] theorem ofAlgebraAction_section (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) (a : A) :
    ofAlgebraAction D ζ φ (sectionMap D a) = φ (basis D ζ a) := by
  simp

/-- Every reconstructed group operator is invertible. -/
theorem ofAlgebraAction_isUnit (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) (h : H) :
    IsUnit (ofAlgebraAction D ζ φ h) := by
  rw [← Representation.asGroupHom_apply (ofAlgebraAction D ζ φ) h]
  exact ((ofAlgebraAction D ζ φ).asGroupHom h).isUnit

/-- Forward algebra action and reconstruction recover every original group operator. -/
@[simp] theorem of_toAlgebraAction (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    ofAlgebraAction D ζ (toAlgebraAction D ζ σ hcentral) = σ := by
  apply MonoidHom.ext
  intro h
  exact (action_normal_form D ζ σ hcentral h).symm

/-- Reconstruction and forward extension recover the original algebra homomorphism. -/
@[simp] theorem to_ofAlgebraAction (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) :
    toAlgebraAction D ζ (ofAlgebraAction D ζ φ) (ofAlgebraAction_central D ζ φ) = φ := by
  apply AlgHom.toLinearMap_injective
  apply (basis D ζ).ext
  intro a
  change toAlgebraAction D ζ (ofAlgebraAction D ζ φ)
      (ofAlgebraAction_central D ζ φ) (basis D ζ a) = φ (basis D ζ a)
  rw [toAlgebraAction_basis, ofAlgebraAction_section]

/-- The actual central-character representations on a fixed complex vector
space are equivalent to the actual twisted-algebra actions on that space. -/
def actionEquiv (D : Datum Z H A) (ζ : Z →* ℂˣ) :
    {σ : Representation ℂ H W //
      ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id} ≃
        (Algebra D ζ →ₐ[ℂ] Module.End ℂ W) where
  toFun σ := toAlgebraAction D ζ σ.val σ.property
  invFun φ := ⟨ofAlgebraAction D ζ φ, ofAlgebraAction_central D ζ φ⟩
  left_inv σ := Subtype.ext (of_toAlgebraAction D ζ σ.val σ.property)
  right_inv φ := to_ofAlgebraAction D ζ φ

end PaperXI.CentralCharacter
