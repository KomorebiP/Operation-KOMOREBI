import PaperX.SystemCompletion

/-! Actual polynomial coefficients survive reconstruction and coefficient change.
The common coefficient field is not mapped into an integral DVR: local integral
polynomials and embeddings into local fields are supplied separately. Good-place
predicates are explicit and may depend on the coefficient index. No Chebotarev,
Galois realization, or Hodge--Tate theorem is introduced as an axiom. -/
set_option autoImplicit false
namespace PaperX.CommonSpine
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
open PaperX.SystemCompletion
variable {R G ι : Type*} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R)

/-- Separatedness alone identifies prescribed integral characteristic polynomials. -/
theorem charpoly_detected [IsHausdorff I R] (ρ : MatrixRep R G ι) (g : G)
    (P : Polynomial R)
    (h : ∀ k, (reduce I ρ k g).charpoly = P.map (Ideal.Quotient.mk (I^k))) :
    (ρ g).charpoly = P := by
  apply Polynomial.ext
  intro n
  apply scalar_ext I
  intro k
  have H : (Polynomial.map (Ideal.Quotient.mk (I^k)) (ρ g).charpoly).coeff n =
      (P.map (Ideal.Quotient.mk (I^k))).coeff n := by
    rw [← Matrix.charpoly_map]
    exact congrArg (fun p : Polynomial (R ⧸ I^k) => p.coeff n) (h k)
  simpa using H

/-- Specifying Frobenius polynomials at all allowed reductions determines the
whole polynomial, rather than just the trace or a bounded coefficient sample. -/
theorem realization_has_spine {R G ι V : Type} [CommRing R] [Group G]
    [Fintype ι] [DecidableEq ι] (I : Ideal R) [IsHausdorff I R]
    (C : Conditions (G := G) (ι := ι) I) (ρ : MatrixRep R G ι) (hρ : Realizes I C ρ)
    (sample : V → G) (good : V → Prop) (P : V → Polynomial R)
    (spec : ∀ k τ, C.allowed k τ → ∀ v, good v →
      (τ (sample v)).charpoly = (P v).map (Ideal.Quotient.mk (I^k))) :
    ∀ v, good v → (ρ (sample v)).charpoly = P v := by
  intro v hv
  apply charpoly_detected I ρ (sample v) (P v)
  intro k
  exact spec k _ (hρ k) v hv

/-- Base change realizes the common polynomial over the local field. -/
theorem polynomial_base_change {K E : Type*} [CommRing K] [CommRing E]
    (inc : R →+* K) (emb : E →+* K) (ρ : MatrixRep R G ι) (g : G)
    (localP : Polynomial R) (commonP : Polynomial E)
    (hlocal : (ρ g).charpoly = localP)
    (hcommon : localP.map inc = commonP.map emb) :
    (changeCoefficients inc ρ g).charpoly = commonP.map emb := by
  change ((ρ g).map inc).charpoly = _
  rw [Matrix.charpoly_map, hlocal, hcommon]

/-- Common-spine completion at the representation-and-polynomial level. Local
arithmetic conditions are only those justified by the supplied stability input.
All good-place restrictions, local integrality, and coefficient embeddings remain
visible hypotheses. This is not an unconditional strict compatibility theorem. -/
theorem common_spine_completion
    {Λ G ι V E : Type} [Group G] [TopologicalSpace G] [Fintype ι] [DecidableEq ι]
    [Field E] (O K : Λ → Type) [∀ l, CommRing (O l)] [∀ l, Field (K l)]
    (I : (l : Λ) → Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
    (C : (l : Λ) → Conditions (G := G) (ι := ι) (I l))
    (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
    (occupied : ∀ l k, ∃ ρ, (C l).allowed k ρ)
    (continuous : ∀ l k ρ, (C l).allowed k ρ → FiniteRepContinuous ρ)
    (Local : (l : Λ) → MatrixRep (O l) G ι → Prop)
    (stable : ∀ l ρ, Realizes (I l) (C l) ρ → Local l ρ)
    (inc : (l : Λ) → O l →+* K l) (emb : (l : Λ) → E →+* K l)
    (sample : V → G) (good : Λ → V → Prop)
    (P : V → Polynomial E) (localP : (l : Λ) → V → Polynomial (O l))
    (integrality : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (spec : ∀ l k τ, (C l).allowed k τ → ∀ v, good l v →
      (τ (sample v)).charpoly = (localP l v).map (Ideal.Quotient.mk ((I l)^k))) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      SystemRealizes O I C ρ ∧
      (∀ l, AdicRepContinuous (I l) (ρ l) ∧ Local l (ρ l)) ∧
      ∀ l v, good l v →
        (changeCoefficients (inc l) (ρ l) (sample v)).charpoly = (P v).map (emb l) := by
  obtain ⟨ρ,hρ,hc⟩ := continuous_system_completion O I C finite occupied continuous Local stable
  refine ⟨ρ,hρ,hc,?_⟩
  intro l v hv
  exact polynomial_base_change (inc l) (emb l) (ρ l) (sample v) (localP l v) (P v)
    (realization_has_spine (I l) (C l) (ρ l) (hρ l) sample (good l) (localP l)
      (spec l) v hv) (integrality l v hv)

end PaperX.CommonSpine
