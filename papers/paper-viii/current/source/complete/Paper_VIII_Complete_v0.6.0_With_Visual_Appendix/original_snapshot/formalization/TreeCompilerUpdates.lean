module
public import ExactTreeCompiler
import all ExactTreeCompiler

/-!
Author: Komorebi P.
Paper VIII 9.11 and 9.12. Full-tree decision stability and an actual cached
ancestor-only update algorithm. The update receives cached sibling values,
not an oracle for the desired new optimum.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.CandidateTree
open scoped BigOperators
variable {α R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Scores perturbed by less than half their absolute gap keep the same order. -/
theorem half_gap_order (K S K' S' : R)
    (hK : |K' - K| < |K - S| / 2) (hS : |S' - S| < |K - S| / 2) :
    (K' ≤ S' ↔ K ≤ S) := by
  by_cases h : K ≤ S
  · rw [abs_of_nonpos (sub_nonpos.mpr h)] at hK hS
    have hk := (abs_lt.mp hK).2
    have hs := (abs_lt.mp hS).1
    have h' : K' < S' := by linarith
    exact iff_of_true (le_of_lt h') h
  · have hslt : S < K := lt_of_not_ge h
    rw [abs_of_pos (sub_pos.mpr hslt)] at hK hS
    have hk := (abs_lt.mp hK).1
    have hs := (abs_lt.mp hS).2
    have h' : S' < K' := by linarith
    exact iff_of_false (not_le_of_gt h') h

/-- Bounds are imposed on the solved keep/split scores, at every internal node. -/
def GapControlled (keep overhead keep' overhead' : α → R) : CandidateTree α → Prop
  | .leaf _ => True
  | .node a _ ts =>
    let oldSplit := overhead a + ∑ i, optimalValue keep overhead (ts i)
    let newSplit := overhead' a + ∑ i, optimalValue keep' overhead' (ts i)
    |keep' a - keep a| < |keep a - oldSplit| / 2 ∧
    |newSplit - oldSplit| < |keep a - oldSplit| / 2 ∧
    ∀ i, GapControlled keep overhead keep' overhead' (ts i)

/-- Under the source's strict half-gap hypotheses the entire selected cut agrees. -/
theorem compiler_stability (keep overhead keep' overhead' : α → R)
    (t : CandidateTree α) (hg : GapControlled keep overhead keep' overhead' t) :
    compile keep' overhead' t = compile keep overhead t := by
  induction t with
  | leaf a => rfl
  | node a n ts ih =>
    rcases hg with ⟨hk, hs, hc⟩
    have ho := half_gap_order _ _ _ _ hk hs
    simp only [compile]
    by_cases h : keep a ≤ overhead a + ∑ i, optimalValue keep overhead (ts i)
    · rw [ite_eq_left h, ite_eq_left (ho.mpr h)]
    · rw [ite_eq_right h, ite_eq_right (fun hp => h (ho.mp hp))]
      congr 1
      funext i
      exact ih i (hc i)

/-- A path to a changed subtree stores the untouched siblings and their cached values. -/
inductive CachedContext (α R : Type*) where
  | hole
  | frame (label : α) (arity : ℕ) (siblings : Fin (arity + 1) → CandidateTree α)
      (slot : Fin (arity + 1)) (cache : Fin (arity + 1) → R) (outer : CachedContext α R)

namespace CachedContext

def fill : CachedContext α R → CandidateTree α → CandidateTree α
  | .hole, t => t
  | .frame a n siblings slot _ outer, t =>
    fill outer (.node a n (Function.update siblings slot t))

/-- Only the newly supplied subtree value and already cached siblings are read. -/
def updateValue (keep overhead : α → R) : CachedContext α R → R → R
  | .hole, v => v
  | .frame a _ _ slot cache outer, v =>
    updateValue keep overhead outer
      (min (keep a) (overhead a + ∑ i, if i = slot then v else cache i))

def Valid (keep overhead : α → R) : CachedContext α R → Prop
  | .hole => True
  | .frame _ _ siblings slot cache outer =>
    (∀ i, i ≠ slot → cache i = optimalValue keep overhead (siblings i)) ∧
      Valid keep overhead outer

/-- Building caches from the original model always supplies a valid context. -/
def refresh (keep overhead : α → R) : CachedContext α R → CachedContext α R
  | .hole => .hole
  | .frame a n siblings slot _ outer =>
    .frame a n siblings slot (fun i => optimalValue keep overhead (siblings i))
      (refresh keep overhead outer)

omit [IsStrictOrderedRing R] in
theorem refresh_valid (keep overhead : α → R) (ctx : CachedContext α R) :
    Valid keep overhead (refresh keep overhead ctx) := by
  induction ctx with
  | hole => trivial
  | frame a n siblings slot cache outer ih => exact ⟨fun _ _ => rfl, ih⟩

omit [IsStrictOrderedRing R] in
theorem refresh_fill (keep overhead : α → R) (ctx : CachedContext α R) (t : CandidateTree α) :
    fill (refresh keep overhead ctx) t = fill ctx t := by
  induction ctx generalizing t with
  | hole => rfl
  | frame a n siblings slot cache outer ih => exact ih _

omit [IsStrictOrderedRing R] in
theorem updateValue_correct (keep overhead : α → R) (ctx : CachedContext α R)
    (hv : Valid keep overhead ctx) (newTree : CandidateTree α) :
    updateValue keep overhead ctx (optimalValue keep overhead newTree) =
      optimalValue keep overhead (fill ctx newTree) := by
  induction ctx generalizing newTree with
  | hole => rfl
  | frame a n siblings slot cache outer ih =>
    rcases hv with ⟨hc, ho⟩
    have he : (∑ i, if i = slot then optimalValue keep overhead newTree else cache i) =
        ∑ i, optimalValue keep overhead (Function.update siblings slot newTree i) := by
      apply Finset.sum_congr rfl
      intro i _
      by_cases hi : i = slot
      · subst i; simp
      · simp [hi, hc i hi]
    simp only [updateValue, fill, he]
    exact ih ho (.node a n (Function.update siblings slot newTree))

omit [Field R] [LinearOrder R] [IsStrictOrderedRing R] in
theorem sibling_tree_unchanged (n : ℕ) (siblings : Fin (n + 1) → CandidateTree α)
    (slot i : Fin (n + 1)) (t : CandidateTree α) (hi : i ≠ slot) :
    Function.update siblings slot t i = siblings i := by
  exact Function.update_of_ne hi t siblings

omit [IsStrictOrderedRing R] in
theorem sibling_value_unchanged (keep overhead : α → R) (n : ℕ)
    (siblings : Fin (n + 1) → CandidateTree α) (slot i : Fin (n + 1))
    (t : CandidateTree α) (hi : i ≠ slot) :
    optimalValue keep overhead (Function.update siblings slot t i) =
      optimalValue keep overhead (siblings i) := by
  rw [Function.update_of_ne hi]

/-- The cached update is globally optimal against all cuts of the edited tree. -/
theorem local_recompilation (keep overhead : α → R) (ctx : CachedContext α R)
    (hv : Valid keep overhead ctx) (newTree : CandidateTree α) :
    (∀ c : Cut (fill ctx newTree),
      updateValue keep overhead ctx (optimalValue keep overhead newTree) ≤
        cutValue keep overhead c) ∧
    ∃ c : Cut (fill ctx newTree), cutValue keep overhead c =
      updateValue keep overhead ctx (optimalValue keep overhead newTree) := by
  rw [updateValue_correct keep overhead ctx hv newTree]
  exact exact_tree_compiler keep overhead (fill ctx newTree)

end CachedContext

/-- A strict Pareto point need not minimize any scalarized objective. -/
theorem unsupported_pareto_example (lam : ℚ) :
    min (2 * lam) 2 < 3 / 2 + lam := by
  by_cases h : lam ≤ 1
  · exact (min_le_left _ _).trans_lt (by linarith)
  · exact (min_le_right _ _).trans_lt (by linarith)

end KomorebiPaperVIII.CandidateTree

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.CandidateTree.half_gap_order
#print axioms KomorebiPaperVIII.CandidateTree.compiler_stability
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.refresh_valid
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.refresh_fill
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.updateValue_correct
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.sibling_tree_unchanged
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.sibling_value_unchanged
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.local_recompilation
#print axioms KomorebiPaperVIII.CandidateTree.unsupported_pareto_example
#print axioms KomorebiPaperVIII.CandidateTree.CachedContext.updateValue
