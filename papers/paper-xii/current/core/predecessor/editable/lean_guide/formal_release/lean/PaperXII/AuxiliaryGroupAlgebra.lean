import Mathlib.Algebra.MonoidAlgebra.Basic
import Mathlib.RingTheory.Ideal.Quotient.Operations

set_option autoImplicit false

/-! Paper XII, Proposition 5.1. Actual group-algebra transfer and augmentation.
The monoids need not be finite or commutative. -/
namespace PaperXII.AuxiliaryGroupAlgebra

open scoped MonoidAlgebra

variable {R G H K : Type*} [CommRing R] [Monoid G] [Monoid H] [Monoid K]

/-- Linear extension of the supplied homomorphism on the group basis. -/
noncomputable def transfer (q : G →* H) : R[G] →ₐ[R] R[H] :=
  MonoidAlgebra.mapDomainAlgHom R R q

/-- Transfer on every basis element, including its coefficient. -/
theorem transfer_single (q : G →* H) (g : G) (r : R) :
    transfer q (MonoidAlgebra.single g r) = MonoidAlgebra.single (q g) r := by
  simp [transfer]

/-- The induced transfer is surjective whenever the group map is. -/
theorem transfer_surjective (q : G →* H) (hq : Function.Surjective q) :
    Function.Surjective (transfer (R := R) q) := by
  intro x
  obtain ⟨y, hy⟩ := Finsupp.mapDomain_surjective hq x.coeff
  refine ⟨MonoidAlgebra.ofCoeff y, ?_⟩
  apply MonoidAlgebra.coeff_injective
  exact hy

/-- Transfer respects identity maps. -/
theorem transfer_id : transfer (R := R) (MonoidHom.id G) = AlgHom.id R R[G] := by
  exact MonoidAlgebra.mapDomainAlgHom_id

/-- Transfer respects composition. -/
theorem transfer_comp (q : G →* H) (s : H →* K) :
    transfer (R := R) (s.comp q) = (transfer s).comp (transfer q) := by
  exact MonoidAlgebra.mapDomainAlgHom_comp q s

/-- The actual augmentation sends every group element to one. -/
noncomputable def augmentation : R[G] →ₐ[R] R :=
  MonoidAlgebra.lift R R G 1

/-- Augmentation of a basis term is its coefficient. -/
theorem augmentation_single (g : G) (r : R) :
    augmentation (MonoidAlgebra.single g r) = r := by
  simp [augmentation]

/-- Augmentation is split surjective by the coefficient inclusion. -/
theorem augmentation_surjective : Function.Surjective (augmentation (R := R) (G := G)) := by
  intro r
  exact ⟨MonoidAlgebra.single 1 r, augmentation_single 1 r⟩

/-- Augmentation commutes with transfer, as an equality of algebra maps. -/
theorem augmentation_transfer (q : G →* H) :
    (augmentation (R := R)).comp (transfer q) = augmentation := by
  apply MonoidAlgebra.algHom_ext
  · intro g
    simp [AlgHom.comp_apply, transfer_single, augmentation_single]
  · ext

/-- The augmentation ideal is the kernel of the actual augmentation map. -/
noncomputable abbrev augmentationIdeal : Ideal (R[G]) :=
  RingHom.ker (augmentation (R := R) (G := G)).toRingHom

/-- Exact quotient identification, valid also for noncommutative group algebras. -/
noncomputable def augmentationQuotient :
    (R[G] ⧸ (augmentationIdeal (R := R) (G := G))) ≃ₐ[R] R :=
  Ideal.quotientKerAlgEquivOfSurjective (augmentation_surjective (R := R) (G := G))

end PaperXII.AuxiliaryGroupAlgebra
