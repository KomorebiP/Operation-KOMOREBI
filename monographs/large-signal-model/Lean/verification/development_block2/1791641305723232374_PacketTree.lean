import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Fintype.Sum
import Mathlib.Data.Fintype.Sigma
import Mathlib.Data.Fintype.BigOperators

/-! Finite rooted trees and path-complete cuts. A selection is arbitrary
on nodes. Completeness means exactly one selected node on each full
root-to-leaf path. Reconstruction is derived from local conservation,
not included in the definition of a cut. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM

/-- Every internal node has a finite nonempty child family. -/
inductive PacketTree where
  | leaf : PacketTree
  | branch (n : ℕ) (child : Fin (n + 1) → PacketTree) : PacketTree

namespace PacketTree

/-- Nodes have structural addresses, even when labels coincide. -/
def Node : PacketTree → Type
  | .leaf => Unit
  | .branch n child => Unit ⊕ (Σ i : Fin (n + 1), Node (child i))

/-- Full root-to-leaf paths are indexed by the leaf they reach. -/
def Leaf : PacketTree → Type
  | .leaf => Unit
  | .branch n child => Σ i : Fin (n + 1), Leaf (child i)

def root : (t : PacketTree) → Node t
  | .leaf => ()
  | .branch _ _ => Sum.inl ()

/-- A canonical leaf proves that no descendant branch is empty. -/
def firstLeaf : (t : PacketTree) → Leaf t
  | .leaf => ()
  | .branch _ child => ⟨0, firstLeaf (child 0)⟩

/-- Counts every selected node along a full path, including the root. -/
def pathCount : (t : PacketTree) → (Node t → Bool) → Leaf t → ℕ
  | .leaf, s, _ => (s ()).toNat
  | .branch _ child, s, p => (s (Sum.inl ())).toNat +
      pathCount (child p.1) (fun v => s (Sum.inr ⟨p.1, v⟩)) p.2

def IsCompleteCut (t : PacketTree) (s : Node t → Bool) : Prop :=
  ∀ p : Leaf t, pathCount t s p = 1

/-- Canonical recursive finite sum over every node. -/
def nodeSum {A : Type*} [AddCommMonoid A] : (t : PacketTree) → (Node t → A) → A
  | .leaf, f => f ()
  | .branch _ child, f => f (Sum.inl ()) +
      ∑ i, nodeSum (child i) (fun v => f (Sum.inr ⟨i, v⟩))

def selectedSum {A : Type*} [AddCommMonoid A]
    (t : PacketTree) (s : Node t → Bool) (f : Node t → A) : A :=
  nodeSum t (fun v => if s v then f v else 0)

/-- Local conservation imposes no condition on terminal node labels. -/
def Conservative {A : Type*} [AddCommMonoid A] :
    (t : PacketTree) → (Node t → A) → Prop
  | .leaf, _ => True
  | .branch _ child, f =>
      f (Sum.inl ()) = ∑ i, f (Sum.inr ⟨i, root (child i)⟩) ∧
      ∀ i, Conservative (child i) (fun v => f (Sum.inr ⟨i, v⟩))

theorem nodeSum_zero {A : Type*} [AddCommMonoid A] (t : PacketTree) :
    nodeSum t (fun _ => (0 : A)) = 0 := by
  induction t with
  | leaf => rfl
  | branch n child ih => simp [nodeSum, ih]

theorem pathCount_zero_iff (t : PacketTree) (s : Node t → Bool) :
    (∀ p, pathCount t s p = 0) ↔ (∀ v, s v = false) := by
  induction t with
  | leaf =>
      constructor
      · intro h v
        cases v
        simpa [pathCount] using h ()
      · intro h p
        cases p
        simp [pathCount, h ()]
  | branch n child ih =>
      constructor
      · intro h
        have hroot : s (Sum.inl ()) = false := by
          have h0 := h ⟨0, firstLeaf (child 0)⟩
          cases hs : s (Sum.inl ()) <;> simp [pathCount, hs] at h0 ⊢
        intro v
        cases v with
        | inl u => cases u; exact hroot
        | inr p =>
            apply (ih p.1 (fun v => s (Sum.inr ⟨p.1, v⟩))).mp
            · intro q
              simpa [pathCount, hroot] using h ⟨p.1, q⟩
      · intro h p
        have hi := (ih p.1 (fun v => s (Sum.inr ⟨p.1, v⟩))).mpr
          (fun v => h (Sum.inr ⟨p.1, v⟩))
        simp [pathCount, h (Sum.inl ()), hi]

theorem completeCut_leaf (s : Node .leaf → Bool) :
    IsCompleteCut .leaf s ↔ s () = true := by
  simp [IsCompleteCut, pathCount, Leaf]

/-- The path criterion forces either a root-only cut or full child cuts. -/
theorem completeCut_branch {n : ℕ} {child : Fin (n+1) → PacketTree}
    (s : Node (.branch n child) → Bool) :
    IsCompleteCut (.branch n child) s ↔
      (s (Sum.inl ()) = true ∧ ∀ i v, s (Sum.inr ⟨i, v⟩) = false) ∨
      (s (Sum.inl ()) = false ∧ ∀ i,
        IsCompleteCut (child i) (fun v => s (Sum.inr ⟨i, v⟩))) := by
  constructor
  · intro h
    cases hs : s (Sum.inl ()) with
    | false =>
        right
        refine ⟨rfl, ?_⟩
        intro i p
        simpa [pathCount, hs] using h ⟨i, p⟩
    | true =>
        left
        refine ⟨rfl, ?_⟩
        intro i
        apply (pathCount_zero_iff (child i) _).mp
        intro p
        have hp := h ⟨i, p⟩
        simpa [pathCount, hs] using hp
  · rintro (⟨hr, hz⟩ | ⟨hr, hc⟩) p
    · have hp := (pathCount_zero_iff (child p.1) _).mpr (hz p.1) p.2
      simp [pathCount, hr, hp]
    · simpa [pathCount, hr] using hc p.1 p.2

/-- Complete cuts conserve any additive label with conservative splits. -/
theorem selectedSum_eq_root {A : Type*} [AddCommMonoid A]
    (t : PacketTree) (s : Node t → Bool) (f : Node t → A)
    (cut : IsCompleteCut t s) (hf : Conservative t f) :
    selectedSum t s f = f (root t) := by
  induction t with
  | leaf =>
      have hs := (completeCut_leaf s).mp cut
      simp [selectedSum, nodeSum, root, hs]
  | branch n child ih =>
      rcases (completeCut_branch s).mp cut with ⟨hr, hz⟩ | ⟨hr, hc⟩
      · simp [selectedSum, nodeSum, hr, hz, nodeSum_zero, root]
      · have hh (i : Fin (n+1)) := ih i
          (fun v => s (Sum.inr ⟨i, v⟩)) (fun v => f (Sum.inr ⟨i, v⟩))
          (hc i) (hf.2 i)
        simp only [selectedSum] at hh
        simp only [selectedSum, nodeSum, hr, Bool.false_eq_true, ↓reduceIte,
          zero_add, hh]
        exact hf.1.symm

/-- An explicit enumeration of all structural node addresses. -/
@[instance_reducible] def nodeFintype : (t : PacketTree) → Fintype (Node t)
  | .leaf => inferInstanceAs (Fintype Unit)
  | .branch n child => by
      letI (i : Fin (n+1)) : Fintype (Node (child i)) := nodeFintype (child i)
      exact inferInstanceAs (Fintype (Unit ⊕ (Σ i : Fin (n+1), Node (child i))))

instance instFintypeNode (t : PacketTree) : Fintype (Node t) := nodeFintype t

theorem nodeSum_eq_sum {A : Type*} [AddCommMonoid A]
    (t : PacketTree) (f : Node t → A) :
    nodeSum t f = ∑ v, f v := by
  induction t with
  | leaf =>
      change f () = ∑ v : Unit, f v
      simp
  | branch n child ih =>
      change f (Sum.inl ()) + ∑ i, nodeSum (child i) (fun v => f (Sum.inr ⟨i,v⟩)) = _
      rw [Fintype.sum_sum_type, Fintype.sum_sigma]
      simp only [Finset.univ_unique, PUnit.default_eq_unit, Finset.sum_singleton]
      congr 1
      exact Finset.sum_congr rfl (fun i _ => ih i _)

/-- Standard finite-sum form of the complete-antichain conservation law. -/
theorem complete_cut_sum {A : Type*} [AddCommMonoid A]
    (t : PacketTree) (s : Node t → Bool) (f : Node t → A)
    (cut : IsCompleteCut t s) (hf : Conservative t f) :
    (∑ v, if s v then f v else 0) = f (root t) := by
  rw [← nodeSum_eq_sum]
  exact selectedSum_eq_root t s f cut hf

end PacketTree
end Komorebi.LSM
