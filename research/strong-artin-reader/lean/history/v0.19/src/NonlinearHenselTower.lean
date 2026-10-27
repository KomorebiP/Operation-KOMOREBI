import NonlinearHenselStep

/-!
# Compatible nonlinear Hensel towers

Iterating the one-step theorem produces an actual sequence of approximate
solutions whose defects gain one power at every stage and whose successive
states remain compatible modulo the previous power.
-/

namespace Komorebi.StrongArtin.NonlinearHenselTower

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.NonlinearHenselStep

noncomputable section

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- An exact right inverse and one-power Taylor gain produce a compatible tower
of genuine nonlinear approximations. -/
theorem exists_approximation_tower
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : ℕ → X,
      x 0 = x₀ ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (F (x n))) ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (x (n + 1) - x n)) := by
  let S : ℕ → Type _ := fun n => {x : X // PowDivisible pi (n + 1) (F x)}
  have hstep : ∀ n : ℕ, ∀ a : S n,
      ∃ b : S (n + 1), PowDivisible pi (n + 1) (b.1 - a.1) := by
    intro n a
    obtain ⟨x', hcongr, hnext⟩ :=
      exists_next_approximation pi F J rightInv hRight hgain
        (Nat.succ_le_succ (Nat.zero_le n)) a.1 a.2
    refine ⟨⟨x', ?_⟩, hcongr⟩
    simpa [Nat.add_assoc] using hnext
  let next : ∀ n : ℕ, S n → S (n + 1) :=
    fun n a => Classical.choose (hstep n a)
  let seqS : ∀ n : ℕ, S n :=
    fun n => Nat.rec (motive := fun n => S n) ⟨x₀, hx₀⟩
      (fun n a => next n a) n
  refine ⟨fun n => (seqS n).1, ?_, ?_, ?_⟩
  · rfl
  · intro n
    exact (seqS n).2
  · intro n
    have hspec := Classical.choose_spec (hstep n (seqS n))
    change PowDivisible pi (n + 1) ((seqS (n + 1)).1 - (seqS n).1)
    simpa [seqS, next] using hspec

/-- At every prescribed depth there is an actual nonlinear approximation of
that depth, compatible with the initial residual point through a tower. -/
theorem exists_approximation_at_depth
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀))
    (n : ℕ) :
    ∃ x : X, PowDivisible pi (n + 1) (F x) := by
  obtain ⟨tower, -, htower, -⟩ :=
    exists_approximation_tower pi F J rightInv hRight hgain x₀ hx₀
  exact ⟨tower n, htower n⟩

/-- If the coefficient power vanishes, the tower reaches an exact zero of the
nonlinear equation. -/
theorem exists_exact_solution_of_pow_eq_zero
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀))
    (n : ℕ) (hpi : pi ^ (n + 1) = 0) :
    ∃ x : X, F x = 0 := by
  obtain ⟨x, hx⟩ :=
    exists_approximation_at_depth pi F J rightInv hRight hgain x₀ hx₀ n
  exact ⟨x, eq_zero_of_pow_eq_zero hx hpi⟩

end

end Komorebi.StrongArtin.NonlinearHenselTower

#print axioms Komorebi.StrongArtin.NonlinearHenselTower.exists_approximation_tower
#print axioms Komorebi.StrongArtin.NonlinearHenselTower.exists_exact_solution_of_pow_eq_zero
