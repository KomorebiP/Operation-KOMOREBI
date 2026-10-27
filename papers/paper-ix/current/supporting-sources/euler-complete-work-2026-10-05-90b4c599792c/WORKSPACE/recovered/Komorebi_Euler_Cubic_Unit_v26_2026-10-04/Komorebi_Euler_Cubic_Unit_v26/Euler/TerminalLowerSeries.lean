module
public import Euler.TerminalShift
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- The lower-prefix normalization is its OWN minimum, not the full wall minimum. -/
def terminalLowerScalar (r q : ℕ) : ℚ_[2] :=
  (2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))*(residualScalarRat r q:ℚ_[2])

lemma terminalLowerScalar_ne_zero (r q : ℕ) : terminalLowerScalar r q≠0 := by
  apply mul_ne_zero (zpow_ne_zero _ (by norm_num))
  exact_mod_cast residualScalarRat_ne_zero r q

lemma terminalLowerScalar_val (r q : ℕ) (hr : 0<r) (hq : q<residualTerminalIndex r) :
    Padic.valuation (terminalLowerScalar r q)=
      terminalLowerCost (residualTerminalIndex r) q-
        terminalLowerMinimum (residualTerminalIndex r) := by
  have hp : Padic.valuation (2:ℚ_[2])=1 := Padic.valuation_p
  rw [terminalLowerScalar,Padic.valuation_mul (zpow_ne_zero _ (by norm_num))
    (by exact_mod_cast residualScalarRat_ne_zero r q),Padic.valuation_zpow,
    hp,Padic.valuation_ratCast,residualScalarRat_val r q hr,
    residualCarryCost_before_terminal r q hr hq]
  ring

lemma terminalLowerScalar_norm_le_one (r q : ℕ) (hr : 0<r)
    (hq : q<residualTerminalIndex r) : ‖terminalLowerScalar r q‖≤1 := by
  apply (Padic.norm_le_one_iff_val_nonneg _).mpr
  rw [terminalLowerScalar_val r q hr hq]
  exact sub_nonneg.mpr (terminalLowerMinimum_le _ q hq)

def terminalLowerScalarInt (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) : D :=
  ⟨terminalLowerScalar r q,terminalLowerScalar_norm_le_one r q hr q.isLt⟩

lemma terminalLowerScalarInt_red (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) :
    red (terminalLowerScalarInt r hr q)=
      if terminalLowerCost (residualTerminalIndex r) q=terminalLowerMinimum (residualTerminalIndex r)
      then 1 else 0 := by
  have hv := terminalLowerScalar_val r q hr q.isLt
  have hn : ‖terminalLowerScalarInt r hr q‖=
      (2:ℝ)^(-(terminalLowerCost (residualTerminalIndex r) q-
        terminalLowerMinimum (residualTerminalIndex r))) := by
    change ‖terminalLowerScalar r q‖=_
    rw [Padic.norm_eq_zpow_neg_valuation (terminalLowerScalar_ne_zero r q),hv]
    norm_num
  by_cases h : terminalLowerCost (residualTerminalIndex r) q=terminalLowerMinimum (residualTerminalIndex r)
  · rw [ite_eq_left h]
    apply red_not_zero_eq_one
    intro hz
    have hh := (red_zero_iff_norm_lt_one _).mp hz
    rw [hn,h,sub_self,neg_zero,zpow_zero] at hh
    exact (lt_irrefl 1) hh
  · rw [ite_eq_right h]
    apply (red_zero_iff_norm_lt_one _).mpr
    rw [hn]
    have hc := terminalLowerMinimum_le (residualTerminalIndex r) q q.isLt
    have hp : -(terminalLowerCost (residualTerminalIndex r) q-
        terminalLowerMinimum (residualTerminalIndex r))<0 := by omega
    exact (zpow_lt_zpow_right₀ (by norm_num : (1:ℝ)<2) hp).trans_eq (zpow_zero _)

/-- One actual lower packet, including its convergent translated source. -/
def terminalLowerPacket (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) : Series :=
  C (terminalLowerScalarInt r hr q)*((eulerPacket q:Series)*sourceShift (-(q.val:D)))

lemma terminalLowerPacket_restricted (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) :
    Restricted (terminalLowerPacket r hr q) :=
  PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
    (PowerSeries.isRestricted.mul 1 (polynomial_restricted _) (sourceShift_restricted _))

/-- The full finite lower prefix V_r is now a constructed analytic series. -/
def terminalLowerSeries (r : ℕ) (hr : 0<r) : Series :=
  ∑ q:Fin (residualTerminalIndex r),terminalLowerPacket r hr q

lemma restricted_finset_sum {ι : Type*} (s : Finset ι) (f : ι→Series)
    (hf : ∀ i∈s, Restricted (f i)) : Restricted (∑ i∈s,f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using PowerSeries.isRestricted_zero (R:=D) 1
  | @insert a s ha ih =>
    rw [Finset.sum_insert ha]
    exact PowerSeries.isRestricted.add 1 (hf a (Finset.mem_insert_self _ _))
      (ih (fun i hi => hf i (Finset.mem_insert_of_mem hi)))

lemma reval_finset_sum {ι : Type*} (s : Finset ι) (f : ι→Series)
    (hf : ∀ i∈s, Restricted (f i)) (x : D) :
    reval (∑ i∈s,f i) x=∑ i∈s,reval (f i) x := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [reval]
  | @insert a s ha ih =>
    rw [Finset.sum_insert ha,Finset.sum_insert ha]
    rw [reval_add (hf a (Finset.mem_insert_self _ _))
      (restricted_finset_sum s f (fun i hi => hf i (Finset.mem_insert_of_mem hi)))]
    rw [ih (fun i hi => hf i (Finset.mem_insert_of_mem hi))]

lemma terminalLowerSeries_restricted (r : ℕ) (hr : 0<r) :
    Restricted (terminalLowerSeries r hr) :=
  restricted_finset_sum _ _ (fun q _ => terminalLowerPacket_restricted r hr q)

lemma terminalLowerPacket_reval (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) (x : D) :
    reval (terminalLowerPacket r hr q) x=
      terminalLowerScalarInt r hr q*(eulerPacket q).eval x*reval eulerSource (x-(q.val:D)) := by
  rw [terminalLowerPacket,reval_C_mul
    (PowerSeries.isRestricted.mul 1 (polynomial_restricted _) (sourceShift_restricted _)),
    reval_mul (polynomial_restricted _) (sourceShift_restricted _),
    reval_polynomial,sourceShift_reval]
  simp only [sub_eq_add_neg,mul_assoc]

lemma terminalLowerSeries_reval (r : ℕ) (hr : 0<r) (x : D) :
    reval (terminalLowerSeries r hr) x=
      ∑ q:Fin (residualTerminalIndex r),terminalLowerScalarInt r hr q*
        (eulerPacket q).eval x*reval eulerSource (x-(q.val:D)) := by
  rw [terminalLowerSeries,reval_finset_sum _ _ (fun q _ => terminalLowerPacket_restricted r hr q)]
  simp_rw [terminalLowerPacket_reval]

lemma terminalLowerPacket_red (r : ℕ) (hr : 0<r) (q : Fin (residualTerminalIndex r)) :
    PowerSeries.map red (terminalLowerPacket r hr q)=
      if terminalLowerCost (residualTerminalIndex r) q=terminalLowerMinimum (residualTerminalIndex r)
      then (descPochhammer F₂ q:PowerSeries F₂) else 0 := by
  rw [terminalLowerPacket,map_mul,map_mul,map_C,sourceShift_red,mul_one,
    terminalLowerScalarInt_red]
  have hp : PowerSeries.map red (eulerPacket q:Series)=
      (descPochhammer F₂ q:PowerSeries F₂) := by
    rw [← eulerPacket_red]
    ext n
    simp
  rw [hp]
  split <;> simp_all

/-- Full lower residue, including the constant packet whenever it ties. -/
theorem terminalLowerSeries_red (r : ℕ) (hr : 0<r) :
    PowerSeries.map red (terminalLowerSeries r hr)=
      ∑ q:Fin (residualTerminalIndex r),
        if terminalLowerCost (residualTerminalIndex r) q=terminalLowerMinimum (residualTerminalIndex r)
        then (descPochhammer F₂ q:PowerSeries F₂) else 0 := by
  rw [terminalLowerSeries,map_sum]
  simp_rw [terminalLowerPacket_red]

end Komorebi.Euler
