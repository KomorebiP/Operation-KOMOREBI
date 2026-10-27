module
public import PolynomialDigitBridge
public import ResidueLiftDigits
public import FiniteFiberCounts
public import IntegerFiniteCokernel

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped Classical

namespace Komorebi.PolynomialLiftCounts
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
open Komorebi.PolynomialDigitBridge Komorebi.ResidueLiftDigits
variable {d e : ℕ}

/-- Actual next-level residue classes solving the original polynomial equations
and retaining the prescribed lower residue. Evaluation uses their canonical
integer representatives; polynomial congruence makes this representative independent. -/
abbrev ActualLifts (q L : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) :=
  {y : ResidueFiber q L x // ∀ i, (q : ℤ)^(L+1) ∣
    evalSystem F (integerLift (q^(L+1)) y.val) i}

/-- The residue class represented by a correction solves the actual equations
exactly when the finite Jacobian cancels the residual digit. -/
theorem digit_residue_solution_iff (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (t : Fin d → ZMod q) :
    (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F
      (integerLift (q^(L+1)) (digitEquivResidue q L hq x t).val) i) ↔
      reduction q e r + digitJacobian q F x t = 0 := by
  rw [← digit_solution_iff q L hq hL F x r hr t]
  apply forall_congr'
  intro i
  apply dvd_iff_of_dvd_sub
  apply Komorebi.PolynomialTaylor.eval_dvd_of_dvd
  intro k
  exact next_modulus_dvd_val_sub_shift q L hq x t k

/-- The correction-digit fiber is precisely the finite set of actual polynomial lifts. -/
def digitEquivLifts (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r) :
    DigitSolutions q F x r ≃ ActualLifts q L F x :=
  Equiv.subtypeEquiv (digitEquivResidue q L hq x)
    (fun t => (digit_residue_solution_iff q L hq hL F x r hr t).symm)

/-- The actual nonempty digit fiber carries its natural kernel torsor structure. -/
@[instance_reducible] def digitAddTorsor (q : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) (r : Fin e → ℤ)
    (h : obstruction q (jacobian F x) r = 0) :
    AddTorsor (digitJacobian q F x).ker (DigitSolutions q F x r) :=
  FiniteFiberCounts.fiberAddTorsor (digitJacobian q F x) (reduction q e r)
    ((digit_solutions_nonempty_iff q hq F x r).mpr h)

/-- A chosen valid digit identifies all distinct next-level lifts with the kernel. -/
def liftEquivKernel (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (u : DigitSolutions q F x r) :
    ActualLifts q L F x ≃ (digitJacobian q F x).ker :=
  (digitEquivLifts q L hq hL F x r hr).symm.trans
    (FiniteFiberCounts.fiberEquivKernel (digitJacobian q F x) (reduction q e r) u)

/-- The previously constructed obstruction is the actual residue-ring cokernel. -/
def obstructionEquiv (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    Obstruction q (jacobian F x) ≃ₗ[ℤ]
      ((Fin e → ZMod q) ⧸ (digitJacobian q F x).range) :=
  IntegerFiniteCokernel.cokernelEquiv q (jacobian F x) (digitJacobian q F x)
    (reduction_jacobian q F x)

@[simp] theorem obstructionEquiv_class (q : ℕ)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) (r : Fin e → ℤ) :
    obstructionEquiv q F x (obstruction q (jacobian F x) r) =
      Submodule.Quotient.mk (reduction q e r) := rfl

/-- Exact count of distinct polynomial lift classes; an obstruction gives zero. -/
theorem lift_card (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (p : ℤ)^L • r) :
    Nat.card (ActualLifts p L F x) =
      if obstruction p (jacobian F x) r = 0 then
        p ^ (d - FiniteFiberCounts.rank p (digitJacobian p F x)) else 0 := by
  have hp : 0 < p := (Fact.out : Nat.Prime p).pos
  have hc := FiniteFiberCounts.fiber_card p (digitJacobian p F x) (reduction p e r)
  change Nat.card (DigitSolutions p F x r) =
    if Nonempty (DigitSolutions p F x r) then
      p ^ (d - FiniteFiberCounts.rank p (digitJacobian p F x)) else 0 at hc
  rw [digit_solutions_nonempty_iff p hp F x r] at hc
  rw [← Nat.card_congr (digitEquivLifts p L hp hL F x r hr)]
  exact hc

/-- Exact cardinality of the original obstruction group, not just a surrogate. -/
theorem obstruction_card (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    Nat.card (Obstruction p (jacobian F x)) =
      p ^ (e - FiniteFiberCounts.rank p (digitJacobian p F x)) := by
  rw [Nat.card_congr (obstructionEquiv p F x).toEquiv]
  exact FiniteFiberCounts.cokernel_card p (digitJacobian p F x)

/-- Counts and residual are obtained from the actual lower polynomial solution. -/
theorem finite_polynomial_lift_count (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i) :
    ∃ r : Fin e → ℤ,
      evalSystem F x = (p : ℤ)^L • r ∧
      Nat.card (ActualLifts p L F x) =
        (if obstruction p (jacobian F x) r = 0 then
          p ^ (d - FiniteFiberCounts.rank p (digitJacobian p F x)) else 0) ∧
      Nat.card (Obstruction p (jacobian F x)) =
        p ^ (e - FiniteFiberCounts.rank p (digitJacobian p F x)) := by
  obtain ⟨r, hr⟩ := Komorebi.PolynomialObstruction.residual_exists p L F x hx
  exact ⟨r, hr, lift_card p L hL F x r hr, obstruction_card p F x⟩

end Komorebi.PolynomialLiftCounts
