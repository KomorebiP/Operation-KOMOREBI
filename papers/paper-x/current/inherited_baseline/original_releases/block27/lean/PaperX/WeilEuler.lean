import PaperX.WeilCopies
import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff

/-! The local Euler denominator is identified with det(1-XF) on the actual
inertia-fixed monodromy kernel. No analytic L-function is constructed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilEuler
open scoped BigOperators Matrix
open Polynomial PaperX.WeilData PaperX.WeilCopies
variable {K G : Type*} [Field K] [Group G] {ν : G →* Kˣ}
variable {V : Type*} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

def eulerPolynomial (D : Datum ν V) (H : Subgroup G) [H.Normal] (φ : G) : Polynomial K :=
  (localCharpoly D H φ).reverse

theorem euler_eq_determinant (D : Datum ν V) (H : Subgroup G) [H.Normal] (φ : G)
    {J : Type*} [Fintype J] [DecidableEq J] (b : Module.Basis J K (fixedKernel D H)) :
    eulerPolynomial D H φ =
      Matrix.det (1 - (X : Polynomial K) • (LinearMap.toMatrix b b (fixedRep D H φ)).map C) := by
  unfold eulerPolynomial localCharpoly
  rw [← LinearMap.charpoly_toMatrix _ b, Matrix.reverse_charpoly]
  rfl

theorem euler_constant (D : Datum ν V) (H : Subgroup G) [H.Normal] (φ : G) :
    (eulerPolynomial D H φ).coeff 0 = 1 := by
  rw [eulerPolynomial, Polynomial.coeff_zero_reverse]
  exact (LinearMap.charpoly_monic _).leadingCoeff

theorem euler_lift_independent (D : Datum ν V) (H : Subgroup G) [H.Normal]
    (φ : G) (h : H) : eulerPolynomial D H (φ * h) = eulerPolynomial D H φ := by
  unfold eulerPolynomial
  rw [localCharpoly_lift_independent]

/-- Over a field, reversal is multiplicative, including zero polynomials. -/
def reverseHom : Polynomial K →* Polynomial K where
  toFun := Polynomial.reverse
  map_one' := by simpa using (Polynomial.reverse_C (1 : K))
  map_mul' := Polynomial.reverse_mul_of_domain

variable {I : Type*} [Fintype I] {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
variable [∀ i, FiniteDimensional K (W i)]

theorem euler_product (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal]
    (m : I → ℕ) (φ : G) :
    eulerPolynomial (copiesDatum D m) H φ = ∏ i, eulerPolynomial (D i) H φ ^ m i := by
  unfold eulerPolynomial
  rw [local_charpoly_product]
  change reverseHom (∏ i, localCharpoly (D i) H φ ^ m i) = _
  simp only [map_prod, map_pow]
  rfl

theorem common_euler_polynomial {E : Type*} [CommRing E] (σ : E →+* K)
    (D : ∀ i, Datum ν (W i)) (H : Subgroup G) [H.Normal] (m : I → ℕ) (φ : G)
    (P : I → Polynomial E) (hP : ∀ i, eulerPolynomial (D i) H φ = (P i).map σ) :
    eulerPolynomial (copiesDatum D m) H φ = (∏ i, P i ^ m i).map σ := by
  rw [euler_product]
  simp [hP, Polynomial.map_prod]

end PaperX.WeilEuler
