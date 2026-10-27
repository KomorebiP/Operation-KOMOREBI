import PaperXI.UnramifiedLocalFactor
import PaperXI.ValuationConductor

/-! # Conductor zero for the finite unramified Weil model

This module does two separate things.

* It proves a generic theorem in the existing `ValuationConductor` interface:
  a representation has Artin conductor zero when the actual degree-kernel inertia
  subgroup is trivial.
* It packages the corresponding codimension/Swan/Artin exponents for the finite
  unramified Weil model constructed in Block 39.

The model-specific exponents are not asserted to be the conductor of an absolute
Weil representation. They record the exact unramified specialization of the
existing fixed-space formula.
-/

set_option autoImplicit false
noncomputable section

open scoped Classical

namespace PaperXI.ValuationConductor

open PaperXI.ResidueWeil PaperXI.ValuationRamification

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [MulSemiringAction D R]
variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- In the existing lower-numbering conductor interface, a literally trivial
inertia subgroup forces both the Swan term and the zeroth fixed-space defect to
vanish. No irreducibility assumption is required. -/
theorem artin_zero_of_degree_kernel_bot
    (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V)
    (hI : (degree (residue R D) F).ker = ⊥) :
    artin R D F ρ = 0 := by
  have ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1 := by
    intro g
    have hg : lift R D F 1 g ∈ (degree (residue R D) F).ker := by
      change degree (residue R D) F (lift R D F 1 g) = 1
      exact lift_degree R D F 1 g
    have hbot : lift R D F 1 g ∈ (⊥ : Subgroup (Pullback (residue R D) F)) := by
      rw [← hI]
      exact hg
    have he : lift R D F 1 g = 1 := by
      simpa only [Subgroup.mem_bot] using hbot
    simp [he]
  have htop : fixed R D F ρ 0 = ⊤ := by
    rw [fixed_zero]
    exact (PaperXI.NormalInertia.fixed_top_iff_le_kernel ρ
      (degree (residue R D) F).ker).2 (by rw [hI]; exact bot_le)
  rw [artin, tame_swan_zero R D F ρ ht]
  unfold codimension
  rw [htop]
  simp

end PaperXI.ValuationConductor

namespace PaperXI.FiniteUnramifiedWeil

open PaperXI.ResidueWeil
open ValuativeRel

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]
variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- The fixed-space defect at inertia for the finite unramified model. -/
def inertiaCodimension [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : ℕ :=
  Module.finrank ℂ V - Module.finrank ℂ
    (Representation.invariants (ρ.comp (Inertia K s).subtype))

/-- There are no positive-depth ramification contributions in the finite
unramified model. -/
def swanConductorExponent
    (_ρ : Representation ℂ (UnramifiedWeil K s) V) : ℝ := 0

/-- Artin exponent in the unramified fixed-space specialization. -/
def artinConductorExponent [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : ℝ :=
  (inertiaCodimension K s ρ : ℝ) + swanConductorExponent K s ρ

/-- Trivial model inertia makes the inertia codimension zero. -/
theorem inertiaCodimension_eq_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    inertiaCodimension K s ρ = 0 := by
  unfold inertiaCodimension
  rw [inertia_invariants_eq_top K s ρ]
  simp

@[simp]
theorem swanConductorExponent_eq_zero
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    swanConductorExponent K s ρ = 0 := rfl

/-- Every finite-dimensional representation of the finite unramified model has
conductor exponent zero in this specialization. -/
theorem artinConductorExponent_eq_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    artinConductorExponent K s ρ = 0 := by
  rw [artinConductorExponent, inertiaCodimension_eq_zero]
  simp

end PaperXI.FiniteUnramifiedWeil
