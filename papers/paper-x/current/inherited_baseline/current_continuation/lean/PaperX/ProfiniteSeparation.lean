import PaperX.GeneralCharacters
import Mathlib.Topology.Algebra.ClopenNhdofOne

/-! The topological step from coverage in every finite quotient to density.
The arithmetic theorem that Frobenius samples have this coverage is not assumed
as a Lean axiom and is not proved in this module. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ProfiniteSeparation
variable {G X : Type*} [Group G] [TopologicalSpace G]

/-- Every coset of every open normal subgroup contains a conjugate of a sample.
For a compact group these are finite quotients. -/
def QuotientCoverage (s : X → G) : Prop :=
  ∀ (H : OpenNormalSubgroup G) (g : G),
    ∃ x k, g⁻¹ * (k * s x * k⁻¹) ∈ H

variable [IsTopologicalGroup G] [CompactSpace G] [TotallyDisconnectedSpace G]

theorem dense_of_quotient_coverage (s : X → G) (h : QuotientCoverage s) :
    DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹) := by
  apply dense_iff_inter_open.mpr
  rintro U hU ⟨g, hg⟩
  have hopen : IsOpen ((fun z : G => g * z) ⁻¹' U) :=
    hU.preimage (continuous_const.mul continuous_id)
  have hone : (1 : G) ∈ ((fun z : G => g * z) ⁻¹' U) := by simpa using hg
  obtain ⟨H, hH⟩ := ProfiniteGrp.exist_openNormalSubgroup_sub_open_nhds_of_one hopen hone
  obtain ⟨x, k, hx⟩ := h H g
  have hu : k * s x * k⁻¹ ∈ U := by simpa [mul_assoc] using hH hx
  exact ⟨_, hu, ⟨(x,k), rfl⟩⟩

theorem irreducible_separator_of_quotient_coverage
    {K I : Type*} [Field K] [CharZero K] [TopologicalSpace K]
    [IsTopologicalRing K] [T2Space K] [Fintype I] [DecidableEq I]
    {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
    [∀ i, FiniteDimensional K (W i)]
    (ρ : ∀ i, Representation K G (W i)) [∀ i, (ρ i).IsIrreducible]
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j)
    (hc : ∀ i, Continuous (ρ i).character) (s : X → G) (h : QuotientCoverage s) :
    ∃ v : I → X, Function.Injective v ∧
      (PaperX.FiniteSeparation.sampleMatrix (fun i x => (ρ i).character (s x)) v).det ≠ 0 :=
  PaperX.GeneralCharacters.irreducible_dense_separator ρ hne hc s
    (dense_of_quotient_coverage s h)

end PaperX.ProfiniteSeparation
