import Mathlib.Analysis.InnerProductSpace.Projection.Minimal
import Mathlib.Analysis.Convex.Basic
import Mathlib.Topology.Order.MonotoneConvergence
import Mathlib.Tactic

/-!
# Nested minimum corrections (WR02)

Minimum norm points are constructed from nonempty closed convex sets in an arbitrary
real Hilbert space. A general convex projection inequality proves a strong nested
intersection theorem. For affine sets the inequality becomes the exact WR02 energy
identity. No finite dimensionality, separability, or compactness of norm balls is
assumed.
-/

open Filter Set
open scoped Topology

namespace KomorebiSpace.NestedMinimumCorrections

variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]

/-- Membership and global minimum norm, rather than an assumed projection operator. -/
def IsMinimum (C : Set H) (a : H) : Prop :=
  a ∈ C ∧ ∀ x ∈ C, ‖a‖ ≤ ‖x‖

/-- Existence uses the Hilbert projection theorem on the actual closed convex set. -/
theorem exists_minimum (C : Set H) (hne : C.Nonempty) (hc : IsClosed C)
    (hcv : Convex ℝ C) : ∃ a, IsMinimum C a := by
  obtain ⟨a, ha, he⟩ := exists_norm_eq_iInf_of_complete_convex hne hc.isComplete hcv (0 : H)
  refine ⟨a, ha, ?_⟩
  intro x hx
  have hi := ciInf_le (show BddBelow (Set.range (fun w : C => ‖(0 : H) - w‖)) from
    ⟨0, by rintro _ ⟨w, rfl⟩; exact norm_nonneg _⟩) (⟨x, hx⟩ : C)
  simpa only [zero_sub, norm_neg] using he.le.trans hi

omit [CompleteSpace H] in
/-- The normal variational inequality of the minimum norm point. -/
theorem minimum_inner_nonneg {C : Set H} (hcv : Convex ℝ C) {a : H}
    (ha : IsMinimum C a) {x : H} (hx : x ∈ C) :
    0 ≤ inner ℝ a (x - a) := by
  let : Nonempty C := ⟨⟨a, ha.1⟩⟩
  have he : ‖(0 : H) - a‖ = ⨅ w : C, ‖(0 : H) - w‖ := by
    apply le_antisymm
    · apply le_ciInf
      intro w
      simpa only [zero_sub, norm_neg] using ha.2 w w.2
    · exact ciInf_le (show BddBelow (Set.range (fun w : C => ‖(0 : H) - w‖)) from
        ⟨0, by rintro _ ⟨w, rfl⟩; exact norm_nonneg _⟩) (⟨a, ha.1⟩ : C)
  have hi := (norm_eq_iInf_iff_real_inner_le_zero hcv ha.1).mp he x hx
  simpa only [zero_sub, inner_neg_left, neg_nonpos] using hi

omit [CompleteSpace H] in
/-- The convex projection inequality controls distance by the difference of energies. -/
theorem minimum_energy_le {C : Set H} (hcv : Convex ℝ C) {a : H}
    (ha : IsMinimum C a) {x : H} (hx : x ∈ C) :
    ‖x - a‖ ^ 2 ≤ ‖x‖ ^ 2 - ‖a‖ ^ 2 := by
  have hi := minimum_inner_nonneg hcv ha hx
  have he := norm_add_sq_real a (x - a)
  rw [add_sub_cancel] at he
  nlinarith

omit [CompleteSpace H] in
/-- The minimizer is unique, including in the zero dimensional case. -/
theorem minimum_unique {C : Set H} (hcv : Convex ℝ C) {a b : H}
    (ha : IsMinimum C a) (hb : IsMinimum C b) : a = b := by
  have he := minimum_energy_le hcv ha hb.1
  have hn := ha.2 b hb.1
  have hn' := hb.2 a ha.1
  rw [le_antisymm hn' hn] at he
  have hz : ‖b - a‖ = 0 := by nlinarith [sq_nonneg ‖b - a‖, norm_nonneg (b - a)]
  exact (sub_eq_zero.mp (norm_eq_zero.mp hz)).symm

/-- A canonical choice is independent of the existence proof by uniqueness. -/
noncomputable def minimumPoint (C : Set H) (hne : C.Nonempty) (hc : IsClosed C)
    (hcv : Convex ℝ C) : H := Classical.choose (exists_minimum C hne hc hcv)

theorem minimumPoint_spec (C : Set H) (hne : C.Nonempty) (hc : IsClosed C)
    (hcv : Convex ℝ C) : IsMinimum C (minimumPoint C hne hc hcv) :=
  Classical.choose_spec (exists_minimum C hne hc hcv)

omit [InnerProductSpace ℝ H] [CompleteSpace H] in
/-- Bounded energies with the nested projection inequality force a norm Cauchy sequence. -/
theorem cauchySeq_of_energy_le (a : ℕ → H)
    (he : ∀ n m, n ≤ m → ‖a m - a n‖ ^ 2 ≤ ‖a m‖ ^ 2 - ‖a n‖ ^ 2)
    (hb : ∃ M : ℝ, ∀ n, ‖a n‖ ≤ M) : CauchySeq a := by
  obtain ⟨M, hM⟩ := hb
  have hM0 : 0 ≤ M := (norm_nonneg (a 0)).trans (hM 0)
  have hbd : BddAbove (Set.range (fun n => ‖a n‖ ^ 2)) := by
    refine ⟨M ^ 2, ?_⟩
    rintro _ ⟨n, rfl⟩
    exact pow_le_pow_left₀ (norm_nonneg _) (hM n) 2
  apply Metric.cauchySeq_iff'.mpr
  intro ε hε
  obtain ⟨q, ⟨N, rfl⟩, hN⟩ := exists_lt_of_lt_csSup
    (Set.range_nonempty (fun n => ‖a n‖ ^ 2))
    (show sSup (Set.range (fun n => ‖a n‖ ^ 2)) - ε ^ 2 <
      sSup (Set.range (fun n => ‖a n‖ ^ 2)) by nlinarith)
  refine ⟨N, ?_⟩
  intro n hn
  have hnS := le_csSup hbd (Set.mem_range_self n)
  have hd := he N n hn
  rw [dist_eq_norm]
  nlinarith [norm_nonneg (a n - a N)]

/-- The actual minimum sequence of closed convex nested sets converges if uniformly bounded. -/
theorem minimum_sequence_converges (C : ℕ → Set H)
    (hc : ∀ n, IsClosed (C n)) (hcv : ∀ n, Convex ℝ (C n)) (hnest : Antitone C)
    (a : ℕ → H) (ha : ∀ n, IsMinimum (C n) (a n))
    (hb : ∃ M : ℝ, ∀ n, ‖a n‖ ≤ M) :
    ∃ aStar, Tendsto a atTop (𝓝 aStar) ∧ IsMinimum (⋂ n, C n) aStar := by
  have hca : CauchySeq a := cauchySeq_of_energy_le a
    (fun n m hnm => minimum_energy_le (hcv n) (ha n) (hnest hnm (ha m).1)) hb
  obtain ⟨aStar, ht⟩ := cauchySeq_tendsto_of_complete hca
  have hm : aStar ∈ ⋂ n, C n := by
    apply Set.mem_iInter.mpr
    intro n
    apply (hc n).mem_of_tendsto ht
    filter_upwards [Filter.eventually_ge_atTop n] with m hm
    exact hnest hm (ha m).1
  refine ⟨aStar, ht, hm, ?_⟩
  intro x hx
  exact le_of_tendsto ht.norm (Filter.Eventually.of_forall (fun n =>
    (ha n).2 x (Set.mem_iInter.mp hx n)))

/-- General convex intersection bridge: bounded feasible representatives suffice.
This is stronger than the affine existence part of WR02 and supports WR01. -/
theorem exists_mem_iInter_of_closed_convex_bounded (C : ℕ → Set H)
    (hne : ∀ n, (C n).Nonempty) (hc : ∀ n, IsClosed (C n))
    (hcv : ∀ n, Convex ℝ (C n)) (hnest : Antitone C)
    (M : ℝ) (hbudget : ∀ n, ∃ a ∈ C n, ‖a‖ ≤ M) :
    ∃ a, (∀ n, a ∈ C n) ∧ ‖a‖ ≤ M := by
  let a : ℕ → H := fun n => minimumPoint (C n) (hne n) (hc n) (hcv n)
  have ha : ∀ n, IsMinimum (C n) (a n) := fun n =>
    minimumPoint_spec (C n) (hne n) (hc n) (hcv n)
  have hb : ∀ n, ‖a n‖ ≤ M := by
    intro n
    obtain ⟨x, hx, hMx⟩ := hbudget n
    exact ((ha n).2 x hx).trans hMx
  obtain ⟨aStar, ht, hm⟩ := minimum_sequence_converges C hc hcv hnest a ha ⟨M, hb⟩
  exact ⟨aStar, Set.mem_iInter.mp hm.1,
    le_of_tendsto ht.norm (Filter.Eventually.of_forall hb)⟩

omit [CompleteSpace H] in
/-- Affineness upgrades the convex variational inequality to orthogonality. -/
theorem affine_minimum_inner_eq_zero (A : AffineSubspace ℝ H) {a : H}
    (ha : IsMinimum (A : Set H) a) {x : H} (hx : x ∈ A) :
    inner ℝ a (x - a) = 0 := by
  have hp := minimum_inner_nonneg A.convex ha hx
  have hr : -(x - a) + a ∈ A := by
    simpa only [vsub_eq_sub, vadd_eq_add, neg_one_smul] using
      A.smul_vsub_vadd_mem (-1 : ℝ) hx ha.1 ha.1
  have hn := minimum_inner_nonneg A.convex ha hr
  have hid : -(x - a) + a - a = -(x - a) := by abel
  rw [hid, inner_neg_right] at hn
  linarith

omit [CompleteSpace H] in
/-- The exact affine energy identity applies to every point in the same affine set. -/
theorem affine_minimum_energy (A : AffineSubspace ℝ H) {a : H}
    (ha : IsMinimum (A : Set H) a) {x : H} (hx : x ∈ A) :
    ‖x - a‖ ^ 2 = ‖x‖ ^ 2 - ‖a‖ ^ 2 := by
  have hi := affine_minimum_inner_eq_zero A ha hx
  have he := norm_add_sq_real a (x - a)
  rw [add_sub_cancel, hi] at he
  linarith

/-- Canonically constructed minimum corrections for a sequence of affine constraints. -/
noncomputable def affineCorrections (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H)) : ℕ → H :=
  fun n => minimumPoint (A n : Set H) (hne n) (hc n) (A n).convex

theorem affineCorrections_spec (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H)) (n : ℕ) :
    IsMinimum (A n : Set H) (affineCorrections A hne hc n) :=
  minimumPoint_spec (A n : Set H) (hne n) (hc n) (A n).convex

/-- WR02 finite energy equality for all ordered index pairs. -/
theorem nested_affine_energy (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H))
    (hnest : Antitone A) {n m : ℕ} (hnm : n ≤ m) :
    ‖affineCorrections A hne hc m - affineCorrections A hne hc n‖ ^ 2 =
      ‖affineCorrections A hne hc m‖ ^ 2 - ‖affineCorrections A hne hc n‖ ^ 2 :=
  affine_minimum_energy (A n) (affineCorrections_spec A hne hc n)
    (hnest hnm (affineCorrections_spec A hne hc m).1)

/-- WR02: the minimum correction norms are nondecreasing. -/
theorem nested_affine_norm_monotone (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H))
    (hnest : Antitone A) : Monotone (fun n => ‖affineCorrections A hne hc n‖) := by
  intro n m hnm
  exact (affineCorrections_spec A hne hc n).2 _
    (hnest hnm (affineCorrections_spec A hne hc m).1)

/-- WR02: nonempty intersection is equivalent to a finite uniform minimum budget. -/
theorem nested_affine_intersection_iff_bounded (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H))
    (hnest : Antitone A) :
    (∃ x, ∀ n, x ∈ A n) ↔ ∃ M : ℝ, ∀ n, ‖affineCorrections A hne hc n‖ ≤ M := by
  constructor
  · rintro ⟨x, hx⟩
    exact ⟨‖x‖, fun n => (affineCorrections_spec A hne hc n).2 x (hx n)⟩
  · rintro ⟨M, hM⟩
    obtain ⟨x, hx, _⟩ := exists_mem_iInter_of_closed_convex_bounded
      (fun n => (A n : Set H)) hne hc (fun n => (A n).convex) hnest M
      (fun n => ⟨affineCorrections A hne hc n, (affineCorrections_spec A hne hc n).1, hM n⟩)
    exact ⟨x, hx⟩

/-- WR02: the minimum corrections converge strongly to the unique minimum in the
intersection, and the exact error is the remaining energy. -/
theorem nested_affine_strong_realization (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H))
    (hnest : Antitone A) (hb : ∃ M : ℝ, ∀ n, ‖affineCorrections A hne hc n‖ ≤ M) :
    ∃ aStar, Tendsto (affineCorrections A hne hc) atTop (𝓝 aStar) ∧
      IsMinimum (⋂ n, (A n : Set H)) aStar ∧
      (∀ b, IsMinimum (⋂ n, (A n : Set H)) b → b = aStar) ∧
      ∀ n, ‖aStar - affineCorrections A hne hc n‖ ^ 2 =
        ‖aStar‖ ^ 2 - ‖affineCorrections A hne hc n‖ ^ 2 := by
  obtain ⟨aStar, ht, hm⟩ := minimum_sequence_converges
    (fun n => (A n : Set H)) hc (fun n => (A n).convex) hnest
    (affineCorrections A hne hc) (affineCorrections_spec A hne hc) hb
  refine ⟨aStar, ht, hm, ?_, ?_⟩
  · intro b hb
    exact minimum_unique (convex_iInter (fun n => (A n).convex)) hb hm
  · intro n
    exact affine_minimum_energy (A n) (affineCorrections_spec A hne hc n)
      (Set.mem_iInter.mp hm.1 n)

/-- WR02: an empty intersection forces the entire norm sequence to infinity. -/
theorem nested_affine_escape (A : ℕ → AffineSubspace ℝ H)
    (hne : ∀ n, (A n : Set H).Nonempty) (hc : ∀ n, IsClosed (A n : Set H))
    (hnest : Antitone A) (hempty : ¬ ∃ x, ∀ n, x ∈ A n) :
    Tendsto (fun n => ‖affineCorrections A hne hc n‖) atTop atTop := by
  apply tendsto_atTop_atTop_of_monotone' (nested_affine_norm_monotone A hne hc hnest)
  intro hb
  apply hempty
  apply (nested_affine_intersection_iff_bounded A hne hc hnest).mpr
  obtain ⟨M, hM⟩ := hb
  exact ⟨M, fun n => hM (Set.mem_range_self n)⟩

end KomorebiSpace.NestedMinimumCorrections
