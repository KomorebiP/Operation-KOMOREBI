module

public import Mathlib.Data.Nat.Log
public import Mathlib.Tactic

/-!
Arithmetic thresholds used to reduce dyadic Newton coefficient estimates to a
finite prefix. All tail bounds follow by induction, not by bounded evaluation.
-/

@[expose] public section

namespace KomorebiPaperIX.DyadicLogThresholds

theorem log_two_succ_le (n : ℕ) (hn : 1 ≤ n) :
    Nat.log 2 (n + 1) ≤ Nat.log 2 n + 1 := by
  calc
    Nat.log 2 (n + 1) ≤ Nat.log 2 (n * 2) :=
      Nat.log_mono_right (by omega)
    _ = Nat.log 2 n + 1 := Nat.log_mul_base (by omega) (by omega)

/-- Once an offset-log bound holds at a positive index, it holds thereafter. -/
theorem offset_log_bound_of_le (a c n : ℕ) (ha : 1 ≤ a)
    (hbase : c + Nat.log 2 a ≤ a) (han : a ≤ n) :
    c + Nat.log 2 n ≤ n := by
  induction n, han using Nat.le_induction with
  | base => exact hbase
  | succ n hn ih =>
      have hstep := log_two_succ_le n (by omega)
      omega

theorem two_add_log_le (k : ℕ) (hk : 3 ≤ k) :
    2 + Nat.log 2 k ≤ k := by
  apply offset_log_bound_of_le 3 2 k (by omega) _ hk
  decide

theorem three_add_log_le (k : ℕ) (hk : 5 ≤ k) :
    3 + Nat.log 2 k ≤ k := by
  apply offset_log_bound_of_le 5 3 k (by omega) _ hk
  decide

theorem five_add_log_le (k : ℕ) (hk : 7 ≤ k) :
    5 + Nat.log 2 k ≤ k := by
  apply offset_log_bound_of_le 7 5 k (by omega) _ hk
  decide

end KomorebiPaperIX.DyadicLogThresholds
