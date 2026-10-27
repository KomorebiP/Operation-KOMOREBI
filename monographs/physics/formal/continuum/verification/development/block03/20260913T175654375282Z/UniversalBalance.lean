module

public import KomorebiPhysics.RefinementTower

/-!
Chapter 4.5 (4.29)--(4.34). Finite antisymmetric balance with explicit sources.
Unlike the Hilbert-space theorems, this interface assumes the stated scalar
balance equation; it proves its exact finite aggregation consequences.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.UniversalBalance
open scoped BigOperators Matrix
variable {I J : Type*} [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]

/-- Universal cancellation does not depend on a quantum realization of F. -/
theorem boundary_sum (F : I → I → ℝ) (hF : ∀ i j, F i j = -F j i) (C : Finset I) :
    (∑ i ∈ C, ∑ j, F i j) = ∑ i ∈ C, ∑ j ∈ Cᶜ, F i j := by
  calc
    _ = ∑ i ∈ C, ((∑ j ∈ C, F i j) + ∑ j ∈ Cᶜ, F i j) := by
      apply Finset.sum_congr rfl
      intro i _
      exact (Finset.sum_add_sum_compl C _).symm
    _ = _ := by
      rw [Finset.sum_add_distrib, antisymmetric_sum_zero F C (fun i _ j _ => hF i j),
        zero_add]

/-- Sources remain; only internal exchange cancels. -/
theorem source_boundary_sum (s : I → ℝ) (F : I → I → ℝ)
    (hF : ∀ i j, F i j = -F j i) (C : Finset I) :
    (∑ i ∈ C, (s i + ∑ j, F i j)) =
      (∑ i ∈ C, s i) + ∑ i ∈ C, ∑ j ∈ Cᶜ, F i j := by
  rw [Finset.sum_add_distrib, boundary_sum F hF C]

/-- Equation (4.31), with actual scalar derivatives as inputs. -/
theorem hasDerivAt_subset {q : I → ℝ → ℝ} {s : I → ℝ} {F : I → I → ℝ} {t : ℝ}
    (hq : ∀ i, HasDerivAt (q i) (s i + ∑ j, F i j) t)
    (hF : ∀ i j, F i j = -F j i) (C : Finset I) :
    HasDerivAt (fun u => ∑ i ∈ C, q i u)
      ((∑ i ∈ C, s i) + ∑ i ∈ C, ∑ j ∈ Cᶜ, F i j) t := by
  have h := HasDerivAt.fun_sum (u := C) (fun i _ => hq i)
  rwa [source_boundary_sum s F hF C] at h

/-- The total amount changes by total source, not necessarily by zero. -/
theorem hasDerivAt_total {q : I → ℝ → ℝ} {s : I → ℝ} {F : I → I → ℝ} {t : ℝ}
    (hq : ∀ i, HasDerivAt (q i) (s i + ∑ j, F i j) t)
    (hF : ∀ i j, F i j = -F j i) :
    HasDerivAt (fun u => ∑ i, q i u) (∑ i, s i) t := by
  simpa using hasDerivAt_subset hq hF Finset.univ

/-- Equation (4.33), no coarse antisymmetry is assumed. -/
theorem coarse_antisymm (f : I → J) (F : I → I → ℝ)
    (hF : ∀ i j, F i j = -F j i) (a b : J) :
    (∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, F i j) =
      -(∑ i ∈ Atlas.fiber f b, ∑ j ∈ Atlas.fiber f a, F i j) := by
  calc
    _ = ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, -F j i := by
      apply Finset.sum_congr rfl
      intro i _
      apply Finset.sum_congr rfl
      intro j _
      exact hF i j
    _ = _ := by
      simp only [Finset.sum_neg_distrib]
      rw [Finset.sum_comm]

omit [DecidableEq I] in
/-- Sum of incoming coarse currents equals the sum of fine current rows. -/
theorem coarse_row_sum (f : I → J) (F : I → I → ℝ) (a : J) :
    (∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, F i j) =
      ∑ i ∈ Atlas.fiber f a, ∑ j, F i j := by
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  simp_rw [← RefinementTower.push_eq_fiber]
  exact RefinementTower.sum_push f (F i)

/-- Equation (4.34), actual coarse derivatives with all sources retained.
This aggregation step itself does not require antisymmetry. -/
theorem hasDerivAt_coarse (f : I → J) {q : I → ℝ → ℝ}
    {s : I → ℝ} {F : I → I → ℝ} {t : ℝ}
    (hq : ∀ i, HasDerivAt (q i) (s i + ∑ j, F i j) t) (a : J) :
    HasDerivAt (fun u => ∑ i ∈ Atlas.fiber f a, q i u)
      ((∑ i ∈ Atlas.fiber f a, s i) +
        ∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, F i j) t := by
  have h := HasDerivAt.fun_sum (u := Atlas.fiber f a) (fun i _ => hq i)
  simpa only [Finset.sum_add_distrib, coarse_row_sum] using h

end KomorebiPhysics.UniversalBalance
