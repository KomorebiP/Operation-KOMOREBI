import KomorebiLSM.RationalSqrtEnclosure
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Data.Nat.Log

/-! P84's logarithms are bounded by integer dyadic ceilings before any
rational confidence arithmetic or endpoint rounding is performed. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalConfidenceArithmetic
open RationalSqrtEnclosure

theorem log_two_lt_seven_tenths : Real.log 2<(7/10 : ℝ) := by
  have hs := Real.sum_le_exp_of_nonneg (by norm_num : (0 : ℝ)≤7/10) 5
  norm_num [Finset.sum_range_succ] at hs
  have he : (2 : ℝ)<Real.exp (7/10) := by linarith
  exact (Real.log_lt_iff_lt_exp (by norm_num : (0 : ℝ)<2)).mpr he

/-- This is literally the ceiling of the real base-two logarithm. -/
noncomputable def ceilLog2 (x : ℝ) : ℤ := ⌈Real.log x/Real.log 2⌉

theorem ceilLog2_nonneg (x : ℝ) (hx : 1≤x) : 0≤ceilLog2 x := by
  apply Int.ceil_nonneg
  exact div_nonneg (Real.log_nonneg hx) (Real.log_nonneg (by norm_num))

theorem log_le_ceilLog2 (x : ℝ) : Real.log x≤(ceilLog2 x : ℝ)*Real.log 2 := by
  exact (div_le_iff₀ (Real.log_pos (by norm_num : (1 : ℝ)<2))).mp (Int.le_ceil _)

/-- The dyadic exponent is computed entirely from rational ceiling and integer clog. -/
def rationalCeilLog2 (x : ℚ) : ℕ := Nat.clog 2 ⌈x⌉₊

theorem rationalCeilLog2_le_iff (x : ℚ) (n : ℕ) :
    rationalCeilLog2 x≤n ↔ x≤(2 : ℚ)^n := by
  rw [rationalCeilLog2,Nat.clog_le_iff_le_pow (by norm_num : 1<(2 : ℕ)),Nat.ceil_le]
  norm_cast

theorem ceilLog2_le_nat_iff (x : ℝ) (hx : 0<x) (n : ℕ) :
    ceilLog2 x≤(n : ℤ) ↔ x≤(2 : ℝ)^n := by
  rw [ceilLog2,Int.ceil_le,div_le_iff₀ (Real.log_pos (by norm_num : (1 : ℝ)<2)),Int.cast_natCast,
    ← Real.log_pow]
  exact Real.log_le_log_iff hx (pow_pos (by norm_num) _)

/-- The exact integer algorithm agrees with the mathematical log ceiling. -/
theorem rationalCeilLog2_eq (x : ℚ) (hx : 1≤x) :
    (rationalCeilLog2 x : ℤ)=ceilLog2 (x : ℝ) := by
  have hxr : (1 : ℝ)≤x := by exact_mod_cast hx
  have hxp : (0 : ℝ)<x := by linarith
  have hz : 0≤ceilLog2 (x : ℝ) := ceilLog2_nonneg _ hxr
  apply le_antisymm
  · have hcast : (((ceilLog2 (x : ℝ)).toNat : ℕ) : ℤ)=ceilLog2 (x : ℝ) := Int.toNat_of_nonneg hz
    have hpowr : (x : ℝ)≤(2 : ℝ)^((ceilLog2 (x : ℝ)).toNat) :=
      (ceilLog2_le_nat_iff _ hxp _).mp (by rw [hcast])
    have hpowq : x≤(2 : ℚ)^((ceilLog2 (x : ℝ)).toNat) := by exact_mod_cast hpowr
    have hn := (rationalCeilLog2_le_iff x _).mpr hpowq
    have hi : (rationalCeilLog2 x : ℤ)≤(((ceilLog2 (x : ℝ)).toNat : ℕ) : ℤ) := by exact_mod_cast hn
    rwa [hcast] at hi
  · apply (ceilLog2_le_nat_iff _ hxp _).mpr
    have hq := (rationalCeilLog2_le_iff x (rationalCeilLog2 x)).mp le_rfl
    exact_mod_cast hq

theorem logarithm_budget (V delta : ℝ) (hV : 1≤V) (hd : 0<delta) (hd1 : delta≤1) :
    Real.log V+2*Real.log (1/delta)≤
      (7/10 : ℝ)*((ceilLog2 V : ℝ)+2*(ceilLog2 (1/delta) : ℝ)) := by
  have hdi : (1 : ℝ)≤1/delta := (le_div_iff₀ hd).mpr (by linarith)
  have hk : (0 : ℝ)≤ceilLog2 V := by exact_mod_cast ceilLog2_nonneg V hV
  have hh : (0 : ℝ)≤ceilLog2 (1/delta) := by exact_mod_cast ceilLog2_nonneg (1/delta) hdi
  have hsum := add_le_add (log_le_ceilLog2 V)
    (mul_le_mul_of_nonneg_left (log_le_ceilLog2 (1/delta)) (by norm_num : (0 : ℝ)≤2))
  have hbound := mul_le_mul_of_nonneg_right log_two_lt_seven_tenths.le (by linarith :
    0≤(ceilLog2 V : ℝ)+2*(ceilLog2 (1/delta) : ℝ))
  nlinarith

noncomputable def scalarRadius (sigma V delta : ℝ) : ℝ :=
  sigma*Real.sqrt ((Real.log V+2*Real.log (1/delta))/V)+Real.sqrt (1/V)

noncomputable def dyadicRadius (sigma V delta : ℝ) : ℝ :=
  sigma*Real.sqrt (((7/10 : ℝ)*((ceilLog2 V : ℝ)+2*(ceilLog2 (1/delta) : ℝ)))/V)+
    Real.sqrt (1/V)

theorem scalarRadius_le_dyadic (sigma V delta : ℝ) (hs : 0≤sigma)
    (hV : 1≤V) (hd : 0<delta) (hd1 : delta≤1) :
    scalarRadius sigma V delta≤dyadicRadius sigma V delta := by
  unfold scalarRadius dyadicRadius
  apply add_le_add _ le_rfl
  apply mul_le_mul_of_nonneg_left _ hs
  apply Real.sqrt_le_sqrt
  exact div_le_div_of_nonneg_right (logarithm_budget V delta hV hd hd1) (by linarith)

/-- All quantities in the submitted upper enclosure are rational. -/
def rationalRadius (denominator : ℕ) (sigma V : ℚ) (k h : ℤ) : ℚ :=
  sigma*upperSqrt denominator (((7/10 : ℚ)*((k : ℚ)+2*(h : ℚ)))/V)+
    upperSqrt denominator (1/V)

def computedRadius (denominator : ℕ) (sigma V delta : ℚ) : ℚ :=
  rationalRadius denominator sigma V (rationalCeilLog2 V) (rationalCeilLog2 (1/delta))

/-- Exact real-input version of the same componentwise outer-enclosure
protocol; rational inputs admit the integer-only implementation above. -/
noncomputable def outerRadius (denominator : ℕ) (sigma : ℚ) (V delta : ℝ) : ℚ :=
  sigma*realUpperSqrt denominator
    (((7/10 : ℝ)*((ceilLog2 V : ℝ)+2*(ceilLog2 (1/delta) : ℝ)))/V)+
      realUpperSqrt denominator (1/V)

theorem outerRadius_nonneg (denominator : ℕ) (sigma : ℚ) (hs : 0≤sigma) (V delta : ℝ) :
    0≤outerRadius denominator sigma V delta :=
  add_nonneg (mul_nonneg hs (realUpperSqrt_nonneg _ _)) (realUpperSqrt_nonneg _ _)

theorem scalarRadius_le_outer (denominator : ℕ) (hden : 0<denominator)
    (sigma : ℚ) (hs : 0≤sigma) (V delta : ℝ) (hV : 1≤V) (hd : 0<delta) (hd1 : delta≤1) :
    scalarRadius sigma V delta≤(outerRadius denominator sigma V delta : ℝ) := by
  apply (scalarRadius_le_dyadic sigma V delta (by exact_mod_cast hs) hV hd hd1).trans
  have ha := sqrt_le_realUpperSqrt denominator hden
    (((7/10 : ℝ)*((ceilLog2 V : ℝ)+2*(ceilLog2 (1/delta) : ℝ)))/V)
  have hb := sqrt_le_realUpperSqrt denominator hden (1/V)
  have hc := add_le_add (mul_le_mul_of_nonneg_left ha (by exact_mod_cast hs : (0 : ℝ)≤sigma)) hb
  simpa only [dyadicRadius,outerRadius,Rat.cast_add,Rat.cast_mul] using hc

theorem dyadicRadius_le_rational (denominator : ℕ) (hden : 0<denominator)
    (sigma V delta : ℚ) (hs : 0≤sigma) (hV : 1≤V) (hd : 0<delta) (hd1 : delta≤1) :
    dyadicRadius sigma V delta≤
      (rationalRadius denominator sigma V (ceilLog2 V) (ceilLog2 (1/(delta : ℝ))) : ℝ) := by
  have hVr : (0 : ℚ)<V := by linarith
  have hdi : (1 : ℝ)≤1/(delta : ℝ) := by
    apply (le_div_iff₀ (by exact_mod_cast hd : (0 : ℝ)<delta)).mpr
    have hd1r : (delta : ℝ)≤1 := by exact_mod_cast hd1
    simpa only [one_mul] using hd1r
  have hk : 0≤ceilLog2 (V : ℝ) := ceilLog2_nonneg _ (by exact_mod_cast hV)
  have hh : 0≤ceilLog2 (1/(delta : ℝ)) := ceilLog2_nonneg _ hdi
  have hx : (0 : ℚ)≤((7/10 : ℚ)*((ceilLog2 (V : ℝ) : ℚ)+2*(ceilLog2 (1/(delta : ℝ)) : ℚ)))/V := by
    positivity
  have ha := sqrt_le_upperSqrt denominator hden _ hx
  have hb := sqrt_le_upperSqrt denominator hden (1/V) (by positivity)
  have hsr : (0 : ℝ)≤sigma := by exact_mod_cast hs
  have hc := add_le_add (mul_le_mul_of_nonneg_left ha hsr) hb
  simpa only [dyadicRadius,rationalRadius,Rat.cast_add,Rat.cast_mul,Rat.cast_div,
    Rat.cast_intCast,Rat.cast_ofNat,Rat.cast_one] using hc

theorem scalarRadius_le_computed (denominator : ℕ) (hden : 0<denominator)
    (sigma V delta : ℚ) (hs : 0≤sigma) (hV : 1≤V) (hd : 0<delta) (hd1 : delta≤1) :
    scalarRadius sigma V delta≤(computedRadius denominator sigma V delta : ℝ) := by
  have hdi : (1 : ℚ)≤1/delta := (le_div_iff₀ hd).mpr (by linarith)
  have heV := rationalCeilLog2_eq V hV
  have hed : (rationalCeilLog2 (1/delta) : ℤ)=ceilLog2 (1/(delta : ℝ)) := by
    simpa only [Rat.cast_div,Rat.cast_one] using rationalCeilLog2_eq (1/delta) hdi
  have h := (scalarRadius_le_dyadic (sigma : ℝ) V delta (by exact_mod_cast hs)
    (by exact_mod_cast hV) (by exact_mod_cast hd) (by exact_mod_cast hd1)).trans
      (dyadicRadius_le_rational denominator hden sigma V delta hs hV hd hd1)
  simpa only [computedRadius,heV,hed] using h

end Komorebi.LSM.RationalConfidenceArithmetic
