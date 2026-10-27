import MvPowerSeriesArtinTruncation
import Mathlib.RingTheory.MvPowerSeries.Substitution
import Mathlib.RingTheory.MvPowerSeries.Equiv

/-!
# Canonical nilpotent substitution equals finite Artin truncation

A formal power series evaluated on coordinates in the principal nilpotent ideal
is equal to the evaluation of its finite total-degree truncation.  The left side
uses Mathlib's actual substitution operation; the right side is the finite
polynomial evaluation compiled in the preceding modules.
-/

namespace Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.NilpotentMonomialEvaluation
open Komorebi.StrongArtin.MvPowerSeriesArtinTruncation

noncomputable section

variable {R ι : Type*} [CommRing R]

/-- Constant power-series substitution attached to a point. -/
def constSubst (x : ι → R) : ι → MvPowerSeries Empty R :=
  fun i => MvPowerSeries.C (x i)

@[simp] theorem constantCoeff_constSubst (x : ι → R) (i : ι) :
    MvPowerSeries.constantCoeff (constSubst x i) = x i := by
  simp [constSubst]

/-- Canonical algebraic evaluation by substitution into power series with no
remaining variables.  Under nilpotence this is genuine substitution rather than
the dummy branch of `MvPowerSeries.subst`. -/
def formalEval (f : MvPowerSeries ι R) (x : ι → R) : R :=
  MvPowerSeries.isEmptyEquiv Empty R (MvPowerSeries.subst (constSubst x) f)

@[simp] theorem formalEval_coe (p : MvPolynomial ι R) (x : ι → R) :
    formalEval (p : MvPowerSeries ι R) x = MvPolynomial.eval x p := by
  classical
  simp [formalEval, MvPowerSeries.subst_coe, MvPolynomial.aeval_def,
    MvPolynomial.eval₂_eq, MvPolynomial.eval_eq, constSubst,
    MvPowerSeries.algebraMap_apply]

/-- The constant coefficient of one substituted monomial is its ordinary
monomial value. -/
theorem constantCoeff_monomial_constSubst (x : ι → R) (d : ι →₀ ℕ) :
    MvPowerSeries.constantCoeff
      (d.prod fun i n => (constSubst x i) ^ n) =
        d.prod fun i n => x i ^ n := by
  simp [constSubst, map_finsuppProd]

/-- Coordinates divisible by `pi` are nilpotent when `pi` is. -/
theorem isNilpotent_coord_of_powDivisible
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i)) (i : ι) :
    IsNilpotent (x i) := by
  refine ⟨N, ?_⟩
  exact eq_zero_of_pow_eq_zero
    (powDivisible_pow_of_depth_one (hx i) N) hpi

variable [Finite ι]

/-- Constant substitution is admissible on a principal nilpotent point. -/
theorem hasSubst_constSubst
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i)) :
    MvPowerSeries.HasSubst (constSubst x) := by
  apply MvPowerSeries.hasSubst_of_constantCoeff_nilpotent
  intro i
  simpa [constSubst] using
    isNilpotent_coord_of_powDivisible pi N hpi x hx i

/-- Canonical formal substitution at a principal nilpotent point is exactly
finite total-degree truncation evaluation. -/
theorem formalEval_eq_artinEval
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (f : MvPowerSeries ι R) :
    formalEval f x = artinEval N f x := by
  classical
  let a := constSubst x
  have ha : MvPowerSeries.HasSubst a := by
    simpa [a] using hasSubst_constSubst pi N hpi x hx
  let term : (ι →₀ ℕ) → R := fun d =>
    MvPowerSeries.coeff d f •
      MvPowerSeries.constantCoeff (d.prod fun i n => (a i) ^ n)
  have hsupport : Function.support term ⊆ ↑((f.truncTotal N).support) := by
    intro d hd
    have hterm : term d ≠ 0 := hd
    have hdeg : d.degree < N := by
      by_contra hnot
      have hmon : d.prod (fun i n => x i ^ n) = 0 :=
        monomialValue_eq_zero_of_nilpotent_depth pi N hpi x hx d (not_lt.mp hnot)
      have hcc : MvPowerSeries.constantCoeff
          (d.prod fun i n => (a i) ^ n) = 0 := by
        simpa [a, constantCoeff_monomial_constSubst] using hmon
      exact hterm (by simp [term, hcc])
    have hcoeff : MvPowerSeries.coeff d f ≠ 0 := by
      intro hz
      exact hterm (by simp [term, hz])
    apply MvPolynomial.mem_support_iff.mpr
    rw [MvPowerSeries.coeff_truncTotal f hdeg]
    exact hcoeff
  rw [formalEval, MvPowerSeries.isEmptyEquiv_apply,
    MvPowerSeries.constantCoeff_subst ha f]
  change (∑ᶠ d, term d) = artinEval N f x
  rw [finsum_eq_sum_of_support_subset term hsupport]
  rw [artinEval, MvPolynomial.eval_eq]
  apply Finset.sum_congr rfl
  intro d hd
  have hdeg : d.degree < N := by
    have hcoeff : (f.truncTotal N).coeff d ≠ 0 :=
      MvPolynomial.mem_support_iff.mp hd
    by_contra hnot
    exact hcoeff (MvPowerSeries.coeff_truncTotal_eq_zero f (not_lt.mp hnot))
  rw [MvPowerSeries.coeff_truncTotal f hdeg]
  simp [term, a, Finsupp.prod]

/-- The canonical evaluation is independent of any later truncation after the
nilpotence cutoff. -/
theorem formalEval_eq_later_truncation {M : ℕ}
    (pi : R) (N : ℕ) (hNM : N ≤ M) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (f : MvPowerSeries ι R) :
    formalEval f x = MvPolynomial.eval x (f.truncTotal M) := by
  rw [formalEval_eq_artinEval pi N hpi x hx f]
  symm
  exact eval_truncTotal_stable hNM pi hpi x hx f

end

end Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution

#print axioms Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution.formalEval_eq_artinEval
#print axioms Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution.formalEval_eq_later_truncation
