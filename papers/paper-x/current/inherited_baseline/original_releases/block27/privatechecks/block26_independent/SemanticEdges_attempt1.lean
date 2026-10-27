import PaperX.AbsoluteGaloisRestriction
import PaperX.CyclotomicAbsoluteSamples
import PaperX.SurjectiveRepresentationPullback
import PaperX.SurjectivePullbackBoundary
open PaperX.AbsoluteGaloisRestriction PaperX.CyclotomicAbsoluteSamples
open PaperX.SurjectiveRepresentationPullback PaperX.SurjectivePullbackBoundary
open PaperX.CompletionExamples PaperX.QuadraticCharacters

-- The boundary actions are actual distinct endomorphisms of the rational line.
example : signRepresentation generator (1 : ℚ) = -1 := by
  norm_num [signRepresentation, PaperX.FiniteAvoidanceBoundary.signCharacter,
    Algebra.algebraMap_eq_smul_one, ofRoot_generator]
example : trivialRepresentation generator (1 : ℚ) = 1 := rfl

-- Every global lift acts identically after an actual factored representation.
example {L : Type*} [Field L] [Algebra ℚ L] [Normal ℚ L]
    {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K Gal(L/ℚ) V) (γ δ : Field.absoluteGaloisGroup ℚ)
    (h : restriction L γ = restriction L δ) :
    (ρ.comp (restriction L)) γ = (ρ.comp (restriction L)) δ := by
  change ρ (restriction L γ) = ρ (restriction L δ)
  exact congrArg ρ h

-- The exact isomorphism theorem accepts different underlying module types.
example {K G H V W : Type*} [Field K] [Monoid G] [Monoid H]
    [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
    (f : G →* H) (hf : Function.Surjective f)
    (ρ : Representation K H V) (τ : Representation K H W) :
    Nonempty (Representation.Equiv (ρ.comp f) (τ.comp f)) ↔ Nonempty (ρ.Equiv τ) :=
  nonempty_equiv_iff f hf ρ τ

-- One quotient covers all its points although the actual product group misses one.
example : (1, generator) ∉ Set.range quotientSamples := by
  rintro ⟨x, hx⟩
  have h := congrArg Prod.snd hx
  exact generator_ne_one h.symm

-- The zero-size separator convention is the multiplicative unit.
example : (PaperX.FiniteSeparation.sampleMatrix (fun (_ : Fin 0) (_ : ℕ) => (0 : ℚ))
    (fun i : Fin 0 => Fin.elim0 i)).det = 1 := by
  simp [PaperX.FiniteSeparation.sampleMatrix]
