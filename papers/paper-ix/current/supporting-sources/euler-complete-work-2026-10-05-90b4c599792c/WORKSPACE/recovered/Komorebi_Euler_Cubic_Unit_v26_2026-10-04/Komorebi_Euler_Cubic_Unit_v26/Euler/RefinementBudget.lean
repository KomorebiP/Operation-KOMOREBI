module
public import Euler.Dyadic
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- Exact Hasse-refinement coefficient identity. A is the translated series,
F the normalized child, and c the removed content. -/
def ChildIdentity (A F : PowerSeries D) (c : ℕ) : Prop :=
  C ((2:D)^c)*F = rescale (2:D) A

lemma child_coeff (A F : PowerSeries D) (c n : ℕ) (h : ChildIdentity A F c) :
    (2:D)^c*coeff n F = (2:D)^n*coeff n A := by
  have hc := congrArg (coeff n) h
  simpa only [coeff_C_mul, coeff_rescale] using hc

/-- A nonzero m-th Hasse coefficient modulo two bounds content removal. -/
theorem child_content_le (A F : PowerSeries D) (c m : ℕ)
    (h : ChildIdentity A F c) (hm : red (coeff m A)=1) : c ≤ m := by
  by_contra hn
  have hmc : m+1 ≤ c := by omega
  obtain ⟨d,hd⟩ := Nat.exists_eq_add_of_le hmc
  have hc := child_coeff A F c m h
  rw [hd, show m+1+d=m+(d+1) by omega, pow_add, mul_assoc] at hc
  have hcancel := mul_left_cancel₀ (pow_ne_zero m two_ne_zero) hc
  have hred := congrArg red hcancel
  have hd0 : d+1 ≠ 0 := by omega
  simp only [map_mul, map_pow, red_two, zero_pow hd0, zero_mul, hm] at hred
  norm_num at hred

/-- Every coefficient strictly above m in the normalized child is even. -/
theorem child_high_even (A F : PowerSeries D) (c m : ℕ)
    (h : ChildIdentity A F c) (hm : red (coeff m A)=1) :
    ∀ i, m < i → red (coeff i F)=0 := by
  have hcm := child_content_le A F c m h hm
  intro i hi
  obtain ⟨d,hd⟩ := Nat.exists_eq_add_of_le (show c ≤ i by omega)
  have hc := child_coeff A F c i h
  rw [hd, pow_add, mul_assoc] at hc
  have hcancel := mul_left_cancel₀ (pow_ne_zero c two_ne_zero) hc
  have hred := congrArg red hcancel
  have hd0 : d ≠ 0 := by omega
  simpa only [hd, map_mul, map_pow, red_two, zero_pow hd0, zero_mul] using hred

/-- The algebraic degree-budget step, before invoking analytic preparation. -/
theorem child_degree_le (A F : PowerSeries D) (c m d : ℕ)
    (h : ChildIdentity A F c) (hm : red (coeff m A)=1)
    (hd : LastOdd F d) : d ≤ m := by
  by_contra hn
  have hz := child_high_even A F c m h hm d (by omega)
  rw [hd.1] at hz
  norm_num at hz

/-- Two children cannot exceed the parent multiplicity budget. -/
theorem binary_degree_budget (A₀ A₁ F₀ F₁ : PowerSeries D)
    (c₀ c₁ m₀ m₁ d₀ d₁ d : ℕ)
    (h₀ : ChildIdentity A₀ F₀ c₀) (h₁ : ChildIdentity A₁ F₁ c₁)
    (hm₀ : red (coeff m₀ A₀)=1) (hm₁ : red (coeff m₁ A₁)=1)
    (hd₀ : LastOdd F₀ d₀) (hd₁ : LastOdd F₁ d₁)
    (hm : m₀+m₁≤d) : d₀+d₁≤d := by
  have a := child_degree_le A₀ F₀ c₀ m₀ d₀ h₀ hm₀ hd₀
  have b := child_degree_le A₁ F₁ c₁ m₁ d₁ h₁ hm₁ hd₁
  omega

end Komorebi.Euler
