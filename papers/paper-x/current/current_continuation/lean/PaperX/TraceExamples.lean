import PaperX.TraceRecovery
import PaperX.FiniteCharacters
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-! Explicit finite-image representation example and exact failure cases.
No numerical table is claimed to come from an unspecified arithmetic carrier. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.TraceExamples

open scoped BigOperators Matrix
open PaperX.FiniteSeparation PaperX.TraceRecovery

abbrev G := Multiplicative (ZMod 2 × ZMod 2)

def chi (i : Fin 3) (g : G) : ℚ :=
  if i = 0 then 1 else if i = 1 then
    if g.toAdd.1 = 0 then 1 else -1
  else if g.toAdd.2 = 0 then 1 else -1

theorem chi_one : ∀ i, chi i 1 = 1 := by decide +kernel

theorem chi_mul : ∀ i g h, chi i (g * h) = chi i g * chi i h := by decide +kernel

def chiHom (i : Fin 3) : G →* ℚ where
  toFun := chi i
  map_one' := chi_one i
  map_mul' := chi_mul i

/-- Actual one-dimensional representations of the four-element group. -/
def rep (i : Fin 3) : Representation ℚ G (Fin 1 → ℚ) :=
  ((algebraMap ℚ (Module.End ℚ (Fin 1 → ℚ))).toMonoidHom).comp (chiHom i)

theorem rep_character (i : Fin 3) : (rep i).character = chi i := by
  funext g
  simp [Representation.character, rep, chiHom, Algebra.algebraMap_eq_smul_one,
    LinearMap.trace_one]

def samples : Fin 3 → G := ![Multiplicative.ofAdd (0,0),
  Multiplicative.ofAdd (1,0), Multiplicative.ofAdd (0,1)]

def separator : Matrix (Fin 3) (Fin 3) ℚ := !![1,1,1; 1,-1,1; 1,1,-1]

theorem actual_trace_matrix : sampleMatrix (fun i => (rep i).character) samples = separator := by
  simp_rw [rep_character]
  decide +kernel

theorem distinct_samples : Function.Injective samples := by decide +kernel

theorem determinant_four : separator.det = 4 := by
  rw [Matrix.det_fin_three]; decide +kernel

theorem determinant_nonzero : separator.det ≠ 0 := by rw [determinant_four]; norm_num

theorem actual_characters_independent :
    LinearIndependent ℚ (fun i => (rep i).character) := by
  apply independent_of_separator _ samples
  rw [actual_trace_matrix]
  exact determinant_nonzero

def multiplicities : Fin 3 → ℕ := ![2,0,1]
def capacities : Fin 3 → ℕ := ![3,2,2]
def observed : Fin 3 → ℚ := ![3,3,1]

theorem observed_trace : separator *ᵥ (fun i => (multiplicities i : ℚ)) = observed := by
  decide +kernel

theorem exact_recovery : recover separator observed = fun i => (multiplicities i : ℚ) := by
  rw [← observed_trace, recover_trace separator determinant_nonzero]

theorem multiplicities_admissible : Admissible capacities multiplicities := by unfold Admissible; decide +kernel

theorem only_natural_solution (m : Fin 3 → ℕ)
    (h : separator *ᵥ (fun i => (m i : ℚ)) = observed) : m = multiplicities := by
  exact natural_multiplicity_unique separator determinant_nonzero m multiplicities
    (h.trans observed_trace.symm)

/-- One equation has a unique rational solution but no natural multiplicity solution. -/
def fractionalTrace : Fin 3 → ℚ := ![1/2,1/2,1/2]

theorem fractional_solution : recover separator fractionalTrace = ![1/2,0,0] := by
  have h : separator *ᵥ ![(1/2 : ℚ),0,0] = fractionalTrace := by decide +kernel
  rw [← h, recover_trace separator determinant_nonzero]

theorem fractional_not_natural : ¬ ∃ m : Fin 3 → ℕ,
    separator *ᵥ (fun i => (m i : ℚ)) = fractionalTrace := by
  rintro ⟨m, hm⟩
  have he := congrArg (recover separator) hm
  rw [recover_trace separator determinant_nonzero, fractional_solution] at he
  have h0 := congrFun he 0
  norm_num at h0
  have h1 : (2 : ℚ) * (m 0 : ℚ) = 1 := by linarith
  have h2 : 2 * m 0 = 1 := by exact_mod_cast h1
  omega

/-- Integer recovery alone does not check the stated carrier capacities. -/
def excessive : Fin 3 → ℕ := ![4,0,1]

theorem excessive_not_admissible : ¬ Admissible capacities excessive := by unfold Admissible; decide +kernel

theorem no_admissible_excessive_trace : ¬ ∃ m : Fin 3 → ℕ,
    Admissible capacities m ∧
    separator *ᵥ (fun i => (m i : ℚ)) = separator *ᵥ (fun i => (excessive i : ℚ)) := by
  rintro ⟨m, hm, ht⟩
  have h := natural_multiplicity_unique separator determinant_nonzero m excessive ht
  exact excessive_not_admissible (h ▸ hm)

/-- Field extension preserves rank, but residue reduction need not. -/
theorem separator_mod2_singular :
    ( (!![1,1,1; 1,-1,1; 1,1,-1] : Matrix (Fin 3) (Fin 3) (ZMod 2))).det = 0 := by
  rw [Matrix.det_fin_three]; decide +kernel

/-- Natural multiplicities cannot be recovered from traces in characteristic two. -/
theorem natural_trace_collision_mod2 :
    (1 : Matrix (Fin 1) (Fin 1) (ZMod 2)) *ᵥ (fun _ => (0 : ZMod 2)) =
    (1 : Matrix (Fin 1) (Fin 1) (ZMod 2)) *ᵥ (fun _ => (2 : ZMod 2)) := by
  decide +kernel

end PaperX.TraceExamples
