module
public import Euler.EulerLocalAtlas
public import Euler.SkeletonPartition
public import Mathlib.SetTheory.Cardinal.Finite
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler

/-- Precisely the separating skeleton balls whose threshold has been reached. -/
def ActiveSkeleton (r : ℕ) :=
  {i:Fin (residualTerminalIndex r) //
    skeletonContent (residualTerminalIndex r) i.val≤terminalWallDistance r}

instance (r : ℕ) : Fintype (ActiveSkeleton r) :=
  inferInstanceAs (Fintype {i:Fin (residualTerminalIndex r) //
    skeletonContent (residualTerminalIndex r) i.val≤terminalWallDistance r})

/-- The roots of the actual constructed normalized Euler residual. -/
def EulerResidualRoots (r : ℕ) (hr : 0 < r) :=
  {x:D // reval (eulerNormalizedResidual r hr) x=0}

noncomputable def skeletonSelectedRoot (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1)
    (i : ActiveSkeleton r) : D :=
  Classical.choose (eulerWall_superthreshold_atlas r i.val.val hr i.val.isLt i.property
    (hv (i.val.val:D)))

lemma skeletonSelectedRoot_spec (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1) (i : ActiveSkeleton r) :
    let α:=skeletonSelectedRoot r hr hv i
    α∈dyadicBall (i.val.val:D) (skeletonDepth (residualTerminalIndex r) i.val.val) ∧
    reval (eulerNormalizedResidual r hr) α=0 ∧
    ‖deriv (qeval (eulerNormalizedResidual r hr)) (α:ℚ_[2])‖=
      ‖(2:D)^(skeletonSlope (residualTerminalIndex r) i.val.val)‖ ∧
    (∀ x∈dyadicBall (i.val.val:D) (skeletonDepth (residualTerminalIndex r) i.val.val),
      reval (eulerNormalizedResidual r hr) x=0 ↔ x=α) ∧
    (∀ x∈dyadicBall (i.val.val:D) (skeletonDepth (residualTerminalIndex r) i.val.val),
      ‖reval (eulerNormalizedResidual r hr) x‖=
        ‖(2:D)^(skeletonSlope (residualTerminalIndex r) i.val.val)‖*‖x-α‖) :=
  Classical.choose_spec (eulerWall_superthreshold_atlas r i.val.val hr i.val.isLt i.property
    (hv (i.val.val:D)))

noncomputable def activeSkeletonToRoot (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1)
    (i : ActiveSkeleton r) : EulerResidualRoots r hr :=
  ⟨skeletonSelectedRoot r hr hv i,(skeletonSelectedRoot_spec r hr hv i).2.1⟩

lemma activeSkeletonToRoot_injective (r : ℕ) (hr : 0 < r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1) :
    Function.Injective (activeSkeletonToRoot r hr hv) := by
  intro i l he
  have he' : skeletonSelectedRoot r hr hv i=skeletonSelectedRoot r hr hv l :=
    congrArg Subtype.val he
  have h1:=(skeletonSelectedRoot_spec r hr hv i).1
  have h2:=(skeletonSelectedRoot_spec r hr hv l).1
  by_contra hne
  have hn : i.val.val≠l.val.val := by
    intro hh
    apply hne
    apply Subtype.ext
    exact Fin.ext hh
  have hd:=skeleton_balls_disjoint (residualTerminalIndex r) i.val.val l.val.val
    i.val.isLt l.val.isLt hn
  rw [Set.disjoint_left] at hd
  rw [← he'] at h2
  exact hd h1 h2

lemma activeSkeletonToRoot_surjective (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1) :
    Function.Surjective (activeSkeletonToRoot r hr hv) := by
  intro x
  obtain ⟨i,hi,hxi⟩:=skeleton_balls_cover (residualTerminalIndex r) hj x.val
  have ht : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r := by
    by_contra hn
    exact eulerWall_subthreshold_nonzero r i hr hi (by omega) (hv (i:D)) x.val hxi x.property
  let a:ActiveSkeleton r:=⟨⟨i,hi⟩,ht⟩
  refine ⟨a,?_⟩
  apply Subtype.ext
  exact ((skeletonSelectedRoot_spec r hr hv a).2.2.2.1 x.val hxi).mp x.property |>.symm

/-- A finite skeleton-threshold type is exactly equivalent to all actual dyadic Euler roots. -/
noncomputable def eulerPointwiseRootEquiv (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1) :
    ActiveSkeleton r ≃ EulerResidualRoots r hr :=
  Equiv.ofBijective (activeSkeletonToRoot r hr hv)
    ⟨activeSkeletonToRoot_injective r hr hv,activeSkeletonToRoot_surjective r hr hj hv⟩

/-- All-distance exact root count for the actual pointwise-unit lower-prefix class. -/
theorem eulerPointwise_root_count (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1) :
    Nat.card (EulerResidualRoots r hr)=
      Fintype.card {i:Fin (residualTerminalIndex r) //
        skeletonContent (residualTerminalIndex r) i.val≤terminalWallDistance r} := by
  rw [← Nat.card_congr (eulerPointwiseRootEquiv r hr hj hv),Nat.card_eq_fintype_card]
  rfl

/-- Every actual root in this entire class has nonzero genuine analytic derivative. -/
theorem eulerPointwise_no_critical (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (hv : ∀x:D, red (reval (terminalLowerSeries r hr) x)=1)
    (x : D) (hx : reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 := by
  obtain ⟨i,hi⟩:=activeSkeletonToRoot_surjective r hr hj hv ⟨x,hx⟩
  have he : skeletonSelectedRoot r hr hv i=x := congrArg Subtype.val hi
  have hn:=(skeletonSelectedRoot_spec r hr hv i).2.2.1
  rw [he] at hn
  intro hz
  rw [hz,norm_zero] at hn
  exact (norm_ne_zero_iff.mpr (pow_ne_zero _ (by norm_num : (2:D)≠0))) hn.symm

/-- The pointwise-unit input is discharged by the actual lower carry costs. -/
theorem eulerCarry_unit_no_critical (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r)
    (he : terminalLowerMinimum (residualTerminalIndex r)=0)
    (h1 : terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r))
    (x : D) (hx : reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 :=
  eulerPointwise_no_critical r hr hj
    ((terminalLowerSeries_pointwise_unit_iff r hr hj).mpr ⟨he,h1⟩) x hx

/-- Every regular actual terminal wall of degree at least two is formally simple. -/
theorem eulerRegular_no_critical (r : ℕ) (hr : 0 < r)
    (hj : 2≤residualTerminalIndex r) (hreg : TerminalRegular (residualTerminalIndex r))
    (x : D) (hx : reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 := by
  have he:=terminalLowerMinimum_regular _ (by omega) hreg
  apply eulerCarry_unit_no_critical r hr hj he _ x hx
  have hp:=hreg 1 (by decide) (by omega)
  omega

end Komorebi.Euler
