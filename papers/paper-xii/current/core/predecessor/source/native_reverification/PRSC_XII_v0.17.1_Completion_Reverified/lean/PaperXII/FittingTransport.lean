import PaperXII.FittingBaseChange
import PaperXII.SupportTransport

noncomputable section
namespace PaperXII
open TensorProduct
variable {R S M : Type*} [CommRing R] [CommRing S] [Algebra R S]
  [AddCommGroup M] [Module R M] [Module S M] [IsScalarTower R S M]

/-- Extension of scalars cancels for an existing S-module when R → S is surjective. -/
def scalarTensorEquiv (hf : Function.Surjective (algebraMap R S)) : S ⊗[R] M ≃ₗ[S] M :=
  { ((LinearMap.id : M →ₗ[S] M).restrictScalars R).liftBaseChange S with
    invFun := fun m => (1 : S) ⊗ₜ[R] m
    left_inv := by
      intro z
      change (1 : S) ⊗ₜ[R] ((((LinearMap.id : M →ₗ[S] M).restrictScalars R).liftBaseChange S) z) = z
      induction z with
      | zero => simp
      | tmul s m =>
        obtain ⟨r,rfl⟩ := hf s
        simp only [LinearMap.liftBaseChange_tmul,LinearMap.restrictScalars_apply,
          LinearMap.id_apply,IsScalarTower.algebraMap_smul]
        rw [← TensorProduct.smul_tmul]
        simp [Algebra.smul_def]
      | add x y hx hy => simp only [map_add,TensorProduct.tmul_add,hx,hy]
    right_inv := by intro m; simp }

/-- Intrinsic Fitting transport, in fact valid for any surjective scalar map. -/
theorem fittingIdeal_transport [Module.FinitePresentation R M] [Module.FinitePresentation S M]
    (hf : Function.Surjective (algebraMap R S)) (j : ℕ) :
    Ideal.map (algebraMap R S) (fittingIdeal R M j) = fittingIdeal S M j := by
  rw [← fittingIdeal_baseChange]
  exact fittingIdeal_linearEquiv (scalarTensorEquiv hf) j

/-- Complete support and Fitting transport in Claim 7.1, under a ring identification. -/
theorem support_and_fitting_transport [Module.FinitePresentation R M] [Module.FinitePresentation S M]
    (hf : Function.Bijective (algebraMap R S)) :
    IsHomeomorph (PrimeSpectrum.comap (algebraMap R S)) ∧
    PrimeSpectrum.comap (algebraMap R S) '' Module.support S M = Module.support R M ∧
    ∀ j : ℕ, Ideal.map (algebraMap R S) (fittingIdeal R M j) = fittingIdeal S M j := by
  exact ⟨SupportTransport.spectrum_isHomeomorph hf, SupportTransport.image_support hf,
    fun j => fittingIdeal_transport hf.surjective j⟩

/-- Claim 7.1 at the manuscript hypotheses. All finite-presentation inputs are derived. -/
theorem support_and_fitting_transport_noetherian [IsNoetherianRing R] [IsNoetherianRing S]
    [Module.Finite S M] (hf : Function.Bijective (algebraMap R S)) :
    let _ : Module.Finite R S := Module.Finite.of_surjective (Algebra.linearMap R S) hf.surjective
    let _ : Module.Finite R M := Module.Finite.trans S M
    let _ : Module.FinitePresentation R M := Module.finitePresentation_of_finite R M
    let _ : Module.FinitePresentation S M := Module.finitePresentation_of_finite S M
    IsHomeomorph (PrimeSpectrum.comap (algebraMap R S)) ∧
    PrimeSpectrum.comap (algebraMap R S) '' Module.support S M = Module.support R M ∧
    ∀ j : ℕ, Ideal.map (algebraMap R S) (fittingIdeal R M j) = fittingIdeal S M j := by
  let : Module.Finite R S := Module.Finite.of_surjective (Algebra.linearMap R S) hf.surjective
  let : Module.Finite R M := Module.Finite.trans S M
  let : Module.FinitePresentation R M := Module.finitePresentation_of_finite R M
  let : Module.FinitePresentation S M := Module.finitePresentation_of_finite S M
  exact support_and_fitting_transport hf

end PaperXII
