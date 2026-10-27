import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.Module.Equiv.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank

/-! Scalar loop operators and the faithfulness boundary at rank zero. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.ScalarHolonomy

variable {K G V W : Type*} [Field K] [Group G]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- Scalars act by actual invertible linear operators, including on the zero space. -/
def scalarHom : Kˣ →* (V ≃ₗ[K] V) where
  toFun := LinearEquiv.smulOfUnit
  map_one' := by ext x; simp [LinearEquiv.smulOfUnit]
  map_mul' a b := by ext x; simp [LinearEquiv.smulOfUnit, smul_smul]

@[simp] theorem scalarHom_apply (c : Kˣ) (x : V) :
    scalarHom (V := V) c x = (c : K) • x := rfl

/-- Conjugation transports a scalar operator to the same scalar operator at any rank. -/
theorem scalar_conjugate (U : V ≃ₗ[K] W) (c : Kˣ) :
    ((U.symm.trans (scalarHom c)).trans U) = scalarHom c := by
  ext x
  simp

/-- Changing the identifying isomorphism has no effect on an actual scalar operator. -/
theorem scalar_conjugate_independent (U Q : V ≃ₗ[K] W) (A : V ≃ₗ[K] V)
    (hA : ∃ c : Kˣ, A = scalarHom c) :
    ((U.symm.trans A).trans U) = ((Q.symm.trans A).trans Q) := by
  obtain ⟨c, rfl⟩ := hA
  rw [scalar_conjugate, scalar_conjugate]

/-- A nonzero vector makes the unit scalar identifiable. -/
theorem scalarHom_injective [Nontrivial V] :
    Function.Injective (scalarHom (K := K) (V := V)) := by
  intro a b h
  obtain ⟨x, hx⟩ := exists_ne (0 : V)
  apply Units.ext
  exact (smul_left_injective K hx) (LinearEquiv.congr_fun h x)

/-- Scalarity is a property of the actual operators. -/
def IsScalar (ρ : G →* (V ≃ₗ[K] V)) : Prop :=
  ∀ g, ∃ c : Kˣ, ρ g = scalarHom c

/-- For a nonzero space, scalar loop operators determine a character. -/
def character [Nontrivial V] (ρ : G →* (V ≃ₗ[K] V)) (hρ : IsScalar ρ) : G →* Kˣ where
  toFun g := Classical.choose (hρ g)
  map_one' := by
    apply scalarHom_injective (V := V)
    rw [← Classical.choose_spec (hρ 1), map_one, map_one]
  map_mul' g h := by
    apply scalarHom_injective (V := V)
    rw [← Classical.choose_spec (hρ (g * h)), map_mul, map_mul,
      ← Classical.choose_spec (hρ g), ← Classical.choose_spec (hρ h)]

@[simp] theorem character_spec [Nontrivial V]
    (ρ : G →* (V ≃ₗ[K] V)) (hρ : IsScalar ρ) (g : G) :
    scalarHom (character ρ hρ g) = ρ g := (Classical.choose_spec (hρ g)).symm

theorem character_apply [Nontrivial V]
    (ρ : G →* (V ≃ₗ[K] V)) (hρ : IsScalar ρ) (g : G) (x : V) :
    ρ g x = (character ρ hρ g : K) • x := by
  rw [← character_spec ρ hρ g, scalarHom_apply]

/-- The extracted character is the only scalar character realizing these operators. -/
theorem character_unique [Nontrivial V]
    (ρ : G →* (V ≃ₗ[K] V)) (hρ : IsScalar ρ) (χ : G →* Kˣ)
    (hχ : ∀ g, scalarHom (χ g) = ρ g) : χ = character ρ hρ := by
  apply MonoidHom.ext
  intro g
  apply scalarHom_injective (V := V)
  rw [hχ, character_spec]

/-- Scalar operators on nonzero spaces intertwine exactly when their scalars agree. -/
theorem intertwines_iff [Nontrivial V] (U : V ≃ₗ[K] W) (a b : Kˣ) :
    (∀ x, U (scalarHom a x) = scalarHom b (U x)) ↔ a = b := by
  constructor
  · intro h
    obtain ⟨x, hx⟩ := exists_ne (0 : V)
    have hUx : U x ≠ 0 := by simpa using (U.map_ne_zero_iff).mpr hx
    apply Units.ext
    exact (smul_left_injective K hUx) (by simpa using h x)
  · intro h
    subst b
    intro x
    simp

/-- The matrix intertwining criterion becomes equality of the two scalar characters. -/
theorem character_intertwines_iff [Nontrivial V] [Nontrivial W]
    (ρ : G →* (V ≃ₗ[K] V)) (σ : G →* (W ≃ₗ[K] W))
    (hρ : IsScalar ρ) (hσ : IsScalar σ) (U : V ≃ₗ[K] W) :
    (∀ g x, U (ρ g x) = σ g (U x)) ↔ character ρ hρ = character σ hσ := by
  constructor
  · intro h
    apply MonoidHom.ext
    intro g
    apply (intertwines_iff U _ _).mp
    simpa only [character_spec] using h g
  · intro h g x
    rw [character_apply ρ hρ, character_apply σ hσ, map_smul]
    exact congrArg (fun c : Kˣ => (c : K) • U x) (DFunLike.congr_fun h g)

/-- Ratios of scalar characters are characters even for nonabelian loop groups. -/
def ratio (χ ψ : G →* Kˣ) : G →* Kˣ := ψ * χ⁻¹

@[simp] theorem ratio_apply (χ ψ : G →* Kˣ) (g : G) :
    ratio χ ψ g = ψ g * (χ g)⁻¹ := rfl

theorem ratio_eq_one_iff (χ ψ : G →* Kˣ) : ratio χ ψ = 1 ↔ χ = ψ := by
  constructor
  · intro h
    apply MonoidHom.ext
    intro g
    exact (mul_inv_eq_one.mp (DFunLike.congr_fun h g)).symm
  · intro h
    subst ψ
    apply MonoidHom.ext
    intro g
    exact mul_inv_cancel (χ g)

theorem ratio_apply_eq_one_iff (χ ψ : G →* Kˣ) (g : G) :
    ratio χ ψ g = 1 ↔ χ g = ψ g := by
  change ψ g * (χ g)⁻¹ = 1 ↔ χ g = ψ g
  rw [mul_inv_eq_one]
  exact eq_comm

/-- On a zero space every invertible operator is the same operator. -/
theorem zero_space_operator_eq [Subsingleton V] (A B : V ≃ₗ[K] V) : A = B := by
  ext x
  exact Subsingleton.elim _ _

/-- Consequently the intertwining equations impose no condition on scalar representatives. -/
theorem zero_space_intertwines [Subsingleton V] (U : V ≃ₗ[K] W)
    (A : V ≃ₗ[K] V) (B : W ≃ₗ[K] W) (x : V) : U (A x) = B (U x) := by
  have hx : x = 0 := Subsingleton.elim _ _
  simp [hx]

theorem zero_space_scalar_eq [Subsingleton V] (a b : Kˣ) :
    scalarHom (V := V) a = scalarHom (V := V) b := zero_space_operator_eq _ _

/-- In particular, complex scalar extraction cannot be unique on a zero space. -/
theorem zero_space_complex_not_injective [Module ℂ V] [Subsingleton V] :
    ¬Function.Injective (scalarHom (K := ℂ) (V := V)) := by
  intro h
  have he : (1 : ℂˣ) = -1 := h (zero_space_scalar_eq 1 (-1))
  have hc := congrArg (fun c : ℂˣ => (c : ℂ)) he
  norm_num at hc

end PaperXI.ScalarHolonomy
