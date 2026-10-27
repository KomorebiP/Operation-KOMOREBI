module
public import Euler.NearestNeighborSkeleton
public import Euler.DirectCollisionCoefficients
public import Euler.EulerSlopeRows
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Both closest integer neighbors lie in the actual finite skeleton. -/
def HasTwoNearest (j i:ℕ) : Prop :=
  (2^(skeletonDepth j i-1) ≤ i) ∧ (2^(skeletonDepth j i-1) ≤ j-1-i)

lemma nearestSkeletonFactor_two (j i:ℕ) (h:HasTwoNearest j i) :
    nearestSkeletonFactor j i=1-C (4:D)*X^2 := by
  simp only [nearestSkeletonFactor,ite_eq_left h.1,ite_eq_left h.2]
  rw [show C (4:D)=C (2:D)*C (2:D) by rw [←map_mul];norm_num]
  ring

lemma nearestSkeletonFactor_one (j i:ℕ) (hj:2≤j) (hi:i<j)
    (h:¬HasTwoNearest j i) :
    ∃ε:D, red ε=1 ∧ nearestSkeletonFactor j i=1+C (2*ε)*X := by
  have hn:=skeleton_nearest_exists j i hj hi
  by_cases hl : (2^(skeletonDepth j i-1) ≤ i)
  · have hr : ¬(2^(skeletonDepth j i-1) ≤ j-1-i) := by
      intro he;exact h ⟨hl,he⟩
    exact ⟨1,by simp,by simp [nearestSkeletonFactor,hl,hr]⟩
  · have hr : (2^(skeletonDepth j i-1) ≤ j-1-i) := hn.resolve_left hl
    refine ⟨-1,by simp,?_⟩
    simp [nearestSkeletonFactor,hl,hr]
    ring

/-- At equal slopes the exact existing half chart has a direct center identity.
No division by a lower-root unit and no prior root factorization are needed. -/
lemma eulerSlope_direct_core (r i:ℕ) (hr:0<r) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) :
    IsDirectHalfCore
      (skeletonLocalSeries (residualTerminalIndex r) i (terminalUpperSeries r hr))
      (lowerAffineTail (terminalLowerSeries r hr) (i:D)
        (skeletonDepth (residualTerminalIndex r) i)) F w := by
  unfold IsDirectHalfCore
  rw [hF,eulerSlopeAfterChart,slopeAfterSeries,hd,Nat.sub_self,pow_zero,map_one,one_mul]
  simp only [eulerLowerRootChart,normalizedLowerChart,Nat.sub_self,pow_zero,map_one,one_mul]
  ring

/-- Actual one-neighbor Euler half-core has a fully controlled quadratic coefficient tail. -/
theorem eulerSlope_oneNeighbor_coefficients (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) :
    ∃e t:Series, ∃ε:D, red (coeff 0 e)=1 ∧ red ε=1 ∧
      IsDirectHalfCore ((1+C (2*ε)*X)*rescale (4:D) e) (rescale (4:D) t) F w ∧
      ∀n:ℕ, coeff (n+2) F=(4:D)^n*
        (2*(coeff (n+1) e+coeff (n+1) t)+ε*coeff n e) := by
  have hk:=skeletonDepth_ge_two _ _ hj hi
  obtain ⟨e,he,he0⟩:=skeletonLocalSeries_nearest _ _ hk
    (terminalUpperSeries_restricted r hr) (terminalUpperSeries_red r hr)
  obtain ⟨t,ht⟩:=lowerAffineTail_fourScaled (terminalLowerSeries r hr) (i:D) _ hk
  obtain ⟨ε,hε,hN⟩:=nearestSkeletonFactor_one _ _ (by omega) hi hnear
  have hc:=eulerSlope_direct_core r i hr w F hd hF
  rw [he,hN,ht] at hc
  exact ⟨e,t,ε,he0,hε,hc,directOne_coeff e t F w ε hc⟩

/-- Actual two-neighbor Euler half-core has a forced nonzero cubic half coefficient. -/
theorem eulerSlope_twoNeighbor_coefficients (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:HasTwoNearest (residualTerminalIndex r) i) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) :
    ∃e t:Series, red (coeff 0 e)=1 ∧
      IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w ∧
      ∀n:ℕ, coeff (n+3) F=2*(4:D)^n*
        (4*(coeff (n+2) e+coeff (n+2) t)-coeff n e) := by
  have hk:=skeletonDepth_ge_two _ _ hj hi
  obtain ⟨e,he,he0⟩:=skeletonLocalSeries_nearest _ _ hk
    (terminalUpperSeries_restricted r hr) (terminalUpperSeries_red r hr)
  obtain ⟨t,ht⟩:=lowerAffineTail_fourScaled (terminalLowerSeries r hr) (i:D) _ hk
  have hc:=eulerSlope_direct_core r i hr w F hd hF
  rw [he,nearestSkeletonFactor_two _ _ hnear,ht] at hc
  exact ⟨e,t,he0,hc,directTwo_coeff e t F w hc⟩

/-- The inherited existence theorem now feeds a proved actual quadratic reduction. -/
theorem eulerSlope_oneNeighbor_quadratic (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven:red w=0) :
    ∃F:Series, Restricted F ∧ LastOdd F 2 ∧
      C (2:D)*F=eulerSlopeAfterChart r i hr w ∧
      ∀y:D, reval (eulerNormalizedResidual r hr)
        (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
        (2:D)^(skeletonContent (residualTerminalIndex r) i+1)*reval F y := by
  obtain ⟨F,hFr,hF,hval⟩:=eulerSlope_equal_even_core r i hr hi w hw hjet hd heven
  obtain ⟨e,t,ε,he0,hε,hc,_⟩:=eulerSlope_oneNeighbor_coefficients r i hr hj hi hnear w F hd hF
  exact ⟨F,hFr,directOne_lastOdd e t F w ε he0 hε hc,hF,hval⟩

/-- The actual two-neighbor core is constant/affine, or exactly one additional
integral division exposes a cubic. No last-odd index exceeds three. -/
theorem eulerSlope_twoNeighbor_trichotomy (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:HasTwoNearest (residualTerminalIndex r) i) (w:D)
    (hw:reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet:red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven:red w=0) :
    ∃F:Series, Restricted F ∧ C (2:D)*F=eulerSlopeAfterChart r i hr w ∧
      (∀y:D, reval (eulerNormalizedResidual r hr)
        (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
        (2:D)^(skeletonContent (residualTerminalIndex r) i+1)*reval F y) ∧
      (LastOdd F 0 ∨ LastOdd F 1 ∨
        ∃K:Series, C (2:D)*K=F ∧ Restricted K ∧ LastOdd K 3) := by
  obtain ⟨F,hFr,hF,hval⟩:=eulerSlope_equal_even_core r i hr hi w hw hjet hd heven
  obtain ⟨e,t,he0,hc,_⟩:=eulerSlope_twoNeighbor_coefficients r i hr hj hi hnear w F hd hF
  exact ⟨F,hFr,hF,hval,directTwo_dichotomy e t F w he0 hc⟩

end Komorebi.Euler
