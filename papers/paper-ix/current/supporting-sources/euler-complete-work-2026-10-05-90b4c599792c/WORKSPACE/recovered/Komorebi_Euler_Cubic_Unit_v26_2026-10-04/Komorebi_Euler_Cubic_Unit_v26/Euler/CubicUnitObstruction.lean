module
public import Euler.CubicCriticalValues
public import Euler.ThirdOrderRemainder
@[expose] public section
noncomputable section
set_option maxHeartbeats 1200000
namespace Komorebi.Euler
open PowerSeries

lemma rjet_two_hasse_one {f:Series} (hf:Restricted f) (x:D) :
    rjet 2 (hasseSeries 1 f) x=3*rjet 3 f x := by
  have he : hasseSeries 2 (hasseSeries 1 f)=C (3:D)*hasseSeries 3 f := by
    ext n
    simp only [coeff_hasseSeries,coeff_C_mul,Nat.choose_one_right]
    have hb : (n+3)*Nat.choose (n+2) 2=Nat.choose (n+3) 3*3 := by
      simpa only [Nat.add_assoc] using Nat.add_one_mul_choose_eq (n+2) 2
    have hd : (n+3:D)*(Nat.choose (n+2) 2:D)=(Nat.choose (n+3) 3:D)*3 := by
      exact_mod_cast hb
    rw [show n+2+1=n+3 by omega]
    push_cast
    calc
      _ = ((n+3:D)*(Nat.choose (n+2) 2:D))*coeff (n+3) f := by ring
      _ = ((Nat.choose (n+3) 3:D)*3)*coeff (n+3) f := by rw [hd]
      _ = _ := by ring
  unfold rjet
  rw [he,reval_C_mul (restricted_hasseSeries hf 3)]

lemma cubicCore_rjet_three (a b c u:D) {R:Series} (hR:Restricted R) (x:D) :
    rjet 3 (cubicCoreSeries a b c u R) x=u+4*rjet 3 ((X:Series)^4*R) x := by
  let p:Polynomial D:=Polynomial.C a+Polynomial.C b*Polynomial.X+
    Polynomial.C c*Polynomial.X^2+Polynomial.C u*Polynomial.X^3
  have he : cubicCoreSeries a b c u R=(p:Series)+C (4:D)*((X:Series)^4*R) := by
    simp only [p,cubicCoreSeries,Polynomial.coe_add,Polynomial.coe_mul,
      Polynomial.coe_C,Polynomial.coe_X,Polynomial.coe_pow,mul_assoc]
  rw [he,rjet_add_value 3 (polynomial_restricted p)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (cubicTail_restricted hR)),
    rjet_polynomial_order,rjet_C_mul (cubicTail_restricted hR)]
  have hp : Polynomial.hasseDeriv 3 p=Polynomial.C u := by
    ext n
    cases n with
    | zero => norm_num [p,Polynomial.hasseDeriv_coeff,Nat.choose]
    | succ n => simp [p,Polynomial.hasseDeriv_coeff]
  rw [hp];simp

/-- This is an inflection-centered jet obstruction, NOT the exact discriminant
of a Weierstrass polynomial. The infinite tail is accounted for below. -/
def cubicJetDiscriminant (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R) : D :=
  let F:=cubicCoreSeries a b c (u:D) R
  let ρ:=cubicInflectionPoint c u R hR
  4*(rjet 1 F ρ)^3+27*rjet 3 F ρ*(reval F ρ)^2

lemma cubicInflection_cubic_unit (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R) :
    ‖rjet 3 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖=1 := by
  apply res_nonzero_norm_one
  rw [cubicCore_rjet_three a b c (u:D) hR]
  simp [res_eq_red,qc_unit_red]

/-- Exact centered critical data with INTEGRAL error coefficients. -/
theorem cubicCritical_integral_data (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R)
    (x:D) (hx:deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0) :
    let F:=cubicCoreSeries a b c (u:D) R
    let ρ:=cubicInflectionPoint c u R hR
    let h:=x-ρ
    let v:=rjet 3 F ρ
    ∃e f:D,
      rjet 1 F ρ = -3*v*h^2-4*h^3*e ∧
      reval F ρ-reval F x = 2*v*h^3+4*h^4*(e-f) := by
  let F:=cubicCoreSeries a b c (u:D) R
  let ρ:=cubicInflectionPoint c u R hR
  let h:=x-ρ
  let T:Series:=(X:Series)^4*R
  have hT:Restricted T:=cubicTail_restricted hR
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
  have hc:=cubicInflection_rjet_two a b c u R hR
  rw [cubicCore_rjet_two a b c (u:D) hR] at hc
  change c+3*(u:D)*ρ+4*rjet 2 T ρ=0 at hc
  rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero,
    cubicCore_rjet_one a b c (u:D) hR] at hx
  change b+2*c*x+3*(u:D)*x^2+4*rjet 1 T x=0 at hx
  change ∃e f:D,rjet 1 F ρ = -3*rjet 3 F ρ*h^2-4*h^3*e ∧
    reval F ρ-reval F x = 2*rjet 3 F ρ*h^3+4*h^4*(e-f)
  refine ⟨e,f,?_,?_⟩
  · dsimp only [F]
    rw [cubicCore_rjet_one a b c (u:D) hR,cubicCore_rjet_three a b c (u:D) hR]
    change b+2*c*ρ+3*(u:D)*ρ^2+4*rjet 1 T ρ = _
    dsimp only [e1,h] at he ⊢
    linear_combination hx-2*(x-ρ)*hc-4*he
  · dsimp only [F]
    rw [cubicCore_reval a b c (u:D) hR,cubicCore_reval a b c (u:D) hR,
      cubicCore_rjet_three a b c (u:D) hR]
    change (a+b*ρ+c*ρ^2+(u:D)*ρ^3+4*reval T ρ)-
      (a+b*x+c*x^2+(u:D)*x^3+4*reval T x)=_
    dsimp only [e1,e2,h] at he hf ⊢
    linear_combination -(x-ρ)*hx+(x-ρ)^2*hc+4*(x-ρ)*he-4*hf

/-- Exact algebraic cancellation underlying the unit-sensitive cubic test. -/
lemma cubic_discriminant_error_factor (v h e f:D) :
    4*(-3*v*h^2-4*h^3*e)^3+27*v*(2*v*h^3+4*h^4*(e-f))^2 =
    16*h^7*(-27*v^2*f+9*v*h*(3*(e-f)^2-4*e^2)-16*h^2*e^3) := by ring

/-- At an ACTUAL critical zero the centered discriminant is forced into a
strictly deeper ideal. This includes all infinite-tail effects. -/
theorem cubicCritical_discriminant_divisible (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])) :
    ∃z:D,cubicJetDiscriminant a b c u R hR =
      16*(x-cubicInflectionPoint c u R hR)^7*z := by
  obtain ⟨e,f,hA,hC⟩:=cubicCritical_integral_data a b c u R hR x hx.2
  have hz:reval (cubicCoreSeries a b c (u:D) R) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    simpa only [coe_reval (cubicCore_restricted a b c (u:D) hR)] using hx.1
  simp only [hz,sub_zero] at hC
  dsimp only [cubicJetDiscriminant]
  rw [hA,hC,cubic_discriminant_error_factor]
  exact ⟨_,rfl⟩

/-- A squared-norm obstruction has no square-root or nonzero-value conventions. -/
theorem cubicCritical_discriminant_bound (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])) :
    ‖cubicJetDiscriminant a b c u R hR‖^2 ≤
      (1/256:ℝ)*‖rjet 1 (cubicCoreSeries a b c (u:D) R)
        (cubicInflectionPoint c u R hR)‖^7 := by
  obtain ⟨z,hz⟩:=cubicCritical_discriminant_divisible a b c u R hR x hx
  have hs:=cubicCritical_slope_radius a b c u R hR x hx.2
  rw [hz,hs]
  have h16:‖(16:D)‖=(1/16:ℝ) := by
    rw [show (16:D)=4^2 by norm_num,norm_pow,qc_norm_four];norm_num
  have hn:‖16*(x-cubicInflectionPoint c u R hR)^7*z‖≤
      (1/16:ℝ)*‖x-cubicInflectionPoint c u R hR‖^7 := by
    rw [norm_mul,norm_mul,h16,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one z)
  have hh:=pow_le_pow_left₀ (norm_nonneg _) hn 2
  calc
    _ ≤ ((1/16:ℝ)*‖x-cubicInflectionPoint c u R hR‖^7)^2 := hh
    _ = _ := by ring

/-- Unit information in the centered jets can settle the old norm-equality boundary. -/
theorem cubicCore_no_critical_of_discriminant_gap (a b c:D) (u:Dˣ)
    (R:Series) (hR:Restricted R)
    (hgap:(1/256:ℝ)*‖rjet 1 (cubicCoreSeries a b c (u:D) R)
      (cubicInflectionPoint c u R hR)‖^7 < ‖cubicJetDiscriminant a b c u R hR‖^2)
    (x:D) : ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2]) := by
  intro hx
  exact (not_lt_of_ge (cubicCritical_discriminant_bound a b c u R hR x hx)) hgap

end Komorebi.Euler
