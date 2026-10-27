import Komorebi.DyadicBall
import Komorebi.RationalMatrixCertificates

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix
open Komorebi.ExactPosterior

variable {ι κ ν : Type*}

abbrev BallMatrix (ι κ : Type*) := ι → κ → Ball
def MatrixEncloses (A : BallMatrix ι κ) (X : Matrix ι κ ℚ) : Prop :=
  ∀ i j, Encloses (A i j) (X i j)
def VectorEncloses (b : ι → Ball) (x : ι → ℚ) : Prop :=
  ∀ i, Encloses (b i) (x i)

def matrixInput (p : ℕ) (X : Matrix ι κ ℚ) : BallMatrix ι κ :=
  fun i j => rExact p (X i j)
def vectorInput (p : ℕ) (x : ι → ℚ) : ι → Ball := fun i => rExact p (x i)
def matrixTranspose (A : BallMatrix ι κ) : BallMatrix κ ι := fun j i => A i j

def matrixAdd (p : ℕ) (A B : BallMatrix ι κ) : BallMatrix ι κ :=
  fun i j => rAdd p (A i j) (B i j)
def matrixSub (p : ℕ) (A B : BallMatrix ι κ) : BallMatrix ι κ :=
  fun i j => rSub p (A i j) (B i j)
def matrixMul [Fintype κ] (p : ℕ) (A : BallMatrix ι κ) (B : BallMatrix κ ν) :
    BallMatrix ι ν := fun i k => rSum p Finset.univ (fun j => rMul p (A i j) (B j k))
def matrixVector [Fintype κ] (p : ℕ) (A : BallMatrix ι κ) (x : κ → Ball) : ι → Ball :=
  fun i => rSum p Finset.univ (fun j => rMul p (A i j) (x j))
def vectorSub (p : ℕ) (a b : ι → Ball) : ι → Ball := fun i => rSub p (a i) (b i)

theorem matrixInput_encloses (p : ℕ) (X : Matrix ι κ ℚ) :
    MatrixEncloses (matrixInput p X) X := fun i j => rExact_encloses p (X i j)
theorem vectorInput_encloses (p : ℕ) (x : ι → ℚ) :
    VectorEncloses (vectorInput p x) x := fun i => rExact_encloses p (x i)
theorem matrixTranspose_encloses {A : BallMatrix ι κ} {X : Matrix ι κ ℚ}
    (h : MatrixEncloses A X) : MatrixEncloses (matrixTranspose A) X.transpose :=
  fun j i => h i j

theorem matrixAdd_encloses (p : ℕ) {A B : BallMatrix ι κ} {X Y : Matrix ι κ ℚ}
    (hA : MatrixEncloses A X) (hB : MatrixEncloses B Y) :
    MatrixEncloses (matrixAdd p A B) (X+Y) :=
  fun i j => rAdd_encloses p (hA i j) (hB i j)
theorem matrixSub_encloses (p : ℕ) {A B : BallMatrix ι κ} {X Y : Matrix ι κ ℚ}
    (hA : MatrixEncloses A X) (hB : MatrixEncloses B Y) :
    MatrixEncloses (matrixSub p A B) (X-Y) :=
  fun i j => rSub_encloses p (hA i j) (hB i j)
theorem matrixMul_encloses [Fintype κ] (p : ℕ)
    {A : BallMatrix ι κ} {B : BallMatrix κ ν} {X : Matrix ι κ ℚ} {Y : Matrix κ ν ℚ}
    (hA : MatrixEncloses A X) (hB : MatrixEncloses B Y) :
    MatrixEncloses (matrixMul p A B) (X*Y) := by
  intro i k
  exact rSum_encloses p Finset.univ _ _ (fun j _ => rMul_encloses p (hA i j) (hB j k))
theorem matrixVector_encloses [Fintype κ] (p : ℕ)
    {A : BallMatrix ι κ} {b : κ → Ball} {X : Matrix ι κ ℚ} {y : κ → ℚ}
    (hA : MatrixEncloses A X) (hb : VectorEncloses b y) :
    VectorEncloses (matrixVector p A b) (X *ᵥ y) := by
  intro i
  exact rSum_encloses p Finset.univ _ _ (fun j _ => rMul_encloses p (hA i j) (hb j))
theorem vectorSub_encloses (p : ℕ) {a b : ι → Ball} {x y : ι → ℚ}
    (ha : VectorEncloses a x) (hb : VectorEncloses b y) :
    VectorEncloses (vectorSub p a b) (x-y) := fun i => rSub_encloses p (ha i) (hb i)

def matrixEnergyUpper [Fintype ι] [Fintype κ] (A : BallMatrix ι κ) : ℚ :=
  ∑ i, ∑ j, energyUpper (A i j)
def vectorEnergyUpper [Fintype ι] (b : ι → Ball) : ℚ := ∑ i, energyUpper (b i)

theorem matrixEnergyUpper_sound [Fintype ι] [Fintype κ]
    {A : BallMatrix ι κ} {X : Matrix ι κ ℚ} (h : MatrixEncloses A X) :
    rationalEnergy X ≤ matrixEnergyUpper A :=
  Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun j _ => energyUpper_sound (h i j)
theorem vectorEnergyUpper_sound [Fintype ι]
    {b : ι → Ball} {x : ι → ℚ} (h : VectorEncloses b x) :
    rationalVectorEnergy x ≤ vectorEnergyUpper b :=
  Finset.sum_le_sum fun i _ => energyUpper_sound (h i)

/-- The enclosure is also an inequality in the reals, with exact rational embedding. -/
theorem matrixEncloses_real {A : BallMatrix ι κ} {X : Matrix ι κ ℚ}
    (h : MatrixEncloses A X) (i : ι) (j : κ) :
    |(X i j : ℝ) - ((A i j).center : ℝ)| ≤ ((A i j).radius : ℝ) := by
  exact_mod_cast h i j

end Komorebi.RoundedPosterior
