import Komorebi.SufficientResolution.ContinuousClosure
import Mathlib.Analysis.Calculus.IteratedDeriv.Defs

/-!
# Actual time derivatives and finite Taylor-jet certificates

The jets here are identified with Mathlib's iteratedDeriv. The certificate tests
operator derivatives at zero, not values at finitely sampled times.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousFlow
variable {X W : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]

 theorem iteratedDeriv_mapped_flow (L : X →L[ℝ] X) (K : (X →L[ℝ] X) →L[ℝ] W) (n : ℕ) :
    iteratedDeriv n (fun t => K (flow L t)) = fun t => K (jet L n t) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [iteratedDeriv_succ, ih]
    funext t
    exact (hasDerivAt_mapped_jet L K n t).deriv

 theorem iteratedDeriv_flow (L : X →L[ℝ] X) (n : ℕ) :
    iteratedDeriv n (flow L) = jet L n := by
  simpa using iteratedDeriv_mapped_flow L (ContinuousLinearMap.id ℝ (X →L[ℝ] X)) n

 theorem iteratedDeriv_flow_zero (L : X →L[ℝ] X) (n : ℕ) :
    iteratedDeriv n (flow L) 0 = L^n := by
  rw [iteratedDeriv_flow, jet_at_zero]

end Komorebi.SufficientResolution.ContinuousFlow

namespace Komorebi.SufficientResolution.ContinuousBlockDynamics
open ContinuousFlow
variable {V H : Type*}
variable [NormedAddCommGroup V] [NormedSpace ℝ V] [CompleteSpace V]
variable [NormedAddCommGroup H] [NormedSpace ℝ H] [CompleteSpace H]
variable (b : ContinuousBlockDynamics V H)

 theorem iteratedDeriv_prepared_zero (n : ℕ) :
    iteratedDeriv n b.prepared 0 = b.generatorPrepared n := by
  have h := congrFun (iteratedDeriv_mapped_flow b.generator
    (sandwich (ContinuousLinearMap.fst ℝ V H) (ContinuousLinearMap.inl ℝ V H)) n) 0
  simpa [prepared, generatorPrepared] using! h

omit [CompleteSpace V] in
 theorem iteratedDeriv_memory_zero (n : ℕ) :
    iteratedDeriv n b.memory 0 = b.memoryMoment n := by
  have h := congrFun (iteratedDeriv_mapped_flow b.D (sandwich b.B b.G) n) 0
  simpa [memory, memoryMoment] using! h

/-- Vanishing earlier feedback gives agreement of the corresponding lower time derivatives. -/
 theorem derivative_prefix_of_memory_prefix (k : ℕ)
    (h : ∀ j < k, b.memoryMoment j = 0) (n : ℕ) (hn : n ≤ k+1) :
    iteratedDeriv n b.prepared 0 = b.A^n := by
  rw [b.iteratedDeriv_prepared_zero, b.generatorPrepared_eq_iff]
  exact b.linear.prepared_prefix_of_memory_prefix k
    (fun j hj => (b.memoryMoment_zero_iff j).mp (h j hj)) n hn

/-- The first new time derivative is exactly the first surviving hidden return. -/
 theorem first_return_derivative (k : ℕ) (h : ∀ j < k, b.memoryMoment j = 0) :
    iteratedDeriv (k+2) b.prepared 0 - b.A^(k+2) = b.memoryMoment k := by
  rw [b.iteratedDeriv_prepared_zero]
  apply ContinuousLinearMap.coe_injective
  simp only [ContinuousLinearMap.toLinearMap_sub, b.generatorPrepared_toLinearMap,
    ContinuousLinearMap.toLinearMap_pow, b.memoryMoment_toLinearMap]
  exact b.linear.first_return_discrepancy k
    (fun j hj => (b.memoryMoment_zero_iff j).mp (h j hj))

/-- Finite hidden dimension gives a finite, exact operator-Taylor certificate. -/
 theorem prepared_exact_iff_finite_derivatives [FiniteDimensional ℝ H] :
    (∀ t, b.prepared t = flow b.A t) ↔
      (∀ n ≤ Module.finrank ℝ H + 1, iteratedDeriv n b.prepared 0 = b.A^n) := by
  simp only [b.iteratedDeriv_prepared_zero]
  exact b.prepared_exact_iff_finite_generator

 theorem memory_zero_iff_finite_derivatives [FiniteDimensional ℝ H] :
    (∀ t, b.memory t = 0) ↔
      (∀ n < Module.finrank ℝ H, iteratedDeriv n b.memory 0 = 0) := by
  simp only [b.iteratedDeriv_memory_zero]
  rw [← b.prepared_exact_iff_memory_zero]
  exact b.prepared_exact_iff_finite_memory

end Komorebi.SufficientResolution.ContinuousBlockDynamics
