import PaperX.IntegerCellBounds
import Mathlib.Analysis.Normed.Module.Basic
import Mathlib.Topology.MetricSpace.Lipschitz

open Set
open scoped NNReal

namespace PaperX.IntegerCellBounds

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- Vertices of the regular mesh of denominator `m`. -/
noncomputable def meshPoint (m : ℕ) (k : κ → Fin (m + 1)) : κ → ℝ :=
  fun i => (k i : ℕ) / (m : ℝ)

omit [Fintype ι] [Fintype κ] in
theorem meshPoint_mem_unitBox (m : ℕ) (hm : 0 < m) (k : κ → Fin (m + 1)) :
    meshPoint m k ∈ Set.Icc (0 : κ → ℝ) 1 := by
  have hm' : (0 : ℝ) < m := by exact_mod_cast hm
  constructor
  · intro i
    exact div_nonneg (Nat.cast_nonneg _) hm'.le
  · intro i
    apply (div_le_one hm').mpr
    exact_mod_cast (Nat.le_of_lt_succ (k i).isLt)

omit [Fintype ι] in
theorem exists_meshPoint_dist_le (m : ℕ) (hm : 0 < m) (x : κ → ℝ)
    (hx : x ∈ Set.Icc (0 : κ → ℝ) 1) :
    ∃ k : κ → Fin (m + 1), dist x (meshPoint m k) ≤ 1 / (m : ℝ) := by
  have hm' : (0 : ℝ) < m := by exact_mod_cast hm
  let k : κ → Fin (m + 1) := fun i =>
    ⟨Nat.floor ((m : ℝ) * x i), Nat.lt_succ_of_le (Nat.floor_le_of_le (by
      have hxi := hx.2 i
      change x i ≤ 1 at hxi
      nlinarith))⟩
  refine ⟨k, (dist_pi_le_iff (by positivity)).mpr ?_⟩
  intro i
  have hx0 : 0 ≤ x i := hx.1 i
  have hfloor := Nat.floor_le (mul_nonneg hm'.le hx0)
  have hlt := Nat.lt_floor_add_one ((m : ℝ) * x i)
  change |x i - (Nat.floor ((m : ℝ) * x i) : ℝ) / (m : ℝ)| ≤ 1 / (m : ℝ)
  rw [abs_le]
  constructor
  · have h : (Nat.floor ((m : ℝ) * x i) : ℝ) / (m : ℝ) ≤ x i :=
      (div_le_iff₀ hm').mpr (by nlinarith [hfloor])
    have hinv : 0 ≤ 1 / (m : ℝ) := by positivity
    linarith
  · apply (le_div_iff₀ hm').mpr
    have hid : ((Nat.floor ((m : ℝ) * x i) : ℝ) / (m : ℝ)) * m =
        (Nat.floor ((m : ℝ) * x i) : ℝ) := div_mul_cancel₀ _ hm'.ne'
    nlinarith

/-- A dilated translated Lipschitz chart is covered by a regular finite family of balls. -/
theorem chart_image_ball_cover (f : (κ → ℝ) → (ι → ℝ)) (L : ℝ≥0)
    (hf : LipschitzOnWith L f (Set.Icc (0 : κ → ℝ) 1))
    (a : ι → ℝ) (t : ℝ) (ht : 1 ≤ t) :
    (fun x => a + t • f x) '' Set.Icc (0 : κ → ℝ) 1 ⊆
      ⋃ k : κ → Fin (Nat.ceil t + 1),
        Metric.closedBall (a + t • f (meshPoint (Nat.ceil t) k)) (L : ℝ) := by
  have ht0 : 0 ≤ t := by linarith
  have hm : 0 < Nat.ceil t := Nat.ceil_pos.mpr (by linarith)
  have hm' : (0 : ℝ) < Nat.ceil t := by exact_mod_cast hm
  have htm : t ≤ (Nat.ceil t : ℝ) := Nat.le_ceil _
  rintro y ⟨x, hx, rfl⟩
  obtain ⟨k, hk⟩ := exists_meshPoint_dist_le (Nat.ceil t) hm x hx
  apply Set.mem_iUnion.mpr
  refine ⟨k, ?_⟩
  change dist (a + t • f x) (a + t • f (meshPoint (Nat.ceil t) k)) ≤ (L : ℝ)
  have hdist := hf.dist_le_mul x hx (meshPoint (Nat.ceil t) k)
    (meshPoint_mem_unitBox _ hm k)
  have hsmall : dist (f x) (f (meshPoint (Nat.ceil t) k)) ≤
      (L : ℝ) / (Nat.ceil t : ℝ) := by
    calc
      _ ≤ (L : ℝ) * dist x (meshPoint (Nat.ceil t) k) := hdist
      _ ≤ (L : ℝ) * (1 / (Nat.ceil t : ℝ)) := mul_le_mul_of_nonneg_left hk L.coe_nonneg
      _ = _ := by ring
  rw [dist_add_left, dist_eq_norm, ← smul_sub, norm_smul, Real.norm_eq_abs, abs_of_nonneg ht0]
  have hdist' : ‖f x - f (meshPoint (Nat.ceil t) k)‖ ≤
      (L : ℝ) / (Nat.ceil t : ℝ) := by simpa only [dist_eq_norm] using hsmall
  calc
    _ ≤ t * ((L : ℝ) / (Nat.ceil t : ℝ)) := mul_le_mul_of_nonneg_left hdist' ht0
    _ ≤ (Nat.ceil t : ℝ) * ((L : ℝ) / (Nat.ceil t : ℝ)) :=
      mul_le_mul_of_nonneg_right htm (div_nonneg L.coe_nonneg hm'.le)
    _ = (L : ℝ) := mul_div_cancel₀ _ hm'.ne'

/-- Explicit, translation-uniform cell bound for one Lipschitz chart. -/
theorem touching_chart_image_bound (f : (κ → ℝ) → (ι → ℝ)) (L : ℝ≥0)
    (hf : LipschitzOnWith L f (Set.Icc (0 : κ → ℝ) 1))
    (a : ι → ℝ) (t : ℝ) (ht : 1 ≤ t) :
    let S := (fun x => a + t • f x) '' Set.Icc (0 : κ → ℝ) 1
    (touching S).Finite ∧ (touching S).ncard ≤
      (Nat.ceil t + 1) ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι := by
  classical
  simpa [Fintype.card_fun] using touching_of_finite_ball_cover
    ((fun x => a + t • f x) '' Set.Icc (0 : κ → ℝ) 1)
    (fun k : κ → Fin (Nat.ceil t + 1) => a + t • f (meshPoint (Nat.ceil t) k))
    (L : ℝ) (chart_image_ball_cover f L hf a t ht)

end PaperX.IntegerCellBounds
