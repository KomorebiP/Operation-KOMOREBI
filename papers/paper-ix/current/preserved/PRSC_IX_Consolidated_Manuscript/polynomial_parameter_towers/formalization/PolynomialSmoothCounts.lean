module
public import PolynomialIntegerTower
public import PolynomialLiftCounts

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialSmoothCounts
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
open Komorebi.PolynomialDigitBridge Komorebi.PolynomialLiftCounts
open Komorebi.PolynomialIntegerTower
variable {d e : ℕ}

/-- A surjective reduced Jacobian has rank equal to the number of equations. -/
theorem smooth_rank (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    FiniteFiberCounts.rank p (digitJacobian p F x) = e := by
  unfold FiniteFiberCounts.rank
  rw [LinearMap.range_eq_top.mpr hJ, finrank_top, Module.finrank_fin_fun]

/-- The dimension bound implicit in Jacobian surjectivity is an actual consequence. -/
theorem smooth_dimension (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) : e ≤ d := by
  simpa only [Module.finrank_fin_fun] using
    LinearMap.finrank_le_finrank_of_surjective hJ

/-- At every smooth lower root, there are exactly p^(d-e) distinct next-level
residue classes solving the original polynomial equations. -/
theorem smooth_lift_card (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    Nat.card (ActualLifts p L F x) = p^(d-e) := by
  have hp : 0 < p := (Fact.out : Nat.Prime p).pos
  obtain ⟨r, hr⟩ := Komorebi.PolynomialObstruction.residual_exists p L F x hx
  obtain ⟨t, ht⟩ := hJ (-(reduction p e r))
  have hnonempty : Nonempty (DigitSolutions p F x r) := by
    refine ⟨⟨t, ?_⟩⟩
    rw [ht, add_neg_cancel]
  have ho := (digit_solutions_nonempty_iff p hp F x r).mp hnonempty
  rw [lift_card p L hL F x r hr, ite_eq_left ho, smooth_rank p F x hJ]

/-- At a smooth point the original finite obstruction group has one element. -/
theorem smooth_obstruction_card (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    Nat.card (Obstruction p (jacobian F x)) = 1 := by
  rw [obstruction_card p F x, smooth_rank p F x hJ, Nat.sub_self, pow_zero]

/-- A compatible infinite tower through a smooth root has the same exact
number of possible next-level residue lifts at every stage. -/
theorem exists_regular_tower (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ z : ℕ → Fin d → ℤ,
      z 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ n, Function.Surjective (digitJacobian p F (z n))) ∧
      (∀ n, Nat.card (ActualLifts p (L+n) F (z n)) = p^(d-e)) := by
  have hp : 0 < p := (Fact.out : Nat.Prime p).pos
  obtain ⟨z, hz0, hroot, hstep, hsurj⟩ := exists_compatible_tower p L hp hL F x hx hJ
  refine ⟨z, hz0, hroot, hstep, hsurj, ?_⟩
  intro n
  exact smooth_lift_card p (L+n) (by omega) F (z n) (hroot n) (hsurj n)

end Komorebi.PolynomialSmoothCounts
