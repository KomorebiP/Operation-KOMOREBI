import PaperX.FiniteGroupAveraging
import PaperX.ComparisonCertificates
import Mathlib.RingTheory.LocalRing.Quotient

/-! Completion with a prescribed tame finite-group representation type.

Finite coefficient quotients and a finite source make the actual allowed
representation sets finite.  Residual conjugacy to the supplied template is
lifted by averaging after reconstruction.  Consequently no separate comparison
certificate occupancy or determinant-depth hypothesis is needed in this class.
The arbitrary allowed conditions may depend on the chosen integral frame.
-/
set_option autoImplicit false

namespace PaperX.AveragingCompletion
open PaperX.RepresentationLimits PaperX.RepresentationForests
open PaperX.RepresentationTopology PaperX.FiniteGroupAveraging

variable {R Γ ι : Type} [CommRing R] [Group Γ] [Fintype Γ]
  [Fintype ι] [DecidableEq ι]
variable (I : Ideal R) (C : Conditions (G := Γ) (ι := ι) I)

/-- For a finite source group, finite coefficients do imply finite actual
allowed representation sets.  No finite-generation proxy is used. -/
theorem finite_group_levels (finiteR : ∀ k, Finite (R ⧸ I^k)) :
    ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) Γ ι // C.allowed k ρ} := by
  intro k
  let : Finite (R ⧸ I^k) := finiteR k
  exact Finite.of_injective (fun ρ => (ρ.val : Γ → Matrix ι ι (R ⧸ I^k)))
    (fun _ _ h => Subtype.ext (MonoidHom.ext (congrFun h)))

/-- The first positive quotient remains nontrivial and its quotient map reflects
units.  In the maximal-ideal specialization this is the residue field map. -/
theorem first_quotient_local [IsLocalRing R] (hI : I ≠ ⊤) :
    IsLocalHom (Ideal.Quotient.mk (I^1)) := by
  let : Nontrivial (R ⧸ I^1) := Ideal.Quotient.nontrivial_iff.mpr (by simpa using hI)
  exact IsLocalHom.of_surjective _ Ideal.Quotient.mk_surjective

/-- Exact residual equivalence is imposed only at the first positive precision.
The witness is an actual invertible matrix, not equality of traces. -/
def ResidualType (τ : MatrixRep R Γ ι) : Prop :=
  ∀ σ, C.allowed 1 σ → ∃ B : (Matrix ι ι (R ⧸ I^1))ˣ,
    ∀ g, σ g * (B : Matrix ι ι (R ⧸ I^1)) =
      (B : Matrix ι ι (R ⧸ I^1)) * (reduce I τ 1) g

/-- Averaging proves preservation of the specified finite-group type.  This is
the missing local implication proved from residual type and a unit group order,
rather than supplied as an arbitrary limit-stability hypothesis. -/
theorem integral_type_of_realization [IsLocalRing R] (hI : I ≠ ⊤)
    (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I C τ) (ρ : MatrixRep R Γ ι) (hρ : Realizes I C ρ) :
    ∃ P : (Matrix ι ι R)ˣ, ∀ g,
      ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g := by
  let : IsLocalHom (Ideal.Quotient.mk (I^1)) := first_quotient_local I hI
  obtain ⟨B, hB⟩ := hres (reduce I ρ 1) (hρ 1)
  obtain ⟨P, _, hP⟩ := exists_isomorphism_lift (Ideal.Quotient.mk (I^1))
    Ideal.Quotient.mk_surjective ρ τ hΓ B hB
  exact ⟨P, hP⟩

/-- Every-precision occupancy constructs a representation of the required
integral isomorphism type.  The detecting depth is a conclusion, not an input. -/
theorem finite_group_completion [IsLocalRing R] [IsAdicComplete I R]
    (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I C τ) (finiteR : ∀ k, Finite (R ⧸ I^k))
    (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes I C ρ ∧
      (∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ∧
      Ideal.Quotient.mk (I^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, hρ⟩ := exists_realization I C (finite_group_levels I C finiteR) occupied
  obtain ⟨P, hP⟩ := integral_type_of_realization I C hI τ hΓ hres ρ hρ
  refine ⟨ρ, P, hρ, hP, ?_⟩
  let : Nontrivial (R ⧸ I^1) := Ideal.Quotient.nontrivial_iff.mpr (by simpa using hI)
  exact ((Matrix.isUnit_iff_isUnit_det _).mp P.isUnit).map
    (Ideal.Quotient.mk (I^1)) |>.ne_zero

/-- The finite criterion is an equivalence, with no surjectivity assumption on
the reductions between allowed levels. -/
theorem finite_group_completion_iff [IsLocalRing R] [IsAdicComplete I R]
    (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I C τ) (finiteR : ∀ k, Finite (R ⧸ I^k)) :
    (∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ), Realizes I C ρ ∧
      ∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ↔
      ∀ k, ∃ σ, C.allowed k σ := by
  constructor
  · rintro ⟨ρ, _, hρ, _⟩
    exact levels_of_realization I C ρ hρ
  · intro occupied
    obtain ⟨ρ, P, hρ, hP, _⟩ := finite_group_completion I C hI τ hΓ hres finiteR occupied
    exact ⟨ρ, P, hρ, hP⟩

/-- This class supplies the actual depth-one certificates used in Block 15.
The matrices in the nodes are reductions of the constructed integral unit. -/
theorem depth_one_certificate_occupancy [IsLocalRing R] [IsAdicComplete I R]
    (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I C τ) (finiteR : ∀ k, Finite (R ⧸ I^k))
    (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∀ k, Nonempty (PaperX.ComparisonCertificates.Node I C
      (fun _ : Unit => MonoidHom.id Γ) (fun _ : Unit => τ) (fun _ : Unit => 1) k) := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion I C hI τ hΓ hres finiteR occupied
  intro k
  exact ⟨PaperX.ComparisonCertificates.node_of_integral I C
    (fun _ : Unit => MonoidHom.id Γ) (fun _ : Unit => τ) (fun _ : Unit => 1)
    ρ (fun _ => (P : Matrix ι ι R)) hρ (fun _ => hP) (fun _ => hdet) k⟩

/-- A finite group with its discrete topology gives an actual continuous
completion; continuity is not inferred for an arbitrary source topology. -/
theorem continuous_finite_group_completion [IsLocalRing R] [IsAdicComplete I R]
    [TopologicalSpace Γ] [DiscreteTopology Γ]
    (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I C τ) (finiteR : ∀ k, Finite (R ⧸ I^k))
    (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes I C ρ ∧ AdicRepContinuous I ρ ∧
      (∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ∧
      Ideal.Quotient.mk (I^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion I C hI τ hΓ hres finiteR occupied
  refine ⟨ρ, P, hρ, ?_, hP, hdet⟩
  let : TopologicalSpace R := I.adicTopology
  exact continuous_of_discreteTopology

section Pullback
variable {G : Type} [Group G]
variable (q : G →* Γ) (D : Conditions (G := G) (ι := ι) I)

/-- Conditions on an arbitrary group are tested on representations pulled back
from one fixed finite group map.  The map does not vary with precision. -/
def pullbackConditions : Conditions (G := Γ) (ι := ι) I where
  allowed k σ := D.allowed k (σ.comp q)
  downward h σ hσ := D.downward h (σ.comp q) hσ

/-- Fixed finite-image completion for an arbitrary source group.  Independently
occupied finite levels need only admit factorizations through the fixed map;
compatible choices of those factors are not assumed. -/
theorem fixed_quotient_completion [IsLocalRing R] [IsAdicComplete I R]
    (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I (pullbackConditions I q D) τ)
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (occupied : ∀ k, ∃ σ : MatrixRep (R ⧸ I^k) Γ ι, D.allowed k (σ.comp q)) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes I D (ρ.comp q) ∧
      (∀ g, (ρ.comp q) g * (P : Matrix ι ι R) =
        (P : Matrix ι ι R) * (τ.comp q) g) ∧
      Ideal.Quotient.mk (I^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion I (pullbackConditions I q D)
    hI τ hΓ hres finiteR occupied
  exact ⟨ρ, P, hρ, fun g => hP (q g), hdet⟩

/-- The reconstructed pullback is continuous for a continuous map to the finite
discrete group, including infinite profinite or absolute Galois sources when
that map is actually supplied. -/
theorem continuous_fixed_quotient_completion [IsLocalRing R] [IsAdicComplete I R]
    [TopologicalSpace G] [TopologicalSpace Γ] [DiscreteTopology Γ]
    (hq : Continuous q) (hI : I ≠ ⊤) (τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R))
    (hres : ResidualType I (pullbackConditions I q D) τ)
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (occupied : ∀ k, ∃ σ : MatrixRep (R ⧸ I^k) Γ ι, D.allowed k (σ.comp q)) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes I D (ρ.comp q) ∧ AdicRepContinuous I (ρ.comp q) ∧
      (∀ g, (ρ.comp q) g * (P : Matrix ι ι R) =
        (P : Matrix ι ι R) * (τ.comp q) g) ∧
      Ideal.Quotient.mk (I^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hcont, hP, hdet⟩ := continuous_finite_group_completion I
    (pullbackConditions I q D) hI τ hΓ hres finiteR occupied
  refine ⟨ρ, P, hρ, ?_, fun g => hP (q g), hdet⟩
  let : TopologicalSpace R := I.adicTopology
  exact hcont.comp hq

end Pullback

end PaperX.AveragingCompletion
