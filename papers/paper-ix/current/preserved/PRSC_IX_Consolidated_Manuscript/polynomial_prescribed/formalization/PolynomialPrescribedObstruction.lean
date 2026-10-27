module
public import PolynomialPrescribedLifts
public import PolynomialPrescribedCounts

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped Classical

namespace Komorebi.PolynomialPrescribedObstruction
open PolynomialObstruction PolynomialDigitBridge PolynomialPrescribedSystem
open PolynomialPrescribedLifts PolynomialParameterSystem ResidueLiftDigits
variable {m k e : ℕ}

/-- The solved-block cokernel class decides actual next-level residue lifts with
the requested parameter digits, including positive composite moduli. -/
theorem prescribed_lift_iff_obstruction_zero (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ) ^ L • r)
    (v : Fin k → ZMod q) :
    Nonempty (PrescribedLifts q L F x v) ↔ PolynomialPrescribedSystem.obstruction q F x r v = 0 := by
  have he := prescribedDigitEquivLifts q L hq hL F x r hr v
  constructor
  · rintro ⟨y⟩
    exact (prescribed_digits_nonempty_iff q F x r v).mp ⟨he.symm y⟩
  · intro h
    obtain ⟨u⟩ := (prescribed_digits_nonempty_iff q F x r v).mpr h
    exact ⟨he u⟩

/-- Expanded actual residue-vector form: the lower residue, the polynomial root
condition, and the prescribed next parameter residues are all explicit. -/
theorem prescribed_residue_exists_iff (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ) ^ L • r)
    (v : Fin k → ZMod q) :
    (∃ y : Fin (m + k) → ZMod (q ^ (L + 1)),
      (∀ i, (q : ℤ) ^ L ∣ ((y i).val : ℤ) - x i) ∧
      (∀ i, (q : ℤ) ^ (L + 1) ∣ evalSystem F (integerLift (q ^ (L + 1)) y) i) ∧
      (∀ j : Fin k, y (Fin.natAdd m j) =
        ((x (Fin.natAdd m j) + (q : ℤ) ^ L * ((v j).val : ℤ) : ℤ) :
          ZMod (q ^ (L + 1))))) ↔ PolynomialPrescribedSystem.obstruction q F x r v = 0 := by
  rw [← prescribed_lift_iff_obstruction_zero q L hq hL F x r hr v]
  constructor
  · rintro ⟨y, hy, hF, hv⟩
    exact ⟨⟨⟨⟨y, hy⟩, hF⟩, funext hv⟩⟩
  · rintro ⟨y⟩
    exact ⟨y.val.val.val, y.val.val.property, y.val.property, fun j => congrFun y.property j⟩

/-- The solved-block cokernel is finite for every positive modulus. -/
theorem prescribed_obstruction_finite (q : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ) :
    Finite (PrescribedObstruction q F x) := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  unfold PrescribedObstruction
  infer_instance

/-- The residual and a single finite obstruction object are obtained from the
actual lower root, uniformly for every choice of the parameter digit. -/
theorem finite_prescribed_obstruction (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ) ^ L ∣ evalSystem F x i) :
    ∃ r : Fin e → ℤ, evalSystem F x = (q : ℤ) ^ L • r ∧
      Finite (PrescribedObstruction q F x) ∧
      (∀ v : Fin k → ZMod q, Nonempty (PrescribedLifts q L F x v) ↔
        PolynomialPrescribedSystem.obstruction q F x r v = 0) := by
  obtain ⟨r, hr⟩ := residual_exists q L F x hx
  exact ⟨r, hr, prescribed_obstruction_finite q hq F x,
    fun v => prescribed_lift_iff_obstruction_zero q L hq hL F x r hr v⟩

/-- From an actual lower root, every prescribed parameter fiber has the exact
prime-field count, and the solved-block obstruction has its exact cardinality. -/
theorem finite_prescribed_lift_count (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (p : ℤ) ^ L ∣ evalSystem F x i) :
    ∃ r : Fin e → ℤ, evalSystem F x = (p : ℤ) ^ L • r ∧
      (∀ v : Fin k → ZMod p,
        (Nonempty (PrescribedLifts p L F x v) ↔
          PolynomialPrescribedSystem.obstruction p F x r v = 0) ∧
        Nat.card (PrescribedLifts p L F x v) =
          if PolynomialPrescribedSystem.obstruction p F x r v = 0 then
            p ^ (m - FiniteFiberCounts.rank p (PolynomialPrescribedSystem.solvedJacobian p F x))
          else 0) ∧
      Nat.card (PrescribedObstruction p F x) =
        p ^ (e - FiniteFiberCounts.rank p (PolynomialPrescribedSystem.solvedJacobian p F x)) := by
  obtain ⟨r, hr⟩ := residual_exists p L F x hx
  refine ⟨r, hr, ?_, PolynomialPrescribedCounts.obstruction_card p F x⟩
  intro v
  exact ⟨prescribed_lift_iff_obstruction_zero p L (Fact.out : Nat.Prime p).pos hL F x r hr v,
    PolynomialPrescribedCounts.lift_card p L hL F x r hr v⟩

end Komorebi.PolynomialPrescribedObstruction
