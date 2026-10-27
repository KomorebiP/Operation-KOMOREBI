import FiniteCyclicTamePairing
import OneDimensionalPairingNormalization

/-!
# Local Tate normalization boundary

Once an arithmetic local quotient line is identified with the finite cyclic
`H¹` model, the checked trace pairing gives a canonical model functional.  Any
nonzero arithmetic Tate functional on that one-dimensional line differs from
it by one unique unit.  Thus exact sign and Frobenius normalization are not
needed for the nonvanishing detector used by auxiliary-prime selection.

This file does not construct the arithmetic comparison equivalence or prove
local Tate duality.  It isolates the remaining arithmetic input to nonvanishing
of one functional after the comparison map is supplied.
-/

namespace Komorebi.StrongArtin.LocalTateNormalizationBoundary

open CategoryTheory
open Rep
open groupCohomology
open Komorebi.StrongArtin.FiniteCyclicH1Model
open Komorebi.StrongArtin.FiniteCyclicTamePairing
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing
open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.OneDimensionalPairingNormalization

noncomputable section

universe u v

variable {k G n : Type u} {L : Type v}
  [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]
  [AddCommGroup L] [Module k L]

/-- Pull the finite-cyclic trace functional back to an arithmetic comparison
space. -/
def transportedCyclicTraceFunctional
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (P : frobeniusCentralizer F) :
    Module.Dual k L :=
  (centralizerEquivCyclicH1Dual ρ g hg F hact hN P).comp e.toLinearMap

@[simp]
theorem transportedCyclicTraceFunctional_apply
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (P : frobeniusCentralizer F) (x : L) :
    transportedCyclicTraceFunctional ρ g hg F hact hN e P x =
      centralizerEquivCyclicH1Dual ρ g hg F hact hN P (e x) := rfl


/-- Once a comparison equivalence with finite cyclic `H¹` is supplied, the
Frobenius centralizer is perfectly paired with the compared arithmetic space. -/
def centralizerEquivComparedH1Dual
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ)) :
    frobeniusCentralizer F ≃ₗ[k] Module.Dual k L :=
  (centralizerEquivCyclicH1Dual ρ g hg F hact hN).trans
    (LinearEquiv.dualMap e)

@[simp]
theorem centralizerEquivComparedH1Dual_apply
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (P : frobeniusCentralizer F) :
    centralizerEquivComparedH1Dual ρ g hg F hact hN e P =
      transportedCyclicTraceFunctional ρ g hg F hact hN e P := by
  rfl

/-- Pullback along a linear equivalence preserves nonzeroness of the model
functional. -/
theorem transportedCyclicTraceFunctional_ne_zero_iff
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (P : frobeniusCentralizer F) :
    transportedCyclicTraceFunctional ρ g hg F hact hN e P ≠ 0 ↔ P ≠ 0 := by
  constructor
  · intro h
    by_contra hP
    apply h
    simp [transportedCyclicTraceFunctional, hP]
  · intro hP hzero
    have hmodel : centralizerEquivCyclicH1Dual ρ g hg F hact hN P ≠ 0 :=
      (centralizerEquivCyclicH1Dual_ne_zero_iff ρ g hg F hact hN P).2 hP
    apply hmodel
    ext z
    obtain ⟨x, rfl⟩ := e.surjective z
    have hx := LinearMap.congr_fun hzero x
    simpa [transportedCyclicTraceFunctional] using hx

/-- On a one-dimensional arithmetic local quotient, every nonzero Tate
functional agrees with the transported cyclic trace functional up to one unique
unit. -/
theorem exists_unique_unit_trace_normalization
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (hdim : Module.finrank k L = 1)
    (P : frobeniusCentralizer F) (hP : P ≠ 0)
    (tate : Module.Dual k L) (htate : tate ≠ 0) :
    ∃! u : kˣ,
      (u : k) • transportedCyclicTraceFunctional ρ g hg F hact hN e P = tate := by
  apply exists_unique_unit_smul_eq hdim tate
    (transportedCyclicTraceFunctional ρ g hg F hact hN e P) htate
  exact (transportedCyclicTraceFunctional_ne_zero_iff ρ g hg F hact hN e P).2 hP

/-- Exact Tate normalization is irrelevant to the nonvanishing detector on a
one-dimensional local quotient. -/
theorem tate_ne_zero_iff_transported_trace_ne_zero
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (hdim : Module.finrank k L = 1)
    (P : frobeniusCentralizer F) (hP : P ≠ 0)
    (tate : Module.Dual k L) (htate : tate ≠ 0)
    (x : L) :
    tate x ≠ 0 ↔
      transportedCyclicTraceFunctional ρ g hg F hact hN e P x ≠ 0 := by
  exact nonzero_functionals_detect_same_vectors hdim tate
    (transportedCyclicTraceFunctional ρ g hg F hact hN e P) htate
    ((transportedCyclicTraceFunctional_ne_zero_iff ρ g hg F hact hN e P).2 hP) x

/-- If the comparison sends an arithmetic class to the cyclic class represented
by a matrix `X`, nonvanishing of the arithmetic Tate functional is equivalent
to nonvanishing of the checked trace probe `tr(PX)`. -/
theorem tate_ne_zero_iff_traceProbe_ne_zero
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ))
    (hdim : Module.finrank k L = 1)
    (P : frobeniusCentralizer F) (hP : P ≠ 0)
    (tate : Module.Dual k L) (htate : tate ≠ 0)
    (x : L) (X : Matrix n n k)
    (hx : e x = h1ClassOfValue (Rep.of ρ) g hg hN X) :
    tate x ≠ 0 ↔ traceProbe P.1 X ≠ 0 := by
  rw [tate_ne_zero_iff_transported_trace_ne_zero ρ g hg F hact hN e hdim P hP tate htate]
  rw [transportedCyclicTraceFunctional_apply, hx]
  rw [centralizerEquivCyclicH1Dual_apply_class]

end
end Komorebi.StrongArtin.LocalTateNormalizationBoundary

#print axioms Komorebi.StrongArtin.LocalTateNormalizationBoundary.centralizerEquivComparedH1Dual
#print axioms Komorebi.StrongArtin.LocalTateNormalizationBoundary.exists_unique_unit_trace_normalization
#print axioms Komorebi.StrongArtin.LocalTateNormalizationBoundary.tate_ne_zero_iff_traceProbe_ne_zero
