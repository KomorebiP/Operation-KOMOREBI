module
public import Euler.EulerLocalRows
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

lemma skeletonTwo_data (i : ℕ) (hi : i < 2) :
    skeletonDepth 2 i=1 ∧ skeletonSlope 2 i=0 ∧ skeletonContent 2 i=1 := by
  interval_cases i <;> decide +kernel

lemma terminalTwo_lower_odd (r : ℕ) (hr : 0 < r) (hj : residualTerminalIndex r=2)
    (x : D) : red (reval (terminalLowerSeries r hr) x)=1 := by
  have he : terminalLowerMinimum (residualTerminalIndex r)=0 := by
    rw [hj]
    exact terminalLowerMinimum_regular 2 (by decide) terminalTwo_regular
  apply (terminalLowerSeries_pointwise_unit_iff r hr (by omega)).mpr ⟨he,?_⟩ x
  rw [he,hj]
  decide +kernel

/-- The complete actual terminal-two family, at every wall distance. -/
theorem eulerTerminalTwo_root_count (r : ℕ) (hr : 0 < r) (hj : residualTerminalIndex r=2) :
    Nat.card (EulerResidualRoots r hr)=if terminalWallDistance r=0 then 0 else 2 := by
  rw [eulerPointwise_root_count r hr (by omega) (terminalTwo_lower_odd r hr hj),hj]
  have hp : ∀ i:Fin 2, skeletonContent 2 i.val=1 := by
    intro i
    exact (skeletonTwo_data i.val i.isLt).2.2
  simp_rw [hp]
  by_cases hd : terminalWallDistance r=0
  · simp [hd]
  · have h : 1≤terminalWallDistance r := by omega
    simp [h,hd]

theorem eulerTerminalTwo_no_critical (r : ℕ) (hr : 0 < r) (hj : residualTerminalIndex r=2)
    (x : D) (hx : reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 :=
  eulerPointwise_no_critical r hr (by omega) (terminalTwo_lower_odd r hr hj) x hx

/-- Actual finite carry data, checked from the independently defined arithmetic. -/
lemma residualTerminalIndex_510 : residualTerminalIndex 510=2 := by
  apply residualTerminalIndex_eq_of_finite_witness 510 2 (by decide)
  · change ∀q∈Finset.range 3, residualCarryCost 510 2≤residualCarryCost 510 q
    decide +kernel
  · change ∀q∈Finset.range 3, residualCarryCost 510 q=residualCarryCost 510 2 → q≤2
    decide +kernel

lemma terminalWallDistance_510 : terminalWallDistance 510=1 := by
  have he : terminalWallExponent 510=9 := by
    rw [terminalWallExponent,residualTerminalIndex_510]
    decide +kernel
  rw [terminalWallDistance,he,residualTerminalIndex_510,terminalWallOrigin,
    terminalLowerMinimum_regular 2 (by decide) terminalTwo_regular]
  decide +kernel

lemma residualCarryMinimum_510 : residualCarryMinimum 510= -1 := by
  rw [residualCarryMinimum_eq_lower_sub_distance 510 (by decide)
    (by rw [residualTerminalIndex_510];decide),residualTerminalIndex_510,
    terminalWallDistance_510,terminalLowerMinimum_regular 2 (by decide) terminalTwo_regular]
  norm_num

/-- Exactly two simple roots of an ACTUAL Euler residual, not a synthetic coefficient model. -/
theorem eulerResidual510_root_count :
    Nat.card (EulerResidualRoots 510 (by decide))=2 := by
  rw [eulerTerminalTwo_root_count 510 (by decide) residualTerminalIndex_510,terminalWallDistance_510]
  decide +kernel

lemma eulerResidual510_root_simple (x : D)
    (hx : reval (eulerNormalizedResidual 510 (by decide)) x=0) :
    deriv (qeval (eulerNormalizedResidual 510 (by decide))) (x:ℚ_[2])≠0 :=
  eulerTerminalTwo_no_critical 510 (by decide) residualTerminalIndex_510 x hx

/-- The exact root law on each parity ball, with derivative norm one. -/
theorem eulerResidual510_local (i : ℕ) (hi : i < 2) :
    ∃ α:D, α∈dyadicBall (i:D) 1 ∧
      reval (eulerNormalizedResidual 510 (by decide)) α=0 ∧
      ‖deriv (qeval (eulerNormalizedResidual 510 (by decide))) (α:ℚ_[2])‖=1 ∧
      (∀ x∈dyadicBall (i:D) 1,
        reval (eulerNormalizedResidual 510 (by decide)) x=0 ↔ x=α) ∧
      (∀ x∈dyadicBall (i:D) 1,
        ‖reval (eulerNormalizedResidual 510 (by decide)) x‖=‖x-α‖) := by
  have ht : skeletonContent (residualTerminalIndex 510) i≤terminalWallDistance 510 := by
    rw [residualTerminalIndex_510,terminalWallDistance_510,(skeletonTwo_data i hi).2.2]
  have h:=eulerWall_superthreshold_atlas 510 i (by decide)
    (by rw [residualTerminalIndex_510];exact hi) ht
    (terminalTwo_lower_odd 510 (by decide) residualTerminalIndex_510 (i:D))
  simpa only [residualTerminalIndex_510,(skeletonTwo_data i hi).1,
    (skeletonTwo_data i hi).2.1,pow_zero,norm_one,one_mul] using h

/-- The Euler-number error itself has the exact local root-distance formula for every N. -/
theorem signedEuler_error_510 (i : ℕ) (hi : i < 2) :
    ∃ α:D, α∈dyadicBall (i:D) 1 ∧
      reval (eulerNormalizedResidual 510 (by decide)) α=0 ∧
      ∀ N:ℕ, 510≤N → ((N-510:ℕ):D)∈dyadicBall (i:D) 1 →
        ‖signedEulerEven N-reconstructionTrunc 509 N‖=
          (2:ℝ)^(-(2038:ℤ))*‖(N.choose 510:ℚ_[2])‖*‖((N-510:ℕ):D)-α‖ := by
  obtain ⟨α,ha,hz,_,_,hn⟩:=eulerResidual510_local i hi
  refine ⟨α,ha,hz,?_⟩
  intro N hN hx
  have h:=signedEuler_error_normalized_norm 510 N (by decide) hN
  rw [residualCarryMinimum_510,hn _ hx] at h
  simpa only [Nat.cast_ofNat,show (510:ℕ)-1=509 by decide,
    show 4*(510:ℤ)-1+(-1)=2038 by norm_num] using h

end Komorebi.Euler
