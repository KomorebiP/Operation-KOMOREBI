import PaperXI.ValuationRamification
import Mathlib.RingTheory.Filtration
import Mathlib.Data.Finset.Lattice.Fold

/-! Separated local rings and finite faithful automorphism groups have a terminating
lower congruence filtration. This justifies finite support of the conductor sum;
eventual triviality is a theorem, not an assumed cutoff. -/
set_option autoImplicit false
noncomputable section
open scoped Classical
namespace PaperXI.RamificationSeparation
open PaperXI.ValuationRamification
variable (R D : Type*) [CommRing R] [IsLocalRing R] [IsNoetherianRing R]
  [Group D] [MulSemiringAction D R] [FaithfulSMul D R]

/-- Krull intersection separates automorphisms that agree to every depth. -/
theorem mem_all_lower_iff (g : D) : (∀ i, g ∈ lower R D i) ↔ g = 1 := by
  constructor
  · intro hg
    apply eq_of_smul_eq_smul (α := R)
    intro x
    rw [one_smul]
    apply sub_eq_zero.mp
    have hx : g • x - x ∈ ⨅ n : ℕ, (IsLocalRing.maximalIdeal R)^n := by
      rw [Submodule.mem_iInf]
      intro n
      cases n with
      | zero => simp
      | succ n => exact hg n x
    rw [Ideal.iInf_pow_eq_bot_of_isLocalRing (IsLocalRing.maximalIdeal R)
      Ideal.IsPrime.ne_top'] at hx
    exact hx
  · rintro rfl i
    exact (lower R D i).one_mem

/-- A finite group admits a single cutoff valid for every automorphism. -/
theorem eventually_trivial [Finite D] : ∃ N : ℕ, ∀ i, N ≤ i → lower R D i = ⊥ := by
  classical
  let := Fintype.ofFinite D
  have hex : ∀ g : D, ∃ n : ℕ, ∀ i, n ≤ i → g ∈ lower R D i → g = 1 := by
    intro g
    by_cases hg : g = 1
    · exact ⟨0, fun _ _ _ => hg⟩
    · have hn : ¬ ∀ i, g ∈ lower R D i := fun hh => hg ((mem_all_lower_iff R D g).mp hh)
      obtain ⟨n, hn⟩ := not_forall.mp hn
      exact ⟨n, fun i hi hh => False.elim (hn (antitone R D hi hh))⟩
  choose n hn using hex
  refine ⟨Finset.univ.sup n, fun i hi => ?_⟩
  apply le_antisymm
  · intro g hg
    exact hn g i (le_trans (Finset.le_sup (f := n) (Finset.mem_univ g)) hi) hg
  · exact bot_le

section Valuation
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]

/-- Restricting a decomposition-group element to its valuation ring is faithful:
every field element or its inverse lies in that ring. -/
instance valuation_faithful (A : ValuationSubring L) :
    FaithfulSMul (A.decompositionSubgroup K) A where
  eq_of_smul_eq_smul {g h} hh := by
    apply Subtype.ext
    apply AlgEquiv.ext
    intro x
    rcases A.mem_or_inv_mem x with hx | hx
    · exact congrArg (fun z : A => (z : L)) (hh ⟨x, hx⟩)
    · have hi := congrArg (fun z : A => (z : L)) (hh ⟨x⁻¹, hx⟩)
      change g.val (x⁻¹) = h.val (x⁻¹) at hi
      simpa only [map_inv₀, inv_inj] using hi

/-- A valuation-ring specialization with derived faithfulness. -/
theorem valuation_eventually_trivial (A : ValuationSubring L)
    [IsNoetherianRing A] [Finite (A.decompositionSubgroup K)] :
    ∃ N : ℕ, ∀ i, N ≤ i → lower A (A.decompositionSubgroup K) i = ⊥ :=
  eventually_trivial A (A.decompositionSubgroup K)

end Valuation
end PaperXI.RamificationSeparation
