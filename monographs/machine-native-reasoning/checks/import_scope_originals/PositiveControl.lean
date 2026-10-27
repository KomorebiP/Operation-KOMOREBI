import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section
example : True := True.intro
example : run noncommuting [false, true] 1 = 4 := action_order_matters.1
example : ¬ FiberCriterion visible mixedLaw.kernel := mixed_fiber_failure
example : posterior? (fun _ : Bool => (0 : ℝ)) = none := no_posterior_for_zero_mass
