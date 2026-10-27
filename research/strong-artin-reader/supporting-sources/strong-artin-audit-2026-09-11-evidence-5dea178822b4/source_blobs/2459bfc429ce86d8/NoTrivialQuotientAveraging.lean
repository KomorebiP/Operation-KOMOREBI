import Mathlib.Algebra.Field.Basic
import Mathlib.RepresentationTheory.Basic

namespace Komorebi.StrongArtin.NoTrivialQuotientAveraging

noncomputable section

variable {k G W T : Type*}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W]
  [AddCommGroup T] [Module k T]

/-- The normalized Reynolds average attached to a finite group representation. -/
def reynoldsAverage (ρ : Representation k G W) (w : W) : W :=
  (Fintype.card G : k)⁻¹ • ρ.norm w

/-- The normalized average is fixed by the whole finite group. -/
theorem reynoldsAverage_fixed
    (ρ : Representation k G W) (w : W) (g : G) :
    ρ g (reynoldsAverage ρ w) = reynoldsAverage ρ w := by
  simp [reynoldsAverage]

/-- An equivariant linear map into a trivial representation preserves the
normalized Reynolds average. -/
theorem map_reynoldsAverage
    (ρ : Representation k G W)
    (q : W →ₗ[k] T)
    (hequiv : ∀ g w, q (ρ g w) = q w)
    (hcard : (Fintype.card G : k) ≠ 0)
    (w : W) :
    q (reynoldsAverage ρ w) = q w := by
  have hqnorm : q (ρ.norm w) = (Fintype.card G : k) • q w := by
    simp [Representation.norm, LinearMap.sum_apply, map_sum, hequiv,
      Finset.sum_const, Nat.cast_smul_eq_nsmul]
  rw [reynoldsAverage, q.map_smul, hqnorm, smul_smul,
    inv_mul_cancel₀ hcard, one_smul]

/-- **Prime-to-characteristic no-trivial-quotient lemma.** If a finite-group
representation has no nonzero invariant vector and the group order is nonzero
in the coefficient field, then every equivariant linear map to a trivial
representation is zero.

This is the representation-theoretic input needed in the cyclotomic-depth
survival argument: a nonzero intersection with a cyclotomic extension would
produce precisely such a trivial quotient. -/
theorem equivariant_map_to_trivial_eq_zero
    (ρ : Representation k G W)
    (q : W →ₗ[k] T)
    (hequiv : ∀ g w, q (ρ g w) = q w)
    (hnoinv : ∀ w : W, (∀ g : G, ρ g w = w) → w = 0)
    (hcard : (Fintype.card G : k) ≠ 0) :
    q = 0 := by
  ext w
  let a := reynoldsAverage ρ w
  have hafixed : ∀ g : G, ρ g a = a := by
    intro g
    exact reynoldsAverage_fixed ρ w g
  have ha : a = 0 := hnoinv a hafixed
  have hqa : q a = q w := map_reynoldsAverage ρ q hequiv hcard w
  rw [ha] at hqa
  simpa using hqa.symm

/-- Equivalent pointwise form: every equivariant map to a trivial target kills
every vector. -/
theorem equivariant_map_to_trivial_apply_eq_zero
    (ρ : Representation k G W)
    (q : W →ₗ[k] T)
    (hequiv : ∀ g w, q (ρ g w) = q w)
    (hnoinv : ∀ w : W, (∀ g : G, ρ g w = w) → w = 0)
    (hcard : (Fintype.card G : k) ≠ 0)
    (w : W) :
    q w = 0 := by
  rw [equivariant_map_to_trivial_eq_zero ρ q hequiv hnoinv hcard]
  rfl

end

end Komorebi.StrongArtin.NoTrivialQuotientAveraging

namespace Komorebi.StrongArtin.NoTrivialQuotientAveraging

noncomputable section

variable {k G W T : Type*}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W]
  [AddCommGroup T] [Module k T]

/-- A surjective equivariant map to a trivial target forces that target to be
subsingleton under the prime-to-characteristic/no-invariants hypotheses. -/
theorem subsingleton_of_surjective_equivariant_to_trivial
    (ρ : Representation k G W)
    (q : W →ₗ[k] T)
    (hequiv : ∀ g w, q (ρ g w) = q w)
    (hnoinv : ∀ w : W, (∀ g : G, ρ g w = w) → w = 0)
    (hcard : (Fintype.card G : k) ≠ 0)
    (hsurj : Function.Surjective q) :
    Subsingleton T := by
  constructor
  intro x y
  obtain ⟨wx, hwx⟩ := hsurj x
  obtain ⟨wy, hwy⟩ := hsurj y
  have hq := equivariant_map_to_trivial_eq_zero ρ q hequiv hnoinv hcard
  have hx : x = 0 := by
    rw [← hwx, hq]
    rfl
  have hy : y = 0 := by
    rw [← hwy, hq]
    rfl
  exact hx.trans hy.symm

/-- Consequently, there is no surjective equivariant map onto a nontrivial
trivial representation. This is the quotient form used to rule out a nonzero
cyclotomic intersection. -/
theorem not_surjective_equivariant_to_nontrivial_trivial
    [Nontrivial T]
    (ρ : Representation k G W)
    (q : W →ₗ[k] T)
    (hequiv : ∀ g w, q (ρ g w) = q w)
    (hnoinv : ∀ w : W, (∀ g : G, ρ g w = w) → w = 0)
    (hcard : (Fintype.card G : k) ≠ 0) :
    ¬ Function.Surjective q := by
  intro hsurj
  exact (not_subsingleton T)
    (subsingleton_of_surjective_equivariant_to_trivial
      ρ q hequiv hnoinv hcard hsurj)

end

end Komorebi.StrongArtin.NoTrivialQuotientAveraging
