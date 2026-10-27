module
public import Euler.EulerSlopeExamples
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- A proved exact integral chart preserves critical zeros, including both nonzero scales. -/
theorem restricted_scaled_critical_iff {g f:Series} (hg:Restricted g) (hf:Restricted f)
    (a:D) (k c:ℕ) (hk:0<k)
    (he:∀y:D,reval g (dyadicChart a k y)=(2:D)^c*reval f y) (y:D) :
    (reval g (dyadicChart a k y)=0 ∧
      deriv (qeval g) ((dyadicChart a k y:D):ℚ_[2])=0) ↔
    (reval f y=0 ∧ deriv (qeval f) (y:ℚ_[2])=0) := by
  have hs:‖(2:D)^k‖<1 := by
    rw [norm_pow,norm_two]
    exact pow_lt_one₀ (by norm_num) (by norm_num) (by omega)
  have hd:=restricted_chart_derivative hg hf a ((2:D)^k) ((2:D)^c) hs he y
  have hn:(2:D)^c≠0:=pow_ne_zero _ two_ne_zero
  have hnk:((2:D)^k:ℚ_[2])≠0:=PadicInt.coe_ne_zero.mpr (pow_ne_zero _ two_ne_zero)
  have hnc:((2:D)^c:ℚ_[2])≠0:=PadicInt.coe_ne_zero.mpr hn
  rw [he,mul_eq_zero]
  simp only [hn,false_or]
  constructor
  · rintro ⟨h0,h1⟩
    refine ⟨h0,?_⟩
    change deriv (qeval g) ((dyadicChart a k y:D):ℚ_[2])*_= _ at hd
    rw [h1,zero_mul] at hd
    exact (mul_eq_zero.mp hd.symm).resolve_left hnc
  · rintro ⟨h0,h1⟩
    refine ⟨h0,?_⟩
    rw [h1,mul_zero] at hd
    exact (mul_eq_zero.mp hd).resolve_right hnk

/-- The unresolved even collision now has an exact analytic core and critical-zero equivalence. -/
theorem eulerSlope_equal_critical_core (r i:ℕ) (hr:0<r)
    (hi:i<residualTerminalIndex r) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven:red w=0) :
    ∃F:Series, Restricted F ∧
      (∀y:D, reval (eulerNormalizedResidual r hr)
        (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
        (2:D)^(skeletonContent (residualTerminalIndex r) i+1)*reval F y) ∧
      (∀y:D,
        (reval (eulerNormalizedResidual r hr)
          (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=0 ∧
         deriv (qeval (eulerNormalizedResidual r hr))
          ((dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y:D):ℚ_[2])=0) ↔
        (reval F y=0 ∧ deriv (qeval F) (y:ℚ_[2])=0)) := by
  obtain ⟨F,hF,_,hval⟩:=eulerSlope_equal_even_core r i hr hi w hw hjet hd heven
  exact ⟨F,hF,hval,fun y => restricted_scaled_critical_iff
    (eulerNormalizedResidual_restricted r hr) hF (i:D)
    (skeletonDepth (residualTerminalIndex r) i) (skeletonContent (residualTerminalIndex r) i+1)
    (skeletonDepth_pos _ _) hval y⟩

/-- Any constructed actual local atlas gives the original independent Euler error law. -/
theorem signedEuler_error_of_simpleBall (r:ℕ) (hr:0<r) (a:D) (k d:ℕ)
    (ha:SimpleBallAtlas (eulerNormalizedResidual r hr) a k d) :
    ∃α:D, α∈dyadicBall a k ∧ reval (eulerNormalizedResidual r hr) α=0 ∧
      ∀N:ℕ, r≤N → ((N-r:ℕ):D)∈dyadicBall a k →
        ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
          (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r+(d:ℤ)))*
          ‖(N.choose r:ℚ_[2])‖*‖((N-r:ℕ):D)-α‖ := by
  obtain ⟨α,hb,hz,_,_,hn⟩:=ha
  refine ⟨α,hb,hz,?_⟩
  intro N hN hx
  rw [signedEuler_error_normalized_norm r N hr hN,hn _ hx,dyadic_two_pow_norm]
  have he:(2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r))*(2:ℝ)^(-(d:ℤ))=
      (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r+(d:ℤ))) := by
    rw [←zpow_add₀ (by norm_num : (2:ℝ)≠0)]
    congr 1
    ring
  calc
    _=((2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r))*(2:ℝ)^(-(d:ℤ)))*
        ‖(N.choose r:ℚ_[2])‖*‖((N-r:ℕ):D)-α‖ := by ring
    _=_ := by rw [he]

/-- End-to-end slope-controlled error for every nonresonant lower-root ball. -/
theorem signedEuler_error_nonresonant_slope (r i:ℕ) (hr:0<r)
    (hi:i<residualTerminalIndex r) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r≠skeletonSlope (residualTerminalIndex r) i) :
    ∃α:D, α∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) ∧
      reval (eulerNormalizedResidual r hr) α=0 ∧
      ∀N:ℕ, r≤N → ((N-r:ℕ):D)∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) →
        ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
          (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r+
            ((min (terminalWallDistance r) (skeletonSlope (residualTerminalIndex r) i):ℕ):ℤ)))*
          ‖(N.choose r:ℚ_[2])‖*‖((N-r:ℕ):D)-α‖ := by
  exact signedEuler_error_of_simpleBall r hr (i:D)
    (skeletonDepth (residualTerminalIndex r) i)
    (min (terminalWallDistance r) (skeletonSlope (residualTerminalIndex r) i))
    (eulerSlope_nonresonant_atlas r i hr hi w hw hjet hd)

end Komorebi.Euler
