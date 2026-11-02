import CoupledUniqueness
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example : ∃! pair : (ℂ → ℂ) × (ℂ → ℂ), workedScales.IsEntireSolution pair.1 pair.2 :=
  workedScales.coupled_entire_exists_unique workedScales_positive (by norm_num [workedScales])

-- Competing entire solutions need no parity or coefficient-expansion premise.
example {f g : ℂ → ℂ} (hsol : workedScales.IsEntireSolution f g) (z : ℂ) :
    HasSum (fun n => ((workedScales.coefficients n).1 : ℂ) * z ^ (2 * n + 1)) (f z) ∧
    HasSum (fun n => ((workedScales.coefficients n).2 : ℂ) * z ^ (2 * n + 1)) (g z) :=
  workedScales.entire_solution_hasSum workedScales_positive (by norm_num [workedScales]) hsol z

def zeroScales : Scales := ⟨0, 0, 0, 0⟩

-- Conditional uniqueness also admits zero scales; no inverse scaling is assumed.
example {f g : ℂ → ℂ} (hsol : zeroScales.IsEntireSolution f g) : f = id ∧ g = id := by
  apply zeroScales.entire_solution_unique hsol
  refine ⟨rfl, rfl, ?_⟩
  intro z
  constructor <;> simpa [zeroScales] using (hasDerivAt_id z)
