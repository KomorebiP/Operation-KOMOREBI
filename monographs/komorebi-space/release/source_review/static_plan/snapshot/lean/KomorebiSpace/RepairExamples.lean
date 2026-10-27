import KomorebiSpace.RepairProjection
import Mathlib.Topology.Algebra.Module.ContinuousLinearMap.PiProd

set_option autoImplicit false

/-!
# Constructed and non-canonical examples

The split model satisfies all correction hypotheses with rate zero and retains
an arbitrary nonzero semantic coordinate. A second model shows that preservation
of a nontrivial observable does not by itself make exact repairs unique.
-/
universe u v w
noncomputable section
namespace KomorebiSpace
namespace RepairExamples
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (S : Type v) (R : Type w)
variable [NormedAddCommGroup S] [NormedSpace 𝕜 S]
variable [NormedAddCommGroup R] [NormedSpace 𝕜 R]

def splitScheme : RepairDynamics.Scheme
    (ContinuousLinearMap.snd 𝕜 S R) (ContinuousLinearMap.fst 𝕜 S R) where
  correction := ContinuousLinearMap.inr 𝕜 S R
  rate := 0
  rate_nonneg := le_rfl
  rate_lt_one := zero_lt_one
  preserve _ := rfl
  contract x := by simp

/-- The actual iteration, not just its existential conclusion, repairs in one step. -/
theorem split_step (x : S × R) :
    RepairDynamics.step (ContinuousLinearMap.snd 𝕜 S R)
      (ContinuousLinearMap.inr 𝕜 S R) x = (x.1, 0) := by
  ext <;> simp [RepairDynamics.step]

variable [CompleteSpace S] [CompleteSpace R]

/-- The constructed analytic projection agrees with the explicit split projection. -/
theorem split_projection (x : S × R) :
    (splitScheme (𝕜 := 𝕜) S R).projection x = (x.1, 0) := by
  apply Prod.ext
  · exact (splitScheme (𝕜 := 𝕜) S R).limit_semantics x
  · exact (splitScheme (𝕜 := 𝕜) S R).limit_exact x

/-- Nonzero semantic information survives exactification in the model. -/
theorem split_nonzero (s : S) (hs : s ≠ 0) (r : R) :
    (splitScheme (𝕜 := 𝕜) S R).projection (s,r) ≠ 0 := by
  rw [split_projection]
  intro h
  exact hs (congrArg Prod.fst h)

/-- Exactness and one nontrivial protected coordinate need not determine the result. -/
theorem semantics_alone_not_unique :
    ∃ a b : ℝ × (ℝ × ℝ), a ≠ b ∧
      a.2.2 = 0 ∧ b.2.2 = 0 ∧ a.1 = b.1 ∧ a.1 = 1 := by
  refine ⟨(1,(0,0)), (1,(1,0)), ?_, rfl, rfl, rfl, rfl⟩
  intro h
  have h01 : (0 : ℝ) = 1 := congrArg (fun x : ℝ × (ℝ × ℝ) => x.2.1) h
  exact zero_ne_one h01

end RepairExamples
end KomorebiSpace
end
