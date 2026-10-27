module
public import PolynomialPrescribedLifts
public import FiniteFiberCounts

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped Classical

namespace Komorebi.PolynomialPrescribedCounts
open Komorebi.PolynomialObstruction Komorebi.PolynomialPrescribedSystem
open Komorebi.PolynomialPrescribedLifts
variable {m k e : ℕ}

/-- The solved-block kernel acts freely and transitively on compatible solved digits.
The action is ordinary translation and does not require a chosen valid digit. -/
@[instance_reducible] def digitAddTorsor (q : ℕ)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (v : Fin k → ZMod q) (h : obstruction q F x r v = 0) :
    AddTorsor (solvedJacobian q F x).ker (PrescribedDigits q F x r v) :=
  FiniteFiberCounts.fiberAddTorsor (solvedJacobian q F x) (parameterResidual q F x r v)
    ((prescribed_digits_nonempty_iff q F x r v).mpr h)

/-- A chosen valid solved digit identifies all actual prescribed lifts with the kernel. -/
def liftEquivKernel (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (v : Fin k → ZMod q) (u : PrescribedDigits q F x r v) :
    PrescribedLifts q L F x v ≃ (solvedJacobian q F x).ker :=
  (prescribedDigitEquivLifts q L hq hL F x r hr v).symm.trans
    (FiniteFiberCounts.fiberEquivKernel (solvedJacobian q F x)
      (parameterResidual q F x r v) u)

/-- The actual residue lifts inherit the natural kernel action through their exact
digit equivalence. No base lift is chosen to define this torsor. -/
@[instance_reducible] def liftAddTorsor (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (v : Fin k → ZMod q) (h : obstruction q F x r v = 0) :
    AddTorsor (solvedJacobian q F x).ker (PrescribedLifts q L F x v) := by
  let E := prescribedDigitEquivLifts q L hq hL F x r hr v
  let J := solvedJacobian q F x
  let b := parameterResidual q F x r v
  exact {
    vadd := fun w t => E (FiniteFiberCounts.translate J b w (E.symm t))
    zero_vadd := by
      intro t
      change E (FiniteFiberCounts.translate J b 0 (E.symm t)) = t
      rw [FiniteFiberCounts.translate_zero, E.apply_symm_apply]
    add_vadd := by
      intro w z t
      change E (FiniteFiberCounts.translate J b (w + z) (E.symm t)) =
        E (FiniteFiberCounts.translate J b w
          (E.symm (E (FiniteFiberCounts.translate J b z (E.symm t)))))
      rw [E.symm_apply_apply, FiniteFiberCounts.translate_add]
    vsub := fun t u => FiniteFiberCounts.difference J b (E.symm t) (E.symm u)
    nonempty := by
      obtain ⟨u⟩ := (prescribed_digits_nonempty_iff q F x r v).mpr h
      exact ⟨E u⟩
    vsub_vadd' := by
      intro t u
      change E (FiniteFiberCounts.translate J b
        (FiniteFiberCounts.difference J b (E.symm t) (E.symm u)) (E.symm u)) = t
      rw [FiniteFiberCounts.translate_difference, E.apply_symm_apply]
    vadd_vsub' := by
      intro w t
      change FiniteFiberCounts.difference J b
        (E.symm (E (FiniteFiberCounts.translate J b w (E.symm t)))) (E.symm t) = w
      rw [E.symm_apply_apply, FiniteFiberCounts.difference_translate] }

/-- A nonempty prescribed lift set has exactly the solved-kernel cardinality,
without requiring the modulus to be prime. -/
theorem lift_card_eq_kernel (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (v : Fin k → ZMod q) (h : obstruction q F x r v = 0) :
    Nat.card (PrescribedLifts q L F x v) = Nat.card (solvedJacobian q F x).ker := by
  obtain ⟨u⟩ := (prescribed_digits_nonempty_iff q F x r v).mpr h
  exact Nat.card_congr (liftEquivKernel q L hq hL F x r hr v u)

/-- The cardinality of the prescribed solved digits obeys rank-nullity over a prime field. -/
theorem digit_card (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (v : Fin k → ZMod p) :
    Nat.card (PrescribedDigits p F x r v) =
      if obstruction p F x r v = 0 then
        p ^ (m - FiniteFiberCounts.rank p (solvedJacobian p F x)) else 0 := by
  have hc := FiniteFiberCounts.fiber_card p (solvedJacobian p F x)
    (parameterResidual p F x r v)
  change Nat.card (PrescribedDigits p F x r v) =
    if Nonempty (PrescribedDigits p F x r v) then
      p ^ (m - FiniteFiberCounts.rank p (solvedJacobian p F x)) else 0 at hc
  rw [prescribed_digits_nonempty_iff p F x r v] at hc
  exact hc

/-- Exact count of distinct actual next-level roots with the specified parameter digit. -/
theorem lift_card (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (p : ℤ)^L • r)
    (v : Fin k → ZMod p) :
    Nat.card (PrescribedLifts p L F x v) =
      if obstruction p F x r v = 0 then
        p ^ (m - FiniteFiberCounts.rank p (solvedJacobian p F x)) else 0 := by
  have hp : 0 < p := (Fact.out : Nat.Prime p).pos
  rw [← Nat.card_congr (prescribedDigitEquivLifts p L hp hL F x r hr v)]
  exact digit_card p F x r v

/-- Dimension of the obstruction space for the solved block. -/
theorem obstruction_finrank (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ) :
    Module.finrank (ZMod p) (PrescribedObstruction p F x) =
      e - FiniteFiberCounts.rank p (solvedJacobian p F x) :=
  FiniteFiberCounts.cokernel_finrank p (solvedJacobian p F x)

/-- Exact cardinality of the prescribed-parameter obstruction space. -/
theorem obstruction_card (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ) :
    Nat.card (PrescribedObstruction p F x) =
      p ^ (e - FiniteFiberCounts.rank p (solvedJacobian p F x)) :=
  FiniteFiberCounts.cokernel_card p (solvedJacobian p F x)

end Komorebi.PolynomialPrescribedCounts
