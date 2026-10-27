import Komorebi.SufficientResolution.Compression
import Mathlib.LinearAlgebra.Prod
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Lean.Elab.Tactic.Omega

/-!
# Exact discrete elimination of hidden state

All identities are algebraic and quantified over arbitrary natural time.  A
prepared hidden initial state is distinguished from an arbitrary initial state.
No continuous-time integral or convergence assertion is made.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution

universe uR uV uH
variable {R : Type uR} [CommRing R]
variable {V : Type uV} [AddCommGroup V] [Module R V]
variable {H : Type uH} [AddCommGroup H] [Module R H]

/-- The four blocks of a visible/hidden linear dynamical system. -/
structure BlockDynamics (R : Type uR) [CommRing R]
    (V : Type uV) [AddCommGroup V] [Module R V]
    (H : Type uH) [AddCommGroup H] [Module R H] where
  A : V →ₗ[R] V
  B : H →ₗ[R] V
  G : V →ₗ[R] H
  D : H →ₗ[R] H

namespace BlockDynamics
variable (b : BlockDynamics R V H)

/-- The actual full state transition, not a supplied recurrence hypothesis. -/
def step : (V × H) →ₗ[R] (V × H) :=
  ((b.A.comp (LinearMap.fst R V H)) + (b.B.comp (LinearMap.snd R V H))).prod
    ((b.G.comp (LinearMap.fst R V H)) + (b.D.comp (LinearMap.snd R V H)))

@[simp] theorem step_apply (y : V) (z : H) :
    b.step (y,z) = (b.A y + b.B z, b.G y + b.D z) := rfl

/-- Actual visible trajectory from the full initial state. -/
def visible (n : ℕ) (y : V) (z : H) : V := ((b.step ^ n) (y,z)).1
/-- Actual hidden trajectory from the full initial state. -/
def hiddenState (n : ℕ) (y : V) (z : H) : H := ((b.step ^ n) (y,z)).2

@[simp] theorem visible_zero (y : V) (z : H) : b.visible 0 y z = y := rfl
@[simp] theorem hiddenState_zero (y : V) (z : H) : b.hiddenState 0 y z = z := rfl

 theorem visible_succ (n : ℕ) (y : V) (z : H) :
    b.visible (n+1) y z = b.A (b.visible n y z) + b.B (b.hiddenState n y z) := by
  simp only [visible, hiddenState, pow_succ', Module.End.mul_apply, step]
  rfl

 theorem hiddenState_succ (n : ℕ) (y : V) (z : H) :
    b.hiddenState (n+1) y z = b.D (b.hiddenState n y z) + b.G (b.visible n y z) := by
  simp only [visible, hiddenState, pow_succ', Module.End.mul_apply, step]
  exact add_comm _ _

/-- A forced linear recurrence has an exact finite convolution solution. -/
 theorem forced_recurrence_formula (D : H →ₗ[R] H) (u f : ℕ → H)
    (h : ∀ n, u (n+1) = D (u n) + f n) (n : ℕ) :
    u n = (D^n) (u 0) + ∑ j ∈ Finset.range n, (D^(n-1-j)) (f j) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [h, ih, map_add, map_sum, Finset.sum_range_succ]
    have hs : ∑ j ∈ Finset.range n, D ((D^(n-1-j)) (f j)) =
        ∑ j ∈ Finset.range n, (D^(n+1-1-j)) (f j) := by
      apply Finset.sum_congr rfl
      intro j hj
      have hjn : j < n := Finset.mem_range.mp hj
      have hn : n+1-1-j = (n-1-j)+1 := by omega
      rw [hn, pow_succ', Module.End.mul_apply]
    rw [hs]
    simp only [Nat.add_sub_cancel, Nat.sub_self, pow_zero, Module.End.one_apply]
    rw [pow_succ', Module.End.mul_apply, add_assoc]

/-- Hidden state is initial hidden evolution plus all visible-to-hidden inputs. -/
 theorem hidden_elimination (n : ℕ) (y : V) (z : H) :
    b.hiddenState n y z = (b.D^n) z +
      ∑ j ∈ Finset.range n, (b.D^(n-1-j)) (b.G (b.visible j y z)) := by
  exact forced_recurrence_formula b.D (fun k => b.hiddenState k y z)
    (fun k => b.G (b.visible k y z)) (fun k => b.hiddenState_succ k y z) n

/-- Delayed hidden-return kernel: first enter hidden state, evolve, then return. -/
def memory (n : ℕ) : V →ₗ[R] V := b.B.comp ((b.D^n).comp b.G)

@[simp] theorem memory_apply (n : ℕ) (y : V) :
    b.memory n y = b.B ((b.D^n) (b.G y)) := rfl

@[simp] theorem memory_zero : b.memory 0 = b.B.comp b.G := by
  ext y
  rfl

/-- Exact discrete memory equation derived from the full state evolution. -/
 theorem discrete_memory_equation (n : ℕ) (y : V) (z : H) :
    b.visible (n+1) y z = b.A (b.visible n y z) + b.B ((b.D^n) z) +
      ∑ j ∈ Finset.range n, b.memory (n-1-j) (b.visible j y z) := by
  rw [b.visible_succ, b.hidden_elimination, map_add, map_sum]
  simp only [memory_apply, add_assoc]

/-- The first-coordinate split compression of the full state space. -/
def compression (_b : BlockDynamics R V H) : SplitCompression R (V × H) V where
  compress := LinearMap.fst R V H
  lift := LinearMap.inl R V H
  compress_lift := by ext y; rfl

/-- Visible evolution with hidden initial state exactly zero. -/
def prepared (n : ℕ) : V →ₗ[R] V := b.compression.coarse (b.step^n)

@[simp] theorem prepared_apply (n : ℕ) (y : V) :
    b.prepared n y = b.visible n y 0 := rfl

@[simp] theorem prepared_zero : b.prepared 0 = 1 := by
  ext y
  rfl

@[simp] theorem prepared_one : b.prepared 1 = b.A := by
  ext y
  simp [prepared_apply, visible, step]

/-- Operator-valued renewal recurrence for every prepared visible evolution. -/
 theorem prepared_recurrence (n : ℕ) :
    b.prepared (n+1) = b.A * b.prepared n +
      ∑ j ∈ Finset.range n, b.memory (n-1-j) * b.prepared j := by
  ext y
  have h := b.discrete_memory_equation n y 0
  simpa only [LinearMap.add_apply, LinearMap.sum_apply, Module.End.mul_apply,
    prepared_apply, map_zero, add_zero] using h

/-- At the first potentially nonzero memory index, the return is isolated. -/
 theorem prepared_first_return (k : ℕ) (h : ∀ j < k, b.memory j = 0) :
    b.prepared (k+2) = b.A * b.prepared (k+1) + b.memory k := by
  rw [show k+2 = (k+1)+1 by omega, b.prepared_recurrence]
  congr 1
  calc
    ∑ j ∈ Finset.range (k+1), b.memory (k+1-1-j) * b.prepared j =
        b.memory (k+1-1-0) * b.prepared 0 := by
      apply Finset.sum_eq_single 0
      · intro j hj hj0
        have hjk : j < k+1 := Finset.mem_range.mp hj
        rw [h (k+1-1-j) (by omega), zero_mul]
      · intro hf
        exact False.elim (hf (Finset.mem_range.mpr (by omega)))
    _ = b.memory k := by simp

end BlockDynamics
end Komorebi.SufficientResolution
