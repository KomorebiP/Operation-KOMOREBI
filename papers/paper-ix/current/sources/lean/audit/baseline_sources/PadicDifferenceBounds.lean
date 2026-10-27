module

public import FiniteMahler
public import Mathlib.NumberTheory.Padics.PadicIntegers

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.PadicBounds

open Mahler

variable (p : ℕ) [Fact p.Prime]

/-- Zero-safe additive valuation: zero has valuation infinity, not the library's finite default. -/
def order (x : ℤ_[p]) : WithTop ℕ := by
  classical
  exact if x = 0 then ⊤ else (x.valuation : WithTop ℕ)

@[simp] theorem order_zero : order p 0 = ⊤ := by simp [order]

@[simp] theorem order_nonzero (x : ℤ_[p]) (hx : x ≠ 0) :
    order p x = (x.valuation : WithTop ℕ) := by simp [order, hx]

/-- The extended valuation inequality means actual ideal divisibility in Z_p. -/
theorem nat_le_order_iff (x : ℤ_[p]) (L : ℕ) :
    (L : WithTop ℕ) ≤ order p x ↔ (p : ℤ_[p])^L ∣ x := by
  by_cases hx : x = 0
  · simp [hx]
  · rw [order_nonzero p x hx, Nat.cast_le]
    rw [← PadicInt.mem_span_pow_iff_le_valuation x hx L, Ideal.mem_span_singleton]

theorem order_mul (x y : ℤ_[p]) : order p (x*y) = order p x + order p y := by
  by_cases hx : x = 0
  · simp [hx]
  by_cases hy : y = 0
  · simp [hy]
  simp [order, hx, hy, mul_ne_zero hx hy, PadicInt.valuation_mul hx hy]

theorem order_add_lower (x y : ℤ_[p]) :
    min (order p x) (order p y) ≤ order p (x+y) := by
  by_cases hxy : x+y = 0
  · simp [hxy]
  by_cases hx : x = 0
  · simp [hx]
  by_cases hy : y = 0
  · simp [hy]
  simp only [order_nonzero p _ hxy, order_nonzero p _ hx, order_nonzero p _ hy]
  calc
    _ = ((min x.valuation y.valuation : ℕ) : WithTop ℕ) := (WithTop.coe_min _ _).symm
    _ ≤ _ := WithTop.coe_le_coe.mpr (PadicInt.le_valuation_add hxy)

theorem order_sum_lower {ι : Type*} (S : Finset ι) (f : ι → ℤ_[p]) (L : WithTop ℕ)
    (h : ∀ i ∈ S, L ≤ order p (f i)) : L ≤ order p (∑ i ∈ S, f i) := by
  classical
  induction S using Finset.induction_on with
  | empty => simp
  | @insert i S hi ih =>
    rw [Finset.sum_insert hi]
    apply le_trans _ (order_add_lower p _ _)
    exact le_min (h i (Finset.mem_insert_self _ _))
      (ih (by intro j hj; exact h j (Finset.mem_insert_of_mem hj)))

theorem order_natCast (k : ℕ) (hk : k ≠ 0) :
    order p (k : ℤ_[p]) = (padicValNat p k : WithTop ℕ) := by
  rw [order_nonzero p _ (Nat.cast_ne_zero.mpr hk)]
  congr 1
  simp [PadicInt.valuation, Padic.valuation_natCast]

/-- Only r=s,...,s+n contribute at a natural argument n. -/
def weightedBound (w : ℕ → WithTop ℕ) (n s : ℕ) : WithTop ℕ :=
  (Finset.range (n+1)).inf (fun j => w (s+j) + (padicValNat p (n.choose j) : WithTop ℕ))

/-- The complete weighted minimum, including the binomial valuation and the zero case. -/
theorem weighted_difference_bound (f : ℕ → ℤ_[p]) (w : ℕ → WithTop ℕ) (n s : ℕ)
    (hw : ∀ j ≤ n, w (s+j) ≤ order p (coefficient f (s+j))) :
    weightedBound p w n s ≤ order p (difference 1 s f n) := by
  rw [difference_from_coefficients]
  apply order_sum_lower
  intro j hj
  have hjn := Finset.mem_range_succ_iff.mp hj
  have hchoose : n.choose j ≠ 0 := Nat.ne_of_gt (Nat.choose_pos hjn)
  rw [order_mul, order_natCast p _ hchoose]
  exact (Finset.inf_le hj).trans (add_le_add (hw j hjn) le_rfl)

/-- Equivalent finite precision certificate with no appeal to a finite valuation at zero. -/
theorem weighted_difference_divisibility (f : ℕ → ℤ_[p]) (w : ℕ → WithTop ℕ)
    (n s L : ℕ) (hw : ∀ j ≤ n, w (s+j) ≤ order p (coefficient f (s+j)))
    (hL : (L : WithTop ℕ) ≤ weightedBound p w n s) :
    (p : ℤ_[p])^L ∣ difference 1 s f n := by
  exact (nat_le_order_iff p _ L).mp (hL.trans (weighted_difference_bound p f w n s hw))

/-- The simpler infimum bound follows because binomial valuations are nonnegative. -/
theorem coefficient_tail_bound (f : ℕ → ℤ_[p]) (w : ℕ → WithTop ℕ) (n s : ℕ)
    (hw : ∀ r, w r ≤ order p (coefficient f r)) :
    (⨅ r : ℕ, w (s+r)) ≤ order p (difference 1 s f n) := by
  apply le_trans _ (weighted_difference_bound p f w n s (by intro j _; exact hw _))
  apply Finset.le_inf
  intro j _
  exact (iInf_le (fun r : ℕ => w (s+r)) j).trans (le_self_add)

/-- A common finite precision for the relevant coefficients passes to the difference. -/
theorem difference_dvd_of_coefficients (f : ℕ → ℤ_[p]) (n s L : ℕ)
    (h : ∀ j ≤ n, (p : ℤ_[p])^L ∣ coefficient f (s+j)) :
    (p : ℤ_[p])^L ∣ difference 1 s f n := by
  rw [difference_from_coefficients]
  apply Finset.dvd_sum
  intro j hj
  exact dvd_mul_of_dvd_left (h j (Finset.mem_range_succ_iff.mp hj)) _

/-- The same weighted certificate for arbitrary finite binomial expansions. -/
theorem interpolant_weighted_bound (N : ℕ) (c : ℕ → ℤ_[p]) (w : ℕ → WithTop ℕ)
    (n s : ℕ) (hw : ∀ r ≤ N, w r ≤ order p (c r)) :
    weightedBound p (fun r => if r ≤ N then w r else ⊤) n s ≤
      order p (difference 1 s (interpolant N c) n) := by
  apply weighted_difference_bound
  intro j _
  rw [coefficient_interpolant]
  by_cases hj : s+j ≤ N
  · simpa [hj] using hw (s+j) hj
  · simp [hj]

end KomorebiPaperIX.PadicBounds
