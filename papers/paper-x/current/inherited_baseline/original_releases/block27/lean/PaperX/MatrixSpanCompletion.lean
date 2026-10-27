import PaperX.SplitTemplateRigidity
import PaperX.ComparisonCertificates

/-! A fixed full-span rational representation type is preserved by completion
from integral finite-condition approximants. Existence of those approximants
is explicit; arbitrary torsion representations are not assumed to lift. -/
set_option autoImplicit false
namespace PaperX.MatrixSpanCompletion
open PaperX.RepresentationLimits PaperX.RepresentationForests
open PaperX.RepresentationClasses PaperX.ComparisonCertificates
variable {R G ι K : Type} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
  [Group G] [Fintype ι] [DecidableEq ι] [Field K] [Algebra R K] [IsFractionRing R K]
variable (π : R) (hπ : Irreducible π)
variable (C : Conditions (G := G) (ι := ι) (Ideal.span {π}))
variable (τ : MatrixRep R G ι)

/-- Ordinary finite-condition approximation in the field-isomorphism class.
Each precision may use a different integral representation and comparison. -/
def Approximation : Prop := ∀ k, ∃ ρ : MatrixRep R G ι,
    Conjugate (changeCoefficients (algebraMap R K) τ)
      (changeCoefficients (algebraMap R K) ρ) ∧
    C.allowed k (reduce (Ideal.span {π}) ρ k)

include hπ

/-- The fixed bound derived from the template produces augmented finite nodes
without any assumed uniform determinant certificate. -/
theorem certificate_levels_from_approximation
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤)
    (occupied : Approximation (K := K) π C τ) :
    ∃ c : ℕ, ∀ k, Nonempty (Node (Ideal.span {π}) C
      (fun _ : Unit => MonoidHom.id G) (fun _ : Unit => τ)
      (fun _ : Unit => c * Fintype.card ι + 1) k) := by
  obtain ⟨c, hc⟩ := MatrixSpanBound.uniform_detector_for_conjugates (K := K) τ π hπ hspan
  refine ⟨c, fun k => ?_⟩
  obtain ⟨ρ, hρ, ha⟩ := occupied k
  obtain ⟨P, hP, hd⟩ := hc ρ hρ
  refine ⟨{ rep := reduce (Ideal.span {π}) ρ k
            allowed := ha
            comparison := fun _ => P.map (Ideal.Quotient.mk ((Ideal.span {π})^k))
            intertwines := ?_
            detected := ?_ }⟩
  · intro s g
    change (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^k)) *
      P.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
      P.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) *
      (τ g).map (Ideal.Quotient.mk ((Ideal.span {π})^k))
    simpa only [Matrix.map_mul] using
      congrArg (fun A => A.map (Ideal.Quotient.mk ((Ideal.span {π})^k))) (hP g)
  · intro s hs
    change Ideal.Quotient.factorPow (Ideal.span {π}) hs
      ((Ideal.Quotient.mk ((Ideal.span {π})^k)).mapMatrix P).det ≠ 0
    rw [← RingHom.map_det, Ideal.Quotient.factor_mk]
    change ((Ideal.Quotient.mk ((Ideal.span {π}) ^ (c * Fintype.card ι + 1))).mapMatrix P).det ≠ 0 at hd
    rw [← RingHom.map_det] at hd
    exact hd

/-- Completion preserves this actual rational isomorphism type. The proof
constructs finite witnesses with the uniform bound and invokes the existing
simultaneous certificate theorem. -/
theorem full_span_completion [IsAdicComplete (Ideal.span {π}) R]
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span {π})^k))
    (finiteC : ∀ k, Finite {ρ : MatrixRep (R ⧸ (Ideal.span {π})^k) G ι // C.allowed k ρ})
    (occupied : Approximation (K := K) π C τ) :
    ∃ ρ : MatrixRep R G ι, Realizes (Ideal.span {π}) C ρ ∧
      Conjugate (changeCoefficients (algebraMap R K) τ)
        (changeCoefficients (algebraMap R K) ρ) := by
  obtain ⟨c, hc⟩ := certificate_levels_from_approximation π hπ C τ hspan occupied
  obtain ⟨ρ, P, hρ, hP, hd⟩ := exists_comparison_realization (Ideal.span {π}) C
    (fun _ : Unit => MonoidHom.id G) (fun _ : Unit => τ)
    (fun _ : Unit => c * Fintype.card ι + 1) finiteR finiteC hc
  refine ⟨ρ, hρ, ?_⟩
  apply PaperX.CertificateIsomorphisms.conjugate_of_finite_certificate (Ideal.span {π})
    (algebraMap R K) (IsFractionRing.injective R K) ρ τ (P ())
    (c * Fintype.card ι + 1)
  · change ((Ideal.Quotient.mk ((Ideal.span {π}) ^ (c * Fintype.card ι + 1))).mapMatrix (P ())).det ≠ 0
    rw [← RingHom.map_det]
    exact hd ()
  · exact hP ()

end PaperX.MatrixSpanCompletion
