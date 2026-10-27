import ContinuousLocalGluingCokernel
import FiniteLocalFamilyUpToConjugacy

/-! Actual representation-level composition of the two-stage obstruction.
Absolute H2 vanishing and simultaneous local compatibility are not conflated. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

theorem simultaneous_lifts_iff_gluing_obstruction_zero
    (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (b0 : D.continuousOneCochains)
    (hb0 : D.continuousDifferential hr b0=D.continuousDefectOf D.lift D.lift_residue hr) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, D.q (lift g)=D.rho g) ∧ ∀ i h, lift (loc i h)=t i h) ↔
    D.strictGluingObstruction L hr loc hloc
      (D.prescribedLocalPair L hr loc hloc t ht htc) b0 hb0=0 := by
  rw [D.continuous_simultaneous_local_lifts_iff]
  exact D.localConstraint_zero_iff_gluing_zero L hr loc hloc _ b0 hb0

/-- This criterion constructs the absolute primitive from the actual global
vanishing theorem, and then applies surjectivity of continuous Z1 restriction. -/
theorem simultaneous_lifts_of_absolute_zero_and_surjective_restriction
    (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (habs : D.continuousObstruction hr=0)
    (hs : Function.Surjective (D.restrictOneCocycles L hr loc hloc)) :
    ∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, D.q (lift g)=D.rho g) ∧ ∀ i h, lift (loc i h)=t i h := by
  obtain ⟨b,hbc,hb⟩ := (D.continuousObstruction_zero_iff hr).mp habs
  have hb0 : D.continuousDifferential hr ⟨b,hbc⟩=D.continuousDefectOf D.lift D.lift_residue hr := by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm
  apply (D.continuous_simultaneous_local_lifts_iff L hr loc hloc t ht htc).mpr
  exact D.localConstraint_zero_of_surjective_restriction L hr loc hloc _ ⟨b,hbc⟩ hb0 hs

end Komorebi.StrongArtin.SquareZeroH2.Datum

namespace Komorebi.StrongArtin.SquareZeroH2

/-- Matrix specialization of the positive finite-quotient local-conjugacy sector. -/
theorem finite_matrix_lift_matching_local_family_up_to_conjugacy
    {Q I n R S : Type} [Group Q] [Fintype Q]
    [Fintype n] [DecidableEq n] [CommRing R] [CommRing S]
    (H : I → Type) [∀ i, Group (H i)] [∀ i, Fintype (H i)]
    (q : R →+* S) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* (Matrix n n S)ˣ)
    (hn : IsUnit (Fintype.card Q : Matrix n n R))
    (loc : ∀ i, H i →* Q)
    (t : ∀ i, H i →* (Matrix n n R)ˣ)
    (ht : ∀ i h, (q.mapMatrix : Matrix n n R →+* Matrix n n S) (t i h)=
      (rho (loc i h) : Matrix n n S))
    (hlocal : ∀ i, IsUnit (Fintype.card (H i) : Matrix n n R)) :
    ∃ lift : Q →* (Matrix n n R)ˣ,
      (∀ g, q.mapMatrix (lift g)=(rho g : Matrix n n S)) ∧
      ∀ i, ∃ u : (Matrix n n R)ˣ, (q.mapMatrix : Matrix n n R →+* Matrix n n S) u=1 ∧
        ∀ h, t i h=u*lift (loc i h)*u⁻¹ := by
  exact finite_quotient_lift_matching_local_family_up_to_conjugacy H q.mapMatrix
    (matrix_map_surjective q hq) (matrix_kernel_squareZero q hsq) rho hn loc t ht hlocal

end Komorebi.StrongArtin.SquareZeroH2
