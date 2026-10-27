import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions

namespace Komorebi.StrongArtin.AdaptiveAuxiliarySelection

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- The active subspace left after imposing the scalar local conditions indexed
by `Q`.  In the Taylor--Wiles application this models the dual Selmer classes
that remain invisible at every already chosen auxiliary prime. -/
def selectedKernel (probe : ι → Module.Dual k V) (Q : Finset ι) : Submodule k V where
  carrier := {v | ∀ i ∈ Q, probe i v = 0}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy i hi
    simp [hx i hi, hy i hi]
  smul_mem' := by
    intro a x hx i hi
    simp [hx i hi]

@[simp]
theorem mem_selectedKernel
    (probe : ι → Module.Dual k V) (Q : Finset ι) (v : V) :
    v ∈ selectedKernel probe Q ↔ ∀ i ∈ Q, probe i v = 0 := Iff.rfl

@[simp]
theorem selectedKernel_empty (probe : ι → Module.Dual k V) :
    selectedKernel probe ∅ = ⊤ := by
  ext v
  simp [selectedKernel]

/-- Adding an auxiliary functional can only shrink the active subspace. -/
theorem selectedKernel_insert_le [DecidableEq ι]
    (probe : ι → Module.Dual k V) (Q : Finset ι) (i : ι) :
    selectedKernel probe (insert i Q) ≤ selectedKernel probe Q := by
  intro v hv j hj
  exact hv j (Finset.mem_insert_of_mem hj)

/-- One-prime detection produces a genuinely new auxiliary label and a strict
shrinkage of the currently active space. -/
theorem exists_fresh_probe_strict_drop
    [DecidableEq ι]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0)
    (Q : Finset ι)
    (hactive : selectedKernel probe Q ≠ ⊥) :
    ∃ i : ι, i ∉ Q ∧
      selectedKernel probe (insert i Q) < selectedKernel probe Q := by
  obtain ⟨v, hvQ, hv0⟩ := (Submodule.ne_bot_iff (selectedKernel probe Q)).mp hactive
  obtain ⟨i, hi⟩ := hdetect v hv0
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
  exact ⟨i, hiQ, lt_of_le_of_ne hle hne⟩

/-- In finite dimension, every successful one-prime step strictly lowers the
active dimension. -/
theorem exists_fresh_probe_finrank_drop
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0)
    (Q : Finset ι)
    (hactive : selectedKernel probe Q ≠ ⊥) :
    ∃ i : ι, i ∉ Q ∧
      Module.finrank k (selectedKernel probe (insert i Q)) <
        Module.finrank k (selectedKernel probe Q) := by
  obtain ⟨i, hiQ, hlt⟩ :=
    exists_fresh_probe_strict_drop probe hdetect Q hactive
  exact ⟨i, hiQ, Submodule.finrank_lt_finrank_of_lt hlt⟩


/-- Starting from any already selected finite auxiliary set, repeated one-class
selection terminates after at most the current active dimension.  The output is
a finite superset whose joint kernel is zero.  This is the abstract adaptive
Taylor--Wiles selection theorem: changing Selmer conditions are represented by
successive intersections with local functional kernels. -/
theorem exists_finite_auxiliary_superset
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0)
    (Q₀ : Finset ι) :
    ∃ Q : Finset ι,
      Q₀ ⊆ Q ∧
      Q.card ≤ Q₀.card + Module.finrank k (selectedKernel probe Q₀) ∧
      selectedKernel probe Q = ⊥ := by
  classical
  generalize hn : Module.finrank k (selectedKernel probe Q₀) = n
  induction n using Nat.strong_induction_on generalizing Q₀ with
  | h n ih =>
      by_cases hbot : selectedKernel probe Q₀ = ⊥
      · refine ⟨Q₀, Finset.Subset.rfl, ?_, hbot⟩
        omega
      · obtain ⟨i, hiQ₀, hlt⟩ :=
          exists_fresh_probe_strict_drop probe hdetect Q₀ hbot
        have hdimlt :
            Module.finrank k (selectedKernel probe (insert i Q₀)) < n := by
          rw [← hn]
          exact Submodule.finrank_lt_finrank_of_lt hlt
        obtain ⟨Q, hsub, hcard, hfinal⟩ :=
          ih _ hdimlt (insert i Q₀) rfl
        refine ⟨Q, ?_, ?_, hfinal⟩
        · exact (Finset.subset_insert i Q₀).trans hsub
        · have hcard_insert : (insert i Q₀).card = Q₀.card + 1 :=
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

/-- Empty-start specialization: at most `finrank k V` auxiliary labels suffice
to annihilate a finite-dimensional active space. -/
theorem exists_finite_auxiliary_set
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0) :
    ∃ Q : Finset ι,
      Q.card ≤ Module.finrank k V ∧
      selectedKernel probe Q = ⊥ := by
  obtain ⟨Q, -, hcard, hker⟩ :=
    exists_finite_auxiliary_superset probe hdetect (∅ : Finset ι)
  refine ⟨Q, ?_, hker⟩
  have htop : selectedKernel probe (∅ : Finset ι) = ⊤ := selectedKernel_empty probe
  rw [htop] at hcard
  simpa using hcard


/-- Simultaneous evaluation at a finite auxiliary set. -/
def evaluationMap
    (probe : ι → Module.Dual k V) (Q : Finset ι) :
    V →ₗ[k] (Q → k) where
  toFun v i := probe i.1 v
  map_add' x y := by
    funext i
    simp
  map_smul' a x := by
    funext i
    simp

@[simp]
theorem evaluationMap_apply
    (probe : ι → Module.Dual k V) (Q : Finset ι)
    (v : V) (i : Q) :
    evaluationMap probe Q v i = probe i.1 v := rfl

/-- The kernel of simultaneous evaluation is exactly the active subspace. -/
theorem ker_evaluationMap
    (probe : ι → Module.Dual k V) (Q : Finset ι) :
    LinearMap.ker (evaluationMap probe Q) = selectedKernel probe Q := by
  ext v
  constructor
  · intro hv i hi
    have hzero := LinearMap.mem_ker.mp hv
    have hcoord := congrFun hzero (⟨i, hi⟩ : Q)
    simpa using hcoord
  · intro hv
    apply LinearMap.mem_ker.mpr
    funext i
    exact hv i.1 i.2

/-- Vanishing of the active kernel is equivalent to injectivity of the
simultaneous local evaluation map. -/
theorem selectedKernel_eq_bot_iff_evaluationMap_injective
    (probe : ι → Module.Dual k V) (Q : Finset ι) :
    selectedKernel probe Q = ⊥ ↔
      Function.Injective (evaluationMap probe Q) := by
  rw [← ker_evaluationMap, LinearMap.ker_eq_bot]

/-- Any scalar-valued auxiliary set whose simultaneous evaluation is injective
has at least the dimension of the active space many labels. -/
theorem finrank_le_card_of_evaluationMap_injective
    [FiniteDimensional k V]
    (probe : ι → Module.Dual k V) (Q : Finset ι)
    (hinj : Function.Injective (evaluationMap probe Q)) :
    Module.finrank k V ≤ Q.card := by
  have h := (evaluationMap probe Q).finrank_le_finrank_of_injective hinj
  simpa [Module.finrank_fintype_fun_eq_card, Fintype.card_coe] using h

/-- Canonical finite-set form: scalar one-prime detection admits a finite
auxiliary set of exactly the active dimension, and simultaneous localization at
those labels is injective. -/
theorem exists_finite_auxiliary_set_exact
    [DecidableEq ι] [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0) :
    ∃ Q : Finset ι,
      Q.card = Module.finrank k V ∧
      Function.Injective (evaluationMap probe Q) := by
  obtain ⟨Q, hcard, hker⟩ := exists_finite_auxiliary_set probe hdetect
  have hinj : Function.Injective (evaluationMap probe Q) := by
    rw [← LinearMap.ker_eq_bot, ker_evaluationMap]
    exact hker
  have hdim_le : Module.finrank k V ≤ Q.card :=
    finrank_le_card_of_evaluationMap_injective probe Q hinj
  exact ⟨Q, Nat.le_antisymm hcard hdim_le, hinj⟩

end
end Komorebi.StrongArtin.AdaptiveAuxiliarySelection

#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.exists_fresh_probe_strict_drop
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.exists_fresh_probe_finrank_drop
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.exists_finite_auxiliary_superset
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.exists_finite_auxiliary_set
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.selectedKernel_eq_bot_iff_evaluationMap_injective
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.finrank_le_card_of_evaluationMap_injective
#print axioms Komorebi.StrongArtin.AdaptiveAuxiliarySelection.exists_finite_auxiliary_set_exact
