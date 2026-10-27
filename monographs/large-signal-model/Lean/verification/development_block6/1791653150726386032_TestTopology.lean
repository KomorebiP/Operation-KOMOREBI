import KomorebiLSM.TestCones
import Mathlib.Topology.Algebra.Module.FiniteDimension
import Mathlib.Topology.Order.Compact

/-! Finite-dimensional probability-domain topology. The compactness proof uses
an actual closed observation embedding, not a boundedness assumption. -/
set_option autoImplicit false
namespace Komorebi.LSM.TestDomains
open scoped BigOperators
open FiniteInstruments
variable {E S : Type*} [AddCommGroup E] [Module ℝ E]
variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [T2Space E] [FiniteDimensional ℝ E]

theorem allTests_closed (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    IsClosed (allTests B l) := by
  have he : allTests B l = ⋂ w, {x | 0 ≤ l (wordAction B w x)} := by
    ext x; simp only [allTests,Set.mem_ofPred_eq,Set.mem_iInter,observe_apply]
  rw [he]
  exact isClosed_iInter (fun w => isClosed_le continuous_const
    (l.comp (wordAction B w)).continuous_of_finiteDimensional)

theorem testLevel_closed (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ) :
    IsClosed (testLevel B l h) := by
  have he : testLevel B l h = ⋂ w, ⋂ (_ : w.length ≤ h), {x | 0 ≤ l (wordAction B w x)} := by
    ext x; simp only [testLevel,Set.mem_ofPred_eq,Set.mem_iInter,observe_apply]
  rw [he]
  exact isClosed_iInter (fun w => isClosed_iInter (fun _ => isClosed_le continuous_const
    (l.comp (wordAction B w)).continuous_of_finiteDimensional))

theorem base_closed (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    IsClosed (base B l) :=
  (allTests_closed B l).inter (isClosed_eq l.continuous_of_finiteDimensional continuous_const)

/-- A finite observable linear space embeds as a closed subspace of all tests. -/
theorem observe_closedEmbedding (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (ho : Function.Injective (observe B l)) : Topology.IsClosedEmbedding (observe B l) :=
  LinearMap.isClosedEmbedding_of_injective (LinearMap.ker_eq_bot.mpr ho)

section Causal
variable {A O : Type*} [Fintype O]
variable (B : A × O → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
variable (hm : ∀ a x, ∑ o, l (B (a,o) x) = l x)
include hm

/-- Closed finite-dimensional observation range plus bounded tests gives compactness. -/
theorem base_compact (ho : Function.Injective (observe B l)) :
    IsCompact (base B l) := by
  let K : Set (List (A × O) → ℝ) :=
    {v | (∀ w, v w ∈ Set.Icc (0 : ℝ) 1) ∧ v [] = 1}
  have hk : IsCompact K :=
    (isCompact_pi_infinite (fun _ => isCompact_Icc)).inter_right
      (isClosed_eq (continuous_apply []) continuous_const)
  have he : base B l = observe B l ⁻¹' K := by
    ext x
    constructor
    · intro hx
      exact ⟨base_test_bounds B l hm hx,hx.2⟩
    · rintro ⟨hx,he⟩
      exact ⟨fun w => (hx w).1,he⟩
  rw [he]
  exact (observe_closedEmbedding B l ho).isCompact_preimage hk

end Causal
end Komorebi.LSM.TestDomains
