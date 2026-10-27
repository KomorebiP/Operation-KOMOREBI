module
public import Euler.TerminalSlope
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- A finite arithmetic witness identifies the ACTUAL globally last minimum. -/
theorem residualTerminalIndex_eq_of_finite_witness (r j : ℕ) (hr : 0<r)
    (hmin : ∀q∈residualCarryRange r, residualCarryCost r j≤residualCarryCost r q)
    (hlast : ∀q∈residualCarryRange r, residualCarryCost r q=residualCarryCost r j → q≤j) :
    residualTerminalIndex r=j := by
  obtain ⟨q,hq,he⟩ := residualCarryMinimum_attained r
  have ha := hmin q hq
  have hb := residualCarryMinimum_le r j hr
  have hm : residualCarryCost r j=residualCarryMinimum r := by omega
  have hjmem := (mem_residualMinimizers_iff r j hr).mpr hm
  have hle := Finset.le_max' (residualMinimizers r) j hjmem
  change j≤residualTerminalIndex r at hle
  have hc := (Finset.mem_filter.mp (residualTerminalIndex_mem r)).1
  have ht := hlast (residualTerminalIndex r) hc
    ((residualTerminalIndex_cost r).trans hm.symm)
  omega

lemma terminalUpperSeries_reval_ne_zero (r : ℕ) (hr : 0<r) (x : D) :
    reval (terminalUpperSeries r hr) x≠0 := by
  intro hz
  have h := terminalUpperSeries_norm r hr x
  rw [hz,norm_zero] at h
  norm_num at h

lemma eulerNormalizedResidual_equality_norm (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r) (hd : terminalWallDistance r=0)
    (he : terminalLowerMinimum (residualTerminalIndex r)=0)
    (h1 : terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r))
    (x : D) : ‖reval (eulerNormalizedResidual r hr) x‖=1 := by
  have h := eulerNormalizedResidual_equality_unit r hr hj hd he h1 x
  apply res_nonzero_norm_one
  rw [res_eq_red,h]
  decide

/-- An exact all-row law at a pointwise-unit equality wall. -/
theorem signedEuler_error_equality_wall_norm (r N : ℕ) (hr : 0<r) (hN : r≤N)
    (hj : 2≤residualTerminalIndex r) (hd : terminalWallDistance r=0)
    (he : terminalLowerMinimum (residualTerminalIndex r)=0)
    (h1 : terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r)) :
    ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
      (2:ℝ)^(-(4*(r:ℤ)-1))*‖(N.choose r:ℚ_[2])‖ := by
  have hm : residualCarryMinimum r=0 := by
    rw [residualCarryMinimum_eq_lower_sub_distance r hr (by omega),he,hd]
    simp
  rw [signedEuler_error_normalized_norm r N hr hN,
    eulerNormalizedResidual_equality_norm r hr hj hd he h1,hm,add_zero,mul_one]

/-- A small actual multi-packet equality wall, checked from the finite carry costs. -/
theorem residualTerminalIndex_254 : residualTerminalIndex 254=2 := by
  apply residualTerminalIndex_eq_of_finite_witness 254 2 (by decide)
  · change ∀q∈Finset.range 3, residualCarryCost 254 2≤residualCarryCost 254 q
    decide +kernel
  · change ∀q∈Finset.range 3, residualCarryCost 254 q=residualCarryCost 254 2 → q≤2
    decide +kernel

lemma terminalTwo_regular : TerminalRegular 2 := by
  intro q hq hq2
  have : q=1 := by omega
  subst q
  decide +kernel

lemma terminalWallDistance_254 : terminalWallDistance 254=0 := by
  have he : terminalWallExponent 254=8 := by
    rw [terminalWallExponent,residualTerminalIndex_254]
    decide +kernel
  rw [terminalWallDistance,he,residualTerminalIndex_254,terminalWallOrigin,
    terminalLowerMinimum_regular 2 (by decide) terminalTwo_regular]
  decide +kernel

/-- End-to-end Euler error at r=254, for EVERY original row beyond the cutoff. -/
theorem signedEuler_error_254 (N : ℕ) (hN : 254≤N) :
    ‖signedEulerEven N-reconstructionTrunc 253 N‖=
      (2:ℝ)^(-(1015:ℤ))*‖(N.choose 254:ℚ_[2])‖ := by
  have he : terminalLowerMinimum (residualTerminalIndex 254)=0 := by
    rw [residualTerminalIndex_254]
    exact terminalLowerMinimum_regular 2 (by decide) terminalTwo_regular
  have hc : terminalLowerCost (residualTerminalIndex 254) 1≠
      terminalLowerMinimum (residualTerminalIndex 254) := by
    rw [he,residualTerminalIndex_254]
    decide +kernel
  simpa only [Nat.cast_ofNat, show (254:ℕ)-1=253 by decide,
    show 4*(254:ℤ)-1=1015 by decide] using
    signedEuler_error_equality_wall_norm 254 N (by decide) hN
      (by rw [residualTerminalIndex_254]) terminalWallDistance_254 he hc

end Komorebi.Euler
