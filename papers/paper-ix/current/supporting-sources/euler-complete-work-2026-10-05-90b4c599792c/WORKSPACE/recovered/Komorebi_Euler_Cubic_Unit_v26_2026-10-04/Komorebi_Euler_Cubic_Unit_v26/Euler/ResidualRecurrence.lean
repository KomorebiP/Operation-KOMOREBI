module
public import Euler.ResidualTruncation
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- One actually evaluated numerator packet on the dyadic unit disc. -/
def residualPacketValue (r q : ℕ) (x : D) : D :=
  residualNumeratorTap r q*(eulerPacket q).eval x*reval eulerSource (x-(q:D))

lemma residualPacketValue_norm (r q : ℕ) (x : D) :
    ‖residualPacketValue r q x‖≤(1/8:ℝ)^q := by
  unfold residualPacketValue
  rw [mul_assoc,norm_mul]
  exact (mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (residualNumeratorTap_norm r q)

lemma residualPacketValue_summable (r : ℕ) (x : D) :
    Summable (fun q => residualPacketValue r q x) := by
  exact (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
    (by norm_num : (1/8:ℝ)<1)).of_norm_bounded (residualPacketValue_norm r · x)

lemma residualPacketValue_add (r a q : ℕ) (x : D) :
    residualPacketValue r (q+a) x=
      (8:D)^a*(eulerPacket a).eval x*residualPacketValue (r+a) q (x-(a:D)) := by
  unfold residualPacketValue residualNumeratorTap
  rw [show q+a=a+q by omega,eulerPacket_block,pow_add]
  rw [show r+(a+q)=r+a+q by omega]
  push_cast
  rw [show x-((a:D)+(q:D))=(x-(a:D))-(q:D) by ring]
  ring

@[simp] lemma residualPacketValue_zero (r : ℕ) (x : D) :
    residualPacketValue r 0 x=eulerBeta r*reval eulerSource x := by
  simp [residualPacketValue,residualNumeratorTap]

/-- Exact block transport of the entire convergent numerator, not a finite approximation. -/
theorem eulerResidualNumerator_block (r a : ℕ) (x : D) :
    reval (eulerResidualNumerator r) x=
      (∑ q ∈ Finset.range a, residualPacketValue r q x)+
      (8:D)^a*(eulerPacket a).eval x*
        reval (eulerResidualNumerator (r+a)) (x-(a:D)) := by
  rw [eulerResidualNumerator_reval r x]
  change (∑'q, residualPacketValue r q x)=_
  rw [← (residualPacketValue_summable r x).sum_add_tsum_nat_add a]
  simp_rw [residualPacketValue_add]
  rw [(residualPacketValue_summable (r+a) (x-(a:D))).tsum_mul_left]
  rw [eulerResidualNumerator_reval]
  rfl

/-- First-order numerator recursion with the source and packet polynomial retained exactly. -/
theorem eulerResidualNumerator_succ (r : ℕ) (x : D) :
    reval (eulerResidualNumerator r) x=
      eulerBeta r*reval eulerSource x+
      8*x*(2*x-1)*reval (eulerResidualNumerator (r+1)) (x-1) := by
  have hp : (eulerPacket 1).eval x=x*(2*x-1) := by
    simp [eulerPacket_succ]
  simpa only [Finset.sum_range_one,residualPacketValue_zero,pow_one,hp,
    Nat.cast_one,mul_assoc] using eulerResidualNumerator_block r 1 x

/-- The original H_r recursion, now for the actually constructed infinite residual. -/
theorem eulerResidual_succ (r : ℕ) (x : D) :
    eulerResidual r (x:ℚ_[2])=
      (reval eulerSource x:ℚ_[2])+
      8*(eulerBeta (r+1):ℚ_[2])/(eulerBeta r:ℚ_[2])*
        (x:ℚ_[2])*(2*(x:ℚ_[2])-1)*eulerResidual (r+1) ((x:ℚ_[2])-1) := by
  have h := congrArg (fun z:D => (z:ℚ_[2])) (eulerResidualNumerator_succ r x)
  simp only [PadicInt.coe_add,PadicInt.coe_mul,PadicInt.coe_sub,
    PadicInt.coe_one] at h
  rw [← eulerResidual_beta_mul r x] at h
  have hnext := eulerResidual_beta_mul (r+1) (x-1)
  simp only [PadicInt.coe_sub,PadicInt.coe_one] at hnext
  rw [← hnext] at h
  change (eulerBeta r:ℚ_[2])*eulerResidual r (x:ℚ_[2])=
    (eulerBeta r:ℚ_[2])*(reval eulerSource x:ℚ_[2])+
    8*(x:ℚ_[2])*(2*(x:ℚ_[2])-1)*
      ((eulerBeta (r+1):ℚ_[2])*eulerResidual (r+1) ((x:ℚ_[2])-1)) at h
  have hb : (eulerBeta r:ℚ_[2])≠0 := (PadicInt.coe_eq_zero).not.mpr (eulerBeta_ne_zero r)
  apply (mul_left_cancel₀ hb)
  rw [h]
  field_simp

end Komorebi.Euler
