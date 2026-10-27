import PaperXI.DyadicAbstractOrthogonal
import Mathlib.LinearAlgebra.Dimension.Constructions

/-! Actual finite orthogonal products of dyadic quadratic refinements.
The index type may be empty and the factors may have dimension zero. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakQuadratic
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine

variable {ι : Type*} [Fintype ι] {V : ι → Type*}
  [∀ i, AddCommGroup (V i)] [∀ i, Module F2 (V i)]

/-- The actual sum of the component bilinear forms on a dependent product. -/
def form (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2) :
    (∀ i, V i) →ₗ[F2] (∀ i, V i) →ₗ[F2] F2 where
  toFun x :=
    { toFun := fun y => ∑ i, b i (x i) (y i)
      map_add' := by intro y z; simp [Finset.sum_add_distrib]
      map_smul' := by intro a y; simp [Finset.mul_sum] }
  map_add' := by intro x y; ext z; simp [Finset.sum_add_distrib]
  map_smul' := by intro a x; ext y; simp [Finset.mul_sum]

@[simp] theorem form_apply (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (x y : ∀ i, V i) : form b x y = ∑ i, b i (x i) (y i) := rfl

theorem form_alternating (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (ha : ∀ i x, b i x x = 0) (x : ∀ i, V i) : form b x x = 0 := by
  simp [ha]

theorem form_single_right (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (x : ∀ i, V i) (j : ι) (y : V j) :
    form b x (Pi.single j y) = b j (x j) y := by
  classical
  rw [form_apply, Finset.sum_eq_single j]
  · simp
  · intro i _ hij
    simp [Pi.single_eq_of_ne hij]
  · simp

theorem form_nondegenerate (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (hn : ∀ i x, (∀ y, b i x y = 0) → x = 0)
    (x : ∀ i, V i) (hx : ∀ y, form b x y = 0) : x = 0 := by
  funext i
  apply hn i (x i)
  intro y
  simpa only [form_single_right] using hx (Pi.single i y)

/-- The quadratic refinement is the actual sum of the supplied refinements. -/
def refinement (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (q : ∀ i, Refinement (b i)) : Refinement (form b) where
  value x := ∑ i, (q i).value (x i)
  polar x y := by
    simp only [Pi.add_apply, Refinement.polar, form_apply, Finset.sum_add_distrib]

@[simp] theorem refinement_apply (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (q : ∀ i, Refinement (b i)) (x : ∀ i, V i) :
    (refinement b q).value x = ∑ i, (q i).value (x i) := rfl

/-- The explicit polar identity identifies the total refinement, not merely
its alternating form. -/
theorem refinement_polar (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (q : ∀ i, Refinement (b i)) (x y : ∀ i, V i) :
    (refinement b q).value (x + y) =
      (refinement b q).value x + (refinement b q).value y + form b x y :=
  (refinement b q).polar x y

/-- The literal Gauss sum of a finite product is the product of the literal
component Gauss sums. No nondegeneracy or dimension hypothesis is needed. -/
theorem gauss_sum_product [∀ i, Fintype (V i)]
    (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2) (q : ∀ i, Refinement (b i)) :
    (∑ x : (∀ i, V i), sign ((refinement b q).value x)) =
      ∏ i, ∑ x : V i, sign ((q i).value x) := by
  simp only [refinement_apply, sign_sum]
  exact (Fintype.prod_sum (fun i x => sign ((q i).value x))).symm

variable [∀ i, FiniteDimensional F2 (V i)]

omit [Fintype ι] in
/-- Each nondegenerate alternating factor has the actual even dimension. -/
theorem finrank_eq_twice_half (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (ha : ∀ i x, b i x x = 0)
    (hn : ∀ i x, (∀ y, b i x y = 0) → x = 0) (i : ι) :
    Module.finrank F2 (V i) = 2 * (Module.finrank F2 (V i) / 2) := by
  obtain ⟨r, hr⟩ := SymplecticCoordinates.even_finrank (b i) (ha i) (hn i)
  omega

/-- The positive square-root normalization uses the sum of actual
half-dimensions, including the empty sum. -/
theorem half_finrank_product (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
    (ha : ∀ i x, b i x x = 0)
    (hn : ∀ i x, (∀ y, b i x y = 0) → x = 0) :
    Module.finrank F2 (∀ i, V i) / 2 =
      ∑ i, Module.finrank F2 (V i) / 2 := by
  rw [Module.finrank_pi_fintype]
  have h : (∑ i, Module.finrank F2 (V i)) =
      2 * ∑ i, Module.finrank F2 (V i) / 2 := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl (fun i _ => finrank_eq_twice_half b ha hn i)
  rw [h]
  omega

end PaperXI.BreakQuadratic
