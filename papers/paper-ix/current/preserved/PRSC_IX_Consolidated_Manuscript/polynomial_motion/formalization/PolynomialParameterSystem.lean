module
public import PolynomialPadicLift

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift
variable {d e q : ℕ}

/-- The coordinates to be solved. -/
def solvedPart {R : Type*} (z : Fin (e + q) → R) : Fin e → R :=
  fun i => z (Fin.castAdd q i)
/-- The free coordinates. -/
def freePart {R : Type*} (z : Fin (e + q) → R) : Fin q → R :=
  fun j => z (Fin.natAdd e j)
/-- Join solved and free coordinates in their original order. -/
def join {R : Type*} (y : Fin e → R) (t : Fin q → R) : Fin (e + q) → R :=
  Fin.append y t

@[simp] theorem join_solved {R : Type*} (y : Fin e → R) (t : Fin q → R) (i : Fin e) :
    join y t (Fin.castAdd q i) = y i := by simp [join]
@[simp] theorem join_free {R : Type*} (y : Fin e → R) (t : Fin q → R) (j : Fin q) :
    join y t (Fin.natAdd e j) = t j := by simp [join]
@[simp] theorem solvedPart_join {R : Type*} (y : Fin e → R) (t : Fin q → R) :
    solvedPart (join y t) = y := by ext i; simp [solvedPart]
@[simp] theorem freePart_join {R : Type*} (y : Fin e → R) (t : Fin q → R) :
    freePart (join y t) = t := by ext i; simp [freePart]
@[simp] theorem join_parts {R : Type*} (z : Fin (e + q) → R) :
    join (solvedPart z) (freePart z) = z := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;> simp [solvedPart, freePart]

theorem continuous_solvedPart {R : Type*} [TopologicalSpace R] :
    Continuous (solvedPart (e := e) (q := q) (R := R)) := by
  exact continuous_pi fun i => continuous_apply _
theorem continuous_freePart {R : Type*} [TopologicalSpace R] :
    Continuous (freePart (e := e) (q := q) (R := R)) := by
  exact continuous_pi fun i => continuous_apply _
theorem continuous_join {R : Type*} [TopologicalSpace R] :
    Continuous (fun yt : (Fin e → R) × (Fin q → R) => join yt.1 yt.2) := by
  apply continuous_pi
  intro i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i
  · simpa only [join_solved, Function.comp_def] using (continuous_apply j).comp continuous_fst
  · simpa only [join_free, Function.comp_def] using (continuous_apply j).comp continuous_snd

/-- Append the free coordinate functions to the polynomial equations. -/
def augmented (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) :
    Fin (e + q) → MvPolynomial (Fin (e + q)) ℤ :=
  join F (fun j => MvPolynomial.X (Fin.natAdd e j))
@[simp] theorem augmented_solved (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (i : Fin e) :
    augmented F (Fin.castAdd q i) = F i := by simp [augmented]
@[simp] theorem augmented_free (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (j : Fin q) :
    augmented F (Fin.natAdd e j) = MvPolynomial.X (Fin.natAdd e j) := by simp [augmented]

theorem evalSystem_augmented (F : Fin e → MvPolynomial (Fin (e + q)) ℤ)
    (z : Fin (e + q) → ℤ) :
    evalSystem (augmented F) z = join (evalSystem F z) (freePart z) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [evalSystem, freePart]

theorem padicEval_augmented (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (z : Fin (e + q) → ℤ_[p]) :
    padicEval p (augmented F) z = join (padicEval p F z) (freePart z) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [padicEval, freePart]

theorem padicEval_augmented_iff (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ)
    (z : Fin (e + q) → ℤ_[p]) (t : Fin q → ℤ_[p]) :
    padicEval p (augmented F) z = join 0 t ↔ padicEval p F z = 0 ∧ freePart z = t := by
  rw [padicEval_augmented]
  constructor
  · intro h
    exact ⟨by simpa using congrArg solvedPart h, by simpa using congrArg freePart h⟩
  · rintro ⟨hF, ht⟩
    rw [hF, ht]

/-- The actual Jacobian restricted to the solved coordinates. -/
def solvedJacobian (p : ℕ) (F : Fin e → MvPolynomial (Fin (e + q)) ℤ)
    (x : Fin (e + q) → ℤ) : (Fin e → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p) where
  toFun u i := ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv (Fin.castAdd q k) (F i)) : ZMod p) * u k
  map_add' u v := by ext i; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a u := by
    ext i
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k _
    ring

theorem digitJacobian_join_zero (p : ℕ) (F : Fin e → MvPolynomial (Fin (e + q)) ℤ)
    (x : Fin (e + q) → ℤ) (u : Fin e → ZMod p) :
    digitJacobian p F x (join u 0) = solvedJacobian p F x u := by
  ext i
  simp [digitJacobian, solvedJacobian, Fin.sum_univ_add]

theorem digitJacobian_augmented (p : ℕ) (F : Fin e → MvPolynomial (Fin (e + q)) ℤ)
    (x : Fin (e + q) → ℤ) (u : Fin (e + q) → ZMod p) :
    digitJacobian p (augmented F) x u = join (digitJacobian p F x u) (freePart u) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i
  · simp [digitJacobian]
  · simp [digitJacobian, freePart, MvPolynomial.pderiv_X, Pi.single_apply, apply_ite]

theorem augmented_jacobian_surjective (p : ℕ)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hJ : Function.Surjective (solvedJacobian p F x)) :
    Function.Surjective (digitJacobian p (augmented F) x) := by
  intro b
  obtain ⟨u, hu⟩ := hJ (solvedPart b - digitJacobian p F x (join 0 (freePart b)))
  refine ⟨join u (freePart b), ?_⟩
  rw [digitJacobian_augmented, freePart_join]
  have hsplit : join u (freePart b) = join u 0 + join 0 (freePart b) := by
    ext i
    refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;> simp
  rw [hsplit, map_add, digitJacobian_join_zero, hu, sub_add_cancel, join_parts]

end Komorebi.PolynomialParameterSystem
