module
public import PolynomialPrescribedStep
public import PolynomialIntegerTower

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedIntegerTower

open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialIntegerTower
open Komorebi.PolynomialPrescribedSystem
open Komorebi.PolynomialParameterSystem (freePart join)

variable {m k e : ℕ}

/-- Every compatible integer parameter path extends to an actual polynomial
solution tower. Its parameter coordinates agree with the supplied integers
exactly, and only the initial solved-coordinate Jacobian must be surjective. -/
theorem exists_prescribed_tower (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian q F x))
    (t : ℕ → Fin k → ℤ) (ht0 : t 0 = freePart x)
    (ht : ∀ n j, (q : ℤ)^(L+n) ∣ t (n+1) j - t n j) :
    ∃ z : ℕ → Fin (m + k) → ℤ,
      z 0 = x ∧
      (∀ n, freePart (z n) = t n) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ n, solvedJacobian q F (z n) = solvedJacobian q F x) := by
  let State (n : ℕ) :=
    {y : Fin (m + k) → ℤ //
      (∀ i, (q : ℤ)^(L+n) ∣ evalSystem F y i) ∧
      freePart y = t n ∧ solvedJacobian q F y = solvedJacobian q F x}
  have advance (n : ℕ) (y : State n) :
      ∃ w : State (n+1), ∀ i, (q : ℤ)^(L+n) ∣ (w.val - y.val) i := by
    have hyJ : Function.Surjective (solvedJacobian q F y.val) := by
      rw [y.property.2.2]
      exact hJ
    have hparams : ∀ j, (q : ℤ)^(L+n) ∣ t (n+1) j - freePart y.val j := by
      rw [y.property.2.1]
      exact ht n
    obtain ⟨w, hcong, hroot, hfree, hfixed⟩ :=
      PolynomialPrescribedStep.one_step_lift q (L+n) hq (by omega)
        F y.val y.property.1 hyJ (t (n+1)) hparams
    refine ⟨⟨w, ?_, hfree, hfixed.trans y.property.2.2⟩, hcong⟩
    simpa only [Nat.add_assoc] using hroot
  let next (n : ℕ) (y : State n) : State (n+1) := Classical.choose (advance n y)
  let initial : State 0 := ⟨x, by simpa only [Nat.add_zero] using hx, ht0.symm, rfl⟩
  let state : (n : ℕ) → State n := fun n => Nat.rec initial (fun j y => next j y) n
  refine ⟨fun n => (state n).val, rfl, ?_, ?_, ?_, ?_⟩
  · exact fun n => (state n).property.2.1
  · exact fun n => (state n).property.1
  · intro n
    exact Classical.choose_spec (advance n (state n))
  · exact fun n => (state n).property.2.2

/-- The solved block itself is fixed along any compatible positive-depth
integer tower; this does not require surjectivity. -/
theorem tower_solvedJacobian_eq (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (z : ℕ → Fin (m + k) → ℤ)
    (hstep : ∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i)
    (n : ℕ) : solvedJacobian q F (z n) = solvedJacobian q F (z 0) := by
  apply LinearMap.ext
  intro u
  have h := congrArg (fun A : (Fin (m + k) → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) =>
    A (join u 0)) (tower_digitJacobian_eq q L hL F z hstep n)
  simpa only [digitJacobian_join, map_zero, add_zero] using h

/-- The prescribed tower retains every earlier residue and both the full and
solved reduced Jacobians. In particular, solved-block surjectivity persists
without an additional hypothesis at later levels. -/
theorem exists_prescribed_tower_strong (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian q F x))
    (t : ℕ → Fin k → ℤ) (ht0 : t 0 = freePart x)
    (ht : ∀ n j, (q : ℤ)^(L+n) ∣ t (n+1) j - t n j) :
    ∃ z : ℕ → Fin (m + k) → ℤ,
      z 0 = x ∧
      (∀ n, freePart (z n) = t n) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ a b, a ≤ b → ∀ i, (q : ℤ)^(L+a) ∣ (z b - z a) i) ∧
      (∀ n, digitJacobian q F (z n) = digitJacobian q F x) ∧
      (∀ n, solvedJacobian q F (z n) = solvedJacobian q F x) ∧
      (∀ n, Function.Surjective (solvedJacobian q F (z n))) := by
  obtain ⟨z, hz0, hfree, hroot, hstep, hfixed⟩ :=
    exists_prescribed_tower q L hq hL F x hx hJ t ht0 ht
  refine ⟨z, hz0, hfree, hroot, hstep, ?_, ?_, hfixed, ?_⟩
  · exact fun a b hab => tower_pairwise_congruent q L z hstep a b hab
  · intro n
    rw [← hz0]
    exact tower_digitJacobian_eq q L hL F z hstep n
  · intro n
    rw [hfixed n]
    exact hJ

end Komorebi.PolynomialPrescribedIntegerTower
