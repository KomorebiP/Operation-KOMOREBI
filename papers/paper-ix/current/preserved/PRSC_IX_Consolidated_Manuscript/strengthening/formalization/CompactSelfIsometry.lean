module

public import Mathlib.Topology.MetricSpace.Isometry
public import Mathlib.Topology.MetricSpace.Cauchy
public import Mathlib.Topology.Sequences
public import Mathlib.Tactic

@[expose] public section

namespace KomorebiPaperIX.CompactSelfIsometry

variable {X : Type*} [MetricSpace X] {f : X → X}

theorem iterate_isometry (hf : Isometry f) (n : ℕ) : Isometry f^[n] := by
  induction n with
  | zero => exact isometry_id
  | succ n ih => exact ih.comp hf

theorem denseRange [CompactSpace X] (hf : Isometry f) : DenseRange f := by
  rw [Metric.denseRange_iff]
  intro x ε hε
  obtain ⟨a, φ, hφ, ht⟩ := CompactSpace.tendsto_subseq (fun n : ℕ => f^[n] x)
  obtain ⟨N, hN⟩ := Metric.cauchySeq_iff.mp ht.cauchySeq ε hε
  have hclose := hN N le_rfl (N + 1) (by omega)
  have hlt : φ N < φ (N + 1) := hφ (by omega)
  let k := φ (N + 1) - φ N
  have hk : 0 < k := by dsimp [k]; omega
  have heq : φ N + k = φ (N + 1) := by dsimp [k]; omega
  have hd : dist x (f^[k] x) < ε := by
    rw [← (iterate_isometry hf (φ N)).dist_eq]
    simpa only [Function.comp_apply, ← Function.iterate_add_apply, heq] using hclose
  obtain ⟨l, hl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hk)
  refine ⟨f^[l] x, ?_⟩
  simpa only [hl, Function.iterate_succ_apply'] using hd

theorem surjective [CompactSpace X] (hf : Isometry f) : Function.Surjective f := by
  intro x
  have hx := denseRange hf x
  rw [(isCompact_range hf.continuous).isClosed.closure_eq] at hx
  exact hx

end KomorebiPaperIX.CompactSelfIsometry
