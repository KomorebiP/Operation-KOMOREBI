module
public import PolynomialPrescribedObstruction

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped BigOperators Classical

namespace Komorebi.PolynomialPrescribedContract
open MvPolynomial
variable {m k e : ℕ}

/-- The contract writes the solved-coordinate derivative columns explicitly. -/
def actualSolvedMap (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) : (Fin m → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) where
  toFun u i := ∑ j, (eval x (pderiv (Fin.castAdd k j) (F i)) : ZMod q) * u j
  map_add' u v := by ext i; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a u := by
    ext i
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- Actual next-level residue vectors, with all three restrictions written out. -/
abbrev ActualResidues (q L : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (v : Fin k → ZMod q) :=
  {y : Fin (m + k) → ZMod (q ^ (L + 1)) //
    (∀ i, (q : ℤ) ^ L ∣ ((y i).val : ℤ) - x i) ∧
    (∀ i, (q : ℤ) ^ (L + 1) ∣ eval (fun j => ((y j).val : ℤ)) (F i)) ∧
    (∀ j : Fin k, y (Fin.natAdd m j) =
      ((x (Fin.natAdd m j) + (q : ℤ) ^ L * ((v j).val : ℤ) : ℤ) :
        ZMod (q ^ (L + 1))))}

/-- Flattening the formal lift subtype preserves precisely the residue vectors. -/
def actualResidueEquiv (q L : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (v : Fin k → ZMod q) :
    ActualResidues q L F x v ≃ PolynomialPrescribedLifts.PrescribedLifts q L F x v where
  toFun y := ⟨⟨⟨y.val, y.property.1⟩, y.property.2.1⟩, funext y.property.2.2⟩
  invFun y := ⟨y.val.val.val, y.val.val.property, y.val.property,
    fun j => congrFun y.property j⟩
  left_inv _ := rfl
  right_inv _ := rfl

/-- The lower root alone supplies one residual for every parameter choice.
Both the solved quotient and parameter derivative contributions are explicit. -/
theorem actual_lower_root_obstruction (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ) ^ L ∣ eval x (F i)) :
    ∃ r : Fin e → ℤ, (∀ i, eval x (F i) = (q : ℤ) ^ L * r i) ∧
      Finite ((Fin e → ZMod q) ⧸ (actualSolvedMap q F x).range) ∧
      (∀ v : Fin k → ZMod q,
        (∃ y : Fin (m + k) → ZMod (q ^ (L + 1)),
          (∀ i, (q : ℤ) ^ L ∣ ((y i).val : ℤ) - x i) ∧
          (∀ i, (q : ℤ) ^ (L + 1) ∣ eval (fun j => ((y j).val : ℤ)) (F i)) ∧
          (∀ j : Fin k, y (Fin.natAdd m j) =
            ((x (Fin.natAdd m j) + (q : ℤ) ^ L * ((v j).val : ℤ) : ℤ) :
              ZMod (q ^ (L + 1))))) ↔
        (Submodule.Quotient.mk (fun i => (r i : ZMod q) +
          ∑ j : Fin k, (eval x (pderiv (Fin.natAdd m j) (F i)) : ZMod q) * v j) :
          (Fin e → ZMod q) ⧸ (actualSolvedMap q F x).range) = 0) := by
  obtain ⟨r, hr, hf, _⟩ :=
    PolynomialPrescribedObstruction.finite_prescribed_obstruction q L hq hL F x hx
  refine ⟨r, fun i => congrFun hr i, hf, ?_⟩
  intro v
  exact PolynomialPrescribedObstruction.prescribed_residue_exists_iff q L hq hL F x r hr v

/-- Prime-field counts apply to the actual constrained residue vectors, using
rank of the solved derivative block and the same derived residual for every v. -/
theorem actual_lower_root_prime_count (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (p : ℤ) ^ L ∣ eval x (F i)) :
    ∃ r : Fin e → ℤ, (∀ i, eval x (F i) = (p : ℤ) ^ L * r i) ∧
      (∀ v : Fin k → ZMod p,
        Nat.card (ActualResidues p L F x v) =
          if (Submodule.Quotient.mk (fun i => (r i : ZMod p) +
            ∑ j : Fin k, (eval x (pderiv (Fin.natAdd m j) (F i)) : ZMod p) * v j) :
            (Fin e → ZMod p) ⧸ (actualSolvedMap p F x).range) = 0 then
              p ^ (m - Module.finrank (ZMod p) (actualSolvedMap p F x).range) else 0) ∧
      Nat.card ((Fin e → ZMod p) ⧸ (actualSolvedMap p F x).range) =
        p ^ (e - Module.finrank (ZMod p) (actualSolvedMap p F x).range) := by
  obtain ⟨r, hr, hv, hc⟩ :=
    PolynomialPrescribedObstruction.finite_prescribed_lift_count p L hL F x hx
  refine ⟨r, fun i => congrFun hr i, ?_, hc⟩
  intro v
  rw [Nat.card_congr (actualResidueEquiv p L F x v)]
  exact (hv v).2

end Komorebi.PolynomialPrescribedContract
