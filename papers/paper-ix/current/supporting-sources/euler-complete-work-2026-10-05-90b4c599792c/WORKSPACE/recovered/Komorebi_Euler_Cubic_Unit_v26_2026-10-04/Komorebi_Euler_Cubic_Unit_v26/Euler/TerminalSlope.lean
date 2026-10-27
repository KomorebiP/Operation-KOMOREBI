module
public import Euler.TerminalResidues
public import Euler.ResidualSlopeTransport
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The terminal skeleton times its ACTUAL continuation, as a field function. -/
def terminalSkeletonFunction (r : ℕ) (hr : 0<r) (x : ℚ_[2]) : ℚ_[2] :=
  qeval (eulerPacket (residualTerminalIndex r):Series) x*
    qeval (terminalUpperSeries r hr) (x-(residualTerminalIndex r:ℚ_[2]))

lemma terminalSkeletonFunction_hasDerivAt (r : ℕ) (hr : 0<r) (x : D) :
    HasDerivAt (terminalSkeletonFunction r hr)
      (deriv (qeval (eulerPacket (residualTerminalIndex r):Series)) (x:ℚ_[2])*
        qeval (terminalUpperSeries r hr) ((x:ℚ_[2])-(residualTerminalIndex r:ℚ_[2]))+
       qeval (eulerPacket (residualTerminalIndex r):Series) (x:ℚ_[2])*
        deriv (qeval (terminalUpperSeries r hr)) ((x:ℚ_[2])-(residualTerminalIndex r:ℚ_[2])))
      (x:ℚ_[2]) := by
  have hp := (hasDerivAt_qeval (polynomial_restricted (eulerPacket (residualTerminalIndex r))) x).differentiableAt.hasDerivAt
  have hu := (hasDerivAt_qeval (terminalUpperSeries_restricted r hr)
    (x-(residualTerminalIndex r:D))).differentiableAt.hasDerivAt
  simp only [PadicInt.coe_sub,PadicInt.coe_natCast] at hu
  have hs : HasDerivAt
      (fun y:ℚ_[2] => qeval (terminalUpperSeries r hr) (y-(residualTerminalIndex r:ℚ_[2])))
      (deriv (qeval (terminalUpperSeries r hr)) ((x:ℚ_[2])-(residualTerminalIndex r:ℚ_[2])))
      (x:ℚ_[2]) := by
    convert hu.comp (x:ℚ_[2])
      ((hasDerivAt_id (x:ℚ_[2])).sub_const (residualTerminalIndex r:ℚ_[2])) using 1 <;>
      first | rfl | simp only [mul_one]
  exact hp.mul hs

lemma terminalWall_qeval_identity (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D) :
    qeval (eulerNormalizedResidual r hr) (x:ℚ_[2])=
      terminalSkeletonFunction r hr (x:ℚ_[2])+
        (2:ℚ_[2])^(terminalWallDistance r)*qeval (terminalLowerSeries r hr) (x:ℚ_[2]) := by
  have h := congrArg (fun z:D => (z:ℚ_[2]))
    (eulerNormalizedResidual_terminal_form r hr hj x)
  simp only [PadicInt.coe_add,PadicInt.coe_mul,PadicInt.coe_pow] at h
  rw [coe_reval (eulerNormalizedResidual_restricted r hr),
    coe_reval (terminalLowerSeries_restricted r hr),
    coe_reval (terminalUpperSeries_restricted r hr)] at h
  simp only [PadicInt.coe_sub,PadicInt.coe_natCast] at h
  have hp : (((eulerPacket (residualTerminalIndex r)).eval x:D):ℚ_[2])=
      qeval (eulerPacket (residualTerminalIndex r):Series) (x:ℚ_[2]) := by
    rw [← coe_reval (polynomial_restricted _),reval_polynomial]
  rw [hp] at h
  exact h

/-- The actual wall decomposition carries a genuine analytic slope identity. -/
theorem eulerNormalizedResidual_terminal_derivative (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=
      deriv (terminalSkeletonFunction r hr) (x:ℚ_[2])+
      (2:ℚ_[2])^(terminalWallDistance r)*
        deriv (qeval (terminalLowerSeries r hr)) (x:ℚ_[2]) := by
  have he : qeval (eulerNormalizedResidual r hr)=ᶠ[𝓝 (x:ℚ_[2])]
      (fun y:ℚ_[2] => terminalSkeletonFunction r hr y+
        (2:ℚ_[2])^(terminalWallDistance r)*qeval (terminalLowerSeries r hr) y) :=
    eventuallyEq_of_eq_on_dyadic (terminalWall_qeval_identity r hr hj) x
  have hs := (terminalSkeletonFunction_hasDerivAt r hr x).differentiableAt.hasDerivAt
  have hv := (hasDerivAt_qeval (terminalLowerSeries_restricted r hr) x).differentiableAt.hasDerivAt
  exact ((hs.add (hv.const_mul ((2:ℚ_[2])^(terminalWallDistance r)))).congr_of_eventuallyEq he).deriv

/-- No division by the skeleton or the lower residual is made. -/
def terminalWallWronskian (r : ℕ) (hr : 0<r) (x : ℚ_[2]) : ℚ_[2] :=
  qeval (terminalLowerSeries r hr) x*deriv (terminalSkeletonFunction r hr) x-
  deriv (qeval (terminalLowerSeries r hr)) x*terminalSkeletonFunction r hr x

lemma terminalWallWronskian_identity (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D) :
    terminalWallWronskian r hr (x:ℚ_[2])=
      qeval (terminalLowerSeries r hr) (x:ℚ_[2])*
        deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])-
      deriv (qeval (terminalLowerSeries r hr)) (x:ℚ_[2])*
        qeval (eulerNormalizedResidual r hr) (x:ℚ_[2]) := by
  rw [eulerNormalizedResidual_terminal_derivative r hr hj,
    terminalWall_qeval_identity r hr hj]
  unfold terminalWallWronskian
  ring

/-- Exact value/slope criterion when the lower residual does not vanish. -/
theorem terminalWall_critical_iff (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D)
    (hv : reval (terminalLowerSeries r hr) x≠0) :
    CriticalZero (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2]) ↔
      qeval (eulerNormalizedResidual r hr) (x:ℚ_[2])=0 ∧
      terminalWallWronskian r hr (x:ℚ_[2])=0 := by
  have hv' : qeval (terminalLowerSeries r hr) (x:ℚ_[2])≠0 := by
    rw [← coe_reval (terminalLowerSeries_restricted r hr)]
    exact PadicInt.coe_ne_zero.mpr hv
  unfold CriticalZero
  rw [terminalWallWronskian_identity r hr hj]
  constructor
  · rintro ⟨h0,h1⟩
    simp only [h0,h1,mul_zero,sub_zero,and_self]
  · rintro ⟨h0,hw⟩
    refine ⟨h0,?_⟩
    rw [h0,mul_zero,sub_zero] at hw
    exact (mul_eq_zero.mp hw).resolve_left hv'

/-- A genuine wall Wronskian witness rules out a critical zero without any lower-unit hypothesis. -/
theorem terminalWall_no_critical_of_wronskian (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D)
    (hw : terminalWallWronskian r hr (x:ℚ_[2])≠0) :
    ¬CriticalZero (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2]) := by
  rintro ⟨h0,h1⟩
  apply hw
  rw [terminalWallWronskian_identity r hr hj,h0,h1,mul_zero,mul_zero,sub_zero]

end Komorebi.Euler
