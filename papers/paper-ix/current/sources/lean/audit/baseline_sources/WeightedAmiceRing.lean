module
public import Mathlib.RingTheory.PowerSeries.Inverse
public import Mathlib.RingTheory.PowerSeries.Derivative
public import Mathlib.RingTheory.PowerSeries.Log
public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.Algebra.BigOperators.NatAntidiagonal
public import Mathlib.Tactic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.WeightedAmice
open PowerSeries
variable (p : ℕ) [Fact p.Prime]

/-- Ordinary coefficients with the explicit weight floor(n/p). -/
def IsWeighted (f : PowerSeries ℚ_[p]) : Prop :=
  ∀ n, (p:ℚ_[p])^(n/p)*coeff n f ∈ PadicInt.subring p

theorem raise_weight {a : ℚ_[p]} {r s : ℕ} (h : r≤s)
    (ha : (p:ℚ_[p])^r*a ∈ PadicInt.subring p) :
    (p:ℚ_[p])^s*a ∈ PadicInt.subring p := by
  have he : (p:ℚ_[p])^s*a = (p:ℚ_[p])^(s-r)*((p:ℚ_[p])^r*a) := by
    rw [←mul_assoc, ←pow_add, Nat.sub_add_cancel h]
  rw [he]
  exact (PadicInt.subring p).mul_mem (pow_mem (natCast_mem _ p) _) ha

theorem weighted_product_term {f g : PowerSeries ℚ_[p]} (hf : IsWeighted p f)
    (hg : IsWeighted p g) (n r : ℕ) (hr : r≤n) :
    (p:ℚ_[p])^(n/p)*(coeff r f*coeff (n-r) g) ∈ PadicInt.subring p := by
  have hh : r/p+(n-r)/p≤n/p := by
    simpa [Nat.add_sub_of_le hr] using (Nat.div_add_div_le_add_div (x:=r) (y:=n-r) (z:=p))
  apply raise_weight p hh
  have h := (PadicInt.subring p).mul_mem (hf r) (hg (n-r))
  simpa only [pow_add, mul_mul_mul_comm] using h

/-- Weighted coefficients form a genuine subring; multiplication is proved coefficientwise. -/
def ring : Subring (PowerSeries ℚ_[p]) where
  carrier := IsWeighted p
  zero_mem' := by intro n; simp
  one_mem' := by
    intro n
    by_cases hn : n=0
    · subst n; simp
    · simp [coeff_one, hn]
  add_mem' := by
    intro f g hf hg n
    rw [map_add, mul_add]
    exact (PadicInt.subring p).add_mem (hf n) (hg n)
  neg_mem' := by
    intro f hf n
    rw [map_neg, mul_neg]
    exact (PadicInt.subring p).neg_mem (hf n)
  mul_mem' := by
    intro f g hf hg n
    rw [coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk, Finset.mul_sum]
    apply (PadicInt.subring p).sum_mem
    intro r hr
    exact weighted_product_term p hf hg n r (Finset.mem_range_succ_iff.mp hr)

@[simp] theorem mem_ring (f : PowerSeries ℚ_[p]) : f∈ring p ↔ IsWeighted p f := Iff.rfl

theorem constant_mem {a : ℚ_[p]} (ha : a∈PadicInt.subring p) : C a∈ring p := by
  intro n
  by_cases hn : n=0
  · subst n; simpa using ha
  · simp [coeff_C, hn]

theorem monomial_mem {a : ℚ_[p]} (n : ℕ)
    (ha : (p:ℚ_[p])^(n/p)*a∈PadicInt.subring p) : monomial n a∈ring p := by
  intro d
  by_cases hd : d=n
  · subst d; simpa using ha
  · simp [coeff_monomial, hd]

theorem ordinary_mem (f : PowerSeries ℚ_[p]) (hf : ∀ n, coeff n f∈PadicInt.subring p) :
    f∈ring p := by
  intro n
  exact (PadicInt.subring p).mul_mem (pow_mem (natCast_mem _ _) _) (hf n)

theorem X_mem : (X:PowerSeries ℚ_[p])∈ring p := by
  apply ordinary_mem
  intro n
  by_cases hn : n=1 <;> simp [coeff_X, hn]

/-- Differentiation is stable despite the change of floor weight at multiples of p. -/
theorem derivative_mem (f : PowerSeries ℚ_[p]) (hf : f∈ring p) :
    derivative ℚ_[p] f∈ring p := by
  intro n
  rw [coeff_derivative]
  by_cases hd : p∣n+1
  · have he : (p:ℚ_[p])^(n/p)*(coeff (n+1) f*(n+1:ℚ_[p])) =
        (((n+1)/p:ℕ):ℚ_[p])*((p:ℚ_[p])^((n+1)/p)*coeff (n+1) f) := by
      have hpow : (p:ℚ_[p])^((n+1)/p)=(p:ℚ_[p])^(n/p)*(p:ℚ_[p]) := by
        rw [Nat.succ_div_of_dvd hd, pow_succ]
      rw [hpow]
      have hcast : (((n+1)/p:ℕ):ℚ_[p])*(p:ℚ_[p])=(n+1:ℚ_[p]) := by
        exact_mod_cast Nat.div_mul_cancel hd
      linear_combination -((p:ℚ_[p])^(n/p)*coeff (n+1) f)*hcast
    rw [he]
    exact (PadicInt.subring p).mul_mem (natCast_mem _ _) (hf (n+1))
  · have h := (PadicInt.subring p).mul_mem (hf (n+1)) (natCast_mem (PadicInt.subring p) (n+1))
    simpa only [Nat.succ_div_of_not_dvd hd, Nat.cast_add, Nat.cast_one, mul_assoc] using h

/-- Actual reciprocal coefficients, with the unit constant coefficient exposed. -/
theorem inverse_coefficient (f : PowerSeries ℚ_[p]) (h0 : constantCoeff f=1) (n : ℕ) :
    coeff n f⁻¹ = (if n=0 then 1 else 0) -
      ∑ r∈Finset.range n, coeff r f⁻¹*coeff (n-r) f := by
  have h := congrArg (coeff n) (PowerSeries.inv_mul_cancel f (by rw [h0]; exact one_ne_zero))
  rw [coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk, Finset.sum_range_succ] at h
  rw [Nat.sub_self, coeff_zero_eq_constantCoeff, h0, mul_one, coeff_one] at h
  linear_combination h

/-- Inversion preserves the weighted ring when the constant coefficient is one. -/
theorem inverse_mem (f : PowerSeries ℚ_[p]) (hf : f∈ring p) (h0 : constantCoeff f=1) :
    f⁻¹∈ring p := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    rw [inverse_coefficient p f h0 n, mul_sub, Finset.mul_sum]
    apply (PadicInt.subring p).sub_mem
    · by_cases hn : n=0 <;> simp [hn]
    · apply (PadicInt.subring p).sum_mem
      intro r hr
      have hrl := Finset.mem_range.mp hr
      have hh : r/p+(n-r)/p≤n/p := by
        simpa [Nat.add_sub_of_le hrl.le] using (Nat.div_add_div_le_add_div (x:=r) (y:=n-r) (z:=p))
      apply raise_weight p hh
      have h := (PadicInt.subring p).mul_mem (ih r hrl) (hf (n-r))
      simpa only [pow_add, mul_mul_mul_comm] using h

/-- Exact tail shifting, used only when the removed order is a multiple of p. -/
def tail (c : ℕ) (f : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  PowerSeries.mk (fun d => coeff (d+c) f)

@[simp] theorem tail_coeff (c d : ℕ) (f : PowerSeries ℚ_[p]) :
    coeff d (tail p c f)=coeff (d+c) f := by simp [tail]

theorem shifted_weight (a : ℕ) (f : PowerSeries ℚ_[p]) (hf : f∈ring p) :
    C ((p:ℚ_[p])^a)*tail p (a*p) f∈ring p := by
  intro n
  rw [coeff_C_mul, tail_coeff]
  have he : (n+a*p)/p=n/p+a := by
    rw [Nat.add_mul_div_right _ _ (Fact.out : p.Prime).pos]
  have h := hf (n+a*p)
  rw [he, pow_add] at h
  simpa only [mul_assoc] using h

end KomorebiPaperIX.WeightedAmice
