import ProofPath.Examples
open ProofPath ProofPath.Examples
-- The pairwise matching assignment is not a model of the whole AND-rule.
example : conjunctionField.Model (fun v => v ≠ 2) := by
  change (∀ v : Fin 3, False → v ≠ 2) ∧
    (∀ _ : Unit, True → (∀ v : Fin 3, v ≠ 2 → v ≠ 2) → (2 : Fin 3) ≠ 2)
  decide
