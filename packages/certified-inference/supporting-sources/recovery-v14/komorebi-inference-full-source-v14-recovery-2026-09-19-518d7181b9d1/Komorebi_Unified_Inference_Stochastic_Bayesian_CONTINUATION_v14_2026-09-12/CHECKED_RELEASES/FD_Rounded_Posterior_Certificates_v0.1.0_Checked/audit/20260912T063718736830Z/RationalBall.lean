import Mathlib.Data.Rat.Floor
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

set_option autoImplicit false
namespace Komorebi.RoundedPosterior

/-- A rational center and an absolute error radius. Validity is carried by `Encloses`. -/
structure Ball where
  center : ℚ
  radius : ℚ
  deriving DecidableEq, Repr

def Encloses (b : Ball) (x : ℚ) : Prop := |x - b.center| ≤ b.radius

def exact (x : ℚ) : Ball := ⟨x, 0⟩
def add (a b : Ball) : Ball := ⟨a.center+b.center, a.radius+b.radius⟩
def neg (a : Ball) : Ball := ⟨-a.center, a.radius⟩
def sub (a b : Ball) : Ball := add a (neg b)
def mul (a b : Ball) : Ball :=
  ⟨a.center*b.center,
    |a.center|*b.radius + |b.center|*a.radius + a.radius*b.radius⟩

theorem exact_encloses (x : ℚ) : Encloses (exact x) x := by
  simp [Encloses, exact]

theorem radius_nonneg {b : Ball} {x : ℚ} (h : Encloses b x) : 0 ≤ b.radius :=
  (abs_nonneg _).trans h

theorem add_encloses {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (add a b) (x+y) := by
  change |x+y-(a.center+b.center)| ≤ a.radius+b.radius
  calc
    _ = |(x-a.center)+(y-b.center)| := by congr 1; ring
    _ ≤ |x-a.center|+|y-b.center| := abs_add_le _ _
    _ ≤ _ := add_le_add ha hb

theorem neg_encloses {a : Ball} {x : ℚ} (h : Encloses a x) :
    Encloses (neg a) (-x) := by
  simpa [Encloses, neg, ← neg_sub, abs_neg] using h

theorem sub_encloses {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (sub a b) (x-y) := by
  simpa [sub, sub_eq_add_neg] using add_encloses ha (neg_encloses hb)

theorem mul_encloses {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (mul a b) (x*y) := by
  change |x*y-a.center*b.center| ≤ _
  calc
    _ = |a.center*(y-b.center)+b.center*(x-a.center)+(x-a.center)*(y-b.center)| := by
      congr 1; ring
    _ ≤ |a.center*(y-b.center)|+|b.center*(x-a.center)|+
        |(x-a.center)*(y-b.center)| := abs_add_three _ _ _
    _ = |a.center|*|y-b.center|+|b.center|*|x-a.center|+
        |x-a.center|*|y-b.center| := by simp only [abs_mul]
    _ ≤ _ := add_le_add
      (add_le_add (mul_le_mul_of_nonneg_left hb (abs_nonneg _))
        (mul_le_mul_of_nonneg_left ha (abs_nonneg _)))
      (mul_le_mul ha hb (abs_nonneg _) (radius_nonneg ha))

def sum {ι : Type*} (s : Finset ι) (b : ι → Ball) : Ball :=
  ⟨∑ i ∈ s, (b i).center, ∑ i ∈ s, (b i).radius⟩

theorem sum_encloses {ι : Type*} (s : Finset ι) (b : ι → Ball) (x : ι → ℚ)
    (h : ∀ i ∈ s, Encloses (b i) (x i)) : Encloses (sum s b) (∑ i ∈ s, x i) := by
  change |(∑ i ∈ s, x i)-(∑ i ∈ s, (b i).center)| ≤ ∑ i ∈ s, (b i).radius
  rw [← Finset.sum_sub_distrib]
  exact (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum h)

/-- A squared-energy upper bound from an absolute error enclosure. -/
def energyUpper (b : Ball) : ℚ := (|b.center|+b.radius)^2

theorem abs_le_center_radius {b : Ball} {x : ℚ} (h : Encloses b x) :
    |x| ≤ |b.center|+b.radius := by
  calc
    |x| = |b.center+(x-b.center)| := by congr 1; ring
    _ ≤ |b.center|+|x-b.center| := abs_add_le _ _
    _ ≤ _ := add_le_add_left h _

theorem energyUpper_sound {b : Ball} {x : ℚ} (h : Encloses b x) :
    x^2 ≤ energyUpper b := by
  have he := abs_le_center_radius h
  have hp := mul_self_le_mul_self (abs_nonneg x) he
  simpa [energyUpper, pow_two, ← sq_abs] using hp

end Komorebi.RoundedPosterior
