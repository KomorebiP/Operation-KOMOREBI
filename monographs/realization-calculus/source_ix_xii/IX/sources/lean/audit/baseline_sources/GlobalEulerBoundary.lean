module

public import StandardWindowPeriod
public import DifferenceFiltration
public import PadicDifferenceBounds

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.GlobalEulerBoundary

open Mahler WindowIndependence WindowPeriod DifferenceFiltration

variable (p : ℕ) [Fact p.Prime]

/-- Zero-safe valuation precision, permitting the negative normalized loss. -/
def precision (L : ℤ) (x : ℚ) : Prop := x=0 ∨ L≤padicValRat p x

omit [Fact p.Prime] in
@[simp] theorem precision_zero (L : ℤ) : precision p L 0 := Or.inl rfl

/-- Normalization commutes with the actual iterated difference at every order. -/
theorem unnormalized_difference (N j h k n : ℕ) :
    difference h k (Congruential.unnormalized N j) n =
      (j.factorial : ℚ) * difference h k (Congruential.coeff N j) n := by
  exact congrFun (difference_mul_const h k (j.factorial : ℚ) (Congruential.coeff N j)) n

/-- A proved unnormalized estimate entails exactly the factorial loss, including zero differences.
The global unnormalized estimate is not established by this implication. -/
theorem factorial_loss_transfer (N j h k n : ℕ) (L : ℤ)
    (H : precision p L (difference h k (Congruential.unnormalized N j) n)) :
    precision p (L - (padicValNat p j.factorial : ℤ))
      (difference h k (Congruential.coeff N j) n) := by
  by_cases hx : difference h k (Congruential.coeff N j) n = 0
  · exact Or.inl hx
  · right
    rw [unnormalized_difference] at H
    rcases H with H | H
    · exact False.elim ((mul_ne_zero (by exact_mod_cast Nat.factorial_ne_zero j) hx) H)
    · rw [padicValRat.mul (by exact_mod_cast Nat.factorial_ne_zero j) hx,
        padicValRat.of_nat] at H
      omega

/-- No factorial loss in the standard window, conditional only on the supplied estimate. -/
theorem standard_window_loss_transfer (N j h k n : ℕ) (hj : j<p) (L : ℤ)
    (H : precision p L (difference h k (Congruential.unnormalized N j) n)) :
    precision p L (difference h k (Congruential.coeff N j) n) := by
  have h := factorial_loss_transfer p N j h k n L H
  have hv : padicValNat p j.factorial = 0 :=
    padicValNat.eq_zero_of_not_dvd (StandardWindow.factorial_unit_window p j hj)
  simpa [hv] using h

/-- A genuinely proved mod-p fragment of 7.5 for all positive orders, in the standard window.
It is one power of p, not the full power min(k,m*n). -/
theorem standard_window_all_orders_mod_p (m j n u k : ℕ)
    (hm : m ∣ p-1) (hj : j<p) (hn : 1≤n) (hk : 0<k) :
    (p : ℤ_[p]) ∣ difference (u*((p-1)/m)) k (coeffPadic p m j hj) n := by
  apply tail_period_higher_difference (p : ℤ_[p]) (u*((p-1)/m)) 1
    (coeffPadic p m j hj) _ k n hk hn
  intro r hr
  exact standard_window_period_divisibility p m j r u hm hj hr

/-- Infinity at zero is retained in the valuation formulation. -/
theorem standard_window_all_orders_order (m j n u k : ℕ)
    (hm : m ∣ p-1) (hj : j<p) (hn : 1≤n) (hk : 0<k) :
    (1 : WithTop ℕ) ≤ PadicBounds.order p
      (difference (u*((p-1)/m)) k (coeffPadic p m j hj) n) := by
  apply (PadicBounds.nat_le_order_iff p _ 1).mpr
  simpa using standard_window_all_orders_mod_p p m j n u k hm hj hn hk

/-- The p-adic statement concerns the original rational coefficient function. -/
theorem lifted_difference_coe (m j h k n : ℕ) (hj : j<p) :
    ((difference h k (coeffPadic p m j hj) n : ℤ_[p]) : ℚ_[p]) =
      ((difference h k (Congruential.coeff (m*p) j) n : ℚ) : ℚ_[p]) := by
  change (algebraMap ℤ_[p] ℚ_[p]) (difference h k (coeffPadic p m j hj) n) =
    (algebraMap ℚ ℚ_[p]) (difference h k (Congruential.coeff (m*p) j) n)
  rw [← difference_map (algebraMap ℤ_[p] ℚ_[p]),
      ← difference_map (algebraMap ℚ ℚ_[p])]
  congr 1
  funext r
  exact coeffPadic_coe p m j hj r

end KomorebiPaperIX.GlobalEulerBoundary
