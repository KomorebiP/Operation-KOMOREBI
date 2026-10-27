module
public import PolynomialParameterSystem
public import PolynomialMinorSelection

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialCoordinateReorder
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialMinorSelection
variable {d e q : ℕ}

/-- Reorder coordinates by a permutation. -/
def reorderPoint {R : Type*} (σ : Equiv.Perm (Fin d)) (x : Fin d → R) : Fin d → R :=
  fun i => x (σ i)
/-- Rename actual polynomial variables consistently with reordered coordinates. -/
def reorderSystem (σ : Equiv.Perm (Fin d)) (F : Fin e → MvPolynomial (Fin d) ℤ) :
    Fin e → MvPolynomial (Fin d) ℤ := fun i => MvPolynomial.rename σ.symm (F i)

@[simp] theorem reorderPoint_inverse {R : Type*} (σ : Equiv.Perm (Fin d)) (x : Fin d → R) :
    reorderPoint σ.symm (reorderPoint σ x) = x := by ext i; simp [reorderPoint]
@[simp] theorem reorderPoint_inverse' {R : Type*} (σ : Equiv.Perm (Fin d)) (x : Fin d → R) :
    reorderPoint σ (reorderPoint σ.symm x) = x := by ext i; simp [reorderPoint]

theorem continuous_reorderPoint {R : Type*} [TopologicalSpace R] (σ : Equiv.Perm (Fin d)) :
    Continuous (reorderPoint (R := R) σ) := by exact continuous_pi fun i => continuous_apply _

theorem evalSystem_reorder (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (z : Fin d → ℤ) :
    evalSystem (reorderSystem σ F) z = evalSystem F (reorderPoint σ.symm z) := by
  ext i
  simp only [evalSystem, reorderSystem, MvPolynomial.eval_rename]
  rfl

theorem evalSystem_reorder_at (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    evalSystem (reorderSystem σ F) (reorderPoint σ x) = evalSystem F x := by
  rw [evalSystem_reorder, reorderPoint_inverse]

theorem padicEval_reorder (p : ℕ) [Fact (Nat.Prime p)] (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (z : Fin d → ℤ_[p]) :
    padicEval p (reorderSystem σ F) z = padicEval p F (reorderPoint σ.symm z) := by
  ext i
  simp only [padicEval, reorderSystem, MvPolynomial.eval₂_rename]
  rfl

theorem padicEval_reorder_at (p : ℕ) [Fact (Nat.Prime p)] (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ_[p]) :
    padicEval p (reorderSystem σ F) (reorderPoint σ x) = padicEval p F x := by
  rw [padicEval_reorder, reorderPoint_inverse]

theorem pderiv_reorder (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (i : Fin e) (k : Fin d) :
    MvPolynomial.pderiv k (reorderSystem σ F i) =
      MvPolynomial.rename σ.symm (MvPolynomial.pderiv (σ k) (F i)) := by
  simpa only [Equiv.symm_apply_apply, reorderSystem] using
    MvPolynomial.pderiv_rename σ.symm.injective (σ k) (F i)

theorem pderiv_eval_reorder (σ : Equiv.Perm (Fin d))
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) (i : Fin e) (k : Fin d) :
    MvPolynomial.eval (reorderPoint σ x) (MvPolynomial.pderiv k (reorderSystem σ F i)) =
      MvPolynomial.eval x (MvPolynomial.pderiv (σ k) (F i)) := by
  rw [pderiv_reorder, MvPolynomial.eval_rename]
  have hx : reorderPoint σ x ∘ σ.symm = x := by
    ext j
    simp [reorderPoint]
  rw [hx]

theorem digitJacobian_single (p : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) (k : Fin d) (i : Fin e) :
    digitJacobian p F x (Pi.single k 1) i =
      (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) := by
  classical
  simp [digitJacobian, Pi.single_apply, apply_ite]

theorem solvedJacobian_reorder_apply (p : ℕ) (σ : Equiv.Perm (Fin (e + q)))
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (u : Fin e → ZMod p) :
    solvedJacobian p (reorderSystem σ F) (reorderPoint σ x) u =
      ∑ k, u k • digitJacobian p F x (Pi.single (σ (Fin.castAdd q k)) 1) := by
  ext i
  simp only [solvedJacobian, LinearMap.coe_mk, AddHom.coe_mk, pderiv_eval_reorder,
    Finset.sum_apply, Pi.smul_apply, smul_eq_mul, digitJacobian_single]
  apply Finset.sum_congr rfl
  intro k _
  ring

theorem exists_reorder_solvedJacobian_surjective (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ σ : Equiv.Perm (Fin (e + q)),
      Function.Surjective (solvedJacobian p (reorderSystem σ F) (reorderPoint σ x)) := by
  obtain ⟨σ, hσ⟩ := exists_prime_permuted_columns p (digitJacobian p F x) hJ
  refine ⟨σ, ?_⟩
  intro b
  obtain ⟨u, hu⟩ := hσ b
  exact ⟨u, by rw [solvedJacobian_reorder_apply]; exact hu⟩

end Komorebi.PolynomialCoordinateReorder
