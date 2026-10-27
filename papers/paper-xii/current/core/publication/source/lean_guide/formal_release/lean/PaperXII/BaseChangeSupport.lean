import PaperXII.FieldFibers
import Mathlib.RingTheory.TensorProduct.Finite
import Mathlib.RingTheory.Spectrum.Prime.RingHom

/-! Supporting theorems: arbitrary scalar extension of a finite module.
These strengthen the support tools, but do not claim the paper's Fitting identities. -/
namespace PaperXII.BaseChangeSupport

open scoped TensorProduct
open FieldFibers ModuleSupport

variable {R S M : Type*} [CommRing R] [CommRing S] [Algebra R S]
    [AddCommGroup M] [Module R M] [Module.Finite R M]

/-- Pointwise support under arbitrary scalar extension of a finite module. -/
theorem mem_support_baseChange_iff (q : PrimeSpectrum S) :
    q ∈ Module.support S (S ⊗[R] M) ↔
      PrimeSpectrum.comap (algebraMap R S) q ∈ Module.support R M := by
  let K := q.asIdeal.ResidueField
  let e := TensorProduct.AlgebraTensorModule.cancelBaseChange R S K K M
  rw [Module.mem_support_iff_nontrivial_residueField_tensorProduct q, e.nontrivial_congr]
  have hp : pointPrime (algebraMap R K) = PrimeSpectrum.comap (algebraMap R S) q := by
    ext r
    change algebraMap R K r = 0 ↔ algebraMap R S r ∈ q.asIdeal
    rw [IsScalarTower.algebraMap_apply R S K, Ideal.algebraMap_residueField_eq_zero]
  rw [← hp]
  exact nontrivial_tensor_iff_support

/-- Support of scalar extension is the inverse image of the original support. -/
theorem support_baseChange :
    Module.support S (S ⊗[R] M) =
      PrimeSpectrum.comap (algebraMap R S) ⁻¹' Module.support R M := by
  ext q
  exact mem_support_baseChange_iff q

/-- Full support survives any commutative scalar extension. -/
theorem fullSupport_baseChange (h : FullSupport R M) : FullSupport S (S ⊗[R] M) := by
  unfold FullSupport at h ⊢
  rw [support_baseChange, h, Set.preimage_univ]

/-- Near faithfulness survives scalar extension when both rings are Noetherian. -/
theorem nearlyFaithful_baseChange [IsNoetherianRing R] [IsNoetherianRing S]
    (h : NearlyFaithful R M) : NearlyFaithful S (S ⊗[R] M) :=
  (nearlyFaithful_iff_fullSupport S _).mpr
    (fullSupport_baseChange ((nearlyFaithful_iff_fullSupport R M).mp h))

end PaperXII.BaseChangeSupport
