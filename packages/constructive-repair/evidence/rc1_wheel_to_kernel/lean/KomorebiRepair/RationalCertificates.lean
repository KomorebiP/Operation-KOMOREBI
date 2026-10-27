import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.Rank

/-!
Exact rational matrix certificates. Fixed input matrices are never supplied by
certificate fields. Boolean failure is not a proof of infeasibility.
- Rational witnesses are checked, not exhaustively enumerated.
- Finite menu optimality is relative to the declared menu, admissibility and cost.
-/
set_option autoImplicit false
namespace KomorebiRepair.RationalCertificates

abbrev Mat (rows cols : ℕ) := Matrix (Fin rows) (Fin cols) ℚ

structure Problem (m n q s : ℕ) where
  D : Mat m n
  E : Mat m q
  R : Mat m s
  allowed : Finset (Fin q) → Bool
  cost : Finset (Fin q) → ℕ

variable {m n q s : ℕ}

def masked (P : Problem m n q s) (S : Finset (Fin q)) : Mat m q :=
  Matrix.of fun i j => if j ∈ S then P.E i j else 0

abbrev Equation (P : Problem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) : Prop :=
  P.D * U + masked P S * W = -P.R

def Feasible (P : Problem m n q s) (S : Finset (Fin q)) : Prop :=
  ∃ U : Mat n s, ∃ W : Mat q s, Equation P S U W

abbrev Separates (P : Problem m n q s) (S : Finset (Fin q))
    (Y : Mat 1 m) : Prop :=
  Y * P.D = 0 ∧ Y * masked P S = 0 ∧ Y * P.R ≠ 0

def checkRepair (P : Problem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) : Bool :=
  decide (P.allowed S = true ∧ Equation P S U W)

def checkSeparator (P : Problem m n q s) (S : Finset (Fin q))
    (Y : Mat 1 m) : Bool := decide (Separates P S Y)

theorem checkRepair_sound (P : Problem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) (h : checkRepair P S U W = true) :
    P.allowed S = true ∧ Feasible P S := by
  have hs : P.allowed S = true ∧ Equation P S U W := of_decide_eq_true h
  exact ⟨hs.1, ⟨U, W, hs.2⟩⟩

theorem annihilator_kills_residual {a b c d t : ℕ}
    (D : Mat a b) (E : Mat a c) (R : Mat a d)
    (U : Mat b d) (W : Mat c d) (Y : Mat t a)
    (hEq : D * U + E * W = -R) (hYD : Y * D = 0) (hYE : Y * E = 0) :
    Y * R = 0 := by
  have hneg : -(Y * R) = 0 := by
    calc
      -(Y * R) = Y * (-R) := (Matrix.mul_neg Y R).symm
      _ = Y * (D * U + E * W) := congrArg (fun Z : Mat a d => Y * Z) hEq.symm
      _ = 0 := by
        simp only [Matrix.mul_add, ← Matrix.mul_assoc, hYD, hYE, Matrix.zero_mul, zero_add]
  exact neg_eq_zero.mp hneg

theorem separator_sound (P : Problem m n q s) (S : Finset (Fin q))
    (Y : Mat 1 m) (h : Separates P S Y) : ¬ Feasible P S := by
  rintro ⟨U, W, hEq⟩
  exact h.2.2 (annihilator_kills_residual P.D (masked P S) P.R U W Y hEq h.1 h.2.1)

theorem checkSeparator_sound (P : Problem m n q s) (S : Finset (Fin q))
    (Y : Mat 1 m) (h : checkSeparator P S Y = true) : ¬ Feasible P S := by
  exact separator_sound P S Y (of_decide_eq_true h)

def checkOptimal (P : Problem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) (reject : Finset (Fin q) → Mat 1 m) : Bool :=
  decide (P.allowed S = true ∧ Equation P S U W ∧
    ∀ T : Finset (Fin q), P.allowed T = true → P.cost T < P.cost S →
      Separates P T (reject T))

theorem checkOptimal_sound (P : Problem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) (reject : Finset (Fin q) → Mat 1 m)
    (h : checkOptimal P S U W reject = true) :
    P.allowed S = true ∧ Feasible P S ∧
    ∀ T : Finset (Fin q), P.allowed T = true → Feasible P T → P.cost S ≤ P.cost T := by
  have hc : P.allowed S = true ∧ Equation P S U W ∧
      ∀ T : Finset (Fin q), P.allowed T = true → P.cost T < P.cost S →
        Separates P T (reject T) := of_decide_eq_true h
  rcases hc with ⟨hAllowed, hEq, hReject⟩
  refine ⟨hAllowed, ⟨U, W, hEq⟩, ?_⟩
  intro T hT hFeasible
  exact le_of_not_gt fun hCheaper => separator_sound P T (reject T)
    (hReject T hT hCheaper) hFeasible

def checkNoRepair (P : Problem m n q s) (reject : Finset (Fin q) → Mat 1 m) : Bool :=
  decide (∀ S : Finset (Fin q), P.allowed S = true → Separates P S (reject S))

theorem checkNoRepair_sound (P : Problem m n q s)
    (reject : Finset (Fin q) → Mat 1 m) (h : checkNoRepair P reject = true) :
    ∀ S : Finset (Fin q), P.allowed S = true → ¬ Feasible P S := by
  have hc : ∀ S : Finset (Fin q), P.allowed S = true → Separates P S (reject S) :=
    of_decide_eq_true h
  intro S hAllowed
  exact separator_sound P S (reject S) (hc S hAllowed)

theorem dimension_certificate_right_inverse {a b d t w : ℕ}
    (D : Mat a b) (R : Mat a d) (H : Mat t a) (K : Mat d t)
    (E : Mat a w) (U : Mat b d) (W : Mat w d)
    (hHD : H * D = 0) (hHRK : (H * R) * K = 1)
    (hEq : D * U + E * W = -R) :
    (H * E) * (-(W * K)) = 1 := by
  have hProduct : (H * E) * (W * K) = -(1 : Mat t t) := by
    calc
      (H * E) * (W * K) = (H * (D * U + E * W)) * K := by
        simp only [Matrix.mul_add, ← Matrix.mul_assoc, hHD, Matrix.zero_mul, zero_add]
      _ = (H * (-R)) * K := by rw [hEq]
      _ = -((H * R) * K) := by rw [Matrix.mul_neg, Matrix.neg_mul]
      _ = -1 := by rw [hHRK]
  calc
    (H * E) * (-(W * K)) = -((H * E) * (W * K)) := Matrix.mul_neg _ _
    _ = 1 := by rw [hProduct, neg_neg]

theorem width_le_of_right_inverse {t w : ℕ}
    (A : Mat t w) (B : Mat w t) (h : A * B = 1) : t ≤ w := by
  calc
    t = Matrix.rank (1 : Mat t t) := by simp
    _ = Matrix.rank (A * B) := by rw [h]
    _ ≤ A.rank := Matrix.rank_mul_le_left A B
    _ ≤ w := Matrix.rank_le_width A

theorem dimension_certificate_lower_bound {a b d t w : ℕ}
    (D : Mat a b) (R : Mat a d) (H : Mat t a) (K : Mat d t)
    (E : Mat a w) (U : Mat b d) (W : Mat w d)
    (hHD : H * D = 0) (hHRK : (H * R) * K = 1)
    (hEq : D * U + E * W = -R) : t ≤ w := by
  exact width_le_of_right_inverse (H * E) (-(W * K))
    (dimension_certificate_right_inverse D R H K E U W hHD hHRK hEq)

def checkDimension {a b d t : ℕ}
    (D : Mat a b) (R : Mat a d) (E : Mat a t) (U : Mat b d) (W : Mat t d)
    (H : Mat t a) (K : Mat d t) : Bool :=
  decide (D * U + E * W = -R ∧ H * D = 0 ∧ (H * R) * K = 1)

theorem checkDimension_sound {a b d t : ℕ}
    (D : Mat a b) (R : Mat a d) (E : Mat a t) (U : Mat b d) (W : Mat t d)
    (H : Mat t a) (K : Mat d t) (h : checkDimension D R E U W H K = true) :
    D * U + E * W = -R ∧
    ∀ (w : ℕ) (E' : Mat a w) (U' : Mat b d) (W' : Mat w d),
      D * U' + E' * W' = -R → t ≤ w := by
  have hc : D * U + E * W = -R ∧ H * D = 0 ∧ (H * R) * K = 1 :=
    of_decide_eq_true h
  refine ⟨hc.1, ?_⟩
  intro w E' U' W' hEq
  exact dimension_certificate_lower_bound D R H K E' U' W' hc.2.1 hc.2.2 hEq

def checkRank {a b d : ℕ} (A : Mat a b) (F : Mat a d) (G : Mat d b)
    (P : Mat d a) (Q : Mat b d) : Bool := decide (A = F * G ∧ (P * A) * Q = 1)

theorem checkRank_sound {a b d : ℕ} (A : Mat a b) (F : Mat a d) (G : Mat d b)
    (P : Mat d a) (Q : Mat b d) (h : checkRank A F G P Q = true) : A.rank = d := by
  have hc : A = F * G ∧ (P * A) * Q = 1 := of_decide_eq_true h
  have hUpper : A.rank ≤ d := by
    calc
      A.rank = (F * G).rank := congrArg Matrix.rank hc.1
      _ ≤ F.rank := Matrix.rank_mul_le_left F G
      _ ≤ d := Matrix.rank_le_width F
  have hLower : d ≤ A.rank := by
    calc
      d = Matrix.rank (1 : Mat d d) := by simp
      _ = ((P * A) * Q).rank := by rw [hc.2]
      _ ≤ (P * A).rank := Matrix.rank_mul_le_left (P * A) Q
      _ ≤ A.rank := Matrix.rank_mul_le_right P A
  exact Nat.le_antisymm hUpper hLower

end KomorebiRepair.RationalCertificates
