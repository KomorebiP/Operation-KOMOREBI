import FiniteProbeExtraction

namespace Komorebi.StrongArtin.FiniteAuxiliarySelection

open Komorebi.StrongArtin.FiniteProbeExtraction

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- Pointwise one-class detection is equivalent to joint separation. -/
theorem separates_of_detects_each_nonzero
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0) :
    ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0 := by
  intro v hv
  by_contra hv0
  obtain ⟨i, hi⟩ := hdetect v hv0
  exact hi (hv i)

/-- Evaluation at a fixed vector, regarded as a linear functional on the
algebraic dual. -/
def evalAt (v : V) : Module.Dual k (Module.Dual k V) where
  toFun φ := φ v
  map_add' φ ψ := by simp
  map_smul' a φ := by simp

@[simp] theorem evalAt_apply (v : V) (φ : Module.Dual k V) :
    evalAt v φ = φ v := rfl

/-- If every functional in a spanning finite family vanishes at `v`, then every
functional in the entire dual vanishes at `v`. -/
theorem all_dual_zero_of_spanning_finset_zero
    (t : Finset (Module.Dual k V))
    (htop : Submodule.span k (t : Set (Module.Dual k V)) = ⊤)
    (v : V)
    (hv : ∀ φ ∈ t, φ v = 0) :
    ∀ φ : Module.Dual k V, φ v = 0 := by
  have hspan : Submodule.span k (t : Set (Module.Dual k V)) ≤
      LinearMap.ker (evalAt v) := by
    apply Submodule.span_le.2
    intro φ hφ
    change φ v = 0
    exact hv φ hφ
  intro φ
  have hφtop : φ ∈ Submodule.span k (t : Set (Module.Dual k V)) := by
    rw [htop]
    trivial
  exact hspan hφtop

/-- **Finite auxiliary selection theorem.** If every nonzero global class is
detected by at least one member of an arbitrary probe family, then one can
select exactly `finrank V` actual probes from that family which jointly detect
all classes. This is the finite-dimensional iteration underlying the passage
from a one-prime Taylor--Wiles lemma to a complete auxiliary set. -/
theorem exists_finite_auxiliary_probe_basis
    [FiniteDimensional k V]
    (probe : ι → Module.Dual k V)
    (hdetect : ∀ v : V, v ≠ 0 → ∃ i : ι, probe i v ≠ 0) :
    ∃ t : Finset (Module.Dual k V),
      (t : Set (Module.Dual k V)) ⊆ Set.range probe ∧
      t.card = Module.finrank k V ∧
      LinearIndepOn k id (t : Set (Module.Dual k V)) ∧
      (∀ v : V, (∀ φ ∈ t, φ v = 0) → v = 0) := by
  have hsep := separates_of_detects_each_nonzero probe hdetect
  obtain ⟨t, htRange, htCard, htSpan, htIndep⟩ :=
    exists_finite_probe_basis_of_separates probe hsep
  refine ⟨t, htRange, htCard, htIndep, ?_⟩
  intro v hv
  apply (Module.forall_dual_apply_eq_zero_iff k v).1
  exact all_dual_zero_of_spanning_finset_zero t htSpan v hv

end

end Komorebi.StrongArtin.FiniteAuxiliarySelection
