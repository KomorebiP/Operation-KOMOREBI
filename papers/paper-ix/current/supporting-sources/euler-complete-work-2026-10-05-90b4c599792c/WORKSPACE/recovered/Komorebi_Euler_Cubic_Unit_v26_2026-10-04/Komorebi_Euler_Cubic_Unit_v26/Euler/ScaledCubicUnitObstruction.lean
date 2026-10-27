module
public import Euler.CubicUnitObstruction
@[expose] public section
noncomputable section
set_option maxHeartbeats 1200000
namespace Komorebi.Euler
open PowerSeries

/-- The original tail scale is retained instead of absorbed into an arbitrary unit bound. -/
theorem cubicCritical_scaled_integral_data (a b c:D) (u:Dˣ) (s:D) (R:Series) (hR:Restricted R)
    (x:D) (hx:deriv (qeval (cubicCoreSeries a b c (u:D) (C s*R))) (x:ℚ_[2])=0) :
    let F:=cubicCoreSeries a b c (u:D) (C s*R)
    let ρ:=cubicInflectionPoint c u (C s*R) (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
    let h:=x-ρ
    let v:=rjet 3 F ρ
    ∃e f:D,
      rjet 1 F ρ = -3*v*h^2-4*s*h^3*e ∧
      reval F ρ-reval F x = 2*v*h^3+4*s*h^4*(e-f) := by
  let F:=cubicCoreSeries a b c (u:D) (C s*R)
  let ρ:=cubicInflectionPoint c u (C s*R) (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
  let h:=x-ρ
  let T:Series:=(X:Series)^4*R
  have hT:Restricted T:=cubicTail_restricted hR
  have hRs:Restricted (C s*R):=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR
  have heT:(X:Series)^4*(C s*R)=C s*T := by dsimp only [T];ring
  let e1:=rjet 1 T x-rjet 1 T ρ-h*(2*rjet 2 T ρ)-h^2*(3*rjet 3 T ρ)
  let e2:=reval T x-reval T ρ-h*rjet 1 T ρ-h^2*rjet 2 T ρ-h^3*rjet 3 T ρ
  have he1:‖e1‖≤‖h^3‖ := by
    have hh:=reval_second_order_error (restricted_hasseSeries hT 1) ρ x
    rw [rjet_one_hasseSeries hT 1 ρ,rjet_two_hasse_one hT ρ] at hh
    norm_num only at hh
    simpa only [e1,h,rjet,norm_pow] using hh
  have he2:‖e2‖≤‖h^4‖ := by
    simpa only [e2,h,norm_pow] using reval_third_order_error hT ρ x
  obtain ⟨e,he⟩:=exists_mul_of_norm_le e1 (h^3) he1
  obtain ⟨f,hf⟩:=exists_mul_of_norm_le e2 (h^4) he2
  have hc:=cubicInflection_rjet_two a b c u (C s*R) hRs
  rw [cubicCore_rjet_two a b c (u:D) hRs,heT,rjet_C_mul hT] at hc
  change c+3*(u:D)*ρ+4*(s*rjet 2 T ρ)=0 at hc
  rw [deriv_qeval (cubicCore_restricted a b c (u:D) hRs),PadicInt.coe_eq_zero,
    cubicCore_rjet_one a b c (u:D) hRs,heT,rjet_C_mul hT] at hx
  change b+2*c*x+3*(u:D)*x^2+4*(s*rjet 1 T x)=0 at hx
  change ∃e f:D,rjet 1 F ρ = -3*rjet 3 F ρ*h^2-4*s*h^3*e ∧
    reval F ρ-reval F x = 2*rjet 3 F ρ*h^3+4*s*h^4*(e-f)
  refine ⟨e,f,?_,?_⟩
  · dsimp only [F]
    rw [cubicCore_rjet_one a b c (u:D) hRs,heT,rjet_C_mul hT,cubicCore_rjet_three a b c (u:D) hRs,heT,rjet_C_mul hT]
    dsimp only [e1,h] at he ⊢
    linear_combination hx-2*(x-ρ)*hc-4*s*he
  · dsimp only [F]
    rw [cubicCore_reval a b c (u:D) hRs,heT,reval_C_mul hT,cubicCore_reval a b c (u:D) hRs,heT,reval_C_mul hT,
      cubicCore_rjet_three a b c (u:D) hRs,heT,rjet_C_mul hT]
    dsimp only [e1,e2,h] at he hf ⊢
    linear_combination -(x-ρ)*hx+(x-ρ)^2*hc+4*s*(x-ρ)*he-4*s*hf

lemma cubic_discriminant_scaled_error_factor (v s h e f:D) :
    4*(-3*v*h^2-4*s*h^3*e)^3+27*v*(2*v*h^3+4*s*h^4*(e-f))^2 =
    16*s*h^7*(-27*v^2*f+9*v*s*h*(3*(e-f)^2-4*e^2)-16*s^2*h^2*e^3) := by ring

/-- Full scale-sensitive divisibility for the ACTUAL infinite function. -/
theorem cubicCritical_scaled_discriminant_divisible (a b c:D) (u:Dˣ) (s:D)
    (R:Series) (hR:Restricted R) (x:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) (C s*R))) (x:ℚ_[2])) :
    let hRs:=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 s) hR
    ∃z:D,cubicJetDiscriminant a b c u (C s*R) hRs =
      16*s*(x-cubicInflectionPoint c u (C s*R) hRs)^7*z := by
  obtain ⟨e,f,hA,hC⟩:=cubicCritical_scaled_integral_data a b c u s R hR x hx.2
  have hRs:Restricted (C s*R):=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR
  have hz:reval (cubicCoreSeries a b c (u:D) (C s*R)) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    simpa only [coe_reval (cubicCore_restricted a b c (u:D) hRs)] using hx.1
  simp only [hz,sub_zero] at hC
  dsimp only [cubicJetDiscriminant]
  rw [hA,hC,cubic_discriminant_scaled_error_factor]
  exact ⟨_,rfl⟩

/-- The squared norm formulation handles A=0, s=0 and zero obstruction without exceptions. -/
theorem cubicCritical_scaled_discriminant_bound (a b c:D) (u:Dˣ) (s:D)
    (R:Series) (hR:Restricted R) (x:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) (C s*R))) (x:ℚ_[2])) :
    let hRs:=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 s) hR
    ‖cubicJetDiscriminant a b c u (C s*R) hRs‖^2 ≤
      (1/256:ℝ)*‖s‖^2*‖rjet 1 (cubicCoreSeries a b c (u:D) (C s*R))
        (cubicInflectionPoint c u (C s*R) hRs)‖^7 := by
  let hRs:=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 s) hR
  obtain ⟨z,hz⟩:=cubicCritical_scaled_discriminant_divisible a b c u s R hR x hx
  have hs:=cubicCritical_slope_radius a b c u (C s*R) hRs x hx.2
  dsimp only
  rw [hz,hs]
  have h16:‖(16:D)‖=(1/16:ℝ) := by
    rw [show (16:D)=4^2 by norm_num,norm_pow,qc_norm_four];norm_num
  have hn:‖16*s*(x-cubicInflectionPoint c u (C s*R) hRs)^7*z‖≤
      (1/16:ℝ)*‖s‖*‖x-cubicInflectionPoint c u (C s*R) hRs‖^7 := by
    simp only [norm_mul,h16,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one z)
  have hh:=pow_le_pow_left₀ (norm_nonneg _) hn 2
  calc
    _ ≤ ((1/16:ℝ)*‖s‖*‖x-cubicInflectionPoint c u (C s*R) hRs‖^7)^2 := hh
    _ = _ := by ring

/-- Retaining the actual tail scale strengthens the critical-value exclusion. -/
theorem cubicCore_no_critical_of_scaled_discriminant_gap (a b c:D) (u:Dˣ)
    (s:D) (R:Series) (hR:Restricted R)
    (hgap:let hRs:=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 s) hR
      (1/256:ℝ)*‖s‖^2*‖rjet 1 (cubicCoreSeries a b c (u:D) (C s*R))
        (cubicInflectionPoint c u (C s*R) hRs)‖^7 <
      ‖cubicJetDiscriminant a b c u (C s*R) hRs‖^2)
    (x:D) : ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) (C s*R))) (x:ℚ_[2]) := by
  intro hx
  exact (not_lt_of_ge (cubicCritical_scaled_discriminant_bound a b c u s R hR x hx)) hgap

end Komorebi.Euler
