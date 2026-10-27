import PaperXI.FiniteTameComparison
import PaperXI.RamifiedUnramifiedQuotient
import PaperXI.ActualUnramifiedBaseChange
import PaperXI.RamificationPolyphase

/-!
# Actual tame-monomial attachment to the local-field ramification calculus

The parameter in this file is constructed by genuine degree-subgroup induction
on the actual residue--Frobenius pullback.  Its finite packet invariants are
then attached to the literal lower ramification filtration and its conventional
Artin--Swan sums.  No automorphic representation, local class field theory, or
automorphic induction theorem is encoded as data in this Lean module.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.ActualMonomialLocalGlobal

open scoped Classical BigOperators Polynomial
open Polynomial
open PaperXI.ResidueWeil
open PaperXI.CyclicInduced
open PaperXI.TameOrbitTransitivity
open PaperXI.ValuationConductor
open PaperXI.ValuationRamification
open PaperXI.RamificationPolyphase

section InvariantRange

variable {G H V : Type*} [Group G] [Group H]
variable [AddCommGroup V] [Module ℂ V]

/-- Invariant spaces depend only on the image of the acting homomorphism. -/
theorem invariants_eq_of_range_eq
    (ρ : Representation ℂ G V) (f : H →* G) (S : Subgroup G)
    (hrange : f.range = S) :
    Representation.invariants (ρ.comp f) =
      Representation.invariants (ρ.comp S.subtype) := by
  ext v
  constructor
  · intro hv g
    have hg : g.val ∈ f.range := by simpa [hrange] using g.property
    obtain ⟨h, hh⟩ := hg
    have hfix := hv h
    change ρ (f h) v = v at hfix
    simpa [hh] using hfix
  · intro hv h
    have hf : f h ∈ S := by
      rw [← hrange]
      exact ⟨h, rfl⟩
    exact hv ⟨f h, hf⟩

end InvariantRange

section ActualTameParameter

variable (R D : Type*) [CommRing R] [IsLocalRing R]
  [Group D] [Fintype D] [MulSemiringAction D R]
variable (F : RingAut (IsLocalRing.ResidueField R))

abbrev RamifiedWeil := Pullback (residue R D) F
abbrev actualDegree : RamifiedWeil R D F →* Multiplicative ℤ :=
  degree (residue R D) F

variable {M n : ℕ} [NeZero M] [NeZero n]
variable (ι : Multiplicative (ZMod M) →* RamifiedWeil R D F)
variable (hιrange : ι.range = (actualDegree R D F).ker)
variable (φ : RamifiedWeil R D F)
variable (hφ : actualDegree R D F φ = Multiplicative.ofAdd (1 : ℤ))
variable (ξ : TameDegree.degreeSubgroup (actualDegree R D F) n →* ℂˣ)
variable (q : (ZMod M)ˣ) (j : ZMod M)
variable (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
  ι (Multiplicative.ofAdd (q : ZMod M)))
variable (hξ : ∀ a : ZMod M,
  (ξ (InducedTameProfile.inertiaInDegree (actualDegree R D F) ι n
    (Multiplicative.ofAdd a)) : ℂ) = ZMod.stdAddChar (j * a))

/-- The actual monomial parameter is constructed by induction from the degree-
`n` subgroup of the literal residue--Frobenius pullback. -/
abbrev actualParameter : Representation ℂ (RamifiedWeil R D F)
    (DegreeIndSpace (actualDegree R D F) n ξ) :=
  degreeInduced (actualDegree R D F) n ξ

/-- The finite cyclic inertia model is required to have exactly the same image
as the degree-zero inertia subgroup of the actual pullback. -/
theorem fixed_zero_eq_tame_invariants :
    fixed R D F (actualParameter R D F n ξ) 0 =
      (tameRestriction (actualParameter R D F n ξ) ι).invariants := by
  rw [fixed_zero]
  exact (invariants_eq_of_range_eq (actualParameter R D F n ξ) ι
    (actualDegree R D F).ker hιrange).symm

/-- The Block 43 projector is literally the projector onto the actual fixed
space of the constructed parameter. -/
theorem actual_depthProjector_range (i : ℕ) :
    LinearMap.range (depthProjector (R := R) (D := D) (F := F)
      (ρ := actualParameter R D F n ξ) i) =
      fixed R D F (actualParameter R D F n ξ) i :=
  depthProjector_range (R := R) (D := D) (F := F)
    (ρ := actualParameter R D F n ξ) i

/-- The actual ramification-detail channel is the newly fixed lower-depth
subspace with the preceding coarse component removed. -/
theorem actual_detailProjector_range (i : ℕ) :
    LinearMap.range (detailProjector (R := R) (D := D) (F := F)
      (ρ := actualParameter R D F n ξ) i) =
      fixed R D F (actualParameter R D F n ξ) (i + 1) ⊓
        LinearMap.ker (depthProjector (R := R) (D := D) (F := F)
          (ρ := actualParameter R D F n ξ) i) :=
  detailProjector_range (R := R) (D := D) (F := F)
    (ρ := actualParameter R D F n ξ) i

/-- Image of an actual lower ramification group in the ramified Weil pullback. -/
def lowerImage (i : ℕ) : Subgroup (RamifiedWeil R D F) :=
  (lift R D F i).range

/-- Rational form of the conventional lower-numbering weight. -/
def lowerWeight (i : ℕ) : ℚ :=
  (Nat.card (lower R D i) : ℚ) / (Nat.card (lower R D 0) : ℚ)

/-- Finite tame Swan expression formed from the actual lower-group images. -/
def packetSwan (S : Finset ℕ) : ℚ :=
  TameConductor.finiteSwan (actualParameter R D F n ξ) S
    (fun r => lowerImage R D F (r + 1))
    (fun r => lowerWeight R D (r + 1))

/-- Finite tame Artin expression formed from the actual inertia map and actual
lower-group images. -/
def packetArtin (S : Finset ℕ) : ℚ :=
  TameConductor.finiteArtin (actualParameter R D F n ξ) ι S
    (fun r => lowerImage R D F (r + 1))
    (fun r => lowerWeight R D (r + 1))

/-- The actual first lower group acts trivially in the declared tame class. -/
variable (htame : ∀ g : lower R D 1,
  actualParameter R D F n ξ (lift R D F 1 g) = 1)

include htame in
/-- Every positive lower-group image acts trivially. -/
theorem positive_lowerImage_trivial (r : ℕ) :
    ∀ g ∈ lowerImage R D F (r + 1), ∀ v,
      actualParameter R D F n ξ g v = v := by
  intro g hg v
  obtain ⟨h, rfl⟩ := hg
  let h1 : lower R D 1 :=
    RamificationPolyphase.lowerInclusion (R := R) (D := D)
      (Nat.le_add_left 1 r) h
  have hact := htame h1
  have hlift : lift R D F 1 h1 = lift R D F (r + 1) h :=
    RamificationPolyphase.lift_lowerInclusion (R := R) (D := D)
      (F := F) (Nat.le_add_left 1 r) h
  rw [hlift] at hact
  exact LinearMap.congr_fun hact v

include htame in
/-- The packet Swan expression vanishes because it uses the actual positive
lower-group images and those act trivially. -/
theorem packetSwan_eq_zero (S : Finset ℕ) :
    packetSwan R D F n ξ S = 0 := by
  unfold packetSwan TameConductor.finiteSwan
  apply Finset.sum_eq_zero
  intro r hr
  rw [TameConductor.fixedCodimension_zero_of_trivial_on
    (actualParameter R D F n ξ) (lowerImage R D F (r + 1))
    (positive_lowerImage_trivial R D F n ξ htame r)]
  simp

include htame in
/-- The standard lower-numbering Swan conductor of the actual parameter
vanishes in the declared tame class. -/
theorem standardSwan_eq_zero :
    swan R D F (actualParameter R D F n ξ) = 0 :=
  tame_swan_zero R D F (actualParameter R D F n ξ) htame

variable [FiniteDimensional ℂ (DegreeIndSpace (actualDegree R D F) n ξ)]

include hφ hrel hξ htame in
/-- The conventional Artin conductor of the actual lower filtration is the
packet codimension: zero in the unramified label and `n` otherwise. -/
theorem standardArtin_eq_coordinates :
    artin R D F (actualParameter R D F n ξ) =
      if j = 0 then 0 else (n : ℝ) := by
  unfold artin codimension
  rw [standardSwan_eq_zero R D F n ξ htame, add_zero,
    fixed_zero_eq_tame_invariants R D F ι hιrange n ξ,
    InducedCycleInvariants.dimension (actualDegree R D F) φ hφ n ξ,
    InducedTameProfile.invariant_dimension (actualDegree R D F) ι φ hφ n ξ
      q j hrel hξ]
  split_ifs <;> simp

include hφ hrel hξ htame in
/-- The finite packet Artin expression built from the actual lower-group images
has the same coordinate value. -/
theorem packetArtin_eq_coordinates (S : Finset ℕ) :
    packetArtin R D F ι n ξ S = if j = 0 then 0 else (n : ℚ) := by
  unfold packetArtin TameConductor.finiteArtin
  rw [packetSwan_eq_zero R D F n ξ htame S,
    InducedCycleInvariants.dimension (actualDegree R D F) φ hφ n ξ,
    InducedTameProfile.invariant_dimension (actualDegree R D F) ι φ hφ n ξ
      q j hrel hξ]
  split_ifs <;> simp

include hφ hrel hξ htame in
/-- In the tame monomial class the finite packet expression is literally the
standard lower-numbering Artin conductor after scalar extension to `ℝ`. -/
theorem packetArtin_eq_standardArtin (S : Finset ℕ) :
    ((packetArtin R D F ι n ξ S : ℚ) : ℝ) =
      artin R D F (actualParameter R D F n ξ) := by
  rw [packetArtin_eq_coordinates R D F ι φ hφ n ξ q j hrel hξ htame S,
    standardArtin_eq_coordinates R D F ι hιrange φ hφ n ξ q j hrel hξ htame]
  split_ifs <;> simp

include htame in
/-- The finite packet Swan expression and the standard Swan conductor agree. -/
theorem packetSwan_eq_standardSwan (S : Finset ℕ) :
    ((packetSwan R D F n ξ S : ℚ) : ℝ) =
      swan R D F (actualParameter R D F n ξ) := by
  rw [packetSwan_eq_zero R D F n ξ htame S,
    standardSwan_eq_zero R D F n ξ htame]
  simp

/-- Equality of the finite cyclic invariant space with the actual zeroth lower
fixed space, packaged as a linear equivalence for Frobenius transport. -/
def tameInvariantsEquivFixedZero :
    (tameRestriction (actualParameter R D F n ξ) ι).invariants ≃ₗ[ℂ]
      fixed R D F (actualParameter R D F n ξ) 0 :=
  LinearEquiv.ofEq _ _
    (fixed_zero_eq_tame_invariants R D F ι hιrange n ξ).symm

/-- Frobenius on the actual inertia-fixed space, obtained by transporting the
literal induced Frobenius operator through the proved fixed-space equality. -/
def actualFixedFrobenius :
    Module.End ℂ (fixed R D F (actualParameter R D F n ξ) 0) :=
  (tameInvariantsEquivFixedZero R D F ι hιrange n ξ).conj
    (InvariantPolynomial.fixedFrobenius
      (tameRestriction (actualParameter R D F n ξ) ι)
      (actionEquiv (actualParameter R D F n ξ) φ) q
      (geometric_relation (actualParameter R D F n ξ) ι φ q hrel)).toLinearMap

/-- The standard local polynomial on the actual inertia-fixed space. -/
def actualLocalPolynomial : ℂ[X] :=
  InvariantPolynomial.operatorPolynomial
    (actualFixedFrobenius R D F ι hιrange φ n ξ q hrel)

/-- The finite packet local polynomial is the polynomial of Frobenius on the
actual zeroth lower fixed space. -/
theorem packetLocalPolynomial_eq_actualLocalPolynomial :
    InvariantPolynomial.localPolynomial
      (tameRestriction (actualParameter R D F n ξ) ι)
      (actionEquiv (actualParameter R D F n ξ) φ) q
      (geometric_relation (actualParameter R D F n ξ) ι φ q hrel) =
      actualLocalPolynomial R D F ι hιrange φ n ξ q hrel := by
  change InvariantPolynomial.operatorPolynomial
      (InvariantPolynomial.fixedFrobenius
        (tameRestriction (actualParameter R D F n ξ) ι)
        (actionEquiv (actualParameter R D F n ξ) φ) q
        (geometric_relation (actualParameter R D F n ξ) ι φ q hrel)).toLinearMap =
    InvariantPolynomial.operatorPolynomial
      ((tameInvariantsEquivFixedZero R D F ι hιrange n ξ).conj
        (InvariantPolynomial.fixedFrobenius
          (tameRestriction (actualParameter R D F n ξ) ι)
          (actionEquiv (actualParameter R D F n ξ) φ) q
          (geometric_relation (actualParameter R D F n ξ) ι φ q hrel)).toLinearMap)
  exact (InvariantPolynomial.operatorPolynomial_conj
    (tameInvariantsEquivFixedZero R D F ι hιrange n ξ)
    (InvariantPolynomial.fixedFrobenius
      (tameRestriction (actualParameter R D F n ξ) ι)
      (actionEquiv (actualParameter R D F n ξ) φ) q
      (geometric_relation (actualParameter R D F n ξ) ι φ q hrel)).toLinearMap).symm

include hφ hrel hξ in
/-- Triviality on the actual inertia kernel is equivalent to the zero inertia
label of the induced tame packet. -/
theorem inertia_le_kernel_iff_label_zero :
    (actualDegree R D F).ker ≤ (actualParameter R D F n ξ).ker ↔ j = 0 := by
  constructor
  · intro hI
    have hkerTop : Representation.invariants
        ((actualParameter R D F n ξ).comp (actualDegree R D F).ker.subtype) = ⊤ :=
      (NormalInertia.fixed_top_iff_le_kernel
        (actualParameter R D F n ξ) (actualDegree R D F).ker).2 hI
    have hfiniteTop :
        (tameRestriction (actualParameter R D F n ξ) ι).invariants = ⊤ :=
      (invariants_eq_of_range_eq (actualParameter R D F n ξ) ι
        (actualDegree R D F).ker hιrange).trans hkerTop
    have htopdim : Module.finrank ℂ
        (tameRestriction (actualParameter R D F n ξ) ι).invariants =
        Module.finrank ℂ (DegreeIndSpace (actualDegree R D F) n ξ) :=
      (LinearEquiv.ofTop _ hfiniteTop).finrank_eq
    have hdim := InducedTameProfile.invariant_dimension
      (actualDegree R D F) ι φ hφ n ξ q j hrel hξ
    rw [htopdim, InducedCycleInvariants.dimension (actualDegree R D F) φ hφ n ξ] at hdim
    by_contra hj
    rw [if_neg hj] at hdim
    exact (NeZero.ne n) hdim.symm
  · intro hj
    have hfiniteTop :
        (tameRestriction (actualParameter R D F n ξ) ι).invariants = ⊤ := by
      simpa [hj] using InducedTameProfile.inertia_invariants
        (actualDegree R D F) ι φ hφ n ξ q j hrel hξ
    have hkerTop : Representation.invariants
        ((actualParameter R D F n ξ).comp (actualDegree R D F).ker.subtype) = ⊤ := by
      rw [← invariants_eq_of_range_eq (actualParameter R D F n ξ) ι
        (actualDegree R D F).ker hιrange]
      exact hfiniteTop
    exact (NormalInertia.fixed_top_iff_le_kernel
      (actualParameter R D F n ξ) (actualDegree R D F).ker).1 hkerTop

/-- The actual finite packet record, using the literal lower-group images and
lower-numbering weights rather than a supplied abstract filtration. -/
def actualObserved {k : Type*} [Field k] [Fintype k]
    (S : Finset ℕ) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    FiniteTameComparison.Observables M :=
  FiniteTameComparison.observed (actualDegree R D F) ι φ n ξ q hrel S
    (fun r => lowerImage R D F (r + 1))
    (fun r => lowerWeight R D (r + 1)) χ ψ

include hφ hrel hξ htame in
/-- One source-facing theorem: the actual lower filtration supplies the finite
packet coordinates, their local polynomial is Frobenius on the actual inertia
fixed space, and the packet conductors equal the standard lower-numbering sums. -/
theorem actual_comparison_package {k : Type*} [Field k] [Fintype k]
    (S : Finset ℕ) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    actualObserved R D F ι φ n ξ q hrel S χ ψ =
      FiniteTameComparison.fromCoordinates n q j
        (InducedCycleInvariants.returnScalar (actualDegree R D F) φ hφ n ξ) χ ψ ∧
    (((actualObserved R D F ι φ n ξ q hrel S χ ψ).finiteSwan : ℚ) : ℝ) =
      swan R D F (actualParameter R D F n ξ) ∧
    (((actualObserved R D F ι φ n ξ q hrel S χ ψ).finiteArtin : ℚ) : ℝ) =
      artin R D F (actualParameter R D F n ξ) ∧
    (actualObserved R D F ι φ n ξ q hrel S χ ψ).localPolynomial =
      actualLocalPolynomial R D F ι hιrange φ n ξ q hrel := by
  have hP : ∀ g ∈ lowerImage R D F 1, ∀ v,
      actualParameter R D F n ξ g v = v := by
    intro g hg v
    obtain ⟨h, rfl⟩ := hg
    exact LinearMap.congr_fun (htame h) v
  have hJP : ∀ r ∈ S,
      lowerImage R D F (r + 1) ≤ lowerImage R D F 1 := by
    intro r hr g hg
    obtain ⟨h, rfl⟩ := hg
    let h1 : lower R D 1 :=
      RamificationPolyphase.lowerInclusion (R := R) (D := D)
        (Nat.le_add_left 1 r) h
    refine ⟨h1, ?_⟩
    exact (RamificationPolyphase.lift_lowerInclusion (R := R) (D := D)
      (F := F) (Nat.le_add_left 1 r) h).symm
  refine ⟨?_, ?_, ?_, ?_⟩
  · exact FiniteTameComparison.observations_eq_coordinates
      (actualDegree R D F) ι φ hφ n ξ q j hrel hξ
      (lowerImage R D F 1) hP S
      (fun r => lowerImage R D F (r + 1))
      (fun r => lowerWeight R D (r + 1)) hJP χ ψ
  · change ((packetSwan R D F n ξ S : ℚ) : ℝ) = _
    exact packetSwan_eq_standardSwan R D F n ξ htame S
  · change ((packetArtin R D F ι n ξ S : ℚ) : ℝ) = _
    exact packetArtin_eq_standardArtin R D F ι hιrange φ hφ n ξ q j hrel hξ htame S
  · exact packetLocalPolynomial_eq_actualLocalPolynomial
      R D F ι hιrange φ n ξ q hrel

end ActualTameParameter

section DescentToCurrentLocalField

variable (R D : Type*) [CommRing R] [IsLocalRing R]
  [Group D] [Fintype D] [MulSemiringAction D R]
variable (F : RingAut (IsLocalRing.ResidueField R))
variable {M n : ℕ} [NeZero M] [NeZero n]
variable (ι : Multiplicative (ZMod M) →*
  Pullback (residue R D) F)
variable (hιrange : ι.range = (degree (residue R D) F).ker)
variable (φ : Pullback (residue R D) F)
variable (hφ : degree (residue R D) F φ = Multiplicative.ofAdd (1 : ℤ))
variable (ξ : TameDegree.degreeSubgroup (degree (residue R D) F) n →* ℂˣ)
variable (q : (ZMod M)ˣ) (j : ZMod M)
variable (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
  ι (Multiplicative.ofAdd (q : ZMod M)))
variable (hξ : ∀ a : ZMod M,
  (ξ (InducedTameProfile.inertiaInDegree (degree (residue R D) F) ι n
    (Multiplicative.ofAdd a)) : ℂ) = ZMod.stdAddChar (j * a))
variable [FiniteDimensional ℂ
  (DegreeIndSpace (degree (residue R D) F) n ξ)]

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]
variable (hF : F ∈ (residue R D).range)

/-- The zero-label actual monomial parameter descends uniquely to the current
integer-degree unramified Weil model. -/
def descendedParameter (hj : j = 0) :
    Representation ℂ (FiniteUnramifiedWeil.UnramifiedWeil K s)
      (DegreeIndSpace (degree (residue R D) F) n ξ) :=
  RamifiedUnramifiedQuotient.descendRepresentation
    (residue R D) F K s hF
    (degreeInduced (degree (residue R D) F) n ξ)
    ((inertia_le_kernel_iff_label_zero R D F ι hιrange φ hφ n ξ q j hrel hξ).2 hj)

/-- Pulling the descended parameter back recovers the constructed ramified
parameter literally. -/
theorem descendedParameter_comp_degreeModelMap (hj : j = 0) :
    (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj).comp
      (RamifiedUnramifiedQuotient.degreeModelMap (residue R D) F K s) =
    degreeInduced (degree (residue R D) F) n ξ :=
  RamifiedUnramifiedQuotient.descendRepresentation_comp_degreeModelMap
    (residue R D) F K s hF
    (degreeInduced (degree (residue R D) F) n ξ)
    ((inertia_le_kernel_iff_label_zero R D F ι hιrange φ hφ n ξ q j hrel hξ).2 hj)

/-- The actual monomial parameter descends to the inertia-free model exactly in
the zero inertia-label case. -/
theorem exists_unramified_descent_iff :
    (∃ σ : Representation ℂ (FiniteUnramifiedWeil.UnramifiedWeil K s)
        (DegreeIndSpace (degree (residue R D) F) n ξ),
      σ.comp (RamifiedUnramifiedQuotient.degreeModelMap
        (residue R D) F K s) =
        degreeInduced (degree (residue R D) F) n ξ) ↔ j = 0 := by
  constructor
  · rintro ⟨σ, hσ⟩
    have hI := RamifiedUnramifiedQuotient.inertia_le_pullbackDegreeRepresentation_ker
      (residue R D) F K s σ
    have hker : (degree (residue R D) F).ker ≤
        (degreeInduced (degree (residue R D) F) n ξ).ker := by
      simpa only [RamifiedUnramifiedQuotient.Inertia,
        RamifiedUnramifiedQuotient.pullbackDegreeRepresentation] using
        (show RamifiedUnramifiedQuotient.Inertia (residue R D) F ≤
          (σ.comp (RamifiedUnramifiedQuotient.degreeModelMap
            (residue R D) F K s)).ker from hI)
    exact (inertia_le_kernel_iff_label_zero R D F ι hιrange φ hφ n ξ q j hrel hξ).1
      (by simpa [hσ] using hker)
  · intro hj
    exact ⟨descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj,
      descendedParameter_comp_degreeModelMap R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj⟩

variable (t : Type*) [Field t] [Algebra s t] [FiniteDimensional s t]

/-- Actual unramified field-tower restriction of the descended monomial
parameter agrees with the Block 40 degree-dilation polynomial. -/
theorem descended_actual_baseChange_polynomial (hj : j = 0) :
    FiniteUnramifiedWeil.frobeniusPolynomial
      (UnramifiedFieldTower.LowerField K s) t
      (UnramifiedFieldTower.restrictRepresentation K s t
        (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)) =
    FiniteUnramifiedWeil.frobeniusPolynomial K s
      (FiniteUnramifiedWeil.baseChangeRepresentation K s
        (Module.finrank s t)
        (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)) :=
  ActualUnramifiedBaseChange.frobeniusPolynomial_eq_modelBaseChange K s t
    (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)

/-- The corresponding Euler factors agree under the actual unramified field
tower and the internal monomial degree dilation. -/
theorem descended_actual_baseChange_localFactor (hj : j = 0) :
    FiniteUnramifiedWeil.unramifiedLocalFactor
      (UnramifiedFieldTower.LowerField K s) t
      (UnramifiedFieldTower.restrictRepresentation K s t
        (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)) =
    FiniteUnramifiedWeil.unramifiedLocalFactor K s
      (FiniteUnramifiedWeil.baseChangeRepresentation K s
        (Module.finrank s t)
        (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)) :=
  ActualUnramifiedBaseChange.localFactor_eq_modelBaseChange K s t
    (descendedParameter R D F ι hιrange φ hφ n ξ q j hrel hξ K s hF hj)

end DescentToCurrentLocalField

end PaperXI.ActualMonomialLocalGlobal
