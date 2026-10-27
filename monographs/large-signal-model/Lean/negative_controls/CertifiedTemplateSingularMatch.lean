import KomorebiLSM.CertifiedTemplate

/-! Rejected control: even a unique exact match with observable fitted rows
can be singular. The explicit reset collapses distinct coordinate states. -/
open Komorebi.LSM.CertifiedTemplate

example : Matches Boundaries.templateCoefficient Boundaries.fittedCoefficient
    Boundaries.mass Boundaries.mass Boundaries.singularReset ∧
    CoefficientObservable Boundaries.fittedCoefficient Boundaries.mass ∧
    Function.Bijective Boundaries.singularReset := by
  refine ⟨Boundaries.singular_observable_matches,Boundaries.fitted_observable,?_⟩
  have h : ¬ Function.Bijective Boundaries.singularReset := fun hb => Boundaries.singular_not_injective hb.1
  rw [iff_false_intro h]
