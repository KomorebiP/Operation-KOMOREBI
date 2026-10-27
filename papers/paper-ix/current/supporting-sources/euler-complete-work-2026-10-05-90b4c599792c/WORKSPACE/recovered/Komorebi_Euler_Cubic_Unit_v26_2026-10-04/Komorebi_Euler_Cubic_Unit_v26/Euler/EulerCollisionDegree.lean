module
public import Euler.EulerNearestCore
public import Euler.LastOddDerivatives
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Every aligned equal-slope Euler chart has an exact normalized degree at most
three. The content is t_i+1 or t_i+2, never an unspecified normalization. -/
theorem eulerSlope_core_degree_bound (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven:red w=0) :
    ∃F:Series, ∃d c:ℕ, Restricted F ∧ LastOdd F d ∧ d≤3 ∧
      (c=skeletonContent (residualTerminalIndex r) i+1 ∨
       c=skeletonContent (residualTerminalIndex r) i+2) ∧
      ∀y:D, reval (eulerNormalizedResidual r hr)
        (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
        (2:D)^c*reval F y := by
  by_cases hn:HasTwoNearest (residualTerminalIndex r) i
  · obtain ⟨F,hFr,_,hval,hcases⟩:=
      eulerSlope_twoNeighbor_trichotomy r i hr hj hi hn w hw hjet hd heven
    rcases hcases with h0 | h1 | ⟨K,hK,hKr,h3⟩
    · exact ⟨F,0,_,hFr,h0,by omega,Or.inl rfl,hval⟩
    · exact ⟨F,1,_,hFr,h1,by omega,Or.inl rfl,hval⟩
    · refine ⟨K,3,skeletonContent (residualTerminalIndex r) i+2,hKr,h3,le_rfl,Or.inr rfl,?_⟩
      intro y
      rw [hval,←hK,reval_C_mul hKr]
      rw [show skeletonContent (residualTerminalIndex r) i+2=
        (skeletonContent (residualTerminalIndex r) i+1)+1 by omega,pow_succ]
      ring
  · obtain ⟨F,hFr,h2,_,hval⟩:=
      eulerSlope_oneNeighbor_quadratic r i hr hj hi hn w hw hjet hd heven
    exact ⟨F,2,_,hFr,h2,by omega,Or.inl rfl,hval⟩

/-- No exact chart with last odd index d can have its dth analytic derivative zero.
This transports a jet obstruction to the original, unnormalized variable. -/
lemma scaled_lastOdd_derivative_nonzero {g f:Series}
    (hg:Restricted g) (hf:Restricted f) (a:D) (k c d:ℕ)
    (hd:LastOdd f d)
    (he:∀y:D,reval g (dyadicChart a k y)=(2:D)^c*reval f y) (y:D) :
    iteratedDeriv d (qeval g) ((dyadicChart a k y:D):ℚ_[2])≠0 := by
  have hh:=restricted_scaled_iteratedDeriv hg hf a ((2:D)^k) ((2:D)^c) he d y
  intro hz
  change ((2:D)^k:ℚ_[2])^d*
    iteratedDeriv d (qeval g) ((dyadicChart a k y:D):ℚ_[2])=_ at hh
  rw [hz,mul_zero] at hh
  have hc:((2:D)^c:ℚ_[2])≠0:=PadicInt.coe_ne_zero.mpr (pow_ne_zero c two_ne_zero)
  exact lastOdd_top_iteratedDeriv_ne_zero hf hd y ((mul_eq_zero.mp hh.symm).resolve_left hc)

/-- One nearest neighbor excludes even an analytic triple jet on the ACTUAL
Euler ball. It does not exclude double roots. -/
theorem eulerSlope_oneNeighbor_second_ne_zero (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven:red w=0) (y:D) :
    iteratedDeriv 2 (qeval (eulerNormalizedResidual r hr))
      ((dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y:D):ℚ_[2])≠0 := by
  obtain ⟨F,hFr,h2,_,hval⟩:=
    eulerSlope_oneNeighbor_quadratic r i hr hj hi hnear w hw hjet hd heven
  exact scaled_lastOdd_derivative_nonzero (eulerNormalizedResidual_restricted r hr)
    hFr (i:D) _ _ 2 h2 hval y

/-- End-to-end derivative-jet ceiling: under the actual simple lower-residue
hypothesis no Euler residual has simultaneous derivatives of orders 0,1,2,3 zero.
No closed-disc Weierstrass preparation or hypothetical polynomial is needed. -/
theorem eulerResidual_no_orderFour_zero (r:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r)
    (hs:LowerResidueSimple (residualTerminalIndex r)) :
    ∀x:D, ¬(∀d:Fin 4, iteratedDeriv d.val
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
  obtain ⟨F,d,c,hFr,hFo,hd3,_,hval⟩:=
    eulerSlope_core_degree_bound r i hr hj hi w hw hjet hd hw0
  obtain ⟨y,rfl⟩:=hx
  exact scaled_lastOdd_derivative_nonzero (eulerNormalizedResidual_restricted r hr)
    hFr (i:D) _ c d hFo hval y (hall ⟨d,by omega⟩)

end Komorebi.Euler
