import PaperX.ComparisonCertificates
import PaperX.CertificateIsomorphisms
import PaperX.ClassCommonSpine

/-! Completion with independently meaningful local comparison equations. The
comparison matrices and their fixed detecting depths replace an uninterpreted
local-stability predicate for this particular class of conditions. Arithmetic
identification and the existence of uniform detecting bounds remain separate. -/
set_option autoImplicit false
namespace PaperX.LocalComparisonCompletion
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.RepresentationForests PaperX.ClassCompletion PaperX.ClassCommonSpine
open PaperX.CompletionAssembly PaperX.ComparisonCertificates PaperX.CertificateIsomorphisms

variable {R G ι S : Type} [CommRing R] [Group G] [TopologicalSpace G]
variable [Fintype ι] [DecidableEq ι] [Finite S]
variable {H : S → Type} [∀ s, Group (H s)]

/-- Positive finite unframed levels, occupied comparison certificates, and one
continuous representative in each allowed class give actual local conjugacies.
Finite comparison matrices need not be units. The field inclusion is injective. -/
theorem unframed_comparison_completion
    (I : Ideal R) [IsAdicComplete I R] (hI : I.FG) [Finite (R ⧸ I)]
    (C : ClassConditions (G := G) (ι := ι) I)
    (φ : ∀ s, H s →* G) (τ : ∀ s, MatrixRep R (H s) ι) (d : S → ℕ)
    (finiteC : ∀ k, 0 < k → Finite {c // C.allowed k c})
    (occupied : ∀ k, 0 < k → Nonempty (Node I (framed I C) φ τ d k))
    (continuous : ∀ k c, C.allowed k c → ∃ σ, classOf σ = c ∧ FiniteRepContinuous σ)
    {K : Type} [Field K] [TopologicalSpace K]
    (inc : R →+* K) (hinj : Function.Injective inc)
    (hinc : @Continuous R K I.adicTopology inferInstance inc) :
    ∃ (ρ : MatrixRep R G ι) (P : S → Matrix ι ι R),
      (∀ k, C.allowed k (classOf (reduce I ρ k))) ∧
      Continuous (changeCoefficients inc ρ) ∧
      ∀ s, ∃ u : (Matrix ι ι K)ˣ,
        (u : Matrix ι ι K) = (P s).map inc ∧
        conjugate u (changeCoefficients inc (τ s)) =
          changeCoefficients inc (ρ.comp (φ s)) := by
  have hf : ∀ k, Finite {ρ // (framed I C).allowed k ρ} := by
    apply positive_finite_levels
    intro k hk
    let : Finite (R ⧸ I^k) := finite_coefficients I hI k
    let : Finite {c // C.allowed k c} := finiteC k hk
    exact framed_finite I C k
  have ho : ∀ k, Nonempty (Node I (framed I C) φ τ d k) := by
    intro k
    by_cases hk : k = 0
    · subst k
      obtain ⟨x⟩ := occupied 1 (by decide)
      exact ⟨nodeTransition I (framed I C) φ τ d (Nat.zero_le 1) x⟩
    · exact occupied k (Nat.pos_of_ne_zero hk)
  obtain ⟨ρ, P, hρ, hc, hP, hd⟩ := exists_continuous_comparison_realization I
    (framed I C) φ τ d (finite_coefficients I hI) hf ho
    (fun k σ hσ => all_frames_continuous (classOf σ) (continuous k _ hσ) σ rfl)
  refine ⟨ρ, P, hρ, coefficient_change_continuous I inc hinc ρ hc, ?_⟩
  intro s
  apply exists_conjugating_unit inc hinj (ρ.comp (φ s)) (τ s) (P s) ?_ (hP s)
  intro hz
  exact hd s (by rw [hz, map_zero])

/-- The common polynomial theorem with actual local isomorphisms produced by
fixed-depth certificates. There is no generic Local or stable premise here.
The finite witnesses, their detecting bounds and the local templates are explicit. -/
theorem certified_common_spine_completion
    {Λ V E : Type} [Field E]
    (O K : Λ → Type) [∀ l, CommRing (O l)] [∀ l, Field (K l)]
    [∀ l, TopologicalSpace (K l)]
    (I : ∀ l, Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
    (hI : ∀ l, (I l).FG) [∀ l, Finite (O l ⧸ I l)]
    (C : ∀ l, ClassConditions (G := G) (ι := ι) (I l))
    (φ : ∀ s, H s →* G) (τ : ∀ l s, MatrixRep (O l) (H s) ι)
    (d : Λ → S → ℕ)
    (finiteC : ∀ l k, 0 < k → Finite {c // (C l).allowed k c})
    (occupied : ∀ l k, 0 < k →
      Nonempty (Node (I l) (framed (I l) (C l)) φ (τ l) (d l) k))
    (continuous : ∀ l k c, (C l).allowed k c →
      ∃ σ, classOf σ = c ∧ FiniteRepContinuous σ)
    (inc : ∀ l, O l →+* K l) (hinj : ∀ l, Function.Injective (inc l))
    (hinc : ∀ l, @Continuous (O l) (K l) (I l).adicTopology inferInstance (inc l))
    (emb : ∀ l, E →+* K l) (sample : V → G) (good : Λ → V → Prop)
    (P : V → Polynomial E) (localP : ∀ l, V → Polynomial (O l))
    (integrality : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (spec : ∀ l k c, (C l).allowed k c → ∀ v, good l v →
      PaperX.ClassInvariants.classCharpoly c (sample v) =
        (localP l v).map (Ideal.Quotient.mk ((I l)^k))) :
    ∃ (ρ : ∀ l, MatrixRep (O l) G ι) (Q : ∀ l, S → Matrix ι ι (O l)),
      (∀ l k, (C l).allowed k (classOf (reduce (I l) (ρ l) k))) ∧
      (∀ l, Continuous (changeCoefficients (inc l) (ρ l))) ∧
      (∀ l s, ∃ u : (Matrix ι ι (K l))ˣ,
        (u : Matrix ι ι (K l)) = (Q l s).map (inc l) ∧
        conjugate u (changeCoefficients (inc l) (τ l s)) =
          changeCoefficients (inc l) ((ρ l).comp (φ s))) ∧
      ∀ l v, good l v →
        (changeCoefficients (inc l) (ρ l) (sample v)).charpoly = (P v).map (emb l) := by
  classical
  have hx (l : Λ) := unframed_comparison_completion (I l) (hI l) (C l) φ (τ l)
    (d l) (finiteC l) (occupied l) (continuous l) (inc l) (hinj l) (hinc l)
  choose ρ Q hρ hc hQ using hx
  refine ⟨ρ, Q, hρ, hc, hQ, ?_⟩
  intro l v hv
  apply PaperX.CommonSpine.polynomial_base_change (inc l) (emb l) (ρ l)
    (sample v) (localP l v) (P v) ?_ (integrality l v hv)
  apply PaperX.CommonSpine.charpoly_detected (I l)
  intro k
  exact spec l k (classOf (reduce (I l) (ρ l) k)) (hρ l k) v hv

end PaperX.LocalComparisonCompletion
