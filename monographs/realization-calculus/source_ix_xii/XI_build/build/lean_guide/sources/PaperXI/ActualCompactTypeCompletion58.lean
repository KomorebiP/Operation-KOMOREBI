import PaperXI.ActualNormalizerTypeExtension58
import PaperXI.CompactTypeTensorNormalizer58

/-!
# Same-factor actual compact type extension

The literal tensor action retains the prescribed Heisenberg factor. Its
irreducibility and smoothness, and the whole-type normalizer intertwiner, are
constructed. Actual embedded-field arithmetic supplies cyclic freeness.
Normalization of the actual compact subgroup, quotient-triviality, and one
nonzero first-factor intertwiner remain explicit type-theoretic inputs.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCompactTypeCompletion58

open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualEmbeddedUniformizer58 NormalizerExtensionInducing58

section FirstFactor
variable {J W : Type*} [Group J] [AddCommGroup W] [Module ℂ W]

/-- Irreducibility on a subgroup already implies irreducibility of the extension. -/
theorem firstFactor_irreducible (N : Subgroup J) (κ : Representation ℂ J W)
    [IsIrreducible (κ.comp N.subtype)] : IsIrreducible κ := by
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space (κ.comp N.subtype)
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  apply RepresentationStability.eq_bot_or_top (κ.comp N.subtype) S
  intro n w hw
  exact hS (n : J) w hw
end FirstFactor

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K]
  [Field E] [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]
  [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (ι : E →ₐ[K] Matrix n n K)
variable (J : Subgroup (GeneralLinearGroup n K))
  (ht : embeddedUniformizer K E n ι ∈ Subgroup.normalizer (J : Set (GeneralLinearGroup n K)))
variable {Q W U : Type*} [Group Q] [Finite Q]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  [AddCommGroup U] [Module ℂ U]
variable (N : Subgroup J) (q : J →* Q) (hN : N ≤ q.ker)
  (κ : Representation ℂ J W) (σ : Representation ℂ Q U)

include hN in
/-- The prescribed compact first factor is retained in one smooth irreducible
tensor action and its actual noncentral uniformizer extension. No whole-type
irreducibility, whole-type intertwiner or extension is supplied as an input. -/
theorem completed
    (hK : Continuous (algebraMap K E))
    (hcompact : IsCompact (J : Set (GeneralLinearGroup n K)))
    (hopen : IsOpen (J : Set (GeneralLinearGroup n K)))
    (hNopen : IsOpen (N : Set J)) (hq : Function.Surjective q)
    (hqa : ∀ j, q (conjugation J (embeddedUniformizer K E n ι) ht j) = q j)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ]
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (T : IntertwiningMap κ
      (κ.comp (conjugation J (embeddedUniformizer K E n ι) ht).toMonoidHom))
    (hT : T ≠ 0) :
    FiniteDimensional ℂ (W ⊗[ℂ] U) ∧
    IsIrreducible (CompactTypeTensor58.action q κ σ) ∧
    SmoothDegreeQuotient.IsSmooth (CompactTypeTensor58.action q κ σ) ∧
    (CompactTypeTensor58.action q κ σ).comp N.subtype =
      Representation.tprod (κ.comp N.subtype) (1 : Representation ℂ N U) ∧
    (∃ Λ : Representation ℂ (extendedSubgroup J (embeddedUniformizer K E n ι) ht)
        (W ⊗[ℂ] U),
      (∀ j : J, Λ (subgroupInclusion J (embeddedUniformizer K E n ι) ht j) =
        CompactTypeTensor58.action q κ σ j) ∧
      (∀ w u, Λ (generator J (embeddedUniformizer K E n ι) ht) (w ⊗ₜ[ℂ] u) =
        T w ⊗ₜ[ℂ] u) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ) := by
  let t := embeddedUniformizer K E n ι
  let a := conjugation J t ht
  let : IsIrreducible κ := firstFactor_irreducible N κ
  let e := T.ofBijective (intertwiner_bijective J t ht κ T hT)
  have hA : ∀ j w, e.toLinearEquiv (κ j w) = κ (a j) (e.toLinearEquiv w) := by
    intro j w
    exact LinearMap.congr_fun (e.isIntertwining' j) w
  let eTensor := CompactTypeTensorNormalizer58.normalizerEquiv q κ σ a hqa e.toLinearEquiv hA
  have hfree := embeddedUniformizer_free_of_algebraMap K E n ι hK J hcompact
  obtain ⟨hi, hf, hs, hr⟩ := CompactTypeTensor58.completed N q hN κ σ hq hNopen hκ
  let : IsIrreducible (CompactTypeTensor58.action q κ σ) := hi
  refine ⟨hf, hi, hs, hr,
    extensionOfEquiv J t ht (CompactTypeTensor58.action q κ σ) eTensor hfree, ?_, ?_, ?_, ?_⟩
  · intro j
    exact extensionOfEquiv_restrict J t ht (CompactTypeTensor58.action q κ σ) eTensor hfree j
  · intro w u
    rw [extensionOfEquiv_generator]
    rfl
  · exact extendedRepresentation_irreducible J t ht (CompactTypeTensor58.action q κ σ) _ _ hfree
  · exact extendedRepresentation_smooth J t ht (CompactTypeTensor58.action q κ σ) _ _ hfree hopen hs

end PaperXI.ActualCompactTypeCompletion58
