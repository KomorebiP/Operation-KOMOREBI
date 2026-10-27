import FiniteQuotientCocycleDescent
import Mathlib.Algebra.Group.Prod

namespace Komorebi.StrongArtin.CommonKernelCocycleSurvival

open Komorebi.StrongArtin.FiniteGroupCocycleAveraging
open Komorebi.StrongArtin.FiniteQuotientCocycleDescent

noncomputable section

variable {k G Γ C V : Type*}
  [Field k] [Group G] [Group Γ] [Fintype Γ] [CommGroup C]
  [AddCommGroup V] [Module k V]

/-- Every one-cocycle vanishes at the identity. -/
theorem cocycle_one_eq_zero
    (ρG : Representation k G V)
    (f : G → V) (hf : IsRepresentationCocycle ρG f) :
    f 1 = 0 := by
  have h := hf 1 1
  have h' : f 1 + 0 = f 1 + f 1 := by
    simpa using h
  exact (add_left_cancel h').symm

omit [Fintype Γ] in
/-- If the coefficient action factors through `q` and `sigma ∈ ker q`, then
conjugating `sigma` transports its cocycle value by the residual action. -/
theorem cocycle_conjugate_of_quotient_kernel
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (g sigma : G) (hqSigma : q sigma = 1) :
    f (g * (sigma * g⁻¹)) = ρG g (f sigma) := by
  have hsAction : ρG sigma = 1 := by
    rw [haction sigma, hqSigma]
    exact map_one ρΓ
  have hsg : f (sigma * g⁻¹) = f sigma + f g⁻¹ := by
    rw [hf sigma g⁻¹, hsAction]
    rfl
  have hone := cocycle_one_eq_zero ρG f hf
  have hcancel : f g + ρG g (f g⁻¹) = 0 := by
    simpa [hone] using (hf g g⁻¹).symm
  calc
    f (g * (sigma * g⁻¹))
        = f g + ρG g (f (sigma * g⁻¹)) := hf g (sigma * g⁻¹)
    _ = f g + ρG g (f sigma + f g⁻¹) := by rw [hsg]
    _ = ρG g (f sigma) + (f g + ρG g (f g⁻¹)) := by
      rw [map_add]
      abel
    _ = ρG g (f sigma) := by rw [hcancel, add_zero]

/-- **Common residual/cyclotomic-kernel survival.** Let a Galois-type group `G`
map onto a finite residual quotient `Γ`, and also map to an abelian quotient
`C` (the finite cyclotomic quotient). Assume the coefficient action factors
through `Γ`, `|Γ|` is invertible, and the `Γ`-module has no nonzero invariants.
Then every nontrivial one-cocycle class has a nonzero value on
`ker q ∩ ker chi`.

This directly replaces the earlier field-intersection argument. No linear
disjointness theorem is required at this algebraic stage. -/
theorem exists_nonzero_value_in_common_kernel
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ) (hq : Function.Surjective q)
    (chi : G →* C)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (hnoinv : ∀ v : V, (∀ a : Γ, ρΓ a v = v) → v = 0)
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρG f) :
    ∃ sigma : G, q sigma = 1 ∧ chi sigma = 1 ∧ f sigma ≠ 0 := by
  obtain ⟨sigma, hqSigma, hfSigma⟩ :=
    exists_nonzero_value_in_quotient_kernel
      ρG ρΓ q hq haction f hf hcard hnontrivial
  by_contra hnone
  have hcommon : ∀ x : G, q x = 1 → chi x = 1 → f x = 0 := by
    intro x hqx hcx
    by_contra hfx
    exact hnone ⟨x, hqx, hcx, hfx⟩
  let qc : G →* Γ × C := q.prod chi
  have hkerQC : ∀ x : G, qc x = 1 → f x = 0 := by
    intro x hx
    have hqx : q x = 1 := by
      have := congrArg Prod.fst hx
      simpa [qc] using this
    have hcx : chi x = 1 := by
      have := congrArg Prod.snd hx
      simpa [qc] using this
    exact hcommon x hqx hcx
  have hfixed : ∀ a : Γ, ρΓ a (f sigma) = f sigma := by
    intro a
    obtain ⟨g, hg⟩ := hq a
    have hqc : qc (g * (sigma * g⁻¹)) = qc sigma := by
      apply Prod.ext
      · simp [qc, hqSigma]
      · simp [qc, mul_comm, mul_left_comm]
    have heq : f (g * (sigma * g⁻¹)) = f sigma :=
      cocycle_eq_of_quotient_eq ρG f hf qc hkerQC hqc
    have hconj : f (g * (sigma * g⁻¹)) = ρG g (f sigma) :=
      cocycle_conjugate_of_quotient_kernel
        ρG ρΓ q haction f hf g sigma hqSigma
    calc
      ρΓ a (f sigma) = ρΓ (q g) (f sigma) := by rw [hg]
      _ = ρG g (f sigma) := by rw [haction g]
      _ = f sigma := hconj.symm.trans heq
  exact hfSigma (hnoinv (f sigma) hfixed)

end

end Komorebi.StrongArtin.CommonKernelCocycleSurvival
