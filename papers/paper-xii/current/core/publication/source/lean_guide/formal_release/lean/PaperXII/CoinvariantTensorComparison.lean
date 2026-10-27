import PaperXII.BalancedAugmentation
import Mathlib.LinearAlgebra.TensorProduct.Tower

set_option autoImplicit false

/-! Comparison with Mathlib's tensor product when the augmented algebra is
commutative. The noncommutative construction retains its proved universal property. -/
namespace PaperXII.CoinvariantTensorComparison

open scoped TensorProduct
open BalancedAugmentation

variable {R A M : Type*} [CommRing R] [CommRing A] [Algebra R A]
  [AddCommGroup M] [Module R M] [Module A M] [IsScalarTower R A M]

/-- The coefficient-bilinear map to the ordinary tensor product over A. -/
noncomputable def ordinaryMk (ε : A →ₐ[R] R) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    R →ₗ[R] M →ₗ[R] (R ⊗[A] M) := by
  letI : Algebra A R := ε.toRingHom.toAlgebra
  letI : IsScalarTower R A R := IsScalarTower.of_algebraMap_eq' (by
    ext r
    exact (ε.commutes r).symm)
  exact (TensorProduct.mk R R M).compr₂ (TensorProduct.mapOfCompatibleSMul A R R R M)

/-- This comparison uses the original pure tensor. -/
theorem ordinaryMk_apply (ε : A →ₐ[R] R) (r : R) (m : M) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    ordinaryMk ε r m = r ⊗ₜ[A] m := rfl

/-- The ordinary tensor map has the augmentation balancing law. -/
theorem ordinaryMk_balanced (ε : A →ₐ[R] R) (r : R) (a : A) (m : M) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    ordinaryMk ε r (a • m) = ordinaryMk ε (r * ε a) m := by
  let : Algebra A R := ε.toRingHom.toAlgebra
  change r ⊗ₜ[A] (a • m) = (r * ε a) ⊗ₜ[A] m
  rw [← TensorProduct.smul_tmul]
  change (ε a * r) ⊗ₜ[A] m = (r * ε a) ⊗ₜ[A] m
  rw [mul_comm]

/-- Descend to Mathlib's tensor product. -/
noncomputable def toOrdinary (ε : A →ₐ[R] R) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    Tensor (M := M) ε →ₗ[R] (R ⊗[A] M) :=
  lift ε (ordinaryMk ε) (ordinaryMk_balanced ε)

/-- Build the inverse using the additive balanced universal property. -/
noncomputable def fromOrdinary (ε : A →ₐ[R] R) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    (R ⊗[A] M) →ₗ[R] Tensor (M := M) ε := by
  letI : Algebra A R := ε.toRingHom.toAlgebra
  let f : R →+ M →+ Tensor (M := M) ε := {
    toFun := fun r => (tensorMk ε r).toAddMonoidHom
    map_zero' := by ext m; simp
    map_add' := by intro r s; ext m; simp }
  let hf : ∀ a r m, f (a • r) m = f r (a • m) := by
    intro a r m
    change tensorMk ε (ε a * r) m = tensorMk ε r (a • m)
    rw [mul_comm]
    exact (tensorMk_balanced ε r a m).symm
  let F := TensorProduct.liftAddHom f hf
  exact {
    F with
    map_smul' := by
      intro r x
      change F (r • x) = r • F x
      induction x using TensorProduct.induction_on with
      | zero => simp
      | add x y hx hy => simp [hx, hy, smul_add]
      | tmul s m =>
        rw [TensorProduct.smul_tmul']
        change tensorMk ε (r • s) m = r • tensorMk ε s m
        rw [map_smul, LinearMap.smul_apply] }

/-- Both comparisons fix the pure tensors. -/
theorem toOrdinary_tensorMk (ε : A →ₐ[R] R) (r : R) (m : M) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    toOrdinary ε (tensorMk ε r m) = r ⊗ₜ[A] m := rfl

omit [IsScalarTower R A M] in
/-- The inverse comparison fixes pure tensors. -/
theorem fromOrdinary_tmul (ε : A →ₐ[R] R) (r : R) (m : M) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    fromOrdinary ε (r ⊗ₜ[A] m) = tensorMk ε r m := rfl

/-- The constructed balanced tensor is Mathlib's ordinary tensor in the commutative case. -/
noncomputable def ordinaryEquiv (ε : A →ₐ[R] R) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    Tensor (M := M) ε ≃ₗ[R] (R ⊗[A] M) := by
  letI : Algebra A R := ε.toRingHom.toAlgebra
  refine LinearEquiv.ofLinearMap (toOrdinary ε) (fromOrdinary ε) ?_ ?_
  · apply TensorProduct.AlgebraTensorModule.ext
    intro r m
    change toOrdinary ε (fromOrdinary ε (r ⊗ₜ[A] m)) = r ⊗ₜ[A] m
    rw [fromOrdinary_tmul, toOrdinary_tensorMk]
  · apply BalancedAugmentation.hom_ext ε
    intro r m
    change fromOrdinary ε (toOrdinary ε (tensorMk ε r m)) = tensorMk ε r m
    rw [toOrdinary_tensorMk, fromOrdinary_tmul]

/-- The full ordinary free-module recovery, with the usual tensor product. -/
noncomputable def ordinaryFreeEquiv {ι : Type*} [Fintype ι]
    (ε : A →ₐ[R] R) (b : Module.Basis ι A M) :
    letI : Algebra A R := ε.toRingHom.toAlgebra
    (R ⊗[A] M) ≃ₗ[R] (ι → R) :=
  (ordinaryEquiv ε).symm.trans (freeTensorEquiv ε b)

end PaperXII.CoinvariantTensorComparison
