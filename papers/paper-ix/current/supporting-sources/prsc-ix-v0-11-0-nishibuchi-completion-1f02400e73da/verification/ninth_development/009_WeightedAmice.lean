module
public import SectionLogBridge
public import Mathlib.RingTheory.PowerSeries.Inverse
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.WeightedAmice
open PowerSeries
variable (p : ℕ) [Fact p.Prime]

def Integral (x : ℚ_[p]) : Prop := x ∈ PadicInt.subring p

theorem integral_zero : Integral p 0 := (PadicInt.subring p).zero_mem

theorem integral_one : Integral p 1 := (PadicInt.subring p).one_mem

theorem integral_nat (n : ℕ) : Integral p (n:ℚ_[p]) := natCast_mem _ _

theorem integral_int (n : ℤ) : Integral p (n:ℚ_[p]) := intCast_mem _ _

theorem integral_mul {x y : ℚ_[p]} (hx : Integral p x) (hy : Integral p y) :
    Integral p (x*y) := (PadicInt.subring p).mul_mem hx hy

theorem integral_add {x y : ℚ_[p]} (hx : Integral p x) (hy : Integral p y) :
    Integral p (x+y) := (PadicInt.subring p).add_mem hx hy

theorem integral_neg {x : ℚ_[p]} (hx : Integral p x) :
    Integral p (-x) := (PadicInt.subring p).neg_mem hx

theorem integral_sum {ι : Type*} (s : Finset ι) (f : ι → ℚ_[p])
    (h : ∀ i∈s, Integral p (f i)) : Integral p (∑ i∈s, f i) :=
  (PadicInt.subring p).sum_mem h

theorem integral_pow {x : ℚ_[p]} (h : Integral p x) (n : ℕ) : Integral p (x^n) :=
  (PadicInt.subring p).pow_mem h n

theorem scaled_mono {x : ℚ_[p]} {a b : ℕ} (hab : a ≤ b)
    (h : Integral p ((p:ℚ_[p])^a*x)) : Integral p ((p:ℚ_[p])^b*x) := by
  have he : (p:ℚ_[p])^b*x = (p:ℚ_[p])^(b-a)*((p:ℚ_[p])^a*x) := by
    rw [←mul_assoc, ←pow_add, Nat.sub_add_cancel hab]
  rw [he]
  exact integral_mul p (integral_pow p (integral_nat p p) _) h

theorem scaled_product {x y : ℚ_[p]} {a b c : ℕ} (hab : a+b≤c)
    (hx : Integral p ((p:ℚ_[p])^a*x)) (hy : Integral p ((p:ℚ_[p])^b*y)) :
    Integral p ((p:ℚ_[p])^c*(x*y)) := by
  apply scaled_mono p hab
  rw [pow_add]
  convert integral_mul p hx hy using 1
  ring

/-- Coefficients may lose at most floor(n/p) powers of p. Zero requires no special convention. -/
def Weighted (f : PowerSeries ℚ_[p]) : Prop :=
  ∀ n, Integral p ((p:ℚ_[p])^(n/p)*coeff n f)

theorem weighted_zero : Weighted p 0 := by
  intro n
  simpa using integral_zero p

theorem weighted_one : Weighted p 1 := by
  intro n
  by_cases hn : n=0
  · subst n; simpa using integral_one p
  · simpa [coeff_one, hn] using integral_zero p

theorem weighted_constant {a : ℚ_[p]} (ha : Integral p a) : Weighted p (C a) := by
  intro n
  by_cases hn : n=0
  · subst n; simpa using ha
  · simpa [coeff_C, hn] using integral_zero p

theorem weighted_add {f g : PowerSeries ℚ_[p]} (hf : Weighted p f) (hg : Weighted p g) :
    Weighted p (f+g) := by
  intro n
  simpa only [map_add, mul_add] using integral_add p (hf n) (hg n)

theorem weighted_neg {f : PowerSeries ℚ_[p]} (hf : Weighted p f) : Weighted p (-f) := by
  intro n
  simpa only [map_neg, mul_neg] using integral_neg p (hf n)

theorem weighted_mul {f g : PowerSeries ℚ_[p]} (hf : Weighted p f) (hg : Weighted p g) :
    Weighted p (f*g) := by
  intro n
  rw [coeff_mul, Finset.mul_sum]
  apply integral_sum p
  intro ij hij
  have h := Finset.mem_antidiagonal.mp hij
  apply scaled_product p _ (hf ij.1) (hg ij.2)
  simpa [h] using Nat.div_add_div_le_add_div ij.1 ij.2 p

theorem weighted_pow {f : PowerSeries ℚ_[p]} (hf : Weighted p f) (n : ℕ) :
    Weighted p (f^n) := by
  induction n with
  | zero => simpa using weighted_one p
  | succ n ih => simpa [pow_succ] using weighted_mul p ih hf

/-- Inverse stability is proved from the actual reciprocal coefficient recurrence. -/
theorem weighted_inverse {f : PowerSeries ℚ_[p]} (hf : Weighted p f)
    (h0 : constantCoeff f=1) : Weighted p f⁻¹ := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    rw [coeff_inv, h0, inv_one]
    by_cases hn : n=0
    · subst n; simpa using integral_one p
    · rw [ite_eq_right hn, neg_one_mul, mul_neg, Finset.mul_sum]
      apply integral_neg p
      apply integral_sum p
      intro ij hij
      by_cases hj : ij.2 < n
      · rw [ite_eq_left hj]
        apply scaled_product p _ (hf ij.1) (ih ij.2 hj)
        have h := Finset.mem_antidiagonal.mp hij
        simpa [h] using Nat.div_add_div_le_add_div ij.1 ij.2 p
      · rw [ite_eq_right hj, mul_zero]
        exact integral_zero p

/-- Actual rational section coefficients, embedded into the completed field. -/
def sectionPadic (N : ℕ) (r : ZMod N) : PowerSeries ℚ_[p] :=
  PowerSeries.map (Rat.castHom ℚ_[p]) (SectionLogBridge.sectionPullback N r)

theorem weighted_section (N : ℕ) (hN : N ∣ p*(p-1)) (r : ZMod N) :
    Weighted p (sectionPadic p N r) := by
  intro d
  change (p:ℚ_[p])^(d/p) * ((coeff d (SectionLogBridge.sectionPullback N r) : ℚ) : ℚ_[p])
    ∈ PadicInt.subring p
  exact SectionLogBridge.section_weighted_integral p N d hN r

end KomorebiPaperIX.WeightedAmice
