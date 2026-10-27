import AVOC.BayesianGuardedBridge
import AVOC.ResearchPolicy

namespace Komorebi.AVOC.Research

variable {Ω P C M : Type*} [Fintype Ω] [Fintype P] [Fintype C]
    [PartialOrder P] [DecidableEq P] {claim : P → Prop}

/-- End-to-end use of primitive Bayesian/model errors inside the actual
certificate-gated research protocol. The sound admission invariant is separate
from performance accuracy. Exact metadata and action guards must be preserved. -/
theorem certified_bayesian_model_policy
    (p : Protocol Ω P C claim)
    (model : Guarded.System (RationalBelief Ω × M) (Action P) (Option C))
    (phi : State Ω P → RationalBelief Ω × M)
    (W : ℕ → (RationalBelief Ω × M) → ℚ)
    (eps alpha beta : ℚ) (L R chi residual : ℕ → ℚ)
    (hc : Guarded.BayesianModelCertificate (controller p) model phi
      (fun s => s.belief) W eps alpha beta L R chi residual)
    (estimate : ℕ → State Ω P → Action P → ℚ)
    (choose : ℕ → State Ω P → Action P) (codeError tau : ℕ → ℚ)
    (ha : ∀ k s, Allowed p s (choose k s))
    (he : ∀ k s a, Allowed p s a →
      |Guarded.tableQ model (W k) (phi s) a - estimate k s a| ≤ codeError k)
    (hm : ∀ k s a, Allowed p s a → estimate k s a ≤ estimate k s (choose k s) + tau k)
    (B n : ℕ) (s : State Ω P) (hs : BudgetSafe claim B s) :
    Guarded.TreeSafe (controller p) (BudgetSafe claim B) s
      (Guarded.policyPlan (controller p) choose n s) ∧
    0 ≤ Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ∧
    Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ≤
      Guarded.regretBudget (fun k => 2 *
        (Guarded.modelQBudget eps (Guarded.bayesianTransportBudget alpha beta L R chi) residual k +
         codeError k) + tau k) n := by
  have hf : ∀ k s, choose k s ∈ (controller p).actions s :=
    fun k s => (mem_actions p s _).2 (ha k s)
  refine ⟨Guarded.admissible_approximate_policy_safe (controller p) (BudgetSafe claim B)
    (controller_budget_preserves p B) choose hf n s hs, ?_⟩
  exact Guarded.model_decoded_policy_regret (controller p) model phi W eps _ residual
    hc.toModelCertificate estimate choose codeError tau hf
    (fun k s a h => he k s a ((mem_actions p s a).1 h))
    (fun k s a h => hm k s a ((mem_actions p s a).1 h)) n s

end Komorebi.AVOC.Research
