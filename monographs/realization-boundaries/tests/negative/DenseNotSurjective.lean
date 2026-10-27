import RealizationBoundaries
set_option autoImplicit false
noncomputable section
open RealizationBoundaries

example (a : ℕ → Bool) : Function.Surjective (fun d : finiteSupport =>
    (⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩ : pairedGroup a)) := by
  exact finiteSupport_inclusion_not_surjective a
