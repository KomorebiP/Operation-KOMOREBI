module
public import PolynomialPrescribedSystem
public import PolynomialLiftCounts

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedLifts
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
open Komorebi.PolynomialDigitBridge Komorebi.PolynomialLiftCounts
open Komorebi.PolynomialParameterSystem Komorebi.ResidueLiftDigits
open Komorebi.PolynomialPrescribedSystem
variable {m k e : ℕ}

/-- Actual polynomial residue lifts whose free coordinates have the prescribed
next-level residue classes. The condition fixes residue classes, not chosen
integer representatives of the parameter digits. -/
abbrev PrescribedLifts (q L : ℕ)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (v : Fin k → ZMod q) :=
  {y : ActualLifts q L F x //
    freePart y.val.val = digitResidue q L (freePart x) v}

/-- Taking the free coordinates commutes with forming actual digit residues. -/
theorem freePart_digitResidue (q L : ℕ) (x : Fin (m + k) → ℤ)
    (t : Fin (m + k) → ZMod q) :
    freePart (digitResidue q L x t) = digitResidue q L (freePart x) (freePart t) := rfl

/-- Solved correction digits are precisely full correction solutions with the
specified parameter digit. -/
def prescribedDigitEquivRestricted (q : ℕ)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (v : Fin k → ZMod q) :
    PrescribedDigits q F x r v ≃ {t : DigitSolutions q F x r // freePart t.val = v} where
  toFun u := ⟨⟨join u.val v, (prescribed_equation_iff q F x r v u.val).mp u.property⟩,
    freePart_join u.val v⟩
  invFun t := ⟨solvedPart t.val.val, (prescribed_equation_iff q F x r v _).mpr (by
    rw [← t.property, join_parts]
    exact t.val.property)⟩
  left_inv u := by
    apply Subtype.ext
    exact solvedPart_join u.val v
  right_inv t := by
    apply Subtype.ext
    apply Subtype.ext
    change join (solvedPart t.val.val) v = t.val.val
    rw [← t.property, join_parts]

/-- The unrestricted digit-to-lift equivalence retains exactly the parameter
constraint, including for composite moduli and the degenerate modulus one. -/
def restrictedDigitEquivLifts (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ) ^ L • r)
    (v : Fin k → ZMod q) :
    {t : DigitSolutions q F x r // freePart t.val = v} ≃ PrescribedLifts q L F x v :=
  Equiv.subtypeEquiv (digitEquivLifts q L hq hL F x r hr) (fun t => by
    change freePart t.val = v ↔
      freePart (digitResidue q L x t.val) = digitResidue q L (freePart x) v
    rw [freePart_digitResidue]
    constructor
    · intro h
      rw [h]
    · intro h
      exact digitResidue_injective q L hq (freePart x) h)

/-- The prescribed solved-digit fiber parametrizes exactly the actual next-level
polynomial residues having the prescribed parameter digits. -/
def prescribedDigitEquivLifts (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ) ^ L • r)
    (v : Fin k → ZMod q) :
    PrescribedDigits q F x r v ≃ PrescribedLifts q L F x v :=
  (prescribedDigitEquivRestricted q F x r v).trans
    (restrictedDigitEquivLifts q L hq hL F x r hr v)

/-- The equivalence sends a solved digit to its actual shifted residue vector. -/
@[simp] theorem prescribedDigitEquivLifts_apply (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ) ^ L • r)
    (v : Fin k → ZMod q) (u : PrescribedDigits q F x r v) :
    (prescribedDigitEquivLifts q L hq hL F x r hr v u).val.val.val =
      digitResidue q L x (join u.val v) := rfl

end Komorebi.PolynomialPrescribedLifts
