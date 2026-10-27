import PaperX.IntegerCellChartCounting

open Set
open scoped NNReal

namespace PaperX.IntegerCellBounds

variable {ι κ β : Type*} [Fintype ι] [Fintype κ] [Fintype β]

/-- Uniform cell bound for any set covered by finitely many dilated Lipschitz charts. -/
theorem touching_finite_charts_bound (S : Set (ι → ℝ))
    (f : β → (κ → ℝ) → (ι → ℝ)) (L : ℝ≥0)
    (hf : ∀ b, LipschitzOnWith L (f b) (Set.Icc (0 : κ → ℝ) 1))
    (a : ι → ℝ) (t : ℝ) (ht : 1 ≤ t)
    (hS : S ⊆ ⋃ b, (fun x => a + t • f b x) '' Set.Icc (0 : κ → ℝ) 1) :
    (touching S).Finite ∧ (touching S).ncard ≤
      Fintype.card β * (Nat.ceil t + 1) ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι := by
  classical
  have hcover : S ⊆ ⋃ bk : β × (κ → Fin (Nat.ceil t + 1)),
      Metric.closedBall (a + t • f bk.1 (meshPoint (Nat.ceil t) bk.2)) (L : ℝ) := by
    intro x hx
    obtain ⟨b, hb⟩ := Set.mem_iUnion.mp (hS hx)
    obtain ⟨k, hk⟩ := Set.mem_iUnion.mp (chart_image_ball_cover (f b) L (hf b) a t ht hb)
    exact Set.mem_iUnion.mpr ⟨(b, k), hk⟩
  simpa [Fintype.card_prod, Fintype.card_fun] using touching_of_finite_ball_cover S
    (fun bk : β × (κ → Fin (Nat.ceil t + 1)) =>
      a + t • f bk.1 (meshPoint (Nat.ceil t) bk.2)) (L : ℝ) hcover

omit [Fintype ι] [Fintype κ] [Fintype β] in
theorem ceil_add_one_le_three_mul (t : ℝ) (ht : 1 ≤ t) :
    ((Nat.ceil t + 1 : ℕ) : ℝ) ≤ 3 * t := by
  have h := Nat.ceil_lt_add_one (show 0 ≤ t by linarith)
  push_cast
  linarith

/-- A real polynomial bound with degree equal to the chart-domain dimension. -/
theorem touching_finite_charts_polynomial_bound (S : Set (ι → ℝ))
    (f : β → (κ → ℝ) → (ι → ℝ)) (L : ℝ≥0)
    (hf : ∀ b, LipschitzOnWith L (f b) (Set.Icc (0 : κ → ℝ) 1))
    (a : ι → ℝ) (t : ℝ) (ht : 1 ≤ t)
    (hS : S ⊆ ⋃ b, (fun x => a + t • f b x) '' Set.Icc (0 : κ → ℝ) 1) :
    (touching S).Finite ∧ ((touching S).ncard : ℝ) ≤
      ((Fintype.card β : ℝ) * 3 ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι) * t ^ Fintype.card κ := by
  obtain ⟨hfin, hn⟩ := touching_finite_charts_bound S f L hf a t ht hS
  refine ⟨hfin, ?_⟩
  have hpow : (((Nat.ceil t + 1 : ℕ) : ℝ)) ^ Fintype.card κ ≤
      (3 * t) ^ Fintype.card κ := by
    gcongr
    exact ceil_add_one_le_three_mul t ht
  have hn' : ((touching S).ncard : ℝ) ≤
      (Fintype.card β : ℝ) * ((Nat.ceil t + 1 : ℕ) : ℝ) ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι := by exact_mod_cast hn
  calc
    _ ≤ (Fintype.card β : ℝ) * ((Nat.ceil t + 1 : ℕ) : ℝ) ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι := hn'
    _ ≤ (Fintype.card β : ℝ) * (3 * t) ^ Fintype.card κ *
        (2 * Nat.ceil ((L : ℝ) + 1) + 3) ^ Fintype.card ι := by gcongr
    _ = _ := by rw [mul_pow]; ring

end PaperX.IntegerCellBounds
