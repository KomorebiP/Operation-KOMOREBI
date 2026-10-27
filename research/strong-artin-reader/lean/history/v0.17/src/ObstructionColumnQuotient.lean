import ObstructionFunctionalColumnRepresentation

/-!
# Equation columns modulo the original Jacobian image

The evaluation map from the equation space to the dual obstruction space has
kernel exactly the original Jacobian image.  Thus representing columns are
unique modulo `range J`, and in finite dimension the quotient equation space is
canonically equivalent to the dual obstruction space.
-/

namespace Komorebi.StrongArtin.ObstructionColumnQuotient

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation

noncomputable section

variable {k U W : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- The columns invisible to every dual obstruction are exactly the original
Jacobian columns. -/
theorem ker_evaluationColumnMap_eq_range (J : U →ₗ[k] W) :
    LinearMap.ker (evaluationColumnMap J) = LinearMap.range J := by
  ext w
  constructor
  · intro hw
    have hcoann : w ∈ (obstructionDual J).dualCoannihilator := by
      rw [Submodule.mem_dualCoannihilator]
      intro φ hφ
      have heval := congrArg
        (fun ℓ : Module.Dual k (obstructionDual J) => ℓ ⟨φ, hφ⟩)
        (LinearMap.mem_ker.mp hw)
      simpa [evaluationColumnMap_apply] using heval
    simpa [obstructionDual, LinearMap.ker_dualMap_eq_dualAnnihilator_range,
      Subspace.dualAnnihilator_dualCoannihilator_eq] using hcoann
  · intro hw
    rcases hw with ⟨u, rfl⟩
    rw [LinearMap.mem_ker]
    apply LinearMap.ext
    intro φ
    rw [evaluationColumnMap_apply]
    exact (mem_obstructionDual J φ.1).mp φ.2 u

/-- Two columns induce the same functional on the dual obstruction space exactly
when their difference belongs to the original Jacobian image. -/
theorem evaluationColumnMap_eq_iff_sub_mem_range
    (J : U →ₗ[k] W) (w₁ w₂ : W) :
    evaluationColumnMap J w₁ = evaluationColumnMap J w₂ ↔
      w₁ - w₂ ∈ LinearMap.range J := by
  constructor
  · intro h
    have hk : w₁ - w₂ ∈ LinearMap.ker (evaluationColumnMap J) :=
      (LinearMap.sub_mem_ker_iff).2 h
    simpa [ker_evaluationColumnMap_eq_range J] using hk
  · intro h
    apply (LinearMap.sub_mem_ker_iff).1
    simpa [ker_evaluationColumnMap_eq_range J] using h

/-- Pointwise formulation: representing columns are unique modulo the original
Jacobian image. -/
theorem representing_columns_eq_iff_sub_mem_range
    (J : U →ₗ[k] W) (w₁ w₂ : W) :
    (∀ φ : obstructionDual J, φ.1 w₁ = φ.1 w₂) ↔
      w₁ - w₂ ∈ LinearMap.range J := by
  rw [← evaluationColumnMap_eq_iff_sub_mem_range J]
  constructor
  · intro h
    apply LinearMap.ext
    intro φ
    simpa [evaluationColumnMap_apply] using h φ
  · intro h φ
    have heq := congrArg
      (fun ℓ : Module.Dual k (obstructionDual J) => ℓ φ) h
    simpa [evaluationColumnMap_apply] using heq

/-- The equation space modulo the original Jacobian image is canonically
isomorphic to the dual obstruction space. -/
def quotientRangeEquivObstructionDual
    [FiniteDimensional k W] (J : U →ₗ[k] W) :
    (W ⧸ LinearMap.range J) ≃ₗ[k] Module.Dual k (obstructionDual J) := by
  let eKer : (W ⧸ LinearMap.range J) ≃ₗ[k]
      (W ⧸ LinearMap.ker (evaluationColumnMap J)) :=
    Submodule.quotEquivOfEq (LinearMap.range J)
      (LinearMap.ker (evaluationColumnMap J))
      (ker_evaluationColumnMap_eq_range J).symm
  exact eKer.trans
    ((evaluationColumnMap J).quotKerEquivOfSurjective
      (evaluationColumnMap_surjective J))

@[simp]
theorem quotientRangeEquivObstructionDual_mk
    [FiniteDimensional k W] (J : U →ₗ[k] W) (w : W) :
    quotientRangeEquivObstructionDual J (Submodule.Quotient.mk w) =
      evaluationColumnMap J w := by
  simp [quotientRangeEquivObstructionDual,
    Submodule.quotEquivOfEq_mk,
    LinearMap.quotKerEquivOfSurjective_apply_mk]

end

end Komorebi.StrongArtin.ObstructionColumnQuotient

#print axioms Komorebi.StrongArtin.ObstructionColumnQuotient.ker_evaluationColumnMap_eq_range
#print axioms Komorebi.StrongArtin.ObstructionColumnQuotient.representing_columns_eq_iff_sub_mem_range
#print axioms Komorebi.StrongArtin.ObstructionColumnQuotient.quotientRangeEquivObstructionDual
