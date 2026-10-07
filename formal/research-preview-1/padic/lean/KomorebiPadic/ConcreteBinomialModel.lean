import Mathlib.Data.Nat.MaxPowDiv
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Algebra.Ring.Divisibility.Basic
import KomorebiPadic.ValuationModel

/-!
# Concrete binomial p-adic valuation model

This file supplies the concrete instance left open in Block 03:

`ν q k = padicValNat p ((q + k - 1).choose k)`.

The key input is proved directly from divisibility.  If `p^m` divides two
positive naturals, then it divides their sum, so the p-adic valuation of the
sum is at least the minimum of the two valuations.  Pascal's identity then
produces the predecessor disjunction required by `PascalValuationModel`.
-/

namespace KomorebiPadic

/-- The natural p-adic valuation of a sum dominates the minimum valuation. -/
theorem min_padicValNat_le_add
    {p a b : ℕ} (hp : p ≠ 1) (ha : a ≠ 0) (hb : b ≠ 0) :
    min (padicValNat p a) (padicValNat p b) ≤ padicValNat p (a + b) := by
  have hab : a + b ≠ 0 := by omega
  exact (Nat.pow_dvd_iff_le_padicValNat hp hab).1
    (Nat.dvd_add
      ((Nat.pow_dvd_iff_le_padicValNat hp ha).2 (min_le_left _ _))
      ((Nat.pow_dvd_iff_le_padicValNat hp hb).2 (min_le_right _ _)))

/-- Pascal descent for the concrete binomial p-adic valuation. -/
theorem binomial_padic_pascalPred
    {p q k : ℕ} (hp : 1 < p) (hq : 1 < q) (hk : 0 < k) :
    padicValNat p ((q + (k - 1) - 1).choose (k - 1)) ≤
        padicValNat p ((q + k - 1).choose k) ∨
      padicValNat p (((q - 1) + k - 1).choose k) ≤
        padicValNat p ((q + k - 1).choose k) := by
  have hleft_ne : (q + k - 2).choose (k - 1) ≠ 0 :=
    Nat.choose_ne_zero (by omega)
  have hright_ne : (q + k - 2).choose k ≠ 0 :=
    Nat.choose_ne_zero (by omega)
  have hpascal :
      (q + k - 1).choose k =
        (q + k - 2).choose (k - 1) + (q + k - 2).choose k := by
    have h := Nat.choose_eq_choose_pred_add
      (n := q + k - 1) (k := k) (by omega) hk
    have hidx : q + k - 1 - 1 = q + k - 2 := by omega
    simpa only [hidx] using h
  have hmin :
      min
          (padicValNat p ((q + k - 2).choose (k - 1)))
          (padicValNat p ((q + k - 2).choose k)) ≤
        padicValNat p ((q + k - 1).choose k) := by
    rw [hpascal]
    exact min_padicValNat_le_add (Nat.ne_of_gt hp) hleft_ne hright_ne
  rcases (min_le_iff.mp hmin) with hleft | hright
  · left
    have hidx : q + (k - 1) - 1 = q + k - 2 := by omega
    simpa only [hidx] using hleft
  · right
    have hidx : (q - 1) + k - 1 = q + k - 2 := by omega
    simpa only [hidx] using hright

/-- The concrete valuation model for correction binomial coefficients. -/
def binomialPadicModel (p : ℕ) (hp : 1 < p) : PascalValuationModel where
  ν q k := padicValNat p ((q + k - 1).choose k)
  zeroOrder := by
    intro q
    simp
  firstQuotient := by
    intro k
    have h : 1 + k - 1 = k := by omega
    simp [h]
  pascalPred := by
    intro q k hq hk
    exact binomial_padic_pascalPred hp hq hk

/-- The concrete active-edge system used by the Cartier correction graph. -/
def binomialPadicEdgeSystem
    (p r h : ℕ) (hp : 1 < p) : PredecessorEdgeSystem :=
  valuationEdgeSystem (binomialPadicModel p hp) r h

/-- Concrete binomial p-adic targets form an initial interval. -/
theorem binomial_padic_targets_form_initial_interval
    {p r h Q M : ℕ} (hp : 1 < p)
    (hM : IsTarget (binomialPadicEdgeSystem p r h hp) Q M) :
    ∀ s : ℕ, 1 ≤ s → s ≤ M →
      IsTarget (binomialPadicEdgeSystem p r h hp) Q s := by
  exact valuation_targets_form_initial_interval (binomialPadicModel p hp) hM

end KomorebiPadic
