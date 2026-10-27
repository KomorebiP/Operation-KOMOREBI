module
public import Euler.ResidualSeries
public import Euler.EulerError
public import Mathlib.Analysis.Calculus.Deriv.Mul
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The genuine unnormalized row residual as a function on Q_2. -/
def eulerResidual (r : ℕ) (x : ℚ_[2]) : ℚ_[2] :=
  qeval (eulerResidualNumerator r) x / (eulerBeta r:ℚ_[2])

/-- Its Taylor series over Q_2; no false integrality assertion is made for H_r. -/
def eulerResidualSeries (r : ℕ) : PowerSeries ℚ_[2] :=
  C ((eulerBeta r:ℚ_[2])⁻¹) *
    PowerSeries.map (PadicInt.Coe.ringHom : D →+* ℚ_[2]) (eulerResidualNumerator r)

lemma eulerResidualSeries_coeff (r n : ℕ) :
    coeff n (eulerResidualSeries r) =
      ((coeff n (eulerResidualNumerator r):D):ℚ_[2])/(eulerBeta r:ℚ_[2]) := by
  simp only [eulerResidualSeries,coeff_C_mul,coeff_map]
  change _ = _ * (eulerBeta r:ℚ_[2])⁻¹
  exact mul_comm _ _

lemma eulerResidualSeries_restricted (r : ℕ) :
    PowerSeries.IsRestricted 1 (eulerResidualSeries r) := by
  rw [PowerSeries.isRestricted_iff']
  simp only [one_pow,mul_one,eulerResidualSeries_coeff,norm_div]
  have hn := (restricted_iff _).mp (eulerResidualNumerator_restricted r)
  convert hn.div_const ‖(eulerBeta r:ℚ_[2])‖ using 1 <;> simp

lemma eulerResidual_eq_series (r : ℕ) (x : ℚ_[2]) :
    eulerResidual r x=∑' n, coeff n (eulerResidualSeries r)*x^n := by
  simp_rw [eulerResidualSeries_coeff,div_mul_eq_mul_div]
  rw [tsum_div_const]
  rfl

lemma eulerResidual_coe (r : ℕ) (x : D) :
    eulerResidual r (x:ℚ_[2])=(reval (eulerResidualNumerator r) x:ℚ_[2])/(eulerBeta r:ℚ_[2]) := by
  rw [eulerResidual,coe_reval (eulerResidualNumerator_restricted r) x]

lemma eulerResidual_beta_mul (r : ℕ) (x : D) :
    (eulerBeta r:ℚ_[2])*eulerResidual r (x:ℚ_[2])=
      (reval (eulerResidualNumerator r) x:ℚ_[2]) := by
  rw [eulerResidual,← coe_reval (eulerResidualNumerator_restricted r) x]
  exact mul_div_cancel₀ _ ((PadicInt.coe_eq_zero).not.mpr (eulerBeta_ne_zero r))

lemma eulerResidual_hasDerivAt (r : ℕ) (x : D) :
    HasDerivAt (eulerResidual r)
      ((rjet 1 (eulerResidualNumerator r) x:ℚ_[2])/(eulerBeta r:ℚ_[2])) (x:ℚ_[2]) := by
  exact (hasDerivAt_qeval (eulerResidualNumerator_restricted r) x).div_const _

lemma eulerResidual_deriv (r : ℕ) (x : D) :
    deriv (eulerResidual r) (x:ℚ_[2]) =
      (rjet 1 (eulerResidualNumerator r) x:ℚ_[2])/(eulerBeta r:ℚ_[2]) :=
  (eulerResidual_hasDerivAt r x).deriv

/-- The original infinite packet formula for H_r is an equality of convergent sums. -/
theorem eulerResidual_packet_sum (r : ℕ) (x : D) :
    eulerResidual r (x:ℚ_[2]) =
      ∑' q, ((8:ℚ_[2])^q*(eulerBeta (r+q):ℚ_[2])/(eulerBeta r:ℚ_[2])) *
        (((eulerPacket q).eval x:D):ℚ_[2]) * (reval eulerSource (x-(q:D)):ℚ_[2]) := by
  rw [eulerResidual,← coe_reval (eulerResidualNumerator_restricted r) x,
    eulerResidualNumerator_reval]
  have hs : Summable (fun q => residualNumeratorTap r q*(eulerPacket q).eval x*
      reval eulerSource (x-(q:D))) := by
    apply (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
      (by norm_num : (1/8:ℝ)<1)).of_norm_bounded
    intro q
    calc
      _ = ‖residualNumeratorTap r q*((eulerPacket q).eval x*reval eulerSource (x-(q:D)))‖ := by congr 1; ring
      _ ≤ ‖residualNumeratorTap r q‖ := by
        rw [norm_mul]
        exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)
      _ ≤ _ := residualNumeratorTap_norm r q
  have hh := hs.hasSum.map (PadicInt.Coe.ringHom : D →+* ℚ_[2])
    PadicInt.isOpenEmbedding_coe.continuous
  change HasSum (fun q => ((residualNumeratorTap r q*(eulerPacket q).eval x*
    reval eulerSource (x-(q:D)):D):ℚ_[2]))
    (((∑' q, residualNumeratorTap r q*(eulerPacket q).eval x*
      reval eulerSource (x-(q:D))):D):ℚ_[2]) at hh
  rw [← hh.tsum_eq,← tsum_div_const]
  apply tsum_congr
  intro q
  simp only [PadicInt.coe_mul,residualNumeratorTap,
    PadicInt.coe_pow]
  change ((8:ℚ_[2])^q*(eulerBeta (r+q):ℚ_[2])*
    (((eulerPacket q).eval x:D):ℚ_[2])*(reval eulerSource (x-(q:D)):ℚ_[2])) /
    (eulerBeta r:ℚ_[2]) = _
  ring

lemma eulerResidualNumerator_zero (r : ℕ) :
    reval (eulerResidualNumerator r) 0=eulerBeta r := by
  simpa [residualNumeratorTap,eulerPacket_zero,eulerSource_at_zero] using
    eulerResidualNumerator_reval_nat r 0

@[simp] theorem eulerResidual_at_zero (r : ℕ) : eulerResidual r 0=1 := by
  change eulerResidual r ((0:D):ℚ_[2])=1
  rw [eulerResidual_coe,eulerResidualNumerator_zero]
  exact div_self ((PadicInt.coe_eq_zero).not.mpr (eulerBeta_ne_zero r))

/-- Exact finite evaluation at every original integer offset. -/
theorem eulerResidual_reval_nat (r n : ℕ) :
    eulerResidual r (n:ℚ_[2]) =
      (∑ q ∈ Finset.range (n+1),
        residualNumeratorTap r q*(eulerPacket q).eval (n:D)*
          reval eulerSource ((n:D)-(q:D)) : D) / (eulerBeta r:ℚ_[2]) := by
  have h := eulerResidual_coe r (n:D)
  rw [eulerResidualNumerator_reval_nat] at h
  simpa only [PadicInt.coe_natCast] using h

end Komorebi.Euler
