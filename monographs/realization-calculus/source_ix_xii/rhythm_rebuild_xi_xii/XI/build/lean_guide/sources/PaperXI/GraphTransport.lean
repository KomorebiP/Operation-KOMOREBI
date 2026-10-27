import Mathlib.Combinatorics.Quiver.Symmetric
import Mathlib.LinearAlgebra.Pi
import Mathlib.Tactic

/-! Paper XI, Section 14. Actual typed path transport on the symmetrification
of a quiver. An original arrow is one chosen orientation of an underlying edge;
parallel arrows and self-loops keep their identities. Concatenation traverses
its left argument first. -/
set_option autoImplicit false

namespace PaperXI.GraphTransport

open Quiver

variable {K α : Type*} [Field K] [Quiver α]
/-- Traversals retain the positive/negative tag of each original edge. -/
abbrev Traversal (u v : α) := @Quiver.Hom (Symmetrify α) _ u v

/-- Typed walks in the symmetrified original quiver. -/
abbrev Walk (u v : α) := @Quiver.Path (Symmetrify α) _ u v

variable {V : α → Type*} [iV : ∀ u, AddCommGroup (V u)] [mV : ∀ u, Module K (V u)]

/-- The original additive structure on a fiber over the vertex synonym. -/
@[instance_reducible] def symmetrifyAdd (u : Symmetrify α) : AddCommGroup (V u) := iV u
attribute [local instance] symmetrifyAdd

/-- The original module structure on a fiber over the vertex synonym. -/
@[instance_reducible] def symmetrifyModule (u : Symmetrify α) : Module K (V u) := mV u
attribute [local instance] symmetrifyModule

/-- Edge transport on both formal orientations of an original arrow. -/
def edge (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (e : u ⟶ v) : V u ≃ₗ[K] V v :=
  match e with
  | Sum.inl a => A a
  | Sum.inr a => (A a).symm

@[simp] theorem edge_inl (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : α} (e : u ⟶ v) : edge A (Sum.inl e) = A e := rfl

@[simp] theorem edge_inr (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : α} (e : u ⟶ v) : edge A (Sum.inr e) = (A e).symm := rfl

@[simp] theorem edge_reverse (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (e : u ⟶ v) :
    edge A (Quiver.reverse e) = (edge A e).symm := by
  cases e using Sum.rec <;> rfl

/-- Transport along an actual path; the last traversal acts last. -/
def path (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u : Symmetrify α} : ∀ {v : Symmetrify α}, Path u v → (V u ≃ₗ[K] V v)
  | _, .nil => LinearEquiv.refl K (V u)
  | _, .cons p e => (path A p).trans (edge A e)

@[simp] theorem nil (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (u : Symmetrify α) : path A (Path.nil : Path u u) = LinearEquiv.refl K (V u) := rfl

@[simp] theorem cons (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v w : Symmetrify α} (p : Path u v) (e : v ⟶ w) :
    path A (p.cons e) = (path A p).trans (edge A e) := rfl

@[simp] theorem toPath (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (e : u ⟶ v) : path A e.toPath = edge A e := by
  ext x
  rfl

@[simp] theorem comp (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v w : Symmetrify α} (p : Path u v) (q : Path v w) :
    path A (p.comp q) = (path A p).trans (path A q) := by
  induction q with
  | nil => ext x; rfl
  | cons q e ih =>
    rw [Path.comp_cons, cons, ih, cons]
    rfl

@[simp] theorem reverse (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (p : Path u v) : path A p.reverse = (path A p).symm := by
  induction p with
  | nil => rfl
  | cons p e ih =>
    rw [Path.reverse, comp, toPath, edge_reverse, ih, cons]
    rfl

@[simp] theorem path_reverse_cancel
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (p : Path u v) :
    path A (p.comp p.reverse) = LinearEquiv.refl K (V u) := by
  ext x
  simp

@[simp] theorem reverse_path_cancel
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v : Symmetrify α} (p : Path u v) :
    path A (p.reverse.comp p) = LinearEquiv.refl K (V v) := by
  ext x
  simp

/-- An inverse pair may be removed inside an arbitrary typed path. -/
theorem cancel (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    {u v w z : Symmetrify α} (p : Path u v) (e : v ⟶ w) (q : Path v z) :
    path A (((p.cons e).cons (Quiver.reverse e)).comp q) = path A (p.comp q) := by
  rw [comp, comp, cons, cons, edge_reverse]
  ext x
  simp

variable {W : α → Type*} [iW : ∀ u, AddCommGroup (W u)] [mW : ∀ u, Module K (W u)]

/-- Intertwining original edges also intertwines their formal inverses. -/
theorem gauge_edge
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (U : ∀ u, V u →ₗ[K] W u)
    (hU : ∀ {u v : α} (e : u ⟶ v) (x : V u), U v (A e x) = B e (U u x))
    {u v : Symmetrify α} (e : u ⟶ v) (x : V u) :
    U v (edge A e x) = edge B e (U u x) := by
  cases e using Sum.rec with
  | inl e => exact hU e x
  | inr e =>
    change U v ((A e).symm x) = (B e).symm (U u x)
    apply (B e).injective
    simpa using (hU e ((A e).symm x)).symm

/-- The actual edge equations imply all path equations by induction. -/
theorem gauge_path
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (U : ∀ u, V u →ₗ[K] W u)
    (hU : ∀ {u v : α} (e : u ⟶ v) (x : V u), U v (A e x) = B e (U u x))
    {u v : Symmetrify α} (p : Path u v) (x : V u) :
    U v (path A p x) = path B p (U u x) := by
  induction p with
  | nil => rfl
  | cons p e ih =>
    change U _ (edge A e (path A p x)) = edge B e (path B p (U _ x))
    rw [gauge_edge A B U hU, ih]

/-- Equivalence-valued formulation of the same path intertwining law. -/
theorem gauge_path_equiv
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (U : ∀ u, V u ≃ₗ[K] W u)
    (hU : ∀ {u v : α} (e : u ⟶ v), (A e).trans (U v) = (U u).trans (B e))
    {u v : Symmetrify α} (p : Path u v) :
    (path A p).trans (U v) = (U u).trans (path B p) := by
  ext x
  exact gauge_path A B (fun u => (U u).toLinearMap)
    (fun e y => LinearEquiv.congr_fun (hU e) y) p x

end PaperXI.GraphTransport
