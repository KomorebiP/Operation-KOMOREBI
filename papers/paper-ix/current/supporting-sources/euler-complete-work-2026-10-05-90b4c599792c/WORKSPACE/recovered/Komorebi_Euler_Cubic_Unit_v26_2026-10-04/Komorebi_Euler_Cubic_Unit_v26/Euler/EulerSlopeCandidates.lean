module
public import Euler.EulerSlopeLocalization
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler

lemma dyadicBall_red_center (a x:D) (k:ℕ) (hk:0<k)
    (hx:x∈dyadicBall a k) : red x=red a := by
  obtain ⟨y,rfl⟩:=hx
  simp [dyadicChart,map_add,map_mul,map_pow,show k≠0 by omega]

/-- Two zeros of the actual lower prefix in the same simple residue are equal. -/
lemma terminalLower_roots_unique_parity (r:ℕ) (hr:0<r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r)) (x y:D)
    (hx:reval (terminalLowerSeries r hr) x=0)
    (hy:reval (terminalLowerSeries r hr) y=0) (he:red x=red y) : x=y := by
  have hp:=terminalLowerSeries_certificate r hr
  have hv:=reval_residue_polynomial (terminalLowerSeries_restricted r hr) 1
    (terminalLowerPolynomial (residualTerminalIndex r)) hp y
  rw [hy,map_zero,res_eq_red] at hv
  have hd:=hsimple (red y) hv.symm
  have hn:=restricted_isometry_on_simple_residue (terminalLowerSeries_restricted r hr)
    (terminalLowerPolynomial (residualTerminalIndex r)) hp x y
    (by simpa only [res_eq_red] using he) (by simpa only [res_eq_red] using hd)
  rw [hx,hy,sub_self,norm_zero] at hn
  exact sub_eq_zero.mp (norm_eq_zero.mp hn.symm)

/-- Every radius-aligned skeleton ball has an actual lower root. -/
lemma eulerLower_root_of_radius (r i:ℕ) (hr:0<r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r))
    (hc:redPow (skeletonDepth (residualTerminalIndex r) i)
      (reval (terminalLowerSeries r hr) (i:D))=0) :
    ∃β:D, β∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) ∧
      reval (terminalLowerSeries r hr) β=0 := by
  obtain ⟨w,hw⟩:=(dyadic_redPow_zero_iff_factor _ _).mp hc
  have hzero:red (reval (terminalLowerSeries r hr) (i:D))=0 := by
    rw [hw,map_mul,skeleton_scale_red,zero_mul]
  obtain ⟨β,hb,hz,_⟩:=eulerLower_root_atlas r i hr w hw
    (terminalLower_jet_unit r hr hsimple (i:D) hzero)
  exact ⟨β,hb,hz⟩

/-- Skeleton balls containing a lower root, characterized by a finite-precision center test. -/
def LowerAlignedSkeleton (r:ℕ) (hr:0<r) :=
  {i:Fin (residualTerminalIndex r) //
    redPow (skeletonDepth (residualTerminalIndex r) i.val)
      (reval (terminalLowerSeries r hr) (i.val:D))=0}

noncomputable instance (r:ℕ) (hr:0<r) : Fintype (LowerAlignedSkeleton r hr) := by
  classical
  exact inferInstanceAs (Fintype {i:Fin (residualTerminalIndex r) //
    redPow (skeletonDepth (residualTerminalIndex r) i.val)
      (reval (terminalLowerSeries r hr) (i.val:D))=0})

/-- Different aligned skeleton balls must correspond to different binary lower roots. -/
theorem lowerAlignedSkeleton_parity_injective (r:ℕ) (hr:0<r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r)) :
    Function.Injective (fun i:LowerAlignedSkeleton r hr => red (i.val.val:D)) := by
  intro i l he
  obtain ⟨x,hxi,hx⟩:=eulerLower_root_of_radius r i.val.val hr hsimple i.property
  obtain ⟨y,hyl,hy⟩:=eulerLower_root_of_radius r l.val.val hr hsimple l.property
  have hrx:=dyadicBall_red_center (i.val.val:D) x _ (skeletonDepth_pos _ _) hxi
  have hry:=dyadicBall_red_center (l.val.val:D) y _ (skeletonDepth_pos _ _) hyl
  have hxy:=terminalLower_roots_unique_parity r hr hsimple x y hx hy
    (hrx.trans (he.trans hry.symm))
  have hil:i.val.val=l.val.val := by
    by_contra hn
    have hdis:=skeleton_balls_disjoint (residualTerminalIndex r) i.val.val l.val.val
      i.val.isLt l.val.isLt hn
    rw [Set.disjoint_left] at hdis
    rw [←hxy] at hyl
    exact hdis hxi hyl
  exact Subtype.ext (Fin.ext hil)

/-- At most two skeleton balls contain lower roots for this fixed actual Euler residual. -/
theorem lowerAlignedSkeleton_card_le_two (r:ℕ) (hr:0<r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r)) :
    Fintype.card (LowerAlignedSkeleton r hr)≤2 := by
  have h:=Fintype.card_le_of_injective
    (fun i:LowerAlignedSkeleton r hr => red (i.val.val:D))
    (lowerAlignedSkeleton_parity_injective r hr hsimple)
  simpa using h

/-- The genuinely undecided centers additionally require slope equality and one extra bit. -/
def SlopeCandidate (r:ℕ) (hr:0<r) :=
  {i:LowerAlignedSkeleton r hr //
    terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i.val.val ∧
    redPow (skeletonDepth (residualTerminalIndex r) i.val.val+1)
      (reval (terminalLowerSeries r hr) (i.val.val:D))=0}

noncomputable instance (r:ℕ) (hr:0<r) : Fintype (SlopeCandidate r hr) := by
  classical
  unfold SlopeCandidate
  infer_instance

theorem slopeCandidate_card_le_two (r:ℕ) (hr:0<r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r)) :
    Fintype.card (SlopeCandidate r hr)≤2 := by
  exact (Fintype.card_le_of_injective
    (fun i:SlopeCandidate r hr => i.val) Subtype.val_injective).trans
    (lowerAlignedSkeleton_card_le_two r hr hsimple)

/-- Every critical zero is in one of the at most two constructed candidate balls. -/
theorem eulerCritical_mem_slopeCandidate (r:ℕ) (hr:0<r)
    (hj:2≤residualTerminalIndex r)
    (hsimple:LowerResidueSimple (residualTerminalIndex r)) (x:D)
    (hz:reval (eulerNormalizedResidual r hr) x=0)
    (hd:deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) :
    ∃i:SlopeCandidate r hr,
      x∈dyadicBall (i.val.val.val:D) (skeletonDepth (residualTerminalIndex r) i.val.val.val) := by
  obtain ⟨i,hi,hx,hs,hv⟩:=eulerSlope_global_critical_localization r hr hj hsimple x hz hd
  have hv0:redPow (skeletonDepth (residualTerminalIndex r) i)
      (reval (terminalLowerSeries r hr) (i:D))=0 := by
    obtain ⟨z,hz'⟩:=(dyadic_redPow_zero_iff_factor _ _).mp hv
    apply (dyadic_redPow_zero_iff_factor _ _).mpr
    exact ⟨2*z,by rw [hz',pow_succ,mul_assoc]⟩
  exact ⟨⟨⟨⟨i,hi⟩,hv0⟩,hs,hv⟩,hx⟩

end Komorebi.Euler
