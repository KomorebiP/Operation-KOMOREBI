module
public import Euler.CollisionAnalytic
public import Mathlib.NumberTheory.Bernoulli
public import Mathlib.RingTheory.Polynomial.Pochhammer
public import Mathlib.NumberTheory.Padics.PadicVal.Basic
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The small dyadic quotient left after extracting 4^q from a Newton-source tap. -/
def sourceScalarRat (q : ℕ) : ℚ := 2^q / (q+1).factorial

lemma sourceScalarRat_ne_zero (q : ℕ) : sourceScalarRat q ≠ 0 := by
  exact div_ne_zero (pow_ne_zero _ (by norm_num)) (by exact_mod_cast Nat.factorial_ne_zero (q+1))

lemma sourceScalarRat_val (q : ℕ) :
    padicValRat 2 (sourceScalarRat q) = (q:ℤ) - padicValNat 2 (q+1).factorial := by
  rw [sourceScalarRat, padicValRat.div (pow_ne_zero _ (by norm_num))
    (by exact_mod_cast Nat.factorial_ne_zero (q+1)), padicValRat.pow]
  have hp : padicValRat 2 (2:ℚ) = 1 := by
    change padicValRat 2 ((2:ℕ):ℚ) = 1
    rw [padicValRat.of_nat]
    norm_num [padicValNat.self]
  rw [hp, mul_one, padicValRat.of_nat]

lemma sourceScalarRat_val_nonneg (q : ℕ) : 0 ≤ padicValRat 2 (sourceScalarRat q) := by
  rw [sourceScalarRat_val]
  have h := padicValNat_factorial_lt_of_ne_zero 2 (show q+1 ≠ 0 by omega)
  omega

/-- This is the actual rational 2^q/(q+1)! embedded in the dyadic integers. -/
def sourceScalar (q : ℕ) : D :=
  ⟨(sourceScalarRat q : ℚ_[2]), (Padic.norm_le_one_iff_val_nonneg _).mpr
    (by simpa only [Padic.valuation_ratCast] using sourceScalarRat_val_nonneg q)⟩

@[simp] lemma sourceScalar_coe (q : ℕ) :
    (sourceScalar q : ℚ_[2]) = (sourceScalarRat q : ℚ_[2]) := rfl

@[simp] lemma sourceScalar_zero : sourceScalar 0 = 1 := by
  apply Subtype.ext
  simp [sourceScalarRat]

/-- The Newton-source tap is 8^q/(q+1)!, with a visible integral 4^q factor. -/
def sourceTap (q : ℕ) : D := (4:D)^q * sourceScalar q

lemma sourceTap_coe (q : ℕ) :
    (sourceTap q : ℚ_[2]) = (8:ℚ_[2])^q / (q+1).factorial := by
  simp only [sourceTap, PadicInt.coe_mul, PadicInt.coe_pow, sourceScalar_coe,
    sourceScalarRat, Rat.cast_div, Rat.cast_pow, Rat.cast_ofNat, Rat.cast_natCast]
  rw [show ((4:D):ℚ_[2]) = 4 from rfl, ← mul_div_assoc, ← mul_pow]
  norm_num

@[simp] lemma sourceTap_zero : sourceTap 0 = 1 := by simp [sourceTap]

lemma sourceTap_norm_bound (q : ℕ) : ‖sourceTap q‖ ≤ (1/4:ℝ)^q := by
  have hn : ‖(4:D)‖ = (1/4:ℝ) := by
    have hp := PadicInt.norm_p_pow (p:=2) 2
    norm_num at hp ⊢
    exact hp
  rw [sourceTap, norm_mul, norm_pow, hn]
  exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

lemma sourceTap_tendsto : Tendsto (fun q => ‖sourceTap q‖) atTop (𝓝 0) := by
  apply squeeze_zero (fun _ => norm_nonneg _) sourceTap_norm_bound
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

end Komorebi.Euler
