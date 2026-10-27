import AVOC.Core
import Mathlib.Data.Finset.Max

namespace Komorebi.AVOC

universe u v w z

/-- Sufficiency for a finite active query set. -/
def SufficientForQueries
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    (φ : X → Z) (tasks : Q → X → Y) (queries : Finset Q) : Prop :=
  ∀ q ∈ queries, TaskSufficient φ (tasks q)

/-- Removing active queries cannot invalidate a context that was sufficient for
the larger query family. -/
theorem sufficientForQueries_antitone
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y} {small large : Finset Q}
    (hsub : small ⊆ large)
    (h : SufficientForQueries φ tasks large) :
    SufficientForQueries φ tasks small := by
  intro q hq
  exact h q (hsub hq)

/-- Adding a query makes the sufficiency requirement exactly the conjunction of
old sufficiency and sufficiency for the added target. -/
theorem sufficientForQueries_insert_iff
    {Q : Type z} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y} {queries : Finset Q} {q : Q} :
    SufficientForQueries φ tasks (insert q queries) ↔
      TaskSufficient φ (tasks q) ∧ SufficientForQueries φ tasks queries := by
  simp [SufficientForQueries]

/-- Candidate context encodings indexed by a finite design type. -/
structure ContextFamily (R : Type z) (X : Type u) (Z : Type v) where
  encode : R → X → Z
  cost : R → ℕ

/-- The candidate contexts in `designs` that are sufficient for the currently
active finite query family. This is noncomputable because exact sufficiency is a
logical property rather than an assumed executable decision procedure. -/
noncomputable def sufficientContexts
    {R : Type z} [DecidableEq R]
    {Q : Type*} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y) (queries : Finset Q) : Finset R := by
  classical
  exact designs.filter (fun r => SufficientForQueries (family.encode r) tasks queries)

/-- Membership in the filtered context family exposes both admissibility and
query sufficiency. -/
theorem mem_sufficientContexts_iff
    {R : Type z} [DecidableEq R]
    {Q : Type*} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y) (queries : Finset Q) (r : R) :
    r ∈ sufficientContexts family designs tasks queries ↔
      r ∈ designs ∧ SufficientForQueries (family.encode r) tasks queries := by
  classical
  simp [sufficientContexts]

/-- Every nonempty finite family of sufficient candidate contexts contains a
minimum-cost sufficient context. -/
theorem finite_minimum_cost_sufficient_context_exists
    {R : Type z} [DecidableEq R]
    {Q : Type*} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y) (queries : Finset Q)
    (hne : (sufficientContexts family designs tasks queries).Nonempty) :
    ∃ chosen,
      chosen ∈ designs ∧
      SufficientForQueries (family.encode chosen) tasks queries ∧
      ∀ r ∈ designs,
        SufficientForQueries (family.encode r) tasks queries →
        family.cost chosen ≤ family.cost r := by
  classical
  let feasible := sufficientContexts family designs tasks queries
  let costs := feasible.image family.cost
  have hcosts : costs.Nonempty := hne.image family.cost
  let cmin := costs.min' hcosts
  have hcminmem : cmin ∈ costs := costs.min'_mem hcosts
  rcases Finset.mem_image.mp hcminmem with ⟨chosen, hchosenFeas, hcostEq⟩
  have hchosen := (mem_sufficientContexts_iff family designs tasks queries chosen).1 hchosenFeas
  refine ⟨chosen, hchosen.1, hchosen.2, ?_⟩
  intro r hr hsr
  have hrFeas : r ∈ feasible := by
    exact (mem_sufficientContexts_iff family designs tasks queries r).2 ⟨hr, hsr⟩
  have hrcost : family.cost r ∈ costs := Finset.mem_image.mpr ⟨r, hrFeas, rfl⟩
  have hmin : cmin ≤ family.cost r := costs.min'_le (family.cost r) hrcost
  simpa [cmin, hcostEq] using hmin

/-- Expanding the active query set can only remove designs from the sufficient
context pool. -/
theorem sufficientContexts_antitone_queries
    {R : Type z} [DecidableEq R]
    {Q : Type*} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y)
    {small large : Finset Q} (hsub : small ⊆ large) :
    sufficientContexts family designs tasks large ⊆
      sufficientContexts family designs tasks small := by
  classical
  intro r hr
  rw [mem_sufficientContexts_iff] at hr ⊢
  exact ⟨hr.1, sufficientForQueries_antitone hsub hr.2⟩

/-- A chosen design is minimum-cost sufficient for the declared active queries
inside a finite candidate family. -/
def MinimumCostSufficientContext
    {R : Type z} {Q : Type*} {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y) (queries : Finset Q)
    (chosen : R) : Prop :=
  chosen ∈ designs ∧
  SufficientForQueries (family.encode chosen) tasks queries ∧
  ∀ r ∈ designs,
    SufficientForQueries (family.encode r) tasks queries →
    family.cost chosen ≤ family.cost r

/-- The existence theorem packaged in the `MinimumCostSufficientContext`
predicate. -/
theorem minimumCostSufficientContext_exists
    {R : Type z} [DecidableEq R]
    {Q : Type*} [DecidableEq Q]
    {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y) (queries : Finset Q)
    (hne : (sufficientContexts family designs tasks queries).Nonempty) :
    ∃ chosen, MinimumCostSufficientContext family designs tasks queries chosen := by
  simpa [MinimumCostSufficientContext] using
    finite_minimum_cost_sufficient_context_exists family designs tasks queries hne

/-- Query-family monotonicity of optimal context cost: if `small ⊆ large`, then
any minimum-cost context for `small` costs no more than any minimum-cost context
for `large`. -/
theorem minimum_context_cost_monotone_queries
    {R : Type z} {Q : Type*} {X : Type u} {Z : Type v} {Y : Type w}
    (family : ContextFamily R X Z)
    (designs : Finset R) (tasks : Q → X → Y)
    {small large : Finset Q} {smallChoice largeChoice : R}
    (hsub : small ⊆ large)
    (hsmall : MinimumCostSufficientContext family designs tasks small smallChoice)
    (hlarge : MinimumCostSufficientContext family designs tasks large largeChoice) :
    family.cost smallChoice ≤ family.cost largeChoice := by
  apply hsmall.2.2 largeChoice hlarge.1
  exact sufficientForQueries_antitone hsub hlarge.2.1

end Komorebi.AVOC
