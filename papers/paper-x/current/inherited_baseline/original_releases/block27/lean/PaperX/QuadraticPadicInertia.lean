import PaperX.QuadraticValuationInertia
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure
import Mathlib.NumberTheory.Padics.PadicIntegers
import Mathlib.RingTheory.Valuation.LocalSubring

/-!+# Actual valuation rings above the p-adic integers

Local domination is constructed, rather than assumed to exist. The inertia
statement uses the decomposition subgroup of the resulting valuation ring.
-/

noncomputable section

namespace PaperX.QuadraticPadicInertia

variable (p : ℕ) [hp : Fact p.Prime]

abbrev LocalClosure := AlgebraicClosure ℚ_[p]

def integralMap : ℤ_[p] →+* LocalClosure p :=
  (algebraMap ℚ_[p] (LocalClosure p)).comp PadicInt.Coe.ringHom

theorem exists_dominating_valuation :
    ∃ (A : ValuationSubring (LocalClosure p))
      (h : ∀ x : ℤ_[p], integralMap p x ∈ A),
      IsLocalHom ((integralMap p).codRestrict A.toSubring h) :=
  IsLocalRing.exists_factor_valuationRing (integralMap p)

theorem two_isUnit (hodd : p ≠ 2) : IsUnit (2 : ℤ_[p]) := by
  apply PadicInt.isUnit_iff.mpr
  change ‖((2 : ℕ) : ℤ_[p])‖ = 1
  rw [PadicInt.norm_natCast_eq_one_iff]
  exact (hp.out.coprime_iff_not_dvd).mpr (by
    intro h
    exact hodd ((Nat.dvd_prime Nat.prime_two).mp h |>.resolve_left hp.out.ne_one))

theorem two_isUnit_of_contains (hodd : p ≠ 2)
    (A : ValuationSubring (LocalClosure p))
    (h : ∀ x : ℤ_[p], integralMap p x ∈ A) : IsUnit (2 : A) := by
  simpa only [map_ofNat] using
    (two_isUnit p hodd).map ((integralMap p).codRestrict A.toSubring h)

theorem inertia_fixes_square_neg_one (hodd : p ≠ 2)
    (A : ValuationSubring (LocalClosure p))
    (h : ∀ x : ℤ_[p], integralMap p x ∈ A)
    (y : LocalClosure p) (hy : y ^ 2 = -1)
    (σ : A.decompositionSubgroup ℚ_[p]) (hσ : σ ∈ A.inertiaSubgroup ℚ_[p]) :
    (σ.val : LocalClosure p ≃ₐ[ℚ_[p]] LocalClosure p) y = y :=
  QuadraticValuationInertia.inertia_fixes_square_neg_one ℚ_[p] A
    (two_isUnit_of_contains p hodd A h) y hy σ hσ

theorem exists_dominating_valuation_with_fixed_roots (hodd : p ≠ 2) :
    ∃ (A : ValuationSubring (LocalClosure p))
      (h : ∀ x : ℤ_[p], integralMap p x ∈ A),
      IsLocalHom ((integralMap p).codRestrict A.toSubring h) ∧
      ∀ (y : LocalClosure p), y ^ 2 = -1 →
        ∀ (σ : A.decompositionSubgroup ℚ_[p]), σ ∈ A.inertiaSubgroup ℚ_[p] →
          (σ.val : LocalClosure p ≃ₐ[ℚ_[p]] LocalClosure p) y = y := by
  obtain ⟨A, h, hlocal⟩ := exists_dominating_valuation p
  exact ⟨A, h, hlocal, fun y hy σ hσ =>
    inertia_fixes_square_neg_one p hodd A h y hy σ hσ⟩

end PaperX.QuadraticPadicInertia
