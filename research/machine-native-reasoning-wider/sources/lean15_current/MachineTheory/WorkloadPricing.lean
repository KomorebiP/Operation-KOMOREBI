import MachineTheory.ResourcePrices
import Mathlib.Tactic.Linarith

/-! # Preparation and repeated workloads

The ledger is a difference of actual nonnegative counters, formed only after
embedding them in the signed real-valued event space. Workload counts are fixed
natural numbers. This account does not silently include memory peaks or wall time.
-/
namespace Komorebi.MachineTheory.ResourcePrices
open scoped BigOperators
noncomputable section
variable {E : Type*} [Fintype E]

/-- Per-use savings may be negative in some coordinates. -/
def net {J : Type*} [Fintype J] (setup : E → ℝ) (uses : J → ℕ)
    (perUse : J → E → ℝ) : E → ℝ :=
  fun i => (∑ j, (uses j : ℝ) * perUse j i) - setup i

/-- Full old and new ledgers, including the incremental preparation charge. -/
structure Ledger (J E : Type*) where
  setup : E → ℕ
  uses : J → ℕ
  old : J → E → ℕ
  revised : J → E → ℕ

def Ledger.oldTotal {J : Type*} [Fintype J] (L : Ledger J E) (i : E) : ℕ :=
  ∑ j, L.uses j * L.old j i

def Ledger.newTotal {J : Type*} [Fintype J] (L : Ledger J E) (i : E) : ℕ :=
  L.setup i + ∑ j, L.uses j * L.revised j i

def Ledger.delta {J : Type*} [Fintype J] (L : Ledger J E) : E → ℝ :=
  net (fun i => L.setup i) L.uses (fun j i => (L.old j i : ℝ) - L.revised j i)

omit [Fintype E] in
/-- The signed net equals old total minus revised total, not natural subtraction. -/
theorem Ledger.delta_eq_total_difference {J : Type*} [Fintype J] (L : Ledger J E) (i : E) :
    L.delta i = (L.oldTotal i : ℝ) - (L.newTotal i : ℝ) := by
  simp only [Ledger.delta,net,Ledger.oldTotal,Ledger.newTotal,Nat.cast_sum,Nat.cast_add,
    Nat.cast_mul,mul_sub,Finset.sum_sub_distrib]
  ring

/-- Valuation commutes with aggregation of the entire declared workload. -/
theorem saving_net {J : Type*} [Fintype J] (setup : E → ℝ) (uses : J → ℕ)
    (perUse : J → E → ℝ) (w : E → ℝ) :
    saving (net setup uses perUse) w =
      (∑ j, (uses j : ℝ) * saving (perUse j) w) - saving setup w := by
  simp only [saving,net,mul_sub,Finset.sum_sub_distrib,Finset.mul_sum]
  rw [Finset.sum_comm]
  congr 1
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro i _
  ring

/-- One actual old/revised ledger supports the price comparison. -/
theorem Ledger.saving_eq_cost_difference {J : Type*} [Fintype J] (L : Ledger J E) (w : E → ℝ) :
    saving L.delta w = saving (fun i => (L.oldTotal i : ℝ)) w -
      saving (fun i => (L.newTotal i : ℝ)) w := by
  have he : L.delta = (fun i => (L.oldTotal i : ℝ)) - (fun i => (L.newTotal i : ℝ)) := by
    funext i
    exact L.delta_eq_total_difference i
  rw [he,saving_event_sub]

/-- Source formula, including setup, with the all-price quantifier unchanged. -/
theorem workload_robust_iff {J : Type*} [Fintype J] (setup : E → ℝ) (uses : J → ℕ)
    (perUse : J → E → ℝ) :
    (∀ w : E → ℝ, (∀ i, 0 ≤ w i) → 0 ≤ saving (net setup uses perUse) w) ↔
      ∀ i, setup i ≤ ∑ j, (uses j : ℝ) * perUse j i := by
  rw [all_nonnegative_prices_iff]
  simp only [net,sub_nonneg]

/-- A change in an event unit must not silently change the associated price. -/
theorem saving_mono (a b w : E → ℝ) (hw : ∀ i, 0 ≤ w i) (hab : ∀ i, a i ≤ b i) :
    saving a w ≤ saving b w :=
  Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hab i) (hw i))

theorem preparation_is_not_free {J : Type*} [Fintype J] (K L : E → ℝ)
    (uses : J → ℕ) (s : J → E → ℝ) (w : E → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hKL : ∀ i, K i ≤ L i) :
    saving (net L uses s) w ≤ saving (net K uses s) w := by
  rw [saving_net,saving_net]
  exact sub_le_sub_left (saving_mono K L w hw hKL) _

/-- Scalar reuse is evaluated only after the event coordinates have been priced. -/
def repeated (setup perUse : E → ℝ) (N : ℕ) : E → ℝ :=
  fun i => (N : ℝ) * perUse i - setup i

theorem saving_repeated (setup perUse w : E → ℝ) (N : ℕ) :
    saving (repeated setup perUse N) w = (N : ℝ) * saving perUse w - saving setup w := by
  change saving ((N : ℝ) • perUse - setup) w = _
  rw [saving_event_sub,saving_event_smul]

/-- Strict break-even boundary for a fixed workload and fixed additive prices. -/
theorem amortization_iff (setup perUse w : E → ℝ) (N : ℕ)
    (hd : 0 < saving perUse w) :
    0 < saving (repeated setup perUse N) w ↔ saving setup w / saving perUse w < (N : ℝ) := by
  rw [saving_repeated,sub_pos,div_lt_iff₀ hd]

/-- Repetition cannot repay nonnegative setup when per-use savings are nonpositive. -/
theorem no_amortization_of_nonpositive (setup perUse w : E → ℝ) (N : ℕ)
    (hK : 0 ≤ saving setup w) (hd : saving perUse w ≤ 0) :
    saving (repeated setup perUse N) w ≤ 0 := by
  rw [saving_repeated]
  have hm := mul_nonpos_of_nonneg_of_nonpos (Nat.cast_nonneg N : (0 : ℝ) ≤ N) hd
  linarith

/-- An interval guarantee on the already priced per-use and setup accounts composes. -/
theorem robust_repeated_lower (setup perUse w : E → ℝ) (N : ℕ) (d K : ℝ)
    (hd : d ≤ saving perUse w) (hK : saving setup w ≤ K) :
    (N : ℝ) * d - K ≤ saving (repeated setup perUse N) w := by
  rw [saving_repeated]
  exact sub_le_sub (mul_le_mul_of_nonneg_left hd (Nat.cast_nonneg N)) hK

/-- Applying the finite-price theorem to the net ledger includes preparation automatically. -/
theorem workload_minimum {J : Type*} [Fintype J]
    (setup : E → ℝ) (uses : J → ℕ) (perUse : J → E → ℝ)
    (W : Finset (E → ℝ)) (hne : W.Nonempty) :
    ∃ w ∈ W, IsLeast ((saving (net setup uses perUse)) '' convexHull ℝ (W : Set (E → ℝ)))
      (saving (net setup uses perUse) w) := by
  obtain ⟨w,hw,he,hmin⟩ := finite_price_minimum (net setup uses perUse) W hne
  exact ⟨w,hw,he.symm ▸ hmin⟩

end
end Komorebi.MachineTheory.ResourcePrices
