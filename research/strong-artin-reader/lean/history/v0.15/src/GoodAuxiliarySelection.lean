import AdaptiveAuxiliarySelection

namespace Komorebi.StrongArtin.GoodAuxiliarySelection

open Komorebi.StrongArtin.AdaptiveAuxiliarySelection

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- Arithmetic-constrained adaptive selection.  If every nonzero active class is
detected by some auxiliary label satisfying `Good`, then one can select exactly
`finrank k V` good labels whose simultaneous local evaluation is injective. -/
theorem exists_finite_good_auxiliary_set_exact
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (Good : ι → Prop)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, Good i ∧ probe i v ≠ 0) :
    ∃ Q : Finset ι,
      (∀ i ∈ Q, Good i) ∧
      Q.card = Module.finrank k V ∧
      Function.Injective (evaluationMap probe Q) := by
  let ιGood := {i : ι // Good i}
  let goodProbe : ιGood → Module.Dual k V := fun i => probe i.1
  have hgoodDetect : ∀ v : V, v ≠ 0 → ∃ i : ιGood, goodProbe i v ≠ 0 := by
    intro v hv
    obtain ⟨i, hiGood, hi⟩ := hdetect v hv
    exact ⟨⟨i, hiGood⟩, hi⟩
  obtain ⟨QGood, hcardGood, hinjGood⟩ :=
    exists_finite_auxiliary_set_exact goodProbe hgoodDetect
  let Q : Finset ι := QGood.image (fun i : ιGood => i.1)
  have hcardQ : Q.card = QGood.card := by
    simpa [Q] using
      (Finset.card_image_of_injective QGood (Subtype.val_injective :
        Function.Injective (fun i : ιGood => i.1)))
  have hGoodQ : ∀ i ∈ Q, Good i := by
    intro i hi
    rcases Finset.mem_image.mp hi with ⟨j, -, rfl⟩
    exact j.2
  have hinjQ : Function.Injective (evaluationMap probe Q) := by
    intro x y hxy
    apply hinjGood
    funext j
    have hjQ : j.1.1 ∈ Q := by
      exact Finset.mem_image.mpr ⟨j.1, j.2, rfl⟩
    exact congrFun hxy ⟨j.1.1, hjQ⟩
  exact ⟨Q, hGoodQ, hcardQ.trans hcardGood, hinjQ⟩


/-- A good detecting label not already selected strictly shrinks the active
subspace.  Freshness is automatic: any previously selected functional vanishes
on the current selected kernel. -/
theorem exists_fresh_good_probe_strict_drop
    [DecidableEq ι]
    (probe : ι → Module.Dual k V)
    (Good : ι → Prop)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, Good i ∧ probe i v ≠ 0)
    (Q : Finset ι)
    (hactive : selectedKernel probe Q ≠ ⊥) :
    ∃ i : ι, Good i ∧ i ∉ Q ∧
      selectedKernel probe (insert i Q) < selectedKernel probe Q := by
  obtain ⟨v, hvQ, hv0⟩ := (Submodule.ne_bot_iff (selectedKernel probe Q)).mp hactive
  obtain ⟨i, hiGood, hi⟩ := hdetect v hv0
  have hiQ : i ∉ Q := by
    intro himem
    exact hi (hvQ i himem)
  have hle : selectedKernel probe (insert i Q) ≤ selectedKernel probe Q :=
    selectedKernel_insert_le probe Q i
  have hvnot : v ∉ selectedKernel probe (insert i Q) := by
    intro hv
    exact hi (hv i (Finset.mem_insert_self i Q))
  have hne : selectedKernel probe (insert i Q) ≠ selectedKernel probe Q := by
    intro hEq
    exact hvnot (hEq ▸ hvQ)
  exact ⟨i, hiGood, hiQ, lt_of_le_of_ne hle hne⟩

/-- Adaptive arithmetic-constrained extension.  Starting from a finite set of
good auxiliary labels, one can extend it to a killing set using at most the
current active dimension additional labels. -/
theorem exists_finite_good_auxiliary_superset
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (Good : ι → Prop)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, Good i ∧ probe i v ≠ 0)
    (Q₀ : Finset ι)
    (hQ₀Good : ∀ i ∈ Q₀, Good i) :
    ∃ Q : Finset ι,
      Q₀ ⊆ Q ∧
      (∀ i ∈ Q, Good i) ∧
      Q.card ≤ Q₀.card + Module.finrank k (selectedKernel probe Q₀) ∧
      selectedKernel probe Q = ⊥ := by
  classical
  generalize hn : Module.finrank k (selectedKernel probe Q₀) = n
  induction n using Nat.strong_induction_on generalizing Q₀ with
  | h n ih =>
      by_cases hbot : selectedKernel probe Q₀ = ⊥
      · exact ⟨Q₀, Finset.Subset.rfl, hQ₀Good, by omega, hbot⟩
      · obtain ⟨i, hiGood, hiQ₀, hlt⟩ :=
          exists_fresh_good_probe_strict_drop probe Good hdetect Q₀ hbot
        have hdimlt :
            Module.finrank k (selectedKernel probe (insert i Q₀)) < n := by
          rw [← hn]
          exact Submodule.finrank_lt_finrank_of_lt hlt
        have hinsertGood : ∀ j ∈ insert i Q₀, Good j := by
          intro j hj
          rcases Finset.mem_insert.mp hj with rfl | hjQ₀
          · exact hiGood
          · exact hQ₀Good j hjQ₀
        obtain ⟨Q, hsub, hQGood, hcard, hfinal⟩ :=
          ih _ hdimlt (insert i Q₀) hinsertGood rfl
        refine ⟨Q, (Finset.subset_insert i Q₀).trans hsub, hQGood, ?_, hfinal⟩
        have hcard_insert : (insert i Q₀).card = Q₀.card + 1 :=
          Finset.card_insert_of_notMem hiQ₀
        have hsucc :
            Module.finrank k (selectedKernel probe (insert i Q₀)) + 1 ≤ n :=
          Nat.succ_le_iff.mpr hdimlt
        calc
          Q.card ≤ (insert i Q₀).card +
              Module.finrank k (selectedKernel probe (insert i Q₀)) := hcard
          _ = Q₀.card + 1 +
              Module.finrank k (selectedKernel probe (insert i Q₀)) := by
                rw [hcard_insert]
          _ = Q₀.card +
              (Module.finrank k (selectedKernel probe (insert i Q₀)) + 1) := by
                omega
          _ ≤ Q₀.card + n := Nat.add_le_add_left hsucc Q₀.card

end
end Komorebi.StrongArtin.GoodAuxiliarySelection

#print axioms Komorebi.StrongArtin.GoodAuxiliarySelection.exists_finite_good_auxiliary_set_exact
#print axioms Komorebi.StrongArtin.GoodAuxiliarySelection.exists_fresh_good_probe_strict_drop
#print axioms Komorebi.StrongArtin.GoodAuxiliarySelection.exists_finite_good_auxiliary_superset
