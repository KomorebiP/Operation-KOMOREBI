import PaperXI.FiniteAverage
import PaperXI.SchrodingerTrace
import PaperXI.HeisenbergCardinality
import PaperXI.HeisenbergProjector

/-! Trace and rank of the literal maximal isotropic averaging projector. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergSelector
open scoped Classical

variable {G V : Type*} [Group G] [Fintype G]
  [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

omit [FiniteDimensional ℂ V] in
/-- The trace of a finite group average is the average of the traces. -/
theorem trace_average (ρ : Representation ℂ G V) :
    LinearMap.trace ℂ V (FiniteAverage.average ρ) =
      (Fintype.card G : ℂ)⁻¹ * ∑ g : G, LinearMap.trace ℂ V (ρ g) := by
  simp [FiniteAverage.average]

/-- The rank equals the trace because the actual average is an idempotent. -/
theorem rank_average (ρ : Representation ℂ G V) :
    (Module.finrank ℂ (LinearMap.range (FiniteAverage.average ρ)) : ℂ) =
      LinearMap.trace ℂ V (FiniteAverage.average ρ) := by
  have hid : IsIdempotentElem (FiniteAverage.average ρ) := FiniteAverage.idempotent ρ
  exact (LinearMap.IsIdempotentElem.isProj_range _ hid).trace.symm

/-- Trace one gives a genuine one-dimensional invariant subspace. -/
theorem invariants_rank_one_of_trace_one (ρ : Representation ℂ G V)
    (htrace : LinearMap.trace ℂ V (FiniteAverage.average ρ) = 1) :
    Module.finrank ℂ ρ.invariants = 1 := by
  have h := rank_average ρ
  rw [FiniteAverage.range_eq, htrace] at h
  exact_mod_cast h

section Isotropic
variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]
open HeisenbergProjector HeisenbergGeometry HeisenbergForm

/-- A zero vector in a subspace is exactly the identity after multiplicative tagging. -/
theorem coordinates_zero_iff (L : Submodule K (X × Module.Dual K X))
    (a : Multiplicative L) :
    ((a.toAdd : X × Module.Dual K X).1 = 0 ∧
      (a.toAdd : X × Module.Dual K X).2 = 0) ↔ a = 1 := by
  constructor
  · intro h
    have ha : a.toAdd = 0 := Subtype.ext (Prod.ext h.1 h.2)
    exact congrArg Multiplicative.ofAdd ha
  · intro h
    subst a
    simp

variable [Fintype X]

/-- A zero-central lift has nonzero trace only at its identity. -/
theorem trace_restriction {ψ : AddChar K ℂ} (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L)
    (a : Multiplicative L) :
    LinearMap.trace ℂ (X → ℂ) (restriction ψ h2 L hL a) =
      if a = 1 then (Fintype.card X : ℂ) else 0 := by
  rw [restriction_apply, SchrodingerTrace.character_support hψ]
  simp only [coordinates_zero_iff, AddChar.map_zero_eq_one, mul_one]

/-- The actual isotropic projector has trace equal to the cardinality ratio. -/
theorem trace_projector {ψ : AddChar K ℂ} (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    LinearMap.trace ℂ (X → ℂ) (projector ψ h2 L hL) =
      (Fintype.card L : ℂ)⁻¹ * Fintype.card X := by
  rw [projector, trace_average (G := Multiplicative L) (V := X → ℂ)]
  simp only [trace_restriction hψ, Fintype.card_multiplicative]
  simp

variable [FiniteDimensional K X]

/-- Maximality supplies the denominator, so the actual projector has trace one. -/
theorem maximal_trace_one {ψ : AddChar K ℂ} (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsMaximalIsotropic form L)
    [Fintype L] : LinearMap.trace ℂ (X → ℂ) (projector ψ h2 L hL.1) = 1 := by
  rw [trace_projector hψ]
  have hcard : Fintype.card L = Fintype.card X := by
    simpa only [Nat.card_eq_fintype_card] using HeisenbergCardinality.natCard_eq L hL
  rw [hcard]
  exact inv_mul_cancel₀ (by exact_mod_cast Fintype.card_ne_zero (α := X))

/-- Every maximal isotropic subgroup selects an actual one-dimensional range
in the Schrödinger model. -/
theorem maximal_rank_one {ψ : AddChar K ℂ} (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsMaximalIsotropic form L)
    [Fintype L] :
    Module.finrank ℂ (LinearMap.range (projector ψ h2 L hL.1)) = 1 := by
  have h := rank_average (G := Multiplicative L) (V := X → ℂ) (restriction ψ h2 L hL.1)
  change (Module.finrank ℂ (LinearMap.range (projector ψ h2 L hL.1)) : ℂ) = _ at h
  rw [show FiniteAverage.average (G := Multiplicative L) (V := X → ℂ)
      (restriction ψ h2 L hL.1) =
    projector ψ h2 L hL.1 from rfl, maximal_trace_one hψ h2 L hL] at h
  exact_mod_cast h

/-- The common fixed subspace of any maximal isotropic zero-central lift is a line. -/
theorem maximal_fixed_line {ψ : AddChar K ℂ} (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsMaximalIsotropic form L)
    [Fintype L] : Module.finrank ℂ
      (Representation.invariants (G := Multiplicative L) (restriction ψ h2 L hL.1)) = 1 := by
  rw [← range_eq_invariants]
  exact maximal_rank_one hψ h2 L hL

end Isotropic

end PaperXI.HeisenbergSelector
