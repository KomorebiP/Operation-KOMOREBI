module
public import Euler.TerminalWallMinimum
public import Euler.ResidualSimpleCases
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- Exact cocycle identity for carry costs under a depth shift. -/
lemma residualCarryCost_shift (r a q : ℕ) :
    residualCarryCost (r+a) q=
      residualCarryCost r (a+q)-residualCarryCost r a := by
  unfold residualCarryCost
  rw [Nat.add_assoc,Nat.cast_add]
  ring

/-- Beyond the last minimum, the shifted residual has strictly positive costs. -/
lemma residualCarryCost_terminal_shift_pos (r q : ℕ) (hr : 0<r) (hq : 0<q) :
    0<residualCarryCost (r+residualTerminalIndex r) q := by
  rw [residualCarryCost_shift,residualTerminalIndex_cost]
  exact sub_pos.mpr (residualCarryCost_after_terminal r _ hr (by omega))

/-- Moving to the terminal packet leaves a residual with terminal index zero. -/
theorem residualTerminalIndex_shift_terminal (r : ℕ) (hr : 0<r) :
    residualTerminalIndex (r+residualTerminalIndex r)=0 := by
  by_contra hn
  have hc := residualCarryCost_terminal_shift_pos r
    (residualTerminalIndex (r+residualTerminalIndex r)) hr (by omega)
  rw [residualTerminalIndex_cost] at hc
  have hm := residualCarryMinimum_nonpos (r+residualTerminalIndex r)
  omega

lemma residualCarryMinimum_shift_terminal (r : ℕ) (hr : 0<r) :
    residualCarryMinimum (r+residualTerminalIndex r)=0 :=
  residualCarryMinimum_zero_of_terminal_zero _ (residualTerminalIndex_shift_terminal r hr)

/-- The entire shifted actual series, not just its values, reduces to one. -/
lemma eulerNormalizedResidual_red_of_terminal_zero (r : ℕ) (hr : 0<r)
    (hj : residualTerminalIndex r=0) :
    PowerSeries.map red (eulerNormalizedResidual r hr)=1 := by
  ext n
  rw [coeff_map,coeff_one]
  have h := eulerNormalizedResidual_lastOdd r hr
  rw [hj] at h
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simpa using h.1
  · rw [ite_eq_right (by omega)]
    exact h.2 n hn

lemma terminal_shift_red (r : ℕ) (hr : 0<r) :
    PowerSeries.map red
      (eulerNormalizedResidual (r+residualTerminalIndex r) (by omega))=1 :=
  eulerNormalizedResidual_red_of_terminal_zero _ (by omega)
    (residualTerminalIndex_shift_terminal r hr)

/-- The actual shifted H residual equals its integral G normalization. -/
lemma terminal_shift_H_eq_G (r : ℕ) (hr : 0<r) (x : D) :
    eulerResidual (r+residualTerminalIndex r) (x:ℚ_[2])=
      (reval (eulerNormalizedResidual (r+residualTerminalIndex r) (by omega)) x:ℚ_[2]) := by
  rw [eulerResidual_from_normalized _ (by omega) x,
    residualCarryMinimum_shift_terminal r hr,zpow_zero,one_mul]

/-- The coefficient at the true terminal minimum is an actual odd unit. -/
lemma terminalScalar_red (r : ℕ) (hr : 0<r) :
    red (normalizedResidualScalarInt r hr (residualTerminalIndex r))=1 := by
  simp only [normalizedResidualScalarInt_red,residualTerminalIndex_cost,ite_true]

/-- Constructed analytic upper factor. Its evaluation is used at x-j. -/
def terminalUpperSeries (r : ℕ) (hr : 0<r) : Series :=
  C (normalizedResidualScalarInt r hr (residualTerminalIndex r))*
    eulerNormalizedResidual (r+residualTerminalIndex r) (by omega)

lemma terminalUpperSeries_restricted (r : ℕ) (hr : 0<r) :
    Restricted (terminalUpperSeries r hr) :=
  PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
    (eulerNormalizedResidual_restricted _ (by omega))

lemma terminalUpperSeries_red (r : ℕ) (hr : 0<r) :
    PowerSeries.map red (terminalUpperSeries r hr)=1 := by
  rw [terminalUpperSeries,map_mul,map_C,terminalScalar_red r hr,terminal_shift_red r hr]
  simp

lemma terminalUpperSeries_norm (r : ℕ) (hr : 0<r) (x : D) :
    ‖reval (terminalUpperSeries r hr) x‖=1 := by
  have h := reval_residue_polynomial (terminalUpperSeries_restricted r hr)
    1 (1:Polynomial F₂) (by
      intro n
      rw [res_eq_red,← coeff_map,terminalUpperSeries_red r hr]
      simp only [coeff_one,Polynomial.coeff_one]) x
  have hh : res (reval (terminalUpperSeries r hr) x)=1 := by simpa using h
  exact res_nonzero_norm_one _ (by rw [hh];decide)

end Komorebi.Euler
