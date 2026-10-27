import KomorebiLSM.RationalFeasibility
import Mathlib.Logic.Encodable.Pi
import Mathlib.Data.Rat.Encodable

/-! P45: executable exhaustive rational certificate enumeration. A rational right
inverse witnesses full row rank; all other checks are rational equalities or signs.
The finite-fuel interface is resumable by increasing fuel and makes no negative
existence claim. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalSearch
open scoped BigOperators

/-- Width, synthesis, branch lifts, initial coefficients and a right inverse. -/
abbrev Candidate (r s : ℕ) := Σ m : ℕ,
  (Matrix (Fin r) (Fin m) ℚ ×
   (Fin s → Matrix (Fin m) (Fin m) ℚ) ×
   (Fin m → ℚ) × Matrix (Fin m) (Fin r) ℚ)

def synthesis {r s : ℕ} (c : Candidate r s) := c.2.1
def lifts {r s : ℕ} (c : Candidate r s) := c.2.2.1
def initial {r s : ℕ} (c : Candidate r s) := c.2.2.2.1
def rightInverse {r s : ℕ} (c : Candidate r s) := c.2.2.2.2

/-- Every condition is finite and decidable over exact rationals. -/
def Valid {r s : ℕ} (l z : Fin r → ℚ) (B : Fin s → Matrix (Fin r) (Fin r) ℚ)
    (c : Candidate r s) : Prop :=
  (∀ j, ∑ i, l i * synthesis c i j = 1) ∧
  synthesis c * rightInverse c = 1 ∧
  (∀ t, B t * synthesis c = synthesis c * lifts c t) ∧
  (∀ t i j, 0 ≤ lifts c t i j) ∧
  (∀ j, 0 ≤ initial c j) ∧
  (∑ j, initial c j) = 1 ∧
  (synthesis c).mulVec (initial c) = z

instance validDecidable {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s) : Decidable (Valid l z B c) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))

/-- Decode one natural number and check the entire witness exactly. -/
def checkCode {r s : ℕ} (l z : Fin r → ℚ) (B : Fin s → Matrix (Fin r) (Fin r) ℚ)
    (k : ℕ) : Option (Candidate r s) :=
  (Encodable.decode k).filter (fun c => decide (Valid l z B c))

/-- Exhaustive dovetailing over widths and every rational entry. -/
def search {r s : ℕ} (l z : Fin r → ℚ) (B : Fin s → Matrix (Fin r) (Fin r) ℚ) :
    ℕ → Option (Candidate r s)
  | 0 => none
  | n+1 => (search l z B n).or (checkCode l z B n)

theorem checkCode_sound {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (k : ℕ) (c : Candidate r s)
    (h : checkCode l z B k = some c) : Valid l z B c := by
  unfold checkCode at h
  cases hd : (Encodable.decode k : Option (Candidate r s)) with
  | none => simp [hd] at h
  | some d =>
    by_cases hv : Valid l z B d
    · simp [hd,hv] at h
      subst d
      exact hv
    · simp [hd,hv] at h

theorem checkCode_encode {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) : checkCode l z B (Encodable.encode c) = some c := by
  simp [checkCode,Encodable.encodek,h]

theorem search_sound {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (n : ℕ) (c : Candidate r s)
    (h : search l z B n = some c) : Valid l z B c := by
  induction n with
  | zero => simp [search] at h
  | succ n ih =>
    cases hn : search l z B n with
    | none => exact checkCode_sound l z B n c (by simpa [search,hn] using h)
    | some d =>
      have he : d = c := by simpa [search,hn] using h
      subst d
      exact ih hn

theorem search_complete_rational {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) : ∃ d, search l z B (Encodable.encode c + 1) = some d := by
  cases hn : search l z B (Encodable.encode c) with
  | none => exact ⟨c, by simp [search,hn,checkCode_encode l z B c h]⟩
  | some d => exact ⟨d, by simp [search,hn]⟩

theorem search_persistent {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (n k : ℕ) (c : Candidate r s)
    (h : search l z B n = some c) : search l z B (n+k) = some c := by
  induction k with
  | zero => simpa using h
  | succ k ih => simpa [search,ih]

/-- Exact model equations and signs over the real interpretation of the witness. -/
def realMatrix {n m : ℕ} (M : Matrix (Fin n) (Fin m) ℚ) : Matrix (Fin n) (Fin m) ℝ :=
  fun i j => M i j

theorem realMatrix_mul {n m k : ℕ} (M : Matrix (Fin n) (Fin m) ℚ)
    (N : Matrix (Fin m) (Fin k) ℚ) : realMatrix (M*N) = realMatrix M * realMatrix N := by
  ext i j
  simp [realMatrix,Matrix.mul_apply]

theorem realMatrix_one (n : ℕ) : realMatrix (1 : Matrix (Fin n) (Fin n) ℚ) = 1 := by
  ext i j
  simp [realMatrix,Matrix.one_apply]

theorem real_synthesis_surjective {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) : Function.Surjective (realMatrix (synthesis c)).mulVecLin := by
  intro x
  refine ⟨(realMatrix (rightInverse c)).mulVec x, ?_⟩
  change (realMatrix (synthesis c)).mulVec ((realMatrix (rightInverse c)).mulVec x) = x
  rw [← Matrix.mulVec_mulVec,← realMatrix_mul,h.2.1,realMatrix_one,Matrix.one_mulVec]

end Komorebi.LSM.RationalSearch
