module
public import Euler.ResidualPacketJets
public import Euler.RestrictedHigherDerivatives
public import Mathlib.Analysis.Calculus.Deriv.Comp
public import Mathlib.Analysis.Calculus.Deriv.Add
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma coe_tsum_dyadic {a : ℕ → D} (ha : Summable a) :
    ((∑' n, a n : D):ℚ_[2])=∑' n, (a n:ℚ_[2]) := by
  exact ((ha.hasSum.map (PadicInt.Coe.ringHom : D →+* ℚ_[2])
    PadicInt.isOpenEmbedding_coe.continuous).tsum_eq).symm

lemma summable_coe_dyadic {a : ℕ → D} (ha : Summable a) :
    Summable (fun n => (a n:ℚ_[2])) :=
  (ha.hasSum.map (PadicInt.Coe.ringHom : D →+* ℚ_[2])
    PadicInt.isOpenEmbedding_coe.continuous).summable

lemma rjet_C_mul {f : Series} (hf : Restricted f) (a : D) (k : ℕ) (x : D) :
    rjet k (C a*f) x=a*rjet k f x := by
  have h : hasseSeries k (C a*f)=C a*hasseSeries k f := by
    ext n
    simp only [coeff_hasseSeries,coeff_C_mul]
    ring
  unfold rjet
  rw [h,reval_C_mul (restricted_hasseSeries hf k)]

lemma rjet_one_polynomial (p : Polynomial D) (x : D) :
    rjet 1 (p:Series) x=p.derivative.eval x := by
  unfold rjet
  rw [hasseSeries_one_eq_derivative,PowerSeries.derivative_coe,reval_polynomial]

/-- Analytic differentiation commutes with the constructed nonzero-constant source shift. -/
lemma sourceShift_rjet_one (a x : D) :
    rjet 1 (sourceShift a) x=rjet 1 eulerSource (x+a) := by
  have he : qeval (sourceShift a) =ᶠ[𝓝 (x:ℚ_[2])]
      (fun y : ℚ_[2] => qeval eulerSource (y+(a:ℚ_[2]))) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro z
    rw [← coe_reval (sourceShift_restricted a) z,sourceShift_reval]
    simpa only [PadicInt.coe_add] using coe_reval eulerSource_restricted (z+a)
  have hs := hasDerivAt_qeval eulerSource_restricted (x+a)
  simp only [PadicInt.coe_add] at hs
  have hd : HasDerivAt (fun y : ℚ_[2] => qeval eulerSource (y+(a:ℚ_[2])))
      (rjet 1 eulerSource (x+a):ℚ_[2]) (x:ℚ_[2]) := by
    convert hs.comp (x:ℚ_[2]) ((hasDerivAt_id (x:ℚ_[2])).add_const (a:ℚ_[2])) using 1 <;>
      first | rfl | simp only [mul_one]
  exact Subtype.ext
    ((hasDerivAt_qeval (sourceShift_restricted a) x).unique
      (hd.congr_of_eventuallyEq he))

/-- The explicit skeleton and source derivative channels of one numerator packet. -/
def residualPacketSlope (r q : ℕ) (x : D) : D :=
  residualNumeratorTap r q *
    ((eulerPacket q).derivative.eval x*reval eulerSource (x-(q:D))+
      (eulerPacket q).eval x*rjet 1 eulerSource (x-(q:D)))

lemma residualPacket_rjet_one (r q : ℕ) (x : D) :
    rjet 1 (residualPacketSeries r q) x=residualPacketSlope r q x := by
  rw [residualPacketSeries,rjet_C_mul
    (PowerSeries.isRestricted.mul 1 (polynomial_restricted _) (sourceShift_restricted _)),
    rjet_one_mul (polynomial_restricted _) (sourceShift_restricted _),
    rjet_one_polynomial,reval_polynomial,sourceShift_reval,sourceShift_rjet_one]
  simp only [residualPacketSlope,sub_eq_add_neg]

/-- The actual qth packet of H_r, as a function of the dyadic row argument. -/
def eulerPacketFunction (r q : ℕ) (x : ℚ_[2]) : ℚ_[2] :=
  (eulerBeta r:ℚ_[2])⁻¹*qeval (residualPacketSeries r q) x

lemma eulerPacketFunction_value (r q : ℕ) (x : D) :
    eulerPacketFunction r q (x:ℚ_[2])=
      (residualNumeratorTap r q:ℚ_[2])/(eulerBeta r:ℚ_[2])*
        (((eulerPacket q).eval x:D):ℚ_[2])*(reval eulerSource (x-(q:D)):ℚ_[2]) := by
  rw [eulerPacketFunction,← coe_reval (residualPacketSeries_restricted r q) x,
    residualPacketSeries_reval]
  push_cast
  ring

lemma eulerPacketFunction_hasDerivAt (r q : ℕ) (x : D) :
    HasDerivAt (eulerPacketFunction r q)
      ((residualPacketSlope r q x:ℚ_[2])/(eulerBeta r:ℚ_[2])) (x:ℚ_[2]) := by
  have h := (hasDerivAt_qeval (residualPacketSeries_restricted r q) x).const_mul
    ((eulerBeta r:ℚ_[2])⁻¹)
  rw [residualPacket_rjet_one] at h
  convert h using 1 <;> first | rfl | ring

/-- Ordinary product-rule derivative, preserving the two packet channels. -/
theorem eulerPacketFunction_deriv_channels (r q : ℕ) (x : D) :
    deriv (eulerPacketFunction r q) (x:ℚ_[2])=
      (residualNumeratorTap r q:ℚ_[2])/(eulerBeta r:ℚ_[2])*
        ((((eulerPacket q).derivative.eval x:D):ℚ_[2])*
          (reval eulerSource (x-(q:D)):ℚ_[2])+
        (((eulerPacket q).eval x:D):ℚ_[2])*
          deriv (qeval eulerSource) ((x:ℚ_[2])-(q:ℚ_[2]))) := by
  rw [(eulerPacketFunction_hasDerivAt r q x).deriv]
  have hs := deriv_qeval eulerSource_restricted (x-(q:D))
  simp only [PadicInt.coe_sub,PadicInt.coe_natCast] at hs
  rw [hs,residualPacketSlope]
  push_cast
  ring

lemma eulerResidual_eq_scaled (r : ℕ) :
    eulerResidual r=(fun x : ℚ_[2] => (eulerBeta r:ℚ_[2])⁻¹*qeval (eulerResidualNumerator r) x) := by
  funext x
  simp only [eulerResidual,div_eq_mul_inv,mul_comm]

lemma eulerPacketFunction_iteratedDeriv (r q k : ℕ) (x : D) :
    iteratedDeriv k (eulerPacketFunction r q) (x:ℚ_[2])=
      (eulerBeta r:ℚ_[2])⁻¹*(k.factorial:ℚ_[2])*
        (rjet k (residualPacketSeries r q) x:ℚ_[2]) :=
  iteratedDeriv_scaled_qeval (residualPacketSeries_restricted r q) _ k x

lemma eulerResidual_iteratedDeriv (r k : ℕ) (x : D) :
    iteratedDeriv k (eulerResidual r) (x:ℚ_[2])=
      (eulerBeta r:ℚ_[2])⁻¹*(k.factorial:ℚ_[2])*
        (rjet k (eulerResidualNumerator r) x:ℚ_[2]) := by
  rw [eulerResidual_eq_scaled]
  exact iteratedDeriv_scaled_qeval (eulerResidualNumerator_restricted r) _ k x

lemma eulerPacketFunction_iteratedDeriv_summable (r k : ℕ) (x : D) :
    Summable (fun q => iteratedDeriv k (eulerPacketFunction r q) (x:ℚ_[2])) := by
  simp_rw [eulerPacketFunction_iteratedDeriv]
  exact (summable_coe_dyadic (residualPacket_rjet_summable r k x)).mul_left _

/-- ALL ordinary analytic derivatives commute with the original infinite Euler packet sum. -/
theorem eulerResidual_iteratedDeriv_packet_sum (r k : ℕ) (x : D) :
    iteratedDeriv k (eulerResidual r) (x:ℚ_[2])=
      ∑' q, iteratedDeriv k (eulerPacketFunction r q) (x:ℚ_[2]) := by
  rw [eulerResidual_iteratedDeriv,eulerResidualNumerator_rjet_sum,
    coe_tsum_dyadic (residualPacket_rjet_summable r k x)]
  simp_rw [eulerPacketFunction_iteratedDeriv]
  exact ((summable_coe_dyadic (residualPacket_rjet_summable r k x)).tsum_mul_left _).symm

/-- The first derivative is the convergent sum of the ordinary packet derivatives. -/
theorem eulerResidual_deriv_packet_sum (r : ℕ) (x : D) :
    deriv (eulerResidual r) (x:ℚ_[2])=
      ∑' q, deriv (eulerPacketFunction r q) (x:ℚ_[2]) := by
  simpa only [iteratedDeriv_one] using eulerResidual_iteratedDeriv_packet_sum r 1 x

/-- The explicit slope channel sum, including all packets beyond an integer row. -/
theorem eulerResidual_deriv_slope_sum (r : ℕ) (x : D) :
    deriv (eulerResidual r) (x:ℚ_[2])=
      (∑' q, (residualPacketSlope r q x:ℚ_[2]))/(eulerBeta r:ℚ_[2]) := by
  rw [eulerResidual_deriv,eulerResidualNumerator_rjet_sum]
  simp_rw [residualPacket_rjet_one]
  congr 1
  exact coe_tsum_dyadic (by
    simpa only [residualPacket_rjet_one] using residualPacket_rjet_summable r 1 x)

end Komorebi.Euler
