import KomorebiLSM.RotationModel
import KomorebiLSM.BehaviorMinimality

/-! Reachability and observability of the actual rational rotation process.
The dimension conclusion concerns the full behavior space, rather than only
the rank of a finite sampled table. -/
set_option autoImplicit false
namespace Komorebi.LSM.RotationModel
open FiniteInstruments

/-- Three actual reachable columns span every state. -/
theorem reachable_column_decomposition (z : State) :
    z = ((5/4:ℝ)*z 0-(1/4:ℝ)*z 1-(11/8:ℝ)*z 2) • initial +
      (-(3/2:ℝ)*z 0+(3/2:ℝ)*z 1+2*z 2) • rotate initial +
      ((5/4:ℝ)*z 0-(5/4:ℝ)*z 1-(5/8:ℝ)*z 2) • rotate (rotate initial) := by
  ext i
  fin_cases i <;> simp [initial] <;> ring

/-- Every state lies in the span of actual chronological history columns. -/
theorem realization_reachable : realization.IsReachable := by
  change realization.reachable = ⊤
  apply top_unique
  intro z _
  have h0 : initial ∈ realization.reachable :=
    Submodule.subset_span ⟨[], rfl⟩
  have h1 : rotate initial ∈ realization.reachable :=
    Submodule.subset_span ⟨[(false,false)], rfl⟩
  have h2 : rotate (rotate initial) ∈ realization.reachable :=
    Submodule.subset_span ⟨[(false,false),(false,false)], rfl⟩
  rw [reachable_column_decomposition z]
  exact Submodule.add_mem _
    (Submodule.add_mem _ (Submodule.smul_mem _ _ h0) (Submodule.smul_mem _ _ h1))
    (Submodule.smul_mem _ _ h2)

/-- Empty, probe, and rotate-then-probe tests distinguish every state. -/
theorem realization_observable : realization.IsObservable := by
  intro z w h
  have h0 : z 0 = w 0 := by
    simpa only [Behavior.Realization.observe_apply, realization, wordAction_nil,
      LinearMap.id_apply, mass_apply] using congrFun h []
  have hp : (z 0+z 1)/2 = (w 0+w 1)/2 := by
    simpa only [Behavior.Realization.observe_apply, realization, wordAction_cons,
      wordAction_nil, LinearMap.id_comp, operator_probe0, probe0_apply,
      map_smul, initial_mass, smul_eq_mul, mul_one] using congrFun h [(true,false)]
  have hr :
      (z 0+((3/5:ℝ)*z 1-(4/5:ℝ)*z 2))/2 =
      (w 0+((3/5:ℝ)*w 1-(4/5:ℝ)*w 2))/2 := by
    simpa only [Behavior.Realization.observe_apply, realization, wordAction_cons,
      wordAction_nil, LinearMap.id_comp, LinearMap.comp_apply, operator_rotate0,
      operator_probe0, probe0_apply, map_smul, initial_mass, smul_eq_mul, mul_one,
      rotate_apply, Matrix.cons_val_zero, Matrix.cons_val_one] using
      congrFun h [(false,false),(true,false)]
  have h1 : z 1 = w 1 := by linarith
  have h2 : z 2 = w 2 := by linarith
  funext i
  fin_cases i
  · exact h0
  · exact h1
  · exact h2

/-- The complete predictive behavior has dimension three. -/
theorem behavior_dimension_three : Module.finrank ℝ (Behavior.space process) = 3 := by
  rw [← realization.minimal_dimension realization_reachable realization_observable]
  simp [State]

/-- Every finite realization of this complete word law has dimension at least three. -/
theorem any_realization_dimension_ge_three {E : Type*} [AddCommGroup E]
    [Module ℝ E] [FiniteDimensional ℝ E] (r : Behavior.Realization process E) :
    3 ≤ Module.finrank ℝ E := by
  rw [← behavior_dimension_three]
  exact r.behavior_dimension_le

end Komorebi.LSM.RotationModel
