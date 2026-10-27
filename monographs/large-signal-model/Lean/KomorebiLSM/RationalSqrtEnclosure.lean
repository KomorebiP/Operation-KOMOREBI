import Mathlib.Data.Nat.Sqrt
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Data.Rat.Floor
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

/-! P84: the least integer square-root ceiling and exact rational grid
enclosures are computed with integer square root and a final rational test. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalSqrtEnclosure

def integerUpperSqrt (x : ℚ) : ℕ :=
  let m := Nat.sqrt ⌊x⌋₊
  if x≤(m : ℚ)^2 then m else m+1

theorem floor_sqrt_bounds (x : ℚ) (hx : 0≤x) :
    ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)^2≤x ∧ x<(((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)+1)^2 := by
  have hlow : ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)^2≤(⌊x⌋₊ : ℚ) := by
    exact_mod_cast Nat.sqrt_le' ⌊x⌋₊
  have hu : (⌊x⌋₊ : ℚ)+1≤(((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)+1)^2 := by
    exact_mod_cast Nat.succ_le_iff.mpr (Nat.lt_succ_sqrt' ⌊x⌋₊)
  exact ⟨hlow.trans (Nat.floor_le hx),(Nat.lt_floor_add_one x).trans_le hu⟩

theorem integerUpperSqrt_correct (x : ℚ) (hx : 0≤x) : x≤(integerUpperSqrt x : ℚ)^2 := by
  dsimp only [integerUpperSqrt]
  split_ifs with h
  · exact h
  · simpa only [Nat.cast_add,Nat.cast_one] using (floor_sqrt_bounds x hx).2.le

theorem integerUpperSqrt_minimal (x : ℚ) (hx : 0≤x) (j : ℕ) (hj : x≤(j : ℚ)^2) :
    integerUpperSqrt x≤j := by
  dsimp only [integerUpperSqrt]
  split_ifs with h
  · have hs : ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)^2≤(j : ℚ)^2 := (floor_sqrt_bounds x hx).1.trans hj
    have hn : ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)≤(j : ℚ) :=
      (sq_le_sq₀ (by positivity) (by positivity)).mp hs
    exact_mod_cast hn
  · have hn : ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)<(j : ℚ) := by
      have hm : ((Nat.sqrt ⌊x⌋₊ : ℕ) : ℚ)^2<x := lt_of_not_ge h
      exact (sq_lt_sq₀ (by positivity) (by positivity)).mp (hm.trans_le hj)
    have hnat : Nat.sqrt ⌊x⌋₊<j := by exact_mod_cast hn
    exact hnat

def upperSqrt (denominator : ℕ) (x : ℚ) : ℚ :=
  (integerUpperSqrt (x*(denominator : ℚ)^2) : ℚ)/(denominator : ℚ)

theorem upperSqrt_nonneg (denominator : ℕ) (x : ℚ) : 0≤upperSqrt denominator x := by
  exact div_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _)

/-- The rational upper endpoint is a true square-root enclosure. -/
theorem upperSqrt_squared (denominator : ℕ) (hd : 0<denominator) (x : ℚ) (hx : 0≤x) :
    x≤(upperSqrt denominator x)^2 := by
  have hdq : (0 : ℚ)<denominator := by exact_mod_cast hd
  have h := integerUpperSqrt_correct (x*(denominator : ℚ)^2) (mul_nonneg hx (sq_nonneg _))
  rw [upperSqrt,div_pow]
  exact (le_div_iff₀ (sq_pos_of_pos hdq)).mpr h

theorem sqrt_le_upperSqrt (denominator : ℕ) (hd : 0<denominator) (x : ℚ) (hx : 0≤x) :
    Real.sqrt (x : ℝ)≤(upperSqrt denominator x : ℝ) := by
  have hsq : (x : ℝ)≤(upperSqrt denominator x : ℝ)^2 := by
    exact_mod_cast upperSqrt_squared denominator hd x hx
  have hn : (0 : ℝ)≤upperSqrt denominator x := by exact_mod_cast upperSqrt_nonneg denominator x
  have hxr : (0 : ℝ)≤x := by exact_mod_cast hx
  nlinarith [Real.sq_sqrt hxr,Real.sqrt_nonneg (x : ℝ)]

/-- This is the smallest rational grid numerator meeting the exact final comparison. -/
theorem upperSqrt_le_grid (denominator : ℕ) (hd : 0<denominator) (x : ℚ) (hx : 0≤x)
    (j : ℕ) (hj : x≤((j : ℚ)/(denominator : ℚ))^2) :
    upperSqrt denominator x≤(j : ℚ)/(denominator : ℚ) := by
  have hdq : (0 : ℚ)<denominator := by exact_mod_cast hd
  have hs : x*(denominator : ℚ)^2≤(j : ℚ)^2 := by
    rw [div_pow] at hj
    exact (le_div_iff₀ (sq_pos_of_pos hdq)).mp hj
  have hm := integerUpperSqrt_minimal (x*(denominator : ℚ)^2) (mul_nonneg hx (sq_nonneg _)) j hs
  apply div_le_div_of_nonneg_right _ hdq.le
  exact_mod_cast hm

/-- An exact mathematical enclosure on real input; on rational input the
integer-square-root implementation below gives exactly the same numerator. -/
noncomputable def realUpperSqrt (denominator : ℕ) (x : ℝ) : ℚ :=
  (⌈(denominator : ℝ)*Real.sqrt x⌉₊ : ℚ)/(denominator : ℚ)

theorem realUpperSqrt_nonneg (denominator : ℕ) (x : ℝ) : 0≤realUpperSqrt denominator x := by
  exact div_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _)

theorem sqrt_le_realUpperSqrt (denominator : ℕ) (hd : 0<denominator) (x : ℝ) :
    Real.sqrt x≤(realUpperSqrt denominator x : ℝ) := by
  have hdr : (0 : ℝ)<denominator := by exact_mod_cast hd
  unfold realUpperSqrt
  push_cast
  exact (le_div_iff₀ hdr).mpr (by simpa only [mul_comm] using Nat.le_ceil ((denominator : ℝ)*Real.sqrt x))

theorem realUpperSqrt_rat (denominator : ℕ) (hd : 0<denominator) (x : ℚ) (hx : 0≤x) :
    realUpperSqrt denominator (x : ℝ)=upperSqrt denominator x := by
  have hdr : (0 : ℝ)<denominator := by exact_mod_cast hd
  have hxr : (0 : ℝ)≤x := by exact_mod_cast hx
  have he : ⌈(denominator : ℝ)*Real.sqrt (x : ℝ)⌉₊=
      integerUpperSqrt (x*(denominator : ℚ)^2) := by
    apply le_antisymm
    · apply Nat.ceil_le.mpr
      have h := sqrt_le_upperSqrt denominator hd x hx
      dsimp only [upperSqrt] at h
      push_cast at h
      simpa only [mul_comm] using (le_div_iff₀ hdr).mp h
    · apply integerUpperSqrt_minimal _ (mul_nonneg hx (sq_nonneg _))
      have hc := Nat.le_ceil ((denominator : ℝ)*Real.sqrt (x : ℝ))
      have hs : (x : ℝ)*(denominator : ℝ)^2≤
          (⌈(denominator : ℝ)*Real.sqrt (x : ℝ)⌉₊ : ℝ)^2 := by
        have hsq := pow_le_pow_left₀ (mul_nonneg hdr.le (Real.sqrt_nonneg (x : ℝ))) hc 2
        rw [mul_pow,Real.sq_sqrt hxr] at hsq
        simpa only [mul_comm] using hsq
      exact_mod_cast hs
  simp only [realUpperSqrt,upperSqrt,he]

end Komorebi.LSM.RationalSqrtEnclosure
