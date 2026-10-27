import ProofPath.Field
import ProofPath.Protected
import ProofPath.Compression
import Mathlib.Tactic.FinCases

namespace ProofPath.Examples

/-- One conjunction needs both premises. No provenance tag changes this. -/
def conjunctionField : Field (Fin 3) Unit where
  leaf := ∅
  premises _ := {v | v ≠ 2}
  conclusion _ := 2
  certified _ := True

def pairPatch (i : Bool) : Set (Fin 3) :=
  if i then {1, 2} else {0, 2}

def pairLocal (i : Bool) : conjunctionField.Local (pairPatch i) where
  val v := v ∈ pairPatch i ∧ v ≠ 2
  outside := fun _ hv h => hv h.1
  leaves := by intro v hv; simp [conjunctionField] at hv
  rules := by
    intro j _ hs _
    cases i
    · have h := hs (by simp [Field.support, conjunctionField] : (1 : Fin 3) ∈ conjunctionField.support j)
      simp [pairPatch] at h
    · have h := hs (by simp [Field.support, conjunctionField] : (0 : Fin 3) ∈ conjunctionField.support j)
      simp [pairPatch] at h

theorem pairwise_data_match : conjunctionField.Matching pairPatch pairLocal := by
  intro i j v hi hj
  exact ⟨fun h => ⟨hj, h.2⟩, fun h => ⟨hi, h.2⟩⟩

theorem pairwise_patches_cover : ∀ v, ∃ i, v ∈ pairPatch i := by
  intro v
  fin_cases v
  · exact ⟨false, by simp [pairPatch]⟩
  · exact ⟨true, by simp [pairPatch]⟩
  · exact ⟨false, by simp [pairPatch]⟩

theorem pairwise_data_have_no_glue :
    ¬ ∃ x, conjunctionField.Model x ∧
      ∀ i v, v ∈ pairPatch i → (x v ↔ (pairLocal i).val v) := by
  rintro ⟨x, hx, ha⟩
  have h0 : x 0 := (ha false 0 (by simp [pairPatch])).mpr (by simp [pairPatch, pairLocal])
  have h1 : x 1 := (ha true 1 (by simp [pairPatch])).mpr (by simp [pairPatch, pairLocal])
  have hn2 : ¬ x 2 := fun h => (by simp [pairLocal] : ¬ (pairLocal false).val 2)
    ((ha false 2 (by simp [pairPatch])).mp h)
  apply hn2
  apply hx.2 () trivial
  intro v hv
  fin_cases v
  · exact h0
  · exact h1
  · exact False.elim (hv rfl)

/-- A zero residual is not evidence of preserving the requested data. -/
theorem rigid_obstruction :
    ¬ ∃ y : ℚ, (LinearMap.id : ℚ →ₗ[ℚ] ℚ) y = 0 ∧
      (LinearMap.id : ℚ →ₗ[ℚ] ℚ) y = (1 : ℚ) := by
  rintro ⟨y, h0, h1⟩
  exact (zero_ne_one : (0 : ℚ) ≠ 1) (h0.symm.trans h1)

end ProofPath.Examples
