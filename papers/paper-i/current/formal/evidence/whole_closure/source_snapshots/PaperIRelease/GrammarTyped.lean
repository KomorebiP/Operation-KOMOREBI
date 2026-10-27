import PaperIRelease.GrammarAlgebra

set_option autoImplicit false
set_option maxHeartbeats 2000000
set_option linter.unnecessarySimpa false
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

open scoped BigOperators
universe u
variable {K V E : Type u} [Field K] [Fintype V]

attribute [local instance] Classical.propDecidable

variable (G : Grammar K V E)

/-- Typed vector spaces and arrow maps, before imposing grammar equations. -/
structure TypedData where
  space : V → Type u
  [addCommGroup : ∀ v, AddCommGroup (space v)]
  [module : ∀ v, Module K (space v)]
  arrow : ∀ a : E, space (G.source a) →ₗ[K] space (G.target a)

attribute [instance] TypedData.addCommGroup TypedData.module

variable {G}

abbrev TypedData.total (X : TypedData G) := (v : V) → X.space v

def TypedData.vertexOperator (X : TypedData G) (v : V) : Module.End K X.total :=
  (LinearMap.single K X.space v).comp (LinearMap.proj v)

def TypedData.arrowOperator (X : TypedData G) (a : E) : Module.End K X.total :=
  (LinearMap.single K X.space (G.target a)).comp
    ((X.arrow a).comp (LinearMap.proj (G.source a)))

def TypedData.freeAction (X : TypedData G) : Free K V E →ₐ[K] Module.End K X.total :=
  FreeAlgebra.lift K (Sum.elim X.vertexOperator X.arrowOperator)

theorem TypedData.vertex_idempotent (X : TypedData G) (v : V) :
    X.vertexOperator v * X.vertexOperator v = X.vertexOperator v := by
  ext x w
  simp [vertexOperator, LinearMap.single_apply]

theorem TypedData.vertex_orthogonal (X : TypedData G) {v w : V} (h : v ≠ w) :
    X.vertexOperator v * X.vertexOperator w = 0 := by
  ext x z
  simp [vertexOperator, LinearMap.single_apply, Pi.single_eq_of_ne h]

theorem TypedData.vertex_complete (X : TypedData G) : ∑ v, X.vertexOperator v = 1 := by
  apply LinearMap.ext
  intro x
  change (∑ v, X.vertexOperator v) x = x
  simp only [LinearMap.sum_apply, vertexOperator, LinearMap.comp_apply, LinearMap.proj_apply]
  exact LinearMap.sum_single_apply X.space x

theorem TypedData.arrow_corner (X : TypedData G) (a : E) :
    X.vertexOperator (G.target a) * X.arrowOperator a * X.vertexOperator (G.source a) =
      X.arrowOperator a := by
  ext x v
  simp [vertexOperator, arrowOperator, LinearMap.single_apply]

/-- A typed realization is precisely a family whose declared relations vanish. -/
structure TypedRealization extends TypedData G where
  declared : ∀ x y, G.equations x y → toTypedData.freeAction x = toTypedData.freeAction y

abbrev TypedRealization.collapse (X : TypedRealization (G := G)) :
    CollapsedRealization G X.total where
  vertex := X.vertexOperator
  arrow := X.arrowOperator
  vertex_idempotent := X.vertex_idempotent
  vertex_orthogonal _ _ h := X.vertex_orthogonal h
  vertex_complete := X.vertex_complete
  arrow_corner := X.arrow_corner
  declared := X.declared

variable {M : Type u} [AddCommGroup M] [Module K M]

/-- Split an arbitrary collapsed action using the actual vertex-idempotent ranges. -/
abbrev CollapsedRealization.splitData (X : CollapsedRealization G M) : TypedData G where
  space v := LinearMap.range (X.vertex v)
  arrow := X.typedArrow

@[simp] theorem CollapsedRealization.coordinates_apply (X : CollapsedRealization G M)
    (x : M) (v : V) : (X.coordinates x v : M) = X.vertex v x := rfl

theorem CollapsedRealization.vertex_on_range (X : CollapsedRealization G M)
    (v : V) (x : LinearMap.range (X.vertex v)) : X.vertex v x = (x : M) := by
  rcases x.property with ⟨y, hy⟩
  rw [← hy]
  exact LinearMap.congr_fun (X.vertex_idempotent v) y

theorem CollapsedRealization.arrow_right (X : CollapsedRealization G M) (a : E) :
    X.arrow a * X.vertex (G.source a) = X.arrow a := by
  calc
    X.arrow a * X.vertex (G.source a) =
        (X.vertex (G.target a) * X.arrow a * X.vertex (G.source a)) * X.vertex (G.source a) :=
      congrArg (· * X.vertex (G.source a)) (X.arrow_corner a).symm
    _ = X.vertex (G.target a) * X.arrow a * X.vertex (G.source a) := by
      simp only [mul_assoc, X.vertex_idempotent]
    _ = X.arrow a := X.arrow_corner a

/-- Analysis respects each declared vertex generator. -/
theorem CollapsedRealization.coordinates_vertex (X : CollapsedRealization G M)
    (v : V) (x : M) :
    X.coordinates (X.vertex v x) = X.splitData.vertexOperator v (X.coordinates x) := by
  ext w
  change X.vertex w (X.vertex v x) =
    ((Pi.single v (X.coordinates x v) : (z : V) → LinearMap.range (X.vertex z)) w : M)
  by_cases h : w = v
  · subst w
    simp only [Pi.single_eq_same, coordinates_apply]
    exact LinearMap.congr_fun (X.vertex_idempotent v) x
  · have hvw : X.vertex w (X.vertex v x) = 0 :=
      LinearMap.congr_fun (X.vertex_orthogonal w v h) x
    rw [hvw]
    simp [Pi.single_eq_of_ne h]

/-- Analysis respects each declared arrow generator. -/
theorem CollapsedRealization.coordinates_arrow (X : CollapsedRealization G M)
    (a : E) (x : M) :
    X.coordinates (X.arrow a x) = X.splitData.arrowOperator a (X.coordinates x) := by
  ext v
  change X.vertex v (X.arrow a x) =
    ((Pi.single (G.target a) (X.typedArrow a (X.coordinates x (G.source a))) :
      (z : V) → LinearMap.range (X.vertex z)) v : M)
  by_cases h : v = G.target a
  · subst v
    simp only [Pi.single_eq_same]
    have hl := LinearMap.congr_fun (X.arrow_left a) x
    have hr := LinearMap.congr_fun (X.arrow_right a) x
    exact hl.trans hr.symm
  · have hz : X.vertex v * X.arrow a = 0 := by
      calc
        X.vertex v * X.arrow a = X.vertex v * (X.vertex (G.target a) * X.arrow a) :=
          congrArg (X.vertex v * ·) (X.arrow_left a).symm
        _ = 0 := by rw [← mul_assoc, X.vertex_orthogonal v (G.target a) h, zero_mul]
    have hz' := LinearMap.congr_fun hz x
    simpa [Pi.single_eq_of_ne h] using hz'

/-- Generator intertwining extends to every free-algebra expression. -/
theorem CollapsedRealization.coordinates_freeAction (X : CollapsedRealization G M)
    (a : Free K V E) (x : M) :
    X.coordinates (X.freeAction a x) = X.splitData.freeAction a (X.coordinates x) := by
  induction a using FreeAlgebra.induction generalizing x with
  | grade0 c => simp
  | grade1 s =>
      cases s with
      | inl v => simpa [freeAction, TypedData.freeAction] using X.coordinates_vertex v x
      | inr a => simpa [freeAction, TypedData.freeAction] using X.coordinates_arrow a x
  | mul a b ha hb =>
      simp only [map_mul, Module.End.mul_apply]
      rw [ha, hb]
  | add a b ha hb =>
      simp only [map_add, LinearMap.add_apply]
      rw [ha, hb]

/-- The split arrow family satisfies every original grammar relation. -/
abbrev CollapsedRealization.split (X : CollapsedRealization G M) : TypedRealization (G := G) where
  toTypedData := X.splitData
  declared a b h := by
    apply LinearMap.ext
    intro x
    obtain ⟨y, rfl⟩ := X.coordinates.surjective x
    rw [← X.coordinates_freeAction a, ← X.coordinates_freeAction b]
    exact congrArg (fun f : Module.End K M => X.coordinates (f y)) (X.declared a b h)

end Komorebi.PaperIRelease.GrammarAlgebra
