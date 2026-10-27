import Komorebi.SufficientResolution.ExactResolution
import Mathlib.LinearAlgebra.Quotient.Basic

/-!
# Compatible local data and the linear globalization obstruction

For G --A--> V --delta--> W with delta A = 0, global realizations lie in
ker delta.  The quotient ker delta / range A detects compatible data which
are not globally realizable.  This is an algebraic construction only.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.Globalization

universe uR uG uV uW

variable {R : Type uR} [CommRing R]
variable {G : Type uG} [AddCommGroup G] [Module R G]
variable {V : Type uV} [AddCommGroup V] [Module R V]
variable {W : Type uW} [AddCommGroup W] [Module R W]

variable (A : G →ₗ[R] V) (delta : V →ₗ[R] W)

/-- The chain condition is a hypothesis, not an automatically supplied existence proof. -/
 theorem realizable_compatible (h : delta.comp A = 0) :
    LinearMap.range A ≤ LinearMap.ker delta := by
  rintro v ⟨g, rfl⟩
  change delta (A g) = 0
  exact LinearMap.congr_fun h g

/-- Realizable vectors, regarded inside the compatible-data submodule. -/
def realizationsInKernel : Submodule R (LinearMap.ker delta) :=
  (LinearMap.range A).comap (LinearMap.ker delta).subtype

/-- No finite-dimensional, orthogonal, or metric hypotheses are needed. -/
abbrev ObstructionSpace :=
  (LinearMap.ker delta) ⧸ realizationsInKernel A delta

/-- The obstruction class of compatible local data. -/
def obstructionClass (v : LinearMap.ker delta) : ObstructionSpace A delta :=
  Submodule.Quotient.mk v

 theorem obstructionClass_zero_iff (v : LinearMap.ker delta) :
    obstructionClass A delta v = 0 ↔ ∃ g : G, A g = (v : V) := by
  change (Submodule.Quotient.mk v : ObstructionSpace A delta) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  rfl

/-- Exactness at the local-data space is equivalent to universal vanishing. -/
 theorem all_obstructions_zero_iff_exact (h : delta.comp A = 0) :
    (∀ v : LinearMap.ker delta, obstructionClass A delta v = 0) ↔
      LinearMap.range A = LinearMap.ker delta := by
  constructor
  · intro hall
    apply le_antisymm (realizable_compatible A delta h)
    intro v hv
    exact (obstructionClass_zero_iff A delta ⟨v, hv⟩).mp (hall ⟨v, hv⟩)
  · intro hex v
    apply (obstructionClass_zero_iff A delta v).mpr
    have hv : (v : V) ∈ LinearMap.range A := by
      rw [hex]
      exact v.2
    exact hv

/-- Injectivity is precisely the extra ingredient used here for uniqueness. -/
 theorem unique_realization_of_zero (hA : Function.Injective A)
    (v : LinearMap.ker delta) (hv : obstructionClass A delta v = 0) :
    ∃! g : G, A g = (v : V) := by
  obtain ⟨g, hg⟩ := (obstructionClass_zero_iff A delta v).mp hv
  exact ⟨g, hg, fun g' hg' => hA (hg'.trans hg.symm)⟩

/-- A left inverse makes the previous uniqueness condition available. -/
 theorem unique_realization_of_leftInverse (S : V →ₗ[R] G)
    (hS : S.comp A = LinearMap.id) (v : LinearMap.ker delta)
    (hv : obstructionClass A delta v = 0) :
    ∃! g : G, A g = (v : V) := by
  apply unique_realization_of_zero A delta _ v hv
  intro g g' h
  have hi (x : G) : S (A x) = x := LinearMap.congr_fun hS x
  simpa only [hi] using congrArg S h

/-- An exact resolution has no linear globalization obstruction for delta = I-a s. -/
 theorem resolution_range_eq_kernel (r : Resolution R G V) :
    LinearMap.range r.analysis = LinearMap.ker (LinearMap.id - r.projector) := by
  ext v
  change (∃ g, r.analysis g = v) ↔ v - r.projector v = 0
  rw [sub_eq_zero, eq_comm]
  exact (r.fixed_iff_realizable v).symm

/-- Compatibility alone can be vacuous even while realizability fails. -/
 theorem compatible_not_realizable_example :
    let A : ℚ →ₗ[ℚ] ℚ := 0
    let delta : ℚ →ₗ[ℚ] ℚ := 0
    delta.comp A = 0 ∧ delta 1 = 0 ∧ ¬ ∃ g : ℚ, A g = 1 := by
  simp

end Komorebi.SufficientResolution.Globalization
