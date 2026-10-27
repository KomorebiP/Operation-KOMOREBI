import CocycleFiberSelector
import Mathlib.RepresentationTheory.Basic

namespace Komorebi.StrongArtin.FiniteGroupCocycleAveraging

open Komorebi.StrongArtin.CocycleFiberSelector

noncomputable section

variable {k G V : Type*}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup V] [Module k V]

/-- A one-cocycle for a specified linear representation. -/
def IsRepresentationCocycle (ρ : Representation k G V) (f : G → V) : Prop :=
  ∀ g h, f (g * h) = f g + ρ g (f h)

/-- A one-cocycle is a coboundary if it has the form `g • x - x`. -/
def IsRepresentationCoboundary (ρ : Representation k G V) (f : G → V) : Prop :=
  ∃ x : V, ∀ g : G, f g = ρ g x - x

/-- Sum of all values of a finite-group cocycle. -/
def cocycleSum (f : G → V) : V := ∑ h : G, f h

/-- The canonical averaging witness for a finite-group cocycle. -/
def averagingWitness (f : G → V) : V :=
  -((Fintype.card G : k)⁻¹) • cocycleSum f

/-- Summing the cocycle equation over the group. -/
theorem cocycleSum_identity
    (ρ : Representation k G V) (f : G → V)
    (hf : IsRepresentationCocycle ρ f) (g : G) :
    cocycleSum f =
      (Fintype.card G : k) • f g + ρ g (cocycleSum f) := by
  have hperm : (∑ h : G, f (g * h)) = ∑ h : G, f h := by
    simpa using (Equiv.sum_comp (Equiv.mulLeft g) f)
  change (∑ h : G, f h) =
    (Fintype.card G : k) • f g + ρ g (∑ h : G, f h)
  calc
    (∑ h : G, f h) = ∑ h : G, f (g * h) := hperm.symm
    _ = ∑ h : G, (f g + ρ g (f h)) := by
      apply Finset.sum_congr rfl
      intro h _
      exact hf g h
    _ = (Fintype.card G : k) • f g + ρ g (∑ h : G, f h) := by
      rw [Finset.sum_add_distrib, map_sum]
      simp [Nat.cast_smul_eq_nsmul]

/-- **Finite-group cocycle averaging.** If the group order is nonzero in the
coefficient field, every one-cocycle is a coboundary. -/
theorem cocycle_is_coboundary
    (ρ : Representation k G V) (f : G → V)
    (hf : IsRepresentationCocycle ρ f)
    (hcard : (Fintype.card G : k) ≠ 0) :
    IsRepresentationCoboundary ρ f := by
  refine ⟨averagingWitness (k := k) f, ?_⟩
  intro g
  have hid := cocycleSum_identity ρ f hf g
  have hdiff :
      cocycleSum f - ρ g (cocycleSum f) =
        (Fintype.card G : k) • f g := by
    have h := congrArg
      (fun x : V => x - ρ g (cocycleSum f)) hid
    simpa using h
  have hsolve :
      f g = (Fintype.card G : k)⁻¹ •
        (cocycleSum f - ρ g (cocycleSum f)) := by
    calc
      f g = (1 : k) • f g := by simp
      _ = ((Fintype.card G : k)⁻¹ * (Fintype.card G : k)) • f g := by
        rw [inv_mul_cancel₀ hcard]
      _ = (Fintype.card G : k)⁻¹ •
          ((Fintype.card G : k) • f g) := by
        rw [smul_smul]
      _ = (Fintype.card G : k)⁻¹ •
          (cocycleSum f - ρ g (cocycleSum f)) := by
        rw [hdiff]
  rw [hsolve, averagingWitness, map_smul]
  rw [smul_sub]
  simp only [neg_smul]
  abel


end

end Komorebi.StrongArtin.FiniteGroupCocycleAveraging
