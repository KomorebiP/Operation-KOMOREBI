import PrimeDegreeFrobeniusNorm
import MatrixSquareZeroObstruction
import Mathlib.Algebra.TrivSqZeroExt.Basic

/-! A genuine matrix-ring instantiation, not an assumed spectrum interface.
For matrices over k[epsilon]/epsilon^2, the actual kernel is the epsilon matrix
space, and diagonal Frobenius acts with eigenvalues lambda_i/lambda_j. -/
namespace Komorebi.StrongArtin.SquareZeroH2.DiagonalModel
variable (k n : Type) [Field k] [Fintype n] [DecidableEq n]
abbrev Dual := TrivSqZeroExt k k

def reduction : Dual k →+* k := (TrivSqZeroExt.fstHom k k k).toRingHom

theorem reduction_squareZero (a b : Dual k)
    (ha : reduction k a = 0) (hb : reduction k b = 0) : a*b = 0 := by
  apply TrivSqZeroExt.ext
  · change a.fst*b.fst=0
    change a.fst=0 at ha
    rw [ha, zero_mul]
  · change a.fst • b.snd + MulOpposite.op b.fst • a.snd = 0
    change a.fst=0 at ha
    change b.fst=0 at hb
    simp [ha,hb]

def datum : Datum PUnit (Matrix n n (Dual k)) (Matrix n n k) where
  q := (reduction k).mapMatrix
  squareZero := matrix_kernel_squareZero (reduction k) (reduction_squareZero k)
  rho := 1
  lift := fun _ => 1
  lift_one := rfl
  lift_residue := by intro g; simp

/-- Extract the epsilon coefficient of every matrix entry. -/
def kernelCoordinates : (datum k n).Kernel ≃+ ((n × n) → k) where
  toFun X ij := (X.val ij.1 ij.2).snd
  invFun x := ⟨fun i j => TrivSqZeroExt.inr (x (i,j)), by ext i j; rfl⟩
  left_inv X := by
    apply Subtype.ext
    funext i j
    apply TrivSqZeroExt.ext
    · exact (congrFun (congrFun X.property i) j).symm
    · rfl
  right_inv x := by funext ij; rfl
  map_add' X Y := by funext ij; rfl

def scalarUnit (u : kˣ) : (Dual k)ˣ :=
  Units.map (TrivSqZeroExt.inlHom k k).toMonoidHom u

/-- An actual upper-ring invertible diagonal Frobenius matrix. -/
def diagonalFrobenius (lambda : n → kˣ) : (Matrix n n (Dual k))ˣ where
  val := Matrix.diagonal fun i => (scalarUnit k (lambda i) : Dual k)
  inv := Matrix.diagonal fun i => (↑(scalarUnit k (lambda i))⁻¹ : Dual k)
  val_inv := by rw [Matrix.diagonal_mul_diagonal]; simp
  inv_val := by rw [Matrix.diagonal_mul_diagonal]; simp

theorem diagonal_conjugation_coordinates (lambda : n → kˣ)
    (X : (datum k n).Kernel) (ij : n × n) :
    kernelCoordinates k n ((datum k n).conjugate (diagonalFrobenius k n lambda) X) ij =
      ((lambda ij.1 : k) * (↑(lambda ij.2)⁻¹ : k)) * kernelCoordinates k n X ij := by
  change (((Matrix.diagonal (fun i => (scalarUnit k (lambda i) : Dual k))) * X.val *
    Matrix.diagonal (fun i => (↑(scalarUnit k (lambda i))⁻¹ : Dual k))) ij.1 ij.2).snd = _
  rw [Matrix.mul_diagonal, Matrix.diagonal_mul]
  change ((TrivSqZeroExt.inl (lambda ij.1 : k) * X.val ij.1 ij.2) *
    TrivSqZeroExt.inl (↑(lambda ij.2)⁻¹ : k)).snd = _
  simp only [TrivSqZeroExt.snd_mul, TrivSqZeroExt.fst_inl,
    TrivSqZeroExt.snd_inl, smul_zero, add_zero, zero_add]
  change ((lambda ij.1 : k) * (X.val ij.1 ij.2).snd) * (↑(lambda ij.2)⁻¹ : k) = _
  change _ = ((lambda ij.1 : k) * (↑(lambda ij.2)⁻¹ : k)) * (X.val ij.1 ij.2).snd
  ring

/-- Construct the spectral model from the actual conjugation calculation. -/
def spectralModel (lambda : n → kˣ) :
    FrobeniusSpectralCoordinates (datum k n) (diagonalFrobenius k n lambda) k (n × n) where
  coordinates := kernelCoordinates k n
  eigenvalue ij := (lambda ij.1 : k) * (↑(lambda ij.2)⁻¹ : k)
  conjugate_coordinates := diagonal_conjugation_coordinates k n lambda

/-- A complete entrywise root criterion for actual invertible matrices over dual numbers. -/
theorem matrix_prescribed_power_iff (lambda : n → kˣ)
    (V : (Matrix n n (Dual k))ˣ) (d : ℕ)
    (hV : (datum k n).q V = (datum k n).q ((diagonalFrobenius k n lambda)^d)) :
    (∃ F' : (Matrix n n (Dual k))ˣ,
      (datum k n).q F' = (datum k n).q (diagonalFrobenius k n lambda) ∧ F'^d=V) ↔
    ∀ ij : n × n,
      normWeight ((lambda ij.1 : k) * (↑(lambda ij.2)⁻¹ : k)) d = 0 →
      kernelCoordinates k n ((datum k n).unitMismatch V
        ((diagonalFrobenius k n lambda)^d) hV) ij = 0 :=
  (spectralModel k n lambda).prescribed_power_iff V d hV

/-- Repeated eigenvalue blocks are exactly the invariant conjugation coordinates. -/
theorem eigenvalue_ratio_one_iff (a b : kˣ) :
    (a : k) * (↑b⁻¹ : k) = 1 ↔ a = b := by
  rw [Units.val_inv_eq_inv_val, mul_inv_eq_one₀ (Units.ne_zero b)]
  exact Units.val_inj

/-- In defining characteristic, the obstruction is the full repeated-eigenvalue
block, not merely its total trace or its scalar part. -/
theorem matrix_prescribed_prime_power_iff (p : ℕ) [Fact (Nat.Prime p)] [CharP k p]
    (lambda : n → kˣ) (V : (Matrix n n (Dual k))ˣ)
    (hV : (datum k n).q V = (datum k n).q ((diagonalFrobenius k n lambda)^p)) :
    (∃ F' : (Matrix n n (Dual k))ˣ,
      (datum k n).q F' = (datum k n).q (diagonalFrobenius k n lambda) ∧ F'^p=V) ↔
    ∀ ij : n × n, lambda ij.1 = lambda ij.2 →
      kernelCoordinates k n ((datum k n).unitMismatch V
        ((diagonalFrobenius k n lambda)^p) hV) ij = 0 := by
  rw [matrix_prescribed_power_iff k n lambda V p hV]
  simp only [normWeight_prime_zero_iff p, eigenvalue_ratio_one_iff]

/-- A prime-to-characteristic degree alone is insufficient: powered eigenvalues
must not acquire new collisions. Under both conditions every prescription lifts. -/
theorem matrix_prescribed_power_lifts_of_no_new_collisions
    (lambda : n → kˣ) (d : ℕ) (hd : (d : k) ≠ 0)
    (hsep : ∀ i j, (lambda i : k)^d = (lambda j : k)^d → lambda i = lambda j)
    (V : (Matrix n n (Dual k))ˣ)
    (hV : (datum k n).q V = (datum k n).q ((diagonalFrobenius k n lambda)^d)) :
    ∃ F' : (Matrix n n (Dual k))ˣ,
      (datum k n).q F' = (datum k n).q (diagonalFrobenius k n lambda) ∧ F'^d=V := by
  apply (spectralModel k n lambda).prescribed_power_lifts_of_nonresonance d _ V hV
  intro ij hzero
  have hz := (normWeight_zero_iff
    ((lambda ij.1 : k) * (↑(lambda ij.2)⁻¹ : k)) d).mp hzero
  rcases hz with ⟨_, hz⟩ | ⟨hne, heq⟩
  · exact hd hz
  · have hp : (lambda ij.1 : k)^d = (lambda ij.2 : k)^d := by
      apply (div_eq_one_iff_eq (pow_ne_zero d (Units.ne_zero (lambda ij.2)))).mp
      simpa only [div_pow, div_eq_mul_inv, Units.val_inv_eq_inv_val, mul_pow, inv_pow]
        using heq
    have he := hsep ij.1 ij.2 hp
    exact hne ((eigenvalue_ratio_one_iff k (lambda ij.1) (lambda ij.2)).mpr he)

/-- In every positive rank, defining-characteristic degree p has genuinely
obstructed prescriptions, even for diagonal residual Frobenius. -/
theorem exists_prescribed_prime_power_obstruction (p : ℕ) [Fact (Nat.Prime p)] [CharP k p]
    (lambda : n → kˣ) (i0 : n) :
    ∃ V : (Matrix n n (Dual k))ˣ,
      (datum k n).q V = (datum k n).q ((diagonalFrobenius k n lambda)^p) ∧
      ¬ ∃ F' : (Matrix n n (Dual k))ˣ,
        (datum k n).q F' = (datum k n).q (diagonalFrobenius k n lambda) ∧ F'^p=V := by
  let e : (datum k n).Kernel := (kernelCoordinates k n).symm
    (fun ij => if ij = (i0,i0) then 1 else 0)
  let F0 := diagonalFrobenius k n lambda
  let V := (datum k n).kernelUnit e * F0^p
  have hV : (datum k n).q V = (datum k n).q (F0^p) := by
    change (datum k n).q (((datum k n).kernelUnit e : Matrix n n (Dual k)) *
      (F0^p : Matrix n n (Dual k))) = _
    rw [map_mul, (datum k n).kernelUnit_residue, one_mul]
  refine ⟨V,hV,?_⟩
  intro h
  have he := (matrix_prescribed_prime_power_iff k n p lambda V hV).mp h (i0,i0) rfl
  have hm : (datum k n).unitMismatch V (F0^p) hV = e :=
    (datum k n).unitMismatch_kernel_perturbed (F0^p) e hV
  change kernelCoordinates k n ((datum k n).unitMismatch V (F0^p) hV) (i0,i0) = 0 at he
  rw [hm] at he
  have hone : kernelCoordinates k n e (i0,i0) = 1 := by
    simp [e]
  rw [hone] at he
  exact one_ne_zero he

end Komorebi.StrongArtin.SquareZeroH2.DiagonalModel
