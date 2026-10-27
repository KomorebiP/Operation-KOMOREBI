import KomorebiPaperVI.FractionalSemigroup
import Mathlib.Analysis.Normed.Group.FunctionSeries

/-! Author: Komorebi P. Uniform bounded-time control from summable actual fractional defects.
The generator-to-fractional estimates remain the separate obligation of Theorem 10.3. -/
namespace KomorebiPaperVI.FractionalTowers
open Set
open KomorebiPaperVI.FractionalSemigroup
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

noncomputable def timeDefect (A C : ℕ → R) (a t : ℝ) (n : ℕ) : R :=
  C n*evolution (A (n+1)) a t-evolution (A n) a t*C n

theorem bounded_time_majorant (A C : ℕ → R) (hA : ∀ n,0 ≤ A n)
    (a T : ℝ) (ha : 0 < a) (n : ℕ) (t : ℝ) (ht : t∈Icc 0 T) :
    ‖timeDefect A C a t n‖ ≤ T*‖defect (A (n+1)) (A n) (C n) a‖ := by
  exact (fractional_contraction_bound _ _ _ (hA (n+1)) (hA n) a t ha ht.1).trans
    (mul_le_mul_of_nonneg_right ht.2 (norm_nonneg _))

theorem time_defects_norm_summable (A C : ℕ → R) (hA : ∀ n,0 ≤ A n)
    (a t : ℝ) (ha : 0 < a) (ht : 0 ≤ t)
    (hs : Summable (fun n => ‖defect (A (n+1)) (A n) (C n) a‖)) :
    Summable (fun n => ‖timeDefect A C a t n‖) := by
  apply (hs.mul_left t).of_norm_bounded
  intro n
  rw [Real.norm_of_nonneg (norm_nonneg _)]
  exact fractional_contraction_bound _ _ _ (hA (n+1)) (hA n) a t ha ht

theorem time_defects_summable (A C : ℕ → R) (hA : ∀ n,0 ≤ A n)
    (a t : ℝ) (ha : 0 < a) (ht : 0 ≤ t)
    (hs : Summable (fun n => ‖defect (A (n+1)) (A n) (C n) a‖)) :
    Summable (timeDefect A C a t) := (time_defects_norm_summable A C hA a t ha ht hs).of_norm

theorem bounded_time_uniform_convergence (A C : ℕ → R) (hA : ∀ n,0 ≤ A n)
    (a T : ℝ) (ha : 0 < a)
    (hs : Summable (fun n => ‖defect (A (n+1)) (A n) (C n) a‖)) :
    TendstoUniformlyOn (fun N t => ∑ n ∈ Finset.range N,timeDefect A C a t n)
      (fun t => ∑' n,timeDefect A C a t n) Filter.atTop (Icc 0 T) := by
  apply tendstoUniformlyOn_tsum_nat (hs.mul_left T)
  intro n t ht
  exact bounded_time_majorant A C hA a T ha n t ht

end KomorebiPaperVI.FractionalTowers
