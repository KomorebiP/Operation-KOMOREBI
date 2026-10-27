import KomorebiLSM.Transfer
import KomorebiLSM.LinearClosure
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Tactic.Abel

/-! Exact recurrence-elimination component of P10.
The geometric tail is proved in MemoryBounds. Recursive rollout error is not claimed here.
-/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM
universe u v w
variable {R : Type u} [Ring R]
variable {X : Type v} [AddCommGroup X] [Module R X]
variable {Y : Type w} [AddCommGroup Y] [Module R Y]

/-- Unresolved-state elimination, with the original history index. -/
theorem unresolved_solution (C : X →ₗ[R] Y) (D : Y →ₗ[R] Y)
    (z : ℕ → X) (q : ℕ → Y)
    (step : ∀ t, q (t+1) = C (z t) + D (q t)) (t : ℕ) :
    q t = (D^t) (q 0) + ∑ s ∈ Finset.range t, (D^(t-1-s)) (C (z s)) := by
  induction t with
  | zero => simp
  | succ t ih =>
    rw [step, ih, map_add, map_sum, Finset.sum_range_succ]
    have hexp : ∀ s ∈ Finset.range t,
        D ((D^(t-1-s)) (C (z s))) = (D^(t+1-1-s)) (C (z s)) := by
      intro s hs
      have hs' := Finset.mem_range.mp hs
      have hn : t+1-1-s = (t-1-s)+1 := by omega
      rw [hn, pow_succ']
      rfl
    have hsum := Finset.sum_congr rfl hexp
    rw [hsum]
    have hpower : D ((D^t) (q 0)) = (D^(t+1)) (q 0) := by
      rw [pow_succ']; rfl
    rw [hpower]
    simp only [Nat.add_sub_cancel, Nat.sub_self, pow_zero, Module.End.one_apply]
    abel

/-- The exact projected history recurrence, without a decay hypothesis. -/
theorem exact_memory_history (A : X →ₗ[R] X) (B : Y →ₗ[R] X)
    (C : X →ₗ[R] Y) (D : Y →ₗ[R] Y) (z : ℕ → X) (q : ℕ → Y)
    (zstep : ∀ t, z (t+1) = A (z t) + B (q t))
    (qstep : ∀ t, q (t+1) = C (z t) + D (q t)) (t : ℕ) :
    z (t+1) = A (z t) +
      (∑ s ∈ Finset.range t, B ((D^(t-1-s)) (C (z s)))) + B ((D^t) (q 0)) := by
  rw [zstep, unresolved_solution C D z q qstep, map_add, map_sum]
  abel

/-- The lag-index form printed in P10, including the unresolved initial state. -/
theorem exact_memory_lags (A : X →ₗ[R] X) (B : Y →ₗ[R] X)
    (C : X →ₗ[R] Y) (D : Y →ₗ[R] Y) (z : ℕ → X) (q : ℕ → Y)
    (zstep : ∀ t, z (t+1) = A (z t) + B (q t))
    (qstep : ∀ t, q (t+1) = C (z t) + D (q t)) (t : ℕ) :
    z (t+1) = A (z t) +
      (∑ k ∈ Finset.range t, B ((D^k) (C (z (t-1-k))))) + B ((D^t) (q 0)) := by
  rw [exact_memory_history A B C D z q zstep qstep]
  congr 2
  have href := Finset.sum_range_reflect
    (fun s => B ((D^(t-1-s)) (C (z s)))) t
  calc
    (∑ s ∈ Finset.range t, B ((D^(t-1-s)) (C (z s)))) =
        ∑ k ∈ Finset.range t, B ((D^(t-1-(t-1-k))) (C (z (t-1-k)))) := href.symm
    _ = _ := by
      apply Finset.sum_congr rfl
      intro k hk
      have hkt := Finset.mem_range.mp hk
      have hn : t-1-(t-1-k) = k := by omega
      rw [hn]

/-- Actual projector blocks give the two coupled recurrences needed above. -/
theorem projected_recurrences (P L : X →ₗ[R] X)
    (idem : ∀ x, P (P x) = P x) (x : ℕ → X)
    (step : ∀ t, x (t+1) = L (x t)) (t : ℕ) :
    (P (x (t+1)) = P (L (P (x t))) +
      P (L (unresolved P (unresolved P (x t))))) ∧
    (unresolved P (x (t+1)) = unresolved P (L (P (P (x t)))) +
      unresolved P (L (unresolved P (x t)))) := by
  rw [step, unresolved_idempotent P idem, idem]
  constructor
  · simpa only [closureDefect, LinearMap.comp_apply] using retained_dynamics_split P L (x t)
  · simp only [unresolved_apply, map_sub]
    abel

/-- P10 specialized to the actual blocks of a single projected transition. -/
theorem projected_memory (P L : X →ₗ[R] X)
    (idem : ∀ x, P (P x) = P x) (x : ℕ → X)
    (step : ∀ t, x (t+1) = L (x t)) (t : ℕ) :
    let Q := unresolved P
    let A := P.comp (L.comp P)
    let B := P.comp (L.comp Q)
    let C := Q.comp (L.comp P)
    let D := Q.comp (L.comp Q)
    P (x (t+1)) = A (P (x t)) +
      (∑ k ∈ Finset.range t, B ((D^k) (C (P (x (t-1-k)))))) +
      B ((D^t) (Q (x 0))) := by
  dsimp only
  refine exact_memory_lags (P.comp (L.comp P)) (P.comp (L.comp (unresolved P)))
    ((unresolved P).comp (L.comp P)) ((unresolved P).comp (L.comp (unresolved P)))
    (fun s => P (x s)) (fun s => unresolved P (x s)) ?_ ?_ t
  · intro s
    have hs := (projected_recurrences P L idem x step s).1
    simpa only [LinearMap.comp_apply, idem] using hs
  · intro s
    have hs := (projected_recurrences P L idem x step s).2
    simpa only [LinearMap.comp_apply, unresolved_idempotent P idem] using hs

end Komorebi.LSM
