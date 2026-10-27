module
public import Euler.SkeletonLocalSeries
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma skeletonBeforeSeries_reval (j i δ : ℕ) {U V : Series}
    (hV : Restricted V) (y : D) :
    reval (skeletonBeforeSeries j i δ U V) y=
      (2:D)^(skeletonContent j i-δ)*y*reval (skeletonLocalSeries j i U) y+
      reval V ((i:D)+(2:D)^(skeletonDepth j i)*y) := by
  have hX : Restricted ((X:Series)*skeletonLocalSeries j i U) :=
    PowerSeries.isRestricted.mul 1
      (by simpa using polynomial_restricted (Polynomial.X:Polynomial D))
      (skeletonLocalSeries_restricted j i U)
  rw [skeletonBeforeSeries,mul_assoc,
    reval_add (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hX)
      (restrictedAffine_restricted V _ _ (skeleton_scale_norm_lt_one j i)),
    reval_C_mul hX,reval_X_mul (skeletonLocalSeries_restricted j i U),
    restrictedAffine_reval hV]
  ring

lemma skeletonAfterSeries_reval (j i δ : ℕ) {U V : Series}
    (hV : Restricted V) (y : D) :
    reval (skeletonAfterSeries j i δ U V) y=
      y*reval (skeletonLocalSeries j i U) y+
      (2:D)^(δ-skeletonContent j i)*reval V ((i:D)+(2:D)^(skeletonDepth j i)*y) := by
  have hX : Restricted ((X:Series)*skeletonLocalSeries j i U) :=
    PowerSeries.isRestricted.mul 1
      (by simpa using polynomial_restricted (Polynomial.X:Polynomial D))
      (skeletonLocalSeries_restricted j i U)
  rw [skeletonAfterSeries,
    reval_add hX (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
      (restrictedAffine_restricted V _ _ (skeleton_scale_norm_lt_one j i))),
    reval_X_mul (skeletonLocalSeries_restricted j i U),
    reval_C_mul (restrictedAffine_restricted V _ _ (skeleton_scale_norm_lt_one j i)),
    restrictedAffine_reval hV]

/-- Exact local normalization before the separated skeleton becomes visible. -/
theorem skeletonBeforeSeries_normalization (j i δ : ℕ) (hi : i < j)
    (hδ : δ≤skeletonContent j i) {U V : Series}
    (hU : Restricted U) (hV : Restricted V) (y : D) :
    (eulerPacket j).eval ((i:D)+(2:D)^(skeletonDepth j i)*y)*
      reval U ((i:D)+(2:D)^(skeletonDepth j i)*y-(j:D))+
      (2:D)^δ*reval V ((i:D)+(2:D)^(skeletonDepth j i)*y)=
    (2:D)^δ*reval (skeletonBeforeSeries j i δ U V) y := by
  rw [skeletonLocalSeries_factorization j i hi hU,
    skeletonBeforeSeries_reval j i δ hV,mul_add,← mul_assoc,← mul_assoc,
    ← pow_add,Nat.add_sub_of_le hδ]

/-- Exact local normalization at and after the separated skeleton scale. -/
theorem skeletonAfterSeries_normalization (j i δ : ℕ) (hi : i < j)
    (hδ : skeletonContent j i≤δ) {U V : Series}
    (hU : Restricted U) (hV : Restricted V) (y : D) :
    (eulerPacket j).eval ((i:D)+(2:D)^(skeletonDepth j i)*y)*
      reval U ((i:D)+(2:D)^(skeletonDepth j i)*y-(j:D))+
      (2:D)^δ*reval V ((i:D)+(2:D)^(skeletonDepth j i)*y)=
    (2:D)^(skeletonContent j i)*reval (skeletonAfterSeries j i δ U V) y := by
  rw [skeletonLocalSeries_factorization j i hi hU,
    skeletonAfterSeries_reval j i δ hV,mul_add,← mul_assoc,← mul_assoc,
    ← pow_add,Nat.add_sub_of_le hδ]

/-- Differentiating a proved local analytic normalization retains the chart scale. -/
theorem restricted_chart_derivative {g f : Series} (hg : Restricted g) (hf : Restricted f)
    (a s c : D) (hs : ‖s‖<1)
    (he : ∀ y:D, reval g (a+s*y)=c*reval f y) (y : D) :
    deriv (qeval g) ((a+s*y:D):ℚ_[2])*(s:ℚ_[2])=
      (c:ℚ_[2])*deriv (qeval f) (y:ℚ_[2]) := by
  have hEq : qeval (restrictedAffine g a s)=ᶠ[𝓝 (y:ℚ_[2])]
      (fun z:ℚ_[2] => (c:ℚ_[2])*qeval f z) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro z
    rw [← coe_reval (restrictedAffine_restricted g a s hs),restrictedAffine_reval hg,
      he,PadicInt.coe_mul,coe_reval hf]
  have hd := ((hasDerivAt_qeval hf y).differentiableAt.hasDerivAt).const_mul (c:ℚ_[2])
  have he' := (hd.congr_of_eventuallyEq hEq).deriv
  rw [restrictedAffine_deriv hg a s y hs] at he'
  exact he'

end Komorebi.Euler
