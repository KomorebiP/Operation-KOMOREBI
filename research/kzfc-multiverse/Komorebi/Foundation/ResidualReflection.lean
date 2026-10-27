import Mathlib.ModelTheory.Satisfiability

/-!
# Komorebi residual reflection: foundational interface

This file isolates a generic residual-reflection judgment and proves that ordinary
first-order compactness is exactly its depth-zero instance.

There are no axioms, `sorry`, or placeholders in this file.
-/

namespace Komorebi

/-- Minimal data for a residual-reflection problem.  `Small` specifies the admissible
local pieces, `Exact` is the global target property, and `Obstruct q J` says that the
piece `J` carries a residual obstruction at depth `q`. -/
structure ResidualSystem where
  Piece : Type u
  Small : Piece → Prop
  Exact : Prop
  Obstruct : Nat → Piece → Prop

namespace ResidualSystem

/-- Some admissible local piece detects a residual obstruction at finite depth. -/
def HasResidualWitness (S : ResidualSystem) : Prop :=
  ∃ q : Nat, ∃ J : S.Piece, S.Small J ∧ S.Obstruct q J

/-- Residual reflection for one system: global failure has a finite-depth local witness. -/
def KRR (S : ResidualSystem) : Prop :=
  ¬ S.Exact → S.HasResidualWitness

/-- The depth-zero specialization of residual reflection. -/
def KRR0 (S : ResidualSystem) : Prop :=
  ¬ S.Exact → ∃ J : S.Piece, S.Small J ∧ S.Obstruct 0 J

/-- Every higher-depth obstruction can be replaced by a depth-zero obstruction on
some admissible local piece.  Failure of this property is the precise place where
a genuinely derived residual principle can carry information not visible at depth zero. -/
def Flattenable (S : ResidualSystem) : Prop :=
  ∀ q : Nat, ∀ J : S.Piece, S.Small J → S.Obstruct q J →
    ∃ J₀ : S.Piece, S.Small J₀ ∧ S.Obstruct 0 J₀

/-- Depth-zero residual reflection always implies finite-depth residual reflection. -/
theorem krr_of_krr0 {S : ResidualSystem} (h : S.KRR0) : S.KRR := by
  intro hfail
  obtain ⟨J, hsmall, hobs⟩ := h hfail
  exact ⟨0, J, hsmall, hobs⟩

/-- **Residual Flattening Theorem.**  If higher residuals flatten to depth zero, then
finite-depth residual reflection cannot be stronger than depth-zero reflection. -/
theorem krr0_of_krr_of_flattenable {S : ResidualSystem}
    (hKRR : S.KRR) (hflat : S.Flattenable) : S.KRR0 := by
  intro hfail
  obtain ⟨q, J, hsmall, hobs⟩ := hKRR hfail
  exact hflat q J hsmall hobs

/-- Under flattenability, the finite-depth and depth-zero principles are equivalent. -/
theorem krr_iff_krr0_of_flattenable {S : ResidualSystem} (hflat : S.Flattenable) :
    S.KRR ↔ S.KRR0 := by
  exact ⟨fun h => krr0_of_krr_of_flattenable h hflat, krr_of_krr0⟩

/-- **Positive-depth necessity.** If finite-depth residual reflection holds but depth-zero
reflection fails, some genuine obstruction is forced to occur at a strictly positive depth. -/
theorem exists_positive_depth_obstruction_of_krr_not_krr0 {S : ResidualSystem}
    (hKRR : S.KRR) (hnot0 : ¬ S.KRR0) :
    ∃ q : Nat, ∃ J : S.Piece, 0 < q ∧ S.Small J ∧ S.Obstruct q J := by
  have hfail : ¬ S.Exact := by
    intro hexact
    apply hnot0
    intro hnotexact
    exact False.elim (hnotexact hexact)
  obtain ⟨q, J, hsmall, hobs⟩ := hKRR hfail
  have hq : q ≠ 0 := by
    intro hzero
    apply hnot0
    intro _
    exact ⟨J, hsmall, hzero ▸ hobs⟩
  exact ⟨q, J, Nat.pos_of_ne_zero hq, hsmall, hobs⟩

/-- Therefore any system separating finite-depth KRR from depth-zero KRR is necessarily
non-flattenable. -/
theorem not_flattenable_of_krr_not_krr0 {S : ResidualSystem}
    (hKRR : S.KRR) (hnot0 : ¬ S.KRR0) : ¬ S.Flattenable := by
  intro hflat
  exact hnot0 (krr0_of_krr_of_flattenable hKRR hflat)

end ResidualSystem

open FirstOrder

namespace FirstOrderResidual

variable {L : FirstOrder.Language} {T : L.Theory}

/-- A finite depth-zero obstruction to satisfiability. -/
def HasFiniteObstruction (T : L.Theory) : Prop :=
  ∃ T₀ : Finset L.Sentence,
    (↑T₀ : L.Theory) ⊆ T ∧
      ¬ FirstOrder.Language.Theory.IsSatisfiable (↑T₀ : L.Theory)

/-- First-order compactness read contrapositively: every unsatisfiable theory has a
finite unsatisfiable subtheory. -/
theorem finite_obstruction_of_unsat
    (hT : ¬ T.IsSatisfiable) :
    HasFiniteObstruction T := by
  have hfin : ¬ T.IsFinitelySatisfiable := by
    intro h
    exact hT (FirstOrder.Language.Theory.isSatisfiable_iff_isFinitelySatisfiable.mpr h)
  unfold FirstOrder.Language.Theory.IsFinitelySatisfiable at hfin
  push Not at hfin
  exact hfin

/-- The obstruction formulation is equivalent to unsatisfiability. -/
theorem unsat_iff_hasFiniteObstruction :
    (¬ T.IsSatisfiable) ↔ HasFiniteObstruction T := by
  constructor
  · exact finite_obstruction_of_unsat
  · rintro ⟨T₀, hsub, hbad⟩ hsat
    exact hbad (hsat.mono hsub)

/-- Encode a first-order theory as a depth-zero residual system.  Finite subtheories
are the pieces; being a subtheory is the smallness/admissibility condition; and an
obstruction exists only at depth zero, where it means unsatisfiable. -/
def system (T : L.Theory) : ResidualSystem where
  Piece := Finset L.Sentence
  Small := fun T₀ => (↑T₀ : L.Theory) ⊆ T
  Exact := T.IsSatisfiable
  Obstruct := fun q T₀ =>
    q = 0 ∧ ¬ FirstOrder.Language.Theory.IsSatisfiable (↑T₀ : L.Theory)

/-- First-order residual reflection as a schema over all theories in `L`. -/
def Schema (L : FirstOrder.Language) : Prop :=
  ∀ T : L.Theory, (system T).KRR0

/-- The usual compactness implication, isolated so that we can compare it directly
with the residual-reflection schema. -/
def Compactness (L : FirstOrder.Language) : Prop :=
  ∀ T : L.Theory, T.IsFinitelySatisfiable → T.IsSatisfiable

/-- Residual reflection implies compactness without appealing to Mathlib's compactness
theorem: a hypothetical global counterexample would yield a finite obstruction. -/
theorem schema_implies_compactness (hKRR : Schema L) : Compactness L := by
  intro T hfin
  by_contra hunsat
  obtain ⟨T₀, hsub, hobs⟩ := hKRR T hunsat
  rcases hobs with ⟨_, hbad⟩
  exact hbad (hfin T₀ hsub)

/-- Conversely, compactness implies depth-zero residual reflection. -/
theorem compactness_implies_schema (hcompact : Compactness L) : Schema L := by
  intro T hunsat
  have hnotfin : ¬ T.IsFinitelySatisfiable := by
    intro hfin
    exact hunsat (hcompact T hfin)
  unfold FirstOrder.Language.Theory.IsFinitelySatisfiable at hnotfin
  push Not at hnotfin
  obtain ⟨T₀, hsub, hbad⟩ := hnotfin
  exact ⟨T₀, hsub, rfl, hbad⟩

/-- For first-order theories, depth-zero Komorebi residual reflection is exactly the
ordinary compactness theorem. -/
theorem schema_iff_compactness : Schema L ↔ Compactness L := by
  exact ⟨schema_implies_compactness, compactness_implies_schema⟩

/-- Mathlib's first-order compactness theorem proves the full depth-zero residual
reflection schema. -/
theorem schema : Schema L := by
  apply compactness_implies_schema
  intro T hfin
  exact FirstOrder.Language.Theory.isSatisfiable_iff_isFinitelySatisfiable.mpr hfin

end FirstOrderResidual
end Komorebi
