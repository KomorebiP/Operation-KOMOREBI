import RealizationBoundaries.HomomorphismObstruction
import RealizationBoundaries.NormalFormTransport
import RealizationBoundaries.CompletionConsequences

/-!
# Finite-change controls and a canonical completion reconstruction obstruction

The example of a changed marked point is distinguished from a changed abstract
group. The completion counterexample compares objects; it does not assert that
an already supplied homomorphism becomes invertible without being invertible.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

def toggleBit (a : ℕ → Bool) (k : ℕ) : ℕ → Bool :=
  fun n => if n = k then !(a n) else a n

theorem toggleBit_disagreement (a : ℕ → Bool) (k : ℕ) :
    {n : ℕ | a n ≠ toggleBit a k n} = {k} := by
  ext n
  by_cases hn : n = k
  · subst n
    cases a k <;> simp [toggleBit]
  · simp [toggleBit, hn]

theorem toggleBit_ne (a : ℕ → Bool) (k : ℕ) : a ≠ toggleBit a k := by
  intro h
  have hk := congrFun h k
  cases ha : a k <;> simp [toggleBit, ha] at hk

/-- One changed bit leaves the original ambient subgroup literally unchanged. -/
theorem toggleBit_group_eq (a : ℕ → Bool) (k : ℕ) :
    pairedGroup a = pairedGroup (toggleBit a k) := by
  apply pairedGroup_eq_of_finite_disagreement
  rw [toggleBit_disagreement]
  exact Set.finite_singleton k

/-- Yet no isomorphism of these groups preserves the prescribed marked elements. -/
theorem toggleBit_not_marked_isomorphic (a : ℕ → Bool) (k : ℕ) :
    ¬ ∃ e : pairedGroup a ≃+ pairedGroup (toggleBit a k),
      e (markedElement (pairedSelector a)) = markedElement (pairedSelector (toggleBit a k)) := by
  rw [pairedGroup_marked_isomorphic_iff]
  exact toggleBit_ne a k

/-- A concrete two-object witness: the constant selectors disagree at every index. -/
theorem constant_selectors_infinite_disagreement :
    {n : ℕ | (fun _ : ℕ => false) n ≠ (fun _ : ℕ => true) n}.Infinite := by
  simpa using (Set.infinite_univ : (Set.univ : Set ℕ).Infinite)

theorem constant_groups_not_isomorphic :
    ¬ Nonempty (pairedGroup (fun _ => false) ≃+ pairedGroup (fun _ => true)) := by
  rw [pairedGroup_isomorphic_iff]
  exact constant_selectors_infinite_disagreement

/-- All actual canonical completions are isomorphic as topological additive groups. -/
def pairedCommonCompletionEquiv (a b : ℕ → Bool) :
    CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
      CanonicalCompletion (selectorLine (pairedSelector b)) :=
  commonCompletionEquiv _ _

/-- Same canonical completion, but no isomorphism of the original groups. -/
theorem completion_object_counterexample :
    ∃ a b : ℕ → Bool,
      Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
        CanonicalCompletion (selectorLine (pairedSelector b))) ∧
      ¬ Nonempty (pairedGroup a ≃+ pairedGroup b) :=
  ⟨(fun _ => false), (fun _ => true),
    ⟨pairedCommonCompletionEquiv _ _⟩, constant_groups_not_isomorphic⟩

/-- No assignment of groups can both respect isomorphism of these canonical
completions and recover every original paired group. No computability is assumed.
The assignment is allowed arbitrary selector-indexed outputs, making the obstruction
stronger than restricting a priori to a particular algorithm or description language. -/
theorem no_completion_invariant_reconstruction (R : (ℕ → Bool) → Type*)
    [∀ a, AddGroup (R a)]
    (invariant : ∀ a b,
      Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
        CanonicalCompletion (selectorLine (pairedSelector b))) → Nonempty (R a ≃+ R b))
    (recovers : ∀ a, Nonempty (R a ≃+ pairedGroup a)) : False := by
  obtain ⟨ea⟩ := recovers (fun _ => false)
  obtain ⟨eb⟩ := recovers (fun _ => true)
  obtain ⟨er⟩ := invariant (fun _ => false) (fun _ => true) ⟨pairedCommonCompletionEquiv _ _⟩
  exact constant_groups_not_isomorphic ⟨(ea.symm.trans er).trans eb⟩

/-- The coordinate identity between completions cannot lift to a group homomorphism
when the selectors disagree infinitely. This is an explicit map-level nonfullness witness. -/
theorem no_lift_of_commonCompletionEquiv (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) :
    ¬ ∃ f : pairedGroup a →+ pairedGroup b, ∀ x : pairedGroup a,
      pairedCommonCompletionEquiv a b
        (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a)) x) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup b)) (f x) := by
  rintro ⟨f, hf⟩
  apply no_injective_hom_of_infinite_disagreement a b h f
  intro x y hxy
  have hη := congrArg (ProfiniteAddGrp.ProfiniteCompletion.etaFn
    (AddGrpCat.of (pairedGroup b))) hxy
  exact (preimage_eta_injective (selectorLine (pairedSelector a)))
    ((pairedCommonCompletionEquiv a b).injective ((hf x).trans (hη.trans (hf y).symm)))

end RealizationBoundaries
