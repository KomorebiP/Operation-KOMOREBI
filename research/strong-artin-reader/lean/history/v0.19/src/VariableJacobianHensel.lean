import NilpotentRightInverse
import PowerDivisibility

/-!
# Nonlinear Hensel lifting with a state-dependent Jacobian

This is the relative formal-smoothness form needed by deformation problems.  A
single lifted residual right inverse is allowed to have a `pi`-divisible error
for the Jacobian at every point in the residual fibre.  Nilpotence corrects it
to an exact right inverse at each stage.  A first-order Taylor law whose
remainder gains one power then produces a compatible nonlinear tower.
-/

namespace Komorebi.StrongArtin.VariableJacobianHensel

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.NilpotentRightInverse

noncomputable section

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- Two points have the same residual class when their difference is divisible
by `pi`. -/
def SameResidual (pi : R) (base x : X) : Prop :=
  PowDivisible pi 1 (x - base)

@[simp] theorem sameResidual_self (pi : R) (x : X) : SameResidual pi x x := by
  simp [SameResidual]

/-- The state-dependent first-order remainder. -/
def variableRemainder
    (F : X → W) (D : X → (X →ₗ[R] W)) (x delta : X) : W :=
  F (x + delta) - F x - D x delta

/-- Corrections of depth `n ≥ 1` have nonlinear remainder of depth `n+1`. -/
def VariableRemainderRaisesOne
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W)) : Prop :=
  ∀ n : ℕ, 1 ≤ n → ∀ x delta : X,
    PowDivisible pi n delta →
    PowDivisible pi (n + 1) (variableRemainder F D x delta)

/-- A correction of positive depth preserves the residual fibre. -/
theorem sameResidual_of_sameResidual_of_powDivisible_sub
    (pi : R) (base x x' : X) {n : ℕ} (hn : 1 ≤ n)
    (hx : SameResidual pi base x)
    (hstep : PowDivisible pi n (x' - x)) :
    SameResidual pi base x' := by
  have hstep₁ : PowDivisible pi 1 (x' - x) := hstep.mono hn
  unfold SameResidual at hx ⊢
  rw [← sub_add_sub_cancel x' x base]
  exact hstep₁.add hx

/-- One nonlinear improvement with a state-dependent Jacobian. -/
theorem exists_next_variable_approximation
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (approxRightInv : W →ₗ[R] X) (E : X → Module.End R W)
    (base : X)
    (happrox : ∀ x : X, SameResidual pi base x →
      (D x).comp approxRightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    {n : ℕ} (hn : 1 ≤ n) (x : X)
    (hxres : SameResidual pi base x)
    (hx : PowDivisible pi n (F x)) :
    ∃ x' : X,
      SameResidual pi base x' ∧
      PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') := by
  obtain ⟨rightInv, hRight⟩ :=
    exists_exact_rightInverse_of_scalar_nilpotent_error
      (D x) approxRightInv pi (E x) (happrox x hxres) hpi
  let delta : X := -rightInv (F x)
  have hdelta : PowDivisible pi n delta := by
    exact (hx.map rightInv).neg
  have happly := LinearMap.congr_fun hRight (F x)
  have hDR : D x (rightInv (F x)) = F x := by
    simpa using happly
  have hDdelta : D x delta = -F x := by
    simp [delta, hDR]
  have hrem := hgain n hn x delta hdelta
  have hremainder : variableRemainder F D x delta = F (x + delta) := by
    simp [variableRemainder, hDdelta]
  rw [hremainder] at hrem
  refine ⟨x + delta, ?_, ?_, hrem⟩
  · apply sameResidual_of_sameResidual_of_powDivisible_sub pi base x (x + delta) hn hxres
    simpa [delta] using hdelta
  · simpa [delta] using hdelta

/-- State-dependent residual Jacobian stability gives a compatible nonlinear
approximation tower. -/
theorem exists_variable_approximation_tower
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (approxRightInv : W →ₗ[R] X) (E : X → Module.End R W)
    (x₀ : X)
    (happrox : ∀ x : X, SameResidual pi x₀ x →
      (D x).comp approxRightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : ℕ → X,
      x 0 = x₀ ∧
      (∀ n : ℕ, SameResidual pi x₀ (x n)) ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (F (x n))) ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (x (n + 1) - x n)) := by
  let S : ℕ → Type _ := fun n =>
    {x : X // SameResidual pi x₀ x ∧ PowDivisible pi (n + 1) (F x)}
  have hstep : ∀ n : ℕ, ∀ a : S n,
      ∃ b : S (n + 1), PowDivisible pi (n + 1) (b.1 - a.1) := by
    intro n a
    obtain ⟨x', hxres', hcongr, hnext⟩ :=
      exists_next_variable_approximation
        pi F D approxRightInv E x₀ happrox hpi hgain
        (Nat.succ_le_succ (Nat.zero_le n)) a.1 a.2.1 a.2.2
    refine ⟨⟨x', hxres', ?_⟩, hcongr⟩
    simpa [Nat.add_assoc] using hnext
  let next : ∀ n : ℕ, S n → S (n + 1) :=
    fun n a => Classical.choose (hstep n a)
  let seqS : ∀ n : ℕ, S n :=
    fun n => Nat.rec (motive := fun n => S n)
      ⟨x₀, sameResidual_self pi x₀, hx₀⟩
      (fun n a => next n a) n
  refine ⟨fun n => (seqS n).1, ?_, ?_, ?_, ?_⟩
  · rfl
  · intro n
    exact (seqS n).2.1
  · intro n
    exact (seqS n).2.2
  · intro n
    have hspec := Classical.choose_spec (hstep n (seqS n))
    change PowDivisible pi (n + 1) ((seqS (n + 1)).1 - (seqS n).1)
    simpa [seqS, next] using hspec

/-- A state-dependent relative Hensel system over a nilpotent thickening reaches
an exact nonlinear solution. -/
theorem exists_exact_solution_variableJacobian
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (approxRightInv : W →ₗ[R] X) (E : X → Module.End R W)
    (x₀ : X)
    (happrox : ∀ x : X, SameResidual pi x₀ x →
      (D x).comp approxRightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : X, SameResidual pi x₀ x ∧ F x = 0 := by
  obtain ⟨tower, -, hres, hdefect, -⟩ :=
    exists_variable_approximation_tower
      pi F D approxRightInv E x₀ happrox hpi hgain hx₀
  obtain ⟨n, hn⟩ := hpi
  have hsucc : pi ^ (n + 1) = 0 := by
    rw [pow_succ, hn, zero_mul]
  refine ⟨tower n, hres n, ?_⟩
  exact eq_zero_of_pow_eq_zero (hdefect n) hsucc

end

end Komorebi.StrongArtin.VariableJacobianHensel

#print axioms Komorebi.StrongArtin.VariableJacobianHensel.exists_next_variable_approximation
#print axioms Komorebi.StrongArtin.VariableJacobianHensel.exists_variable_approximation_tower
#print axioms Komorebi.StrongArtin.VariableJacobianHensel.exists_exact_solution_variableJacobian
