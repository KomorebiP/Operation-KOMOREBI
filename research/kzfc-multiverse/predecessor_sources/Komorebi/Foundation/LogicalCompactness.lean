import Komorebi.Foundation.KappaResidualReflection

/-!
# Logical compactness as depth-zero residual reflection

This file is independent of any particular syntax.  It proves that for any abstract
logic whose local pieces are subtheories, kappa-compactness is exactly depth-zero
Komorebi residual reflection at the same cardinal scale.
-/

namespace Komorebi

/-- Minimal data needed to state a cardinal compactness principle for a logic. -/
structure AbstractLogic where
  Theory : Type u
  Subtheory : Theory → Theory → Prop
  size : Theory → Cardinal
  Satisfiable : Theory → Prop

namespace AbstractLogic

/-- `κ`-compactness: if every `< κ` subtheory of `T` is satisfiable, then `T` is
satisfiable. -/
def KappaCompact (L : AbstractLogic) (κ : Cardinal) : Prop :=
  ∀ T : L.Theory,
    (∀ U : L.Theory, L.Subtheory U T → L.size U < κ → L.Satisfiable U) →
      L.Satisfiable T

/-- Encode one theory as a depth-zero sized residual system. -/
def residualSystem (L : AbstractLogic) (T : L.Theory) : SizedResidualSystem where
  Piece := L.Theory
  size := L.size
  Exact := L.Satisfiable T
  Obstruct := fun q U => q = 0 ∧ L.Subtheory U T ∧ ¬ L.Satisfiable U

/-- Depth-zero residual reflection for every theory of the abstract logic. -/
def KRR0Schema (L : AbstractLogic) (κ : Cardinal) : Prop :=
  ∀ T : L.Theory, (L.residualSystem T).KRR0At κ

/-- `KRR0Schema` implies ordinary cardinal compactness. -/
theorem kappaCompact_of_krr0Schema {L : AbstractLogic} {κ : Cardinal}
    (hKRR : L.KRR0Schema κ) : L.KappaCompact κ := by
  intro T hlocal
  by_contra hunsat
  obtain ⟨U, hsize, hobs⟩ := hKRR T hunsat
  rcases hobs with ⟨_, hsub, hbad⟩
  exact hbad (hlocal U hsub hsize)

/-- Cardinal compactness implies the corresponding depth-zero residual schema. -/
theorem krr0Schema_of_kappaCompact {L : AbstractLogic} {κ : Cardinal}
    (hcompact : L.KappaCompact κ) : L.KRR0Schema κ := by
  intro T hunsat
  by_contra hno
  have hlocal : ∀ U : L.Theory,
      L.Subtheory U T → L.size U < κ → L.Satisfiable U := by
    intro U hsub hsize
    by_contra hbad
    apply hno
    exact ⟨U, hsize, rfl, hsub, hbad⟩
  exact hunsat (hcompact T hlocal)

/-- **Logical Residual Compactness Theorem.**  At depth zero, Komorebi residual
reflection is exactly the ordinary `< κ` compactness principle for any abstract logic
when residual pieces are subtheories. -/
theorem krr0Schema_iff_kappaCompact {L : AbstractLogic} {κ : Cardinal} :
    L.KRR0Schema κ ↔ L.KappaCompact κ := by
  exact ⟨kappaCompact_of_krr0Schema, krr0Schema_of_kappaCompact⟩

end AbstractLogic
end Komorebi

namespace Komorebi
open FirstOrder

namespace FirstOrderResidual

/-- Finitary first-order logic presented through the syntax-independent compactness
interface.  The size of a theory is the cardinality of its set of sentences. -/
def abstractLogic (L : FirstOrder.Language) : AbstractLogic where
  Theory := L.Theory
  Subtheory := fun U T => U ⊆ T
  size := fun U => Cardinal.mk U
  Satisfiable := FirstOrder.Language.Theory.IsSatisfiable

/-- Mathlib first-order compactness realizes abstract `aleph0`-compactness. -/
theorem abstractLogic_kappaCompact_aleph0 {L : FirstOrder.Language} :
    (abstractLogic L).KappaCompact Cardinal.aleph0 := by
  intro T hlocal
  change FirstOrder.Language.Theory.IsSatisfiable T
  change (∀ U : L.Theory, U ⊆ T → Cardinal.mk U < Cardinal.aleph0 →
    FirstOrder.Language.Theory.IsSatisfiable U) at hlocal
  apply FirstOrder.Language.Theory.isSatisfiable_iff_isFinitelySatisfiable.mpr
  intro T₀ hsub
  apply hlocal (↑T₀ : L.Theory) hsub
  exact T₀.finite_toSet.lt_aleph0

/-- Therefore the syntax-independent depth-zero residual schema holds at `aleph0`
for ordinary first-order logic. -/
theorem abstractLogic_krr0Schema_aleph0 {L : FirstOrder.Language} :
    (abstractLogic L).KRR0Schema Cardinal.aleph0 := by
  exact AbstractLogic.krr0Schema_of_kappaCompact abstractLogic_kappaCompact_aleph0

end FirstOrderResidual
end Komorebi
