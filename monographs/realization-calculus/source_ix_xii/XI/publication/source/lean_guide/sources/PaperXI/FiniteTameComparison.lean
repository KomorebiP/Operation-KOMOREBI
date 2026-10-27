import PaperXI.InducedTameProfile
import PaperXI.TameGaussNaturality
import PaperXI.TameTensorSource

/-! Proposition 16.1: an explicit finite comparison package on genuine induced
representations. The local-Weil and standard Artin/epsilon-factor identifications
are intentionally NOT fields of this finite record and are not proved here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteTameComparison
open Polynomial PaperXI.CyclicInduced
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
open scoped Classical BigOperators TensorProduct

/-- A finite output record. The conductor fields are the declared finite sums,
not the standard arithmetic Swan/Artin conductors. -/
@[ext] structure Observables (M : ℕ) where
  dimension : ℕ
  inertiaSupport : Set (ZMod M)
  cyclePolynomial : ℂ[X]
  localPolynomial : ℂ[X]
  finiteSwan : ℚ
  finiteArtin : ℚ
  residuePhase : ℂ

variable {G k : Type*} [Group G] [Field k] [Fintype k]
variable {M : ℕ} [NeZero M]
variable (δ : G →* Multiplicative ℤ) (ι : Multiplicative (ZMod M) →* G)
variable (φ : G) (hφ : δ φ = Multiplicative.ofAdd (1 : ℤ))
variable (n : ℕ) [NeZero n] (ξ : TameDegree.degreeSubgroup δ n →* ℂˣ)
variable (q : (ZMod M)ˣ) (j : ZMod M)
variable (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
  ι (Multiplicative.ofAdd (q : ZMod M)))
variable (hξ : ∀ a : ZMod M,
  (ξ (InducedTameProfile.inertiaInDegree δ ι n (Multiplicative.ofAdd a)) : ℂ) =
    ZMod.stdAddChar (j * a))
variable [FiniteDimensional ℂ (DegreeIndSpace δ n ξ)]

/-- Observations use actual spaces, operators, and character sums. -/
def observed (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) : Observables M where
  dimension := Module.finrank ℂ (DegreeIndSpace δ n ξ)
  inertiaSupport := {b | PacketTransport.packet (tameRestriction (degreeInduced δ n ξ) ι) b ≠ ⊥}
  cyclePolynomial := (degreeInduced δ n ξ φ).charpoly
  localPolynomial := InvariantPolynomial.localPolynomial
    (tameRestriction (degreeInduced δ n ξ) ι) (actionEquiv (degreeInduced δ n ξ) φ) q
    (geometric_relation (degreeInduced δ n ξ) ι φ q hrel)
  finiteSwan := TameConductor.finiteSwan (degreeInduced δ n ξ) S J w
  finiteArtin := TameConductor.finiteArtin (degreeInduced δ n ξ) ι S J w
  residuePhase := GaussCharacters.phase χ ψ

/-- Prediction from packet coordinates and the declared residue/additive characters. -/
def fromCoordinates (c : ℂˣ) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) : Observables M where
  dimension := n
  inertiaSupport := {b | ∃ i : Fin n, ((q ^ (i : ℕ) : (ZMod M)ˣ) : ZMod M) * j = b}
  cyclePolynomial := X ^ n - C (c : ℂ)
  localPolynomial := if j = 0 then 1 - C (c : ℂ) * X ^ n else 1
  finiteSwan := 0
  finiteArtin := if j = 0 then 0 else n
  residuePhase := (∑ x : kˣ, (χ x : ℂ) * ψ x) / (Real.sqrt (Fintype.card k) : ℂ)

include hφ hξ in
/-- The complete finite record is derived, not included as input data. -/
theorem observations_eq_coordinates (P : Subgroup G)
    (hP : ∀ g ∈ P, ∀ v, degreeInduced δ n ξ g v = v)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (hJP : ∀ r ∈ S, J r ≤ P) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    observed δ ι φ n ξ q hrel S J w χ ψ =
      fromCoordinates n q j (InducedCycleInvariants.returnScalar δ φ hφ n ξ) χ ψ := by
  apply Observables.ext
  · exact InducedCycleInvariants.dimension δ φ hφ n ξ
  · apply Set.ext
    intro b
    exact InducedTameProfile.inertia_support δ ι φ hφ n ξ q j hrel hξ b
  · exact (InducedCycleInvariants.cycle_invariants δ φ hφ n ξ).1
  · exact InducedTameProfile.local_polynomial δ ι φ hφ n ξ q j hrel hξ
  · exact (InducedTameProfile.finite_conductors δ ι φ hφ n ξ q j hrel hξ P hP S J w hJP).1
  · exact (InducedTameProfile.finite_conductors δ ι φ hφ n ξ q j hrel hξ P hP S J w hJP).2
  · rfl

/-- The tensor part of the package is an actual constructed equivalence of
representations; it is not encoded merely as matching dimensions. -/
def interactionEquiv (m : ℕ) [NeZero m] (η : TameDegree.degreeSubgroup δ m →* ℂˣ) :
    Representation.Equiv ((degreeInduced δ n ξ).tprod (degreeInduced δ m η))
      (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
        degreeInduced δ (Nat.lcm n m) (TameTensorSource.interactionCharacter δ φ n m ξ η i))) :=
  TameTensorSource.decomposition δ φ n m ξ η hφ

include hφ hξ in
/-- Source-facing finite package with all six advertised components. The final
residue magnitude includes the trivial-character exception. Its interpretation
as the arithmetic package still requires the separate local-field attachment. -/
theorem finite_comparison_package (P : Subgroup G)
    (hP : ∀ g ∈ P, ∀ v, degreeInduced δ n ξ g v = v)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (hJP : ∀ r ∈ S, J r ≤ P)
    (m : ℕ) [NeZero m] (η : TameDegree.degreeSubgroup δ m →* ℂˣ)
    (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) (hψ : ψ ≠ 1) :
    observed δ ι φ n ξ q hrel S J w χ ψ =
      fromCoordinates n q j (InducedCycleInvariants.returnScalar δ φ hφ n ξ) χ ψ ∧
    Nonempty (Representation.Equiv ((degreeInduced δ n ξ).tprod (degreeInduced δ m η))
      (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
        degreeInduced δ (Nat.lcm n m) (TameTensorSource.interactionCharacter δ φ n m ξ η i)))) ∧
    (∑ i : Fin (Nat.gcd n m), Module.finrank ℂ (DegreeIndSpace δ (Nat.lcm n m)
      (TameTensorSource.interactionCharacter δ φ n m ξ η i))) = n*m ∧
    ‖GaussCharacters.phase χ ψ‖ =
      if χ = 1 then (Real.sqrt (Fintype.card k))⁻¹ else 1 := by
  exact ⟨observations_eq_coordinates δ ι φ hφ n ξ q j hrel hξ P hP S J w hJP χ ψ,
    ⟨interactionEquiv δ φ hφ n ξ m η⟩,
    TameTensorSource.interaction_dimension_sum δ φ n m ξ η hφ,
    TameGaussNaturality.phase_norm_cases χ hψ⟩

end PaperXI.FiniteTameComparison
