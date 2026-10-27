module
public import PolynomialPrescribedTowerUnique

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialParameterTowerControls

open MvPolynomial Komorebi.PolynomialPadicLift Komorebi.PolynomialParameterSystem

local instance : Fact (Nat.Prime 2) := ⟨by decide⟩

/-- One equation, two solved coordinates, and one parameter. -/
def firstSolved : Fin 1 → MvPolynomial (Fin (2 + 1)) ℤ := fun _ => X 0

/-- The rectangular solved block is surjective. -/
theorem firstSolved_surjective :
    Function.Surjective (PolynomialPrescribedSystem.solvedJacobian 2 firstSolved (fun _ => 0)) := by
  intro t
  refine ⟨![t 0, 0], ?_⟩
  ext i
  simp [PolynomialPrescribedSystem.solvedJacobian, firstSolved,
    Fin.eq_zero i, Fin.sum_univ_two]

/-- Surjectivity of a rectangular solved block permits distinct exact roots with the same parameter.
Both roots lie in the initial ball modulo two, so square-case uniqueness cannot be generalized. -/
theorem rectangular_same_parameter_nonunique :
    ∃ b c : Fin (2 + 1) → ℤ_[2],
      (∀ i, padicEval 2 firstSolved b i = 0) ∧
      (∀ i, padicEval 2 firstSolved c i = 0) ∧
      (∀ i, (2 : ℤ_[2])^1 ∣ b i - ((0 : Fin (2 + 1) → ℤ) i : ℤ_[2])) ∧
      (∀ i, (2 : ℤ_[2])^1 ∣ c i - ((0 : Fin (2 + 1) → ℤ) i : ℤ_[2])) ∧
      freePart (e := 2) (q := 1) b = freePart c ∧ b ≠ c := by
  refine ⟨![0, 0, 0], ![0, 2, 0], ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro i
    simp [padicEval, firstSolved]
  · intro i
    simp [padicEval, firstSolved]
  · intro i
    fin_cases i <;> simp
  · intro i
    fin_cases i <;> simp
  · ext j
    fin_cases j
    simp [freePart]
  · intro h
    have hi := congrFun h 1
    norm_num at hi

end Komorebi.PolynomialParameterTowerControls
