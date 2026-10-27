import PaperX.AbsoluteIntegralFrobenius
import Mathlib.Tactic
set_option autoImplicit false
noncomputable section
open scoped Pointwise
section Generic
variable {R S G H : Type*} [CommRing R] [CommRing S] [Group G] [Group H]
  [MulSemiringAction G R] [MulSemiringAction H S]
  (f : R →+* S) (φ : H →* G) (hf : ∀ (g : H) (x : R), f (φ g • x) = g • f x)
  (Q : Ideal S)

include hf

theorem restricted_stabilizer (g : H) (hg : g ∈ MulAction.stabilizer H Q) :
    φ g ∈ MulAction.stabilizer G (Ideal.comap f Q) := by
  apply MulAction.mem_stabilizer_iff.mpr
  ext x
  rw [Ideal.mem_pointwise_smul_iff_inv_smul_mem]
  change f ((φ g)⁻¹ • x) ∈ Q ↔ f x ∈ Q
  rw [← map_inv, hf]
  have hinv : g⁻¹ • Q = Q :=
    MulAction.mem_stabilizer_iff.mp ((MulAction.stabilizer H Q).inv_mem hg)
  simpa only [hinv] using
    (Ideal.smul_mem_pointwise_smul_iff (a := g⁻¹) (S := Q) (x := f x))

theorem restricted_inertia (g : H) (hg : g ∈ Q.inertia H) :
    φ g ∈ (Ideal.comap f Q).inertia G := by
  intro x
  change f (φ g • x - x) ∈ Q
  rw [map_sub, hf]
  exact hg (f x)

theorem restricted_residue (p : ℕ) (g : H)
    (hg : ∀ x : S, Ideal.Quotient.mk Q (g • x) = (Ideal.Quotient.mk Q x) ^ p) :
    ∀ x : R, Ideal.Quotient.mk (Ideal.comap f Q) (φ g • x) =
      (Ideal.Quotient.mk (Ideal.comap f Q) x) ^ p := by
  intro x
  rw [← map_pow]
  apply Ideal.Quotient.eq.mpr
  change f (φ g • x - x ^ p) ∈ Q
  rw [map_sub, hf, map_pow]
  apply Ideal.Quotient.eq.mp
  simpa only [map_pow] using hg (f x)
end Generic
