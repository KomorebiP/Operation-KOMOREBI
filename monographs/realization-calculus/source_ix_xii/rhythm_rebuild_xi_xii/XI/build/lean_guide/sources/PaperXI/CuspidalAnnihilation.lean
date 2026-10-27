import PaperXI.PrimitiveCharacterBlock
import PaperXI.FiniteAverage

/-! Subgroup averages and annihilation of an actual central character block.
The cuspidal input is the vanishing of genuine restricted invariants. -/
set_option autoImplicit false
noncomputable section
open scoped MonoidAlgebra BigOperators Classical
namespace PaperXI.CuspidalAnnihilation
open PaperXI.CharacterProjector PaperXI.PrimitiveCharacterBlock
universe u v
variable {G : Type u} [Group G] [Fintype G]
variable {V : Type v} [AddCommGroup V] [Module ℂ V]

/-- The normalized subgroup sum, viewed in the ambient group algebra. -/
def subgroupAverage (U : Subgroup G) : MonoidAlgebra ℂ G :=
  (Fintype.card U : ℂ)⁻¹ • ∑ g : U, MonoidAlgebra.single (g : G) 1

/-- The actual group-algebra action is the Reynolds average of the restricted action. -/
theorem average_action (ρ : Representation ℂ G V) (U : Subgroup G) :
    ρ.asAlgebraHom (subgroupAverage U) = PaperXI.FiniteAverage.average (ρ.comp U.subtype) := by
  simp [subgroupAverage, PaperXI.FiniteAverage.average]

/-- The average has precisely the genuine U-fixed vectors as its range. -/
theorem average_range (ρ : Representation ℂ G V) (U : Subgroup G) :
    LinearMap.range (ρ.asAlgebraHom (subgroupAverage U)) = Representation.invariants (ρ.comp U.subtype) := by
  rw [average_action]
  exact PaperXI.FiniteAverage.range_eq _

/-- No invariant-vector assumption is needed to prove idempotence of the average. -/
theorem average_idempotent (U : Subgroup G) :
    subgroupAverage U * subgroupAverage U = subgroupAverage U := by
  apply PaperXI.SemisimpleDetection.eq_of_irreducible_actions
  intro W _ _ _ σ _
  rw [map_mul, average_action]
  exact PaperXI.FiniteAverage.idempotent _

theorem average_zero_iff (ρ : Representation ℂ G V) (U : Subgroup G) :
    ρ.asAlgebraHom (subgroupAverage U) = 0 ↔ Representation.invariants (ρ.comp U.subtype) = ⊥ := by
  rw [← average_range, LinearMap.range_eq_bot]

variable [FiniteDimensional ℂ V]

/-- A central character projector acts as the identity on its designated irreducible. -/
theorem own_block_action (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    ρ.asAlgebraHom (element ρ) = 1 := by
  have he : Nonempty (Representation.Equiv ρ ρ) := ⟨Representation.Equiv.refl ρ⟩
  simp [irreducible_action ρ ρ, he]

/-- A sharp criterion in the group algebra: annihilation is equivalent to no U-fixed vectors. -/
theorem left_annihilation_iff (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (U : Subgroup G) :
    subgroupAverage U * element ρ = 0 ↔ Representation.invariants (ρ.comp U.subtype) = ⊥ := by
  constructor
  · intro h
    apply (average_zero_iff ρ U).mp
    have hm := congrArg ρ.asAlgebraHom h
    simpa [own_block_action ρ] using hm
  · intro h
    have hz := (average_zero_iff ρ U).mpr h
    apply supported_eq_zero ρ
    · rw [mul_assoc, idempotent ρ]
    · simp [hz]

/-- The opposite multiplication order has the same exact criterion. -/
theorem right_annihilation_iff (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (U : Subgroup G) :
    element ρ * subgroupAverage U = 0 ↔ Representation.invariants (ρ.comp U.subtype) = ⊥ := by
  rw [← Submonoid.mem_center_iff.mp (central ρ) (subgroupAverage U)]
  exact left_annihilation_iff ρ U

/-- Proposition 4.3, specialized to any supplied unipotent radical whose invariants vanish. -/
theorem parabolic_annihilation (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (U : Subgroup G) (hcuspidal : Representation.invariants (ρ.comp U.subtype) = ⊥) :
    subgroupAverage U * element ρ = 0 ∧ element ρ * subgroupAverage U = 0 :=
  ⟨(left_annihilation_iff ρ U).mpr hcuspidal, (right_annihilation_iff ρ U).mpr hcuspidal⟩

/-- A nonzero fixed vector rules out annihilation; irreducibility alone is not cuspidality. -/
theorem nonzero_of_fixed_vector (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (U : Subgroup G) (v : V) (hv : v ≠ 0) (hfixed : v ∈ Representation.invariants (ρ.comp U.subtype)) :
    subgroupAverage U * element ρ ≠ 0 := by
  intro hz
  have hbot := (left_annihilation_iff ρ U).mp hz
  rw [hbot] at hfixed
  exact hv hfixed

end PaperXI.CuspidalAnnihilation
