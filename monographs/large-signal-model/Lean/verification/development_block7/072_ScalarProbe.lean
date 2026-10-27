import KomorebiLSM.InstrumentContraction
open Komorebi.LSM.BaseNorm
noncomputable def scalarC : ProbabilityCone ℝ where
 carrier := {x : ℝ | 0 ≤ x}
 zero_mem := by change (0 : ℝ) ≤ 0; exact le_rfl
 add_mem := by
  intro x y hx hy
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) ≤ y at hy
  change (0 : ℝ) ≤ x+y
  exact add_nonneg hx hy
 smul_mem := by
  intro a ha x hx
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) ≤ a*x
  exact mul_nonneg ha hx
 spans := by
  apply top_unique
  intro x _
  have h : (1 : ℝ) ∈ Submodule.span ℝ {x : ℝ | 0 ≤ x} := Submodule.subset_span (by norm_num)
  simpa using Submodule.smul_mem (Submodule.span ℝ {x : ℝ | 0 ≤ x}) x h
 mass := LinearMap.id
 mass_pos := by
  intro x hx hn
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) < x
  exact lt_of_le_of_ne hx (Ne.symm hn)
 closed := isClosed_le continuous_const continuous_id
