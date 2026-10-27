import KomorebiLSM.Conditioning
import Mathlib.Tactic.FinCases

/-! A parameterized family attains the inverse-event-mass bound exactly. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteTV
open scoped BigOperators
open FiniteBayes FiniteInstruments

noncomputable def sharpP (r : ℝ) : Fin 3 → ℝ := ![r,0,1-r]
noncomputable def sharpQ (r d : ℝ) : Fin 3 → ℝ := ![r-d,d,1-r]
def sharpEvent : Finset (Fin 3) := {0,1}

theorem sharpP_prior (r : ℝ) (hr : 0 ≤ r) (h1 : r ≤ 1) : IsPrior (sharpP r) := by
  constructor
  · intro i; fin_cases i <;> simp [sharpP] <;> linarith
  · simp [sharpP,Fin.sum_univ_three]

theorem sharpQ_prior (r d : ℝ) (h1 : r ≤ 1) (hd : 0 ≤ d) (hdr : d ≤ r) :
    IsPrior (sharpQ r d) := by
  constructor
  · intro i; fin_cases i <;> simp [sharpQ] <;> linarith
  · simp [sharpQ,Fin.sum_univ_three]

theorem sharpP_eventMass (r : ℝ) : eventMass (sharpP r) sharpEvent=r := by
  simp [eventMass,sharpEvent,sharpP]

theorem sharpQ_eventMass (r d : ℝ) : eventMass (sharpQ r d) sharpEvent=r := by
  simp [eventMass,sharpEvent,sharpQ]

theorem sharp_distance (r d : ℝ) (hd : 0 ≤ d) : distance (sharpP r) (sharpQ r d)=d := by
  have he : sharpP r-sharpQ r d=(![d,-d,0] : Fin 3 → ℝ) := by
    funext i; fin_cases i <;> simp [sharpP,sharpQ]
  rw [distance,he]
  simp [l1,Fin.sum_univ_three,abs_of_nonneg hd]

theorem sharpP_conditional (r : ℝ) (hr : 0<r) :
    conditional (sharpP r) sharpEvent=(![1,0,0] : Fin 3 → ℝ) := by
  unfold conditional normalize
  rw [restrict_mass,sharpP_eventMass]
  funext i
  fin_cases i <;> simp [restrict,sharpP,sharpEvent,ne_of_gt hr]

theorem sharpQ_conditional (r d : ℝ) (hr : 0<r) :
    conditional (sharpQ r d) sharpEvent=(![1-d/r,d/r,0] : Fin 3 → ℝ) := by
  unfold conditional normalize
  rw [restrict_mass,sharpQ_eventMass]
  funext i
  fin_cases i <;> simp [restrict,sharpQ,sharpEvent,div_eq_mul_inv] <;> field_simp

theorem sharp_conditional_distance (r d : ℝ) (hr : 0<r) (hd : 0 ≤ d) :
    distance (conditional (sharpP r) sharpEvent) (conditional (sharpQ r d) sharpEvent)=d/r := by
  rw [sharpP_conditional r hr,sharpQ_conditional r d hr]
  have he : (![1,0,0] : Fin 3 → ℝ)-![1-d/r,d/r,0]=![d/r,-(d/r),0] := by
    funext i; fin_cases i <;> simp
  rw [distance,he]
  simp [l1,Fin.sum_univ_three,abs_of_nonneg (div_nonneg hd hr.le)]

/-- P44's sharpness, for every event mass and every admissible moved mass. -/
theorem sharp_conditioning (r d : ℝ) (hr : 0<r) (h1 : r ≤ 1)
    (hd : 0 ≤ d) (hdr : d ≤ r) :
    ∃ (p q : Fin 3 → ℝ) (H : Finset (Fin 3)),
      IsPrior p ∧ IsPrior q ∧ eventMass p H=r ∧ eventMass q H=r ∧
      distance p q=d ∧ distance (conditional p H) (conditional q H)=d/r :=
  ⟨sharpP r,sharpQ r d,sharpEvent,sharpP_prior r hr.le h1,sharpQ_prior r d h1 hd hdr,
    sharpP_eventMass r,sharpQ_eventMass r d,sharp_distance r d hd,
    sharp_conditional_distance r d hr hd⟩

end Komorebi.LSM.FiniteTV
