import CoupledPythonRefinement
open Komorebi.SpecialFunctions.Coupled.Scales
open Komorebi.SpecialFunctions.Coupled.Scales.Python
#check source_evaluation_iff
#check raw_source_return_encloses
#check source_array_bounds
#check source_seed_safe
example (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ) :
    ∃ out, EvaluationRun p x last outer out := source_evaluation_total p x last outer
example : classifyIndex (.boolean true) = none := rfl
example (x : ℚ) : seed x = majorantSeed x := seed_correct x
