import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic

set_option autoImplicit false
noncomputable section
open Filter Set
open scoped Topology

namespace KomorebiSpace.DiagonalRegularization

/-- Any budget above the initial mesh value lies between consecutive mesh values. -/
lemma exists_budget_mesh_bracket (u : ℕ → ℝ)
    (hu : Tendsto u atTop atTop) (M : ℝ) (hM : u 0 ≤ M) :
    ∃ n : ℕ, u n ≤ M ∧ M < u (n + 1) := by
  have he : ∃ n : ℕ, M < u n := (hu.eventually (eventually_gt_atTop M)).exists
  let k := Nat.find he
  have hk : M < u k := Nat.find_spec he
  have hkpos : 0 < k := by
    by_contra h
    have hkzero : k = 0 := by omega
    rw [hkzero] at hk
    linarith
  have hmin : ¬M < u (k - 1) := Nat.find_min he (by change k - 1 < k; omega)
  refine ⟨k - 1, le_of_not_gt hmin, ?_⟩
  have heq : k - 1 + 1 = k := by omega
  simpa only [heq] using hk

/-- A bracket index for every real budget, with the irrelevant initial segment assigned zero. -/
def budgetMeshIndex (u : ℕ → ℝ) (hu : Tendsto u atTop atTop) (M : ℝ) : ℕ :=
  if hM : u 0 ≤ M then Classical.choose (exists_budget_mesh_bracket u hu M hM) else 0

lemma budgetMeshIndex_bracket (u : ℕ → ℝ) (hu : Tendsto u atTop atTop)
    (M : ℝ) (hM : u 0 ≤ M) :
    u (budgetMeshIndex u hu M) ≤ M ∧ M < u (budgetMeshIndex u hu M + 1) := by
  unfold budgetMeshIndex
  rw [dif_pos hM]
  exact Classical.choose_spec (exists_budget_mesh_bracket u hu M hM)

lemma budgetMeshIndex_tendsto (u : ℕ → ℝ) (hmono : Monotone u)
    (hu : Tendsto u atTop atTop) : Tendsto (budgetMeshIndex u hu) atTop atTop := by
  refine tendsto_atTop_atTop.mpr fun N => ⟨max (u 0) (u N), fun M hM => ?_⟩
  have hMzero : u 0 ≤ M := le_trans (le_max_left _ _) hM
  have hMN : u N ≤ M := le_trans (le_max_right _ _) hM
  have hb := (budgetMeshIndex_bracket u hu M hMzero).2
  by_contra h
  have hle : budgetMeshIndex u hu M + 1 ≤ N := by omega
  have hm := hmono hle
  linarith

lemma tendsto_budget_mesh_lower (u : ℕ → ℝ) (β : ℝ → ℝ) (c : ℝ)
    (hpos : ∀ n, 0 < u n)
    (hratio : Tendsto (fun n => u (n + 1) / u n) atTop (𝓝 1))
    (hprod : Tendsto (fun n => u n * β (u n)) atTop (𝓝 c)) :
    Tendsto (fun n => u n * β (u (n + 1))) atTop (𝓝 c) := by
  have hshift := hprod.comp (tendsto_add_atTop_nat 1)
  have hlim : Tendsto (fun n => (u (n + 1) / u n)⁻¹ *
      (u (n + 1) * β (u (n + 1)))) atTop (𝓝 c) := by
    simpa only [Pi.mul_def, Pi.inv_def, Function.comp_def, inv_one, one_mul] using
      (hratio.inv₀ (by norm_num : (1 : ℝ) ≠ 0)).mul hshift
  apply hlim.congr'
  exact Eventually.of_forall (fun n => by
    field_simp [ne_of_gt (hpos n), ne_of_gt (hpos (n + 1))])

lemma tendsto_budget_mesh_upper (u : ℕ → ℝ) (β : ℝ → ℝ) (c : ℝ)
    (hpos : ∀ n, 0 < u n)
    (hratio : Tendsto (fun n => u (n + 1) / u n) atTop (𝓝 1))
    (hprod : Tendsto (fun n => u n * β (u n)) atTop (𝓝 c)) :
    Tendsto (fun n => u (n + 1) * β (u n)) atTop (𝓝 c) := by
  have hlim : Tendsto (fun n => (u (n + 1) / u n) * (u n * β (u n)))
      atTop (𝓝 c) := by
    simpa only [Pi.mul_def, one_mul] using hratio.mul hprod
  apply hlim.congr'
  exact Eventually.of_forall (fun n => by field_simp [ne_of_gt (hpos n)])

/-- Convergence on a positive asymptotically fine monotone budget mesh determines the full
real-budget limit for any nonnegative antitone profile. -/
theorem tendsto_budget_product_of_mesh (u : ℕ → ℝ) (β : ℝ → ℝ) (c : ℝ)
    (hpos : ∀ n, 0 < u n) (hmono : Monotone u) (hu : Tendsto u atTop atTop)
    (hβmono : AntitoneOn β (Ici 0)) (hβnonneg : ∀ M, 0 ≤ M → 0 ≤ β M)
    (hratio : Tendsto (fun n => u (n + 1) / u n) atTop (𝓝 1))
    (hprod : Tendsto (fun n => u n * β (u n)) atTop (𝓝 c)) :
    Tendsto (fun M : ℝ => M * β M) atTop (𝓝 c) := by
  have hi := budgetMeshIndex_tendsto u hmono hu
  have hlo := (tendsto_budget_mesh_lower u β c hpos hratio hprod).comp hi
  have hup := (tendsto_budget_mesh_upper u β c hpos hratio hprod).comp hi
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' hlo hup
  · filter_upwards [eventually_ge_atTop (u 0)] with M hM
    have hb := budgetMeshIndex_bracket u hu M hM
    have hMnonneg : 0 ≤ M := le_trans (hpos 0).le hM
    have hβle : β (u (budgetMeshIndex u hu M + 1)) ≤ β M :=
      hβmono hMnonneg (hpos _).le hb.2.le
    exact mul_le_mul hb.1 hβle (hβnonneg _ (hpos _).le) hMnonneg
  · filter_upwards [eventually_ge_atTop (u 0)] with M hM
    have hb := budgetMeshIndex_bracket u hu M hM
    have hMnonneg : 0 ≤ M := le_trans (hpos 0).le hM
    have hβle : β M ≤ β (u (budgetMeshIndex u hu M)) :=
      hβmono (hpos _).le hMnonneg hb.1
    exact mul_le_mul hb.2.le hβle (hβnonneg M hMnonneg) (hpos _).le

end KomorebiSpace.DiagonalRegularization
