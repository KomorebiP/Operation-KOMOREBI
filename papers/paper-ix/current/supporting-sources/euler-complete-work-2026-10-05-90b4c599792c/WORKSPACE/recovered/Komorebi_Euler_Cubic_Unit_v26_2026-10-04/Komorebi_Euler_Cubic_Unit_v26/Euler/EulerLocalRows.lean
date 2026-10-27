module
public import Euler.EulerPointwiseAtlas
@[expose] public section
noncomputable section
namespace Komorebi.Euler

lemma dyadic_two_pow_norm (n : ℕ) : ‖(2:D)^n‖=(2:ℝ)^(-(n:ℤ)) := by
  rw [norm_pow,norm_two,zpow_neg,zpow_natCast]
  simp only [one_div,inv_pow]

/-- On a root-free skeleton ball the Euler error has its exact lower-packet order. -/
theorem signedEuler_error_below_skeleton (r N i : ℕ) (hr : 0 < r) (hN : r≤N)
    (hi : i < residualTerminalIndex r)
    (hd : terminalWallDistance r < skeletonContent (residualTerminalIndex r) i)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1)
    (hx : ((N-r:ℕ):D)∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i)) :
    ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
      (2:ℝ)^(-(4*(r:ℤ)-1+terminalLowerMinimum (residualTerminalIndex r)))*
      ‖(N.choose r:ℚ_[2])‖ := by
  rw [signedEuler_error_normalized_norm r N hr hN,
    eulerWall_subthreshold_norm r i hr hi hd hv _ hx,dyadic_two_pow_norm,
    residualCarryMinimum_eq_lower_sub_distance r hr (by omega)]
  have he : (2:ℝ)^(-(4*(r:ℤ)-1+
      (terminalLowerMinimum (residualTerminalIndex r)-(terminalWallDistance r:ℤ))))*
      (2:ℝ)^(-(terminalWallDistance r:ℤ))=
      (2:ℝ)^(-(4*(r:ℤ)-1+terminalLowerMinimum (residualTerminalIndex r))) := by
    rw [← zpow_add₀ (by norm_num : (2:ℝ)≠0)]
    congr 1
    ring
  calc
    _= ((2:ℝ)^(-(4*(r:ℤ)-1+
      (terminalLowerMinimum (residualTerminalIndex r)-(terminalWallDistance r:ℤ))))*
      (2:ℝ)^(-(terminalWallDistance r:ℤ)))*‖(N.choose r:ℚ_[2])‖ := by ring
    _=_ := by rw [he]

/-- Exact original Euler-row error, with a constructed local simple root. -/
theorem signedEuler_error_on_skeleton_root (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1)
    (i : ActiveSkeleton r) (N : ℕ) (hN : r≤N)
    (hx : ((N-r:ℕ):D)∈dyadicBall (i.val.val:D)
      (skeletonDepth (residualTerminalIndex r) i.val.val)) :
    ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
      (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r+
        (skeletonSlope (residualTerminalIndex r) i.val.val:ℤ)))*
      ‖(N.choose r:ℚ_[2])‖*
      ‖((N-r:ℕ):D)-skeletonSelectedRoot r hr hv i‖ := by
  have hloc:=(skeletonSelectedRoot_spec r hr hv i).2.2.2.2 _ hx
  rw [signedEuler_error_normalized_norm r N hr hN,hloc,dyadic_two_pow_norm]
  have he : (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r))*
      (2:ℝ)^(-(skeletonSlope (residualTerminalIndex r) i.val.val:ℤ))=
      (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r+
        (skeletonSlope (residualTerminalIndex r) i.val.val:ℤ))) := by
    rw [← zpow_add₀ (by norm_num : (2:ℝ)≠0)]
    congr 1
    ring
  calc
    _= ((2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r))*
      (2:ℝ)^(-(skeletonSlope (residualTerminalIndex r) i.val.val:ℤ)))*
      ‖(N.choose r:ℚ_[2])‖*‖((N-r:ℕ):D)-skeletonSelectedRoot r hr hv i‖ := by ring
    _=_ := by rw [he]

/-- Original row equality on a certified root ball means equality to its unique dyadic root. -/
theorem signedEuler_row_exact_iff_skeleton_root (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1)
    (i : ActiveSkeleton r) (N : ℕ) (hN : r≤N)
    (hx : ((N-r:ℕ):D)∈dyadicBall (i.val.val:D)
      (skeletonDepth (residualTerminalIndex r) i.val.val)) :
    signedEulerEven N=reconstructionTrunc (r-1) N ↔
      ((N-r:ℕ):D)=skeletonSelectedRoot r hr hv i := by
  rw [signedEuler_error_zero_iff_normalized r N hr hN]
  exact (skeletonSelectedRoot_spec r hr hv i).2.2.2.1 _ hx

/-- All-distance root count with only arithmetic lower-cost hypotheses. -/
theorem eulerCarry_unit_root_count (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (he : terminalLowerMinimum (residualTerminalIndex r)=0)
    (h1 : terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r)) :
    Nat.card (EulerResidualRoots r hr)=
      Fintype.card {i:Fin (residualTerminalIndex r) //
        skeletonContent (residualTerminalIndex r) i.val≤terminalWallDistance r} :=
  eulerPointwise_root_count r hr hj
    ((terminalLowerSeries_pointwise_unit_iff r hr hj).mpr ⟨he,h1⟩)

end Komorebi.Euler
