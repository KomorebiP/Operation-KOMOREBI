module
public import PolynomialCoefficientPerturbation

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialCoefficientPerturbationContract

/-- This contract expands both the original polynomial perturbation and its
formal derivative. The reduced Jacobian is unchanged under coefficient perturbation. -/
theorem explicit_perturbed_jacobian (q : ℕ) (c : ℤ) (hc : (q : ℤ) ∣ c)
    {d e : ℕ} (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (t : Fin d → ZMod q) (i : Fin e) :
    (∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k
      (F i + MvPolynomial.C c * H i)) : ZMod q) * t k) =
    ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * t k := by
  have h := PolynomialCoefficientPerturbation.digitJacobian_perturb_eq q c hc F H x
  exact congrFun (LinearMap.congr_fun h t) i

/-- A perturbed exact root is derived from an approximate original root and
one actual surjective Jacobian, with the original residue precision retained. -/
theorem explicit_power_perturbation_root (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) {d e : ℕ}
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin e =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a
        (F i + MvPolynomial.C ((p : ℤ)^M) * H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  exact PolynomialCoefficientPerturbation.exists_padic_root_power_perturb
    p L M hL hLM F H x hx hJ

end Komorebi.PolynomialCoefficientPerturbationContract
