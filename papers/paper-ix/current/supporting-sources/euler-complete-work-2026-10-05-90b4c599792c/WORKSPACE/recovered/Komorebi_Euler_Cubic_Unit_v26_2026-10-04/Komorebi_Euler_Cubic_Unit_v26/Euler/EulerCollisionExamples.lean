module
public import Euler.EulerCollisionDegree
@[expose] public section
noncomputable section
set_option maxHeartbeats 4000000
set_option maxRecDepth 10000
namespace Komorebi.Euler
open PowerSeries

/-- A family whose slope-matching candidates all have one neighbor cannot have
an analytic triple zero. This does NOT exclude double zeros. -/
theorem eulerResidual_no_orderThree_of_one_neighbors (r:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r)
    (hs:LowerResidueSimple (residualTerminalIndex r))
    (hone:∀i, i<residualTerminalIndex r →
      terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i →
      ¬HasTwoNearest (residualTerminalIndex r) i) :
    ∀x:D, ¬(∀d:Fin 3, iteratedDeriv d.val
      (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) := by
  intro x hall
  have hzq : qeval (eulerNormalizedResidual r hr) (x:ℚ_[2])=0 := by
    simpa using hall ⟨0,by decide⟩
  have hz : reval (eulerNormalizedResidual r hr) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    rwa [coe_reval (eulerNormalizedResidual_restricted r hr)]
  have hder : deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0 := by
    simpa only [iteratedDeriv_one] using hall ⟨1,by decide⟩
  obtain ⟨i,hi,hx,hd,hdiv⟩:=
    eulerSlope_global_critical_localization r hr (by omega) hs x hz hder
  obtain ⟨u,hu⟩:=(dyadic_redPow_zero_iff_factor _ _).mp hdiv
  let w:D:=2*u
  have hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w := by
    rw [hu,pow_succ]
    dsimp [w]
    ring
  have hw0:red w=0:=by simp [w]
  have hjet:=terminalLower_jet_unit r hr hs (i:D) (by
    rw [hw,map_mul,hw0,mul_zero])
  obtain ⟨y,rfl⟩:=hx
  exact eulerSlope_oneNeighbor_second_ne_zero r i hr hj hi (hone i hi hd)
    w hw hjet hd hw0 y (hall ⟨2,by decide⟩)

lemma terminalSeventeen_equal11_one_neighbor (i:ℕ) (hi:i<17)
    (hd:skeletonSlope 17 i=11) : ¬HasTwoNearest 17 i := by
  have h:∀i:Fin 17,skeletonSlope 17 i.val=11 → ¬HasTwoNearest 17 i.val := by
    unfold HasTwoNearest
    decide +kernel
  exact h ⟨i,hi⟩ hd

/-- The whole actual terminal-17 resonant distance 11 has no triple derivative jet. -/
theorem eulerTerminalSeventeen_equal11_no_triple (r:ℕ) (hr:0<r)
    (hj:residualTerminalIndex r=17) (hd:terminalWallDistance r=11) :
    ∀x:D, ¬(∀d:Fin 3, iteratedDeriv d.val
      (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) := by
  apply eulerResidual_no_orderThree_of_one_neighbors r hr (by omega)
    (by rw [hj];exact terminalSeventeen_lower_simple)
  intro i hi hs
  rw [hj] at hi ⊢
  rw [hj,hd] at hs
  exact terminalSeventeen_equal11_one_neighbor i hi hs.symm

def collisionExampleR : ℕ := 2^64-17

lemma collisionExampleR_pos : 0<collisionExampleR := by decide +kernel

lemma collisionExampleR_terminal : residualTerminalIndex collisionExampleR=17 := by
  apply residualTerminalIndex_eq_of_finite_witness collisionExampleR 17 collisionExampleR_pos
  · change ∀q∈Finset.range 21,
      residualCarryCost collisionExampleR 17≤residualCarryCost collisionExampleR q
    decide +kernel
  · change ∀q∈Finset.range 21,
      residualCarryCost collisionExampleR q=residualCarryCost collisionExampleR 17 → q≤17
    decide +kernel

lemma collisionExampleR_distance : terminalWallDistance collisionExampleR=11 := by
  have he:terminalWallExponent collisionExampleR=64 := by
    rw [terminalWallExponent,collisionExampleR_terminal]
    decide +kernel
  rw [terminalWallDistance,he,collisionExampleR_terminal]
  decide +kernel

/-- An explicit original depth AT a resonant wall, with no assumed local coefficients. -/
theorem collisionExampleR_no_triple :
    ∀x:D, ¬(∀d:Fin 3, iteratedDeriv d.val
      (qeval (eulerNormalizedResidual collisionExampleR collisionExampleR_pos))
      (x:ℚ_[2])=0) :=
  eulerTerminalSeventeen_equal11_no_triple collisionExampleR collisionExampleR_pos
    collisionExampleR_terminal collisionExampleR_distance

/-- The generic nearest-neighbor algebra permits a double zero. This is NOT an Euler claim. -/
theorem direct_core_double_control :
    IsDirectHalfCore ((1+C (2:D)*X)*rescale (4:D) 1)
      (rescale (4:D) (-1)) (X^2) 0 := by
  simp only [IsDirectHalfCore,map_one,map_neg,map_zero]
  ring

/-- Two nearest neighbors permit a triple zero after one extra division.
This negative control prevents any inference of automatic simplicity. -/
theorem direct_core_triple_control :
    IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) 1)
      (rescale (4:D) (-1)) (-C (2:D)*X^3) 0 := by
  simp only [IsDirectHalfCore,map_one,map_neg,map_zero]
  rw [show C (4:D)=C (2:D)*C (2:D) by rw [←map_mul];norm_num]
  ring

end Komorebi.Euler
