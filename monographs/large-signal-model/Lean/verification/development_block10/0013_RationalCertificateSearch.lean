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

instance candidateEncodable (r s : ℕ) : Encodable (Candidate r s) := by
  unfold Candidate Matrix
  infer_instance

def synthesis {r s : ℕ} (c : Candidate r s) := c.2.1
def lifts {r s : ℕ} (c : Candidate r s) := c.2.2.1
def initial {r s : ℕ} (c : Candidate r s) := c.2.2.2.1
def rightInverse {r s : ℕ} (c : Candidate r s) := c.2.2.2.2

instance rationalMatrixDecidableEq (n m : ℕ) : DecidableEq (Matrix (Fin n) (Fin m) ℚ) :=
  inferInstanceAs (DecidableEq (Fin n → Fin m → ℚ))

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

set_option diagnostics true in
instance validDecidable {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s) : Decidable (Valid l z B c) :=
by
  unfold Valid
  dsimp only [synthesis,lifts,initial,rightInverse]
  exact instDecidableAnd

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
    simp [hd] at h
    exact h.2

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
  | succ k ih => simp [search,ih]

/-- Exact model equations and signs over the real interpretation of the witness. -/
def realMatrix {n m : ℕ} (M : Matrix (Fin n) (Fin m) ℚ) : Matrix (Fin n) (Fin m) ℝ :=
  fun i j => M i j

theorem realMatrix_mul {n m k : ℕ} (M : Matrix (Fin n) (Fin m) ℚ)
    (N : Matrix (Fin m) (Fin k) ℚ) : realMatrix (M*N) = realMatrix M * realMatrix N := by
  ext i j
  simp [realMatrix,Matrix.mul_apply]

theorem realMatrix_one (n : ℕ) : realMatrix (1 : Matrix (Fin n) (Fin n) ℚ) = 1 := by
  ext i j
  simp [realMatrix,Matrix.one_apply,apply_ite]

theorem real_synthesis_surjective {r s : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (c : Candidate r s)
    (h : Valid l z B c) : Function.Surjective (realMatrix (synthesis c)).mulVecLin := by
  intro x
  refine ⟨(realMatrix (rightInverse c)).mulVec x, ?_⟩
  change (realMatrix (synthesis c)).mulVec ((realMatrix (rightInverse c)).mulVec x) = x
  rw [Matrix.mulVec_mulVec,← realMatrix_mul,h.2.1,realMatrix_one,Matrix.one_mulVec]

/-- Real surjectivity of a rational synthesis yields an enumeratable rational
right inverse. This is not an extra rational-inverse hypothesis. -/
theorem rational_right_inverse {r m : ℕ} (V : Matrix (Fin r) (Fin m) ℚ)
    (hv : Function.Surjective (realMatrix V).mulVecLin) :
    ∃ R : Matrix (Fin m) (Fin r) ℚ, V * R = 1 := by
  classical
  have hc : ∀ j : Fin r, ∃ q : Fin m → ℚ, ∀ i,
      ∑ k, V i k * q k = (1 : Matrix (Fin r) (Fin r) ℚ) i j := by
    intro j
    obtain ⟨x,hx⟩ := hv (fun i => (1 : Matrix (Fin r) (Fin r) ℝ) i j)
    apply rational_solution m V (fun i => (1 : Matrix (Fin r) (Fin r) ℚ) i j) x
    intro i
    have := congrFun hx i
    simpa [Matrix.mulVecLin_apply,Matrix.mulVec, dotProduct,realMatrix,Matrix.one_apply,apply_ite] using this
  choose q hq using hc
  refine ⟨fun k j => q j k, ?_⟩
  ext i j
  exact hq j i

/-- The real witnesses in P39 can be rationalized while retaining the supplied
rational generator matrix, including all zero entries and boundary faces. -/
theorem rationalize_certificate {r s m : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (V : Matrix (Fin r) (Fin m) ℚ)
    (hv : Function.Surjective (realMatrix V).mulVecLin)
    (hn : ∀ j, ∑ i, l i * V i j = 1)
    (A : Fin s → Matrix (Fin m) (Fin m) ℝ) (alpha : Fin m → ℝ)
    (ha : ∀ t i j, 0 ≤ A t i j) (hpos : ∀ j, 0 ≤ alpha j)
    (hinit : ∀ i, ∑ j, (V i j : ℝ) * alpha j = (z i : ℝ))
    (hmass : ∑ j, alpha j = 1)
    (hinter : ∀ t, realMatrix (B t) * realMatrix V = realMatrix V * A t) :
    ∃ c : Candidate r s, Valid l z B c := by
  classical
  obtain ⟨R,hR⟩ := rational_right_inverse V hv
  have hc : ∀ t j, ∃ q : Fin m → ℚ, (∀ k, 0 ≤ q k) ∧
      (∀ i, ∑ k, V i k * q k = (B t * V) i j) := by
    intro t j
    apply rational_nonnegative_solution m V (fun i => (B t * V) i j)
      (fun k => A t k j) (fun k => ha t k j)
    intro i
    have he := congrFun (congrFun (hinter t) i) j
    have hr := congrFun (congrFun (realMatrix_mul (B t) V) i) j
    exact he.symm.trans hr.symm
  choose Aq hAq hEq using hc
  let W : (Fin r ⊕ Unit) → Fin m → ℚ
    | .inl i => V i
    | .inr _ => fun _ => 1
  let zz : (Fin r ⊕ Unit) → ℚ | .inl i => z i | .inr _ => 1
  have heq : ∀ i, ∑ j, (W i j : ℝ) * alpha j = (zz i : ℝ) := by
    intro i
    cases i with
    | inl i => exact hinit i
    | inr _ => simpa [W,zz] using hmass
  obtain ⟨q,hq,he⟩ := rational_nonnegative_solution m W zz alpha hpos heq
  refine ⟨⟨m,V,(fun t i j => Aq t j i),q,R⟩,hn,hR,?_,?_,hq,?_,?_⟩
  · intro t
    ext i j
    exact (hEq t j i).symm
  · intro t i j
    exact hAq t j i
  · simpa [W,zz,initial] using he (.inr ())
  · funext i
    exact he (.inl i)

/-- P45 conditional termination, with exactly the rational-generator hypothesis.
Real nonnegative lifts are converted by finite weak rational elimination. -/
theorem rational_finite_certificate_search {r s m : ℕ} (l z : Fin r → ℚ)
    (B : Fin s → Matrix (Fin r) (Fin r) ℚ) (V : Matrix (Fin r) (Fin m) ℚ)
    (hv : Function.Surjective (realMatrix V).mulVecLin)
    (hn : ∀ j, ∑ i, l i * V i j = 1)
    (A : Fin s → Matrix (Fin m) (Fin m) ℝ) (alpha : Fin m → ℝ)
    (ha : ∀ t i j, 0 ≤ A t i j) (hpos : ∀ j, 0 ≤ alpha j)
    (hinit : ∀ i, ∑ j, (V i j : ℝ) * alpha j = (z i : ℝ))
    (hmass : ∑ j, alpha j = 1)
    (hinter : ∀ t, realMatrix (B t) * realMatrix V = realMatrix V * A t) :
    ∃ n c, search l z B n = some c ∧ Valid l z B c := by
  obtain ⟨c,hc⟩ := rationalize_certificate l z B V hv hn A alpha ha hpos hinit hmass hinter
  obtain ⟨d,hd⟩ := search_complete_rational l z B c hc
  exact ⟨_,d,hd,search_sound l z B _ d hd⟩

end Komorebi.LSM.RationalSearch
