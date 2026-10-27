import PaperX.QuadraticGalois
import PaperX.GaloisComparisonCompletion

/-! The fixed quadratic global quotient restricted to actual absolute Galois
groups of characteristic-zero coefficient fields. The field restriction is
Mathlib's actual map, including its chosen algebraic-closure embedding. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticLocalGalois
open PaperX.ArithmeticCertificateExample PaperX.QuadraticGalois
open PaperX.CompletionExamples

variable (K : Type*) [Field K] [CharZero K]

def restriction : Field.absoluteGaloisGroup K →ₜ* Field.absoluteGaloisGroup ℚ :=
  Field.absoluteGaloisGroup.map (algebraMap ℚ K)

def closureEmbedding : Qbar →ₐ[ℚ] AlgebraicClosure K := IsAlgClosed.lift

def localRoot : AlgebraicClosure K := closureEmbedding K imaginary

def localQuotient : Field.absoluteGaloisGroup K →* C2 :=
  quotientMap.comp (restriction K).toMonoidHom

theorem localRoot_sq : localRoot K ^ 2 = -1 := by
  rw [localRoot, ← map_pow, imaginary_sq, map_neg, map_one]

theorem restriction_commutes (σ : Field.absoluteGaloisGroup K) (x : Qbar) :
    closureEmbedding K ((show GQ from restriction K σ) x) =
      (show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ) (closureEmbedding K x) := by
  let g : Qbar →ₐ[ℚ] AlgebraicClosure K := IsAlgClosed.lift
  let : Algebra Qbar (AlgebraicClosure K) := g.toAlgebra
  exact AlgEquiv.restrictNormal_commutes
    ((show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ).restrictScalars ℚ)
    Qbar x

theorem localQuotient_eq_one_iff (σ : Field.absoluteGaloisGroup K) :
    localQuotient K σ = 1 ↔
      (show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ) (localRoot K) = localRoot K := by
  change quotientMap (restriction K σ) = 1 ↔ _
  rw [quotientMap_eq_one_iff]
  constructor
  · intro h
    exact (restriction_commutes K σ imaginary).symm.trans (congrArg (closureEmbedding K) h)
  · intro h
    apply (closureEmbedding K).injective
    exact (restriction_commutes K σ imaginary).trans h

/-- The chosen image is rational over the local field exactly when minus one is a square. -/
theorem localRoot_mem_range_iff :
    localRoot K ∈ Set.range (algebraMap K (AlgebraicClosure K)) ↔
      ∃ x : K, x ^ 2 = -1 := by
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨x, (algebraMap K (AlgebraicClosure K)).injective ?_⟩
    rw [map_pow, hx, localRoot_sq, map_neg, map_one]
  · rintro ⟨x, hx⟩
    have hs : localRoot K ^ 2 = (algebraMap K (AlgebraicClosure K) x) ^ 2 := by
      rw [localRoot_sq, ← map_pow, hx, map_neg, map_one]
    rcases sq_eq_sq_iff_eq_or_eq_neg.mp hs with h | h
    · exact ⟨x, h.symm⟩
    · exact ⟨-x, by rw [map_neg]; exact h.symm⟩

/-- A theorem about the actual field-induced Galois restriction map. -/
theorem localQuotient_trivial_iff :
    localQuotient K = 1 ↔ ∃ x : K, x ^ 2 = -1 := by
  rw [← localRoot_mem_range_iff K,
    InfiniteGalois.mem_range_algebraMap_iff_fixed (localRoot K)]
  constructor
  · intro h σ
    exact (localQuotient_eq_one_iff K σ).mp
      (congrArg (fun f : Field.absoluteGaloisGroup K →* C2 => f σ) h)
  · intro h
    apply MonoidHom.ext
    intro σ
    exact (localQuotient_eq_one_iff K σ).mpr (h σ)

theorem localQuotient_hits_generator
    (h : ¬ ∃ x : K, x ^ 2 = -1) :
    ∃ σ : Field.absoluteGaloisGroup K, localQuotient K σ = generator := by
  by_contra hn
  apply h
  apply (localQuotient_trivial_iff K).mp
  apply MonoidHom.ext
  intro σ
  have hc : ∀ c : C2, c = 1 ∨ c = generator := by decide +kernel
  rcases hc (localQuotient K σ) with hσ | hσ
  · exact hσ
  · exact False.elim (hn ⟨σ, hσ⟩)

theorem localQuotient_surjective
    (h : ¬ ∃ x : K, x ^ 2 = -1) : Function.Surjective (localQuotient K) := by
  intro c
  have hc : ∀ c : C2, c = 1 ∨ c = generator := by decide +kernel
  rcases hc c with rfl | rfl
  · exact ⟨1, map_one _⟩
  · exact localQuotient_hits_generator K h

theorem localQuotient_continuous : Continuous (localQuotient K) :=
  absoluteQuadraticCharacter_continuous.comp (restriction K).continuous

/-- Fixing one square root is equivalent to fixing any other choice. -/
theorem localQuotient_eq_one_iff_fixed_root (y : AlgebraicClosure K)
    (hy : y ^ 2 = -1) (σ : Field.absoluteGaloisGroup K) :
    localQuotient K σ = 1 ↔
      (show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ) y = y := by
  have hs : y ^ 2 = localRoot K ^ 2 := by rw [hy, localRoot_sq]
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp hs with h | h
  · rw [h]
    exact localQuotient_eq_one_iff K σ
  · rw [h]
    have hn : (show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ)
        (-localRoot K) =
        -(show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ) (localRoot K) :=
      map_neg (show AlgebraicClosure K ≃ₐ[K] AlgebraicClosure K from σ) _
    rw [hn, neg_inj]
    exact localQuotient_eq_one_iff K σ

theorem restriction_padic (p : ℕ) [Fact p.Prime] :
    restriction ℚ_[p] = GaloisComparisonCompletion.localRestriction p := rfl

end PaperX.QuadraticLocalGalois
