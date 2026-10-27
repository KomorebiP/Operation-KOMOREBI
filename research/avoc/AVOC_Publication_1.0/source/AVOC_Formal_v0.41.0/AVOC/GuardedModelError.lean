import AVOC.GuardedPolicyRegret
import Mathlib.Algebra.Order.Ring.Abs

namespace Komorebi.AVOC.Guarded

variable {S Z A O : Type*} [DecidableEq A] [Fintype O]

/-- One model backup evaluated on a supplied continuation table, which need not
be the model's optimal value. This exposes approximation/computation residuals. -/
def tableQ (model : System Z A O) (W : Z → ℚ) (z : Z) (a : A) : ℚ :=
  model.reward z a + expectation model W z a

noncomputable def backup (model : System Z A O) (W : Z → ℚ) (z : Z) : ℚ :=
  ((model.actions z).image (tableQ model W z)).max' ((model.actions_nonempty z).image _)

theorem tableQ_le_backup (model : System Z A O) (W : Z → ℚ) (z : Z) (a : A)
    (ha : a ∈ model.actions z) : tableQ model W z a ≤ backup model W z := by
  exact Finset.le_max' _ _ (Finset.mem_image.mpr ⟨a, ha, rfl⟩)

theorem backup_attained (model : System Z A O) (W : Z → ℚ) (z : Z) :
    ∃ a ∈ model.actions z, backup model W z = tableQ model W z a := by
  obtain ⟨a, ha, hm⟩ := Finset.exists_max_image
    (model.actions z) (tableQ model W z) (model.actions_nonempty z)
  refine ⟨a, ha, le_antisymm ?_ (tableQ_le_backup model W z a ha)⟩
  apply Finset.max'_le
  intro y hy
  obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp hy
  exact hm b hb

theorem backup_optimal_value (sys : System S A O) (n : ℕ) (s : S) :
    backup sys (value sys n) s = value sys (n + 1) s := rfl

/-- A uniform state-value error stays bounded after normalized expectation. -/
theorem expectation_uniform_error (sys : System S A O) (V W : S → ℚ) (D : ℚ)
    (h : ∀ s, |V s - W s| ≤ D) (s : S) (a : A) :
    |expectation sys V s a - expectation sys W s a| ≤ D := by
  calc
    _ = |∑ o, sys.prob s a o * (V (sys.step s a o) - W (sys.step s a o))| := by
      simp only [expectation, mul_sub, Finset.sum_sub_distrib]
    _ ≤ ∑ o, |sys.prob s a o * (V (sys.step s a o) - W (sys.step s a o))| :=
      Finset.abs_sum_le_sum_abs _ _
    _ = ∑ o, sys.prob s a o * |V (sys.step s a o) - W (sys.step s a o)| := by
      apply Finset.sum_congr rfl
      intro o _
      rw [abs_mul, abs_of_nonneg (sys.prob_nonneg s a o)]
    _ ≤ ∑ o, sys.prob s a o * D :=
      Finset.sum_le_sum (fun o _ => mul_le_mul_of_nonneg_left (h _) (sys.prob_nonneg s a o))
    _ = D := by rw [← Finset.sum_mul, sys.prob_sum_one, one_mul]

/-- The maxima comparison explicitly requires the same admissible actions. -/
theorem value_backup_error_of_q_error (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (n : ℕ) (W : Z → ℚ) (D : ℚ) (s : S)
    (hA : raw.actions s = model.actions (phi s))
    (hQ : ∀ a ∈ raw.actions s,
      |qValue raw n s a - tableQ model W (phi s) a| ≤ D) :
    |value raw (n + 1) s - backup model W (phi s)| ≤ D := by
  let ar := optimalAction raw n s
  have hr : ar ∈ raw.actions s := optimalAction_mem raw n s
  have hre : value raw (n + 1) s = qValue raw n s ar := optimalAction_realizes raw n s
  have hrm : ar ∈ model.actions (phi s) := hA ▸ hr
  have hru := tableQ_le_backup model W (phi s) ar hrm
  have hreerr := (abs_le.mp (hQ ar hr)).2
  obtain ⟨am, ham, hame⟩ := backup_attained model W (phi s)
  have hamr : am ∈ raw.actions s := hA.symm ▸ ham
  have hml := q_le_value raw n s am hamr
  have hmeerr := (abs_le.mp (hQ am hamr)).1
  apply abs_le.mpr
  constructor <;> linarith

/-- Cumulative model/reward/Bellman-residual error at a value horizon. -/
def modelValueBudget (eps : ℚ) (transport residual : ℕ → ℚ) (n : ℕ) : ℚ :=
  ∑ k ∈ Finset.range n, (eps + transport k + residual k)

def modelQBudget (eps : ℚ) (transport residual : ℕ → ℚ) (n : ℕ) : ℚ :=
  modelValueBudget eps transport residual n + eps + transport n

@[simp] theorem modelValueBudget_zero (eps : ℚ) (transport residual : ℕ → ℚ) :
    modelValueBudget eps transport residual 0 = 0 := by simp [modelValueBudget]

theorem modelValueBudget_succ (eps : ℚ) (transport residual : ℕ → ℚ) (n : ℕ) :
    modelValueBudget eps transport residual (n + 1) =
      modelQBudget eps transport residual n + residual n := by
  simp [modelValueBudget, modelQBudget, Finset.sum_range_succ, add_assoc]

/-- A posteriori model certificate. No true Bellman-Q error is assumed here.
The transport premise is derived from Bayesian primitive bounds in the adapter.
The residual measures how accurately the supplied tables solve model backups. -/
structure ModelCertificate (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (W : ℕ → Z → ℚ) (eps : ℚ) (transport residual : ℕ → ℚ) : Prop where
  actions_eq : ∀ s, raw.actions s = model.actions (phi s)
  initial : ∀ s, W 0 (phi s) = 0
  reward_error : ∀ s a, a ∈ raw.actions s → |raw.reward s a - model.reward (phi s) a| ≤ eps
  transport_error : ∀ n s a, a ∈ raw.actions s →
    |expectation raw (fun t => W n (phi t)) s a - expectation model (W n) (phi s) a| ≤ transport n
  residual_error : ∀ n s, |backup model (W n) (phi s) - W (n + 1) (phi s)| ≤ residual n

/-- One-step Q error from the previous value error and a continuation comparison. -/
theorem model_q_error_step (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (W : ℕ → Z → ℚ) (eps : ℚ) (transport residual : ℕ → ℚ)
    (hc : ModelCertificate raw model phi W eps transport residual)
    (n : ℕ) (D : ℚ)
    (hprev : ∀ s, |value raw n s - W n (phi s)| ≤ D)
    (s : S) (a : A) (ha : a ∈ raw.actions s) :
    |qValue raw n s a - tableQ model (W n) (phi s) a| ≤ D + eps + transport n := by
  have hp := expectation_uniform_error raw (value raw n) (fun t => W n (phi t)) D hprev s a
  have ht := hc.transport_error n s a ha
  have hr := hc.reward_error s a ha
  have he : |expectation raw (value raw n) s a - expectation model (W n) (phi s) a| ≤
      D + transport n := by
    have hh := abs_sub_le (expectation raw (value raw n) s a)
      (expectation raw (fun t => W n (phi t)) s a) (expectation model (W n) (phi s) a)
    linarith
  calc
    _ = |(raw.reward s a - model.reward (phi s) a) +
        (expectation raw (value raw n) s a - expectation model (W n) (phi s) a)| := by
      unfold qValue tableQ; congr 1; ring
    _ ≤ |raw.reward s a - model.reward (phi s) a| +
        |expectation raw (value raw n) s a - expectation model (W n) (phi s) a| := abs_add_le _ _
    _ ≤ D + eps + transport n := by linarith

/-- From model-level primitive errors and computable-table residuals to true
constrained value error. State spaces may be infinite; branching is finite. -/
theorem model_value_error (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (W : ℕ → Z → ℚ) (eps : ℚ) (transport residual : ℕ → ℚ)
    (hc : ModelCertificate raw model phi W eps transport residual) (n : ℕ) (s : S) :
    |value raw n s - W n (phi s)| ≤ modelValueBudget eps transport residual n := by
  induction n generalizing s with
  | zero => simp [hc.initial]
  | succ n ih =>
    have hq := model_q_error_step raw model phi W eps transport residual hc n
      (modelValueBudget eps transport residual n) ih
    have hv := value_backup_error_of_q_error raw model phi n (W n)
      (modelQBudget eps transport residual n) s (hc.actions_eq s) (hq s)
    have hr := hc.residual_error n s
    have ht := abs_sub_le (value raw (n + 1) s) (backup model (W n) (phi s)) (W (n + 1) (phi s))
    rw [modelValueBudget_succ]
    linarith

theorem model_q_error (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (W : ℕ → Z → ℚ) (eps : ℚ) (transport residual : ℕ → ℚ)
    (hc : ModelCertificate raw model phi W eps transport residual)
    (n : ℕ) (s : S) (a : A) (ha : a ∈ raw.actions s) :
    |qValue raw n s a - tableQ model (W n) (phi s) a| ≤ modelQBudget eps transport residual n :=
  model_q_error_step raw model phi W eps transport residual hc n _
    (model_value_error raw model phi W eps transport residual hc n) s a ha

/-- Complete-policy consequence. `codeError` also accounts for numerical or
compressed Q-table reconstruction beyond the model backup itself. -/
theorem model_decoded_policy_regret (raw : System S A O) (model : System Z A O)
    (phi : S → Z) (W : ℕ → Z → ℚ) (eps : ℚ) (transport residual : ℕ → ℚ)
    (hc : ModelCertificate raw model phi W eps transport residual)
    (estimate : ℕ → S → A → ℚ) (choose : ℕ → S → A)
    (codeError tau : ℕ → ℚ)
    (ha : ∀ n s, choose n s ∈ raw.actions s)
    (he : ∀ n s a, a ∈ raw.actions s →
      |tableQ model (W n) (phi s) a - estimate n s a| ≤ codeError n)
    (hm : ∀ n s a, a ∈ raw.actions s → estimate n s a ≤ estimate n s (choose n s) + tau n)
    (n : ℕ) (s : S) :
    0 ≤ value raw n s - planValue raw s (policyPlan raw choose n s) ∧
    value raw n s - planValue raw s (policyPlan raw choose n s) ≤
      regretBudget (fun k => 2 * (modelQBudget eps transport residual k + codeError k) + tau k) n := by
  apply decoded_policy_regret raw choose estimate _ tau ha _ hm n s
  intro k t a hat
  have hx := model_q_error raw model phi W eps transport residual hc k t a hat
  have hy := he k t a hat
  exact (abs_sub_le _ _ _).trans (add_le_add hx hy)

end Komorebi.AVOC.Guarded
