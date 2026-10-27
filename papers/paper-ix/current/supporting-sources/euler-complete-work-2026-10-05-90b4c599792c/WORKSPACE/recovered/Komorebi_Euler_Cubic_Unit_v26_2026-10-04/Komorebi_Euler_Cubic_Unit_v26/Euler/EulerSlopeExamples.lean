module
public import Euler.EulerSlopeCandidates
@[expose] public section
noncomputable section
set_option maxHeartbeats 4000000
set_option maxRecDepth 10000
namespace Komorebi.Euler
open PowerSeries

/-- This is the carry-defined lower polynomial, not an assumed Euler certificate. -/
lemma terminalSeventeen_lower_polynomial :
    terminalLowerPolynomial 17=Polynomial.X+1 := by
  have hm:terminalLowerMinimum 17=0 := by decide +kernel
  have hc:∀q∈Finset.range 17, terminalLowerCost 17 q=0 ↔ q=0 ∨ q=1 := by
    decide +kernel
  unfold terminalLowerPolynomial
  rw [hm]
  calc
    _ = ∑ q ∈ Finset.range 17,
        ((if q=0 then (1:Polynomial F₂) else 0)+
        (if q=1 then (Polynomial.X:Polynomial F₂) else 0)) := by
      apply Finset.sum_congr rfl
      intro q hq
      by_cases h0:q=0
      · subst q
        simp
      by_cases h1:q=1
      · subst q
        have h:terminalLowerCost 17 1=0 := by decide +kernel
        simp [h]
      · have hn:terminalLowerCost 17 q≠0 := by
          intro h
          rcases (hc q hq).mp h with h | h
          · exact h0 h
          · exact h1 h
        simp [hn,h0,h1]
    _ = _ := by rw [Finset.sum_add_distrib];simp [add_comm]

lemma terminalSeventeen_lower_simple : LowerResidueSimple 17 := by
  intro e _
  rw [terminalSeventeen_lower_polynomial]
  simp

lemma terminalSeventeen_slope_bounds (i:ℕ) (hi:i<17) :
    11≤skeletonSlope 17 i ∧ skeletonSlope 17 i≤15 := by
  have h : ∀i:Fin 17, 11≤skeletonSlope 17 i.val ∧ skeletonSlope 17 i.val≤15 := by
    decide +kernel
  exact h ⟨i,hi⟩

/-- An entire actual irregular terminal family is noncritical outside its slope window. -/
theorem eulerTerminalSeventeen_nonresonant (r:ℕ) (hr:0<r)
    (hj:residualTerminalIndex r=17)
    (hd:terminalWallDistance r<11 ∨ 15<terminalWallDistance r)
    (x:D) (hz:reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 := by
  apply eulerSlope_no_critical_of_no_match r hr (by omega)
    (by rw [hj];exact terminalSeventeen_lower_simple) _ x hz
  intro i hi he
  rw [hj] at hi he
  have hb:=terminalSeventeen_slope_bounds i hi
  omega

/-- The base is an independently computed positive first omitted depth. -/
def slopeExampleR : ℕ := 2^63-17

lemma slopeExampleR_pos : 0<slopeExampleR := by decide +kernel

lemma slopeExampleR_terminal : residualTerminalIndex slopeExampleR=17 := by
  apply residualTerminalIndex_eq_of_finite_witness slopeExampleR 17 slopeExampleR_pos
  · change ∀q∈Finset.range 21,
      residualCarryCost slopeExampleR 17≤residualCarryCost slopeExampleR q
    decide +kernel
  · change ∀q∈Finset.range 21,
      residualCarryCost slopeExampleR q=residualCarryCost slopeExampleR 17 → q≤17
    decide +kernel

lemma slopeExampleR_distance : terminalWallDistance slopeExampleR=10 := by
  have he:terminalWallExponent slopeExampleR=63 := by
    rw [terminalWallExponent,slopeExampleR_terminal]
    decide +kernel
  rw [terminalWallDistance,he,slopeExampleR_terminal]
  decide +kernel

/-- A non-pointwise-unit irregular Euler wall, with a fully discharged finite carry witness. -/
theorem slopeExampleR_no_critical (x:D)
    (hz:reval (eulerNormalizedResidual slopeExampleR slopeExampleR_pos) x=0) :
    deriv (qeval (eulerNormalizedResidual slopeExampleR slopeExampleR_pos)) (x:ℚ_[2])≠0 := by
  exact eulerTerminalSeventeen_nonresonant slopeExampleR slopeExampleR_pos
    slopeExampleR_terminal (by rw [slopeExampleR_distance];exact Or.inl (by decide)) x hz

end Komorebi.Euler
