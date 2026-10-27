module
public import PolynomialWeightedInverse
public import PolynomialParameterSystem

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialBlockInverse
open Matrix Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialWeightedInverse
variable {e k : ℕ} {R : Type*} [CommRing R]

/-- An upper triangular block matrix in the original appended coordinate order. -/
def upperBlock (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) :
    Matrix (Fin (e + k)) (Fin (e + k)) R :=
  join (fun i => join (J i) (K i))
    (fun i => join 0 ((c • (1 : Matrix (Fin k) (Fin k) R)) i))

@[simp] theorem upperBlock_solved_solved (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) (i j : Fin e) :
    upperBlock J K c (Fin.castAdd k i) (Fin.castAdd k j) = J i j := by
  simp [upperBlock]

@[simp] theorem upperBlock_solved_free (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) (i : Fin e) (j : Fin k) :
    upperBlock J K c (Fin.castAdd k i) (Fin.natAdd e j) = K i j := by
  simp [upperBlock]

@[simp] theorem upperBlock_free_solved (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) (i : Fin k) (j : Fin e) :
    upperBlock J K c (Fin.natAdd e i) (Fin.castAdd k j) = 0 := by
  simp [upperBlock]

@[simp] theorem upperBlock_free_free (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) (i j : Fin k) :
    upperBlock J K c (Fin.natAdd e i) (Fin.natAdd e j) =
      (c • (1 : Matrix (Fin k) (Fin k) R)) i j := by
  simp [upperBlock]

/-- The block matrix acts by the expected solved and parameter formulas. -/
theorem upperBlock_mulVec_join (J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R)
    (u : Fin e → R) (v : Fin k → R) :
    (upperBlock J K c).mulVec (join u v) =
      join (J.mulVec u + K.mulVec v) (c • v) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i
  · simp [Matrix.mulVec, dotProduct, Fin.sum_univ_add]
  · simp [Matrix.mulVec, dotProduct, Fin.sum_univ_add]
    simp [Matrix.one_apply, mul_ite]

/-- The integral certificate for the augmented Jacobian. -/
def blockCertificate (A : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R) :
    Matrix (Fin (e + k)) (Fin (e + k)) R :=
  upperBlock A (-(A * K)) c

/-- A scalar left certificate transfers to the augmented system with no extra scalar loss. -/
theorem blockCertificate_mul (A J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R)
    (hAJ : A * J = c • (1 : Matrix (Fin e) (Fin e) R)) :
    blockCertificate A K c * upperBlock J K 1 =
      c • (1 : Matrix (Fin (e + k)) (Fin (e + k)) R) := by
  apply Matrix.ext_iff_mulVec.mpr
  intro v
  rw [← join_parts v, ← Matrix.mulVec_mulVec]
  simp only [blockCertificate, upperBlock_mulVec_join, one_smul,
    Matrix.mulVec_add, Matrix.neg_mulVec, Matrix.mulVec_mulVec,
    hAJ, Matrix.smul_mulVec, Matrix.one_mulVec]
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [solvedPart, freePart]

/-- A scalar right certificate also transfers to the augmented system. -/
theorem mul_blockCertificate (A J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R)
    (hJA : J * A = c • (1 : Matrix (Fin e) (Fin e) R)) :
    upperBlock J K 1 * blockCertificate A K c =
      c • (1 : Matrix (Fin (e + k)) (Fin (e + k)) R) := by
  apply Matrix.ext_iff_mulVec.mpr
  intro v
  rw [← join_parts v, ← Matrix.mulVec_mulVec]
  simp only [blockCertificate, upperBlock_mulVec_join, one_smul,
    Matrix.mulVec_add, Matrix.neg_mulVec, Matrix.mulVec_neg,
    Matrix.mulVec_smul, Matrix.mulVec_mulVec, ← Matrix.mul_assoc,
    hJA, Matrix.smul_mul, Matrix.one_mul, Matrix.smul_mulVec, Matrix.one_mulVec]
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [solvedPart, freePart]

/-- The solved block combines coefficient motion and prescribed parameter motion with a plus sign. -/
theorem blockCertificate_mulVec_join_neg (A : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R)
    (h : Fin e → R) (v : Fin k → R) :
    (blockCertificate A K c).mulVec (join h (-v)) =
      join (A.mulVec (h + K.mulVec v)) (-(c • v)) := by
  simp [blockCertificate, upperBlock_mulVec_join, Matrix.mulVec_add,
    Matrix.mulVec_mulVec, Matrix.neg_mulVec, Matrix.mulVec_neg]

/-- Both scalar inverse identities transfer together. -/
theorem blockCertificate_two_sided (A J : Matrix (Fin e) (Fin e) R)
    (K : Matrix (Fin e) (Fin k) R) (c : R)
    (hAJ : A * J = c • (1 : Matrix (Fin e) (Fin e) R))
    (hJA : J * A = c • (1 : Matrix (Fin e) (Fin e) R)) :
    blockCertificate A K c * upperBlock J K 1 =
      c • (1 : Matrix (Fin (e + k)) (Fin (e + k)) R) ∧
    upperBlock J K 1 * blockCertificate A K c =
      c • (1 : Matrix (Fin (e + k)) (Fin (e + k)) R) :=
  ⟨blockCertificate_mul A J K c hAJ, mul_blockCertificate A J K c hJA⟩

/-- The augmented inverse has the same denominator bound as the original solved inverse. -/
theorem bounded_inverse_upperBlock (p s : ℕ) [Fact (Nat.Prime p)]
    (J : Matrix (Fin e) (Fin e) ℤ_[p]) (K : Matrix (Fin e) (Fin k) ℤ_[p])
    (hJ : IsUnit (rationalMatrix p J))
    (hA : ∃ A : Matrix (Fin e) (Fin e) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹) :
    IsUnit (rationalMatrix p (upperBlock J K 1)) ∧
    ∃ C : Matrix (Fin (e + k)) (Fin (e + k)) ℤ_[p],
      rationalMatrix p C =
        (p : ℚ_[p])^s • (rationalMatrix p (upperBlock J K 1))⁻¹ := by
  obtain ⟨A, hAJ, hJA⟩ := (bounded_inverse_iff_certificate p s J).mp ⟨hJ, hA⟩
  exact (bounded_inverse_iff_certificate p s (upperBlock J K 1)).mpr
    ⟨blockCertificate A K ((p : ℤ_[p])^s),
      blockCertificate_two_sided A J K ((p : ℤ_[p])^s) hAJ hJA⟩

end Komorebi.PolynomialBlockInverse
