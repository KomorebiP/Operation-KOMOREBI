module
public import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar
public import Mathlib.NumberTheory.LegendreSymbol.AddCharacter
public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.Algebra.Star.Unitary
public import Mathlib.Tactic
public section
set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVII.CyclicProjectors
open Finset ZMod AddChar
variable {N : ℕ} [NeZero N]
variable {A : Type*} [Ring A] [Algebra ℂ A]

noncomputable def packet (rho : ZMod N → A) (j : ZMod N) : A :=
  (N : ℂ)⁻¹ • ∑ r : ZMod N, stdAddChar (-(r*j)) • rho r

theorem character_sum (t : ZMod N) :
    ∑ r : ZMod N, stdAddChar (t*r) = if t=0 then (N : ℂ) else 0 := by
  split_ifs with h
  · simp [h]
  · exact sum_eq_zero_of_ne_one (isPrimitive_stdAddChar N h)

theorem packet_eigen (rho : ZMod N → A)
    (hadd : ∀ a b, rho (a+b) = rho a * rho b) (a j : ZMod N) :
    rho a * packet rho j = stdAddChar (a*j) • packet rho j := by
  unfold packet
  rw [Algebra.mul_smul_comm, Finset.mul_sum]
  simp only [Algebra.mul_smul_comm, ← hadd]
  have hs : (∑ r : ZMod N, stdAddChar (-(r*j)) • rho (a+r)) =
      ∑ r : ZMod N, stdAddChar (-((r-a)*j)) • rho r := by
    apply Fintype.sum_equiv (Equiv.addLeft a)
    intro r
    simp
  rw [hs]
  have hf (r : ZMod N) : -((r-a)*j) = a*j + -(r*j) := by ring
  simp only [hf, map_add_eq_mul, mul_smul]
  rw [← Finset.smul_sum, smul_comm]

theorem packet_mul (rho : ZMod N → A)
    (hadd : ∀ a b, rho (a+b) = rho a * rho b) (j k : ZMod N) :
    packet rho j * packet rho k = if j=k then packet rho j else 0 := by
  conv_lhs => lhs; unfold packet
  rw [Algebra.smul_mul_assoc, Finset.sum_mul]
  simp only [Algebra.smul_mul_assoc, packet_eigen rho hadd, smul_smul,
    ← map_add_eq_mul]
  have hf (r : ZMod N) : -(r*j) + r*k = (k-j)*r := by ring
  simp only [hf]
  rw [← Finset.sum_smul, character_sum]
  by_cases h : j=k
  · subst k
    simp [NeZero.ne N]
  · have hk : k-j ≠ 0 := sub_ne_zero.mpr (Ne.symm h)
    simp [hk, h]

theorem packet_idempotent (rho : ZMod N → A)
    (hadd : ∀ a b, rho (a+b) = rho a * rho b) (j : ZMod N) :
    packet rho j * packet rho j = packet rho j := by
  simp [packet_mul rho hadd]

theorem packet_complete (rho : ZMod N → A) (hzero : rho 0 = 1) :
    ∑ j : ZMod N, packet rho j = 1 := by
  simp only [packet, ← Finset.smul_sum]
  rw [Finset.sum_comm]
  simp only [← Finset.sum_smul, ← neg_mul, character_sum, neg_eq_zero,
    ite_smul, zero_smul, Finset.sum_ite_eq', Finset.mem_univ, ite_true, hzero]
  simp [NeZero.ne N]

/-- The representation is constructed from actual powers of the finite-order symmetry. -/
noncomputable def cyclicPowers (S : A) (r : ZMod N) : A := S ^ r.val

theorem powers_zero (S : A) : cyclicPowers (N := N) S 0 = 1 := by
  simp [cyclicPowers]

theorem powers_add (S : A) (hS : S^N=1) (r s : ZMod N) :
    cyclicPowers S (r+s) = cyclicPowers S r * cyclicPowers S s := by
  rw [cyclicPowers, ZMod.val_add, ← pow_eq_pow_mod _ hS, pow_add]
  rfl

theorem powers_one (S : A) (hS : S^N=1) : cyclicPowers (N := N) S 1 = S := by
  rw [cyclicPowers, show (1 : ZMod N).val = 1 % N from ZMod.val_natCast N 1, ← pow_eq_pow_mod _ hS, pow_one]

theorem cyclic_quantum_projectors (S : A) (hS : S^N=1) :
    (∀ j k : ZMod N, packet (cyclicPowers S) j * packet (cyclicPowers S) k =
      if j=k then packet (cyclicPowers S) j else 0) ∧
    (∑ j : ZMod N, packet (cyclicPowers S) j) = 1 ∧
    ∀ j : ZMod N, S * packet (cyclicPowers S) j =
      stdAddChar j • packet (cyclicPowers S) j := by
  refine ⟨packet_mul _ (powers_add S hS), packet_complete _ (powers_zero S), ?_⟩
  intro j
  simpa only [powers_one S hS, one_mul] using packet_eigen _ (powers_add S hS) 1 j

section Star
variable [StarRing A] [StarModule ℂ A]

theorem star_character (x : ZMod N) : star (stdAddChar x) = stdAddChar (-x) := by
  simp [stdAddChar_apply, map_neg_eq_inv]

theorem packet_selfAdjoint (rho : ZMod N → A)
    (hstar : ∀ r, star (rho r) = rho (-r)) (j : ZMod N) :
    star (packet rho j) = packet rho j := by
  unfold packet
  simp only [star_smul, star_inv, star_natCast, star_sum, star_character, hstar, neg_neg]
  congr 1
  apply Fintype.sum_equiv (Equiv.neg (ZMod N))
  intro r
  simp

theorem powers_star (S : A) (hS : S^N=1) (hU : star S * S = 1)
    (r : ZMod N) : star (cyclicPowers S r) = cyclicPowers S (-r) := by
  have hleft : star (cyclicPowers S r) * cyclicPowers S r = 1 := by
    unfold cyclicPowers
    rw [star_pow]
    exact (Commute.of_eq hU).symm.mul_pow _ ▸ by simp [hU]
  have hright : cyclicPowers S r * cyclicPowers S (-r) = 1 := by
    rw [← powers_add S hS, add_neg_cancel, powers_zero]
  calc
    star (cyclicPowers S r) = star (cyclicPowers S r) *
      (cyclicPowers S r * cyclicPowers S (-r)) := by rw [hright, mul_one]
    _ = cyclicPowers S (-r) := by rw [← mul_assoc, hleft, one_mul]
end Star
end KomorebiPaperVII.CyclicProjectors
