import PaperIRelease.GrammarEquivalence
import Mathlib.Data.Finsupp.Basic

set_option autoImplicit false
set_option maxHeartbeats 2000000
set_option linter.unusedVariables false
set_option linter.unnecessarySimpa false
set_option linter.unusedSimpArgs false
set_option linter.unusedSectionVars false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

open CategoryTheory
open scoped BigOperators

universe u
variable {K V E : Type u} [Field K] [Fintype V]
attribute [local instance] Classical.propDecidable

/-- A path retains its declared source and target in its type. -/
inductive TypedPath (s t : E → V) : V → V → Type u where
  | nil (v : V) : TypedPath s t v v
  | cons {v : V} (a : E) : TypedPath s t v (s a) → TypedPath s t v (t a)

variable {s t : E → V}

/-- Paths embed as vertex/arrow words; multiplication is composition from right to left. -/
def TypedPath.word : {v w : V} → TypedPath s t v w → Free K V E
  | _, _, .nil v => vertexWord K V E v
  | _, _, .cons a p => arrowWord K V E a * p.word

/-- A homogeneous path relation is a finite K-linear combination at fixed endpoints. -/
abbrev PathCombination (s t : E → V) (v w : V) := TypedPath s t v w →₀ K

def pathCombinationWord {v w : V} (p : PathCombination (K := K) s t v w) : Free K V E :=
  p.sum (fun q c => c • q.word)

variable {G : Grammar K V E}

/-- The action of a typed path is the actual composition of its declared arrow maps. -/
def TypedData.pathMap (X : TypedData G) :
    {v w : V} → TypedPath G.source G.target v w → (X.space v →ₗ[K] X.space w)
  | _, _, .nil _ => LinearMap.id
  | _, _, .cons a p => (X.arrow a).comp (X.pathMap p)

/-- The constructed free-algebra action sends each path to its source-to-target block. -/
theorem TypedData.path_action (X : TypedData G) {v w : V}
    (p : TypedPath G.source G.target v w) :
    X.freeAction (p.word (K := K)) =
      (LinearMap.single K X.space w).comp ((X.pathMap p).comp (LinearMap.proj v)) := by
  classical
  induction p with
  | nil =>
      apply LinearMap.ext
      intro x
      simp [TypedPath.word, freeAction, vertexWord, vertexOperator, pathMap]
  | cons a p ih =>
      apply LinearMap.ext
      intro x
      rw [TypedPath.word, map_mul, Module.End.mul_apply, ih]
      simp [freeAction, arrowWord, arrowOperator, pathMap]

/-- A finite homogeneous path relation acts by the same finite linear combination of path blocks. -/
theorem TypedData.pathCombination_action (X : TypedData G) {v w : V}
    (p : PathCombination (K := K) G.source G.target v w) :
    X.freeAction (pathCombinationWord p) =
      p.sum (fun q c => c •
        ((LinearMap.single K X.space w).comp ((X.pathMap q).comp (LinearMap.proj v)))) := by
  classical
  simp only [pathCombinationWord, Finsupp.sum, map_sum, map_smul, X.path_action]

/-- The grammar obtained from exactly the manuscript's homogeneous path relations. -/
def grammarFromPathRelations (s t : E → V)
    (relations : ∀ v w, Set (PathCombination (K := K) s t v w)) : Grammar K V E where
  source := s
  target := t
  equations x y := ∃ v w, ∃ p ∈ relations v w, x = pathCombinationWord p ∧ y = 0

/-- The equivalence applies to arbitrary sets of typed, homogeneous finite path relations. -/
def typedPathRelationModuleEquivalence (s t : E → V)
    (relations : ∀ v w, Set (PathCombination (K := K) s t v w)) :
    TypedRealization (G := grammarFromPathRelations s t relations) ≌
      ModuleCat.{u} (Algebra (grammarFromPathRelations s t relations)) :=
  typedModuleEquivalence

end Komorebi.PaperIRelease.GrammarAlgebra
