import PaperXII.FieldFibers
import PaperXII.SupportTransport

/-! Paper XII, Corollary 7.5 and Theorem 9.3. Actual Hecke tensor fibers and scalar actions. -/
namespace PaperXII.HeckeFibers

open scoped TensorProduct
open FieldFibers

variable {R T E H : Type*} [CommRing R] [CommRing T] [Field E]

/-- Transport a field-valued point through the inverse ring identification. -/
def transportedPoint (e : R ≃+* T) (x : R →+* E) : T →+* E :=
  x.comp e.symm.toRingHom

/-- The transported point has the prescribed pullback. -/
theorem transportedPoint_comp (e : R ≃+* T) (x : R →+* E) :
    (transportedPoint e x).comp e.toRingHom = x := by
  ext r
  simp [transportedPoint]

/-- Exact kernel transport for the field-valued point. -/
theorem comap_pointPrime (e : R ≃+* T) (x : R →+* E) :
    PrimeSpectrum.comap e.toRingHom (pointPrime (transportedPoint e x)) = pointPrime x := by
  ext r
  change x (e.symm (e r)) = 0 ↔ x r = 0
  rw [e.symm_apply_apply]

variable [AddCommGroup H] [Module T H]

/-- Corollary 7.5 with the Hecke point explicitly constructed as x ∘ e⁻¹. -/
theorem supported_hecke_fiber [Algebra R T] [Module R H] [IsScalarTower R T H]
    [Module.Finite T H] (e : R ≃ₐ[R] T) (x : R →+* E)
    (hx : pointPrime x ∈ Module.support R H) :
    letI : Algebra T E := (transportedPoint e.toRingEquiv x).toAlgebra
    Nontrivial (E ⊗[T] H) := by
  apply (nontrivial_fiber_iff_support (M := H) (transportedPoint e.toRingEquiv x)).mpr
  have he : e.toRingHom = algebraMap R T := by
    ext r
    exact e.commutes r
  have hf : Function.Surjective (algebraMap R T) := by
    rw [← he]
    exact e.surjective
  apply (SupportTransport.mem_support_comap_iff hf _).mp
  rw [← he, comap_pointPrime]
  exact hx

/-- The tensor relation giving the scalar action on pure tensors. -/
theorem pure_tensor_hecke_action (y : T →+* E) (t : T) (a : E) (h : H) :
    letI : Algebra T E := y.toAlgebra
    a ⊗ₜ[T] (t • h) = y t • (a ⊗ₜ[T] h) := by
  let : Algebra T E := y.toAlgebra
  rw [← TensorProduct.smul_tmul, TensorProduct.smul_tmul']
  rfl

/-- Base change of the actual operator h ↦ t • h on the Hecke module. -/
noncomputable def heckeOperator (y : T →+* E) (t : T) :
    letI : Algebra T E := y.toAlgebra
    Module.End E (E ⊗[T] H) :=
  letI : Algebra T E := y.toAlgebra
  (t • (LinearMap.id : H →ₗ[T] H)).baseChange E

/-- The induced Hecke endomorphism equals scalar multiplication on the whole fiber. -/
theorem heckeOperator_eq_scalar (y : T →+* E) (t : T) :
    letI : Algebra T E := y.toAlgebra
    heckeOperator (H := H) y t = y t • (LinearMap.id : Module.End E (E ⊗[T] H)) := by
  let : Algebra T E := y.toAlgebra
  ext h
  change (1 : E) ⊗ₜ[T] (t • h) = y t • ((1 : E) ⊗ₜ[T] h)
  exact pure_tensor_hecke_action y t 1 h

/-- Every element of the actual tensor fiber has the prescribed scalar Hecke action. -/
theorem hecke_action_is_scalar (y : T →+* E) (t : T) :
    letI : Algebra T E := y.toAlgebra
    ∀ z : E ⊗[T] H, t • z = y t • z := by
  let : Algebra T E := y.toAlgebra
  intro z
  exact (IsScalarTower.algebraMap_smul E t z).symm

/-- Theorem 9.3: a supported point gives a nonzero fiber, with its full scalar action. -/
theorem support_gives_hecke_eigensystem [Algebra R T] [Module R H]
    [IsScalarTower R T H] [Module.Finite T H]
    (e : R ≃ₐ[R] T) (x : R →+* E) (hx : pointPrime x ∈ Module.support R H) :
    letI : Algebra T E := (transportedPoint e.toRingEquiv x).toAlgebra
    Nontrivial (E ⊗[T] H) ∧
      ∀ t : T, heckeOperator (H := H) (transportedPoint e.toRingEquiv x) t =
        transportedPoint e.toRingEquiv x t • (LinearMap.id : Module.End E (E ⊗[T] H)) := by
  exact ⟨supported_hecke_fiber e x hx, fun t ↦ heckeOperator_eq_scalar _ t⟩

end PaperXII.HeckeFibers
