import Mathlib.Algebra.FreeAlgebra
import Mathlib.Algebra.RingQuot
import Mathlib.LinearAlgebra.Pi
import KomorebiVerification.ExactCoordinates

/-!
The finite-vertex quiver algebra is constructed by generators and relations,
not assumed as an operator algebra.  Vertices and arrows are independent
generators.  Quotient relations impose the vertex idempotents, their sum, and
the source/target corners of every arrow, together with the declared relations.
-/

set_option autoImplicit false
set_option maxHeartbeats 2000000
set_option linter.unnecessarySimpa false
set_option linter.unusedVariables false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

open scoped BigOperators
open Foundation

universe u

variable (K V E : Type u) [Field K] [Fintype V]

abbrev Free := FreeAlgebra K (V ⊕ E)

def vertexWord (v : V) : Free K V E := FreeAlgebra.ι K (.inl v)
def arrowWord (a : E) : Free K V E := FreeAlgebra.ι K (.inr a)

/-- A finite-vertex typed grammar with arbitrary arrow set and declared equations. -/
structure Grammar where
  source : E → V
  target : E → V
  equations : Free K V E → Free K V E → Prop

variable {K V E}

inductive Relation (G : Grammar K V E) : Free K V E → Free K V E → Prop where
  | vertex_idempotent (v : V) :
      Relation G (vertexWord K V E v * vertexWord K V E v) (vertexWord K V E v)
  | vertex_orthogonal (v w : V) (h : v ≠ w) :
      Relation G (vertexWord K V E v * vertexWord K V E w) 0
  | vertex_complete : Relation G (∑ v, vertexWord K V E v) 1
  | arrow_corner (a : E) :
      Relation G (vertexWord K V E (G.target a) * arrowWord K V E a *
        vertexWord K V E (G.source a)) (arrowWord K V E a)
  | declared {x y : Free K V E} : G.equations x y → Relation G x y

abbrev Algebra (G : Grammar K V E) := RingQuot (Relation G)

def quotient (G : Grammar K V E) : Free K V E →ₐ[K] Algebra G :=
  RingQuot.mkAlgHom K (Relation G)

def vertex (G : Grammar K V E) (v : V) : Algebra G := quotient G (vertexWord K V E v)
def arrow (G : Grammar K V E) (a : E) : Algebra G := quotient G (arrowWord K V E a)

theorem vertex_idempotent (G : Grammar K V E) (v : V) : vertex G v * vertex G v = vertex G v := by
  simpa only [vertex, quotient, map_mul] using
    RingQuot.mkAlgHom_rel K (Relation.vertex_idempotent (G := G) v)

theorem vertex_orthogonal (G : Grammar K V E) {v w : V} (h : v ≠ w) :
    vertex G v * vertex G w = 0 := by
  simpa only [vertex, quotient, map_mul, map_zero] using
    RingQuot.mkAlgHom_rel K (Relation.vertex_orthogonal (G := G) v w h)

theorem vertex_complete (G : Grammar K V E) : ∑ v, vertex G v = 1 := by
  simpa only [vertex, quotient, map_sum, map_one] using
    RingQuot.mkAlgHom_rel K (Relation.vertex_complete (G := G))

theorem arrow_corner (G : Grammar K V E) (a : E) :
    vertex G (G.target a) * arrow G a * vertex G (G.source a) = arrow G a := by
  simpa only [vertex, arrow, quotient, map_mul] using
    RingQuot.mkAlgHom_rel K (Relation.arrow_corner (G := G) a)

theorem declared_relation (G : Grammar K V E) {x y : Free K V E}
    (h : G.equations x y) : quotient G x = quotient G y :=
  RingQuot.mkAlgHom_rel K (Relation.declared h)

variable (G : Grammar K V E) (M : Type u) [AddCommGroup M] [Module K M]

/-- A collapsed realization specifies actual vertex and arrow operators. -/
structure CollapsedRealization where
  vertex : V → Module.End K M
  arrow : E → Module.End K M
  vertex_idempotent : ∀ v, vertex v * vertex v = vertex v
  vertex_orthogonal : ∀ v w, v ≠ w → vertex v * vertex w = 0
  vertex_complete : ∑ v, vertex v = 1
  arrow_corner : ∀ a, vertex (G.target a) * arrow a * vertex (G.source a) = arrow a
  declared : ∀ x y, G.equations x y →
    FreeAlgebra.lift K (Sum.elim vertex arrow) x =
      FreeAlgebra.lift K (Sum.elim vertex arrow) y

variable {G M}

@[ext] theorem CollapsedRealization.ext (X Y : CollapsedRealization G M)
    (hv : X.vertex = Y.vertex) (ha : X.arrow = Y.arrow) : X = Y := by
  cases X
  cases Y
  cases hv
  cases ha
  rfl

def CollapsedRealization.freeAction (X : CollapsedRealization G M) :
    Free K V E →ₐ[K] Module.End K M :=
  FreeAlgebra.lift K (Sum.elim X.vertex X.arrow)

theorem CollapsedRealization.respects (X : CollapsedRealization G M)
    {x y : Free K V E} (h : Relation G x y) : X.freeAction x = X.freeAction y := by
  cases h with
  | vertex_idempotent v =>
      simpa [freeAction, vertexWord] using X.vertex_idempotent v
  | vertex_orthogonal v w h =>
      simpa [freeAction, vertexWord] using X.vertex_orthogonal v w h
  | vertex_complete =>
      simpa [freeAction, vertexWord] using X.vertex_complete
  | arrow_corner a =>
      simpa [freeAction, vertexWord, arrowWord] using X.arrow_corner a
  | declared h => exact X.declared _ _ h

/-- The quotient action is constructed by the universal property. -/
def CollapsedRealization.action (X : CollapsedRealization G M) :
    Algebra G →ₐ[K] Module.End K M :=
  RingQuot.liftAlgHom K ⟨X.freeAction, fun _ _ h => X.respects h⟩

@[simp] theorem CollapsedRealization.action_quotient
    (X : CollapsedRealization G M) (x : Free K V E) :
    X.action (quotient G x) = X.freeAction x :=
  RingQuot.liftAlgHom_mkAlgHom_apply K X.freeAction (fun _ _ h => X.respects h) x

@[simp] theorem CollapsedRealization.action_vertex
    (X : CollapsedRealization G M) (v : V) :
    X.action (GrammarAlgebra.vertex G v) = X.vertex v := by
  simp [GrammarAlgebra.vertex, freeAction, vertexWord]

@[simp] theorem CollapsedRealization.action_arrow
    (X : CollapsedRealization G M) (a : E) :
    X.action (GrammarAlgebra.arrow G a) = X.arrow a := by
  simp [GrammarAlgebra.arrow, freeAction, arrowWord]

/-- Recover the declared generators from any unital algebra action. -/
def ofAction (ρ : Algebra G →ₐ[K] Module.End K M) : CollapsedRealization G M where
  vertex v := ρ (vertex G v)
  arrow a := ρ (arrow G a)
  vertex_idempotent v := by rw [← map_mul, vertex_idempotent]
  vertex_orthogonal v w h := by rw [← map_mul, vertex_orthogonal G h, map_zero]
  vertex_complete := by rw [← map_sum, vertex_complete, map_one]
  arrow_corner a := by rw [← map_mul, ← map_mul, arrow_corner]
  declared x y h := by
    have heq : FreeAlgebra.lift K
        (Sum.elim (fun v => ρ (vertex G v)) (fun a => ρ (arrow G a))) =
        ρ.comp (quotient G) := by
      apply FreeAlgebra.hom_ext
      funext s
      cases s <;> simp [vertex, arrow, vertexWord, arrowWord]
    rw [heq]
    exact congrArg ρ (declared_relation G h)

theorem ofAction_action (X : CollapsedRealization G M) : ofAction X.action = X := by
  apply CollapsedRealization.ext
  · funext v
    exact X.action_vertex v
  · funext a
    exact X.action_arrow a

theorem action_ofAction (ρ : Algebra G →ₐ[K] Module.End K M) : (ofAction ρ).action = ρ := by
  apply RingQuot.ringQuot_ext'
  apply FreeAlgebra.hom_ext
  funext s
  cases s with
  | inl v => exact (ofAction ρ).action_vertex v
  | inr a => exact (ofAction ρ).action_arrow a

/-- The full universal correspondence, with both inverse laws proved. -/
def collapsedActionEquiv : CollapsedRealization G M ≃ (Algebra G →ₐ[K] Module.End K M) where
  toFun := CollapsedRealization.action
  invFun := ofAction
  left_inv := ofAction_action
  right_inv := action_ofAction

def CollapsedRealization.projectors (X : CollapsedRealization G M) :
    LinearProjectorFamily K M V where
  proj := X.vertex
  idempotent v x := LinearMap.congr_fun (X.vertex_idempotent v) x
  orthogonal h x := LinearMap.congr_fun (X.vertex_orthogonal _ _ h) x
  complete x := by
    have h := LinearMap.congr_fun X.vertex_complete x
    simpa using h

/-- The vertex spaces are actual ranges, and their direct-sum coordinates are proved exact. -/
def CollapsedRealization.coordinates (X : CollapsedRealization G M) :
    M ≃ₗ[K] ((v : V) → LinearMap.range (X.vertex v)) :=
  X.projectors.exactPacketCoordinates

theorem CollapsedRealization.arrow_left (X : CollapsedRealization G M) (a : E) :
    X.vertex (G.target a) * X.arrow a = X.arrow a := by
  calc
    X.vertex (G.target a) * X.arrow a =
        X.vertex (G.target a) * (X.vertex (G.target a) * X.arrow a * X.vertex (G.source a)) :=
      congrArg (X.vertex (G.target a) * ·) (X.arrow_corner a).symm
    _ = X.vertex (G.target a) * X.arrow a * X.vertex (G.source a) := by
      simp only [← mul_assoc, X.vertex_idempotent]
    _ = X.arrow a := X.arrow_corner a

/-- Every arrow restricts to precisely its declared source and target vertex spaces. -/
def CollapsedRealization.typedArrow (X : CollapsedRealization G M) (a : E) :
    LinearMap.range (X.vertex (G.source a)) →ₗ[K]
      LinearMap.range (X.vertex (G.target a)) where
  toFun x := ⟨X.arrow a x, ⟨X.arrow a x, LinearMap.congr_fun (X.arrow_left a) x⟩⟩
  map_add' x y := by apply Subtype.ext; exact (X.arrow a).map_add x y
  map_smul' c x := by apply Subtype.ext; exact (X.arrow a).map_smul c x

end Komorebi.PaperIRelease.GrammarAlgebra
