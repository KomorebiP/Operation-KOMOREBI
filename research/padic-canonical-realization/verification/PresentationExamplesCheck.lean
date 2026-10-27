import KomorebiPadic.PresentationExamples

open KomorebiPadic KomorebiPadic.FiniteModulePresentation

noncomputable section

example : Fintype.card {x : ZMod 1 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 1 // (2) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 2 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 2 // (2) • x = 0} = 2 := by

  decide +kernel

example : Fintype.card {x : ZMod 2 // (4) • x = 0} = 2 := by

  decide +kernel

example : Fintype.card {x : ZMod 4 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 4 // (2) • x = 0} = 2 := by

  decide +kernel

example : Fintype.card {x : ZMod 4 // (4) • x = 0} = 4 := by

  decide +kernel

example : Fintype.card {x : ZMod 4 // (8) • x = 0} = 4 := by

  decide +kernel

example : Fintype.card {x : ZMod 8 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 8 // (2) • x = 0} = 2 := by

  decide +kernel

example : Fintype.card {x : ZMod 8 // (4) • x = 0} = 4 := by

  decide +kernel

example : Fintype.card {x : ZMod 8 // (8) • x = 0} = 8 := by

  decide +kernel

example : Fintype.card {x : ZMod 8 // (16) • x = 0} = 8 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (2) • x = 0} = 2 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (4) • x = 0} = 4 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (8) • x = 0} = 8 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (16) • x = 0} = 16 := by

  decide +kernel

example : Fintype.card {x : ZMod 16 // (32) • x = 0} = 16 := by

  decide +kernel

example : Fintype.card {x : ZMod 3 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 3 // (3) • x = 0} = 3 := by

  decide +kernel

example : Fintype.card {x : ZMod 3 // (9) • x = 0} = 3 := by

  decide +kernel

example : Fintype.card {x : ZMod 9 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 9 // (3) • x = 0} = 3 := by

  decide +kernel

example : Fintype.card {x : ZMod 9 // (9) • x = 0} = 9 := by

  decide +kernel

example : Fintype.card {x : ZMod 9 // (27) • x = 0} = 9 := by

  decide +kernel

example : Fintype.card {x : ZMod 5 // (1) • x = 0} = 1 := by

  decide +kernel

example : Fintype.card {x : ZMod 5 // (5) • x = 0} = 5 := by

  decide +kernel

example : Fintype.card {x : ZMod 5 // (25) • x = 0} = 5 := by

  decide +kernel

example : signature cyclicFour = {2} := cyclicFour_signature

example : signature elementaryFour = {1,1} := elementaryFour_signature

example : Nat.card (ZMod 4) = Nat.card (Fin 2 → ZMod 2) ∧ ¬ Nonempty (ZMod 4 ≃+ (Fin 2 → ZMod 2)) := equal_cardinality_not_isomorphic

example : (signature cyclicFour).count 2 = 1 := by rw [cyclicFour_signature]; decide +kernel

example : (signature elementaryFour).count 1 = 2 := by rw [elementaryFour_signature]; decide +kernel

example : intrinsicMultiplicity 2 1 (ZMod 4) = 0 := by rw [multiplicity_eq_count (by decide) cyclicFour 1 (by decide)]; decide +kernel

example : intrinsicMultiplicity 2 2 (ZMod 4) = 1 := by rw [multiplicity_eq_count (by decide) cyclicFour 2 (by decide)]; decide +kernel

example : intrinsicMultiplicity 2 1 (Fin 2 → ZMod 2) = 2 := by rw [multiplicity_eq_count (by decide) elementaryFour 1 (by decide)]; decide +kernel

example : entry identityFivePresentation nilpotentFive (0 : Fin 2) (1 : Fin 2) = 1 := signature_does_not_choose_matrix.2.1

example : entry swappedFivePresentation nilpotentFive (0 : Fin 2) (1 : Fin 2) = 0 := signature_does_not_choose_matrix.2.2

example : (2 : ℕ) • (2 : ZMod 4) = 0 := by decide +kernel

example : (2 : ℕ) • (1 : ZMod 4) ≠ 0 := by decide +kernel

end
