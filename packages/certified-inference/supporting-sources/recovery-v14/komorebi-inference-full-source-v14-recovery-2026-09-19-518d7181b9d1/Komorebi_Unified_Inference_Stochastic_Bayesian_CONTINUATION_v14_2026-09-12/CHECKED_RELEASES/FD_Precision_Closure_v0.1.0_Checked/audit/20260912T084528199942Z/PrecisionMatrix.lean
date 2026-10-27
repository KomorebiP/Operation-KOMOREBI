import Komorebi.PrecisionEnergy
import Komorebi.RoundedMatrix

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ ν : Type*}

abbrev BudgetMatrix (ι κ : Type*) := ι → κ → Budget

def budgetInput (X : Matrix ι κ ℚ) : BudgetMatrix ι κ := fun i j => Budget.input (X i j)
def budgetVectorInput (x : ι → ℚ) : ι → Budget := fun i => Budget.input (x i)
def budgetTranspose (A : BudgetMatrix ι κ) : BudgetMatrix κ ι := fun j i => A i j
def budgetAdd (A B : BudgetMatrix ι κ) : BudgetMatrix ι κ := fun i j => Budget.plus (A i j) (B i j)
def budgetMul [Fintype κ] (A : BudgetMatrix ι κ) (B : BudgetMatrix κ ν) : BudgetMatrix ι ν :=
  fun i k => Budget.total Finset.univ (fun j => Budget.times (A i j) (B j k))
def budgetVector [Fintype κ] (A : BudgetMatrix ι κ) (b : κ → Budget) : ι → Budget :=
  fun i => Budget.total Finset.univ (fun j => Budget.times (A i j) (b j))
def budgetVectorSub (a b : ι → Budget) : ι → Budget := fun i => Budget.plus (a i) (b i)

def MatrixBudgetBounds (p : ℕ) (A : BallMatrix ι κ) (X : Matrix ι κ ℚ)
    (Q : BudgetMatrix ι κ) : Prop := ∀ i j, Budget.Bounds p (A i j) (X i j) (Q i j)
def VectorBudgetBounds (p : ℕ) (b : ι → Ball) (x : ι → ℚ) (q : ι → Budget) : Prop :=
  ∀ i, Budget.Bounds p (b i) (x i) (q i)

theorem budgetInput_bounds (p : ℕ) (X : Matrix ι κ ℚ) :
    MatrixBudgetBounds p (matrixInput p X) X (budgetInput X) :=
  fun i j => Budget.input_bounds p (X i j)
theorem budgetVectorInput_bounds (p : ℕ) (x : ι → ℚ) :
    VectorBudgetBounds p (vectorInput p x) x (budgetVectorInput x) :=
  fun i => Budget.input_bounds p (x i)
theorem budgetTranspose_bounds {p : ℕ} {A : BallMatrix ι κ} {X : Matrix ι κ ℚ}
    {Q : BudgetMatrix ι κ} (h : MatrixBudgetBounds p A X Q) :
    MatrixBudgetBounds p (matrixTranspose A) X.transpose (budgetTranspose Q) := fun j i => h i j

theorem budgetAdd_bounds (p : ℕ) {A B : BallMatrix ι κ} {X Y : Matrix ι κ ℚ}
    {Q D : BudgetMatrix ι κ} (hA : MatrixBudgetBounds p A X Q) (hB : MatrixBudgetBounds p B Y D) :
    MatrixBudgetBounds p (matrixAdd p A B) (X+Y) (budgetAdd Q D) :=
  fun i j => Budget.plus_bounds p (hA i j) (hB i j)
theorem budgetSub_bounds (p : ℕ) {A B : BallMatrix ι κ} {X Y : Matrix ι κ ℚ}
    {Q D : BudgetMatrix ι κ} (hA : MatrixBudgetBounds p A X Q) (hB : MatrixBudgetBounds p B Y D) :
    MatrixBudgetBounds p (matrixSub p A B) (X-Y) (budgetAdd Q D) :=
  fun i j => Budget.minus_bounds p (hA i j) (hB i j)
theorem budgetMul_bounds [Fintype κ] (p : ℕ)
    {A : BallMatrix ι κ} {B : BallMatrix κ ν} {X : Matrix ι κ ℚ} {Y : Matrix κ ν ℚ}
    {Q : BudgetMatrix ι κ} {D : BudgetMatrix κ ν}
    (hA : MatrixBudgetBounds p A X Q) (hB : MatrixBudgetBounds p B Y D) :
    MatrixBudgetBounds p (matrixMul p A B) (X*Y) (budgetMul Q D) := by
  intro i k
  exact Budget.total_bounds p Finset.univ _ _ _
    (fun j _ => Budget.times_bounds p (hA i j) (hB j k))
theorem budgetVector_bounds [Fintype κ] (p : ℕ)
    {A : BallMatrix ι κ} {b : κ → Ball} {X : Matrix ι κ ℚ} {y : κ → ℚ}
    {Q : BudgetMatrix ι κ} {d : κ → Budget}
    (hA : MatrixBudgetBounds p A X Q) (hb : VectorBudgetBounds p b y d) :
    VectorBudgetBounds p (matrixVector p A b) (X *ᵥ y) (budgetVector Q d) := by
  intro i
  exact Budget.total_bounds p Finset.univ _ _ _
    (fun j _ => Budget.times_bounds p (hA i j) (hb j))
theorem budgetVectorSub_bounds (p : ℕ) {a b : ι → Ball} {x y : ι → ℚ}
    {q d : ι → Budget} (ha : VectorBudgetBounds p a x q) (hb : VectorBudgetBounds p b y d) :
    VectorBudgetBounds p (vectorSub p a b) (x-y) (budgetVectorSub q d) :=
  fun i => Budget.minus_bounds p (ha i) (hb i)

def matrixEnergyCoeff [Fintype ι] [Fintype κ] (Q : BudgetMatrix ι κ) : ℚ :=
  ∑ i, ∑ j, (Q i j).energyCoeff
def matrixEnergyMag [Fintype ι] [Fintype κ] (Q : BudgetMatrix ι κ) : ℚ :=
  ∑ i, ∑ j, (Q i j).mag^2
def vectorEnergyCoeff [Fintype ι] (q : ι → Budget) : ℚ := ∑ i, (q i).energyCoeff
def vectorEnergyMag [Fintype ι] (q : ι → Budget) : ℚ := ∑ i, (q i).mag^2

theorem matrixEnergyCoeff_nonneg [Fintype ι] [Fintype κ] (Q : BudgetMatrix ι κ) :
    0 ≤ matrixEnergyCoeff Q :=
  Finset.sum_nonneg fun i _ => Finset.sum_nonneg fun j _ => Budget.energyCoeff_nonneg (Q i j)
theorem vectorEnergyCoeff_nonneg [Fintype ι] (q : ι → Budget) : 0 ≤ vectorEnergyCoeff q :=
  Finset.sum_nonneg fun i _ => Budget.energyCoeff_nonneg (q i)
theorem matrixEnergyMag_nonneg [Fintype ι] [Fintype κ] (Q : BudgetMatrix ι κ) :
    0 ≤ matrixEnergyMag Q := Finset.sum_nonneg fun i _ => Finset.sum_nonneg fun j _ => sq_nonneg _
theorem vectorEnergyMag_nonneg [Fintype ι] (q : ι → Budget) : 0 ≤ vectorEnergyMag q :=
  Finset.sum_nonneg fun i _ => sq_nonneg _

theorem matrixEnergy_inflation [Fintype ι] [Fintype κ]
    {p : ℕ} {A : BallMatrix ι κ} {X : Matrix ι κ ℚ} {Q : BudgetMatrix ι κ}
    (h : MatrixBudgetBounds p A X Q) :
    matrixEnergyUpper A ≤ rationalEnergy X+matrixEnergyCoeff Q*mesh p := by
  have hh := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) =>
    Finset.sum_le_sum fun j (_ : j ∈ Finset.univ) => Budget.energy_upper_le (h i j)
  simpa only [matrixEnergyUpper,rationalEnergy,matrixEnergyCoeff,Finset.sum_add_distrib,
    Finset.sum_mul] using hh
theorem vectorEnergy_inflation [Fintype ι]
    {p : ℕ} {b : ι → Ball} {x : ι → ℚ} {q : ι → Budget} (h : VectorBudgetBounds p b x q) :
    vectorEnergyUpper b ≤ rationalVectorEnergy x+vectorEnergyCoeff q*mesh p := by
  have hh := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) => Budget.energy_upper_le (h i)
  simpa only [vectorEnergyUpper,rationalVectorEnergy,vectorEnergyCoeff,Finset.sum_add_distrib,
    Finset.sum_mul] using hh

theorem matrixExactEnergy_le_mag [Fintype ι] [Fintype κ]
    {p : ℕ} {A : BallMatrix ι κ} {X : Matrix ι κ ℚ} {Q : BudgetMatrix ι κ}
    (h : MatrixBudgetBounds p A X Q) : rationalEnergy X ≤ matrixEnergyMag Q :=
  Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun j _ => Budget.exact_energy_le (h i j)
theorem vectorExactEnergy_le_mag [Fintype ι]
    {p : ℕ} {b : ι → Ball} {x : ι → ℚ} {q : ι → Budget} (h : VectorBudgetBounds p b x q) :
    rationalVectorEnergy x ≤ vectorEnergyMag q :=
  Finset.sum_le_sum fun i _ => Budget.exact_energy_le (h i)

end Komorebi.RoundedPosterior
