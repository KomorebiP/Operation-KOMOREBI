import PaperXII.BalancedAugmentation
import Mathlib.Algebra.Algebra.Opposite

set_option autoImplicit false

/-! Right-module convention for M ⊗[A,ε] R, including noncommutative A.
The construction is the same full balanced quotient with its two inputs flipped.
The right action on M is represented by an Aᵐᵒᵖ-module structure. -/
namespace PaperXII.RightAugmentation

open scoped TensorProduct
open MulOpposite

variable {R A M : Type*} [CommRing R] [Ring A] [Algebra R A]
  [AddCommGroup M] [Module R M] [Module Aᵐᵒᵖ M]

/-- Augmentation on the opposite algebra. -/
def oppositeAugmentation (ε : A →ₐ[R] R) : Aᵐᵒᵖ →ₐ[R] R :=
  ε.fromOpposite fun _ _ => Commute.all _ _

/-- The right balanced tensor M ⊗[A,ε] R. -/
abbrev Tensor (ε : A →ₐ[R] R) :=
  BalancedAugmentation.Tensor (M := M) (oppositeAugmentation ε)

/-- The conventional order of the two tensor inputs. -/
def tensorMk (ε : A →ₐ[R] R) : M →ₗ[R] R →ₗ[R] Tensor (M := M) ε :=
  (BalancedAugmentation.tensorMk (oppositeAugmentation ε)).flip

/-- The full right-module balancing equation. -/
theorem tensorMk_balanced (ε : A →ₐ[R] R) (a : A) (m : M) (r : R) :
    tensorMk ε (op a • m) r = tensorMk ε m (ε a * r) := by
  change BalancedAugmentation.tensorMk (oppositeAugmentation ε) r (op a • m) =
    BalancedAugmentation.tensorMk (oppositeAugmentation ε) (ε a * r) m
  rw [BalancedAugmentation.tensorMk_balanced]
  change BalancedAugmentation.tensorMk (oppositeAugmentation ε) (r * ε a) m = _
  rw [mul_comm]

/-- Right balanced bilinear maps factor uniquely through this tensor. -/
theorem exists_unique_lift {W : Type*} [AddCommGroup W] [Module R W]
    (ε : A →ₐ[R] R) (f : M →ₗ[R] R →ₗ[R] W)
    (hf : ∀ a m r, f (op a • m) r = f m (ε a * r)) :
    ∃! F : Tensor (M := M) ε →ₗ[R] W, ∀ m r, F (tensorMk ε m r) = f m r := by
  have h : ∀ r (a : Aᵐᵒᵖ) m,
      f.flip r (a • m) = f.flip (r * oppositeAugmentation ε a) m := by
    intro r a m
    change f (a • m) r = f m (r * ε a.unop)
    simpa only [op_unop, mul_comm] using hf a.unop m r
  obtain ⟨F,hF,hunique⟩ := BalancedAugmentation.exists_unique_lift
    (oppositeAugmentation ε) f.flip h
  refine ⟨F, fun m r => hF r m, ?_⟩
  intro Q hQ
  exact hunique Q fun r m => hQ m r

/-- The actual augmentation ideal acts from the right. -/
def augmentationSMul (ε : A →ₐ[R] R) : Submodule R M :=
  Submodule.span R {v | ∃ a : A, ε a = 0 ∧ ∃ m : M, op a • m = v}

/-- Opposite-algebra notation preserves exactly the right ideal-action submodule. -/
theorem opposite_augmentationSMul (ε : A →ₐ[R] R) :
    AugmentationCoinvariants.augmentationSMul (M := M) (oppositeAugmentation ε) =
      augmentationSMul ε := by
  unfold AugmentationCoinvariants.augmentationSMul augmentationSMul
  apply congrArg (Submodule.span R)
  ext v
  constructor
  · rintro ⟨a,ha,m,hm⟩
    exact ⟨a.unop,ha,m,by simpa only [op_unop] using hm⟩
  · rintro ⟨a,ha,m,hm⟩
    exact ⟨op a,ha,m,hm⟩

/-- The right tensor is exactly M divided by its augmentation-ideal action. -/
def tensorEquivQuotient [IsScalarTower R Aᵐᵒᵖ M] (ε : A →ₐ[R] R) :
    Tensor (M := M) ε ≃ₗ[R] (M ⧸ augmentationSMul (M := M) ε) :=
  (BalancedAugmentation.tensorEquivCoinvariants (oppositeAugmentation ε)).trans
    (Submodule.quotEquivOfEq _ _
      ((AugmentationCoinvariants.relations_eq_augmentationSMul (M := M)
        (oppositeAugmentation ε)).trans (opposite_augmentationSMul (M := M) ε)))

/-- The free right-module theorem retains every basis index. -/
noncomputable def freeEquiv [IsScalarTower R Aᵐᵒᵖ M] {ι : Type*} [Fintype ι]
    (ε : A →ₐ[R] R) (b : Module.Basis ι Aᵐᵒᵖ M) :
    Tensor (M := M) ε ≃ₗ[R] (ι → R) :=
  BalancedAugmentation.freeTensorEquiv (oppositeAugmentation ε) b

/-- A recovered basis with the same index set as the original right basis. -/
noncomputable def recoveredBasis [IsScalarTower R Aᵐᵒᵖ M] {ι : Type*} [Fintype ι]
    (ε : A →ₐ[R] R) (b : Module.Basis ι Aᵐᵒᵖ M) :
    Module.Basis ι R (Tensor (M := M) ε) :=
  (Pi.basisFun R ι).map (freeEquiv ε b).symm

end PaperXII.RightAugmentation
