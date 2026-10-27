import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Topology.MetricSpace.Pseudo.Pi
import Mathlib.Topology.MetricSpace.Bounded
import Mathlib.Data.Int.Interval
import Mathlib.Data.Set.Card
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic

open scoped BigOperators
open Set

namespace PaperX.IntegerCellBounds

variable {ι : Type*} [Fintype ι]

/-- Closed unit cells in the standard integer lattice. -/
def closedCell (z : ι → ℤ) : Set (ι → ℝ) :=
  Set.Icc (fun i => (z i : ℝ)) (fun i => (z i : ℝ) + 1)

/-- Integer indices of closed unit cells that touch a set. -/
def touching (S : Set (ι → ℝ)) : Set (ι → ℤ) :=
  {z | (closedCell z ∩ S).Nonempty}

/-- A finite containing box, centered at coordinatewise integer floors. -/
noncomputable def indexBox (c : ι → ℝ) (r : ℕ) : Finset (ι → ℤ) := by
  classical
  exact Fintype.piFinset fun i =>
    Finset.Icc (⌊c i⌋ - (r : ℤ) - 1) (⌊c i⌋ + (r : ℤ) + 1)

theorem card_indexBox (c : ι → ℝ) (r : ℕ) :
    (indexBox c r).card = (2 * r + 3) ^ Fintype.card ι := by
  classical
  simp only [indexBox, Fintype.card_piFinset, Int.card_Icc]
  have h : ∀ i, ((⌊c i⌋ + (r : ℤ) + 1 + 1 - (⌊c i⌋ - (r : ℤ) - 1)).toNat)
      = 2 * r + 3 := by
    intro i
    omega
  simp only [h, Finset.prod_const, Finset.card_univ]

theorem mem_indexBox_of_coord_bound (c : ι → ℝ) (r : ℕ) (z : ι → ℤ)
    (h : ∀ i, |(z i : ℝ) - c i| ≤ r) : z ∈ indexBox c r := by
  classical
  apply Fintype.mem_piFinset.mpr
  intro i
  have hc := Int.floor_le (c i)
  have hd := Int.lt_floor_add_one (c i)
  obtain ⟨hl, hu⟩ := abs_le.mp (h i)
  apply Finset.mem_Icc.mpr
  constructor
  · exact_mod_cast (show (⌊c i⌋ : ℝ) - (r : ℝ) - 1 ≤ (z i : ℝ) by linarith)
  · exact_mod_cast (show (z i : ℝ) ≤ (⌊c i⌋ : ℝ) + (r : ℝ) + 1 by linarith)

theorem touching_closedBall_subset_indexBox (c : ι → ℝ) (R : ℝ) :
    touching (Metric.closedBall c R) ⊆ (indexBox c (Nat.ceil (R + 1)) : Set (ι → ℤ)) := by
  intro z hz
  obtain ⟨x, hx, hxc⟩ := hz
  apply mem_indexBox_of_coord_bound
  intro i
  have hd : dist x c ≤ R := hxc
  have hi : dist (x i) (c i) ≤ dist x c := dist_le_pi_dist x c i
  have hc : R + 1 ≤ (Nat.ceil (R + 1) : ℝ) := Nat.le_ceil _
  have hxlo := hx.1 i
  have hxhi := hx.2 i
  rw [Real.dist_eq] at hi
  obtain ⟨hlo, hhi⟩ := abs_le.mp (hi.trans hd)
  apply abs_le.mpr
  constructor <;> linarith

theorem finite_touching_closedBall (c : ι → ℝ) (R : ℝ) :
    (touching (Metric.closedBall c R)).Finite :=
  (indexBox c (Nat.ceil (R + 1))).finite_toSet.subset
    (touching_closedBall_subset_indexBox c R)

theorem ncard_touching_closedBall_le (c : ι → ℝ) (R : ℝ) :
    (touching (Metric.closedBall c R)).ncard ≤
      (2 * Nat.ceil (R + 1) + 3) ^ Fintype.card ι := by
  calc
    _ ≤ ((indexBox c (Nat.ceil (R + 1))) : Set (ι → ℤ)).ncard :=
      Set.ncard_le_ncard (touching_closedBall_subset_indexBox c R)
        (Finset.finite_toSet _)
    _ = _ := by rw [Set.ncard_coe_finset, card_indexBox]

omit [Fintype ι] in
theorem touching_mono {S T : Set (ι → ℝ)} (h : S ⊆ T) : touching S ⊆ touching T := by
  rintro z ⟨x, hx, hxs⟩
  exact ⟨x, hx, h hxs⟩

/-- A finite cover by uniformly bounded balls gives a uniform cell-count bound. -/
theorem touching_of_finite_ball_cover {β : Type*} [Fintype β]
    (S : Set (ι → ℝ)) (c : β → (ι → ℝ)) (R : ℝ)
    (hcover : S ⊆ ⋃ b, Metric.closedBall (c b) R) :
    (touching S).Finite ∧ (touching S).ncard ≤
      Fintype.card β * (2 * Nat.ceil (R + 1) + 3) ^ Fintype.card ι := by
  classical
  let B : Finset (ι → ℤ) := Finset.univ.biUnion fun b => indexBox (c b) (Nat.ceil (R + 1))
  have hsub : touching S ⊆ (B : Set (ι → ℤ)) := by
    rintro z ⟨x, hx, hxs⟩
    obtain ⟨b, hb⟩ := Set.mem_iUnion.mp (hcover hxs)
    apply Finset.mem_biUnion.mpr
    exact ⟨b, Finset.mem_univ _, touching_closedBall_subset_indexBox (c b) R ⟨x, hx, hb⟩⟩
  refine ⟨B.finite_toSet.subset hsub, ?_⟩
  calc
    (touching S).ncard ≤ (B : Set (ι → ℤ)).ncard := Set.ncard_le_ncard hsub B.finite_toSet
    _ = B.card := Set.ncard_coe_finset _
    _ ≤ ∑ b : β, (indexBox (c b) (Nat.ceil (R + 1))).card := Finset.card_biUnion_le
    _ = _ := by simp [card_indexBox]

/-- Bounded sets meet only finitely many closed integer unit cells. -/
theorem finite_touching_of_isBounded {S : Set (ι → ℝ)} (hS : Bornology.IsBounded S) :
    (touching S).Finite := by
  obtain ⟨R, hR⟩ := hS.subset_closedBall (0 : ι → ℝ)
  exact (finite_touching_closedBall _ R).subset (touching_mono hR)

/-- The upper-right unit-cell tags lying in a bounded set form a finite set. -/
theorem finite_upper_tags_of_isBounded {S : Set (ι → ℝ)} (hS : Bornology.IsBounded S) :
    {z : ι → ℤ | (fun i => (z i : ℝ) + 1) ∈ S}.Finite := by
  apply (finite_touching_of_isBounded hS).subset
  intro z hz
  refine ⟨fun i => (z i : ℝ) + 1, ⟨?_, le_rfl⟩, hz⟩
  intro i
  exact le_add_of_nonneg_right zero_le_one

end PaperX.IntegerCellBounds
