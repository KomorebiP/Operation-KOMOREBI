module
public import Euler.WeightedTranslation
@[expose] public section
noncomputable section
set_option maxHeartbeats 800000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The actual source has a full geometric Taylor coefficient bound. -/
lemma eulerSource_coeff_two_dvd (n : ℕ) : (2:D)^n ∣ coeff n eulerSource := by
  rw [eulerSource,coeff_mul]
  apply Finset.dvd_sum
  rintro ⟨i,j⟩ hij
  have he : i+j=n := Finset.mem_antidiagonal.mp hij
  rw [coeff_sourceOddInverse,sourceNumerator_coeff_four]
  refine ⟨(-1:D)^i*(2:D)^j*
    (∑' m, (4:D)^m*(sourceScalar (m+j)*(descPochhammer D (m+j)).coeff j)), ?_⟩
  rw [← he, pow_add, show (-2:D)=(-1:D)*2 by ring,mul_pow,
    show (4:D)^j=(2:D)^j*(2:D)^j by rw [← mul_pow]; norm_num]
  ring

def sourceTwoWeight (n : ℕ) : D := (eulerSource_coeff_two_dvd n).choose

lemma eulerSource_coeff_two (n : ℕ) :
    coeff n eulerSource=(2:D)^n*sourceTwoWeight n :=
  (eulerSource_coeff_two_dvd n).choose_spec

lemma eulerSource_rescale_two :
    eulerSource=rescale (2:D) (mk sourceTwoWeight) := by
  ext n
  simpa only [coeff_rescale,coeff_mk] using eulerSource_coeff_two n

lemma eulerSource_coeff_norm (n : ℕ) :
    ‖coeff n eulerSource‖≤(1/2:ℝ)^n := by
  rw [eulerSource_coeff_two]
  exact norm_two_weight sourceTwoWeight n

/-- Actual analytic translation of the Euler source by any dyadic constant. -/
def sourceShift (a : D) : Series := translatedTwoSeries sourceTwoWeight a

lemma sourceShift_restricted (a : D) : Restricted (sourceShift a) :=
  translatedTwoSeries_restricted _ _

lemma sourceShift_coeff_two (a : D) (n : ℕ) :
    coeff n (sourceShift a) = (2:D)^n*translatedTwoWeight sourceTwoWeight a n := by
  exact coeff_translatedTwoSeries _ _ _

lemma sourceShift_coeff_norm (a : D) (n : ℕ) :
    ‖coeff n (sourceShift a)‖ ≤ (1/2:ℝ)^n := by
  rw [sourceShift_coeff_two]
  exact norm_two_weight _ n

/-- Nonzero-constant translation is justified by convergent double sums. -/
theorem sourceShift_reval (a x : D) :
    reval (sourceShift a) x=reval eulerSource (x+a) := by
  rw [sourceShift,translatedTwoSeries_reval,← eulerSource_rescale_two]

/-- The full infinite evaluation is multiplicative on restricted series. -/
lemma reval_mul {f g : Series} (hf : Restricted f) (hg : Restricted g) (x : D) :
    reval (f*g) x=reval f x*reval g x := by
  let : NonarchimedeanRing D :=
    { is_nonarchimedean := NonarchimedeanAddGroup.is_nonarchimedean }
  have hs := (summable_reval hf x).mul_of_nonarchimedean (summable_reval hg x)
  rw [reval,reval,reval,tsum_mul_tsum_of_nonarchimedean
    (summable_reval hf x) (summable_reval hg x),tsum_antidiagonal_of_summable hs]
  apply tsum_congr
  intro n
  rw [coeff_mul,Finset.sum_mul]
  apply Finset.sum_congr rfl
  rintro ⟨i,j⟩ hij
  have he : i+j=n := Finset.mem_antidiagonal.mp hij
  rw [← he,pow_add]
  ring

lemma polynomial_restricted (p : Polynomial D) : Restricted (p:Series) := by
  rw [restricted_iff]
  apply tendsto_const_nhds.congr'
  filter_upwards [eventually_ge_atTop (p.natDegree+1)] with n hn
  have hp : p.coeff n=0 := Polynomial.coeff_eq_zero_of_natDegree_lt (by omega)
  simp [Polynomial.coeff_coe,hp]

lemma reval_polynomial (p : Polynomial D) (x : D) :
    reval (p:Series) x=p.eval x := by
  simpa only [reval,Polynomial.coeff_coe] using polynomial_eval_tsum p x

end Komorebi.Euler
