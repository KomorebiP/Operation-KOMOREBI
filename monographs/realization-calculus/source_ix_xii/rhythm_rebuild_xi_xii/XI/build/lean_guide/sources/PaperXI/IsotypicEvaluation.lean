import Mathlib.RingTheory.SimpleModule.Isotypic
import Mathlib.RepresentationTheory.AlgebraRepresentation.Basic
import Mathlib.LinearAlgebra.TensorProduct.Basic
import Mathlib.LinearAlgebra.Complex.FiniteDimensional
import Mathlib.Analysis.Complex.Polynomial.Basic

set_option autoImplicit false
noncomputable section

namespace PaperXI.IsotypicEvaluation

open scoped TensorProduct

variable {R W X : Type*} [Ring R] [Algebra ℂ R]
  [AddCommGroup W] [Module ℂ W] [Module R W] [IsScalarTower ℂ R W]
  [AddCommGroup X] [Module ℂ X] [Module R X] [IsScalarTower ℂ R X]

/-- Canonical evaluation on the actual space of module maps. -/
def map : W ⊗[ℂ] (W →ₗ[R] X) →ₗ[ℂ] X :=
  TensorProduct.lift
    { toFun := fun w =>
        { toFun := fun f => f w
          map_add' := fun _ _ => rfl
          map_smul' := fun _ _ => rfl }
      map_add' := by intro w v; ext f; exact f.map_add w v
      map_smul' := by intro c w; ext f; exact f.map_smul_of_tower c w }

@[simp] theorem map_tmul (w : W) (f : W →ₗ[R] X) : map (w ⊗ₜ[ℂ] f) = f w := rfl

/-- A chosen finite decomposition into copies yields the inverse of canonical evaluation. -/
theorem bijective_of_copies [IsSimpleModule R W] [FiniteDimensional ℂ W]
    {n : ℕ} (e : X ≃ₗ[R] (Fin n → W)) : Function.Bijective (map (R := R) (W := W) (X := X)) := by
  classical
  let inc (i : Fin n) : W →ₗ[R] X := e.symm.toLinearMap.comp (LinearMap.single R (fun _ : Fin n => W) i)
  let inv : X →ₗ[ℂ] W ⊗[ℂ] (W →ₗ[R] X) :=
    ∑ i : Fin n, ((TensorProduct.mk ℂ W (W →ₗ[R] X)).flip (inc i)).comp
      (((LinearMap.proj i).comp e.toLinearMap).restrictScalars ℂ)
  have hinv (x : X) : inv x = ∑ i : Fin n, (e x i) ⊗ₜ[ℂ] inc i := by
    simp [inv]
  have right : Function.RightInverse inv map := by
    intro x
    rw [hinv, map_sum]
    simp only [map_tmul, inc, LinearMap.comp_apply, LinearEquiv.coe_coe]
    rw [← map_sum]
    simp only [LinearMap.single_apply, LinearMap.sum_single_apply, e.symm_apply_apply]
  have left : Function.LeftInverse inv map := by
    intro t
    induction t using TensorProduct.induction_on with
    | zero => simp
    | add u v hu hv => simp [hu, hv]
    | tmul w f =>
      have hscalar (i : Fin n) : ∃ c : ℂ,
          (LinearMap.proj i).comp (e.toLinearMap.comp f) =
            algebraMap ℂ (Module.End R W) c := by
        obtain ⟨c, hc⟩ :=
          (IsSimpleModule.algebraMap_end_bijective_of_isAlgClosed (A := R) (V := W) ℂ).2
            ((LinearMap.proj i).comp (e.toLinearMap.comp f))
        exact ⟨c, hc.symm⟩
      choose c hc using hscalar
      have hcoord (i : Fin n) (v : W) : e (f v) i = c i • v := by
        exact congrArg (fun q : Module.End R W => q v) (hc i)
      have esmul (c : ℂ) (x : X) : e (c • x) = c • e x :=
        (e.restrictScalars ℂ).map_smul c x
      have hf : f = ∑ i : Fin n, c i • inc i := by
        ext v
        apply e.injective
        simp only [LinearMap.sum_apply, LinearMap.smul_apply, map_sum,
          esmul, inc, LinearMap.comp_apply, LinearEquiv.coe_coe,
          e.apply_symm_apply]
        have hx := LinearMap.sum_single_apply (fun _ : Fin n => W) (fun i : Fin n => e (f v) i)
        simp_rw [hcoord] at hx
        rw [show e (f v) = (fun i => c i • v) from funext (fun i => hcoord i v)]
        simpa only [LinearMap.single_apply, Pi.single_smul] using hx.symm
      rw [map_tmul, hinv]
      simp_rw [hcoord, TensorProduct.smul_tmul]
      rw [← TensorProduct.tmul_sum, ← hf]
  exact ⟨left.injective, right.surjective⟩

/-- Genuine isotypy implies bijectivity of canonical evaluation. -/
theorem bijective [IsSimpleModule R W] [FiniteDimensional ℂ W]
    [IsSemisimpleModule R X] [Module.Finite R X]
    (h : IsIsotypicOfType R X W) : Function.Bijective (map (R := R) (W := W) (X := X)) := by
  obtain ⟨n, ⟨e⟩⟩ := h.linearEquiv_fun
  exact bijective_of_copies e

/-- The isotypic evaluation equivalence, with its canonical underlying map. -/
def equiv [IsSimpleModule R W] [FiniteDimensional ℂ W]
    [IsSemisimpleModule R X] [Module.Finite R X]
    (h : IsIsotypicOfType R X W) : W ⊗[ℂ] (W →ₗ[R] X) ≃ₗ[ℂ] X :=
  LinearEquiv.ofBijective map (bijective h)

@[simp] theorem equiv_tmul [IsSimpleModule R W] [FiniteDimensional ℂ W]
    [IsSemisimpleModule R X] [Module.Finite R X]
    (h : IsIsotypicOfType R X W) (w : W) (f : W →ₗ[R] X) :
    equiv h (w ⊗ₜ[ℂ] f) = f w := rfl

end PaperXI.IsotypicEvaluation
