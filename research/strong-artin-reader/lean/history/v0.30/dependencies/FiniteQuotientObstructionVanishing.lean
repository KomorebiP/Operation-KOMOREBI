import ContinuousRepresentationLifting
import FiniteTwoCocycleAveraging
import MatrixSquareZeroObstruction

/-! A vanishing theorem with a verified algebraic order condition. The
continuous representation lift factors through the SAME supplied finite quotient.
This is a classical prime-to-characteristic sector, not a claim of wild vanishing. -/
namespace Komorebi.StrongArtin.SquareZeroH2
open FiniteCohomologyAveraging

variable {G A B : Type} [Group G] [Ring A] [Ring B]

namespace Datum
variable (D : Datum G A B)

theorem kernel_nsmul_bijective_of_isUnit (n : ℕ) (hn : IsUnit (n : A)) :
    Function.Bijective (fun x : D.Kernel => n • x) := by
  obtain ⟨u,hu⟩ := hn
  constructor
  · intro x y hxy
    apply Subtype.ext
    have hv : (n : A)*(x : A)=(n : A)*(y : A) := by
      simpa only [AddSubgroup.coe_nsmul,nsmul_eq_mul] using congrArg Subtype.val hxy
    rw [← hu] at hv
    have h := congrArg (fun a : A => (↑u⁻¹ : A)*a) hv
    simpa [← mul_assoc] using h
  · intro y
    let x : D.Kernel := ⟨(↑u⁻¹ : A)*(y : A), by
      have hy : D.q (y : A)=0 := y.property
      simp [hy]⟩
    refine ⟨x, ?_⟩
    apply Subtype.ext
    change n • ((↑u⁻¹ : A)*(y : A))=(y : A)
    rw [nsmul_eq_mul,← hu,← mul_assoc]
    simp

theorem obstruction_zero_of_groupOrder_isUnit [Fintype G]
    (hn : IsUnit (Fintype.card G : A)) : D.obstruction=0 := by
  apply D.obstruction_zero_iff_boundary.mpr
  exact exists_twoCocycle_primitive D.action
    (D.kernel_nsmul_bijective_of_isUnit _ hn)
    (D.normalizedDefect D.lift D.lift_residue)
    (D.normalizedDefect_cocycle D.lift D.lift_residue)

theorem representation_lifts_of_groupOrder_isUnit [Fintype G]
    (hn : IsUnit (Fintype.card G : A)) :
    ∃ L : G →* Aˣ, ∀ g, D.q (L g)=D.rho g :=
  D.representation_lifts_iff_obstruction_zero.mpr (D.obstruction_zero_of_groupOrder_isUnit hn)

end Datum

/-- A continuous representation given on a finite quotient lifts continuously
on that same quotient. Surjectivity of the quotient label is unnecessary. -/
theorem continuous_representation_lifts_through_finite_quotient
    {Q : Type} [Group Q] [Fintype Q] [TopologicalSpace Q] [DiscreteTopology Q]
    [TopologicalSpace G] [TopologicalSpace A]
    (label : G →* Q) (hlabel : Continuous label)
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* Bˣ) (hn : IsUnit (Fintype.card Q : A)) :
    ∃ LQ : Q →* Aˣ, (∀ a, q (LQ a)=(rho a : B)) ∧
      Continuous (LQ.comp label) ∧
      ∀ g, q ((LQ.comp label) g)=(rho (label g) : B) := by
  obtain ⟨LQ,hLQ⟩ := (datumOfSurjective q hq hsq rho).representation_lifts_of_groupOrder_isUnit hn
  exact ⟨LQ,hLQ,(continuous_of_discreteTopology : Continuous LQ).comp hlabel,fun g => hLQ (label g)⟩

/-- An actual GL_n specialization of the same-quotient continuous lifting theorem. -/
theorem continuous_matrix_representation_lifts_through_finite_quotient
    {Q n R S : Type} [Group Q] [Fintype Q] [TopologicalSpace Q] [DiscreteTopology Q]
    [Fintype n] [DecidableEq n] [CommRing R] [CommRing S]
    [TopologicalSpace G] [TopologicalSpace (Matrix n n R)]
    (label : G →* Q) (hlabel : Continuous label)
    (q : R →+* S) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* (Matrix n n S)ˣ)
    (hn : IsUnit (Fintype.card Q : Matrix n n R)) :
    ∃ LQ : Q →* (Matrix n n R)ˣ,
      (∀ a, (q.mapMatrix : Matrix n n R →+* Matrix n n S) (LQ a)=(rho a : Matrix n n S)) ∧
      Continuous (LQ.comp label) := by
  obtain ⟨LQ,hLQ,hc,_⟩ := continuous_representation_lifts_through_finite_quotient
    label hlabel q.mapMatrix (matrix_map_surjective q hq) (matrix_kernel_squareZero q hsq)
    rho hn
  exact ⟨LQ,hLQ,hc⟩

end Komorebi.StrongArtin.SquareZeroH2
