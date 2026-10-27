import Mathlib.Analysis.PSeries
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic
import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization

/-- Natural index `j` denotes the printed positive coordinate `j+1`. -/
def index (j : ℕ) : ℝ := (j : ℝ) + 1

def aCoord (m j : ℕ) : ℝ := (m : ℝ)^2 / ((m : ℝ)^2 + (index j)^2)
def vCoord (m j : ℕ) : ℝ := index j / ((m : ℝ)^2 + (index j)^2)
def cCoord (m j : ℕ) : ℝ := (m : ℝ)^2 / (index j * ((m : ℝ)^2 + (index j)^2))
def wCoord (j : ℕ) : ℝ := (index j)⁻¹
def bCoord (j : ℕ) : ℝ := ((index j)^2)⁻¹

def A (m : ℕ) : ℝ := ∑' j, (aCoord m j)^2
def B (m : ℕ) : ℝ := ∑' j, (vCoord m j)^2
def partialA (m K : ℕ) : ℝ := ∑ j ∈ Finset.range K, (aCoord m j)^2
def partialB (m K : ℕ) : ℝ := ∑ j ∈ Finset.range K, (vCoord m j)^2

end KomorebiSpace.DiagonalRegularization


set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
namespace KomorebiSpace.DiagonalRegularization

 theorem index_pos (j : ℕ) : 0 < index j := by
  unfold index
  positivity

 theorem index_ge_one (j : ℕ) : 1 ≤ index j := by
  unfold index
  linarith [show (0 : ℝ) ≤ (j : ℝ) from Nat.cast_nonneg j]

 theorem denominator_pos (m j : ℕ) : 0 < (m : ℝ)^2 + (index j)^2 := by
  have := sq_pos_of_pos (index_pos j)
  positivity

 theorem aCoord_nonneg (m j : ℕ) : 0 ≤ aCoord m j := by
  unfold aCoord
  positivity

 theorem vCoord_nonneg (m j : ℕ) : 0 ≤ vCoord m j := by
  exact le_of_lt (div_pos (index_pos j) (denominator_pos m j))

 theorem wCoord_nonneg (j : ℕ) : 0 ≤ wCoord j := by
  exact inv_nonneg.mpr (index_pos j).le

 theorem aCoord_le_one (m j : ℕ) : aCoord m j ≤ 1 := by
  unfold aCoord
  apply (div_le_one (denominator_pos m j)).mpr
  nlinarith [sq_nonneg (index j)]

 theorem aCoord_sq_le_one (m j : ℕ) : aCoord m j ^ 2 ≤ 1 := by
  simpa using pow_le_pow_left₀ (aCoord_nonneg m j) (aCoord_le_one m j) 2

 theorem aCoord_le_pseries (m j : ℕ) :
    aCoord m j ≤ (m : ℝ)^2 / (index j)^2 := by
  exact div_le_div_of_nonneg_left (sq_nonneg _) (sq_pos_of_pos (index_pos j))
    (le_add_of_nonneg_left (sq_nonneg _))

 theorem aCoord_sq_le_pseries (m j : ℕ) :
    aCoord m j ^ 2 ≤ (m : ℝ)^4 * ((index j)^4)⁻¹ := by
  calc
    aCoord m j ^ 2 ≤ ((m : ℝ)^2 / (index j)^2)^2 :=
      pow_le_pow_left₀ (aCoord_nonneg m j) (aCoord_le_pseries m j) 2
    _ = (m : ℝ)^4 * ((index j)^4)⁻¹ := by ring

 theorem vCoord_le_wCoord (m j : ℕ) : vCoord m j ≤ wCoord j := by
  have hj := index_pos j
  calc
    vCoord m j ≤ index j / (index j)^2 := by
      unfold vCoord
      apply div_le_div_of_nonneg_left hj.le (sq_pos_of_pos hj)
      nlinarith [sq_nonneg (m : ℝ)]
    _ = wCoord j := by
      unfold wCoord
      field_simp [ne_of_gt hj]

 theorem vCoord_sq_le_wCoord_sq (m j : ℕ) :
    vCoord m j ^ 2 ≤ wCoord j ^ 2 :=
  pow_le_pow_left₀ (vCoord_nonneg m j) (vCoord_le_wCoord m j) 2

 theorem summable_index_pow_inv {p : ℕ} (hp : 1 < p) :
    Summable (fun j : ℕ => ((index j)^p)⁻¹) := by
  have h := (summable_nat_add_iff 1).2 (Real.summable_nat_pow_inv.mpr hp)
  simpa [index, Nat.cast_add, Nat.cast_one] using h

 theorem summable_wCoord_sq : Summable (fun j => wCoord j ^ 2) := by
  simpa [wCoord, inv_pow] using (summable_index_pow_inv (p := 2) (by norm_num))

 theorem summable_aCoord_sq (m : ℕ) : Summable (fun j => aCoord m j ^ 2) := by
  exact Summable.of_nonneg_of_le (fun j => sq_nonneg _) (aCoord_sq_le_pseries m)
    ((summable_index_pow_inv (p := 4) (by norm_num)).mul_left ((m : ℝ)^4))

 theorem summable_vCoord_sq (m : ℕ) : Summable (fun j => vCoord m j ^ 2) := by
  exact Summable.of_nonneg_of_le (fun j => sq_nonneg _) (vCoord_sq_le_wCoord_sq m)
    summable_wCoord_sq

theorem aCoord_sq_lower_prefix (m j : ℕ) (_hm : 1 ≤ m) (hj : j < m) :
    (1 : ℝ) / 4 ≤ aCoord m j ^ 2 := by
  have hjm : index j ≤ (m : ℝ) := by
    simpa [index, Nat.cast_add, Nat.cast_one] using
      (show ((j + 1 : ℕ) : ℝ) ≤ (m : ℝ) by exact_mod_cast (Nat.succ_le_of_lt hj))
  have hjnonneg := (index_pos j).le
  have hs : (index j)^2 ≤ (m : ℝ)^2 := pow_le_pow_left₀ hjnonneg hjm 2
  have hh : (1 : ℝ) / 2 ≤ aCoord m j := by
    unfold aCoord
    apply (le_div_iff₀ (denominator_pos m j)).mpr
    nlinarith
  have hsquare := pow_le_pow_left₀ (by norm_num : (0 : ℝ) ≤ 1 / 2) hh 2
  norm_num at hsquare
  exact hsquare

theorem vCoord_sq_upper_parameter (m j : ℕ) (hm : 1 ≤ m) :
    vCoord m j ^ 2 ≤ 1 / (m : ℝ)^2 := by
  have hmpos : 0 < (m : ℝ) := by exact_mod_cast (show 0 < m by omega)
  have hv : vCoord m j ≤ 1 / (m : ℝ) := by
    unfold vCoord
    apply (div_le_div_iff₀ (denominator_pos m j) hmpos).mpr
    have := sq_nonneg (index j - (m : ℝ))
    have := mul_nonneg (index_pos j).le hmpos.le
    nlinarith
  calc
    vCoord m j ^ 2 ≤ (1 / (m : ℝ))^2 :=
      pow_le_pow_left₀ (vCoord_nonneg m j) hv 2
    _ = 1 / (m : ℝ)^2 := by ring

theorem vCoord_sq_lower_tail (m j : ℕ) (hj : m ≤ j) :
    (1 : ℝ) / 4 * wCoord j ^ 2 ≤ vCoord m j ^ 2 := by
  have hjm : (m : ℝ) ≤ index j := by
    have : (m : ℝ) ≤ (j : ℝ) := by exact_mod_cast hj
    unfold index
    linarith
  have hs : (m : ℝ)^2 ≤ (index j)^2 :=
    pow_le_pow_left₀ (Nat.cast_nonneg m) hjm 2
  have hv : wCoord j / 2 ≤ vCoord m j := by
    calc
      wCoord j / 2 = index j / (2 * (index j)^2) := by
        unfold wCoord
        field_simp [ne_of_gt (index_pos j)]
      _ ≤ vCoord m j := by
        unfold vCoord
        apply div_le_div_of_nonneg_left (index_pos j).le (denominator_pos m j)
        linarith
  have hsquare := pow_le_pow_left₀ (div_nonneg (wCoord_nonneg j) (by norm_num)) hv 2
  nlinarith [hsquare]

theorem partialA_le_A (m K : ℕ) : partialA m K ≤ A m := by
  exact Summable.sum_le_tsum (Finset.range K) (fun j _ => sq_nonneg _)
    (summable_aCoord_sq m)

theorem partialB_le_B (m K : ℕ) : partialB m K ≤ B m := by
  exact Summable.sum_le_tsum (Finset.range K) (fun j _ => sq_nonneg _)
    (summable_vCoord_sq m)

theorem A_lower (m : ℕ) (hm : 1 ≤ m) : (m : ℝ) / 4 ≤ A m := by
  calc
    (m : ℝ) / 4 = ∑ j ∈ Finset.range m, (1 : ℝ) / 4 := by simp; ring
    _ ≤ partialA m m := by
      apply Finset.sum_le_sum
      intro j hj
      exact aCoord_sq_lower_prefix m j hm (Finset.mem_range.mp hj)
    _ ≤ A m := partialA_le_A m m

theorem partialA_upper (m K : ℕ) : partialA m K ≤ (K : ℝ) := by
  calc
    partialA m K ≤ ∑ j ∈ Finset.range K, (1 : ℝ) := by
      exact Finset.sum_le_sum (fun j _ => aCoord_sq_le_one m j)
    _ = (K : ℝ) := by simp

theorem partialB_parameter_upper (m : ℕ) (hm : 1 ≤ m) :
    partialB m m ≤ 1 / (m : ℝ) := by
  have hmne : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  calc
    partialB m m ≤ ∑ j ∈ Finset.range m, (1 / (m : ℝ)^2) := by
      exact Finset.sum_le_sum (fun j _ => vCoord_sq_upper_parameter m j hm)
    _ = 1 / (m : ℝ) := by simp; field_simp

theorem A_sub_partial_eq_tsum (m K : ℕ) :
    A m - partialA m K = ∑' j, aCoord m (j + K)^2 := by
  have h := Summable.sum_add_tsum_nat_add K (summable_aCoord_sq m)
  change partialA m K + (∑' j, aCoord m (j + K)^2) = A m at h
  linarith

theorem B_sub_partial_eq_tsum (m K : ℕ) :
    B m - partialB m K = ∑' j, vCoord m (j + K)^2 := by
  have h := Summable.sum_add_tsum_nat_add K (summable_vCoord_sq m)
  change partialB m K + (∑' j, vCoord m (j + K)^2) = B m at h
  linarith

theorem A_tail_nonneg (m K : ℕ) : 0 ≤ A m - partialA m K := by
  exact sub_nonneg.mpr (partialA_le_A m K)

theorem B_tail_nonneg (m K : ℕ) : 0 ≤ B m - partialB m K := by
  exact sub_nonneg.mpr (partialB_le_B m K)

theorem summable_tail_pseries (K p : ℕ) (hp : 1 < p) :
    Summable (fun j : ℕ => 1 / ((K : ℝ) + j + 1)^p) := by
  have h := (summable_nat_add_iff K).2 (summable_index_pow_inv hp)
  simpa [index, Nat.cast_add, one_div, add_comm, add_left_comm, add_assoc] using h


lemma series_tail_sum_range_le_telescope (f g : ℕ → ℝ)
    (hfg : ∀ j, f j ≤ g j - g (j + 1)) (n : ℕ) :
    ∑ j ∈ Finset.range n, f j ≤ g 0 - g n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ]
    calc
      (∑ j ∈ Finset.range n, f j) + f n ≤
          (g 0 - g n) + (g n - g (n + 1)) := add_le_add ih (hfg n)
      _ = g 0 - g (n + 1) := by ring

lemma series_tail_telescope_le_sum_range (f g : ℕ → ℝ)
    (hfg : ∀ j, g j - g (j + 1) ≤ f j) (n : ℕ) :
    g 0 - g n ≤ ∑ j ∈ Finset.range n, f j := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ]
    calc
      g 0 - g (n + 1) = (g 0 - g n) + (g n - g (n + 1)) := by ring
      _ ≤ (∑ j ∈ Finset.range n, f j) + f n := add_le_add ih (hfg n)

lemma series_tail_sq_upper_step (x : ℝ) (hx : 0 < x) :
    1 / (x + 1)^2 ≤ 1 / x - 1 / (x + 1) := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / x - 1 / (x + 1) - 1 / (x + 1)^2 =
      1 / (x * (x + 1)^2) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ 1 / (x * (x + 1)^2) := by positivity
  linarith

lemma series_tail_sq_lower_step (x : ℝ) (hx : 0 < x) :
    1 / x - 1 / (x + 1) ≤ 1 / x^2 := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / x^2 - (1 / x - 1 / (x + 1)) =
      1 / (x^2 * (x + 1)) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ 1 / (x^2 * (x + 1)) := by positivity
  linarith

lemma series_tail_fourth_upper_step (x : ℝ) (hx : 0 < x) :
    1 / (x + 1)^4 ≤ 1 / (3 * x^3) - 1 / (3 * (x + 1)^3) := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / (3 * x^3) - 1 / (3 * (x + 1)^3) - 1 / (x + 1)^4 =
      (6*x^2 + 4*x + 1) / (3*x^3*(x + 1)^4) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ (6*x^2 + 4*x + 1) / (3*x^3*(x + 1)^4) := by positivity
  linarith

lemma series_tail_sq_partial_upper (K n : ℕ) (hK : 1 ≤ K) :
    ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^2 ≤ 1 / (K : ℝ) := by
  have hKpos : 0 < (K : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hK)
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1)^2 ≤
      1 / ((K : ℝ) + j) - 1 / ((K : ℝ) + (j + 1 : ℕ)) := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_sq_upper_step ((K : ℝ) + j) (by positivity)
  have h := series_tail_sum_range_le_telescope
    (fun j => 1 / ((K : ℝ) + j + 1)^2)
    (fun j => 1 / ((K : ℝ) + j)) hstep n
  simp only [Nat.cast_zero, add_zero] at h
  have hnonneg : 0 ≤ 1 / ((K : ℝ) + n) := by positivity
  linarith

lemma series_tail_fourth_partial_upper (K n : ℕ) (hK : 1 ≤ K) :
    ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^4 ≤ 1 / (3 * (K : ℝ)^3) := by
  have hKpos : 0 < (K : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hK)
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1)^4 ≤
      1 / (3 * ((K : ℝ) + j)^3) - 1 / (3 * ((K : ℝ) + (j + 1 : ℕ))^3) := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_fourth_upper_step ((K : ℝ) + j) (by positivity)
  have h := series_tail_sum_range_le_telescope
    (fun j => 1 / ((K : ℝ) + j + 1)^4)
    (fun j => 1 / (3 * ((K : ℝ) + j)^3)) hstep n
  simp only [Nat.cast_zero, add_zero] at h
  have hnonneg : 0 ≤ 1 / (3 * ((K : ℝ) + n)^3) := by positivity
  linarith

lemma series_tail_sq_partial_lower (K n : ℕ) :
    1 / ((K : ℝ) + 1) - 1 / ((K : ℝ) + n + 1) ≤
      ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^2 := by
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1) -
      1 / ((K : ℝ) + (j + 1 : ℕ) + 1) ≤ 1 / ((K : ℝ) + j + 1)^2 := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_sq_lower_step ((K : ℝ) + j + 1) (by positivity)
  have h := series_tail_telescope_le_sum_range
    (fun j => 1 / ((K : ℝ) + j + 1)^2)
    (fun j => 1 / ((K : ℝ) + j + 1)) hstep n
  simpa only [Nat.cast_zero, add_zero] using h

lemma series_tail_sq_upper (K : ℕ) (hK : 1 ≤ K) :
    (∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^2) ≤ 1 / (K : ℝ) := by
  exact Real.tsum_le_of_sum_range_le (fun j => by positivity)
    (fun n => series_tail_sq_partial_upper K n hK)

lemma series_tail_fourth_upper (K : ℕ) (hK : 1 ≤ K) :
    (∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^4) ≤ 1 / (3 * (K : ℝ)^3) := by
  exact Real.tsum_le_of_sum_range_le (fun j => by positivity)
    (fun n => series_tail_fourth_partial_upper K n hK)

lemma series_tail_sq_lower (K : ℕ)
    (hsum : Summable (fun j : ℕ => 1 / ((K : ℝ) + j + 1)^2)) :
    1 / ((K : ℝ) + 1) ≤ ∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^2 := by
  have hinv : Tendsto (fun n : ℕ => 1 / ((K : ℝ) + n + 1)) atTop (𝓝 0) := by
    simpa only [Nat.cast_add, add_comm, add_left_comm, add_assoc] using
      (tendsto_add_atTop_iff_nat K).2 (tendsto_one_div_add_atTop_nhds_zero_nat (𝕜 := ℝ))
  have hleft : Tendsto (fun n : ℕ => 1 / ((K : ℝ) + 1) -
      1 / ((K : ℝ) + n + 1)) atTop (𝓝 (1 / ((K : ℝ) + 1))) := by
    simpa only [sub_zero] using (tendsto_const_nhds (x := 1 / ((K : ℝ) + 1))).sub hinv
  exact le_of_tendsto_of_tendsto' hleft hsum.hasSum.tendsto_sum_nat
    (fun n => series_tail_sq_partial_lower K n)


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

end KomorebiSpace.DiagonalRegularization