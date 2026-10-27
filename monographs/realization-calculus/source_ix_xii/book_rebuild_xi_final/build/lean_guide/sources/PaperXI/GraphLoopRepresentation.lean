import PaperXI.GraphLoop
import PaperXI.GraphTransport

/-!
# Holonomy as a homomorphism on actual reduced graph loops

The free-groupoid extension of the edge system agrees with the recursively
defined path transport on every represented path. Surjectivity of path classes
then identifies intertwining all based paths with conjugacy of the resulting
honest group homomorphisms.
-/

namespace PaperXI.GraphLoop

open CategoryTheory

attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

universe u v k w z

variable {α : Type u} [Quiver.{v} α] {K : Type k} [Field K]
variable {V : α → Type w} [∀ u, AddCommGroup (V u)] [∀ u, Module K (V u)]

/-- A vertex regarded as its assigned vector space in the groupoid of fiber isomorphisms. -/
structure Fiber (K : Type k) (V : α → Type w) where
  vertex : α

instance fiberGroupoid : Groupoid (Fiber K V) where
  Hom u v := V u.vertex ≃ₗ[K] V v.vertex
  id u := LinearEquiv.refl K (V u.vertex)
  comp f g := f.trans g
  id_comp f := by ext x; rfl
  comp_id f := by ext x; rfl
  assoc f g h := by ext x; rfl
  inv f := f.symm
  inv_comp f := f.symm_trans_self
  comp_inv f := f.self_trans_symm

/-- The original edge system as a prefunctor into actual linear isomorphisms. -/
def edgePrefunctor (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) :
    α ⥤q Fiber K V where
  obj u := ⟨u⟩
  map e := A e

/-- The uniquely extended transport functor on reduced paths. -/
def transportFunctor (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) :
    Quiver.FreeGroupoid α ⥤ Fiber K V :=
  Quiver.FreeGroupoid.lift (edgePrefunctor A)

/-- Transport of a morphism of the actual graph groupoid. -/
def transport (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : α} (f : vertex u ⟶ vertex v) : V u ≃ₗ[K] V v :=
  (transportFunctor A).map f

@[simp] theorem transport_id
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) (u : α) :
    transport A (𝟙 (vertex u)) = LinearEquiv.refl K (V u) :=
  (transportFunctor A).map_id _

@[simp] theorem transport_comp
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v w : α} (f : vertex u ⟶ vertex v) (g : vertex v ⟶ vertex w) :
    transport A (f ≫ g) = (transport A f).trans (transport A g) :=
  (transportFunctor A).map_comp f g

@[simp] theorem transport_edge
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Quiver.Symmetrify α} (e : u ⟶ v) :
    transport A (pathClass e.toPath) = GraphTransport.edge A e := by
  cases e using Sum.casesOn <;> ext x <;> rfl

/-- The quotient construction computes exactly the manuscript's path transport. -/
@[simp] theorem transport_pathClass
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Quiver.Symmetrify α} (p : Quiver.Path u v) :
    transport A (pathClass p) = GraphTransport.path A p := by
  induction p with
  | nil => exact transport_id A _
  | cons p e ih =>
    change transport A (pathClass p ≫ pathClass e.toPath) = _
    calc
      transport A (pathClass p ≫ pathClass e.toPath) =
          (transport A (pathClass p)).trans (transport A (pathClass e.toPath)) :=
        transport_comp A (pathClass p) (pathClass e.toPath)
      _ = GraphTransport.path A (p.cons e) := by
        rw [ih, transport_edge]
        rfl

/-- Based holonomy as an honest representation by linear automorphisms. -/
def holonomy (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) (r : α) :
    Loop r →* (V r ≃ₗ[K] V r) where
  toFun := transport A
  map_one' := transport_id A r
  map_mul' x y := transport_comp A y x

@[simp] theorem holonomy_loopClass
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {r : α} (p : @Quiver.Path (Quiver.Symmetrify α) _ r r) :
    holonomy A r (loopClass p) = GraphTransport.path A p :=
  transport_pathClass A p

variable {W : α → Type z} [∀ u, AddCommGroup (W u)] [∀ u, Module K (W u)]

/-- Conjugacy of the two actual loop representations by a specified root isomorphism. -/
def Conjugates
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    {r : α} (U : V r ≃ₗ[K] W r) : Prop :=
  ∀ g : Loop r, ((U.symm.trans (holonomy A r g)).trans U) = holonomy B r g

/-- Intertwining every based path is equivalent to conjugacy on the reduced loop group. -/
theorem conjugates_iff_paths
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    {r : α} (U : V r ≃ₗ[K] W r) :
    Conjugates A B U ↔
      ∀ (p : @Quiver.Path (Quiver.Symmetrify α) _ r r) (x : V r),
        U (GraphTransport.path A p x) = GraphTransport.path B p (U x) := by
  constructor
  · intro h p x
    have hp := LinearEquiv.congr_fun (h (loopClass p)) (U x)
    simpa using hp
  · intro h g
    obtain ⟨p, rfl⟩ := loopClass_surjective r g
    ext y
    simpa using h p (U.symm y)

/-- The unbased representation comparison allows the conjugating root map to vary. -/
theorem exists_conjugates_iff_paths
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v)) (r : α) :
    (∃ U : V r ≃ₗ[K] W r, Conjugates A B U) ↔
      ∃ U : V r ≃ₗ[K] W r,
        ∀ (p : @Quiver.Path (Quiver.Symmetrify α) _ r r) (x : V r),
          U (GraphTransport.path A p x) = GraphTransport.path B p (U x) := by
  exact exists_congr fun U => conjugates_iff_paths A B U

end PaperXI.GraphLoop
