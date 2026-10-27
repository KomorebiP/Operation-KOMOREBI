import PaperX.ProfiniteSeparation

/-! Finite avoidance must be retained when two coefficient primes have different
sets of good places. This module derives overlap density from quotient coverage
that survives every finite deletion. It does not prove arithmetic Chebotarev. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CofiniteConjugacyCoverage
open PaperX.ProfiniteSeparation

variable {G X : Type*} [Group G] [TopologicalSpace G]

/-- Every finite deletion still covers every open normal quotient up to conjugacy. -/
def CofiniteQuotientCoverage (s : X → G) : Prop :=
  ∀ bad : Finset X, QuotientCoverage (fun x : {x : X // x ∉ bad} => s x)

/-- A finite exceptional set may include ramified places or a coefficient residue
characteristic. The chosen representatives themselves need not be dense. -/
theorem coverage_on_cofinite (s : X → G) (h : CofiniteQuotientCoverage s)
    (good : X → Prop) (hf : Set.Finite {x | ¬ good x}) :
    QuotientCoverage (fun x : {x : X // good x} => s x) := by
  classical
  intro H g
  obtain ⟨x, k, hx⟩ := h hf.toFinset H g
  have hg : good x.val := by
    by_contra hn
    exact x.property (hf.mem_toFinset.mpr hn)
  exact ⟨⟨x.val, hg⟩, k, hx⟩

variable [IsTopologicalGroup G] [CompactSpace G] [TotallyDisconnectedSpace G]

/-- Cofinite quotient coverage supplies the precise conjugacy density on any
cofinite permitted domain. -/
theorem dense_on_cofinite (s : X → G) (h : CofiniteQuotientCoverage s)
    (good : X → Prop) (hf : Set.Finite {x | ¬ good x}) :
    DenseRange (fun p : {x : X // good x} × G => p.2 * s p.1 * p.2⁻¹) :=
  dense_of_quotient_coverage _ (coverage_on_cofinite s h good hf)

/-- Overlap density is proved for each pair; no universal all-prime good set is
postulated. The additional finite exclusions can be chosen freely. -/
theorem dense_good_overlap (s : X → G) (h : CofiniteQuotientCoverage s)
    (good₁ good₂ : X → Prop) (h₁ : Set.Finite {x | ¬ good₁ x})
    (h₂ : Set.Finite {x | ¬ good₂ x}) (bad : Finset X) :
    DenseRange (fun p : {x : X // good₁ x ∧ good₂ x ∧ x ∉ bad} × G =>
      p.2 * s p.1 * p.2⁻¹) := by
  apply dense_on_cofinite s h
  apply ((h₁.union h₂).union bad.finite_toSet).subset
  intro x hx
  simp only [Set.mem_setOf_eq, not_and, not_not] at hx
  by_cases ha : good₁ x
  · by_cases hb : good₂ x
    · exact Or.inr (hx ha hb)
    · exact Or.inl (Or.inr hb)
  · exact Or.inl (Or.inl ha)

end PaperX.CofiniteConjugacyCoverage
