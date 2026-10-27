import PaperXI.CharacterTwist
import PaperXI.CyclicInducedWrap

/-! The projection formula on actual induced spaces, with inertia and return scalars. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedTwist
open PaperXI.CyclicInduced
open PaperXI.CharacterTwist
variable {G Q : Type*} [Group G] [Group Q]
variable (d : G →* Q) (χ : d.ker →* ℂˣ) (ν : G →* ℂˣ)

/-- The product character on the actual inducing subgroup. -/
def character : d.ker →* ℂˣ := χ * ν.comp d.ker.subtype

@[simp] theorem character_apply (h : d.ker) :
    character d χ ν h = χ h * ν h := rfl

/-- Multiplication by the ambient character respects covariant-function equations. -/
def forward (f : CoindSpace d χ) : CoindSpace d (character d χ ν) :=
  ⟨fun x => (ν x : ℂ) * f.1 x, by
    intro h x
    change (ν ((h : G) * x) : ℂ) * f.1 ((h : G) * x) =
      ((χ h * ν h : ℂˣ) : ℂ) * ((ν x : ℂ) * f.1 x)
    have hf := f.property h x
    change f.1 ((h : G) * x) = (χ h : ℂ) * f.1 x at hf
    rw [hf]
    simp [mul_assoc, mul_comm, mul_left_comm]⟩

/-- The inverse multiplies by the inverse ambient character pointwise. -/
def backward (f : CoindSpace d (character d χ ν)) : CoindSpace d χ :=
  ⟨fun x => (ν x : ℂ)⁻¹ * f.1 x, by
    intro h x
    change (ν ((h : G) * x) : ℂ)⁻¹ * f.1 ((h : G) * x) =
      (χ h : ℂ) * ((ν x : ℂ)⁻¹ * f.1 x)
    have hf := f.property h x
    change f.1 ((h : G) * x) = ((χ h * ν h : ℂˣ) : ℂ) * f.1 x at hf
    rw [hf]
    simp only [map_mul, Units.val_mul, mul_inv_rev]
    field_simp⟩

/-- A linear equivalence between the actual covariant function spaces. -/
def coindLinearEquiv : CoindSpace d χ ≃ₗ[ℂ] CoindSpace d (character d χ ν) where
  toFun := forward d χ ν
  invFun := backward d χ ν
  left_inv f := by apply Subtype.ext; funext x; simp [forward, backward]
  right_inv f := by apply Subtype.ext; funext x; simp [forward, backward]
  map_add' f g := by apply Subtype.ext; funext x; simp [forward, mul_add]
  map_smul' a f := by apply Subtype.ext; funext x; simp [forward, mul_left_comm]

/-- Right translation intertwines the pointwise multiplier with scalar twisting. -/
def coindEquiv : Representation.Equiv (twist ν (coinduced d χ))
    (coinduced d (character d χ ν)) :=
  Representation.Equiv.mk (coindLinearEquiv d χ ν) (fun g => by
    ext f x
    change (ν x : ℂ) * ((ν g : ℂ) * f.1 (x*g)) = (ν (x*g) : ℂ) * f.1 (x*g)
    simp [mul_assoc])

variable [Fintype Q]

/-- The projection formula for genuine Mathlib induction from the finite-index kernel. -/
def inducedEquiv : Representation.Equiv
    ((induced d χ).tprod (scalar ν)) (induced d (character d χ ν)) :=
  (tensorEquiv ν (induced d χ)).trans
    ((mapEquiv ν (indCoind d χ)).trans
      ((coindEquiv d χ ν).trans (indCoind d (character d χ ν)).symm))

section Degree
variable (δ : G →* Multiplicative ℤ) (φ : G)
variable (hφ : δ φ = Multiplicative.ofAdd (1 : ℤ)) (n : ℕ) [NeZero n]
variable (ξ : TameDegree.degreeSubgroup δ n →* ℂˣ)

/-- The unramified-twist induction formula for the degree-divisibility subgroup. -/
def degreeEquiv : Representation.Equiv
    ((degreeInduced δ n ξ).tprod (scalar ν))
    (degreeInduced δ n (character (TameDegree.degreeMod δ n) ξ ν)) :=
  inducedEquiv (TameDegree.degreeMod δ n) ξ ν

omit [NeZero n] in
/-- The value at the genuine period element is multiplied by the n-th character power. -/
theorem period_value :
    character (TameDegree.degreeMod δ n) ξ ν (degreePeriod φ δ hφ) =
      ξ (degreePeriod φ δ hφ) * ν φ ^ n := by
  change ξ (degreePeriod φ δ hφ) * ν (φ ^ (n : ℤ)) = _
  simp

/-- The closing scalar is computed on the last basis vector of the twisted induction. -/
theorem closing_basis (j : ZMod n) (hj : j.val + 1 = n) :
    degreeInduced δ n (character (TameDegree.degreeMod δ n) ξ ν) φ
      (degreeBasis δ φ hφ n (character (TameDegree.degreeMod δ n) ξ ν) j) =
    ((ξ (degreePeriod φ δ hφ) * ν φ ^ n : ℂˣ) : ℂ) •
      degreeBasis δ φ hφ n (character (TameDegree.degreeMod δ n) ξ ν) 0 := by
  erw [degreeBasis_phi_of_last φ δ hφ _ j hj, period_value]

omit [NeZero n] in
/-- Unramified means trivial on the specified inertia subgroup; its action is unchanged. -/
theorem inertia_unchanged (I : Subgroup G) (hν : ∀ h : I, ν h = 1) :
    (twist ν (degreeInduced δ n ξ)).comp I.subtype =
      (degreeInduced δ n ξ).comp I.subtype :=
  restrict_eq ν (degreeInduced δ n ξ) I hν

end Degree
end PaperXI.InducedTwist
