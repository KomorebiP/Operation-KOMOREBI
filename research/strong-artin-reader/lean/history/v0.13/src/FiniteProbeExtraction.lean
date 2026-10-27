import AdequateProbeDetection
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition

namespace Komorebi.StrongArtin.FiniteProbeExtraction

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- A separating family of linear probes spans the whole algebraic dual when
the source is finite-dimensional. -/
theorem span_range_eq_top_of_separates
    [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0) :
    Submodule.span k (Set.range probe) = ⊤ := by
  let S : Submodule k (Module.Dual k V) := Submodule.span k (Set.range probe)
  have hco : S.dualCoannihilator = ⊥ := by
    ext v
    constructor
    · intro hv
      have hvall : ∀ i : ι, probe i v = 0 := by
        intro i
        exact (Submodule.mem_dualCoannihilator v).1 hv
          (probe i) (Submodule.subset_span (Set.mem_range_self i))
      have hz : v = 0 := hsep v hvall
      simp [hz]
    · intro hv
      have hz : v = 0 := (Submodule.mem_bot k).1 hv
      subst v
      simp
  have hdouble : S.dualCoannihilator.dualAnnihilator = S :=
    @Subspace.dualCoannihilator_dualAnnihilator_eq k V _ _ _ S (by infer_instance)
  calc
    Submodule.span k (Set.range probe) = S := rfl
    _ = S.dualCoannihilator.dualAnnihilator := hdouble.symm
    _ = (⊥ : Submodule k V).dualAnnihilator := by rw [hco]
    _ = ⊤ := Submodule.dualAnnihilator_bot

/-- Finite extraction: from any separating family on a finite-dimensional
space, one can choose a finite linearly independent collection of actual probe
functionals, each drawn from the original family, that spans the entire dual.
Its cardinality is exactly the source dimension. -/
theorem exists_finite_probe_basis_of_separates
    [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0) :
    ∃ t : Finset (Module.Dual k V),
      (t : Set (Module.Dual k V)) ⊆ Set.range probe ∧
      t.card = Module.finrank k V ∧
      Submodule.span k (t : Set (Module.Dual k V)) = ⊤ ∧
      LinearIndepOn k id (t : Set (Module.Dual k V)) := by
  have hspan : Submodule.span k (Set.range probe) = ⊤ :=
    span_range_eq_top_of_separates probe hsep
  obtain ⟨t, ht_range, ht_card, ht_span, ht_indep⟩ :=
    Submodule.exists_finset_span_eq_linearIndepOn k (Set.range probe)
  refine ⟨t, ht_range, ?_, ?_, ht_indep⟩
  · calc
      t.card = Module.finrank k (Submodule.span k (Set.range probe)) := ht_card
      _ = Module.finrank k (Module.Dual k V) := by rw [hspan, finrank_top]
      _ = Module.finrank k V := Subspace.dual_finrank_eq
  · calc
      Submodule.span k (t : Set (Module.Dual k V)) =
          Submodule.span k (Set.range probe) := ht_span
      _ = ⊤ := hspan

end
end Komorebi.StrongArtin.FiniteProbeExtraction

#print axioms Komorebi.StrongArtin.FiniteProbeExtraction.span_range_eq_top_of_separates
#print axioms Komorebi.StrongArtin.FiniteProbeExtraction.exists_finite_probe_basis_of_separates
