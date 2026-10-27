import AVOC.QRateDistortionFinite
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Two states with the same scalar optimal value but opposite optimal actions. -/
def crossedQ (s a : Bool) : ℚ :=
  if s = a then 1 else 0

/-- The associated scalar optimal value is constant. -/
def crossedValue (_s : Bool) : ℚ := 1

/-- The scalar value can be represented exactly with one context symbol. -/
theorem crossedValue_exact_code_number_one :
    exactValueCodeNumber crossedValue 0 (by norm_num) = 1 := by
  exact exactValueCodeNumber_eq_one_of_center crossedValue 0 (by norm_num) 1 (by
    intro s
    simp [crossedValue])

/-- In the false state, action false is Q-optimal. -/
theorem crossedQ_false_false_optimal :
    QOptimalAt crossedQ false false := by
  intro b
  cases b <;> simp [crossedQ]

/-- In the true state, action true is Q-optimal. -/
theorem crossedQ_true_true_optimal :
    QOptimalAt crossedQ true true := by
  intro b
  cases b <;> simp [crossedQ]

/-- The two exact Q-signatures are different. -/
theorem crossedQ_signatures_ne : crossedQ false ≠ crossedQ true := by
  intro h
  have hval := congrFun h false
  norm_num [crossedQ] at hval

/-- At zero distortion, preserving complete decision signatures needs two codes,
even though preserving scalar optimal value needs only one. -/
theorem crossedQ_exact_code_number_two :
    exactQCodeNumber crossedQ 0 (by norm_num) = 2 := by
  rw [exactQCodeNumber_zero_eq_distinct_signature_card]
  norm_num [crossedQ]
  have hne : crossedQ true ≠ crossedQ false := by
    exact Ne.symm crossedQ_signatures_ne
  simp [hne]

/-- Decision-signature compression can therefore require strictly more context
than scalar-value compression. -/
theorem q_context_strictly_richer_than_scalar_value_context :
    exactValueCodeNumber crossedValue 0 (by norm_num) <
      exactQCodeNumber crossedQ 0 (by norm_num) := by
  rw [crossedValue_exact_code_number_one, crossedQ_exact_code_number_two]
  norm_num

/-- A one-cell exact Q-context for the crossed decision problem is impossible. -/
theorem crossedQ_no_exact_unit_context :
    ¬ ∃ Qbar : Unit → Bool → ℚ,
      QSignatureApproximation (fun _ : Bool => ()) crossedQ Qbar 0 := by
  intro h
  rcases h with ⟨Qbar, happrox⟩
  have hdist := q_coordinate_gap_forces_distinction
    (fun _ : Bool => ()) crossedQ Qbar 0 happrox
    (s := false) (t := true) (a := false) (by norm_num [crossedQ])
  exact hdist rfl

/-- At tolerance `1/2`, one midpoint signature suffices for both crossed states. -/
theorem crossedQ_half_tolerance_one_code :
    exactQCodeNumber crossedQ (1/2 : ℚ) (by norm_num) = 1 := by
  apply le_antisymm
  · let C : Finset (Bool → ℚ) := {fun _ => (1/2 : ℚ)}
    have hcover : QCenterCover crossedQ (1/2 : ℚ) C := by
      intro s
      refine ⟨(fun _ => (1/2 : ℚ)), by simp [C], ?_⟩
      intro a
      cases s <;> cases a <;> norm_num [crossedQ]
    simpa [C] using exactQCodeNumber_le_cover_card crossedQ (1/2 : ℚ) (by norm_num) C hcover
  · obtain ⟨C, hcover, hcard⟩ := exactQCodeNumber_spec crossedQ (1/2 : ℚ) (by norm_num)
    have hne : C.Nonempty := by
      obtain ⟨c, hc, -⟩ := hcover false
      exact ⟨c, hc⟩
    have : 1 ≤ C.card := Finset.one_le_card.mpr hne
    simpa [hcard] using this

end Komorebi.AVOC
