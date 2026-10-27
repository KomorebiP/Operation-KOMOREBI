import PaperX.CommonSpine
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.NumberTheory.Padics.RingHoms
import Mathlib.Tactic

/-! A boundary for arbitrary local conditions: nontrivial representations are
not adically closed. Each nontrivial unipotent representation below becomes
invisible to any fixed finite precision, while the limiting representation is
trivial. This refutes automatic preservation of arbitrary properties. -/
set_option autoImplicit false
namespace PaperX.CompletionBoundary
open scoped Matrix
open PaperX.RepresentationLimits
variable {R : Type*} [CommRing R]

/-- A genuine representation of the additive integers (written multiplicatively). -/
def unipotent (a : R) : MatrixRep R (Multiplicative ℤ) (Fin 2) where
  toFun g := !![1, a * (Multiplicative.toAdd g : ℤ); 0, 1]
  map_one' := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp
  map_mul' g h := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [Matrix.mul_apply, Fin.sum_univ_succ, mul_add, add_comm]

/-- This supplies an actual matrix distinction, not just a descriptive label. -/
theorem unipotent_ne_trivial {a : R} (ha : a ≠ 0) : unipotent a ≠ unipotent (0 : R) := by
  intro he
  have H := congrArg (fun ρ => ρ (Multiplicative.ofAdd (1 : ℤ)) (0 : Fin 2) (1 : Fin 2)) he
  exact ha (by simpa [unipotent] using H)

@[simp] theorem trivial_apply (g : Multiplicative ℤ) : unipotent (0 : R) g = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [unipotent]

/-- A parameter in I^k is invisible to precision k. -/
theorem invisible_parameter (I : Ideal R) (k : ℕ) {a : R} (ha : a ∈ I^k) :
    reduce I (unipotent a) k = reduce I (unipotent (0 : R)) k := by
  have hz : Ideal.Quotient.mk (I^k) a = 0 := Ideal.Quotient.eq_zero_iff_mem.mpr ha
  apply MonoidHom.ext
  intro g
  apply Matrix.ext
  intro i j
  fin_cases i <;> fin_cases j <;> simp [reduce, unipotent, hz]

/-- Every finite neighborhood of the trivial representation contains a nontrivial
one, whenever I contains a nonzero element in a domain. -/
theorem nontrivial_approximations [IsDomain R] (I : Ideal R) (π : R)
    (hne : π ≠ 0) (hπ : π ∈ I) :
    ∀ k, ∃ ρ : MatrixRep R (Multiplicative ℤ) (Fin 2),
      ρ ≠ unipotent (0 : R) ∧ reduce I ρ k = reduce I (unipotent (0 : R)) k := by
  intro k
  refine ⟨unipotent (π^k), unipotent_ne_trivial (pow_ne_zero k hne), ?_⟩
  apply invisible_parameter
  exact Ideal.pow_mem_pow hπ k

/-- Higher and higher unipotent parameters vanish at every fixed precision. -/
theorem eventually_trivial_reduction (I : Ideal R) (π : R) (hπ : π ∈ I)
    (k n : ℕ) (hkn : k ≤ n) :
    reduce I (unipotent (π^n)) k = reduce I (unipotent (0 : R)) k := by
  apply invisible_parameter
  exact Ideal.pow_le_pow_right hkn (Ideal.pow_mem_pow hπ n)

/-- Literal topological convergence of the representation matrices at every
integer group element, not just a finite congruence experiment. -/
theorem unipotent_tendsto (I : Ideal R) (π : R) (hπ : π ∈ I)
    (g : Multiplicative ℤ) :
    letI : TopologicalSpace R := I.adicTopology
    Filter.Tendsto (fun n : ℕ => unipotent (π^n) g) Filter.atTop (nhds (1 : Matrix (Fin 2) (Fin 2) R)) := by
  let : TopologicalSpace R := I.adicTopology
  apply tendsto_pi_nhds.mpr
  intro i
  apply tendsto_pi_nhds.mpr
  intro j
  apply PaperX.RepresentationTopology.adic_tendsto_of_reductions I
  intro k
  apply Filter.eventually_atTop.mpr
  refine ⟨k, ?_⟩
  intro n hn
  have H := congrArg (fun ρ => ρ g i j) (eventually_trivial_reduction I π hπ k n hn)
  simpa [reduce, changeCoefficients] using H

/-- The adic-closure implication is genuinely false for the property of being
nontrivial. Increasing precision does not make arbitrary local properties stable. -/
theorem nontrivial_not_limit_stable [IsDomain R] (I : Ideal R) (π : R)
    (hne : π ≠ 0) (hπ : π ∈ I) :
    ¬ (∀ ρ : MatrixRep R (Multiplicative ℤ) (Fin 2),
      (∀ k, ∃ τ, τ ≠ unipotent (0 : R) ∧ reduce I τ k = reduce I ρ k) →
      ρ ≠ unipotent (0 : R)) := by
  intro h
  exact h (unipotent (0 : R)) (nontrivial_approximations I π hne hπ) rfl

/-- A compatible family is reconstructed uniquely, but not with an arbitrary
property shared by all approximating representatives. -/
theorem trivial_reconstructs (I : Ideal R) [IsAdicComplete I R] :
    reconstruct I (reduceFamily I (unipotent (0 : R))) = unipotent (0 : R) :=
  reconstruct_reduce I _

/-- All scalar congruences 2*x=1 modulo odd powers are solvable. -/
theorem inverse_two_mod_three_power (k : ℕ) :
    ∃ x : ZMod (3^k), 2*x = 1 := by
  have hc : Nat.Coprime 2 (3^k) := (by decide : Nat.Coprime 2 3).pow_right k
  have hu : IsUnit (2 : ZMod (3^k)) := (ZMod.isUnit_iff_coprime 2 (3^k)).mpr hc
  obtain ⟨u,hu⟩ := hu
  exact ⟨↑u⁻¹, by rw [← hu]; simp⟩

/-- Completeness cannot be dropped just because every scalar congruence is solvable. -/
theorem no_integer_inverse_two : ¬ ∃ x : ℤ, 2*x = 1 := by omega

end PaperX.CompletionBoundary
