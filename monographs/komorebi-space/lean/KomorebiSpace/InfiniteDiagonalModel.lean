import KomorebiSpace.DiagonalSeriesBounds
import KomorebiSpace.RegularizedHilbertRepair
import KomorebiSpace.BudgetProfile
import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Tactic

/-!
# The actual infinite Hilbert diagonal model

Natural coordinate `j` denotes the printed positive integer `j + 1`.
All vectors below belong to mathlib's real `lp` space at exponent two.
-/

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization
open scoped RealInnerProductSpace

/-- The real Hilbert space on the printed positive integer coordinates. -/
abbrev H : Type := lp (fun _ : ℕ => ℝ) 2

private theorem hilbert_index_pos (j : ℕ) : 0 < index j := by
  unfold index
  positivity

private theorem hilbert_index_ge_one (j : ℕ) : 1 ≤ index j := by
  unfold index
  have hj : (0 : ℝ) ≤ j := Nat.cast_nonneg j
  linarith

private theorem hilbert_denominator_pos (m j : ℕ) :
    0 < (m : ℝ)^2 + (index j)^2 := by
  have hj := hilbert_index_pos j
  positivity

private theorem hilbert_weight_norm_le (j : ℕ) : ‖wCoord j‖ ≤ 1 := by
  rw [wCoord, norm_inv, Real.norm_eq_abs, abs_of_pos (hilbert_index_pos j)]
  exact inv_le_one_of_one_le₀ (hilbert_index_ge_one j)

private theorem hilbert_mem_of_sq_summable (f : ℕ → ℝ)
    (hf : Summable (fun j => f j ^ 2)) : Memℓp f 2 := by
  apply memℓp_gen
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, Real.norm_eq_abs, sq_abs] using hf

/-- Coordinate multiplication by the real weights `1/(j+1)`. -/
def Tlinear : H →ₗ[ℝ] H where
  toFun u := ⟨fun j => wCoord j * u j,
    (lp.memℓp u).mono' (fun j => by
      rw [norm_mul]
      exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j))⟩
  map_add' u v := by
    apply lp.ext
    funext j
    change wCoord j * (u j + v j) = wCoord j * u j + wCoord j * v j
    ring
  map_smul' r u := by
    apply lp.ext
    funext j
    change wCoord j * (r * u j) = r * (wCoord j * u j)
    ring

/-- The diagonal operator is bounded, with operator norm at most one. -/
def T : H →L[ℝ] H :=
  Tlinear.mkContinuous 1 (by
    intro u
    rw [one_mul]
    apply lp.norm_mono (by norm_num)
    intro j
    change ‖wCoord j * u j‖ ≤ ‖u j‖
    rw [norm_mul]
    exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j))

@[simp] theorem T_apply (u : H) (j : ℕ) : T u j = wCoord j * u j := rfl

theorem T_norm_le (u : H) : ‖T u‖ ≤ ‖u‖ := by
  apply lp.norm_mono (by norm_num)
  intro j
  rw [T_apply, norm_mul]
  exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j)

theorem T_opNorm_le_one : ‖T‖ ≤ 1 := by
  apply T.opNorm_le_bound (by norm_num)
  intro u
  simpa only [one_mul] using T_norm_le u

/-- Self-adjointness is proved from the infinite Hilbert inner product. -/
theorem T_adjoint : T.adjoint = T := by
  apply ContinuousLinearMap.ext
  intro x
  apply ext_inner_right ℝ
  intro y
  rw [ContinuousLinearMap.adjoint_inner_left, lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro j
  simp only [T_apply, Real.inner_apply]
  ring

theorem T_isSelfAdjoint : IsSelfAdjoint T :=
  ContinuousLinearMap.isSelfAdjoint_iff'.mpr T_adjoint

/-- No nonzero coordinate is killed by `T`. -/
theorem T_injective : Function.Injective T := by
  intro x y h
  apply lp.ext
  funext j
  have hj := congrArg (fun u : H => u j) h
  simp only [T_apply] at hj
  exact mul_left_cancel₀ (inv_ne_zero (ne_of_gt (hilbert_index_pos j))) hj

/-- The escaping datum `w_j = 1/(j+1)` is square summable. -/
def w : H := ⟨wCoord, hilbert_mem_of_sq_summable _ summable_wCoord_sq⟩

/-- The exact candidate regularized correction. -/
def a (m : ℕ) : H := ⟨aCoord m, hilbert_mem_of_sq_summable _ (summable_aCoord_sq m)⟩

/-- The residual family in the actual Hilbert space. -/
def v (m : ℕ) : H := ⟨vCoord m, hilbert_mem_of_sq_summable _ (summable_vCoord_sq m)⟩

/-- The attainable datum `b_j = 1/(j+1)^2`. -/
def b : H := T w

/-- Candidate regularized correction for the attainable datum. -/
def c (m : ℕ) : H := T (a m)

@[simp] theorem w_apply (j : ℕ) : w j = wCoord j := rfl
@[simp] theorem a_apply (m j : ℕ) : a m j = aCoord m j := rfl
@[simp] theorem v_apply (m j : ℕ) : v m j = vCoord m j := rfl

@[simp] theorem b_apply (j : ℕ) : b j = bCoord j := by
  change wCoord j * wCoord j = bCoord j
  simp [wCoord, bCoord, pow_two, mul_inv_rev]

@[simp] theorem c_apply (m j : ℕ) : c m j = cCoord m j := by
  change wCoord j * aCoord m j = cCoord m j
  unfold wCoord aCoord cCoord
  simp only [div_eq_mul_inv, mul_inv_rev]
  ring

/-- The regularization parameter is exactly the inverse square of the integer. -/
def alpha (m : ℕ) : ℝ := ((m : ℝ)^2)⁻¹

theorem alpha_pos {m : ℕ} (hm : 1 ≤ m) : 0 < alpha m := by
  have hmp : 0 < (m : ℝ) := by exact_mod_cast (show 0 < m by omega)
  unfold alpha
  positivity

private theorem hilbert_a_normal_coord {m : ℕ} (hm : 1 ≤ m) (j : ℕ) :
    wCoord j * (wCoord j * aCoord m j) + alpha m * aCoord m j =
      wCoord j * wCoord j := by
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  have hj0 := ne_of_gt (hilbert_index_pos j)
  have hd0 := ne_of_gt (hilbert_denominator_pos m j)
  unfold wCoord aCoord alpha
  field_simp [hm0, hj0, hd0]

/-- The coordinate candidate solves the universal normal equation. -/
theorem a_normal {m : ℕ} (hm : 1 ≤ m) :
    RegularizedHilbertRepair.normal T (alpha m) (a m) = T.adjoint w := by
  rw [RegularizedHilbertRepair.normal_apply, T_adjoint]
  apply lp.ext
  funext j
  change wCoord j * (wCoord j * aCoord m j) + alpha m * aCoord m j =
    wCoord j * wCoord j
  exact hilbert_a_normal_coord hm j

/-- Equality with the universal unique regularized correction. -/
theorem a_eq_correction {m : ℕ} (hm : 1 ≤ m) :
    a m = RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) w :=
  RegularizedHilbertRepair.normal_unique T (alpha m) (alpha_pos hm) w (a m) (a_normal hm)

/-- The actual infinite residual has the printed coordinates. -/
theorem residual_eq_v (m : ℕ) : w - T (a m) = v m := by
  apply lp.ext
  funext j
  change wCoord j - wCoord j * aCoord m j = vCoord m j
  have hj0 := ne_of_gt (hilbert_index_pos j)
  have hd0 := ne_of_gt (hilbert_denominator_pos m j)
  unfold wCoord aCoord vCoord
  field_simp [hj0, hd0]
  ring

/-- The Hilbert norm is the actual infinite sum, not a finite-prefix surrogate. -/
theorem norm_sq_eq_tsum (x : H) : ‖x‖^2 = ∑' j, (x j)^2 := by
  rw [← real_inner_self_eq_norm_sq, lp.inner_eq_tsum]
  apply tsum_congr
  intro j
  simp only [Real.inner_apply, pow_two]

theorem norm_a_sq (m : ℕ) : ‖a m‖^2 = A m := by
  rw [norm_sq_eq_tsum]
  rfl

theorem norm_v_sq (m : ℕ) : ‖v m‖^2 = B m := by
  rw [norm_sq_eq_tsum]
  rfl

theorem norm_residual_sq (m : ℕ) : ‖w - T (a m)‖^2 = B m := by
  rw [residual_eq_v, norm_v_sq]

@[simp] theorem T_w_eq_b : T w = b := rfl

/-- The attainable datum has the unique preimage `w`. -/
theorem b_preimage_unique (x : H) (hx : T x = b) : x = w :=
  T_injective hx

/-- In particular, `w` is a minimum-norm preimage of `b`. -/
theorem w_minimum_norm_preimage (x : H) (hx : T x = b) : ‖w‖ ≤ ‖x‖ := by
  rw [b_preimage_unique x hx]

/-- Commutativity of the actual diagonal operators transports the normal equation. -/
theorem c_normal {m : ℕ} (hm : 1 ≤ m) :
    RegularizedHilbertRepair.normal T (alpha m) (c m) = T.adjoint b := by
  have h := congrArg T (a_normal hm)
  simpa only [RegularizedHilbertRepair.normal_apply, T_adjoint, map_add, map_smul,
    c, b] using h

/-- The attainable candidate is also the exact universal regularized correction. -/
theorem c_eq_correction {m : ℕ} (hm : 1 ≤ m) :
    c m = RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) b :=
  RegularizedHilbertRepair.normal_unique T (alpha m) (alpha_pos hm) b (c m) (c_normal hm)

/-- The attainable bias is exactly the escaping problem's residual vector. -/
theorem w_sub_c_eq_v (m : ℕ) : w - c m = v m := residual_eq_v m

theorem norm_bias_sq (m : ℕ) : ‖c m - w‖^2 = B m := by
  rw [norm_sub_rev, w_sub_c_eq_v, norm_v_sq]

theorem norm_a_eq_sqrt_A (m : ℕ) : ‖a m‖ = Real.sqrt (A m) := by
  rw [← norm_a_sq, Real.sqrt_sq (norm_nonneg _)]

theorem norm_v_eq_sqrt_B (m : ℕ) : ‖v m‖ = Real.sqrt (B m) := by
  rw [← norm_v_sq, Real.sqrt_sq (norm_nonneg _)]

/-- The profile is evaluated at the correction's actual infinite Hilbert norm. -/
theorem budget_at_a_norm {m : ℕ} (hm : 1 ≤ m) :
    BudgetProfile.beta T w ‖a m‖ = ‖w - T (a m)‖ := by
  apply le_antisymm (BudgetProfile.beta_le_residual T w (le_refl _))
  obtain ⟨x, hx, he⟩ := BudgetProfile.exists_budget_minimizer T w (norm_nonneg (a m))
  rw [← he]
  rw [a_eq_correction hm] at hx ⊢
  simpa only [norm_sub_rev] using
    RegularizedHilbertRepair.residual_best_at_budget T (alpha m) (alpha_pos hm) w x hx

/-- Exact identification of the infinite budget profile on the regularized budgets. -/
theorem budget_at_sqrt_A {m : ℕ} (hm : 1 ≤ m) :
    BudgetProfile.beta T w (Real.sqrt (A m)) = Real.sqrt (B m) := by
  rw [← norm_a_eq_sqrt_A, budget_at_a_norm hm, residual_eq_v, norm_v_eq_sqrt_B]

/-- Every actual vector has summable squared real coordinates. -/
theorem summable_coordinates_sq (x : H) : Summable (fun j => (x j)^2) := by
  simpa only [Real.inner_apply, pow_two] using (lp.summable_inner (𝕜 := ℝ) x x)

theorem summable_bCoord_sq : Summable (fun j => (bCoord j)^2) := by
  simpa only [b_apply] using summable_coordinates_sq b

theorem summable_cCoord_sq (m : ℕ) : Summable (fun j => (cCoord m j)^2) := by
  simpa only [c_apply] using summable_coordinates_sq (c m)

/-- The hard-prefix correction is a finite sum inside the same infinite Hilbert space. -/
def hardPrefix (N : ℕ) : H := ∑ j ∈ Finset.range N, lp.single 2 j (1 : ℝ)

@[simp] theorem hardPrefix_apply (N j : ℕ) :
    hardPrefix N j = if j < N then 1 else 0 := by
  simp only [hardPrefix, lp.coeFn_sum, Finset.sum_apply, lp.single_apply,
    Finset.sum_pi_single, Finset.mem_range]

/-- Its budget is its actual Hilbert norm, whose square is exactly `N`. -/
theorem norm_hardPrefix_sq (N : ℕ) : ‖hardPrefix N‖^2 = (N : ℝ) := by
  have h := lp.norm_sum_single (p := 2) (by norm_num)
    (fun _ : ℕ => (1 : ℝ)) (Finset.range N)
  simpa [hardPrefix, Real.rpow_two] using h

theorem norm_hardPrefix (N : ℕ) : ‖hardPrefix N‖ = Real.sqrt (N : ℝ) := by
  rw [← norm_hardPrefix_sq, Real.sqrt_sq (norm_nonneg _)]

@[simp] theorem hardPrefix_residual_apply (N j : ℕ) :
    (w - T (hardPrefix N)) j = if j < N then 0 else wCoord j := by
  change wCoord j - wCoord j * hardPrefix N j = _
  rw [hardPrefix_apply]
  split_ifs <;> simp

/-- The hard-prefix residual square is the genuine omitted infinite reciprocal-square tail. -/
theorem norm_hardPrefix_residual_sq (N : ℕ) :
    ‖w - T (hardPrefix N)‖^2 = ∑' j, (wCoord (j + N))^2 := by
  let r : H := w - T (hardPrefix N)
  have hsplit := Summable.sum_add_tsum_nat_add N (summable_coordinates_sq r)
  have hpre : ∑ j ∈ Finset.range N, (r j)^2 = 0 := by
    apply Finset.sum_eq_zero
    intro j hj
    simp [r, hardPrefix_residual_apply, Finset.mem_range.mp hj]
  have htail : (∑' j, (r (j + N))^2) = ∑' j, (wCoord (j + N))^2 := by
    apply tsum_congr
    intro j
    have hj : ¬ j + N < N := by omega
    simp [r, hardPrefix_residual_apply, hj]
  rw [hpre, zero_add] at hsplit
  calc
    ‖r‖^2 = ∑' j, (r j)^2 := norm_sq_eq_tsum r
    _ = ∑' j, (r (j + N))^2 := hsplit.symm
    _ = ∑' j, (wCoord (j + N))^2 := htail

end KomorebiSpace.DiagonalRegularization
