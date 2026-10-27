module

public import EGFCoordinates
public import Mathlib.RingTheory.PowerSeries.Exp

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.OddPower

open PowerSeries

def expAt (a : ℚ) : PowerSeries ℚ := rescale a (PowerSeries.exp ℚ)

def coshAt (a : ℚ) : PowerSeries ℚ := C (1/2) * (expAt a + expAt (-a))

def sech : PowerSeries ℚ := (coshAt 1)⁻¹

def source (p n : ℕ) : ℤ := ∑ a ∈ Finset.range p, (-1:ℤ)^a * (2*a+1:ℤ)^n

def sourceSeries (p : ℕ) : PowerSeries ℚ := EGF.encode (fun n => (source p n : ℚ))

@[simp] theorem expAt_coeff (a : ℚ) (n : ℕ) : coeff n (expAt a) = a^n / n.factorial := by
  simp [expAt, mul_comm, div_eq_mul_inv]

@[simp] theorem expAt_zero : expAt 0 = 1 := by simp [expAt]

@[simp] theorem expAt_constant (a : ℚ) : constantCoeff (expAt a) = 1 := by
  rw [← coeff_zero_eq_constantCoeff_apply, expAt_coeff]; norm_num

@[simp] theorem rescale_constant (a b : ℚ) : rescale a (C b) = C b := by
  ext n
  cases n <;> simp [coeff_rescale, coeff_C]

theorem expAt_mul (a b : ℚ) : expAt a * expAt b = expAt (a+b) :=
  PowerSeries.exp_mul_exp_eq_exp_add a b

@[simp] theorem cosh_constant (a : ℚ) : constantCoeff (coshAt a) = 1 := by simp [coshAt]; norm_num

@[simp] theorem cosh_neg (a : ℚ) : coshAt (-a) = coshAt a := by simp [coshAt, add_comm]

@[simp] theorem sech_mul_cosh : sech * coshAt 1 = 1 := by
  exact PowerSeries.inv_mul_cancel (coshAt 1) (by simp)

@[simp] theorem cosh_mul_sech : coshAt 1 * sech = 1 := by rw [mul_comm, sech_mul_cosh]

/-- Literal finite alternating odd-power sum, encoded coefficient by coefficient. -/
theorem source_as_exponentials (p : ℕ) :
    sourceSeries p = ∑ a ∈ Finset.range p, C ((-1:ℚ)^a) * expAt (2*a+1) := by
  ext n
  simp only [sourceSeries, EGF.encode_coeff, source, Int.cast_sum, Int.cast_mul,
    Int.cast_pow, Int.cast_neg, Int.cast_one, Int.cast_add, Int.cast_ofNat, Int.cast_natCast,
    map_sum, coeff_C_mul, expAt_coeff, Finset.sum_div, mul_div_assoc]

/-- A telescoping identity valid before restricting the parity of p. -/
theorem source_times_cosh (p : ℕ) :
    sourceSeries p * coshAt 1 = C (1/2) * (1 - C ((-1:ℚ)^p) * expAt (2*p)) := by
  rw [source_as_exponentials]
  induction p with
  | zero => simp
  | succ p ih =>
    rw [Finset.sum_range_succ, add_mul, ih]
    have he1 : expAt (2*(p:ℚ)+1) * expAt 1 = expAt (2*(p+1)) := by
      rw [expAt_mul]; congr 1; ring
    have he2 : expAt (2*(p:ℚ)+1) * expAt (-1) = expAt (2*p) := by
      rw [expAt_mul]; congr 1; ring
    simp only [Nat.cast_add, Nat.cast_one, pow_succ, map_mul, map_neg, map_one]
    unfold coshAt
    calc
      _ = C (1/2) * (1 - C ((-1:ℚ)^p)*expAt (2*p)) +
        C (1/2) * C ((-1:ℚ)^p) *
          (expAt (2*(p:ℚ)+1)*expAt 1 + expAt (2*(p:ℚ)+1)*expAt (-1)) := by ring
      _ = _ := by rw [he1, he2]; ring

/-- Lemma 4.1, full EGF identity for every odd positive length. -/
theorem odd_source_egf (p : ℕ) (hp : Odd p) :
    sourceSeries p = C (1/2) * (1 + expAt (2*p)) * sech := by
  have h := source_times_cosh p
  rw [hp.neg_one_pow, map_neg, map_one, neg_mul, one_mul, sub_neg_eq_add] at h
  calc
    sourceSeries p = (sourceSeries p * coshAt 1) * sech := by rw [mul_assoc, cosh_mul_sech, mul_one]
    _ = _ := by rw [h]

/-- Even-part projection as the average of a series and its evaluation at -t. -/
def evenPart (f : PowerSeries ℚ) : PowerSeries ℚ := C (1/2) * (f + rescale (-1) f)

@[simp] theorem rescale_expAt (a b : ℚ) : rescale a (expAt b) = expAt (a*b) := by
  ext n
  simp [mul_pow, div_eq_mul_inv, mul_assoc]

@[simp] theorem rescale_cosh (a b : ℚ) : rescale a (coshAt b) = coshAt (a*b) := by
  simp [coshAt, map_mul, map_add, mul_neg]

@[simp] theorem rescale_sech_neg : rescale (-1) sech = sech := by
  apply (PowerSeries.eq_inv_iff_mul_eq_one (by simp)).mpr
  have h := congrArg (rescale (-1:ℚ)) sech_mul_cosh
  simpa only [map_mul, map_one, rescale_cosh, neg_one_mul, cosh_neg] using h

/-- The elementary hyperbolic duplication identity in the formal series ring. -/
theorem cosh_square (a : ℚ) :
    coshAt a ^ 2 = C (1/4) * (2 + expAt (2*a) + expAt (-(2*a))) := by
  have h1 : expAt a * expAt a = expAt (2*a) := by rw [expAt_mul]; congr 1; ring
  have h2 : expAt (-a) * expAt (-a) = expAt (-(2*a)) := by rw [expAt_mul]; congr 1; ring
  have h3 : expAt a * expAt (-a) = 1 := by rw [expAt_mul]; simp
  have hh : C (1/2:ℚ) * C (1/2:ℚ) = (C (1/4:ℚ) : PowerSeries ℚ) := by rw [← map_mul]; norm_num
  calc
    _ = (C (1/2)*C (1/2)) *
      (expAt a*expAt a + 2*(expAt a*expAt (-a)) + expAt (-a)*expAt (-a)) := by unfold coshAt; ring
    _ = _ := by rw [h1, h2, h3, hh]; ring

/-- Lemma 4.1, actual even part of the odd-power EGF. -/
theorem odd_source_even_egf (p : ℕ) (hp : Odd p) :
    evenPart (sourceSeries p) = coshAt p ^ 2 * sech := by
  rw [odd_source_egf p hp, evenPart]
  simp only [map_mul, map_add, map_one, rescale_constant, rescale_expAt, rescale_sech_neg]
  rw [cosh_square]
  have hh : C (1/2:ℚ) * C (1/2:ℚ) = (C (1/4:ℚ) : PowerSeries ℚ) := by rw [← map_mul]; norm_num
  have hn : (-1:ℚ)*(2*p) = -(2*p) := by ring
  rw [hn]
  calc
    _ = (C (1/2)*C (1/2)) * (2 + expAt (2*p) + expAt (-(2*p))) * sech := by ring
    _ = _ := by rw [hh]

/-- Identifies the average with literal even coefficient selection. -/
theorem evenPart_coeff (f : PowerSeries ℚ) (n : ℕ) :
    coeff n (evenPart f) = if Even n then coeff n f else 0 := by
  simp only [evenPart, coeff_C_mul, map_add, coeff_rescale]
  by_cases h : Even n
  · rw [ite_eq_left h, h.neg_one_pow]; ring
  · rw [ite_eq_right h, (Nat.not_even_iff_odd.mp h).neg_one_pow]; ring

end KomorebiPaperIX.OddPower
