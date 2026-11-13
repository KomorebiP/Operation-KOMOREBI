/-
Copyright (c) 2026 Komorebi P.
Released under the MIT license.
Authors: Komorebi P.
-/
import Mathlib.Analysis.Calculus.ContDiff.FaaDiBruno
import Mathlib.Combinatorics.Enumerative.Stirling

open scoped BigOperators
noncomputable section

namespace Komorebi.PaperIII.CompositionTermCount

theorem sum_partitions_succ (n : ℕ) (f : ℕ → ℕ) :
    (∑ c : OrderedFinpartition (n + 1), f c.length) =
      ∑ c : OrderedFinpartition n, (f (c.length + 1) + c.length * f c.length) := by
  rw [← (OrderedFinpartition.extendEquiv n).sum_comp]
  simp only [Fintype.sum_sigma, OrderedFinpartition.extendEquiv_apply,
    Fintype.sum_option, OrderedFinpartition.extend_none,
    OrderedFinpartition.extend_some, OrderedFinpartition.extendLeft_length,
    OrderedFinpartition.extendMiddle_length, Finset.sum_const, Finset.card_univ,
    Fintype.card_fin, smul_eq_mul]

theorem sum_stirling_succ (n : ℕ) (f : ℕ → ℕ) :
    (∑ k ∈ Finset.range (n + 2), Nat.stirlingSecond (n + 1) k * f k) =
      ∑ k ∈ Finset.range (n + 1),
        Nat.stirlingSecond n k * (f (k + 1) + k * f k) := by
  have shift :
      (∑ k ∈ Finset.range (n + 1), (k + 1) * Nat.stirlingSecond n (k + 1) * f (k + 1)) =
        ∑ k ∈ Finset.range (n + 1), k * Nat.stirlingSecond n k * f k := by
    have h := Finset.sum_range_succ' (fun k => k * Nat.stirlingSecond n k * f k) (n + 1)
    rw [Finset.sum_range_succ] at h
    simpa [Nat.stirlingSecond_eq_zero_of_lt (Nat.lt_succ_self n)] using h.symm
  rw [Finset.sum_range_succ']
  simp only [Nat.stirlingSecond_succ_zero, zero_mul, add_zero]
  have distribute (k : ℕ) : Nat.stirlingSecond (n + 1) (k + 1) * f (k + 1) =
      (k + 1) * Nat.stirlingSecond n (k + 1) * f (k + 1) +
        Nat.stirlingSecond n k * f (k + 1) := by
    rw [Nat.stirlingSecond_succ_succ]
    ring
  simp_rw [distribute]
  rw [Finset.sum_add_distrib]
  rw [shift]
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro k _
  ring

theorem sum_partitions_eq_stirling (n : ℕ) (f : ℕ → ℕ) :
    (∑ c : OrderedFinpartition n, f c.length) =
      ∑ k ∈ Finset.range (n + 1), Nat.stirlingSecond n k * f k := by
  induction n generalizing f with
  | zero => simp [OrderedFinpartition.default_eq]
  | succ n ih =>
    rw [sum_partitions_succ, ih (fun k => f (k + 1) + k * f k)]
    exact (sum_stirling_succ n f).symm

/-- Exactly the indexing type of the two finite sums in packet composition. -/
abbrev DecoratedPartition (n : ℕ) (J : Type*) :=
  (c : OrderedFinpartition n) × (Fin c.length → J)

theorem card_decoratedPartition (n : ℕ) (J : Type*) [Fintype J] :
    Fintype.card (DecoratedPartition n J) =
      ∑ k ∈ Finset.range (n + 1), Nat.stirlingSecond n k * Fintype.card J ^ k := by
  rw [Fintype.card_sigma]
  simp only [Fintype.card_fun, Fintype.card_fin]
  exact sum_partitions_eq_stirling n (fun k => Fintype.card J ^ k)

/-- Proposition 17.6, including the empty intermediate packet set. -/
theorem card_decoratedPartition_pos (n : ℕ) (hn : 0 < n) (J : Type*) [Fintype J] :
    Fintype.card (DecoratedPartition n J) =
      ∑ k ∈ Finset.Icc 1 n, Nat.stirlingSecond n k * Fintype.card J ^ k := by
  rw [card_decoratedPartition]
  symm
  apply Finset.sum_subset
  · intro k hk
    simp only [Finset.mem_Icc, Finset.mem_range] at *
    omega
  · intro k hk hnot
    have hk0 : k = 0 := by
      simp only [Finset.mem_Icc, Finset.mem_range] at *
      omega
    subst k
    obtain ⟨m, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hn)
    simp

theorem card_decoratedPartition_zero (J : Type*) [Fintype J] :
    Fintype.card (DecoratedPartition 0 J) = 1 := by
  rw [card_decoratedPartition]
  simp

theorem card_decoratedPartition_one (J : Type*) [Fintype J] :
    Fintype.card (DecoratedPartition 1 J) = Fintype.card J := by
  rw [card_decoratedPartition]
  simp [Finset.sum_range_succ, Nat.stirlingSecond]

theorem card_decoratedPartition_two (J : Type*) [Fintype J] :
    Fintype.card (DecoratedPartition 2 J) = Fintype.card J ^ 2 + Fintype.card J := by
  rw [card_decoratedPartition]
  simp [Finset.sum_range_succ, Nat.stirlingSecond, add_comm]

end Komorebi.PaperIII.CompositionTermCount
