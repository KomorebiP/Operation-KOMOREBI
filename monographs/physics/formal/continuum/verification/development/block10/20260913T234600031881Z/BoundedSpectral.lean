module
public import Mathlib.Analysis.InnerProductSpace.l2Space
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.Tactic

/-! Actual bounded diagonal operators on infinite-dimensional l2. The symbol
is a bounded sequence, and the operator norm is proved equal to its sup norm. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace BoundedSpectral
open Filter
open scoped Topology BigOperators lp

abbrev Symbol := lp (fun _ : ℕ => ℂ) ∞
abbrev Space := ℓ²(ℕ, ℂ)

/-- Package a uniformly bounded scalar sequence. -/
def ofBound (a : ℕ → ℂ) (C : ℝ) (h : ∀ n, ‖a n‖ ≤ C) : Symbol :=
  ⟨a, memℓp_infty ⟨C, by rintro _ ⟨n, rfl⟩; exact h n⟩⟩

theorem ofBound_apply (a : ℕ → ℂ) (C : ℝ) (h : ∀ n, ‖a n‖ ≤ C) (n : ℕ) :
    ofBound a C h n = a n := rfl

/-- The product is proved square summable from boundedness, not assumed. -/
def multiply (a : Symbol) (x : Space) : Space :=
  ⟨fun n => a n * x n, ((lp.memℓp x).norm.const_smul ‖a‖).mono (fun n => by
    simpa only [norm_mul, Pi.smul_apply, smul_eq_mul] using
      mul_le_mul_of_nonneg_right (lp.norm_apply_le_norm ENNReal.top_ne_zero a n)
        (norm_nonneg (x n)))⟩

theorem multiply_apply (a : Symbol) (x : Space) (n : ℕ) :
    multiply a x n = a n * x n := rfl

theorem multiply_norm_le (a : Symbol) (x : Space) : ‖multiply a x‖ ≤ ‖a‖ * ‖x‖ := by
  have h : ‖multiply a x‖ ≤ ‖(‖a‖ : ℝ) • x‖ := by
    apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simp only [multiply_apply, norm_mul, lp.coeFn_smul, Pi.smul_apply, norm_smul,
      Real.norm_eq_abs, abs_of_nonneg (norm_nonneg a)]
    exact mul_le_mul_of_nonneg_right (lp.norm_apply_le_norm ENNReal.top_ne_zero a n)
      (norm_nonneg (x n))
  simpa only [norm_smul, Real.norm_eq_abs, abs_of_nonneg (norm_nonneg a)] using h

/-- The actual bounded everywhere-defined multiplier. -/
def diagonal (a : Symbol) : Space →L[ℂ] Space :=
  LinearMap.mkContinuous
    { toFun := multiply a
      map_add' := fun x y => lp.ext (funext fun n => mul_add (a n) (x n) (y n))
      map_smul' := fun c x => lp.ext (funext fun n => mul_left_comm (a n) c (x n)) }
    ‖a‖ (multiply_norm_le a)

theorem diagonal_apply (a : Symbol) (x : Space) (n : ℕ) :
    diagonal a x n = a n * x n := rfl

theorem diagonal_single (a : Symbol) (n : ℕ) (c : ℂ) :
    diagonal a (lp.single 2 n c) = lp.single 2 n (a n * c) := by
  apply lp.ext
  funext k
  by_cases h : k = n
  · subst k; simp [diagonal_apply]
  · simp [diagonal_apply, h]

theorem norm_diagonal_le (a : Symbol) : ‖diagonal a‖ ≤ ‖a‖ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg a)
  exact multiply_norm_le a

theorem symbol_le_norm (a : Symbol) (n : ℕ) : ‖a n‖ ≤ ‖diagonal a‖ := by
  have h := (diagonal a).le_opNorm (lp.single 2 n (1 : ℂ))
  simpa only [diagonal_single, mul_one, lp.norm_single (by norm_num : 0 < (2 : ENNReal)),
    norm_one] using h

theorem norm_diagonal (a : Symbol) : ‖diagonal a‖ = ‖a‖ :=
  le_antisymm (norm_diagonal_le a)
    (lp.norm_le_of_forall_le (norm_nonneg _) (symbol_le_norm a))

theorem diagonal_congr {a b : Symbol} (h : ∀ n, a n = b n) : diagonal a = diagonal b := by
  exact congrArg diagonal (lp.ext (funext h))

theorem diagonal_zero : diagonal 0 = 0 := by
  ext x n
  simp [diagonal_apply]

theorem diagonal_one : diagonal 1 = ContinuousLinearMap.id ℂ Space := by
  ext x n
  simp [diagonal_apply]

theorem diagonal_add (a b : Symbol) : diagonal (a + b) = diagonal a + diagonal b := by
  ext x n
  simp only [diagonal_apply, lp.coeFn_add, Pi.add_apply, add_apply]
  exact add_mul (a n) (b n) (x n)

theorem diagonal_sub (a b : Symbol) : diagonal (a - b) = diagonal a - diagonal b := by
  ext x n
  simp only [diagonal_apply, lp.coeFn_sub, Pi.sub_apply, sub_apply]
  exact sub_mul (a n) (b n) (x n)

theorem diagonal_mul (a b : Symbol) : diagonal (a * b) = (diagonal a).comp (diagonal b) := by
  ext x n
  exact mul_assoc (a n) (b n) (x n)

theorem diagonal_smul (c : ℂ) (a : Symbol) : diagonal (c • a) = c • diagonal a := by
  ext x n
  exact mul_assoc c (a n) (x n)

theorem diagonal_norm_sub (a b : Symbol) : ‖diagonal a - diagonal b‖ = ‖a - b‖ := by
  rw [← diagonal_sub, norm_diagonal]

theorem diagonal_adjoint (a : Symbol) : (diagonal a).adjoint = diagonal (star a) := by
  apply ContinuousLinearMap.adjoint_unique
  intro x y
  rw [lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro n
  simp only [diagonal_apply, RCLike.inner_apply, map_mul]
  change star (a n) * star (x n) * y n = star (x n) * (star (a n) * y n)
  ring

end BoundedSpectral
end KomorebiPhysics
