import PaperXI.InvariantPolynomial
import Mathlib.LinearAlgebra.Dimension.Constructions

/-! Characteristic and local polynomials of finite families of varying spaces. -/
set_option autoImplicit false
noncomputable section
universe u v
namespace PaperXI.PiPolynomial
open scoped BigOperators Classical
open Polynomial PaperXI.InvariantPolynomial
variable {K : Type*} [Field K]

theorem charpoly_pi {ι : Type u} [Fintype ι] (V : ι → Type v)
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)] [∀ i, FiniteDimensional K (V i)]
    (F : ∀ i, Module.End K (V i)) :
    (LinearMap.piMap F).charpoly = ∏ i, (F i).charpoly := by
  classical
  refine Fintype.induction_empty_option (P := fun α _ =>
    ∀ (W : α → Type v) [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
      [∀ i, FiniteDimensional K (W i)] (A : ∀ i, Module.End K (W i)),
      (LinearMap.piMap A).charpoly = ∏ i, (A i).charpoly) ?_ ?_ ?_ ι V F
  · intro α β _ e ih V _ _ _ F
    let : Fintype α := Fintype.ofEquiv β e.symm
    let E := LinearEquiv.piCongrLeft K V e
    have he : E.conj (LinearMap.piMap (fun a => F (e a))) = LinearMap.piMap F := by
      apply LinearMap.ext
      intro x
      apply E.symm.injective
      rw [LinearEquiv.conj_apply_apply, E.symm_apply_apply]
      rfl
    rw [← he, LinearEquiv.charpoly_conj, ih]
    exact e.prod_comp (fun i => (F i).charpoly)
  · intro V _ _ _ F
    have hF : LinearMap.piMap F = 0 := Subsingleton.elim _ _
    simp [hF, Module.finrank_zero_of_subsingleton]
  · intro α _ ih V _ _ _ F
    let E := LinearEquiv.piOptionEquivProd K (M := V)
    have he : E.conj (LinearMap.piMap F) =
        (F none).prodMap (LinearMap.piMap (fun i => F (some i))) := by
      apply LinearMap.ext
      intro x
      apply Prod.ext <;> rfl
    rw [← LinearEquiv.charpoly_conj E, he, LinearMap.charpoly_prodMap, ih]
    simp

theorem operatorPolynomial_pi {ι : Type u} [Fintype ι] (V : ι → Type v)
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)] [∀ i, FiniteDimensional K (V i)]
    (F : ∀ i, Module.End K (V i)) :
    operatorPolynomial (LinearMap.piMap F) = ∏ i, operatorPolynomial (F i) := by
  simp only [operatorPolynomial, charpoly_pi]
  have hp (s : Finset ι) : (∏ i ∈ s, (F i).charpoly).reverse =
      ∏ i ∈ s, (F i).charpoly.reverse := by
    induction s using Finset.induction_on with
    | empty => simp [Polynomial.reverse]
    | @insert a s ha ih => simp only [Finset.prod_insert ha, Polynomial.reverse_mul_of_domain, ih]
  exact hp Finset.univ

end PaperXI.PiPolynomial
