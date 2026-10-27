import PowerDivisibility

/-!
# One nonlinear Hensel improvement step

The theorem separates the exact linear solve from the nonlinear Taylor
remainder.  If `J` has a right inverse and the remainder gains one power of
`pi` on corrections already divisible by `pi^n`, then an approximate solution
of depth `n` improves to depth `n+1` without changing its class modulo `pi^n`.
-/

namespace Komorebi.StrongArtin.NonlinearHenselStep

open Komorebi.StrongArtin.PowerDivisibility

noncomputable section

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- The nonlinear remainder after subtracting the fixed linear part. -/
def remainder (F : X → W) (J : X →ₗ[R] W) (x delta : X) : W :=
  F (x + delta) - F x - J delta

/-- The exact filtration gain needed for one Hensel step. -/
def RemainderRaisesOne (pi : R) (F : X → W) (J : X →ₗ[R] W) : Prop :=
  ∀ n : ℕ, 1 ≤ n → ∀ x delta : X,
    PowDivisible pi n delta →
    PowDivisible pi (n + 1) (remainder F J x delta)

/-- A right inverse sends an error of depth `n` to a correction of the same
filtration depth. -/
theorem correction_is_powDivisible
    (pi : R) (rightInv : W →ₗ[R] X)
    {n : ℕ} {error : W}
    (herror : PowDivisible pi n error) :
    PowDivisible pi n (-rightInv error) := by
  exact (herror.map rightInv).neg

/-- The correction built from an exact right inverse cancels the linear error. -/
theorem rightInverse_correction_cancels
    (J : X →ₗ[R] W) (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id) (error : W) :
    J (-rightInv error) + error = 0 := by
  have happly := LinearMap.congr_fun hRight error
  have hJR : J (rightInv error) = error := by
    simpa using happly
  simp [hJR]

/-- One genuine nonlinear improvement step. -/
theorem exists_next_approximation
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id)
    (hgain : RemainderRaisesOne pi F J)
    {n : ℕ} (hn : 1 ≤ n) (x : X)
    (hx : PowDivisible pi n (F x)) :
    ∃ x' : X,
      PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') := by
  let delta : X := -rightInv (F x)
  have hdelta : PowDivisible pi n delta := by
    exact correction_is_powDivisible pi rightInv hx
  have hcancel : J delta + F x = 0 := by
    exact rightInverse_correction_cancels J rightInv hRight (F x)
  have hJdelta : J delta = -F x := eq_neg_of_add_eq_zero_left hcancel
  have hrem := hgain n hn x delta hdelta
  refine ⟨x + delta, ?_, ?_⟩
  · simpa [delta] using hdelta
  · have hremainder : remainder F J x delta = F (x + delta) := by
      simp [remainder, hJdelta]
    rw [hremainder] at hrem
    exact hrem

/-- The Hensel update preserves the previous approximation modulo `pi^n`. -/
theorem next_approximation_congruent
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (rightInv : W →ₗ[R] X)
    (hRight : J.comp rightInv = LinearMap.id)
    (hgain : RemainderRaisesOne pi F J)
    {n : ℕ} (hn : 1 ≤ n) (x : X)
    (hx : PowDivisible pi n (F x)) :
    ∃ x' : X,
      PowDivisible pi n (x' - x) ∧
      PowDivisible pi (n + 1) (F x') :=
  exists_next_approximation pi F J rightInv hRight hgain hn x hx

end

end Komorebi.StrongArtin.NonlinearHenselStep

#print axioms Komorebi.StrongArtin.NonlinearHenselStep.exists_next_approximation
#print axioms Komorebi.StrongArtin.NonlinearHenselStep.rightInverse_correction_cancels
