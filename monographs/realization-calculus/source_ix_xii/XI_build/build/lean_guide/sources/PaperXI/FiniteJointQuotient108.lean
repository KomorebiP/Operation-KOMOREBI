import PaperXI.SmoothDegreeQuotient
import Mathlib.Topology.Algebra.OpenSubgroup

/-! A single finite quotient for two smooth actions, constructed from their
actual joint kernel. No faithful quotient or finite image is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteJointQuotient108
open Representation
variable {k K W U : Type*} [Field k] [Group K]
  [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]

def kernel (ρ : Representation k K W) (σ : Representation k K U) : Subgroup K :=
  ρ.ker ⊓ σ.ker

instance kernel_normal (ρ : Representation k K W) (σ : Representation k K U) :
    (kernel ρ σ).Normal := by unfold kernel; infer_instance

abbrev quotient (ρ : Representation k K W) (σ : Representation k K U) := K ⧸ kernel ρ σ

def first (ρ : Representation k K W) (σ : Representation k K U) :
    Representation k (quotient ρ σ) W :=
  QuotientRepresentation.descend (kernel ρ σ) ρ inf_le_left

def second (ρ : Representation k K W) (σ : Representation k K U) :
    Representation k (quotient ρ σ) U :=
  QuotientRepresentation.descend (kernel ρ σ) σ inf_le_right

@[simp] theorem first_comp (ρ : Representation k K W) (σ : Representation k K U) :
    (first ρ σ).comp (QuotientGroup.mk' (kernel ρ σ)) = ρ := rfl

@[simp] theorem second_comp (ρ : Representation k K W) (σ : Representation k K U) :
    (second ρ σ).comp (QuotientGroup.mk' (kernel ρ σ)) = σ := rfl

variable [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
  [FiniteDimensional k W] [FiniteDimensional k U]

/-- Finiteness follows from compactness and smoothness on finite-dimensional
carriers; the two actions descend through the same quotient. -/
theorem finite (ρ : Representation k K W) (σ : Representation k K U)
    (hρ : SmoothDegreeQuotient.IsSmooth ρ) (hσ : SmoothDegreeQuotient.IsSmooth σ) :
    Finite (quotient ρ σ) :=
  (kernel ρ σ).quotient_finite_of_isOpen
    ((SmoothDegreeQuotient.isOpen_kernel_of_smooth ρ hρ).inter
      (SmoothDegreeQuotient.isOpen_kernel_of_smooth σ hσ))

end PaperXI.FiniteJointQuotient108
