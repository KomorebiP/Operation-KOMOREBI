import AVOC.RetryBayesian

namespace Komorebi.AVOC.Retry

structure Evaluation where
  netValue : ℚ
  retry : Bool
  visits : Nat
  deriving Repr, DecidableEq

/-- Only an unresolved branch continues. The recursion has linear node count.
The meter excludes arithmetic bit complexity, model calls and I/O. -/
def evaluate {S : Type*} (m : Model S) : Nat → S → Evaluation
  | 0, _ => ⟨0,false,1⟩
  | n + 1, s => if m.enabled s then
      let tail := evaluate m n (m.afterFault s)
      let trial := immediate m s + (1 - m.resolve s) * tail.netValue
      ⟨max 0 trial,decide (0 < trial),tail.visits + 1⟩
    else ⟨0,false,1⟩

theorem evaluate_value {S : Type*} (m : Model S) (n : Nat) (s : S) :
    (evaluate m n s).netValue = retryValue m n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    by_cases he : m.enabled s = true
    · simp [evaluate,retryValue,he,ih]
    · have hf := Bool.eq_false_iff.mpr he
      simp [evaluate,retryValue,hf]

theorem evaluate_choice {S : Type*} (m : Model S) (n : Nat) (s : S) :
    (evaluate m n s).retry = choose m n s := by
  cases n with
  | zero => rfl
  | succ n =>
    by_cases he : m.enabled s = true
    · simp only [evaluate,choose,he,↓reduceIte,Bool.true_and]
      apply Bool.eq_iff_iff.mpr
      simp only [decide_eq_true_eq]
      rw [evaluate_value]
      rfl
    · have hf := Bool.eq_false_iff.mpr he
      simp [evaluate,choose,hf]

theorem evaluate_work_bound {S : Type*} (m : Model S) (n : Nat) (s : S) :
    (evaluate m n s).visits ≤ n + 1 := by
  induction n generalizing s with
  | zero => exact le_rfl
  | succ n ih =>
    by_cases he : m.enabled s = true
    · have h := ih (m.afterFault s)
      simp only [evaluate,he,↓reduceIte]
      omega
    · have hf := Bool.eq_false_iff.mpr he
      simp [evaluate,hf]

theorem evaluate_guarded_exact {S : Type*} (m : Model S) (n : Nat) (s : S) :
    (evaluate m n s).netValue = Guarded.value (system m) n (some s) := by
  rw [evaluate_value,guarded_value_eq]

/-- Recommendation alone in the persistent-reliability model needs only the
current posterior mean; it does not run the lookahead evaluator. -/
theorem evaluate_choice_is_threshold {Ω : Type*} [Fintype Ω]
    (q : RetryBayesian.Reliability Ω) (n : Nat) (s : RetryBayesian.State Ω) :
    (evaluate (RetryBayesian.model q) (n + 1) s).retry = RetryBayesian.recommend q s := by
  rw [evaluate_choice,RetryBayesian.exact_retry_threshold]
  rfl

end Komorebi.AVOC.Retry
