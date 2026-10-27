module
public import Euler.QuadraticCriticalSeries
@[expose] public section
noncomputable section
set_option maxHeartbeats 400000
namespace Komorebi.Euler
open PowerSeries

lemma qc_unit_red (u : Dˣ) : red (u:D)=1 := by
  apply red_not_zero_eq_one
  intro h
  have hn : ‖(u:D)‖<1 := (res_zero_iff_norm_lt_one _).mp (by simpa only [res_eq_red] using h)
  rw [PadicInt.norm_units] at hn
  exact (lt_irrefl (1:ℝ)) hn

/-- This point is CONSTRUCTED by restricted-series Hensel lifting; it is not an input. -/
def quadraticCriticalPoint (b : D) (u : Dˣ) (R : Series) (hR : Restricted R) : D :=
  (quadraticCore_unique_critical 0 b (u:D) hR (qc_unit_red u)).choose

lemma quadraticCriticalPoint_spec (b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    (∀ x:D, deriv (qeval (quadraticCoreSeries 0 b (u:D) R)) (x:ℚ_[2])=0 ↔
      x=quadraticCriticalPoint b u R hR) ∧
    ‖quadraticCriticalPoint b u R hR‖=‖b‖ ∧
    reval (quadraticCriticalSeries b (u:D) R) (quadraticCriticalPoint b u R hR)=0 :=
  (quadraticCore_unique_critical 0 b (u:D) hR (qc_unit_red u)).choose_spec

/-- Adding the constant value does not change the unique critical point. -/
theorem quadraticCriticalPoint_unique (a b : D) (u : Dˣ) (R : Series)
    (hR : Restricted R) (x : D) :
    deriv (qeval (quadraticCoreSeries a b (u:D) R)) (x:ℚ_[2])=0 ↔
      x=quadraticCriticalPoint b u R hR := by
  have h := (quadraticCriticalPoint_spec b u R hR).1 x
  rw [deriv_qeval (quadraticCore_restricted 0 b (u:D) hR),
    quadraticCore_rjet_one 0 b (u:D) hR] at h
  rwa [deriv_qeval (quadraticCore_restricted a b (u:D) hR),
    quadraticCore_rjet_one a b (u:D) hR]

lemma quadraticCriticalPoint_norm (b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    ‖quadraticCriticalPoint b u R hR‖=‖b‖ :=
  (quadraticCriticalPoint_spec b u R hR).2.1

/-- The integral part of the differentiated cubic tail. -/
def criticalTailSlope (R : Series) (x : D) : D := 3*reval R x+x*rjet 1 R x

/-- Exact critical-point motion, including the nonlinear displacement term. -/
theorem quadraticCriticalPoint_motion (b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    let c:=quadraticCriticalPoint b u R hR
    c+(↑(u⁻¹):D)*b = -2*(↑(u⁻¹):D)*c^2*criticalTailSlope R c := by
  dsimp only
  let c:=quadraticCriticalPoint b u R hR
  have hc := (quadraticCriticalPoint_spec b u R hR).2.2
  rw [quadraticCritical_reval b (u:D) hR] at hc
  change b+(u:D)*c+2*c^2*criticalTailSlope R c=0 at hc
  have hi : (↑(u⁻¹):D)*(u:D)=1 := Units.inv_mul u
  have hm := congrArg (fun z:D => (↑(u⁻¹):D)*z) hc
  simp only [mul_add,mul_zero,← mul_assoc,hi,one_mul] at hm
  change c+(↑(u⁻¹):D)*b = _
  linear_combination hm

/-- A scalar invariant of the ACTUAL moved critical point. -/
def quadraticCriticalValue (a b : D) (u : Dˣ) (R : Series) (hR : Restricted R) : D :=
  reval (quadraticCoreSeries a b (u:D) R) (quadraticCriticalPoint b u R hR)

/-- Completing the square and retaining the critical-point motion gives an EXACT remainder. -/
theorem quadraticCriticalValue_exact (a b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    let c:=quadraticCriticalPoint b u R hR
    quadraticCriticalValue a b u R hR =
      a-(↑(u⁻¹):D)*b^2+4*c^3*
        (reval R c+(↑(u⁻¹):D)*c*(criticalTailSlope R c)^2) := by
  dsimp only
  let c:=quadraticCriticalPoint b u R hR
  have hm := quadraticCriticalPoint_motion b u R hR
  change c+(↑(u⁻¹):D)*b = -2*(↑(u⁻¹):D)*c^2*criticalTailSlope R c at hm
  have hs:=congrArg (fun z:D => z^2) hm
  have hi : (u:D)*(↑(u⁻¹):D)=1 := Units.mul_inv u
  rw [quadraticCriticalValue,quadraticCore_reval a b (u:D) hR]
  change a+2*b*c+(u:D)*c^2+4*c^3*reval R c = _
  linear_combination (u:D)*hs -
    (2*b*c+(↑(u⁻¹):D)*b^2-4*(↑(u⁻¹):D)*c^4*(criticalTailSlope R c)^2)*hi

lemma qc_norm_four : ‖(4:D)‖=(1/4:ℝ) := by
  rw [show (4:D)=(2:D)^2 by norm_num,norm_pow,norm_two]
  norm_num

/-- Uniform third-order error budget for the moving critical value. Zero b is included. -/
theorem quadraticCriticalValue_error (a b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    ‖quadraticCriticalValue a b u R hR-(a-(↑(u⁻¹):D)*b^2)‖≤(1/4:ℝ)*‖b‖^3 := by
  rw [quadraticCriticalValue_exact]
  simp only [add_sub_cancel_left]
  rw [norm_mul,norm_mul,qc_norm_four,norm_pow,quadraticCriticalPoint_norm]
  exact mul_le_of_le_one_right (mul_nonneg (by norm_num) (pow_nonneg (norm_nonneg _) _))
    (PadicInt.norm_le_one _)

/-- A critical zero exists exactly when the explicitly constructed critical value is zero. -/
theorem quadraticCriticalValue_zero_iff (a b : D) (u : Dˣ) (R : Series) (hR : Restricted R) :
    (∃ x:D, CriticalZero (qeval (quadraticCoreSeries a b (u:D) R)) (x:ℚ_[2])) ↔
      quadraticCriticalValue a b u R hR=0 := by
  constructor
  · rintro ⟨x,hx⟩
    have he := (quadraticCriticalPoint_unique a b u R hR x).mp hx.2
    subst x
    have hv := hx.1
    rw [← coe_reval (quadraticCore_restricted a b (u:D) hR)] at hv
    exact PadicInt.coe_eq_zero.mp hv
  · intro hv
    refine ⟨quadraticCriticalPoint b u R hR,?_,?_⟩
    · rw [← coe_reval (quadraticCore_restricted a b (u:D) hR)]
      exact PadicInt.coe_eq_zero.mpr hv
    · exact (quadraticCriticalPoint_unique a b u R hR _).mpr rfl

/-- Checkable strict margin; it controls the moved point, not only the old center. -/
theorem quadraticCriticalValue_nonzero_of_gap (a b : D) (u : Dˣ) (R : Series)
    (hR : Restricted R)
    (hgap : (1/4:ℝ)*‖b‖^3<‖a-(↑(u⁻¹):D)*b^2‖) :
    quadraticCriticalValue a b u R hR≠0 := by
  intro hz
  have he:=(quadraticCriticalValue_error a b u R hR).trans_lt hgap
  rw [hz,zero_sub,norm_neg] at he
  exact (lt_irrefl _) he

/-- The leading corrected scalar is an effective nondegeneracy certificate. -/
theorem quadraticCore_no_critical_of_gap (a b : D) (u : Dˣ) (R : Series)
    (hR : Restricted R)
    (hgap : (1/4:ℝ)*‖b‖^3<‖a-(↑(u⁻¹):D)*b^2‖) (x:D) :
    ¬CriticalZero (qeval (quadraticCoreSeries a b (u:D) R)) (x:ℚ_[2]) := by
  intro hx
  exact quadraticCriticalValue_nonzero_of_gap a b u R hR hgap
    ((quadraticCriticalValue_zero_iff a b u R hR).mp ⟨x,hx⟩)

end Komorebi.Euler
