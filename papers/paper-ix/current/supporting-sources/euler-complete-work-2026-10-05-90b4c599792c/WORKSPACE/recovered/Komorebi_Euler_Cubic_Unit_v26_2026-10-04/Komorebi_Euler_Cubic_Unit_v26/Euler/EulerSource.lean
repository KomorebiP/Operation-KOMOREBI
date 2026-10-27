module
public import Euler.SourceNewton
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The integral geometric inverse of 1+2X on the whole dyadic unit disc. -/
def sourceOddInverse : Series := mk fun n => (-2:D)^n

@[simp] lemma coeff_sourceOddInverse (n : ℕ) :
    coeff n sourceOddInverse=(-2:D)^n := by simp [sourceOddInverse]

lemma sourceOddInverse_restricted : Restricted sourceOddInverse := by
  rw [restricted_iff]
  have hp : ‖(-2:D)‖=(1/2:ℝ) := by
    rw [norm_neg]
    have h := PadicInt.norm_p (p:=2)
    norm_num at h
    exact h
  simp only [coeff_sourceOddInverse,norm_pow,hp]
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

lemma sourceOddInverse_identity :
    (1+C (2:D)*X)*sourceOddInverse=1 := by
  rw [add_mul,one_mul,mul_assoc]
  ext n
  cases n with
  | zero => simp [sourceOddInverse,constantCoeff_mk]
  | succ n =>
    simp only [map_add,coeff_C_mul,coeff_succ_X_mul,coeff_sourceOddInverse,
      coeff_one,Nat.succ_ne_zero,ite_false]
    rw [pow_succ]
    ring

/-- Actual analytic Euler source, constructed from Newton taps rather than an assumed formula. -/
def eulerSource : Series := sourceOddInverse*sourceNumerator

theorem eulerSource_restricted : Restricted eulerSource :=
  PowerSeries.isRestricted.mul 1 sourceOddInverse_restricted sourceNumerator_restricted

lemma eulerSource_identity : (1+C (2:D)*X)*eulerSource=sourceNumerator := by
  rw [eulerSource,← mul_assoc,sourceOddInverse_identity,one_mul]

lemma reval_C_mul {f : Series} (hf : Restricted f) (a x : D) :
    reval (C a*f) x=a*reval f x := by
  simp only [reval,coeff_C_mul,mul_assoc]
  exact (summable_reval hf x).tsum_mul_left a

lemma reval_X_mul {f : Series} (hf : Restricted f) (x : D) :
    reval (X*f) x=x*reval f x := by
  have hs := (PowerSeries.isRestricted.mul 1
    (PowerSeries.isRestricted_monomial 1 1 (1:D)) hf)
  have hx : Restricted ((X:Series)*f) := by simpa only [← PowerSeries.X_eq] using hs
  rw [reval,← (summable_reval hx x).sum_add_tsum_nat_add 1]
  simp only [Finset.sum_range_one,coeff_zero_X_mul,zero_mul,zero_add,
    coeff_succ_X_mul,pow_succ]
  simp only [← mul_assoc]
  rw [(summable_reval hf x).tsum_mul_right x]
  exact mul_comm _ _

/-- Multiplication by a linear polynomial is compatible with actual infinite evaluation. -/
lemma reval_linear_mul {f : Series} (hf : Restricted f) (a x : D) :
    reval ((1+C a*X)*f) x=(1+a*x)*reval f x := by
  rw [add_mul,one_mul,mul_assoc]
  have hx : Restricted ((X:Series)*f) := by
    exact PowerSeries.isRestricted.mul 1
      (by simpa only [← PowerSeries.X_eq] using PowerSeries.isRestricted_monomial 1 1 (1:D)) hf
  rw [reval_add hf (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 a) hx),
    reval_C_mul hx,reval_X_mul hf]
  ring

/-- The denominator-cleared identity holds on every dyadic argument. -/
theorem eulerSource_reval_identity (x : D) :
    (1+2*x)*reval eulerSource x = reval sourceNumerator x := by
  rw [← reval_linear_mul eulerSource_restricted,eulerSource_identity]

lemma eulerSource_red_coeff (n : ℕ) :
    red (coeff n eulerSource)=if n=0 then 1 else 0 := by
  have hN : PowerSeries.map red sourceNumerator=1 := by
    ext n
    simpa only [coeff_map,coeff_one] using sourceNumerator_red_coeff n
  have hI : PowerSeries.map red sourceOddInverse=1 := by
    ext n
    simp only [coeff_map,coeff_sourceOddInverse,map_pow,map_neg,red_two,neg_zero,coeff_one]
    by_cases hn : n=0 <;> simp [hn]
  rw [← coeff_map,eulerSource,map_mul,hN,hI,mul_one,coeff_one]

/-- A complete coefficient certificate proves the actual source value is odd everywhere. -/
theorem eulerSource_reval_red (x : D) : red (reval eulerSource x)=1 := by
  have h := reval_residue_polynomial eulerSource_restricted 1 (1:Polynomial (ZMod (2^1)))
    (by
      intro n
      change res (coeff n eulerSource) = (1:Polynomial F₂).coeff n
      rw [res_eq_red, Polynomial.coeff_one]
      exact eulerSource_red_coeff n) x
  simpa [redPow,res_eq_red] using h

theorem eulerSource_reval_ne_zero (x : D) : reval eulerSource x≠0 := by
  intro hx
  have h:=eulerSource_reval_red x
  rw [hx,map_zero] at h
  norm_num at h

end Komorebi.Euler
