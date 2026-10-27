module
public import KomorebiPhysics.StrongReconstruction
public import Mathlib.Analysis.InnerProductSpace.l2Space
public import Mathlib.Analysis.Normed.Group.Tannery
public import Mathlib.Topology.Algebra.InfiniteSum.Real

/-! A basis-independent Hilbert--Schmidt class, realized as an actual Hilbert
sum of operator columns. Every use of the real total sum below carries a
separate square-summability proof. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace HilbertSchmidtCore
open Filter
open scoped Topology BigOperators lp
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

def IsHS (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) : Prop :=
  Summable (fun i => ‖X (b i)‖^2)

def energy (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) : ℝ := ∑' i, ‖X (b i)‖^2

def hsNorm (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) : ℝ := Real.sqrt (energy b X)

/-- The column sequence is an actual l2 Hilbert-sum vector, not formal notation. -/
def columns (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) (hX : IsHS b X) : lp (fun _ : I => H) 2 :=
  ⟨(fun i : I => X (b i)), memℓp_gen (by
    simpa only [IsHS, ENNReal.toReal_ofNat, Real.rpow_two] using hX)⟩

theorem columns_apply (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) (hX : IsHS b X) (i : I) :
    columns b X hX i = X (b i) := rfl

theorem energy_nonneg (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) : 0 ≤ energy b X :=
  tsum_nonneg (fun _ => sq_nonneg _)

theorem norm_nonneg (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) : 0 ≤ hsNorm b X :=
  Real.sqrt_nonneg _

theorem norm_sq (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) :
    hsNorm b X ^ 2 = energy b X := Real.sq_sqrt (energy_nonneg b X)

theorem columns_norm_sq (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) (hX : IsHS b X) :
    ‖columns b X hX‖^2 = energy b X := by
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, columns_apply, energy] using
    lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) (columns b X hX)

theorem columns_norm (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) (hX : IsHS b X) :
    ‖columns b X hX‖ = hsNorm b X := by
  rw [hsNorm, ← columns_norm_sq b X hX, Real.sqrt_sq (_root_.norm_nonneg _)]

theorem basis_parseval (b : HilbertBasis I ℂ H) (x : H) :
    HasSum (fun i => ‖inner ℂ (b i) x‖^2) (‖x‖^2) := by
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, b.repr_apply_apply,
    LinearIsometryEquiv.norm_map] using
    lp.hasSum_norm (by norm_num : 0 < (2 : ENNReal).toReal) (b.repr x)

variable [CompleteSpace H]

theorem entry_adjoint (X : H →L[ℂ] H) (x y : H) :
    ‖inner ℂ y (X x)‖ = ‖inner ℂ x (star X y)‖ := by
  rw [ContinuousLinearMap.star_eq_adjoint, ContinuousLinearMap.adjoint_inner_right]
  exact norm_inner_symm _ _

/-- Genuine joint summability of the squared matrix entries (Tonelli). -/
omit [CompleteSpace H] in
theorem entries_summable (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Summable (fun ij : I × J => ‖inner ℂ (c ij.2) (X (b ij.1))‖^2) := by
  apply (summable_prod_of_nonneg (fun _ => sq_nonneg _)).mpr
  constructor
  · intro i; exact (basis_parseval c (X (b i))).summable
  · simpa only [IsHS, (basis_parseval c _).tsum_eq] using hX

/-- Adjoint membership holds in any second basis, not just the original basis. -/
theorem adjoint_mem (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : IsHS b X) : IsHS c (star X) := by
  have h := (summable_prod_of_nonneg
    (fun ji : J × I => sq_nonneg ‖inner ℂ (c ji.1) (X (b ji.2))‖)).mp
    (entries_summable b c X hX).prod_symm
  simpa only [IsHS, entry_adjoint X, (basis_parseval b _).tsum_eq] using h.2

/-- The Hilbert--Schmidt energy of X equals that of its adjoint. -/
theorem energy_adjoint (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : IsHS b X) : energy b X = energy c (star X) := by
  have h : (∑' j, ∑' i, ‖inner ℂ (c j) (X (b i))‖^2) =
      ∑' i, ∑' j, ‖inner ℂ (c j) (X (b i))‖^2 :=
    (entries_summable b c X hX).tsum_comm
  have hc : ∀ i, (∑' j, ‖inner ℂ (c j) (X (b i))‖^2) = ‖X (b i)‖^2 :=
    fun i => (basis_parseval c (X (b i))).tsum_eq
  rw [show (∑' i, ∑' j, ‖inner ℂ (c j) (X (b i))‖^2) = energy b X by simp only [hc, energy]] at h
  simpa only [energy, entry_adjoint X, (basis_parseval b _).tsum_eq] using h.symm

/-- Membership and norm are independent of the chosen Hilbert basis. -/
theorem basis_independent (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) : IsHS b X ↔ IsHS c X := by
  constructor
  · intro h
    simpa only [star_star] using adjoint_mem c c (star X) (adjoint_mem b c X h)
  · intro h
    simpa only [star_star] using adjoint_mem b b (star X) (adjoint_mem c b X h)

theorem energy_basis_independent (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : IsHS b X) : energy b X = energy c X := by
  calc
    energy b X = energy c (star X) := energy_adjoint b c X hX
    _ = energy c X := by
      simpa only [star_star] using energy_adjoint c c (star X) (adjoint_mem b c X hX)

theorem norm_basis_independent (b : HilbertBasis I ℂ H) (c : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : IsHS b X) : hsNorm b X = hsNorm c X :=
  congrArg Real.sqrt (energy_basis_independent b c X hX)

theorem norm_adjoint (b : HilbertBasis I ℂ H) (X : H →L[ℂ] H) (hX : IsHS b X) :
    hsNorm b (star X) = hsNorm b X :=
  (congrArg Real.sqrt (energy_adjoint b b X hX)).symm

omit [CompleteSpace H] in
theorem sub_mem (b : HilbertBasis I ℂ H) (X Y : H →L[ℂ] H)
    (hX : IsHS b X) (hY : IsHS b Y) : IsHS b (X-Y) := by
  have h := (lp.memℓp (columns b X hX - columns b Y hY)).summable
    (by norm_num : 0 < (2 : ENNReal).toReal)
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, lp.coeFn_sub, Pi.sub_apply,
    columns_apply, sub_apply, IsHS] using h

omit [CompleteSpace H] in
theorem sub_norm_le (b : HilbertBasis I ℂ H) (X Y : H →L[ℂ] H)
    (hX : IsHS b X) (hY : IsHS b Y) : hsNorm b (X-Y) ≤ hsNorm b X + hsNorm b Y := by
  have he : columns b (X-Y) (sub_mem b X Y hX hY) = columns b X hX - columns b Y hY := by
    apply lp.ext; rfl
  rw [← columns_norm b (X-Y) (sub_mem b X Y hX hY), he]
  simpa only [columns_norm] using norm_sub_le (columns b X hX) (columns b Y hY)

/-- Bounded left multiplication preserves the HS class, with its ideal bound. -/
omit [CompleteSpace H] in
theorem left_mem (b : HilbertBasis I ℂ H) (A X : H →L[ℂ] H)
    (hX : IsHS b X) : IsHS b (A*X) := by
  apply Summable.of_nonneg_of_le (fun _ => sq_nonneg _)
    (fun i => ?_) (hX.mul_left (‖A‖^2))
  change ‖A (X (b i))‖^2 ≤ ‖A‖^2*‖X (b i)‖^2
  nlinarith [A.le_opNorm (X (b i)), _root_.norm_nonneg (A (X (b i))),
    _root_.norm_nonneg A, _root_.norm_nonneg (X (b i))]

omit [CompleteSpace H] in
theorem left_energy_bound (b : HilbertBasis I ℂ H) (A X : H →L[ℂ] H)
    (hX : IsHS b X) : energy b (A*X) ≤ ‖A‖^2 * energy b X := by
  unfold energy
  rw [← tsum_mul_left]
  apply Summable.tsum_le_tsum _ (left_mem b A X hX) (hX.mul_left _)
  intro i
  change ‖A (X (b i))‖^2 ≤ ‖A‖^2 * ‖X (b i)‖^2
  nlinarith [A.le_opNorm (X (b i)), _root_.norm_nonneg (A (X (b i))),
    _root_.norm_nonneg A, _root_.norm_nonneg (X (b i))]

omit [CompleteSpace H] in
theorem left_norm_bound (b : HilbertBasis I ℂ H) (A X : H →L[ℂ] H)
    (hX : IsHS b X) : hsNorm b (A*X) ≤ ‖A‖ * hsNorm b X := by
  have h := left_energy_bound b A X hX
  rw [← norm_sq, ← norm_sq] at h
  rw [← mul_pow] at h
  exact (sq_le_sq₀ (norm_nonneg b (A*X)) (mul_nonneg (_root_.norm_nonneg A) (norm_nonneg b X))).mp h

theorem right_mem (b : HilbertBasis I ℂ H) (A X : H →L[ℂ] H)
    (hX : IsHS b X) : IsHS b (X*A) := by
  have h := adjoint_mem b b (star A * star X) (left_mem b (star A) (star X) (adjoint_mem b b X hX))
  simpa only [star_mul, star_star] using h

theorem right_norm_bound (b : HilbertBasis I ℂ H) (A X : H →L[ℂ] H)
    (hX : IsHS b X) : hsNorm b (X*A) ≤ ‖A‖ * hsNorm b X := by
  rw [← norm_adjoint b (X*A) (right_mem b A X hX), star_mul]
  have h := left_norm_bound b (star A) (star X) (adjoint_mem b b X hX)
  rw [ContinuousLinearMap.star_eq_adjoint A, LinearIsometryEquiv.norm_map, norm_adjoint b X hX] at h
  exact h

end HilbertSchmidtCore
end KomorebiPhysics
