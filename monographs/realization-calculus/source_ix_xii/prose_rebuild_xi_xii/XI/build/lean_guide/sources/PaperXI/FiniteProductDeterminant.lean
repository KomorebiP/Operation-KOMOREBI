import Mathlib.LinearAlgebra.Determinant
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Data.Fintype.Option

/-! Determinants of actual finite products with varying coordinate spaces. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteProductDeterminant
open scoped BigOperators Classical

universe u v w
variable {k : Type w} [Field k]

def map {ι : Type u} {V : ι → Type v} [∀ i, AddCommGroup (V i)]
    [∀ i, Module k (V i)] (f : ∀ i, Module.End k (V i)) :
    Module.End k (∀ i, V i) :=
  LinearMap.pi fun i => (f i).comp (LinearMap.proj i)

@[simp] theorem map_apply {ι : Type u} {V : ι → Type v}
    [∀ i, AddCommGroup (V i)] [∀ i, Module k (V i)]
    (f : ∀ i, Module.End k (V i)) (x : ∀ i, V i) (i : ι) :
    map f x i = f i (x i) := rfl

theorem determinant (ι : Type u) [Fintype ι] (V : ι → Type v)
    [∀ i, AddCommGroup (V i)] [∀ i, Module k (V i)]
    [∀ i, FiniteDimensional k (V i)] (f : ∀ i, Module.End k (V i)) :
    (map f).det = ∏ i, (f i).det := by
  classical
  revert V
  refine Fintype.induction_empty_option
    (P := fun α _ => ∀ (W : α → Type v) [∀ i, AddCommGroup (W i)]
      [∀ i, Module k (W i)] [∀ i, FiniteDimensional k (W i)]
      (a : ∀ i, Module.End k (W i)), (map a).det = ∏ i, (a i).det)
    ?_ ?_ ?_ ι
  · intro α β _ e ih V _ _ _ f
    let : Fintype α := Fintype.ofEquiv β e.symm
    let E := LinearEquiv.piCongrLeft k V e
    have hmap : E.toLinearMap ∘ₗ map (fun i => f (e i)) ∘ₗ E.symm.toLinearMap =
        map f := by
      apply LinearMap.ext
      intro x
      apply E.symm.injective
      change E.symm (E (map (fun i => f (e i)) (E.symm x))) = E.symm (map f x)
      rw [E.symm_apply_apply]
      rfl
    rw [← hmap, LinearMap.det_conj, ih]
    exact e.prod_comp (fun i => (f i).det)
  · intro V _ _ _ f
    rw [LinearMap.det_eq_one_of_subsingleton]
    simp
  · intro α _ ih V _ _ _ f
    let E := LinearEquiv.piOptionEquivProd k (M := V)
    have hmap : E.toLinearMap ∘ₗ map f ∘ₗ E.symm.toLinearMap =
        LinearMap.prodMap (f none) (map (fun i => f (some i))) := by
      apply LinearMap.ext
      intro x
      apply Prod.ext
      · rfl
      · rfl
    have hd := LinearMap.det_conj (map f) E
    rw [hmap, LinearMap.det_prodMap, ih] at hd
    rw [← hd, Fintype.prod_option]

end PaperXI.FiniteProductDeterminant
