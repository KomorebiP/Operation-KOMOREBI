import PaperX.PrecisionAveraging
import PaperX.AveragingCompletion

/-! Completion with a finite-group type detected beyond the group-order loss.

The allowed finite representations are first reconstructed as an actual
integral representation.  Precision averaging then proves that its integral
isomorphism type agrees with a supplied template.  The group order may be a
nonunit: it need only be nonzero and divide the specified power of the
principal-ideal generator.  Occupancy is still required at every precision.
-/
set_option autoImplicit false

namespace PaperX.PrecisionCompletion
open PaperX.RepresentationLimits PaperX.RepresentationForests
open PaperX.RepresentationTopology PaperX.PrecisionAveraging

variable {R Γ ι : Type} [CommRing R] [IsDomain R] [IsLocalRing R]
  [Group Γ] [Fintype Γ] [Fintype ι] [DecidableEq ι]
variable (π : R)
variable (C : Conditions (G := Γ) (ι := ι) (Ideal.span ({π} : Set R)))

/-- An actual isomorphism at the detecting precision, imposed on every allowed
representation at that precision.  No traces or chosen compatible witnesses
replace the invertible comparison matrix. -/
def FiniteType (e : ℕ) (τ : MatrixRep R Γ ι) : Prop :=
  ∀ σ : MatrixRep (R ⧸ (Ideal.span ({π} : Set R))^(e+1)) Γ ι, C.allowed (e + 1) σ → ∃ B : (Matrix ι ι (R ⧸ (Ideal.span ({π} : Set R))^(e+1)))ˣ,
    ∀ g, σ g * (B : Matrix ι ι (R ⧸ (Ideal.span ({π} : Set R))^(e+1))) =
      (B : Matrix ι ι (R ⧸ (Ideal.span ({π} : Set R))^(e+1))) * (reduce (Ideal.span ({π} : Set R)) τ (e+1)) g

/-- A completed integral representation has the template's integral type once
its detecting quotient has that type.  Completeness is not used in this
comparison step. -/
theorem integral_type_of_realization (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π) (htype : FiniteType π C e τ)
    (ρ : MatrixRep R Γ ι) (hρ : Realizes (Ideal.span ({π} : Set R)) C ρ) :
    ∃ P : (Matrix ι ι R)ˣ, ∀ g,
      ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g := by
  obtain ⟨B, hB⟩ := htype (reduce (Ideal.span ({π} : Set R)) ρ (e+1)) (hρ (e+1))
  obtain ⟨P, _, hP⟩ := exists_isomorphism_lift π e 1 ρ τ hΓ hdiv hπ
    (by decide) B hB
  exact ⟨P, hP⟩

/-- Every-level occupancy constructs an allowed representation of the required
integral type.  Neither invertibility of the group order nor coherent choices
of finite representations and isomorphisms are assumed. -/
theorem finite_group_completion [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π) (htype : FiniteType π C e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k)) (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes (Ideal.span ({π} : Set R)) C ρ ∧
      (∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ∧
      Ideal.Quotient.mk ((Ideal.span ({π} : Set R))^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, hρ⟩ := exists_realization (Ideal.span ({π} : Set R)) C
    (PaperX.AveragingCompletion.finite_group_levels (Ideal.span ({π} : Set R)) C finiteR) occupied
  obtain ⟨P, hP⟩ := integral_type_of_realization π C e τ hΓ hdiv hπ htype ρ hρ
  refine ⟨ρ, P, hρ, hP, ?_⟩
  let : Nontrivial (R ⧸ (Ideal.span ({π} : Set R))^1) := Ideal.Quotient.nontrivial_iff.mpr
    (by simpa using (Ideal.span_singleton_ne_top hπ))
  exact ((Matrix.isUnit_iff_isUnit_det _).mp P.isUnit).map
    (Ideal.Quotient.mk ((Ideal.span ({π} : Set R))^1)) |>.ne_zero

/-- The criterion is an equivalence for the actual allowed conditions.  A
single occupied detecting quotient alone does not imply existence of lifts. -/
theorem finite_group_completion_iff [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π) (htype : FiniteType π C e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k)) :
    (∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ), Realizes (Ideal.span ({π} : Set R)) C ρ ∧
      ∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ↔
      ∀ k, ∃ σ, C.allowed k σ := by
  constructor
  · rintro ⟨ρ, _, hρ, _⟩
    exact levels_of_realization (Ideal.span ({π} : Set R)) C ρ hρ
  · intro occupied
    obtain ⟨ρ, P, hρ, hP, _⟩ := finite_group_completion π C e τ hΓ hdiv hπ
      htype finiteR occupied
    exact ⟨ρ, P, hρ, hP⟩

/-- The constructed integral unit supplies real depth-one determinant
certificates, although identifying its integral type used depth `e+1`. -/
theorem depth_one_certificate_occupancy [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π) (htype : FiniteType π C e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k)) (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∀ k, Nonempty (PaperX.ComparisonCertificates.Node (Ideal.span ({π} : Set R)) C
      (fun _ : Unit => MonoidHom.id Γ) (fun _ : Unit => τ) (fun _ : Unit => 1) k) := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion π C e τ hΓ hdiv hπ
    htype finiteR occupied
  intro k
  exact ⟨PaperX.ComparisonCertificates.node_of_integral (Ideal.span ({π} : Set R)) C
    (fun _ : Unit => MonoidHom.id Γ) (fun _ : Unit => τ) (fun _ : Unit => 1)
    ρ (fun _ => (P : Matrix ι ι R)) hρ (fun _ => hP) (fun _ => hdet) k⟩

/-- On a finite discrete group the completed representation is continuous for
the principal-ideal adic topology on coefficients. -/
theorem continuous_finite_group_completion [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    [TopologicalSpace Γ] [DiscreteTopology Γ]
    (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π) (htype : FiniteType π C e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k)) (occupied : ∀ k, ∃ σ, C.allowed k σ) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes (Ideal.span ({π} : Set R)) C ρ ∧ AdicRepContinuous (Ideal.span ({π} : Set R)) ρ ∧
      (∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g) ∧
      Ideal.Quotient.mk ((Ideal.span ({π} : Set R))^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion π C e τ hΓ hdiv hπ
    htype finiteR occupied
  refine ⟨ρ, P, hρ, ?_, hP, hdet⟩
  let : TopologicalSpace R := (Ideal.span ({π} : Set R)).adicTopology
  exact continuous_of_discreteTopology

section Pullback
variable {G : Type} [Group G]
variable (q : G →* Γ) (D : Conditions (G := G) (ι := ι) (Ideal.span ({π} : Set R)))

/-- The same finite map is used at every precision.  Conditions may depend on
the integral frame; they are imposed on the representation actually built. -/
theorem fixed_quotient_completion [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π)
    (htype : FiniteType π (PaperX.AveragingCompletion.pullbackConditions (Ideal.span ({π} : Set R)) q D) e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k))
    (occupied : ∀ k, ∃ σ : MatrixRep (R ⧸ (Ideal.span ({π} : Set R))^k) Γ ι, D.allowed k (σ.comp q)) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes (Ideal.span ({π} : Set R)) D (ρ.comp q) ∧
      (∀ g, (ρ.comp q) g * (P : Matrix ι ι R) =
        (P : Matrix ι ι R) * (τ.comp q) g) ∧
      Ideal.Quotient.mk ((Ideal.span ({π} : Set R))^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hP, hdet⟩ := finite_group_completion π
    (PaperX.AveragingCompletion.pullbackConditions (Ideal.span ({π} : Set R)) q D) e τ hΓ hdiv hπ
    htype finiteR occupied
  exact ⟨ρ, P, hρ, fun g => hP (q g), hdet⟩

/-- A continuous map to the fixed finite discrete group yields a continuous
pullback, including when the source is an infinite topological group. -/
theorem continuous_fixed_quotient_completion [IsAdicComplete (Ideal.span ({π} : Set R)) R]
    [TopologicalSpace G] [TopologicalSpace Γ] [DiscreteTopology Γ]
    (hq : Continuous q) (e : ℕ) (τ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hπ : ¬ IsUnit π)
    (htype : FiniteType π (PaperX.AveragingCompletion.pullbackConditions (Ideal.span ({π} : Set R)) q D) e τ)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span ({π} : Set R))^k))
    (occupied : ∀ k, ∃ σ : MatrixRep (R ⧸ (Ideal.span ({π} : Set R))^k) Γ ι, D.allowed k (σ.comp q)) :
    ∃ (ρ : MatrixRep R Γ ι) (P : (Matrix ι ι R)ˣ),
      Realizes (Ideal.span ({π} : Set R)) D (ρ.comp q) ∧ AdicRepContinuous (Ideal.span ({π} : Set R)) (ρ.comp q) ∧
      (∀ g, (ρ.comp q) g * (P : Matrix ι ι R) =
        (P : Matrix ι ι R) * (τ.comp q) g) ∧
      Ideal.Quotient.mk ((Ideal.span ({π} : Set R))^1) (P : Matrix ι ι R).det ≠ 0 := by
  obtain ⟨ρ, P, hρ, hcont, hP, hdet⟩ := continuous_finite_group_completion π
    (PaperX.AveragingCompletion.pullbackConditions (Ideal.span ({π} : Set R)) q D) e τ hΓ hdiv hπ
    htype finiteR occupied
  refine ⟨ρ, P, hρ, ?_, fun g => hP (q g), hdet⟩
  let : TopologicalSpace R := (Ideal.span ({π} : Set R)).adicTopology
  exact hcont.comp hq

end Pullback
end PaperX.PrecisionCompletion
