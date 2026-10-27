module
public import Euler.ResidualNormalization
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The actual normalized packet scalar in the integral coefficient ring. -/
def normalizedResidualScalarInt (r : ℕ) (hr : 0<r) (q : ℕ) : D :=
  ⟨normalizedResidualScalar r q,normalizedResidualScalar_norm_le_one r q hr⟩

lemma normalizedResidualScalarInt_norm (r : ℕ) (hr : 0<r) (q : ℕ) :
    ‖normalizedResidualScalarInt r hr q‖=
      (2:ℝ)^(-(residualCarryCost r q-residualCarryMinimum r)) := by
  change ‖normalizedResidualScalar r q‖=_
  rw [Padic.norm_eq_zpow_neg_valuation (normalizedResidualScalar_ne_zero r q),
    normalizedResidualScalar_val r q hr]
  norm_num

lemma normalizedResidualScalarInt_red (r : ℕ) (hr : 0<r) (q : ℕ) :
    red (normalizedResidualScalarInt r hr q)=
      if residualCarryCost r q=residualCarryMinimum r then 1 else 0 := by
  by_cases h : residualCarryCost r q=residualCarryMinimum r
  · rw [ite_eq_left h]
    apply red_not_zero_eq_one
    intro hz
    have hn := (red_zero_iff_norm_lt_one _).mp hz
    rw [normalizedResidualScalarInt_norm,h,sub_self,neg_zero,zpow_zero] at hn
    exact (lt_irrefl 1) hn
  · rw [ite_eq_right h]
    apply (red_zero_iff_norm_lt_one _).mpr
    rw [normalizedResidualScalarInt_norm]
    have hc := residualCarryMinimum_le r q hr
    have hp : -(residualCarryCost r q-residualCarryMinimum r)<0 := by omega
    exact (zpow_lt_zpow_right₀ (by norm_num : (1:ℝ)<2) hp).trans_eq (zpow_zero _)

def normalizedResidualPacket (r : ℕ) (hr : 0<r) (q : ℕ) : Series :=
  C (normalizedResidualScalarInt r hr q)*((eulerPacket q:Series)*sourceShift (-(q:D)))

lemma normalizedResidualPacket_coeff_coe (r : ℕ) (hr : 0<r) (q n : ℕ) :
    ((coeff n (normalizedResidualPacket r hr q):D):ℚ_[2])=
      residualNormalizationFactor r*((coeff n (residualPacketSeries r q):D):ℚ_[2]) := by
  rw [normalizedResidualPacket,coeff_C_mul,PadicInt.coe_mul]
  exact (residualNormalizationFactor_packet r q n).symm

lemma normalizedResidualPacket_summable (r : ℕ) (hr : 0<r) (n : ℕ) :
    Summable (fun q => coeff n (normalizedResidualPacket r hr q)) := by
  have hs := (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
    (by norm_num : (1/8:ℝ)<1)).mul_left ‖residualNormalizationFactor r‖
  apply hs.of_norm_bounded
  intro q
  rw [PadicInt.norm_def,normalizedResidualPacket_coeff_coe,norm_mul,← PadicInt.norm_def]
  exact mul_le_mul_of_nonneg_left (residualPacketSeries_coeff_uniform r q n) (norm_nonneg _)

lemma eulerNormalizedResidual_coeff_sum (r : ℕ) (hr : 0<r) (n : ℕ) :
    coeff n (eulerNormalizedResidual r hr)=
      ∑'q, coeff n (normalizedResidualPacket r hr q) := by
  apply Subtype.ext
  rw [eulerNormalizedResidual_coeff_coe]
  have h1 := ((residualPacketSeries_summable_coeff r n).hasSum.map
    (PadicInt.Coe.ringHom : D →+* ℚ_[2]) PadicInt.isOpenEmbedding_coe.continuous).mul_left
      (residualNormalizationFactor r)
  change HasSum (fun q => residualNormalizationFactor r*
    ((coeff n (residualPacketSeries r q):D):ℚ_[2]))
    (residualNormalizationFactor r*((∑'q, coeff n (residualPacketSeries r q):D):ℚ_[2])) at h1
  have h2 := (normalizedResidualPacket_summable r hr n).hasSum.map
    (PadicInt.Coe.ringHom : D →+* ℚ_[2]) PadicInt.isOpenEmbedding_coe.continuous
  change HasSum (fun q => ((coeff n (normalizedResidualPacket r hr q):D):ℚ_[2]))
    ((∑'q, coeff n (normalizedResidualPacket r hr q):D):ℚ_[2]) at h2
  simp_rw [normalizedResidualPacket_coeff_coe] at h2
  simpa only [coeff_eulerResidualNumerator] using h1.unique h2

/-- Reduction of an actual analytic source translation; no substitution in a formal variable. -/
lemma sourceShift_red (a : D) : PowerSeries.map red (sourceShift a)=1 := by
  ext n
  rw [coeff_map,coeff_one]
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · rw [ite_eq_left rfl]
    have hval : coeff 0 (sourceShift a)=reval eulerSource a := by
      have h := sourceShift_reval a 0
      have hz : reval (sourceShift a) 0=coeff 0 (sourceShift a) := by
        unfold reval
        rw [tsum_eq_single 0 (fun n hn => by rw [zero_pow hn,mul_zero])]
        simp
      simpa only [hz,zero_add] using h
    rw [hval,eulerSource_reval_red]
  · rw [ite_eq_right (by omega),sourceShift_coeff_two,map_mul,map_pow,red_two,
      zero_pow (by omega),zero_mul]

lemma eulerPacket_red (q : ℕ) :
    (eulerPacket q).map red=descPochhammer F₂ q := by
  induction q with
  | zero => simp
  | succ q ih =>
    rw [eulerPacket_succ,Polynomial.map_mul,Polynomial.map_mul,ih,
      descPochhammer_succ_right]
    have hu : (Polynomial.C (2:D)*Polynomial.X-Polynomial.C ((2*q+1:ℕ):D)).map red=1 := by
      have hq : red ((2*q+1:ℕ):D)=1 := by
        push_cast
        rw [map_add,map_mul,red_two,map_one,zero_mul,zero_add]
      rw [Polynomial.map_sub,Polynomial.map_mul,Polynomial.map_C,Polynomial.map_X,
        Polynomial.map_C,red_two,hq]
      norm_num only [Polynomial.C_0,zero_mul,zero_sub,Polynomial.C_1]
      have hn : (-1:F₂)=1 := by decide
      simpa only [Polynomial.C_neg,Polynomial.C_1] using
        congrArg (Polynomial.C : F₂ →+* Polynomial F₂) hn
    rw [hu,mul_one]
    simp

/-- Each normalized packet reduces either to its falling factorial or to zero. -/
lemma normalizedResidualPacket_red (r : ℕ) (hr : 0<r) (q : ℕ) :
    PowerSeries.map red (normalizedResidualPacket r hr q)=
      if residualCarryCost r q=residualCarryMinimum r
      then (descPochhammer F₂ q:PowerSeries F₂) else 0 := by
  rw [normalizedResidualPacket,map_mul,map_mul,map_C,sourceShift_red,mul_one,
    normalizedResidualScalarInt_red]
  have hp : PowerSeries.map red (eulerPacket q:Series)=
      (descPochhammer F₂ q:PowerSeries F₂) := by
    rw [← eulerPacket_red]
    ext n
    simp
  rw [hp]
  split <;> simp_all

/-- The complete residue polynomial of the actual infinite normalized Euler residual. -/
theorem eulerNormalizedResidual_red_coeff (r : ℕ) (hr : 0<r) (n : ℕ) :
    red (coeff n (eulerNormalizedResidual r hr))=
      ∑ q ∈ residualMinimizers r, (descPochhammer F₂ q).coeff n := by
  rw [eulerNormalizedResidual_coeff_sum]
  have h := (normalizedResidualPacket_summable r hr n).hasSum.map red
    (by
      have hc := continuous_redPow 1
      change Continuous res at hc
      have hfun : (res : D → F₂)=(red : D → F₂) := funext res_eq_red
      rw [hfun] at hc
      exact hc)
  change HasSum (fun q => red (coeff n (normalizedResidualPacket r hr q)))
    (red (∑'q, coeff n (normalizedResidualPacket r hr q))) at h
  have he (q:ℕ) : red (coeff n (normalizedResidualPacket r hr q))=
      if q∈residualMinimizers r then (descPochhammer F₂ q).coeff n else 0 := by
    rw [← coeff_map,normalizedResidualPacket_red]
    simp only [mem_residualMinimizers_iff r q hr]
    split <;> simp
  simp_rw [he] at h
  rw [← h.tsum_eq]
  classical
  calc
    _ = ∑ q ∈ residualMinimizers r,
        (if q∈residualMinimizers r then (descPochhammer F₂ q).coeff n else 0) :=
      tsum_eq_sum (fun q hq => ite_eq_right hq)
    _ = _ := Finset.sum_congr rfl (fun q hq => ite_eq_left hq)

/-- The last minimizing carry really is the last odd Taylor coefficient of G_r. -/
theorem eulerNormalizedResidual_lastOdd (r : ℕ) (hr : 0<r) :
    LastOdd (eulerNormalizedResidual r hr) (residualTerminalIndex r) := by
  constructor
  · rw [eulerNormalizedResidual_red_coeff]
    classical
    rw [Finset.sum_eq_single (residualTerminalIndex r)]
    · have h := (monic_descPochhammer F₂ (residualTerminalIndex r)).coeff_natDegree
      simpa only [descPochhammer_natDegree] using h
    · intro q hq hne
      have hle := Finset.le_max' (residualMinimizers r) q hq
      change q≤residualTerminalIndex r at hle
      exact Polynomial.coeff_eq_zero_of_natDegree_lt (by rw [descPochhammer_natDegree]; omega)
    · intro hnot
      exact False.elim (hnot (residualTerminalIndex_mem r))
  · intro n hn
    rw [eulerNormalizedResidual_red_coeff]
    apply Finset.sum_eq_zero
    intro q hq
    have hle := Finset.le_max' (residualMinimizers r) q hq
    change q≤residualTerminalIndex r at hle
    exact Polynomial.coeff_eq_zero_of_natDegree_lt (by rw [descPochhammer_natDegree]; omega)

/-- G_r is nonzero and its normalization has unit coefficient content. -/
theorem eulerNormalizedResidual_ne_zero (r : ℕ) (hr : 0<r) :
    eulerNormalizedResidual r hr≠0 := by
  intro hz
  have h := (eulerNormalizedResidual_lastOdd r hr).1
  rw [hz,map_zero,map_zero] at h
  norm_num at h

end Komorebi.Euler
