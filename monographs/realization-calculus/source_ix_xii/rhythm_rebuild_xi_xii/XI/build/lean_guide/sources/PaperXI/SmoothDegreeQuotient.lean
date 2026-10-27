import PaperXI.QuotientRepresentation
import PaperXI.TameDegree
import Mathlib.Topology.Algebra.Group.Quotient
import Mathlib.Topology.Compactness.Compact

/-!
# A smooth representation quotient which retains every integer degree

The quotient kernel is the intersection of the representation kernel and
integer-degree kernel.  No finiteness of the original inertia group and no
identification with an absolute local-field Weil group is assumed here.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SmoothDegreeQuotient

variable {k G V : Type*} [Field k] [Group G]
  [AddCommGroup V] [Module k V]

/-- The subgroup fixing a particular vector. -/
def vectorStabilizer (ρ : Representation k G V) (v : V) : Subgroup G where
  carrier := {g | ρ g v = v}
  one_mem' := by simp
  mul_mem' := by
    intro g h hg hh
    change ρ (g * h) v = v
    rw [map_mul, Module.End.mul_apply, hh, hg]
  inv_mem' := by
    intro g hg
    apply (ρ.apply_bijective g).injective
    simpa using hg.symm

@[simp] theorem mem_vectorStabilizer (ρ : Representation k G V) (v : V) (g : G) :
    g ∈ vectorStabilizer ρ v ↔ ρ g v = v := Iff.rfl

section Topology
variable [TopologicalSpace G]

/-- Algebraic smoothness means that every vector has an open stabilizer. -/
def IsSmooth (ρ : Representation k G V) : Prop :=
  ∀ v, IsOpen (vectorStabilizer ρ v : Set G)

/-- A finite basis turns pointwise open stabilizers into one open action kernel. -/
theorem isOpen_kernel_of_smooth [FiniteDimensional k V]
    (ρ : Representation k G V) (hρ : IsSmooth ρ) :
    IsOpen (ρ.ker : Set G) := by
  let b := Module.finBasis k V
  have heq : (ρ.ker : Set G) = ⋂ i, (vectorStabilizer ρ (b i) : Set G) := by
    ext g
    simp only [Set.mem_iInter]
    change (ρ g = 1) ↔ ∀ i, ρ g (b i) = b i
    constructor
    · intro hg i
      change ρ g = 1 at hg
      rw [hg]
      rfl
    · intro hg
      apply b.ext
      exact hg
  rw [heq]
  exact isOpen_iInter_of_finite fun i => hρ (b i)
end Topology

variable (ρ : Representation k G V) (δ : G →* Multiplicative ℤ)

/-- Only elements invisible both to the action and the integer degree are killed. -/
def jointKernel : Subgroup G := ρ.ker ⊓ δ.ker

instance jointKernel_normal : (jointKernel ρ δ).Normal := by
  unfold jointKernel
  infer_instance

/-- The representation-dependent quotient, without discarding Frobenius degree. -/
abbrev DegreeQuotient := G ⧸ jointKernel ρ δ

/-- The literal quotient map. -/
abbrev quotientMap : G →* DegreeQuotient ρ δ :=
  QuotientGroup.mk' (jointKernel ρ δ)

/-- The integer degree descends because the kernel inclusion is proved. -/
def descendedDegree : DegreeQuotient ρ δ →* Multiplicative ℤ :=
  QuotientGroup.lift (jointKernel ρ δ) δ inf_le_right

/-- The original action descends through this same quotient. -/
def descendedRepresentation : Representation k (DegreeQuotient ρ δ) V :=
  QuotientRepresentation.descend (jointKernel ρ δ) ρ inf_le_left

@[simp] theorem descendedDegree_mk (g : G) :
    descendedDegree ρ δ (quotientMap ρ δ g) = δ g := rfl

@[simp] theorem descendedRepresentation_mk (g : G) :
    descendedRepresentation ρ δ (quotientMap ρ δ g) = ρ g := rfl

@[simp] theorem descendedDegree_comp :
    (descendedDegree ρ δ).comp (quotientMap ρ δ) = δ := rfl

@[simp] theorem descendedRepresentation_comp :
    (descendedRepresentation ρ δ).comp (quotientMap ρ δ) = ρ := rfl

/-- Irreducibility is preserved, not supplied independently for the quotient. -/
theorem descended_irreducible [Representation.IsIrreducible ρ] :
    Representation.IsIrreducible (descendedRepresentation ρ δ) :=
  QuotientRepresentation.descend_irreducible (jointKernel ρ δ) ρ inf_le_left

/-- Surjectivity of the actual integer degree is unchanged by the quotient. -/
theorem degree_surjective_iff :
    Function.Surjective (descendedDegree ρ δ) ↔ Function.Surjective δ := by
  constructor
  · intro h z
    obtain ⟨x, hx⟩ := h z
    obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective x
    exact ⟨g, hx⟩
  · intro h z
    obtain ⟨g, hg⟩ := h z
    exact ⟨quotientMap ρ δ g, hg⟩

/-- The degree-divisible subgroup pulls back literally, not just up to its index. -/
theorem degreeSubgroup_comap (n : ℕ) :
    (TameDegree.degreeSubgroup (descendedDegree ρ δ) n).comap
        (quotientMap ρ δ) = TameDegree.degreeSubgroup δ n := by
  ext g
  simp only [Subgroup.mem_comap, TameDegree.mem_degreeSubgroup]
  rfl

/-- The action and degree have no common invisible element after descent. -/
theorem jointKernel_descended :
    (descendedRepresentation ρ δ).ker ⊓ (descendedDegree ρ δ).ker = ⊥ := by
  apply Subgroup.ext
  intro x
  obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective x
  change (ρ g = 1 ∧ δ g = 1) ↔ quotientMap ρ δ g = 1
  exact (QuotientGroup.eq_one_iff (N := jointKernel ρ δ) g).symm

/-- A quotient can retain the original degree exactly if its kernel is invisible to degree. -/
theorem degree_descends_iff (N : Subgroup G) [N.Normal] :
    (∃ d : G ⧸ N →* Multiplicative ℤ,
      d.comp (QuotientGroup.mk' N) = δ) ↔ N ≤ δ.ker := by
  constructor
  · rintro ⟨d, hd⟩ g hg
    change δ g = 1
    have he : d (QuotientGroup.mk' N g) = δ g := congrArg (fun f => f g) hd
    have hmk : QuotientGroup.mk' N g = 1 :=
      (QuotientGroup.eq_one_iff (N := N) g).mpr hg
    rw [hmk, map_one] at he
    exact he.symm
  · intro hN
    exact ⟨QuotientGroup.lift N δ hN, rfl⟩

/-- The quotient inertia is exactly the image of original inertia. -/
theorem inertia_image :
    (quotientMap ρ δ) '' (δ.ker : Set G) =
      ((descendedDegree ρ δ).ker : Set (DegreeQuotient ρ δ)) := by
  ext x
  constructor
  · rintro ⟨g, hg, rfl⟩
    exact hg
  · intro hx
    obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective x
    exact ⟨g, hx, rfl⟩

section Topology
variable [TopologicalSpace G]

/-- Smoothness and an open inertia subgroup make the joint quotient kernel open. -/
theorem isOpen_jointKernel [FiniteDimensional k V]
    (hρ : IsSmooth ρ) (hδ : IsOpen (δ.ker : Set G)) :
    IsOpen (jointKernel ρ δ : Set G) :=
  (isOpen_kernel_of_smooth ρ hρ).inter hδ

/-- The quotient carries its actual quotient topology, which is discrete. -/
theorem quotient_discrete [IsTopologicalGroup G] [FiniteDimensional k V]
    (hρ : IsSmooth ρ) (hδ : IsOpen (δ.ker : Set G)) :
    DiscreteTopology (DegreeQuotient ρ δ) :=
  QuotientGroup.discreteTopology (isOpen_jointKernel ρ δ hρ hδ)

/-- The quotient map is continuous for the original group topology. -/
theorem quotientMap_continuous : Continuous (quotientMap ρ δ) :=
  QuotientGroup.continuous_mk

/-- Compact original inertia has finite image in the discrete smooth quotient.
The original inertia itself is not assumed finite. -/
theorem finite_descended_inertia [IsTopologicalGroup G] [FiniteDimensional k V]
    (hρ : IsSmooth ρ) (hδ : IsOpen (δ.ker : Set G))
    (hc : IsCompact (δ.ker : Set G)) :
    Finite (descendedDegree ρ δ).ker := by
  let : DiscreteTopology (DegreeQuotient ρ δ) := quotient_discrete ρ δ hρ hδ
  have hfinite := (hc.image (quotientMap_continuous ρ δ)).finite_of_discrete
  rw [inertia_image] at hfinite
  exact Set.finite_coe_iff.mpr hfinite

end Topology
end PaperXI.SmoothDegreeQuotient
