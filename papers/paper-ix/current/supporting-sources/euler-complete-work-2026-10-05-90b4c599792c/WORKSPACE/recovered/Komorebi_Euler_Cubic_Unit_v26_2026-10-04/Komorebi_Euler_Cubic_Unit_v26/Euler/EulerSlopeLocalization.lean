module
public import Euler.EulerShallowLower
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

lemma dyadic_redPow_zero_iff_factor (k : ℕ) (x : D) :
    redPow k x=0 ↔ ∃w:D, x=(2:D)^k*w := by
  change redPow k x=0 ↔ (2:D)^k∣x
  rw [← RingHom.mem_ker,PadicInt.ker_toZModPow,Ideal.mem_span_singleton]
  norm_num

lemma dyadic_unit_red (u : Dˣ) : red (u:D)=1 := by
  apply red_not_zero_eq_one
  intro hz
  have hh := (red_zero_iff_norm_lt_one _).mp hz
  rw [PadicInt.norm_units] at hh
  exact (lt_irrefl 1) hh

/-- Failure of radius divisibility yields a genuine shallower content and odd unit. -/
theorem dyadic_shallow_factor (k : ℕ) (x : D) (hx : redPow k x≠0) :
    ∃ s:ℕ, ∃w:D, s<k ∧ red w=1 ∧ x=(2:D)^s*w := by
  have hn : x≠0 := by intro h;simp [h] at hx
  let u : Dˣ := PadicInt.unitCoeff hn
  have he : x=(2:D)^x.valuation*(u:D) := by
    simpa [u,mul_comm] using PadicInt.unitCoeff_spec hn
  have hs : x.valuation<k := by
    by_contra h
    have hk : k≤x.valuation := by omega
    apply hx
    apply (dyadic_redPow_zero_iff_factor k x).mpr
    refine ⟨(2:D)^(x.valuation-k)*(u:D),?_⟩
    calc
      x=(2:D)^x.valuation*(u:D) := he
      _=(2:D)^k*((2:D)^(x.valuation-k)*(u:D)) := by
        rw [← mul_assoc,← pow_add,Nat.add_sub_of_le hk]
  exact ⟨x.valuation,(u:D),hs,dyadic_unit_red u,he⟩

/-- A check on the complete carry-defined residue polynomial, not on sampled rows. -/
def LowerResidueSimple (j : ℕ) : Prop :=
  ∀e:F₂, (terminalLowerPolynomial j).eval e=0 →
    (terminalLowerPolynomial j).derivative.eval e≠0

lemma terminalLower_jet_unit (r : ℕ) (hr : 0<r)
    (hsimple : LowerResidueSimple (residualTerminalIndex r)) (a : D)
    (ha : red (reval (terminalLowerSeries r hr) a)=0) :
    red (rjet 1 (terminalLowerSeries r hr) a)=1 := by
  have hp:=terminalLowerSeries_certificate r hr
  have hv:=reval_residue_polynomial (terminalLowerSeries_restricted r hr) 1
    (terminalLowerPolynomial (residualTerminalIndex r)) hp a
  rw [res_eq_red,res_eq_red,ha] at hv
  have hd:=hsimple (red a) hv.symm
  apply red_not_zero_eq_one
  have hh:=res_rjet_one (terminalLowerSeries_restricted r hr)
    (terminalLowerPolynomial (residualTerminalIndex r)) hp a
  simp only [res_eq_red] at hh
  rw [hh]
  exact hd

/-- Local necessary conditions for a critical zero, with all center contents constructed. -/
theorem eulerSlope_local_critical_tests (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r)
    (hsimple : LowerResidueSimple (residualTerminalIndex r)) (x:D)
    (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i))
    (hz : reval (eulerNormalizedResidual r hr) x=0)
    (hder : deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) :
    terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i ∧
      redPow (skeletonDepth (residualTerminalIndex r) i+1)
        (reval (terminalLowerSeries r hr) (i:D))=0 := by
  by_cases hc : redPow (skeletonDepth (residualTerminalIndex r) i)
      (reval (terminalLowerSeries r hr) (i:D))=0
  · obtain ⟨w,hw⟩ := (dyadic_redPow_zero_iff_factor _ _).mp hc
    have hzero : red (reval (terminalLowerSeries r hr) (i:D))=0 := by
      rw [hw,map_mul,skeleton_scale_red,zero_mul]
    have hjet:=terminalLower_jet_unit r hr hsimple (i:D) hzero
    obtain ⟨hd,he⟩ := eulerSlope_critical_necessary r i hr hi w hw hjet x hx hz hder
    refine ⟨hd,?_⟩
    obtain ⟨z,hz'⟩ := (red_eq_zero_iff w).mp he
    apply (dyadic_redPow_zero_iff_factor _ _).mpr
    refine ⟨z,?_⟩
    rw [hw,hz',pow_succ,mul_assoc]
  · obtain ⟨s,w,hs,hu,hw⟩ := dyadic_shallow_factor _ _ hc
    exact False.elim (eulerShallow_no_critical r i s hr hi w hs hw hu x hx hz hder)

/-- Every possible repeated Euler root is localized to an explicit slope/alignment test. -/
theorem eulerSlope_global_critical_localization (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r)
    (hsimple : LowerResidueSimple (residualTerminalIndex r)) (x:D)
    (hz : reval (eulerNormalizedResidual r hr) x=0)
    (hder : deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) :
    ∃i:ℕ, i<residualTerminalIndex r ∧
      x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) ∧
      terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i ∧
      redPow (skeletonDepth (residualTerminalIndex r) i+1)
        (reval (terminalLowerSeries r hr) (i:D))=0 := by
  obtain ⟨i,hi,hx⟩ := skeleton_balls_cover (residualTerminalIndex r) hj x
  exact ⟨i,hi,hx,eulerSlope_local_critical_tests r i hr hi hsimple x hx hz hder⟩

/-- Excluding the finitely many aligned slope matches proves actual Euler simplicity. -/
theorem eulerSlope_no_critical_of_no_match (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r)
    (hsimple : LowerResidueSimple (residualTerminalIndex r))
    (hexclude : ∀i, i<residualTerminalIndex r →
      terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i →
      redPow (skeletonDepth (residualTerminalIndex r) i+1)
        (reval (terminalLowerSeries r hr) (i:D))≠0) :
    ∀x:D, reval (eulerNormalizedResidual r hr) x=0 →
      deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 := by
  intro x hz hd
  obtain ⟨i,hi,_,hs,hv⟩ :=
    eulerSlope_global_critical_localization r hr hj hsimple x hz hd
  exact hexclude i hi hs hv

end Komorebi.Euler
