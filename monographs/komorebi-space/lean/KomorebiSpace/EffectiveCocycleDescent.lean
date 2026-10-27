import KomorebiSpace.CocycleDescent

set_option autoImplicit false

/-!
# Effective descent of cocycles with specified overlap isomorphisms

Patches need not have equal labels. An overlap gauge from patch i to patch j
has values a_ij, with a_ik = a_jk * a_ij. A composition cover lets us choose
local reference frames, strictify the labels, and invoke strict cocycle gluing.
The result includes its local gauges and their compatibility with the supplied
overlap gauges. No site, topology, or unrestricted stack condition is assumed.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z}
variable (F : GroupViewSystem V G)

namespace PatchCocycle
variable {F}

/-- A change of frame inside a full patch. -/
def gauge {S : Set V} (a : ∀ x : S, G x.val) (c : F.PatchCocycle S) :
    F.PatchCocycle S where
  edge := fun {x y} f => a x * c.edge f * (F.pull f (a y))⁻¹
  edge_id := by intro x; rw [c.edge_id, F.pull_id]; simp
  edge_comp := by
    intro x y z f g
    simp only [c.edge_comp, F.pull_comp, map_mul, map_inv]
    group

@[simp] theorem gauge_edge {S : Set V} (a : ∀ x : S, G x.val)
    (c : F.PatchCocycle S) {x y : S} (f : x.val ⟶ y.val) :
    (c.gauge a).edge f = a x * c.edge f * (F.pull f (a y))⁻¹ := rfl
end PatchCocycle

/-- Descent data with actual overlap gauges, not just pairwise existence of an isomorphism. -/
structure CocycleDescentData (U : I → Set V) where
  patch : ∀ i, F.PatchCocycle (U i)
  change : ∀ (i j : I) (x : V), x ∈ U i → x ∈ U j → G x
  change_edge : ∀ (i j : I) (x y : V) (hxi : x ∈ U i) (hyi : y ∈ U i)
      (hxj : x ∈ U j) (hyj : y ∈ U j) (f : x ⟶ y),
    change i j x hxi hxj * (patch i).edge (a := ⟨x,hxi⟩) (b := ⟨y,hyi⟩) f *
        (F.pull f (change i j y hyi hyj))⁻¹ =
      (patch j).edge (a := ⟨x,hxj⟩) (b := ⟨y,hyj⟩) f
  change_comp : ∀ (i j k : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j) (hk : x ∈ U k),
    change i k x hi hk = change j k x hj hk * change i j x hi hj

namespace CocycleDescentData
variable {F} {U : I → Set V}

/-- Identity and inverse overlap laws follow from the triple-overlap equation. -/
theorem change_self (D : F.CocycleDescentData U) (i : I) (x : V) (hi : x ∈ U i) :
    D.change i i x hi hi = 1 := by
  have h := D.change_comp i i i x hi hi hi
  have h' : D.change i i x hi hi * 1 = D.change i i x hi hi * D.change i i x hi hi := by
    simpa only [mul_one] using h
  exact (mul_left_cancel h').symm

theorem change_reverse (D : F.CocycleDescentData U) (i j : I) (x : V)
    (hi : x ∈ U i) (hj : x ∈ U j) :
    D.change j i x hj hi = (D.change i j x hi hj)⁻¹ := by
  have h := D.change_comp i j i x hi hj hi
  rw [D.change_self] at h
  exact eq_inv_of_mul_eq_one_left h.symm

/-- A global representative with isomorphisms to all local cocycles. -/
structure Effectuation (D : F.CocycleDescentData U) where
  global : F.Cocycle
  compare : ∀ i, ∀ x : U i, G x.val
  local_eq : ∀ (i : I) (x y : U i) (f : x.val ⟶ y.val),
    compare i x * global.edge f * (F.pull f (compare i y))⁻¹ = (D.patch i).edge f
  overlap : ∀ (i j : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j),
    compare j ⟨x,hj⟩ = D.change i j x hi hj * compare i ⟨x,hi⟩

/-- Choose a reference patch independently at each view. This is choice data. -/
noncomputable def reference (h : ViewSystem.ObjectCover U) (x : V) : I :=
  Classical.choose (h x)

omit [Category.{v} V] in
theorem reference_mem (h : ViewSystem.ObjectCover U) (x : V) :
    x ∈ U (reference h x) := Classical.choose_spec (h x)

/-- The gauge from the selected reference frame at x into patch i. -/
noncomputable def frame (D : F.CocycleDescentData U) (h : ViewSystem.ObjectCover U)
    (i : I) (x : U i) : G x.val :=
  D.change (reference h x.val) i x.val (reference_mem h x.val) x.property

theorem frame_overlap (D : F.CocycleDescentData U) (h : ViewSystem.ObjectCover U)
    (i j : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j) :
    D.frame h j ⟨x,hj⟩ = D.change i j x hi hj * D.frame h i ⟨x,hi⟩ :=
  D.change_comp (reference h x) i j x (reference_mem h x) hi hj

/-- Rewrite every patch in the independently selected reference frames. -/
noncomputable def strictify (D : F.CocycleDescentData U) (h : ViewSystem.ObjectCover U) :
    F.CocycleMatching U where
  patch := fun i => (D.patch i).gauge (fun x => (D.frame h i x)⁻¹)
  agree := by
    intro i j x y hxi hyi hxj hyj f
    simp only [PatchCocycle.gauge_edge, map_inv, inv_inv]
    rw [D.frame_overlap h i j x hxi hxj, D.frame_overlap h i j y hyi hyj,
      ← D.change_edge i j x y hxi hyi hxj hyj f, map_mul]
    group

/-- Construct an effectuation from arbitrary coherent overlap isomorphisms. -/
noncomputable def effectuate (D : F.CocycleDescentData U) (h : CompositionCover U) :
    D.Effectuation where
  global := (D.strictify (ViewSystem.TransitionCover.objectCover U h.transitionCover)).glue h
  compare := D.frame (ViewSystem.TransitionCover.objectCover U h.transitionCover)
  local_eq := by
    intro i x y f
    let ho := ViewSystem.TransitionCover.objectCover U h.transitionCover
    have he := (D.strictify ho).assembleEdge_local h.transitionCover i x.val y.val
      x.property y.property f
    change D.frame ho i x * (D.strictify ho).assembleEdge h.transitionCover f *
      (F.pull f (D.frame ho i y))⁻¹ = (D.patch i).edge f
    rw [he]
    simp only [strictify, PatchCocycle.gauge_edge, map_inv, inv_inv]
    group
  overlap := D.frame_overlap (ViewSystem.TransitionCover.objectCover U h.transitionCover)

/-- The existence conclusion is derived, not a field in descent data. -/
theorem effective (D : F.CocycleDescentData U) (h : CompositionCover U) :
    Nonempty D.Effectuation := ⟨D.effectuate h⟩

/-- Each local identification satisfies the original overlap law. -/
theorem effectuate_overlap (D : F.CocycleDescentData U) (h : CompositionCover U)
    (i j : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j) :
    (D.effectuate h).compare j ⟨x,hj⟩ =
      D.change i j x hi hj * (D.effectuate h).compare i ⟨x,hi⟩ :=
  (D.effectuate h).overlap i j x hi hj

/-- Inverse form of the local comparison equation, useful for uniqueness. -/
theorem Effectuation.global_local {D : F.CocycleDescentData U} (E : D.Effectuation)
    (i : I) (x y : U i) (f : x.val ⟶ y.val) :
    E.global.edge f = (E.compare i x)⁻¹ * (D.patch i).edge f * F.pull f (E.compare i y) := by
  rw [← E.local_eq i x y f]
  group

end CocycleDescentData
end GroupViewSystem
end KomorebiSpace
