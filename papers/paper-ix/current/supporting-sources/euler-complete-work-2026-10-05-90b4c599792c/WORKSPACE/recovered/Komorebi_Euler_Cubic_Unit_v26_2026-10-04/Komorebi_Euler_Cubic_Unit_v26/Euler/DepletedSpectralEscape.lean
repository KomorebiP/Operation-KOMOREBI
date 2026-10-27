module
public import Euler.ResidualPacketJets
public import Euler.ResidualCarry
public import Euler.UndepletionAlgebra
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Actual depleted beta in the dyadic integers, for positive residual indices. -/
def depletedBetaIntegral (r : ℕ) : D :=
  (1-(2:D)^(2*r-1))*eulerBeta r

lemma depletedBetaIntegral_norm (r : ℕ) (hr : 0<r) :
    ‖depletedBetaIntegral r‖=‖eulerBeta r‖ := by
  have hu : ‖(1-(2:D)^(2*r-1))‖=1 := by
    apply red_ne_zero_norm_one
    simp [show 2*r-1≠0 by omega]
  rw [depletedBetaIntegral,norm_mul,hu,one_mul]

/-- Actual numerator packet with depletion and m additional spectral dilations. -/
def depletedSpectralPacket (r m q : ℕ) (x : D) : D :=
  (4:D)^(m*q)*(1-(2:D)^(2*(r+q)-1))*
    reval (residualPacketSeries r q) x

lemma depletedSpectralPacket_bound (r m q : ℕ) (x : D) :
    ‖depletedSpectralPacket r m q x‖≤(1/2:ℝ)^((2*m+3)*q) := by
  have h4 : ‖(4:D)‖=(1/4:ℝ) := by
    have h := PadicInt.norm_p_pow (p:=2) 2
    norm_num at h ⊢
    exact h
  have hp : ‖reval (residualPacketSeries r q) x‖≤(1/8:ℝ)^q := by
    simpa using residualPacket_rjet_norm r q 0 x
  unfold depletedSpectralPacket
  rw [norm_mul,norm_mul,norm_pow,h4]
  calc
    _ ≤ (1/4:ℝ)^(m*q)*(1/8:ℝ)^q := by
      apply mul_le_mul
      · exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)
      · exact hp
      · positivity
      · positivity
    _ = (1/2:ℝ)^((2*m+3)*q) := by
      calc
        _ = ((1/2:ℝ)^2)^(m*q)*((1/2:ℝ)^3)^q := by norm_num
        _ = _ := by
          rw [← pow_mul, ← pow_mul, ← pow_add]
          congr 1
          ring

lemma depletedSpectralPacket_summable (r m : ℕ) (x : D) :
    Summable (fun q => depletedSpectralPacket r m q x) := by
  apply (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
    (by norm_num : (1/8:ℝ)<1)).of_norm_bounded
  intro q
  calc
    _ ≤ (1/2:ℝ)^((2*m+3)*q) := depletedSpectralPacket_bound r m q x
    _ ≤ (1/2:ℝ)^(3*q) :=
      pow_le_pow_of_le_one (by norm_num) (by norm_num) (by nlinarith)
    _ = (1/8:ℝ)^q := by rw [pow_mul]; norm_num

lemma depletedSpectralPacket_head (r m : ℕ) (x : D) :
    depletedSpectralPacket r m 0 x =
      depletedBetaIntegral r*reval eulerSource x := by
  simp [depletedSpectralPacket,residualPacketSeries_reval,
    residualNumeratorTap,eulerPacket_zero,depletedBetaIntegral,mul_assoc]

/-- The packet sum is convergent; no finite-face approximation is used. -/
def depletedSpectralNumerator (r m : ℕ) (x : D) : D :=
  ∑' q, depletedSpectralPacket r m q x

lemma depletedSpectralNumerator_head_tail (r m : ℕ) (x : D) :
    depletedSpectralNumerator r m x =
      depletedBetaIntegral r*reval eulerSource x +
      ∑' q, depletedSpectralPacket r m (q+1) x := by
  have h := (depletedSpectralPacket_summable r m x).sum_add_tsum_nat_add 1
  simp only [Finset.sum_range_one,depletedSpectralPacket_head] at h
  exact h.symm

lemma depletedSpectralTail_bound (r m : ℕ) (x : D) :
    ‖∑' q, depletedSpectralPacket r m (q+1) x‖≤(1/2:ℝ)^(2*m+3) := by
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro q
  exact (depletedSpectralPacket_bound r m (q+1) x).trans
    (pow_le_pow_of_le_one (by norm_num) (by norm_num) (by nlinarith))

/-- Once the dilated tail is below the fixed source, the whole numerator has the source norm. -/
theorem depletedSpectralNumerator_norm (r m : ℕ) (hr : 0<r)
    (hcut : binaryDigitSum r≤2*m+3) (x : D) :
    ‖depletedSpectralNumerator r m x‖=‖eulerBeta r‖ := by
  have hhead : ‖depletedBetaIntegral r*reval eulerSource x‖=‖eulerBeta r‖ := by
    rw [norm_mul,depletedBetaIntegral_norm r hr,eulerSource_norm_one,mul_one]
  have hsmall : ‖∑' q, depletedSpectralPacket r m (q+1) x‖ < ‖eulerBeta r‖ := by
    apply (depletedSpectralTail_bound r m x).trans_lt
    rw [eulerBeta_norm r hr]
    have he : (1/2:ℝ)^(2*m+3)=(2:ℝ)^(-((2*m+3:ℕ):ℤ)) := by
      rw [zpow_neg,zpow_natCast]
      simp
    rw [he]
    exact zpow_lt_zpow_right₀ (by norm_num : (1:ℝ)<2) (by omega)
  have hfield :
      ‖(depletedSpectralNumerator r m x:ℚ_[2])-
        (depletedBetaIntegral r*reval eulerSource x: D)‖ <
      ‖((depletedBetaIntegral r*reval eulerSource x:D):ℚ_[2])‖ := by
    have hd : ‖depletedSpectralNumerator r m x-
        depletedBetaIntegral r*reval eulerSource x‖ <
        ‖depletedBetaIntegral r*reval eulerSource x‖ := by
      rw [depletedSpectralNumerator_head_tail,add_sub_cancel_left,hhead]
      exact hsmall
    simpa only [PadicInt.norm_def, PadicInt.coe_sub] using hd
  have hnorm := Padic.norm_eq_of_norm_sub_lt_right hfield
  simpa only [← PadicInt.norm_def,hhead] using hnorm

/-- This is the packet-dilated DEPLETED residual; it is not the actual undepleted residual. -/
def depletedSpectralValue (r m : ℕ) (x : D) : ℚ_[2] :=
  (depletedSpectralNumerator r m x:ℚ_[2])/(depletedBetaIntegral r:ℚ_[2])

theorem depletedSpectralValue_unit (r m : ℕ) (hr : 0<r)
    (hcut : binaryDigitSum r≤2*m+3) (x : D) :
    ‖depletedSpectralValue r m x‖=1 := by
  unfold depletedSpectralValue
  rw [norm_div]
  change ‖depletedSpectralNumerator r m x‖/‖depletedBetaIntegral r‖=1
  rw [depletedSpectralNumerator_norm r m hr hcut x,depletedBetaIntegral_norm r hr]
  exact div_self (norm_ne_zero_iff.mpr (eulerBeta_ne_zero r))

/-- A finite all-r spectral escape bound, including the infinite tail. -/
theorem depletedSpectralValue_escape (r : ℕ) (hr : 0<r) (x : D) :
    ‖depletedSpectralValue r ((binaryDigitSum r-2)/2) x‖=1 := by
  apply depletedSpectralValue_unit r _ hr _ x
  omega

/-- A zero of the depleted residual must be detected by at least one of these
finitely many spectral value corrections, even with infinitely many packets.
This does NOT assert that the corresponding epsilon-weighted sum is nonzero. -/
theorem depletedSpectral_correction_detects_zero (r : ℕ) (hr : 0<r) (x : D)
    (hzero : depletedSpectralValue r 0 x=0) :
    ∃ m < (binaryDigitSum r-2)/2,
      depletedSpectralValue r (m+1) x ≠ depletedSpectralValue r m x := by
  by_contra h
  push Not at h
  have hall : ∀ m : ℕ, m≤(binaryDigitSum r-2)/2 →
      depletedSpectralValue r m x=depletedSpectralValue r 0 x := by
    intro m hm
    induction m with
    | zero => rfl
    | succ m ih =>
        rw [h m (by omega), ih (by omega)]
  have hu := depletedSpectralValue_escape r hr x
  rw [hall _ (by omega),hzero,norm_zero] at hu
  norm_num at hu

end Komorebi.Euler
