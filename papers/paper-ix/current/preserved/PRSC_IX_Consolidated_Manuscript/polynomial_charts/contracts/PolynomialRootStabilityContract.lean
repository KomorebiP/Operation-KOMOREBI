module
public import PolynomialRootStability

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialRootStabilityContract

/-- A rectangular system has a nearby perturbed root whenever its actual
reduced Jacobian is surjective. Full coefficient precision M is retained. -/
theorem explicit_rectangular_nearby_root (p M : ℕ) [Fact (Nat.Prime p)]
    (hM : 1 ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c) {d e : ℕ}
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin e =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k))
    (a : Fin d → ℤ_[p])
    (ha : ∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0)
    (hax : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p])) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) b
        (F i + MvPolynomial.C c * H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^M ∣ b i - a i) := by
  exact PolynomialRootStability.exists_nearby_perturbed_root p M hM c hc F H x hJ a ha hax

/-- The displacement bound applies to every perturbed root in the original
square residue ball, without choosing an auxiliary root as an assumption. -/
theorem explicit_square_root_displacement (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c) {d : ℕ}
    (F H : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin d =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0)
    (hb : ∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) b
      (F i + MvPolynomial.C c * H i) = 0)
    (hax : ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) :
    ∀ i, (p : ℤ_[p])^M ∣ b i - a i := by
  exact PolynomialRootStability.perturbed_roots_congruent p L M hL hLM c hc F H x hJ
    a b ha hb hax hbx

/-- From one lower root, obtain the original exact root and a unique exact
perturbed root. The Jacobian is evaluated from F, not supplied as an unrelated matrix. -/
theorem explicit_lower_root_and_unique_perturbation (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c) {d : ℕ}
    (F H : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin d =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) ∧
      ∃! b : Fin d → ℤ_[p],
        (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) b
          (F i + MvPolynomial.C c * H i) = 0) ∧
        (∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) ∧
        (∀ i, (p : ℤ_[p])^M ∣ b i - a i) := by
  exact PolynomialRootStability.exists_root_and_unique_perturbation
    p L M hL hLM c hc F H x hx hJ

end Komorebi.PolynomialRootStabilityContract
