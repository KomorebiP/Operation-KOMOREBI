import PaperXI.GraphTree
import PaperXI.GraphLoopRepresentation
import PaperXI.ScalarHolonomy

/-!
# Independent scalar tests on fundamental graph cycles

Every assignment of unit scalars to the chords of the constructed rooted tree
is realized by actual one-dimensional edge transport: tree edges carry one and
each chord carries its prescribed scalar. Thus the scalar cycle tests can vary
independently. The same realization gives characters on the actual reduced loop
group and its abelianization.
-/

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section

namespace PaperXI.GraphChordCharacters

variable {K α : Type*} [Field K] [Quiver α] {r : α}

/-- Prescribed chord weights, extended by one on the selected tree. -/
def weight (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ)
    (e : GraphTree.Edge α) : Kˣ := by
  classical
  exact if h : e ∈ GraphTree.treeEdges T then 1 else t ⟨e, h⟩

@[simp] theorem weight_tree (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ)
    (e : GraphTree.Edge α) (h : e ∈ GraphTree.treeEdges T) : weight T t e = 1 := by
  simp [weight, h]

@[simp] theorem weight_chord (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ)
    (e : GraphTree.Chord T) : weight T t e.val = t e := by
  rw [weight, dite_eq_right e.property]
  rfl

/-- An actual one-dimensional linear transport system realizing these edge weights. -/
def edgeSystem (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ)
    {u v : α} (e : u ⟶ v) : K ≃ₗ[K] K :=
  ScalarHolonomy.scalarHom (weight T t ⟨u, v, e⟩)

@[simp] theorem edgeSystem_chord (T : GraphTree.Rooted α r)
    (t : GraphTree.Chord T → Kˣ) (e : GraphTree.Chord T) :
    edgeSystem T t e.val.2.2 = ScalarHolonomy.scalarHom (t e) := by
  simp [edgeSystem]

/-- Both directions of every selected tree edge have identity transport. -/
theorem traversal_tree (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ)
    {u v : α} (e : GraphTree.Traversal u v)
    (h : GraphTree.underlying e ∈ GraphTree.treeEdges T) :
    GraphTransport.edge (α := α) (V := fun _ => K) (edgeSystem T t) e = LinearEquiv.refl K K := by
  cases e using Sum.casesOn with
  | inl e =>
    change ScalarHolonomy.scalarHom (weight T t ⟨u, v, e⟩) = _
    change (⟨u, v, e⟩ : GraphTree.Edge α) ∈ GraphTree.treeEdges T at h
    rw [weight_tree T t _ h, map_one]
    rfl
  | inr e =>
    change (ScalarHolonomy.scalarHom (weight T t ⟨v, u, e⟩)).symm = _
    change (⟨v, u, e⟩ : GraphTree.Edge α) ∈ GraphTree.treeEdges T at h
    rw [weight_tree T t _ h, map_one]
    rfl

/-- The recursively constructed root paths use only identity edge transports. -/
@[simp] theorem rootPath_transport (T : GraphTree.Rooted α r)
    (t : GraphTree.Chord T → Kˣ) (v : α) :
    GraphTransport.path (α := α) (V := fun _ => K) (edgeSystem T t) (GraphTree.rootPath T v) =
      LinearEquiv.refl K K := by
  apply GraphTree.rooted_induction T (fun v =>
    GraphTransport.path (α := α) (V := fun _ => K) (edgeSystem T t) (GraphTree.rootPath T v) =
      LinearEquiv.refl K K)
  · rw [GraphTree.rootPath_root]
    rfl
  · intro a ha
    rw [← GraphTree.rootPath_parent, GraphTransport.cons, ha,
      traversal_tree T t (T.parentEdge a) (GraphTree.mem_treeEdges T a)]
    rfl

/-- The based fundamental cycle associated with one actual chord. -/
def chordLoop (T : GraphTree.Rooted α r) (e : GraphTree.Chord T) :
    GraphTree.Path r r :=
  ((GraphTree.rootPath T e.val.1).cons (Sum.inl e.val.2.2)).comp
    (GraphTree.rootPath T e.val.2.1).reverse

/-- Each fundamental cycle recovers exactly its freely assigned scalar. -/
@[simp] theorem chordLoop_transport (T : GraphTree.Rooted α r)
    (t : GraphTree.Chord T → Kˣ) (e : GraphTree.Chord T) :
    GraphTransport.path (α := α) (V := fun _ => K) (edgeSystem T t) (chordLoop (α := α) T e) =
      ScalarHolonomy.scalarHom (t e) := by
  ext x
  simp [chordLoop]

@[simp] theorem chordLoop_holonomy (T : GraphTree.Rooted α r)
    (t : GraphTree.Chord T → Kˣ) (e : GraphTree.Chord T) :
    GraphLoop.holonomy (α := α) (V := fun _ => K) (edgeSystem T t) r (GraphLoop.loopClass (chordLoop (α := α) T e)) =
      ScalarHolonomy.scalarHom (t e) := by
  rw [GraphLoop.holonomy_loopClass, chordLoop_transport]

/-- Every invertible linear map on the scalar field is multiplication by a unit. -/
theorem field_equiv_scalar (L : K ≃ₗ[K] K) :
    ∃ c : Kˣ, L = ScalarHolonomy.scalarHom c := by
  let c : Kˣ := Units.mk0 (L 1) (L.map_ne_zero_iff.mpr one_ne_zero)
  refine ⟨c, ?_⟩
  ext x
  have h : L x = x * L 1 := by
    simpa only [smul_eq_mul, mul_one] using L.map_smul x (1 : K)
  exact h.trans (mul_comm x (L 1))

/-- The one-dimensional loop representation is scalar on every reduced loop. -/
theorem holonomy_isScalar (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ) :
    ScalarHolonomy.IsScalar (GraphLoop.holonomy (α := α) (V := fun _ => K) (edgeSystem T t) r) := by
  intro g
  exact field_equiv_scalar _

/-- The actual scalar character realizing a prescribed tuple of chord tests. -/
def character (T : GraphTree.Rooted α r) (t : GraphTree.Chord T → Kˣ) :
    GraphLoop.Loop r →* Kˣ :=
  ScalarHolonomy.character (GraphLoop.holonomy (α := α) (V := fun _ => K) (edgeSystem T t) r) (holonomy_isScalar T t)

@[simp] theorem character_chord (T : GraphTree.Rooted α r)
    (t : GraphTree.Chord T → Kˣ) (e : GraphTree.Chord T) :
    character T t (GraphLoop.loopClass (chordLoop (α := α) T e)) = t e := by
  apply ScalarHolonomy.scalarHom_injective (V := K)
  rw [character, ScalarHolonomy.character_spec, chordLoop_holonomy]

/-- Arbitrary scalar tests on the actual fundamental cycles are simultaneously realizable. -/
theorem character_tests_surjective (T : GraphTree.Rooted α r) :
    Function.Surjective (fun χ : GraphLoop.Loop r →* Kˣ =>
      fun e : GraphTree.Chord T => χ (GraphLoop.loopClass (chordLoop (α := α) T e))) := by
  intro t
  exact ⟨character T t, funext (character_chord T t)⟩

/-- Their independence persists for characters of the actual loop abelianization. -/
theorem homology_tests_surjective (T : GraphTree.Rooted α r) :
    Function.Surjective (fun χ : GraphLoop.H1 r →* Kˣ =>
      fun e : GraphTree.Chord T =>
        χ (GraphLoop.homologyClass r (GraphLoop.loopClass (chordLoop (α := α) T e)))) := by
  intro t
  refine ⟨GraphLoop.factorCharacter r Kˣ (character T t), ?_⟩
  funext e
  exact character_chord T t e

end PaperXI.GraphChordCharacters
