theorem A_tail_upper (m K : ℕ) (hK : 1 ≤ K) :
    A m - partialA m K ≤ (m : ℝ)^4 / (3 * (K : ℝ)^3) := by
  rw [A_sub_partial_eq_tsum]
  have hcompare : ∀ j : ℕ, aCoord m (j + K)^2 ≤
      (m : ℝ)^4 * (1 / ((K : ℝ) + j + 1)^4) := by
    intro j
    simpa [index, Nat.cast_add, one_div, add_comm, add_left_comm, add_assoc] using
      aCoord_sq_le_pseries m (j + K)
  calc
    (∑' j, aCoord m (j + K)^2) ≤
        ∑' j : ℕ, (m : ℝ)^4 * (1 / ((K : ℝ) + j + 1)^4) := by
      exact Summable.tsum_le_tsum hcompare
        ((summable_nat_add_iff K).2 (summable_aCoord_sq m))
        ((summable_tail_pseries K 4 (by norm_num)).mul_left _)
    _ = (m : ℝ)^4 * (∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^4) := by
      rw [tsum_mul_left]
    _ ≤ (m : ℝ)^4 * (1 / (3 * (K : ℝ)^3)) := by
      exact mul_le_mul_of_nonneg_left (series_tail_fourth_upper K hK) (by positivity)
    _ = (m : ℝ)^4 / (3 * (K : ℝ)^3) := by ring

theorem B_tail_upper (m K : ℕ) (hK : 1 ≤ K) :
    B m - partialB m K ≤ 1 / (K : ℝ) := by
  rw [B_sub_partial_eq_tsum]
  have hcompare : ∀ j : ℕ, vCoord m (j + K)^2 ≤
      1 / ((K : ℝ) + j + 1)^2 := by
    intro j
    simpa [index, wCoord, Nat.cast_add, one_div, inv_pow, add_comm, add_left_comm,
      add_assoc] using vCoord_sq_le_wCoord_sq m (j + K)
  calc
    (∑' j, vCoord m (j + K)^2) ≤ ∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^2 := by
      exact Summable.tsum_le_tsum hcompare
        ((summable_nat_add_iff K).2 (summable_vCoord_sq m))
        (summable_tail_pseries K 2 (by norm_num))
    _ ≤ 1 / (K : ℝ) := series_tail_sq_upper K hK

theorem A_upper (m : ℕ) (hm : 1 ≤ m) : A m ≤ 4 * (m : ℝ) / 3 := by
  have hmne : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  have ht := A_tail_upper m m hm
  have hp := partialA_upper m m
  have heq : (m : ℝ)^4 / (3 * (m : ℝ)^3) = (m : ℝ) / 3 := by
    field_simp
    <;> ring
  rw [heq] at ht
  linarith

theorem B_upper (m : ℕ) (hm : 1 ≤ m) : B m ≤ 2 / (m : ℝ) := by
  have ht := B_tail_upper m m hm
  have hp := partialB_parameter_upper m hm
  linarith

theorem B_lower (m : ℕ) : 1 / (4 * ((m : ℝ) + 1)) ≤ B m := by
  have htail : 1 / ((m : ℝ) + 1) ≤
      ∑' j : ℕ, 1 / ((m : ℝ) + j + 1)^2 :=
    series_tail_sq_lower m (summable_tail_pseries m 2 (by norm_num))
  have hcompare : ∀ j : ℕ, (1 : ℝ) / 4 * (1 / ((m : ℝ) + j + 1)^2) ≤
      vCoord m (j + m)^2 := by
    intro j
    simpa [index, wCoord, Nat.cast_add, one_div, inv_pow, add_comm, add_left_comm,
      add_assoc] using vCoord_sq_lower_tail m (j + m) (by omega)
  have hc := Summable.tsum_le_tsum hcompare
    ((summable_tail_pseries m 2 (by norm_num)).mul_left ((1 : ℝ) / 4))
    ((summable_nat_add_iff m).2 (summable_vCoord_sq m))
  rw [tsum_mul_left] at hc
  have hn : 0 ≤ partialB m m := by
    exact Finset.sum_nonneg (fun j _ => sq_nonneg _)
  rw [← B_sub_partial_eq_tsum] at hc
  have hr : 1 / (4 * ((m : ℝ) + 1)) = (1 : ℝ) / 4 * (1 / ((m : ℝ) + 1)) := by ring
  rw [hr]
  linarith

theorem proposition_30_1_series (m K : ℕ) (hm : 1 ≤ m) (hmK : m ≤ K) :
    (m : ℝ) / 4 ≤ A m ∧ A m ≤ 4 * (m : ℝ) / 3 ∧
    1 / (4 * ((m : ℝ) + 1)) ≤ B m ∧ B m ≤ 2 / (m : ℝ) ∧
    0 ≤ A m - partialA m K ∧
    A m - partialA m K ≤ (m : ℝ)^4 / (3 * (K : ℝ)^3) ∧
    0 ≤ B m - partialB m K ∧ B m - partialB m K ≤ 1 / (K : ℝ) := by
  have hK : 1 ≤ K := le_trans hm hmK
  exact ⟨A_lower m hm, A_upper m hm, B_lower m, B_upper m hm,
    A_tail_nonneg m K, A_tail_upper m K hK, B_tail_nonneg m K, B_tail_upper m K hK⟩
