module
public import PolynomialParameterTowerControls
@[expose] public section
open Komorebi.PolynomialParameterTowerControls Komorebi.PolynomialPadicLift
open Komorebi.PolynomialParameterSystem

-- Invalid: even solved-block surjectivity does not force equal-parameter uniqueness
-- when there are more solved variables than equations. The positive control gives
-- explicit distinct roots in the same initial ball with exactly the same parameter.
example : Function.Surjective
    (Komorebi.PolynomialPrescribedSystem.solvedJacobian 2 firstSolved (fun _ => 0)) →
    ∀ b c : Fin (2 + 1) → ℤ_[2],
      (∀ i, padicEval 2 firstSolved b i = 0) →
      (∀ i, padicEval 2 firstSolved c i = 0) →
      (∀ i, (2 : ℤ_[2])^1 ∣ b i - ((0 : Fin (2 + 1) → ℤ) i : ℤ_[2])) →
      (∀ i, (2 : ℤ_[2])^1 ∣ c i - ((0 : Fin (2 + 1) → ℤ) i : ℤ_[2])) →
      freePart (e := 2) (q := 1) b = freePart c → b = c := by
  exact rectangular_same_parameter_nonunique
