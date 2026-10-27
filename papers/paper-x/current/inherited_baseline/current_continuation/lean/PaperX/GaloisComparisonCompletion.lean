import PaperX.LocalComparisonCompletion
import Mathlib.FieldTheory.AbsoluteGaloisGroup
import Mathlib.NumberTheory.Padics.PadicNumbers

/-! An actual arithmetic specialization: restrictions from the absolute Galois
group of Q to the absolute Galois groups of Q_p. The chosen maps are induced
by the actual field embeddings and choices of algebraic-closure embeddings.
Exact local Galois representation isomorphism is the conclusion; no Hodge--Tate
or Weil--Deligne interpretation is built into an arbitrary predicate. -/
set_option autoImplicit false
namespace PaperX.GaloisComparisonCompletion
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.ClassCompletion PaperX.ComparisonCertificates

/-- The actual continuous homomorphism induced by Q→Q_p. -/
noncomputable def localRestriction (p : ℕ) [Fact p.Prime] :
    Field.absoluteGaloisGroup ℚ_[p] →ₜ* Field.absoluteGaloisGroup ℚ :=
  Field.absoluteGaloisGroup.map (algebraMap ℚ ℚ_[p])

/-- The actual local/global groups instantiate certificate completion. The
templates prescribe entire local actions, a stronger condition than a packet label.
Nonemptiness and the fixed determinant bounds are substantive explicit inputs. -/
theorem rational_galois_comparison_completion
    {R K ι S : Type} [CommRing R] [Field K] [TopologicalSpace K]
    [Fintype ι] [DecidableEq ι] [Finite S]
    (p : S → ℕ) [∀ s, Fact (p s).Prime]
    (I : Ideal R) [IsAdicComplete I R] (hI : I.FG) [Finite (R ⧸ I)]
    (C : ClassConditions (G := Field.absoluteGaloisGroup ℚ) (ι := ι) I)
    (τ : ∀ s, MatrixRep R (Field.absoluteGaloisGroup ℚ_[p s]) ι)
    (d : S → ℕ)
    (finiteC : ∀ k, 0 < k → Finite {c // C.allowed k c})
    (occupied : ∀ k, 0 < k → Nonempty
      (Node I (framed I C) (fun s => (localRestriction (p s)).toMonoidHom) τ d k))
    (continuous : ∀ k c, C.allowed k c →
      ∃ σ, classOf σ = c ∧ FiniteRepContinuous σ)
    (inc : R →+* K) (hinj : Function.Injective inc)
    (hinc : @Continuous R K I.adicTopology inferInstance inc) :
    ∃ (ρ : MatrixRep R (Field.absoluteGaloisGroup ℚ) ι)
      (P : S → Matrix ι ι R),
      (∀ k, C.allowed k (classOf (reduce I ρ k))) ∧
      Continuous (changeCoefficients inc ρ) ∧
      ∀ s, ∃ u : (Matrix ι ι K)ˣ,
        (u : Matrix ι ι K) = (P s).map inc ∧
        conjugate u (changeCoefficients inc (τ s)) =
          changeCoefficients inc (ρ.comp (localRestriction (p s)).toMonoidHom) :=
  PaperX.LocalComparisonCompletion.unframed_comparison_completion I hI C
    (fun s => (localRestriction (p s)).toMonoidHom) τ d finiteC occupied continuous
    inc hinj hinc

end PaperX.GaloisComparisonCompletion
