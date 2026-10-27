import NoTrivialQuotientAveraging
import Mathlib.RepresentationTheory.Basic

namespace Komorebi.StrongArtin.QuotientNoInvariantsAveraging

open Komorebi.StrongArtin.NoTrivialQuotientAveraging

noncomputable section

variable {k G V : Type*}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup V] [Module k V]

/-- A stable submodule contains every upstairs invariant vector. If the finite
 group order is invertible, then the quotient representation has no nonzero
 invariant vector. This is exactness of invariants proved directly by Reynolds
 averaging, without invoking semisimplicity as a black box. -/
theorem quotient_fixed_eq_zero_of_upstairs_fixed_mem
    (ρ : Representation k G V)
    (D : Submodule k V)
    (hD : ∀ g : G, D ≤ D.comap (ρ g))
    (hfixed : ∀ v : V, (∀ g : G, ρ g v = v) → v ∈ D)
    (hcard : (Fintype.card G : k) ≠ 0)
    (q : V ⧸ D)
    (hq : ∀ g : G, (ρ.quotient D hD) g q = q) :
    q = 0 := by
  obtain ⟨v, rfl⟩ := D.mkQ_surjective q
  let a : V := reynoldsAverage ρ v
  have hafixed : ∀ g : G, ρ g a = a := by
    intro g
    exact reynoldsAverage_fixed ρ v g
  have haD : a ∈ D := hfixed a hafixed
  have hqnorm : D.mkQ (ρ.norm v) = (Fintype.card G : k) • D.mkQ v := by
    rw [Representation.norm, LinearMap.sum_apply, map_sum]
    calc
      ∑ g : G, D.mkQ (ρ g v) = ∑ _g : G, D.mkQ v := by
        apply Finset.sum_congr rfl
        intro g hg
        have h := hq g
        simpa [Representation.quotient, Submodule.mkQ_apply] using h
      _ = (Fintype.card G : k) • D.mkQ v := by
        simp [Finset.sum_const, Nat.cast_smul_eq_nsmul]
  have hqa : D.mkQ a = D.mkQ v := by
    change D.mkQ ((Fintype.card G : k)⁻¹ • ρ.norm v) = D.mkQ v
    rw [D.mkQ.map_smul, hqnorm, smul_smul,
      inv_mul_cancel₀ hcard, one_smul]
  calc
    D.mkQ v = D.mkQ a := hqa.symm
    _ = 0 := by
      rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
      exact haD

/-- Pointwise no-invariants formulation for the quotient representation. -/
theorem quotient_has_no_invariants
    (ρ : Representation k G V)
    (D : Submodule k V)
    (hD : ∀ g : G, D ≤ D.comap (ρ g))
    (hfixed : ∀ v : V, (∀ g : G, ρ g v = v) → v ∈ D)
    (hcard : (Fintype.card G : k) ≠ 0) :
    ∀ q : V ⧸ D,
      (∀ g : G, (ρ.quotient D hD) g q = q) → q = 0 := by
  intro q hq
  exact quotient_fixed_eq_zero_of_upstairs_fixed_mem ρ D hD hfixed hcard q hq

end

end Komorebi.StrongArtin.QuotientNoInvariantsAveraging
