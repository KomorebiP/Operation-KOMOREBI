import Mathlib.RepresentationTheory.FiniteIndex
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.Basic.Complex.Basic

/-! Coordinates for genuine induction from the kernel of a finite quotient.
The representative indexed by `q` lies over `q⁻¹`, so the basis action is left translation.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicInduced
open Representation
open scoped Classical
variable {G Q : Type*} [Group G] [Group Q]
variable (d : G →* Q) (r : Q → G) (hr : ∀ q, d (r q) = q⁻¹)

/-- The one dimensional representation defined by a unit-valued character. -/
def scalar {H : Type*} [Group H] (χ : H →* ℂˣ) : Representation ℂ H ℂ where
  toFun h := (χ h : ℂ) • LinearMap.id
  map_one' := by ext; simp
  map_mul' h k := by ext; simp [smul_smul, mul_comm]

@[simp] theorem scalar_apply {H : Type*} [Group H] (χ : H →* ℂˣ)
    (h : H) (a : ℂ) : scalar χ h a = (χ h : ℂ) * a := rfl

/-- Kernel component in the decomposition `x = residual x * r ((d x)⁻¹)`. -/
def residual (x : G) : d.ker :=
  ⟨x * (r (d x)⁻¹)⁻¹, by simp [MonoidHom.mem_ker, hr]⟩

@[simp] theorem residual_rep (q : Q) : residual d r hr (r q) = 1 := by
  apply Subtype.ext
  simp [residual, hr]

@[simp] theorem residual_mul (h : d.ker) (x : G) :
    residual d r hr ((h : G) * x) = h * residual d r hr x := by
  apply Subtype.ext
  have hh : d h = 1 := h.property
  simp [residual, hh, mul_assoc]

variable (χ : d.ker →* ℂˣ)
abbrev CoindSpace := coindV d.ker.subtype (scalar χ)
abbrev coinduced := coind d.ker.subtype (scalar χ)
abbrev IndSpace := IndV d.ker.subtype (scalar χ)
abbrev induced := ind d.ker.subtype (scalar χ)

/-- The covariant function reconstructed from its values on the representatives. -/
def extend (a : Q → ℂ) : CoindSpace d χ :=
  ⟨fun x => (χ (residual d r hr x) : ℂ) * a (d x)⁻¹, by
    intro h x
    have hh : d h = 1 := h.property
    simp [residual_mul, hh, scalar_apply, mul_assoc]⟩

@[simp] theorem extend_rep (a : Q → ℂ) (q : Q) :
    (extend d r hr χ a).1 (r q) = a q := by
  simp [extend, hr]

/-- Evaluation identifies the actual coinduced space with the coordinate space. -/
def coordinates : CoindSpace d χ ≃ₗ[ℂ] (Q → ℂ) where
  toFun f q := f.1 (r q)
  invFun := extend d r hr χ
  left_inv f := by
    apply Subtype.ext
    funext x
    change (χ (residual d r hr x) : ℂ) * f.1 (r (d x)⁻¹) = f.1 x
    have h := f.property (residual d r hr x) (r (d x)⁻¹)
    simpa [residual, scalar_apply] using h.symm
  right_inv a := by funext q; exact extend_rep d r hr χ a q
  map_add' f g := by rfl
  map_smul' c f := by rfl

@[simp] theorem coordinates_apply (f : CoindSpace d χ) (q : Q) :
    coordinates d r hr χ f q = f.1 (r q) := rfl

/-- The actual scalar in the monomial action, read from the group extension. -/
def weight (g : G) (q : Q) : ℂˣ :=
  χ (residual d r hr (r (d g * q) * g))

variable [Fintype Q]

/-- The representative delta functions form a basis of actual coinduction. -/
def coindBasis : Module.Basis Q ℂ (CoindSpace d χ) :=
  (Pi.basisFun ℂ Q).map (coordinates d r hr χ).symm

@[simp] theorem coindBasis_rep (j q : Q) :
    (coindBasis d r hr χ j).1 (r q) = if q = j then 1 else 0 := by
  classical
  change (extend d r hr χ ((Pi.basisFun ℂ Q) j)).1 (r q) = _
  rw [extend_rep]
  simp only [Pi.basisFun_apply]
  by_cases h : q = j
  · subst q; simp
  · rw [ite_eq_right h, Pi.single_eq_of_ne h]

/-- Monomial action on the genuine covariant-function basis. -/
theorem coindBasis_action (g : G) (j : Q) :
    coinduced d χ g (coindBasis d r hr χ j) =
      (weight d r hr χ g j : ℂ) • coindBasis d r hr χ (d g * j) := by
  classical
  apply (coordinates d r hr χ).injective
  funext q
  change (coindBasis d r hr χ j).1 (r q * g) =
    (weight d r hr χ g j : ℂ) * (coindBasis d r hr χ (d g * j)).1 (r q)
  have h := (coindBasis d r hr χ j).property
    (residual d r hr (r q * g)) (r (d (r q * g))⁻¹)
  have hv : (coindBasis d r hr χ j).1 (r q * g) =
      (χ (residual d r hr (r q * g)) : ℂ) *
      (if (d g)⁻¹ * q = j then 1 else 0) := by
    simpa [residual, scalar_apply, hr, coindBasis_rep] using h
  rw [hv, coindBasis_rep]
  by_cases hq : q = d g * j
  · subst q
    simp [weight]
  · have hn : (d g)⁻¹ * q ≠ j := by
      intro he
      apply hq
      calc q = d g * ((d g)⁻¹ * q) := by simp
           _ = d g * j := by rw [he]
    simp [hq, hn]

/-- The standard finite-index induction/coinduction equivalence. -/
def indCoind : (induced d χ).Equiv (coinduced d χ) := by
  classical
  exact Representation.equivOfIso (Rep.indCoindIso (Rep.of (scalar χ)))

/-- An actual basis of induction, obtained from the canonical finite-index isomorphism. -/
def basis : Module.Basis Q ℂ (IndSpace d χ) :=
  (coindBasis d r hr χ).map (indCoind d χ).toLinearEquiv.symm

/-- Formula for the action on the actual induced representation, not an assumed model. -/
theorem basis_action (g : G) (j : Q) :
    induced d χ g (basis d r hr χ j) =
      (weight d r hr χ g j : ℂ) • basis d r hr χ (d g * j) := by
  apply (indCoind d χ).injective
  have hi := Representation.IntertwiningMap.isIntertwining (induced d χ) (coinduced d χ)
    (indCoind d χ).toIntertwiningMap g (basis d r hr χ j)
  change (indCoind d χ).toLinearEquiv _ = coinduced d χ g ((indCoind d χ).toLinearEquiv _) at hi
  rw [hi]
  simp only [basis, Module.Basis.map_apply, LinearEquiv.apply_symm_apply,
    map_smul]
  exact coindBasis_action d r hr χ g j

/-- Conjugation by a representative restricts to the normal kernel. -/
def conjugate (q : Q) : d.ker →* d.ker where
  toFun h := ⟨r q * (h : G) * (r q)⁻¹, by
    have hh : d h = 1 := h.property
    simp [MonoidHom.mem_ker, hh]⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' h k := by apply Subtype.ext; simp [mul_assoc]

/-- The inertia character visible on the corresponding basis line. -/
def conjugateCharacter (q : Q) : d.ker →* ℂˣ :=
  χ.comp (conjugate d r q)

omit [Fintype Q] in
@[simp] theorem weight_kernel (h : d.ker) (j : Q) :
    weight d r hr χ h j = conjugateCharacter d r χ j h := by
  have hh : d h = 1 := h.property
  change χ (residual d r hr (r (d h * j) * h)) = χ (conjugate d r j h)
  apply congrArg χ
  apply Subtype.ext
  simp [residual, conjugate, hh, hr]

/-- Kernel elements act diagonally by the conjugated character. -/
theorem basis_action_kernel (h : d.ker) (j : Q) :
    induced d χ h (basis d r hr χ j) =
      (conjugateCharacter d r χ j h : ℂ) • basis d r hr χ j := by
  have hh : d h = 1 := h.property
  simpa [hh] using basis_action d r hr χ (h : G) j

/-- With the identity representative normalized, its line carries the original character. -/
theorem basis_action_origin (hr1 : r 1 = 1) (h : d.ker) :
    induced d χ h (basis d r hr χ 1) = (χ h : ℂ) • basis d r hr χ 1 := by
  rw [basis_action_kernel]
  have hc : conjugateCharacter d r χ 1 h = χ h := by
    apply congrArg χ
    apply Subtype.ext
    simp [conjugate, hr1]
  rw [hc]

end PaperXI.CyclicInduced
