import PaperXII.PatchingCarriers
import PaperXII.ExistingCompatibleSystems

/-!
# Five-gate completion for actual ordinary and derived carriers

Patching data produce the source carrier. A genuine support inclusion and a
compatible lift of the chosen field point produce the Hecke eigensystem.
Classicality is required only for that eigensystem. The arithmetic comparison
uses explicit continuous representations and common Frobenius polynomials.
Both existing compatible families are retained, and the attached family belongs
to the very automorphic object obtained at the distinguished point.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.FiveGateCompletion

open HeckeCarriers PatchingCarriers

variable {A R T E : Type u} [CommRing A] [CommRing R] [CommRing T]
    [Algebra A R] [Field E]

/-- The witness contains the actual degree, vector, and all induced Hecke identities. -/
structure Eigensystem (H : Carrier T) (y : T →+* E) where
  degree : H.Degree
  inRange : DegreeRange H degree
  vector : fiberSpace H y degree
  eigenvector : IsEigenvector H y degree vector

/-- The patched source point belongs to its actual finite-level support. -/
theorem patched_point_supported (D : PatchedCarrier A R) (x : R →+* E) :
    FieldFibers.pointPrime x ∈ support D.finiteCarrier := by
  rw [D.fullSupport]
  trivial

/-- The fiber gate follows from actual patching, comparison and point compatibility. -/
theorem five_gate_fiber (D : PatchedCarrier A R) (f : R →+* T) (H : Carrier T)
    (comparison : SupportComparison f D.finiteCarrier H)
    (x : R →+* E) (y : T →+* E) (hcomp : y.comp f = x) : FiberNonzero H y :=
  supportComparison_pointwise_fiber_nonzero f D.finiteCarrier H comparison x y hcomp
    (patched_point_supported D x)

/-- A compatible point gives an actual ordinary or derived eigensystem. -/
theorem five_gate_eigensystem (D : PatchedCarrier A R) (f : R →+* T) (H : Carrier T)
    (comparison : SupportComparison f D.finiteCarrier H)
    (x : R →+* E) (y : T →+* E) (hcomp : y.comp f = x) :
    Nonempty (Eigensystem H y) := by
  obtain ⟨n, hn, z, hz⟩ := supportComparison_pointwise_eigensystem
    f D.finiteCarrier H comparison x y hcomp (patched_point_supported D x)
  exact ⟨⟨n, hn, z, hz⟩⟩

/-- Select only the witness already proved to exist; no arithmetic realization is selected. -/
def chosenEigensystem (D : PatchedCarrier A R) (f : R →+* T) (H : Carrier T)
    (comparison : SupportComparison f D.finiteCarrier H)
    (x : R →+* E) (y : T →+* E) (hcomp : y.comp f = x) : Eigensystem H y :=
  Classical.choice (five_gate_eigensystem D f H comparison x y hcomp)

section Realization

open Matrix RepresentationData DenseFrobenius GaloisRealization

variable {Γ Ω ι Auto : Type u} [CharZero E]
    [TopologicalSpace E] [IsTopologicalRing E] [T2Space E]
    [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]

/-- Conditional realization at the particular constructed eigensystem.
The external input supplies occurrence and the attached Frobenius polynomials,
never an isomorphism with the universal specialization. -/
theorem five_gate_completion (D : PatchedCarrier A R) (f : R →+* T) (H : Carrier T)
    (comparison : SupportComparison f D.finiteCarrier H)
    (x : R →+* E) (y : T →+* E) (hcomp : y.comp f = x)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly = (P v).map y)
    (occurs : ∀ n : H.Degree, fiberSpace H y n → Auto → Prop)
    (attached : Auto → Γ →ₜ* GL ι E)
    (classicality :
      let w := chosenEigensystem D f H comparison x y hcomp
      ∃ π : Auto, occurs w.degree w.vector π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∀ v, good v → (attached π (frob v)).val.charpoly = (P v).map y) :
    FiberNonzero H y ∧
      let w := chosenEigensystem D f H comparison x y hcomp
      ∃ π : Auto, occurs w.degree w.vector π ∧
        Isomorphic s.rep (attached π).toMonoidHom ∧
        (Representation.IsIrreducible (representation (specialize ρR x)) →
          Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  obtain ⟨π, hocc, hsemi, hpoly⟩ := classicality
  exact ⟨five_gate_fiber D f H comparison x y hcomp, π, hocc,
    universal_pointwise_realization bn ρR x hx s (attached π) hsemi
      frob good hdense y P hρP hpoly⟩

end Realization

section Systems

open Matrix RepresentationData DenseFrobenius GaloisRealization

variable {Λ Ω Γ ι L Auto : Type u} [Field L]
    [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]
    {K : Λ → Type u} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
    [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]

/-- The compatible-system conclusion uses the family attached to the very
object produced by realization. Both existing families, their distinguished
member identities, and the common coefficient-field spine are explicit. -/
theorem five_gate_system_completion (D : PatchedCarrier A R) (f : R →+* T)
    (H : Carrier T) (comparison : SupportComparison f D.finiteCarrier H)
    (l₀ : Λ) (x : R →+* K l₀) (y : T →+* K l₀) (hcomp : y.comp f = x)
    (ρR : Γ →* GL ι R) (hx : Continuous (specialize ρR x))
    (s : Semisimplification (specialize ρR x))
    (ρ : ∀ l, Γ →ₜ* GL ι (K l))
    (hmember : (ρ l₀).toMonoidHom = specialize ρR x)
    (hsemi : ∀ l, Representation.IsSemisimpleRepresentation (representation (ρ l).toMonoidHom))
    (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (hdense : ∀ l, Dense (conjugacySaturation frob (good l)))
    (emb : ∀ l, L →+* K l) (P : Ω → Polynomial T) (Q : Ω → Polynomial L)
    (hspine : ∀ v, good l₀ v → (P v).map y = (Q v).map (emb l₀))
    (hρ : ∀ l v, good l v → (ρ l (frob v)).val.charpoly = (Q v).map (emb l))
    (occurs : ∀ n : H.Degree, fiberSpace H y n → Auto → Prop)
    (attached : Auto → Γ →ₜ* GL ι (K l₀))
    (bn : ∀ l, BrauerNesbitt (K l) Γ ι)
    (classicality :
      let w := chosenEigensystem D f H comparison x y hcomp
      ∃ π : Auto, occurs w.degree w.vector π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∃ σ : ∀ l, Γ →ₜ* GL ι (K l),
          σ l₀ = attached π ∧
          (∀ l v, good l v → (σ l (frob v)).val.charpoly = (Q v).map (emb l)) ∧
          Nonempty (∀ l, Semisimplification (σ l).toMonoidHom)) :
    FiberNonzero H y ∧
      let w := chosenEigensystem D f H comparison x y hcomp
      ∃ π : Auto, occurs w.degree w.vector π ∧
        Isomorphic s.rep (attached π).toMonoidHom ∧
        ∃ σ : ∀ l, Γ →ₜ* GL ι (K l), σ l₀ = attached π ∧
          ∃ ss : ∀ l, Semisimplification (σ l).toMonoidHom,
            Nonempty (∀ l, Representation.Equiv (representation (ρ l).toMonoidHom)
              (representation (ss l).rep)) := by
  obtain ⟨π, hocc, hatSemi, σ, hatMember, hσ, ⟨ss⟩⟩ := classicality
  have hρP : ∀ v, good l₀ v →
      (specialize ρR x (frob v)).val.charpoly = (P v).map y := by
    intro v hv
    rw [← hmember]
    exact (hρ l₀ v hv).trans (hspine v hv).symm
  have hatP : ∀ v, good l₀ v →
      (attached π (frob v)).val.charpoly = (P v).map y := by
    intro v hv
    rw [← hatMember]
    exact (hσ l₀ v hv).trans (hspine v hv).symm
  exact ⟨five_gate_fiber D f H comparison x y hcomp, π, hocc,
    (universal_pointwise_realization (bn l₀) ρR x hx s (attached π) hatSemi
      frob (good l₀) (hdense l₀) y P hρP hatP).1,
    σ, hatMember, ss,
    ExistingCompatibleSystems.system_completion ρ σ frob good hdense emb Q
      hρ hσ hsemi ss bn⟩

end Systems

end PaperXII.FiveGateCompletion
