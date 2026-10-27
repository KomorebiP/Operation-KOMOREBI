module
public import Euler.SkeletonLocalPolynomial
public import Euler.LocalAnalyticTools
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Local upper unit constructed from the actual finite skeleton and a convergent translate. -/
def skeletonLocalSeries (j i : ℕ) (U : Series) : Series :=
  (skeletonLocalUnit j i (skeletonDepth j i):Series)*
    restrictedAffine U ((i:D)-(j:D)) ((2:D)^(skeletonDepth j i))

lemma skeleton_scale_norm_lt_one (j i : ℕ) :
    ‖(2:D)^(skeletonDepth j i)‖<1 := by
  rw [norm_pow,norm_two]
  exact pow_lt_one₀ (by norm_num) (by norm_num) (by
    have := skeletonDepth_pos j i;omega)

lemma skeleton_scale_red (j i : ℕ) : red ((2:D)^(skeletonDepth j i))=0 := by
  simp [show skeletonDepth j i≠0 by have := skeletonDepth_pos j i;omega]

lemma skeletonLocalSeries_restricted (j i : ℕ) (U : Series) :
    Restricted (skeletonLocalSeries j i U) :=
  PowerSeries.isRestricted.mul 1 (polynomial_restricted _)
    (restrictedAffine_restricted U _ _ (skeleton_scale_norm_lt_one j i))

lemma skeletonLocalSeries_red (j i : ℕ) {U : Series} (hU : Restricted U)
    (hred : PowerSeries.map red U=1) :
    PowerSeries.map red (skeletonLocalSeries j i U)=1 := by
  have hq : PowerSeries.map red
      (skeletonLocalUnit j i (skeletonDepth j i):Series)=1 := by
    have hh := skeletonLocalUnit_red j i (skeletonDepth j i)
      (skeletonDepth_bounds j i).1 (skeletonDepth_bounds j i).2
    ext n
    have hc := congrArg (fun p:Polynomial F₂ => p.coeff n) hh
    simpa only [coeff_map,Polynomial.coeff_coe,Polynomial.coeff_map,coeff_one,Polynomial.coeff_one] using hc
  have hu : red (reval U ((i:D)-(j:D)))=1 := by
    have he := reval_residue_polynomial hU 1 (1:Polynomial F₂) (by
      intro n
      rw [res_eq_red,← coeff_map,hred]
      simp only [coeff_one,Polynomial.coeff_one]) ((i:D)-(j:D))
    change res (reval U ((i:D)-(j:D)))=(1:Polynomial F₂).eval _ at he
    simpa only [res_eq_red,Polynomial.eval_one] using he
  rw [skeletonLocalSeries,map_mul,hq,one_mul,
    restrictedAffine_map_red U _ _ (skeleton_scale_red j i),hu,map_one]

/-- Exact separated-skeleton factorization with the complete analytic upper factor. -/
theorem skeletonLocalSeries_factorization (j i : ℕ) (hi : i < j)
    {U : Series} (hU : Restricted U) (y : D) :
    (eulerPacket j).eval ((i:D)+(2:D)^(skeletonDepth j i)*y)*
      reval U ((i:D)+(2:D)^(skeletonDepth j i)*y-(j:D))=
    (2:D)^(skeletonContent j i)*y*reval (skeletonLocalSeries j i U) y := by
  rw [eulerPacket_canonical_factorization j i hi,skeletonLocalSeries,
    reval_mul (polynomial_restricted _) (restrictedAffine_restricted U _ _
      (skeleton_scale_norm_lt_one j i)),reval_polynomial,restrictedAffine_reval hU]
  rw [show (i:D)+(2:D)^(skeletonDepth j i)*y-(j:D)=
    ((i:D)-(j:D))+(2:D)^(skeletonDepth j i)*y by ring]
  ring

/-- Both normalized wall charts retain the actual translated lower series. -/
def skeletonBeforeSeries (j i δ : ℕ) (U V : Series) : Series :=
  C ((2:D)^(skeletonContent j i-δ))*X*skeletonLocalSeries j i U+
    restrictedAffine V (i:D) ((2:D)^(skeletonDepth j i))

def skeletonAfterSeries (j i δ : ℕ) (U V : Series) : Series :=
  X*skeletonLocalSeries j i U+C ((2:D)^(δ-skeletonContent j i))*
    restrictedAffine V (i:D) ((2:D)^(skeletonDepth j i))

lemma skeletonBeforeSeries_restricted (j i δ : ℕ) (U V : Series) :
    Restricted (skeletonBeforeSeries j i δ U V) := by
  unfold skeletonBeforeSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
        (by simpa using polynomial_restricted (Polynomial.X:Polynomial D)))
      (skeletonLocalSeries_restricted j i U))
    (restrictedAffine_restricted V _ _ (skeleton_scale_norm_lt_one j i))

lemma skeletonAfterSeries_restricted (j i δ : ℕ) (U V : Series) :
    Restricted (skeletonAfterSeries j i δ U V) := by
  unfold skeletonAfterSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1
      (by simpa using polynomial_restricted (Polynomial.X:Polynomial D))
      (skeletonLocalSeries_restricted j i U))
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
      (restrictedAffine_restricted V _ _ (skeleton_scale_norm_lt_one j i)))

lemma skeletonBeforeSeries_red (j i δ : ℕ) (U V : Series)
    (hδ : δ<skeletonContent j i) (hV : red (reval V (i:D))=1) :
    PowerSeries.map red (skeletonBeforeSeries j i δ U V)=1 := by
  rw [skeletonBeforeSeries,map_add,map_mul,map_mul,map_C,map_pow,
    red_two,zero_pow (by omega : skeletonContent j i-δ≠0),map_zero,zero_mul,zero_mul,zero_add,
    restrictedAffine_map_red V _ _ (skeleton_scale_red j i),hV,map_one]

lemma skeletonAfterSeries_red (j i δ : ℕ) (hδ : skeletonContent j i≤δ) {U V : Series}
    (hU : Restricted U) (hUr : PowerSeries.map red U=1)
    (hV : red (reval V (i:D))=1) :
    PowerSeries.map red (skeletonAfterSeries j i δ U V)=
      X+C (if δ=skeletonContent j i then 1 else 0) := by
  rw [skeletonAfterSeries,map_add,map_mul,map_X,skeletonLocalSeries_red j i hU hUr,
    mul_one,map_mul,map_C,map_pow,red_two,
    restrictedAffine_map_red V _ _ (skeleton_scale_red j i),hV,map_one,mul_one]
  by_cases he : δ=skeletonContent j i
  · simp [he]
  · have hn : δ-skeletonContent j i≠0 := by omega
    simp [he,hn]

end Komorebi.Euler
