import AVOC.HorizonBehavior
import AVOC.Context

namespace Komorebi.AVOC

universe u v w z

/-- Candidate encodings sufficient for a declared finite control horizon. -/
noncomputable def horizonSufficientContexts
    {R : Type z} [DecidableEq R]
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ) : Finset R := by
  classical
  exact designs.filter (fun r => HorizonControlSufficient sys (family.encode r) n)

/-- Membership in the horizon-sufficient candidate pool. -/
theorem mem_horizonSufficientContexts_iff
    {R : Type z} [DecidableEq R]
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ) (r : R) :
    r ∈ horizonSufficientContexts family designs sys n ↔
      r ∈ designs ∧ HorizonControlSufficient sys (family.encode r) n := by
  classical
  simp [horizonSufficientContexts]

/-- Increasing the planning horizon can only remove candidate encodings from
the exact sufficient-context pool. -/
theorem horizonSufficientContexts_antitone
    {R : Type z} [DecidableEq R]
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ) :
    horizonSufficientContexts family designs sys (n + 1) ⊆
      horizonSufficientContexts family designs sys n := by
  classical
  intro r hr
  rw [mem_horizonSufficientContexts_iff] at hr ⊢
  exact ⟨hr.1, horizonControlSufficient_of_succ sys n hr.2⟩

/-- A design is minimum-cost horizon sufficient inside the declared finite
candidate family. -/
def MinimumCostHorizonContext
    {R : Type z} {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ) (chosen : R) : Prop :=
  chosen ∈ designs ∧
  HorizonControlSufficient sys (family.encode chosen) n ∧
  ∀ r ∈ designs,
    HorizonControlSufficient sys (family.encode r) n →
    family.cost chosen ≤ family.cost r

/-- A nonempty finite family of horizon-sufficient candidates has a
minimum-cost member. -/
theorem minimumCostHorizonContext_exists
    {R : Type z} [DecidableEq R]
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ)
    (hne : (horizonSufficientContexts family designs sys n).Nonempty) :
    ∃ chosen, MinimumCostHorizonContext family designs sys n chosen := by
  classical
  let feasible := horizonSufficientContexts family designs sys n
  let costs := feasible.image family.cost
  have hcosts : costs.Nonempty := hne.image family.cost
  let cmin := costs.min' hcosts
  have hcminmem : cmin ∈ costs := costs.min'_mem hcosts
  rcases Finset.mem_image.mp hcminmem with ⟨chosen, hchosenFeas, hcostEq⟩
  have hchosen :=
    (mem_horizonSufficientContexts_iff family designs sys n chosen).1 hchosenFeas
  refine ⟨chosen, hchosen.1, hchosen.2, ?_⟩
  intro r hr hsr
  have hrFeas : r ∈ feasible := by
    exact (mem_horizonSufficientContexts_iff family designs sys n r).2 ⟨hr, hsr⟩
  have hrcost : family.cost r ∈ costs := Finset.mem_image.mpr ⟨r, hrFeas, rfl⟩
  have hmin : cmin ≤ family.cost r := costs.min'_le (family.cost r) hrcost
  simpa [cmin, hcostEq] using hmin

/-- Minimum exact context cost is monotone in planning horizon: a minimum-cost
`n`-step sufficient context costs no more than a minimum-cost `(n+1)`-step
sufficient context drawn from the same candidate family. -/
theorem minimum_horizon_context_cost_monotone
    {R : Type z} {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (family : ContextFamily R S Z) (designs : Finset R)
    (sys : StateControlSystem S A) (n : ℕ)
    {shortChoice longChoice : R}
    (hshort : MinimumCostHorizonContext family designs sys n shortChoice)
    (hlong : MinimumCostHorizonContext family designs sys (n + 1) longChoice) :
    family.cost shortChoice ≤ family.cost longChoice := by
  apply hshort.2.2 longChoice hlong.1
  exact horizonControlSufficient_of_succ sys n hlong.2.1

end Komorebi.AVOC
