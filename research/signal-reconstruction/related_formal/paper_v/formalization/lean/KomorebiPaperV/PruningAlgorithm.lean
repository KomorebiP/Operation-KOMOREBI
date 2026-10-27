import KomorebiPaperV.PruningSums

/-!
Author: Komorebi P. A bottom-up evaluator with cached child results.
The cost model charges one node visit, one comparison per internal node, and
one addition per child when summing cached values. Scalar node costs are inputs.
The theorem concerns this unit-cost model, not Lean runtime or output printing.
-/
namespace KomorebiPaperV.PruningAlgorithm
open KomorebiPaperV.FiniteAdaptive KomorebiPaperV.CompletePrunings KomorebiPaperV.PruningSums
variable {A : Type*}

structure Result (t : FiniteAdaptive.Tree A) where
  cut : Cut t
  cost : ℝ
  comparisons : ℕ
  additions : ℕ
  visits : ℕ

noncomputable def solve (c : A → ℝ) : (t : FiniteAdaptive.Tree A) → Result t
  | .leaf a => ⟨.stop _, c a, 0, 0, 1⟩
  | .branch a n ch =>
      let child := fun i => solve c (ch i)
      let total := ∑ i, (child i).cost
      let stop := c a ≤ total
      ⟨if stop then .stop _ else .split (fun i => (child i).cut),
       min (c a) total,
       1 + ∑ i, (child i).comparisons,
       (n+1) + ∑ i, (child i).additions,
       1 + ∑ i, (child i).visits⟩

def nodes : FiniteAdaptive.Tree A → ℕ
  | .leaf _ => 1
  | .branch _ _ ch => 1 + ∑ i, nodes (ch i)

theorem solve_correct (c : A → ℝ) (t : FiniteAdaptive.Tree A) :
    (solve c t).cost = value c t ∧ (solve c t).cut = best c t := by
  induction t with
  | leaf a => exact ⟨rfl,rfl⟩
  | branch a n ch ih =>
    have hc : (∑ i, (solve c (ch i)).cost) = ∑ i, value c (ch i) :=
      Finset.sum_congr rfl (fun i _ => (ih i).1)
    constructor
    · simp only [solve, value, hc]
    · simp only [solve, best, hc]
      split_ifs
      · rfl
      · congr 1
        funext i
        exact (ih i).2

theorem solve_comparisons (c : A → ℝ) (t : FiniteAdaptive.Tree A) :
    (solve c t).comparisons = internalNodes t := by
  induction t with
  | leaf a => rfl
  | branch a n ch ih =>
    simp only [solve, internalNodes]
    rw [Finset.sum_congr rfl (fun i _ => ih i)]
    omega

theorem solve_visits (c : A → ℝ) (t : FiniteAdaptive.Tree A) :
    (solve c t).visits = nodes t := by
  induction t with
  | leaf a => rfl
  | branch a n ch ih =>
    simp only [solve, nodes]
    rw [Finset.sum_congr rfl (fun i _ => ih i)]

theorem solve_additions (c : A → ℝ) (t : FiniteAdaptive.Tree A) :
    (solve c t).additions + 1 = nodes t := by
  induction t with
  | leaf a => rfl
  | branch a n ch ih =>
    have hs : ∑ i, ((solve c (ch i)).additions+1) = ∑ i, nodes (ch i) :=
      Finset.sum_congr rfl (fun i _ => ih i)
    simp only [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ,
      Fintype.card_fin, smul_eq_mul, mul_one] at hs
    dsimp [solve, nodes]
    omega

theorem internal_le_nodes (t : FiniteAdaptive.Tree A) : internalNodes t ≤ nodes t := by
  induction t with
  | leaf a => simp [internalNodes, nodes]
  | branch a n ch ih =>
    have h := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => ih i)
    dsimp [internalNodes, nodes]
    omega

theorem solve_linear_work (c : A → ℝ) (t : FiniteAdaptive.Tree A) :
    (solve c t).visits + (solve c t).comparisons + (solve c t).additions ≤ 3 * nodes t := by
  have hv := solve_visits c t
  have hc := solve_comparisons c t
  have ha := solve_additions c t
  have hi := internal_le_nodes t
  omega

theorem computed_antichain_optimal (c : A → ℝ) (t : FiniteAdaptive.Tree A) (S : Pruning t) :
    nodeSum c (pruningEquiv t (solve c t).cut) ≤ nodeSum c S := by
  rw [(solve_correct c t).2]
  exact selected_global_minimum c t S

theorem antichain_probability {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (good : Set Ω) (δ : ENNReal)
    (c e : A → ℝ) (d : Ω → A → ℝ) (t : FiniteAdaptive.Tree A) (γ : ℝ)
    (hgood : ∀ ω ∈ good, ∀ a, |d ω a-c a| ≤ e a)
    (hg : ∀ S : Pruning t, S ≠ selected c t → γ ≤ nodeSum c S-nodeSum c (selected c t))
    (hm : 2*envelope e t < γ) (hprob : 1-δ ≤ μ good) :
    1-δ ≤ μ {ω | selected (d ω) t = selected c t} := by
  apply hprob.trans
  apply MeasureTheory.measure_mono
  intro ω hω
  exact antichain_selector_stable c (d ω) e (hgood ω hω) t γ hg hm

end KomorebiPaperV.PruningAlgorithm
