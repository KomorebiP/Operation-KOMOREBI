import KomorebiReader.StirlingRecovery

/- Deliberately false: five copies of one address do not meet the distinctness
hypothesis of `finite_samples_determine_profile`. This file must fail. -/

example : Function.Injective (fun _ : Fin 5 => (1 : ℚ)) := by
  decide
