import MachineTheory.ResourcePrices
import MachineTheory.WorkloadPricing
import MachineTheory.PriceExamples
import MachineTheory.PriceRevision

/-! Independently restated source-facing obligations. The functions below are the
actual event valuation, Mathlib convex hull, inherited finite minimum and replay. -/
open scoped BigOperators
open Komorebi.MachineTheory

example {E : Type*} [Fintype E] (delta : E → ℝ) :
    (∀ w : E → ℝ, (∀ i, 0 ≤ w i) → 0 ≤ ∑ i, w i * delta i) ↔
      ∀ i, 0 ≤ delta i := ResourcePrices.all_nonnegative_prices_iff delta

example {E : Type*} [Fintype E] (delta : E → ℝ)
    (W : Finset (E → ℝ)) (hne : W.Nonempty) :
    ∃ w ∈ W, ResourcePrices.saving delta w = Planning.finiteMin W hne (ResourcePrices.saving delta) ∧
      IsLeast ((ResourcePrices.saving delta) '' convexHull ℝ (W : Set (E → ℝ)))
        (Planning.finiteMin W hne (ResourcePrices.saving delta)) :=
  ResourcePrices.finite_price_minimum delta W hne

example {E J : Type*} [Fintype E] [Fintype J] (K : E → ℝ) (n : J → ℕ)
    (s : J → E → ℝ) (w : E → ℝ) :
    (∑ i, w i * ((∑ j, (n j : ℝ) * s j i)-K i)) =
      (∑ j, (n j : ℝ) * (∑ i, w i * s j i)) - ∑ i, w i * K i :=
  ResourcePrices.saving_net K n s w

example {E J : Type*} [Fintype E] [Fintype J] (L : ResourcePrices.Ledger J E) (w : E → ℝ) :
    ResourcePrices.saving L.delta w = ResourcePrices.saving (fun i => (L.oldTotal i : ℝ)) w -
      ResourcePrices.saving (fun i => (L.newTotal i : ℝ)) w := L.saving_eq_cost_difference w

example (N : ℕ) :
    (∀ w ∈ convexHull ℝ (PriceExamples.expensivePrices : Set (Bool → ℝ)),
      0 < ResourcePrices.saving (PriceExamples.paid N) w) ↔ 100 < N :=
  PriceExamples.robust_reuse_threshold N

example : PriceRevision.system.Established PriceRevision.correctedQuote 1 true ∧
    ¬ PriceRevision.system.claim PriceRevision.correctedQuote 2 :=
  ⟨PriceRevision.restored_calculation,PriceRevision.benefit_now_false⟩

example {E : Type*} [Fintype E] (delta w u : E → ℝ) (hu : ∀ i,u i ≠ 0) :
    ResourcePrices.saving (fun i => u i * delta i) (fun i => w i / u i)=
      ResourcePrices.saving delta w := ResourcePrices.consistent_unit_change delta w u hu
