import KomorebiRepair.RationalCertificates

/-!
Attained minimum repair from exact rational matrix certificates.
LD = 0 makes L a detector. DP + KL = I makes it faithful for this problem.
Neither the detector nor the attaining matrices are assumed to arise from
an additional native arithmetic or geometric construction.
-/
set_option autoImplicit false
namespace KomorebiRepair.RationalCertificates
variable {m n d s t : ℕ}

theorem split_constructs_repair
    (D : Mat m n) (R : Mat m s) (P : Mat n m)
    (K : Mat m d) (L : Mat d m) (F : Mat d t) (G : Mat t s)
    (hSplit : D * P + K * L = 1) (hFactor : L * R = F * G) :
    D * (-(P * R)) + (K * F) * (-G) = -R := by
  have hReconstruction : D * (P * R) + (K * F) * G = R := by
    calc
      D * (P * R) + (K * F) * G = (D * P) * R + K * (F * G) := by
        simp only [Matrix.mul_assoc]
      _ = (D * P) * R + K * (L * R) := by rw [← hFactor]
      _ = (D * P + K * L) * R := by simp only [Matrix.add_mul, Matrix.mul_assoc]
      _ = R := by rw [hSplit, Matrix.one_mul]
  calc
    D * (-(P * R)) + (K * F) * (-G) = -(D * (P * R) + (K * F) * G) := by
      simp only [Matrix.mul_neg, neg_add]
    _ = -R := congrArg (fun Z : Mat m s => -Z) hReconstruction

theorem split_correctable_iff
    (D : Mat m n) (R : Mat m s) (P : Mat n m) (K : Mat m d) (L : Mat d m)
    (hLD : L * D = 0) (hSplit : D * P + K * L = 1) :
    (∃ X : Mat n s, D * X = -R) ↔ L * R = 0 := by
  constructor
  · rintro ⟨X, hX⟩
    have h : -(L * R) = 0 := by
      calc
        -(L * R) = L * (-R) := (Matrix.mul_neg L R).symm
        _ = L * (D * X) := by rw [hX]
        _ = 0 := by rw [← Matrix.mul_assoc, hLD, Matrix.zero_mul]
    exact neg_eq_zero.mp h
  · intro hz
    refine ⟨-(P * R), ?_⟩
    have h : D * (P * R) = R := by
      calc
        D * (P * R) = (D * P + K * L) * R := by
          simp only [Matrix.add_mul, Matrix.mul_assoc, hz, Matrix.mul_zero, add_zero]
        _ = R := by rw [hSplit, Matrix.one_mul]
    rw [Matrix.mul_neg, h]

def checkOptimalConstruction
    (D : Mat m n) (R : Mat m s) (P : Mat n m)
    (K : Mat m d) (L : Mat d m) (F : Mat d t) (G : Mat t s)
    (J : Mat t d) (Q : Mat s t) : Bool :=
  decide (L * D = 0 ∧ D * P + K * L = 1 ∧ L * R = F * G ∧
    (J * (L * R)) * Q = 1)

theorem checkOptimalConstruction_sound
    (D : Mat m n) (R : Mat m s) (P : Mat n m)
    (K : Mat m d) (L : Mat d m) (F : Mat d t) (G : Mat t s)
    (J : Mat t d) (Q : Mat s t)
    (h : checkOptimalConstruction D R P K L F G J Q = true) :
    D * (-(P * R)) + (K * F) * (-G) = -R ∧
    ∀ (w : ℕ) (E' : Mat m w) (U' : Mat n s) (W' : Mat w s),
      D * U' + E' * W' = -R → t ≤ w := by
  have hc : L * D = 0 ∧ D * P + K * L = 1 ∧ L * R = F * G ∧
      (J * (L * R)) * Q = 1 := of_decide_eq_true h
  rcases hc with ⟨hLD, hSplit, hFactor, hRank⟩
  refine ⟨split_constructs_repair D R P K L F G hSplit hFactor, ?_⟩
  intro w E' U' W' hEq
  have hHD : (J * L) * D = 0 := by rw [Matrix.mul_assoc, hLD, Matrix.mul_zero]
  have hHRQ : ((J * L) * R) * Q = 1 := by
    simpa only [Matrix.mul_assoc] using hRank
  exact dimension_certificate_lower_bound D R (J * L) Q E' U' W' hHD hHRQ hEq

/-- Additional legal-subspace evidence is checked in the original target. -/
theorem constructed_repair_in_legal_image {a : ℕ}
    (K : Mat m d) (F : Mat d t) (A : Mat m a) (Z : Mat a t)
    (h : K * F = A * Z) (W : Mat t s) :
    (K * F) * W = A * (Z * W) := by rw [h, Matrix.mul_assoc]

/-- An explicit decoder for numeric cells. Wire-format parsing is external;
these typed cells are what the kernel computes on. Zero denominators are rejected. -/
abbrev WireCell := ℤ × ℕ

def decodeCell (x : WireCell) : Option ℚ :=
  if x.2 = 0 then none else some ((x.1 : ℚ) / (x.2 : ℚ))

theorem decodeCell_zero (a : ℤ) : decodeCell (a, 0) = none := by
  simp [decodeCell]

theorem decodeCell_nonzero (a : ℤ) (b : ℕ) (h : b ≠ 0) :
    decodeCell (a, b) = some ((a : ℚ) / (b : ℚ)) := by
  simp [decodeCell, h]

theorem decodeCell_sound (x : WireCell) (r : ℚ) (h : decodeCell x = some r) :
    x.2 ≠ 0 ∧ r = (x.1 : ℚ) / (x.2 : ℚ) := by
  unfold decodeCell at h
  split at h
  · contradiction
  · exact ⟨by assumption, (Option.some.inj h).symm⟩

end KomorebiRepair.RationalCertificates
