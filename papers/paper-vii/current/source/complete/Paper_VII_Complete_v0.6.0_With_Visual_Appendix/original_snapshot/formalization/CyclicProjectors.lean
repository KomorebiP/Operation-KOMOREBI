module
public import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar
public import Mathlib.NumberTheory.LegendreSymbol.AddCharacter
public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.Algebra.Star.Unitary
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, checked third block.
This module is independently compilable using the pinned portable Lean kit. -/
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
  rw [cyclicPowers, show (1 : ZMod N).val = 1 % N from by simpa using ZMod.val_natCast N 1, ← pow_eq_pow_mod _ hS, pow_one]

theorem cyclic_quantum_projectors (S : A) (hS : S^N=1) :
    (∀ j k : ZMod N, packet (cyclicPowers S) j * packet (cyclicPowers S) k =
      if j=k then packet (cyclicPowers S) j else 0) ∧
    (∑ j : ZMod N, packet (cyclicPowers S) j) = 1 ∧
    ∀ j : ZMod N, S * packet (cyclicPowers S) j =
      stdAddChar j • packet (cyclicPowers S) j := by
  refine ⟨packet_mul _ (powers_add S hS), packet_complete _ (powers_zero S), ?_⟩
  intro j
  simpa only [powers_one S hS, one_mul] using packet_eigen _ (powers_add S hS) 1 j

theorem star_character (x : ZMod N) : star (stdAddChar x) = stdAddChar (-x) := by
  simpa only [stdAddChar_apply, map_neg_eq_inv, Circle.coe_inv, starRingEnd_apply] using
    (Circle.coe_inv_eq_conj (toCircle x)).symm

section Star
variable [StarRing A] [StarModule ℂ A]

theorem packet_selfAdjoint (rho : ZMod N → A)
    (hstar : ∀ r, star (rho r) = rho (-r)) (j : ZMod N) :
    star (packet rho j) = packet rho j := by
  unfold packet
  simp only [star_smul, star_sum, star_character, hstar, neg_neg]
  have hn : star ((N : ℂ)⁻¹) = (N : ℂ)⁻¹ := by simp
  rw [hn]
  congr 1
  apply Fintype.sum_equiv (Equiv.neg (ZMod N))
  intro r
  simp

theorem powers_star (S : A) (hS : S^N=1) (hU : S ∈ unitary A)
    (r : ZMod N) : star (cyclicPowers S r) = cyclicPowers S (-r) := by
  have hleft : star (cyclicPowers S r) * cyclicPowers S r = 1 := by
    exact Unitary.star_mul_self_of_mem ((unitary A).pow_mem hU r.val)
  have hright : cyclicPowers S r * cyclicPowers S (-r) = 1 := by
    rw [← powers_add S hS, add_neg_cancel, powers_zero]
  calc
    star (cyclicPowers S r) = star (cyclicPowers S r) *
      (cyclicPowers S r * cyclicPowers S (-r)) := by rw [hright, mul_one]
    _ = cyclicPowers S (-r) := by rw [← mul_assoc, hleft, one_mul]

theorem cyclic_packet_selfAdjoint (S : A) (hS : S^N=1) (hU : S ∈ unitary A)
    (j : ZMod N) : star (packet (cyclicPowers S) j) = packet (cyclicPowers S) j := by
  exact packet_selfAdjoint _ (powers_star S hS hU) j

end Star

/-- The standard complex Nth root, identified with its exponential expression. -/
noncomputable def omega : ℂ := stdAddChar (1 : ZMod N)

theorem omega_exponential : omega (N := N) =
    Complex.exp (2 * Real.pi * Complex.I / (N : ℂ)) := by
  simpa [omega] using (ZMod.stdAddChar_coe (N := N) (1 : ℤ))

theorem character_as_power (r : ZMod N) : stdAddChar r = omega (N := N) ^ r.val := by
  simpa [omega, nsmul_eq_mul] using (stdAddChar (N := N)).map_nsmul_eq_pow r.val (1 : ZMod N)

theorem packet_coefficient (r j : ZMod N) :
    stdAddChar (-(r*j)) = (omega (N := N) ^ (r.val * j.val))⁻¹ := by
  rw [map_neg_eq_inv]
  congr 1
  have h : r*j = (r.val * j.val) • (1 : ZMod N) := by simp [nsmul_eq_mul]
  rw [h, map_nsmul_eq_pow]
  rfl

theorem cyclic_projector_formula (S : A) (j : ZMod N) :
    packet (cyclicPowers S) j = (N : ℂ)⁻¹ •
      ∑ r : ZMod N, ((omega (N := N)) ^ (r.val*j.val))⁻¹ • S^r.val := by
  simp only [packet, packet_coefficient, cyclicPowers]

/-- Concrete complex-matrix version, including the Hermitian projector condition. -/
theorem finite_cyclic_projectors {n : Type*} [Fintype n] [DecidableEq n]
    (S : Matrix n n ℂ) (hS : S^N=1) (hU : S ∈ unitary (Matrix n n ℂ)) :
    (∀ j k : ZMod N, packet (cyclicPowers S) j * packet (cyclicPowers S) k =
      if j=k then packet (cyclicPowers S) j else 0) ∧
    (∑ j : ZMod N, packet (cyclicPowers S) j) = 1 ∧
    (∀ j : ZMod N, S * packet (cyclicPowers S) j =
      omega (N := N)^j.val • packet (cyclicPowers S) j) ∧
    ∀ j : ZMod N, (packet (cyclicPowers S) j).IsHermitian := by
  obtain ⟨hp, hs, he⟩ := cyclic_quantum_projectors S hS
  refine ⟨hp, hs, ?_, ?_⟩
  · intro j
    simpa only [character_as_power] using he j
  · intro j
    exact cyclic_packet_selfAdjoint S hS hU j

end KomorebiPaperVII.CyclicProjectors

/-! Complete declaration-level trust audit. -/
#print axioms KomorebiPaperVII.CyclicProjectors.character_sum
#print axioms KomorebiPaperVII.CyclicProjectors.packet_eigen
#print axioms KomorebiPaperVII.CyclicProjectors.packet_mul
#print axioms KomorebiPaperVII.CyclicProjectors.packet_idempotent
#print axioms KomorebiPaperVII.CyclicProjectors.packet_complete
#print axioms KomorebiPaperVII.CyclicProjectors.powers_zero
#print axioms KomorebiPaperVII.CyclicProjectors.powers_add
#print axioms KomorebiPaperVII.CyclicProjectors.powers_one
#print axioms KomorebiPaperVII.CyclicProjectors.cyclic_quantum_projectors
#print axioms KomorebiPaperVII.CyclicProjectors.star_character
#print axioms KomorebiPaperVII.CyclicProjectors.packet_selfAdjoint
#print axioms KomorebiPaperVII.CyclicProjectors.powers_star
#print axioms KomorebiPaperVII.CyclicProjectors.cyclic_packet_selfAdjoint
#print axioms KomorebiPaperVII.CyclicProjectors.omega_exponential
#print axioms KomorebiPaperVII.CyclicProjectors.character_as_power
#print axioms KomorebiPaperVII.CyclicProjectors.packet_coefficient
#print axioms KomorebiPaperVII.CyclicProjectors.cyclic_projector_formula
#print axioms KomorebiPaperVII.CyclicProjectors.finite_cyclic_projectors
