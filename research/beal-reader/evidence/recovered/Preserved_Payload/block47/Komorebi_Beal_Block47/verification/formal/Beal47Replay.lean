import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Set.Lattice.Bounded
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring


/-!
Generic interfaces for a lane-refined exclusion certificate.

There are no number-theoretic assumptions, external theorem axioms, or Beal
nonexistence claims here. In an application, `Candidate` must contain every
globally fixed choice, including the modular form and a prime above seven.
-/

namespace KomorebiBeal.Block47

variable {Lane Candidate Test State FineLane : Type*}

/-- Candidates satisfying every selected test in a single arithmetic lane. -/
def survivors (compatible : Lane → Candidate → Test → Prop)
    (tests : Set Test) (lane : Lane) : Set Candidate :=
  {candidate | ∀ test ∈ tests, compatible lane candidate test}

theorem survivors_mono_tests
    (compatible : Lane → Candidate → Test → Prop) (lane : Lane)
    {small large : Set Test} (h : small ⊆ large) :
    survivors compatible large lane ⊆ survivors compatible small lane := by
  intro candidate hc test ht
  exact hc test (h ht)

theorem survivors_union
    (compatible : Lane → Candidate → Test → Prop) (lane : Lane)
    (first second : Set Test) :
    survivors compatible (first ∪ second) lane =
      survivors compatible first lane ∩ survivors compatible second lane := by
  ext candidate
  constructor
  · intro h
    exact ⟨fun test ht => h test (Or.inl ht),
      fun test ht => h test (Or.inr ht)⟩
  · intro h test ht
    cases ht with
    | inl hfirst => exact h.1 test hfirst
    | inr hsecond => exact h.2 test hsecond

theorem survivors_refinement
    (fine : FineLane → Candidate → Test → Prop)
    (coarse : Lane → Candidate → Test → Prop)
    (parent : FineLane → Lane) (tests : Set Test)
    (transfer : ∀ lane candidate test,
      fine lane candidate test → coarse (parent lane) candidate test)
    (lane : FineLane) :
    survivors fine tests lane ⊆ survivors coarse tests (parent lane) := by
  intro candidate hc test ht
  exact transfer lane candidate test (hc test ht)

/-- A contradiction certificate may depend on the arithmetic lane, but its
candidate is held fixed throughout all selected tests in that lane. -/
theorem exclusion_from_empty_survivors
    (solution : State → Prop) (phase : State → Lane → Prop)
    (label : State → Candidate → Prop)
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Lane → Set Test)
    (cover : ∀ state, solution state → ∃ lane, phase state lane)
    (attachment : ∀ state, solution state → ∃ candidate, label state candidate)
    (sound : ∀ state, solution state → ∀ lane, phase state lane →
      ∀ candidate, label state candidate →
        candidate ∈ survivors compatible (tests lane) lane)
    (empty : ∀ lane, survivors compatible (tests lane) lane = ∅) :
    ∀ state, ¬solution state := by
  intro state hs
  obtain ⟨lane, hl⟩ := cover state hs
  obtain ⟨candidate, hc⟩ := attachment state hs
  have hmem := sound state hs lane hl candidate hc
  rw [empty lane] at hmem
  exact hmem

/-- Explicit finite exclusion witnesses supply the empty-survivor hypothesis. -/
theorem finite_certificate_empty
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Lane → Finset Test)
    (reject : ∀ lane candidate,
      ∃ test ∈ tests lane, ¬compatible lane candidate test) :
    ∀ lane, survivors compatible (↑(tests lane)) lane = ∅ := by
  intro lane
  apply Set.eq_empty_iff_forall_notMem.mpr
  intro candidate hc
  obtain ⟨test, ht, hbad⟩ := reject lane candidate
  exact hbad (hc test ht)

/-- Refining a covering family remains exhaustive only with a proved lift. -/
theorem refinement_preserves_cover
    (solution : State → Prop) (phase : State → Lane → Prop)
    (finePhase : State → FineLane → Prop)
    (cover : ∀ state, solution state → ∃ lane, phase state lane)
    (lift : ∀ state, solution state → ∀ lane, phase state lane →
      ∃ fineLane, finePhase state fineLane) :
    ∀ state, solution state → ∃ fineLane, finePhase state fineLane := by
  intro state hs
  obtain ⟨lane, hl⟩ := cover state hs
  exact lift state hs lane hl

/-- Saturated tests cannot produce an exclusion certificate. This is a
statement about a fixed candidate satisfying all tests, not separate choices. -/
theorem fixed_witness_prevents_empty
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Set Test) (lane : Lane) (candidate : Candidate)
    (witness : ∀ test ∈ tests, compatible lane candidate test) :
    survivors compatible tests lane ≠ ∅ := by
  intro empty
  have hmem : candidate ∈ survivors compatible tests lane := witness
  rw [empty] at hmem
  exact hmem

end KomorebiBeal.Block47


/-! Exact counterexamples to losing candidate labels or paired coordinates. -/

namespace KomorebiBeal.Block47

/-- Separate tests can each pass after choosing a different label. -/
theorem each_test_has_candidate :
    ∀ test : Bool, ∃ candidate : Bool, candidate = test := by
  intro test
  exact ⟨test, rfl⟩

/-- No single label passes both tests. -/
theorem no_candidate_passes_every_test :
    ¬∃ candidate : Bool, ∀ test : Bool, candidate = test := by
  rintro ⟨candidate, h⟩
  have impossible : (false : Bool) = true := (h false).symm.trans (h true)
  cases impossible

/-- The two tests become incompatible only when their labels are intersected. -/
theorem correlated_tests_have_empty_intersection :
    survivors (fun (_ : Unit) (candidate test : Bool) => candidate = test)
      Set.univ () = ∅ := by
  apply Set.eq_empty_iff_forall_notMem.mpr
  intro candidate h
  exact no_candidate_passes_every_test ⟨candidate, fun test => h test (Set.mem_univ test)⟩

/-- Every coordinate separately occurs in the diagonal relation. -/
theorem diagonal_coordinate_projections_are_full :
    (∀ left : Bool, ∃ right : Bool, left = right) ∧
    (∀ right : Bool, ∃ left : Bool, left = right) := by
  exact ⟨fun left => ⟨left, rfl⟩, fun right => ⟨right, rfl⟩⟩

/-- Passing both marginal membership tests does not imply paired membership. -/
theorem diagonal_marginals_lose_correlation :
    (∃ right : Bool, false = right) ∧
    (∃ left : Bool, left = true) ∧ ¬((false : Bool) = true) := by
  exact ⟨⟨false, rfl⟩, ⟨true, rfl⟩, Bool.false_ne_true⟩

end KomorebiBeal.Block47


namespace KomorebiBeal.Block47

open Polynomial

/-- The sextic reduced modulo seven. Its geometric interpretation is external. -/
noncomputable def freySexticModSeven (a b : ZMod 7) : Polynomial (ZMod 7) :=
  X ^ 6 + C (10 * b) * X ^ 3 + C (12 * a) * X + C (5 * b ^ 2)

theorem frey_cube_expansion (a b : ZMod 7) :
    freySexticModSeven a b ^ 3 =
      X ^ 18 + C (30 * b) * X ^ 15 + C (36 * a) * X ^ 13 +
      C (315 * b ^ 2) * X ^ 12 + C (720 * a * b) * X ^ 10 +
      C (1300 * b ^ 3) * X ^ 9 + C (432 * a ^ 2) * X ^ 8 +
      C (3960 * a * b ^ 2) * X ^ 7 + C (1575 * b ^ 4) * X ^ 6 +
      C (4320 * a ^ 2 * b) * X ^ 5 + C (3600 * a * b ^ 3) * X ^ 4 +
      C (1728 * a ^ 3 + 750 * b ^ 5) * X ^ 3 +
      C (2160 * a ^ 2 * b ^ 2) * X ^ 2 + C (900 * a * b ^ 4) * X +
      C (125 * b ^ 6) := by
  simp only [freySexticModSeven, map_mul, map_add, map_pow, map_ofNat]
  ring

theorem frey_cube_coeff_six (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 6 = 0 := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (1575 : ZMod 7) = 0 from by decide]
  simp only [zero_mul]

theorem frey_cube_coeff_five (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 5 = a ^ 2 * b := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (4320 : ZMod 7) = 1 from by decide]
  simp only [one_mul]

theorem frey_cube_coeff_thirteen (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 13 = a := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (36 : ZMod 7) = 1 from by decide]
  simp only [one_mul]

theorem frey_cube_coeff_twelve (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 12 = 0 := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (315 : ZMod 7) = 0 from by decide]
  simp only [zero_mul]

/-- The determinant expression extracted from the four polynomial coefficients. -/
theorem frey_coeff_determinant (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 6 *
        ((freySexticModSeven a b) ^ 3).coeff 12 -
      ((freySexticModSeven a b) ^ 3).coeff 5 *
        ((freySexticModSeven a b) ^ 3).coeff 13 = -(a ^ 3 * b) := by
  rw [frey_cube_coeff_six, frey_cube_coeff_twelve,
    frey_cube_coeff_five, frey_cube_coeff_thirteen]
  ring

/-- Matrix assembled from the four coefficient positions. Identifying this
matrix with a geometric Cartier operator is not part of this formalization. -/
noncomputable def coefficientMatrix (a b : ZMod 7) :
    Matrix (Fin 2) (Fin 2) (ZMod 7) :=
  !![((freySexticModSeven a b) ^ 3).coeff 6,
      ((freySexticModSeven a b) ^ 3).coeff 5;
     ((freySexticModSeven a b) ^ 3).coeff 13,
      ((freySexticModSeven a b) ^ 3).coeff 12]

theorem coefficientMatrix_eq (a b : ZMod 7) :
    coefficientMatrix a b = !![0, a ^ 2 * b; a, 0] := by
  simp only [coefficientMatrix, frey_cube_coeff_six, frey_cube_coeff_five,
    frey_cube_coeff_thirteen, frey_cube_coeff_twelve]

theorem coefficientMatrix_det (a b : ZMod 7) :
    (coefficientMatrix a b).det = -(a ^ 3 * b) := by
  rw [coefficientMatrix_eq, Matrix.det_fin_two_of]
  ring

theorem coefficientMatrix_square (a b : ZMod 7) :
    coefficientMatrix a b * coefficientMatrix a b =
      (a ^ 3 * b) • (1 : Matrix (Fin 2) (Fin 2) (ZMod 7)) := by
  rw [coefficientMatrix_eq]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two] <;> ring

end KomorebiBeal.Block47


