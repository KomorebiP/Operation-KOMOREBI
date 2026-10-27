import PaperX.RepresentationLimits

/-! Compatible finite matrices reconstruct to actual integral matrices.  Matrix
equations are proved after reconstruction using separatedness, independently
of any invertibility condition. -/
set_option autoImplicit false

namespace PaperX.MatrixWitnessLimits
open PaperX.RepresentationLimits

variable {R : Type*} [CommRing R] (I : Ideal R)
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- An actual compatible family of finite matrices, including precision zero. -/
structure MatrixFamily (R : Type*) [CommRing R] (I : Ideal R)
    (ι : Type*) [Fintype ι] [DecidableEq ι] where
  maps : ∀ k : ℕ, Matrix ι ι (R ⧸ I ^ k)
  compatible : ∀ {j k : ℕ} (h : j ≤ k),
    (maps k).map (Ideal.Quotient.factorPow I h) = maps j

omit [Fintype ι] [DecidableEq ι] in
/-- Adjacent compatibility implies compatibility at every pair of precisions. -/
theorem matrix_compatible_of_succ
    (a : ∀ k : ℕ, Matrix ι ι (R ⧸ I ^ k))
    (ha : ∀ k, (a (k + 1)).map (Ideal.Quotient.factorPow I (Nat.le_succ k)) = a k)
    {j k : ℕ} (h : j ≤ k) :
    (a k).map (Ideal.Quotient.factorPow I h) = a j := by
  ext i l
  apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
    (fun _ _ h => Ideal.pow_le_pow_right h) (fun m => a m i l) ?_ h).symm
  intro m
  exact (congrArg (fun M => M i l) (ha m)).symm

def matrix_family_of_succ
    (a : ∀ k : ℕ, Matrix ι ι (R ⧸ I ^ k))
    (ha : ∀ k, (a (k + 1)).map (Ideal.Quotient.factorPow I (Nat.le_succ k)) = a k) :
    MatrixFamily R I ι where
  maps := a
  compatible := matrix_compatible_of_succ I a ha

noncomputable def reconstructMatrix [IsAdicComplete I R]
    (f : MatrixFamily R I ι) : Matrix ι ι R :=
  fun i j => scalarLift I (fun k => f.maps k i j)
    (fun h => congrArg (fun M => M i j) (f.compatible h))

@[simp] theorem reconstructMatrix_reduces [IsAdicComplete I R]
    (f : MatrixFamily R I ι) (k : ℕ) :
    (reconstructMatrix I f).map (Ideal.Quotient.mk (I ^ k)) = f.maps k := by
  ext i j
  exact scalarLift_reduces I (fun k => f.maps k i j)
    (fun h => congrArg (fun M => M i j) (f.compatible h)) k

/-- The lifted matrix is uniquely determined by its finite reductions. -/
theorem reconstructMatrix_unique [IsAdicComplete I R]
    (f : MatrixFamily R I ι) (P : Matrix ι ι R)
    (hP : ∀ k, P.map (Ideal.Quotient.mk (I ^ k)) = f.maps k) :
    P = reconstructMatrix I f := by
  apply matrix_ext I
  intro k
  rw [reconstructMatrix_reduces, hP]

/-- Products of reconstructed matrices satisfy every compatible finite product
identity.  Invertibility is not supplied as a premise. -/
theorem reconstructMatrix_mul_eq [IsAdicComplete I R]
    (a b c d : MatrixFamily R I ι)
    (h : ∀ k, a.maps k * b.maps k = c.maps k * d.maps k) :
    reconstructMatrix I a * reconstructMatrix I b =
      reconstructMatrix I c * reconstructMatrix I d := by
  apply matrix_ext I
  intro k
  simp only [Matrix.map_mul, reconstructMatrix_reduces]
  exact h k

variable {G : Type*} [Group G]

/-- Actual finite intertwining equations survive reconstruction. -/
theorem reconstructMatrix_intertwines [IsAdicComplete I R]
    (f g : Family R I G ι) (P : MatrixFamily R I ι)
    (h : ∀ k x, f.maps k x * P.maps k = P.maps k * g.maps k x) (x : G) :
    reconstruct I f x * reconstructMatrix I P =
      reconstructMatrix I P * reconstruct I g x := by
  apply matrix_ext I
  intro k
  simp only [Matrix.map_mul, reconstructMatrix_reduces]
  change (liftMatrix I f x).map _ * P.maps k =
    P.maps k * (liftMatrix I g x).map _
  rw [liftMatrix_reduces, liftMatrix_reduces]
  exact h k x

/-- Local comparison uses a specified group homomorphism and a fixed actual
integral comparison representation. -/
theorem reconstructMatrix_local_intertwines {H : Type*} [Group H]
    [IsAdicComplete I R] (f : Family R I G ι) (τ : MatrixRep R H ι)
    (φ : H →* G) (P : MatrixFamily R I ι)
    (h : ∀ k x, f.maps k (φ x) * P.maps k = P.maps k * reduce I τ k x) (x : H) :
    reconstruct I f (φ x) * reconstructMatrix I P = reconstructMatrix I P * τ x := by
  apply matrix_ext I
  intro k
  simp only [Matrix.map_mul, reconstructMatrix_reduces]
  change (liftMatrix I f (φ x)).map _ * P.maps k =
    P.maps k * reduce I τ k x
  rw [liftMatrix_reduces]
  exact h k x

end PaperX.MatrixWitnessLimits
