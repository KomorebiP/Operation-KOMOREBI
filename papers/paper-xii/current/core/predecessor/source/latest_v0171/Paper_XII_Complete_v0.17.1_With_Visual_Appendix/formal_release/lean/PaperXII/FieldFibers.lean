import PaperXII.ModuleSupport
import Mathlib.RingTheory.LocalRing.Module
import Mathlib.RingTheory.Flat.FaithfullyFlat.Basic
import Mathlib.LinearAlgebra.TensorProduct.Tower

/-! Paper XII, Theorem 7.4. The fiber is an actual tensor product. -/
namespace PaperXII.FieldFibers

open scoped TensorProduct

variable {R E M : Type*} [CommRing R] [Field E]
    [AddCommGroup M] [Module R M]

/-- The prime associated with a field-valued point. -/
def pointPrime (x : R →+* E) : PrimeSpectrum R :=
  ⟨RingHom.ker x, RingHom.ker_isPrime x⟩

/-- Every element outside the point kernel maps to a unit in the field. -/
theorem primeCompl_maps_to_units (x : R →+* E) :
    (pointPrime x).asIdeal.primeCompl ≤ (IsUnit.submonoid E).comap x := by
  intro r hr
  change IsUnit (x r)
  apply isUnit_iff_ne_zero.mpr
  exact hr

/-- A field-valued point extends to the residue field at its exact kernel. -/
noncomputable def residueFieldLift (x : R →+* E) :
    (pointPrime x).asIdeal.ResidueField →+* E :=
  Ideal.ResidueField.lift _ x le_rfl (primeCompl_maps_to_units x)

/-- The constructed residue-field embedding factors the original point. -/
theorem residueFieldLift_comp (x : R →+* E) :
    (residueFieldLift x).comp (algebraMap R (pointPrime x).asIdeal.ResidueField) = x := by
  ext r
  exact Ideal.ResidueField.lift_algebraMap (pointPrime x).asIdeal x le_rfl
    (primeCompl_maps_to_units x) r

/-- The field-fiber criterion in algebra-instance form. -/
theorem nontrivial_tensor_iff_support [Algebra R E] [Module.Finite R M] :
    Nontrivial (E ⊗[R] M) ↔ pointPrime (algebraMap R E) ∈ Module.support R M := by
  let p := pointPrime (algebraMap R E)
  let K := p.asIdeal.ResidueField
  let f : K →+* E := residueFieldLift (algebraMap R E)
  let : Algebra K E := f.toAlgebra
  let : IsScalarTower R K E := IsScalarTower.of_algebraMap_eq' (residueFieldLift_comp _).symm
  let e := TensorProduct.AlgebraTensorModule.cancelBaseChange R K E E M
  rw [← e.nontrivial_congr, Module.FaithfullyFlat.nontrivial_tensorProduct_iff_right K E]
  exact (Module.mem_support_iff_nontrivial_residueField_tensorProduct p).symm

/-- Theorem 7.4 for an arbitrary explicitly supplied ring homomorphism. -/
theorem nontrivial_fiber_iff_support (x : R →+* E) [Module.Finite R M] :
    let : Algebra R E := x.toAlgebra
    Nontrivial (E ⊗[R] M) ↔ pointPrime x ∈ Module.support R M := by
  let : Algebra R E := x.toAlgebra
  exact nontrivial_tensor_iff_support

/-- The source tensor order M ⊗ E gives the same field-fiber criterion. -/
theorem nontrivial_right_fiber_iff_support (x : R →+* E) [Module.Finite R M] :
    letI : Algebra R E := x.toAlgebra
    Nontrivial (M ⊗[R] E) ↔ pointPrime x ∈ Module.support R M := by
  let : Algebra R E := x.toAlgebra
  exact (TensorProduct.comm R M E).nontrivial_congr.trans
    (nontrivial_fiber_iff_support x)

/-- Under full support, every actual field-valued fiber is nonzero. -/
theorem nontrivial_fiber_of_fullSupport (x : R →+* E) [Module.Finite R M]
    (h : ModuleSupport.FullSupport R M) :
    letI : Algebra R E := x.toAlgebra
    Nontrivial (E ⊗[R] M) :=
  (nontrivial_fiber_iff_support x).mpr
    ((ModuleSupport.fullSupport_iff_localizations R M).mp h _)

end PaperXII.FieldFibers
