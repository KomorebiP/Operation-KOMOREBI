module
public import Euler.TerminalNormalForm
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- Entire lower residue polynomial: all ties, including q=0, are retained. -/
def terminalLowerPolynomial (j : ℕ) : Polynomial F₂ :=
  ∑ q∈Finset.range j, if terminalLowerCost j q=terminalLowerMinimum j
    then descPochhammer F₂ q else 0

lemma terminalLowerSeries_red_polynomial (r : ℕ) (hr : 0<r) :
    PowerSeries.map red (terminalLowerSeries r hr)=
      (terminalLowerPolynomial (residualTerminalIndex r):PowerSeries F₂) := by
  rw [terminalLowerSeries_red,terminalLowerPolynomial]
  rw [Fin.sum_univ_eq_sum_range
    (fun q:ℕ => if terminalLowerCost (residualTerminalIndex r) q=
        terminalLowerMinimum (residualTerminalIndex r)
      then (descPochhammer F₂ q:PowerSeries F₂) else 0) (residualTerminalIndex r)]
  ext n
  simp [apply_ite,ite_apply]

lemma terminalLowerSeries_certificate (r : ℕ) (hr : 0<r) (n : ℕ) :
    res (coeff n (terminalLowerSeries r hr))=
      (terminalLowerPolynomial (residualTerminalIndex r)).coeff n := by
  rw [res_eq_red,← coeff_map,terminalLowerSeries_red_polynomial]
  simp

/-- High falling-factorial packets vanish at BOTH residue-field arguments. -/
lemma fallingFactorial_binary_eval_zero (q : ℕ) (hq : 2≤q) (x : F₂) :
    (descPochhammer F₂ q).eval x=0 := by
  rcases binary_value x with rfl | rfl
  · exact descPochhammer_eval_coe_nat_of_lt (R:=F₂) (k:=0) (by omega)
  · exact descPochhammer_eval_coe_nat_of_lt (R:=F₂) (k:=1) (by omega)

/-- Pointwise lower reduction depends on precisely the constant and first packets. -/
theorem terminalLowerPolynomial_eval (j : ℕ) (hj : 2≤j) (x : F₂) :
    (terminalLowerPolynomial j).eval x=
      (if terminalLowerMinimum j=0 then 1 else 0)+
      (if terminalLowerCost j 1=terminalLowerMinimum j then x else 0) := by
  have ht (q : ℕ) :
      (if terminalLowerCost j q=terminalLowerMinimum j then descPochhammer F₂ q else 0).eval x=
      (if q=0 then (if terminalLowerMinimum j=0 then 1 else 0) else 0)+
      (if q=1 then (if terminalLowerCost j 1=terminalLowerMinimum j then x else 0) else 0) := by
    rcases q with _ | q
    · by_cases h : terminalLowerMinimum j=0
      · simp [h]
      · have hz : (0:ℤ)≠terminalLowerMinimum j := Ne.symm h
        simp [h,hz]
    rcases q with _ | q
    · by_cases h : terminalLowerCost j 1=terminalLowerMinimum j <;> simp [h]
    · have hz := fallingFactorial_binary_eval_zero (q+2) (by omega) x
      split <;> simp_all
  rw [terminalLowerPolynomial,Polynomial.eval_finsetSum]
  simp_rw [ht]
  rw [Finset.sum_add_distrib]
  simp only [Finset.sum_ite_eq',Finset.mem_range,show 0<j by omega,
    show 1<j by omega,ite_true]

lemma terminalLowerSeries_reval_red (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r) (x : D) :
    red (reval (terminalLowerSeries r hr) x)=
      (if terminalLowerMinimum (residualTerminalIndex r)=0 then 1 else 0)+
      (if terminalLowerCost (residualTerminalIndex r) 1=terminalLowerMinimum (residualTerminalIndex r)
       then red x else 0) := by
  have h := reval_residue_polynomial (terminalLowerSeries_restricted r hr) 1
    (terminalLowerPolynomial (residualTerminalIndex r))
    (terminalLowerSeries_certificate r hr) x
  rw [res_eq_red,terminalLowerPolynomial_eval _ hj,res_eq_red] at h
  exact h

/-- Exact pointwise-unit criterion, distinct from being constant coefficientwise. -/
theorem terminalLowerSeries_pointwise_unit_iff (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r) :
    (∀x:D, red (reval (terminalLowerSeries r hr) x)=1) ↔
      terminalLowerMinimum (residualTerminalIndex r)=0 ∧
      terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r) := by
  constructor
  · intro h
    have h0 := h 0
    have h1 := h 1
    rw [terminalLowerSeries_reval_red r hr hj,map_zero] at h0
    rw [terminalLowerSeries_reval_red r hr hj,map_one] at h1
    by_cases he : terminalLowerMinimum (residualTerminalIndex r)=0
    · refine ⟨he,?_⟩
      intro hcost
      simp only [he,hcost,ite_true] at h1
      exact (by decide : (2:F₂)≠1) h1
    · simp [he] at h0
  · rintro ⟨he,hc⟩ x
    rw [terminalLowerSeries_reval_red r hr hj]
    rw [ite_eq_left he,ite_eq_right hc,add_zero]

/-- Regularity is a strict inequality for every positive predecessor packet. -/
def TerminalRegular (j : ℕ) : Prop :=
  ∀q, 0<q → q<j → 0<terminalLowerCost j q

lemma terminalLowerMinimum_regular (j : ℕ) (hj : 0<j) (hreg : TerminalRegular j) :
    terminalLowerMinimum j=0 := by
  have hnonpos := terminalLowerMinimum_nonpos j hj
  obtain ⟨q,hq,he⟩ := terminalLowerMinimum_attained j hj
  rcases Nat.eq_zero_or_pos q with rfl | hpos
  · simpa using he.symm
  · have hh := hreg q hpos hq
    omega

lemma terminalLowerPolynomial_regular (j : ℕ) (hj : 0<j) (hreg : TerminalRegular j) :
    terminalLowerPolynomial j=1 := by
  have hm := terminalLowerMinimum_regular j hj hreg
  rw [terminalLowerPolynomial,Finset.sum_eq_single 0]
  · simp [hm]
  · intro q hq hne
    have hh := hreg q (by omega) (Finset.mem_range.mp hq)
    rw [hm,ite_eq_right (by omega)]
  · intro hn
    exact False.elim (hn (Finset.mem_range.mpr hj))

/-- Full constant residue for a regular Euler lower prefix. -/
theorem terminalLowerSeries_regular_red (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (hreg : TerminalRegular (residualTerminalIndex r)) :
    PowerSeries.map red (terminalLowerSeries r hr)=1 := by
  rw [terminalLowerSeries_red_polynomial,terminalLowerPolynomial_regular _ hj hreg]
  simp

/-- Exact pointwise-unit case at the equality wall, now for actual Euler objects. -/
theorem eulerNormalizedResidual_equality_unit (r : ℕ) (hr : 0<r)
    (hj : 2≤residualTerminalIndex r) (hd : terminalWallDistance r=0)
    (he : terminalLowerMinimum (residualTerminalIndex r)=0)
    (h1 : terminalLowerCost (residualTerminalIndex r) 1≠terminalLowerMinimum (residualTerminalIndex r))
    (x : D) : red (reval (eulerNormalizedResidual r hr) x)=1 := by
  have hv := (terminalLowerSeries_pointwise_unit_iff r hr hj).mpr ⟨he,h1⟩ x
  rw [eulerNormalizedResidual_terminal_form r hr (by omega),map_add,map_mul,map_mul,hd,
    pow_zero,map_one,one_mul,hv]
  have hp : red ((eulerPacket (residualTerminalIndex r)).eval x)=0 := by
    have hm : red ((eulerPacket (residualTerminalIndex r)).eval x)=
        ((eulerPacket (residualTerminalIndex r)).map red).eval (red x) := by
      rw [Polynomial.eval_map,Polynomial.eval₂_at_apply]
    rw [hm,eulerPacket_red]
    exact fallingFactorial_binary_eval_zero _ hj _
  rw [hp,zero_mul,zero_add]

end Komorebi.Euler
