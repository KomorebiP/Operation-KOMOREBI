module
public import PolynomialSmoothCounts
public import PadicTowerLimit
public import Mathlib.Topology.Algebra.MvPolynomial

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PolynomialPadicLift
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialIntegerTower Komorebi.PolynomialSmoothCounts
variable {d e : ℕ}

/-- Evaluation of the original integer polynomials in the actual p-adic integers. -/
def padicEval (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (a : Fin d → ℤ_[p]) : Fin e → ℤ_[p] :=
  fun i => MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i)

/-- Coefficient casting commutes with evaluation of every original polynomial. -/
theorem padicEval_intCast (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) (i : Fin e) :
    padicEval p F (fun k => (x k : ℤ_[p])) i = (evalSystem F x i : ℤ_[p]) := by
  exact (MvPolynomial.eval₂_comp (Int.castRingHom ℤ_[p]) x (F i)).symm

/-- The actual polynomial evaluation is continuous in the p-adic product topology. -/
theorem continuous_padicEval (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (i : Fin e) :
    Continuous (fun a : Fin d → ℤ_[p] => padicEval p F a i) := by
  simpa only [padicEval, MvPolynomial.eval_map] using
    (MvPolynomial.continuous_eval ((F i).map (Int.castRingHom ℤ_[p])))

/-- A convergent polynomial tower with diverging residual precision has an exact root as its limit. -/
theorem polynomial_tower_limit_root (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (z : ℕ → Fin d → ℤ)
    (a : Fin d → ℤ_[p])
    (hroot : ∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i)
    (hlim : Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a)) :
    ∀ i, padicEval p F a i = 0 := by
  intro i
  have heval := ((continuous_padicEval p F i).tendsto a).comp hlim
  have hzero := PadicTowerLimit.divisible_int_tendsto_zero p L
    (fun n => evalSystem F (z n) i) (fun n => hroot n i)
  have hcast : (fun n => padicEval p F (fun k => (z n k : ℤ_[p])) i) =
      (fun n => (evalSystem F (z n) i : ℤ_[p])) := by
    funext n
    exact padicEval_intCast p F (z n) i
  change Tendsto (fun n => padicEval p F (fun k => (z n k : ℤ_[p])) i)
    atTop (𝓝 (padicEval p F a i)) at heval
  rw [hcast] at heval
  exact tendsto_nhds_unique heval hzero

/-- A surjective initial reduced Jacobian gives an actual convergent tower,
a p-adic root, all retained precisions, a constant reduced Jacobian, and exact branching. -/
theorem exists_padic_root_with_tower (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ z : ℕ → Fin d → ℤ, ∃ a : Fin d → ℤ_[p],
      z 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ a i - (z n i : ℤ_[p])) ∧
      (∀ i, padicEval p F a i = 0) ∧
      (∀ n, digitJacobian p F (z n) = digitJacobian p F x) ∧
      (∀ n, Nat.card (PolynomialLiftCounts.ActualLifts p (L+n) F (z n)) = p^(d-e)) := by
  obtain ⟨z, hz0, hroot, hstep, _, hcount⟩ := exists_regular_tower p L hL F x hx hJ
  obtain ⟨a, ha, hprecision⟩ :=
    PadicTowerLimit.compatible_vector_tower_limit p L z hstep
  refine ⟨z, a, hz0, hroot, hstep, ha, hprecision,
    polynomial_tower_limit_root p L F z a hroot ha, ?_, hcount⟩
  intro n
  rw [← hz0]
  exact tower_digitJacobian_eq p L hL F z hstep n

/-- Every smooth lower polynomial root lifts to an exact p-adic root in the
same prescribed residue class. Only the initial Jacobian is assumed surjective. -/
theorem exists_padic_root (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  obtain ⟨z, a, hz0, _, _, _, hprecision, hroot, _, _⟩ :=
    exists_padic_root_with_tower p L hL F x hx hJ
  refine ⟨a, hroot, ?_⟩
  intro i
  simpa only [Nat.add_zero, hz0] using hprecision 0 i

end Komorebi.PolynomialPadicLift
