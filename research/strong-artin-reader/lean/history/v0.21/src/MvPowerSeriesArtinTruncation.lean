import MvPolynomialExprCompiler
import NilpotentMonomialEvaluation
import Mathlib.RingTheory.MvPowerSeries.Trunc

/-!
# Finite-level truncation of multivariate formal power series

At coordinates lying in the principal ideal `(pi)`, every monomial of total
degree at least `N` vanishes once `pi^N = 0`.  Evaluation of a formal power
series therefore depends only on its total-degree-`N` truncation.
-/

namespace Komorebi.StrongArtin.MvPowerSeriesArtinTruncation

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.NilpotentMonomialEvaluation

noncomputable section

variable {R ι : Type*} [CommRing R] [Finite ι]

/-- Finite Artin-level evaluation by total-degree truncation. -/
def artinEval (N : ℕ) (f : MvPowerSeries ι R) (x : ι → R) : R :=
  MvPolynomial.eval x (f.truncTotal N)

@[simp] theorem artinEval_def (N : ℕ) (f : MvPowerSeries ι R) (x : ι → R) :
    artinEval N f x = MvPolynomial.eval x (f.truncTotal N) := rfl

/-- A monomial occurring in the smaller truncation also occurs in the larger
truncation, with the same coefficient. -/
theorem support_truncTotal_mono {N M : ℕ} (hNM : N ≤ M)
    (f : MvPowerSeries ι R) :
    (f.truncTotal N).support ⊆ (f.truncTotal M).support := by
  intro d hd
  have hcoeffN : (f.truncTotal N).coeff d ≠ 0 :=
    MvPolynomial.mem_support_iff.mp hd
  have hdegN : d.degree < N := by
    by_contra hnot
    have hz := MvPowerSeries.coeff_truncTotal_eq_zero f (not_lt.mp hnot)
    exact hcoeffN hz
  have hdegM : d.degree < M := lt_of_lt_of_le hdegN hNM
  apply MvPolynomial.mem_support_iff.mpr
  rw [MvPowerSeries.coeff_truncTotal f hdegM,
      ← MvPowerSeries.coeff_truncTotal f hdegN]
  exact hcoeffN

/-- Total-degree truncations evaluate identically after the nilpotence cutoff. -/
theorem eval_truncTotal_stable {N M : ℕ} (hNM : N ≤ M)
    (pi : R) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (f : MvPowerSeries ι R) :
    MvPolynomial.eval x (f.truncTotal M) =
      MvPolynomial.eval x (f.truncTotal N) := by
  classical
  let pN := f.truncTotal N
  let pM := f.truncTotal M
  have hsupp : pN.support ⊆ pM.support := by
    simpa [pN, pM] using support_truncTotal_mono hNM f
  rw [MvPolynomial.eval_eq, MvPolynomial.eval_eq]
  calc
    (∑ d ∈ pM.support,
        pM.coeff d * ∏ i ∈ d.support, x i ^ d i) =
      ∑ d ∈ pN.support,
        pM.coeff d * ∏ i ∈ d.support, x i ^ d i := by
        symm
        apply Finset.sum_subset hsupp
        intro d hdM hdN
        have hdeg : N ≤ d.degree := by
          by_contra hnot
          have hlt : d.degree < N := lt_of_not_ge hnot
          have hcoeffM : pM.coeff d ≠ 0 :=
            MvPolynomial.mem_support_iff.mp hdM
          have hdegM : d.degree < M := lt_of_lt_of_le hlt hNM
          have hcoeffEq : pN.coeff d = pM.coeff d := by
            simp only [pN, pM]
            rw [MvPowerSeries.coeff_truncTotal f hlt,
                MvPowerSeries.coeff_truncTotal f hdegM]
          exact hdN (MvPolynomial.mem_support_iff.mpr (hcoeffEq.trans_ne hcoeffM))
        have hzero : ∏ i ∈ d.support, x i ^ d i = 0 := by
          simpa [Finsupp.prod] using
            monomialValue_eq_zero_of_nilpotent_depth pi N hpi x hx d hdeg
        simp [hzero]
    _ = ∑ d ∈ pN.support,
        pN.coeff d * ∏ i ∈ d.support, x i ^ d i := by
        apply Finset.sum_congr rfl
        intro d hd
        have hdegN : d.degree < N := by
          have hcoeffN : pN.coeff d ≠ 0 :=
            MvPolynomial.mem_support_iff.mp hd
          by_contra hnot
          have hz : pN.coeff d = 0 := by
            dsimp [pN]
            exact MvPowerSeries.coeff_truncTotal_eq_zero f (not_lt.mp hnot)
          exact hcoeffN hz
        have hdegM : d.degree < M := lt_of_lt_of_le hdegN hNM
        simp only [pN, pM]
        rw [MvPowerSeries.coeff_truncTotal f hdegM,
            MvPowerSeries.coeff_truncTotal f hdegN]

/-- `artinEval` is independent of all later truncation levels once the
nilpotence exponent has been reached. -/
theorem artinEval_stable {N M : ℕ} (hNM : N ≤ M)
    (pi : R) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (f : MvPowerSeries ι R) :
    artinEval M f x = artinEval N f x := by
  exact eval_truncTotal_stable hNM pi hpi x hx f

/-- Compile a formal power series at Artin level `N` into the v0.20 finite
expression syntax. -/
def compileAt (N : ℕ) (f : MvPowerSeries ι R) :
    Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr ι R :=
  Komorebi.StrongArtin.MvPolynomialExprCompiler.compile (f.truncTotal N)

@[simp] theorem eval_compileAt (N : ℕ) (f : MvPowerSeries ι R) (x : ι → R) :
    Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval (compileAt N f) x =
      artinEval N f x := by
  simp [compileAt, artinEval]

end

end Komorebi.StrongArtin.MvPowerSeriesArtinTruncation

#print axioms Komorebi.StrongArtin.MvPowerSeriesArtinTruncation.eval_truncTotal_stable
#print axioms Komorebi.StrongArtin.MvPowerSeriesArtinTruncation.eval_compileAt
