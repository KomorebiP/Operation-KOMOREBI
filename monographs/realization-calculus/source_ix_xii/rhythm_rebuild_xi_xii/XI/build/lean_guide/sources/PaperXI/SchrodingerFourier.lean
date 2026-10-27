import Mathlib.LinearAlgebra.Pi
import Mathlib.Basic.Complex.Basic
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-! Exact coordinate projections from a separating family of diagonal operators.
The finite elimination argument supplies the projector; orthogonality is not a hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerFourier

variable {I X : Type*}

/-- Remove finitely many coordinates while preserving the distinguished coordinate. -/
theorem finite_elimination (χ : I → X → ℂ)
    (hsep : ∀ u v : X, u ≠ v → ∃ i : I, χ i u ≠ χ i v)
    (S : Submodule ℂ (X → ℂ))
    (hS : ∀ i f, f ∈ S → (fun x => χ i x * f x) ∈ S)
    (u : X) (f : X → ℂ) (hf : f ∈ S) (t : Finset X) :
    ∃ g : X → ℂ, g ∈ S ∧ g u = f u ∧ ∀ v ∈ t, v ≠ u → g v = 0 := by
  classical
  induction t using Finset.induction_on with
  | empty => exact ⟨f, hf, rfl, by simp⟩
  | @insert v t _ ih =>
    obtain ⟨g, hg, hgu, hgt⟩ := ih
    by_cases hv : v = u
    · refine ⟨g, hg, hgu, ?_⟩
      intro w hw hwu
      rcases Finset.mem_insert.mp hw with rfl | hw
      · exact (hwu hv).elim
      · exact hgt w hw hwu
    · obtain ⟨i, hi⟩ := hsep u v (Ne.symm hv)
      let g' : X → ℂ := (χ i u - χ i v)⁻¹ •
        ((fun x => χ i x * g x) - χ i v • g)
      have hg' : g' ∈ S :=
        S.smul_mem _ (S.sub_mem (hS i g hg) (S.smul_mem _ hg))
      have hgu' : g' u = f u := by
        dsimp [g']
        rw [← sub_mul, inv_mul_cancel_left₀ (sub_ne_zero.mpr hi), hgu]
      refine ⟨g', hg', hgu', ?_⟩
      intro w hw hwu
      rcases Finset.mem_insert.mp hw with rfl | hw
      · simp [g']
      · simp [g', hgt w hw hwu]

/-- Stability under a separating diagonal family implies stability under every
coordinate projector, with no spectral theorem assumed. -/
theorem coordinate_projection_mem [Fintype X] [DecidableEq X] (χ : I → X → ℂ)
    (hsep : ∀ u v : X, u ≠ v → ∃ i : I, χ i u ≠ χ i v)
    (S : Submodule ℂ (X → ℂ))
    (hS : ∀ i f, f ∈ S → (fun x => χ i x * f x) ∈ S)
    (u : X) (f : X → ℂ) (hf : f ∈ S) :
    (fun x => if x = u then f u else 0) ∈ S := by
  classical
  obtain ⟨g, hg, hgu, hgt⟩ := finite_elimination χ hsep S hS u f hf Finset.univ
  have heq : g = (fun x => if x = u then f u else 0) := by
    funext x
    by_cases hx : x = u
    · subst x; simpa using hgu
    · simp [hx, hgt x (Finset.mem_univ x) hx]
  rwa [← heq]

/-- A nonzero distinguished coordinate gives its unit coordinate vector. -/
theorem coordinate_unit_mem [Fintype X] [DecidableEq X] (χ : I → X → ℂ)
    (hsep : ∀ u v : X, u ≠ v → ∃ i : I, χ i u ≠ χ i v)
    (S : Submodule ℂ (X → ℂ))
    (hS : ∀ i f, f ∈ S → (fun x => χ i x * f x) ∈ S)
    (u : X) (f : X → ℂ) (hf : f ∈ S) (hfu : f u ≠ 0) :
    (fun x => if x = u then (1 : ℂ) else 0) ∈ S := by
  classical
  have h := S.smul_mem (f u)⁻¹ (coordinate_projection_mem χ hsep S hS u f hf)
  convert h using 1
  funext x
  by_cases hx : x = u <;> simp [hx, hfu]

end PaperXI.SchrodingerFourier
