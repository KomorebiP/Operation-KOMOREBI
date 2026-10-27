import PaperXII.CoinvariantTensorComparison
import PaperXII.RightAugmentation

set_option autoImplicit false

/-! Paper XII, Theorem 5.4 and Corollary 11.2.
The commutative case uses Mathlib's tensor product in the printed order.
For arbitrary groups the right-module convention uses the full balanced tensor
with its proved universal property. No restriction on the coefficient prime. -/
namespace PaperXII.Coinvariants

open scoped MonoidAlgebra TensorProduct
open AuxiliaryGroupAlgebra

variable {R G M ι : Type*} [CommRing R] [AddCommGroup M] [Fintype ι]

/-- Theorem 5.4, with both actual module isomorphisms in the displayed order. -/
theorem free_recovery [CommGroup G] [Module R M] [Module R[G] M]
    [IsScalarTower R R[G] M] (b : Module.Basis ι R[G] M) :
    let ε := augmentation (R := R) (G := G)
    letI : Algebra R[G] R := ε.toRingHom.toAlgebra
    Nonempty ((M ⧸ AugmentationCoinvariants.augmentationSMul (M := M) ε) ≃ₗ[R] (M ⊗[R[G]] R)) ∧
    Nonempty ((M ⊗[R[G]] R) ≃ₗ[R] (ι → R)) := by
  let ε := augmentation (R := R) (G := G)
  let : Algebra R[G] R := ε.toRingHom.toAlgebra
  let : IsScalarTower R R[G] R := IsScalarTower.of_algebraMap_eq' (by
    ext r
    exact (ε.commutes r).symm)
  let c := (TensorProduct.comm R[G] M R).restrictScalars R
  let q := Submodule.quotEquivOfEq _ _
    (AugmentationCoinvariants.relations_eq_augmentationSMul (M := M) ε).symm
  refine ⟨⟨q.trans ((BalancedAugmentation.tensorEquivCoinvariants ε).symm.trans
    ((CoinvariantTensorComparison.ordinaryEquiv ε).trans c.symm))⟩, ?_⟩
  exact ⟨c.trans (CoinvariantTensorComparison.ordinaryFreeEquiv ε b)⟩

/-- Corollary 11.2 for arbitrary groups and coefficient rings, hence for finite
two-groups and dyadic coefficient rings. A right basis is used for M ⊗[R[G]] R. -/
theorem dyadic_free_recovery [Group G] [Module R M] [Module (R[G])ᵐᵒᵖ M]
    [IsScalarTower R (R[G])ᵐᵒᵖ M] (b : Module.Basis ι (R[G])ᵐᵒᵖ M) :
    let ε := augmentation (R := R) (G := G)
    Nonempty (RightAugmentation.Tensor (M := M) ε ≃ₗ[R]
      (M ⧸ RightAugmentation.augmentationSMul (M := M) ε)) ∧
    Nonempty (Module.Basis ι R (RightAugmentation.Tensor (M := M) ε)) := by
  exact ⟨⟨RightAugmentation.tensorEquivQuotient _⟩,
    ⟨RightAugmentation.recoveredBasis _ b⟩⟩

end PaperXII.Coinvariants
