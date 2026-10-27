import Mathlib.Combinatorics.Quiver.Symmetric
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Nat.Find
import Mathlib.Tactic

/-! A rooted spanning tree of a connected quiver, with the identities of the
original edges retained. The construction selects a predecessor along a
shortest path in the symmetrified quiver. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.GraphTree

universe u v
variable {α : Type u} [Quiver.{v} α]

/-- The original edges, counted once with their chosen orientation. -/
abbrev Edge (α : Type u) [Quiver.{v} α] := Σ a b : α, (a ⟶ b)

/-- Traversals include both formal orientations, including for a self-loop. -/
abbrev Traversal (a b : α) := @Quiver.Hom (Quiver.Symmetrify α) _ a b

/-- Paths in the graph use its formal symmetrification. -/
abbrev Path (a b : α) := @Quiver.Path (Quiver.Symmetrify α) _ a b

/-- Connectedness is actual reachability by typed edge paths. -/
def Connected : Prop := ∀ a b : α, Nonempty (Path a b)

/-- Rooted predecessor data with strictly decreasing depth. -/
structure Rooted (α : Type u) [Quiver.{v} α] (r : α) where
  depth : α → ℕ
  depth_root : depth r = 0
  parent : {a : α // a ≠ r} → α
  parentEdge : ∀ a : {a : α // a ≠ r}, Traversal (parent a) a.val
  parent_depth : ∀ a : {a : α // a ≠ r}, depth (parent a) < depth a.val

variable (r : α) (hc : Connected (α := α))

include hc in
private theorem exists_length (a : α) : ∃ n, ∃ p : Path r a, p.length = n := by
  obtain ⟨p⟩ := hc r a
  exact ⟨p.length, p, rfl⟩

/-- The minimum number of traversals from the root. -/
def distance (a : α) : ℕ := by
  classical
  exact Nat.find (exists_length r hc a)

theorem distance_le (a : α) (p : Path r a) : distance r hc a ≤ p.length := by
  classical
  exact Nat.find_min' (exists_length r hc a) ⟨p, rfl⟩

theorem distance_root : distance r hc r = 0 := by
  have h := distance_le r hc r Quiver.Path.nil
  exact Nat.eq_zero_of_le_zero h

private theorem exists_predecessor (a : α) (ha : a ≠ r) :
    ∃ b : α, Nonempty (Traversal b a) ∧ distance r hc b < distance r hc a := by
  classical
  obtain ⟨p, hp⟩ := Nat.find_spec (exists_length r hc a)
  cases p with
  | nil => exact (ha rfl).elim
  | @cons b a p e =>
    refine ⟨b, ⟨e⟩, ?_⟩
    have hm := distance_le r hc b p
    simp only [Quiver.Path.length_cons] at hp
    change _ = distance r hc a at hp
    omega

/-- Connectedness constructs a rooted spanning tree; none is supplied as input. -/
def ofConnected : Rooted α r where
  depth := distance r hc
  depth_root := distance_root r hc
  parent a := Classical.choose (exists_predecessor r hc a.val a.property)
  parentEdge a := Classical.choice
    (Classical.choose_spec (exists_predecessor r hc a.val a.property)).1
  parent_depth a :=
    (Classical.choose_spec (exists_predecessor r hc a.val a.property)).2

variable {r}

/-- The actual root path, constructed by recursion on decreasing depth. -/
def rootPath (T : Rooted α r) (a : α) : Path r a := by
  classical
  exact if h : a = r then h.symm ▸ Quiver.Path.nil
  else (rootPath T (T.parent ⟨a, h⟩)).cons (T.parentEdge ⟨a, h⟩)
termination_by T.depth a
decreasing_by exact T.parent_depth ⟨a, h⟩

variable (T : Rooted α r)

theorem rootPath_root : rootPath T r = Quiver.Path.nil := by
  rw [rootPath]
  simp

theorem rootPath_parent (a : {a : α // a ≠ r}) :
    (rootPath T (T.parent a)).cons (T.parentEdge a) = rootPath T a.val := by
  conv_rhs => rw [rootPath]
  rw [dite_eq_right a.property]

/-- Induction along the constructed rooted tree follows decreasing depth. -/
theorem rooted_induction (P : α → Prop) (hr : P r)
    (step : ∀ a : {a : α // a ≠ r}, P (T.parent a) → P a.val) (a : α) : P a := by
  classical
  by_cases h : a = r
  · simpa only [h] using hr
  · exact step ⟨a, h⟩ (rooted_induction P hr step (T.parent ⟨a, h⟩))
termination_by T.depth a
decreasing_by exact T.parent_depth ⟨a, h⟩

/-- Forget the formal direction, retaining the original edge identity. -/
def underlying {a b : α} (e : Traversal a b) : Edge α :=
  match e with
  | Sum.inl f => ⟨a, b, f⟩
  | Sum.inr f => ⟨b, a, f⟩

/-- One selected original edge for each nonroot vertex. -/
def selected (a : {a : α // a ≠ r}) : Edge α := underlying (T.parentEdge a)

theorem underlying_endpoints {a b : α} (e : Traversal a b) :
    ((underlying e).1 = a ∧ (underlying e).2.1 = b) ∨
    ((underlying e).1 = b ∧ (underlying e).2.1 = a) := by
  cases e <;> simp [underlying]

theorem selected_injective : Function.Injective (selected T) := by
  intro a b hab
  have ha := underlying_endpoints (T.parentEdge a)
  have hb := underlying_endpoints (T.parentEdge b)
  change selected T a = selected T b at hab
  change ((selected T a).1 = T.parent a ∧ (selected T a).2.1 = a.val) ∨
    ((selected T a).1 = a.val ∧ (selected T a).2.1 = T.parent a) at ha
  change ((selected T b).1 = T.parent b ∧ (selected T b).2.1 = b.val) ∨
    ((selected T b).1 = b.val ∧ (selected T b).2.1 = T.parent b) at hb
  rw [hab] at ha
  have hda := T.parent_depth a
  have hdb := T.parent_depth b
  rcases ha with ha | ha <;> rcases hb with hb | hb
  · exact Subtype.ext (ha.2.symm.trans hb.2)
  · have h1 : T.parent a = b.val := ha.1.symm.trans hb.1
    have h2 : T.parent b = a.val := hb.2.symm.trans ha.2
    rw [h1] at hda
    rw [h2] at hdb
    omega
  · have h1 : T.parent a = b.val := ha.2.symm.trans hb.2
    have h2 : T.parent b = a.val := hb.1.symm.trans ha.1
    rw [h1] at hda
    rw [h2] at hdb
    omega
  · exact Subtype.ext (ha.1.symm.trans hb.1)

/-- Tree support is a set of original edges, rather than endpoint pairs. -/
def treeEdges : Set (Edge α) := Set.range (selected T)

/-- Every original edge outside the selected tree is a chord. -/
def Chord := {e : Edge α // e ∉ treeEdges T}

theorem mem_treeEdges (a : {a : α // a ≠ r}) : selected T a ∈ treeEdges T :=
  ⟨a, rfl⟩

theorem treeEdges_induction (P : Edge α → Prop)
    (h : ∀ a : {a : α // a ≠ r}, P (selected T a)) :
    ∀ e ∈ treeEdges T, P e := by
  rintro e ⟨a, rfl⟩
  exact h a

/-- A tree never selects a self-loop, even when the original quiver has them. -/
theorem selected_not_loop (a : {a : α // a ≠ r}) :
    (selected T a).1 ≠ (selected T a).2.1 := by
  have hd := T.parent_depth a
  have he := underlying_endpoints (T.parentEdge a)
  change ((selected T a).1 = T.parent a ∧ (selected T a).2.1 = a.val) ∨
    ((selected T a).1 = a.val ∧ (selected T a).2.1 = T.parent a) at he
  intro h
  rcases he with he | he
  · have hp : T.parent a = a.val := he.1.symm.trans (h.trans he.2)
    rw [hp] at hd
    exact (Nat.lt_irrefl _ hd)
  · have hp : T.parent a = a.val := he.2.symm.trans (h.symm.trans he.1)
    rw [hp] at hd
    exact (Nat.lt_irrefl _ hd)

/-- Every traversal of a supported path belongs to the selected tree. -/
def Supported {a : Quiver.Symmetrify α} :
    ∀ {b : Quiver.Symmetrify α}, Quiver.Path a b → Prop
  | _, .nil => True
  | _, .cons p e => Supported p ∧ underlying (α := α) e ∈ treeEdges T

theorem rootPath_supported (a : α) : Supported T (rootPath T a) := by
  apply rooted_induction T (fun a => Supported T (rootPath T a))
  · rw [rootPath_root]
    trivial
  · intro b hb
    rw [← rootPath_parent]
    exact ⟨hb, mem_treeEdges T b⟩

theorem treeEdges_no_loop (e : Edge α) (he : e ∈ treeEdges T) : e.1 ≠ e.2.1 :=
  treeEdges_induction T (fun e => e.1 ≠ e.2.1) (selected_not_loop T) e he

/-- The selected tree has exactly one edge per nonroot vertex. -/
theorem tree_card [Fintype α] [Fintype (treeEdges T)] :
    Fintype.card (treeEdges T) = Fintype.card α - 1 := by
  classical
  calc
    Fintype.card (treeEdges T) = Fintype.card {a : α // a ≠ r} :=
      (Fintype.card_congr (show {a : α // a ≠ r} ≃ treeEdges T from
        Equiv.ofInjective (selected T) (selected_injective T))).symm
    _ = Fintype.card α - 1 := by
      rw [Fintype.card_subtype_compl, Fintype.card_subtype_eq]

/-- The cycle rank counts original edge identities, not doubled traversals. -/
theorem chord_count [Fintype α] [Fintype (Edge α)] [Fintype (Chord T)] :
    Fintype.card (Chord T) + Fintype.card α = Fintype.card (Edge α) + 1 := by
  classical
  let : Fintype (treeEdges T) := Fintype.ofFinite _
  have htree := tree_card T
  have hle : Fintype.card (treeEdges T) ≤ Fintype.card (Edge α) :=
    Fintype.card_le_of_injective Subtype.val Subtype.val_injective
  have hcomp : Fintype.card (Chord T) =
      Fintype.card (Edge α) - Fintype.card (treeEdges T) :=
    by simpa only [← Nat.card_eq_fintype_card, Chord] using
      Fintype.card_subtype_compl (fun e : Edge α => e ∈ treeEdges T)
  have hpos : 0 < Fintype.card α := Fintype.card_pos_iff.mpr ⟨r⟩
  omega

include T in
theorem edge_count_lower_bound [Fintype α] [Fintype (Edge α)] :
    Fintype.card α - 1 ≤ Fintype.card (Edge α) := by
  classical
  let : Fintype (treeEdges T) := Fintype.ofFinite _
  rw [← tree_card T]
  exact Fintype.card_le_of_injective Subtype.val Subtype.val_injective

theorem chord_card [Fintype α] [Fintype (Edge α)] [Fintype (Chord T)] :
    Fintype.card (Chord T) = Fintype.card (Edge α) + 1 - Fintype.card α := by
  have h := chord_count T
  omega

/-- The usual subtraction formula is exact as an integer identity. -/
theorem chord_card_int [Fintype α] [Fintype (Edge α)] [Fintype (Chord T)] :
    (Fintype.card (Chord T) : ℤ) =
      (Fintype.card (Edge α) : ℤ) - (Fintype.card α : ℤ) + 1 := by
  have h := chord_count T
  omega

end PaperXI.GraphTree
