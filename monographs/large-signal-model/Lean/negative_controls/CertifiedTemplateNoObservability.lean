import KomorebiLSM.CertifiedTemplate

/-! Rejected control: removing fitted observability permits distinct exact
matches, even for the degree-zero identity family with the same mass. -/
open Komorebi.LSM.CertifiedTemplate

example : ∀ T U : State 2 →ₗ[ℝ] State 2,
    Matches Boundaries.coefficients Boundaries.coefficients Boundaries.mass Boundaries.mass T →
    Matches Boundaries.coefficients Boundaries.coefficients Boundaries.mass Boundaries.mass U → T=U := by
  have h : ¬ (∀ T U : State 2 →ₗ[ℝ] State 2,
      Matches Boundaries.coefficients Boundaries.coefficients Boundaries.mass Boundaries.mass T →
      Matches Boundaries.coefficients Boundaries.coefficients Boundaries.mass Boundaries.mass U → T=U) := by
    intro hall
    exact Boundaries.distinct_matches (hall _ _ Boundaries.identity_matches Boundaries.singular_matches)
  rw [iff_false_intro h]
