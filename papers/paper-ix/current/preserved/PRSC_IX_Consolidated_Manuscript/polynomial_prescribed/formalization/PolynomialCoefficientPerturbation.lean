module
public import PolynomialPadicLift

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialCoefficientPerturbation
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialSurjectiveStep
variable {d e : ℕ}

/-- An actual coefficient perturbation of an integer polynomial system. -/
def perturb (c : ℤ) (F H : Fin e → MvPolynomial (Fin d) ℤ) :
    Fin e → MvPolynomial (Fin d) ℤ :=
  fun i => F i + MvPolynomial.C c * H i

/-- Integer evaluation of the perturbed system, derived from polynomial evaluation. -/
theorem evalSystem_perturb (c : ℤ) (F H : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) (i : Fin e) :
    evalSystem (perturb c F H) x i = evalSystem F x i + c * evalSystem H x i := by
  simp [evalSystem, perturb]

/-- Partial derivatives obey the same coefficient perturbation identity. -/
theorem pderiv_perturb (c : ℤ) (F H : Fin e → MvPolynomial (Fin d) ℤ)
    (i : Fin e) (k : Fin d) :
    MvPolynomial.pderiv k (perturb c F H i) =
      MvPolynomial.pderiv k (F i) + MvPolynomial.C c * MvPolynomial.pderiv k (H i) := by
  simp only [perturb, map_add, MvPolynomial.pderiv_C_mul]

/-- A coefficient perturbation divisible by q preserves the actual reduced Jacobian. -/
theorem digitJacobian_perturb_eq (q : ℕ) (c : ℤ) (hc : (q : ℤ) ∣ c)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    digitJacobian q (perturb c F H) x = digitJacobian q F x := by
  have hc0 : (c : ZMod q) = 0 := (ZMod.intCast_zmod_eq_zero_iff_dvd c q).mpr hc
  apply LinearMap.ext
  intro t
  ext i
  change (∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (perturb c F H i)) : ZMod q) * t k) =
    ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * t k
  simp [pderiv_perturb, hc0]

/-- Coefficient perturbations and movement inside one residue class preserve the same Jacobian. -/
theorem digitJacobian_perturb_point_eq (q : ℕ) (c : ℤ) (hc : (q : ℤ) ∣ c)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x y : Fin d → ℤ)
    (hxy : ∀ i, (q : ℤ) ∣ y i - x i) :
    digitJacobian q (perturb c F H) y = digitJacobian q F x := by
  rw [digitJacobian_perturb_eq q c hc F H y]
  exact digitJacobian_eq q F x y hxy

/-- A coefficient perturbation divisible by the prescribed precision preserves a lower root. -/
theorem lower_root_perturb (q L : ℕ) (c : ℤ) (hc : (q : ℤ)^L ∣ c)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i) :
    ∀ i, (q : ℤ)^L ∣ evalSystem (perturb c F H) x i := by
  intro i
  rw [evalSystem_perturb]
  exact dvd_add (hx i) (dvd_mul_of_dvd_left hc _)

/-- A positive-depth coefficient perturbation preserves smooth liftability and its initial precision. -/
theorem exists_padic_root_perturb (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (c : ℤ) (hc : (p : ℤ)^L ∣ c)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (perturb c F H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  have hpc : (p : ℤ) ∣ c :=
    (dvd_pow_self (p : ℤ) (by omega : L ≠ 0)).trans hc
  apply exists_padic_root p L hL (perturb c F H) x
  · exact lower_root_perturb p L c hc F H x hx
  · rw [digitJacobian_perturb_eq p c hpc F H x]
    exact hJ

/-- In particular, F + p^M H has a p-adic root at the original precision whenever M ≥ L ≥ 1. -/
theorem exists_padic_root_power_perturb (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a
        (F i + MvPolynomial.C ((p : ℤ)^M) * H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  exact exists_padic_root_perturb p L hL ((p : ℤ)^M)
    (pow_dvd_pow (p : ℤ) hLM) F H x hx hJ

/-- The p-adic evaluation identity uses the actual perturbed polynomial coefficients. -/
theorem padicEval_perturb (p : ℕ) [Fact (Nat.Prime p)]
    (c : ℤ) (F H : Fin e → MvPolynomial (Fin d) ℤ)
    (a : Fin d → ℤ_[p]) (i : Fin e) :
    padicEval p (perturb c F H) a i = padicEval p F a i + (c : ℤ_[p]) * padicEval p H a i := by
  simp only [padicEval, perturb, MvPolynomial.eval₂_add, MvPolynomial.eval₂_mul,
    MvPolynomial.eval₂_C]
  rfl

end Komorebi.PolynomialCoefficientPerturbation
