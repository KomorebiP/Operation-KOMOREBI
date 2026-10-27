import Komorebi.DyadicPrecision
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring

set_option autoImplicit false
set_option maxHeartbeats 800000
namespace Komorebi.RoundedPosterior

/-- An exact magnitude bound and a precision-independent coefficient of radius growth. -/
structure Budget where
  mag : ℚ
  coeff : ℚ
  mag_nonneg : 0 ≤ mag
  coeff_nonneg : 0 ≤ coeff

namespace Budget

def input (x : ℚ) : Budget := ⟨|x|, 2, abs_nonneg x, by norm_num⟩

def plus (a b : Budget) : Budget :=
  ⟨a.mag+b.mag, a.coeff+b.coeff+2,
    add_nonneg a.mag_nonneg b.mag_nonneg,
    add_nonneg (add_nonneg a.coeff_nonneg b.coeff_nonneg) (by norm_num)⟩

def times (a b : Budget) : Budget :=
  ⟨a.mag*b.mag, a.mag*b.coeff+b.mag*a.coeff+3*a.coeff*b.coeff+2,
    mul_nonneg a.mag_nonneg b.mag_nonneg, by
      have := a.mag_nonneg; have := b.mag_nonneg
      have := a.coeff_nonneg; have := b.coeff_nonneg; positivity⟩

def total {ι : Type*} (s : Finset ι) (b : ι → Budget) : Budget :=
  ⟨∑ i ∈ s, (b i).mag, (∑ i ∈ s, (b i).coeff)+2,
    Finset.sum_nonneg (fun i _ => (b i).mag_nonneg),
    add_nonneg (Finset.sum_nonneg (fun i _ => (b i).coeff_nonneg)) (by norm_num)⟩

/-- The budget describes the exact value and the actual retained rounded evaluator. -/
def Bounds (p : ℕ) (b : Ball) (x : ℚ) (q : Budget) : Prop :=
  |x| ≤ q.mag ∧ Encloses b x ∧ b.radius ≤ q.coeff*mesh p

theorem center_le {p : ℕ} {b : Ball} {x : ℚ} {q : Budget} (h : Bounds p b x q) :
    |b.center| ≤ q.mag+q.coeff := by
  have hab : |b.center-x| ≤ b.radius := by
    rw [abs_sub_comm]
    exact h.2.1
  have hc : |b.center| ≤ |x|+b.radius := by
    calc
      |b.center| = |x+(b.center-x)| := by congr 1; ring
      _ ≤ |x|+|b.center-x| := abs_add_le _ _
      _ ≤ |x|+b.radius := add_le_add_left hab |x|
  have hr := mul_le_mul_of_nonneg_left (mesh_le_one p) q.coeff_nonneg
  linarith only [hc,hr,h.1,h.2.2]

theorem input_bounds (p : ℕ) (x : ℚ) : Bounds p (rExact p x) x (input x) := by
  refine ⟨le_rfl, rExact_encloses p x, ?_⟩
  simpa [rExact, exact, input] using round_radius_le p (exact x)

theorem plus_bounds (p : ℕ) {a b : Ball} {x y : ℚ} {qa qb : Budget}
    (ha : Bounds p a x qa) (hb : Bounds p b y qb) :
    Bounds p (rAdd p a b) (x+y) (plus qa qb) := by
  refine ⟨(abs_add_le x y).trans (add_le_add ha.1 hb.1), rAdd_encloses p ha.2.1 hb.2.1, ?_⟩
  have hr := round_radius_le p (add a b)
  change (round p (add a b)).radius ≤ (qa.coeff+qb.coeff+2)*mesh p
  change (round p (add a b)).radius ≤ a.radius+b.radius+2*mesh p at hr
  nlinarith only [hr, ha.2.2,hb.2.2]

theorem minus_bounds (p : ℕ) {a b : Ball} {x y : ℚ} {qa qb : Budget}
    (ha : Bounds p a x qa) (hb : Bounds p b y qb) :
    Bounds p (rSub p a b) (x-y) (plus qa qb) := by
  refine ⟨(abs_sub x y).trans (add_le_add ha.1 hb.1), rSub_encloses p ha.2.1 hb.2.1, ?_⟩
  have hr := round_radius_le p (sub a b)
  change (round p (sub a b)).radius ≤ (qa.coeff+qb.coeff+2)*mesh p
  change (round p (sub a b)).radius ≤ a.radius+b.radius+2*mesh p at hr
  nlinarith only [hr, ha.2.2,hb.2.2]

theorem times_bounds (p : ℕ) {a b : Ball} {x y : ℚ} {qa qb : Budget}
    (ha : Bounds p a x qa) (hb : Bounds p b y qb) :
    Bounds p (rMul p a b) (x*y) (times qa qb) := by
  refine ⟨?_, rMul_encloses p ha.2.1 hb.2.1, ?_⟩
  · rw [abs_mul]
    exact mul_le_mul ha.1 hb.1 (abs_nonneg y) qa.mag_nonneg
  · have h1 := mul_le_mul (center_le ha) hb.2.2 (radius_nonneg hb.2.1)
        (add_nonneg qa.mag_nonneg qa.coeff_nonneg)
    have h2 := mul_le_mul (center_le hb) ha.2.2 (radius_nonneg ha.2.1)
        (add_nonneg qb.mag_nonneg qb.coeff_nonneg)
    have har : a.radius ≤ qa.coeff := ha.2.2.trans (by
      simpa using mul_le_mul_of_nonneg_left (mesh_le_one p) qa.coeff_nonneg)
    have h3 := mul_le_mul har hb.2.2 (radius_nonneg hb.2.1) qa.coeff_nonneg
    have hr := round_radius_le p (mul a b)
    change (round p (mul a b)).radius ≤
      (qa.mag*qb.coeff+qb.mag*qa.coeff+3*qa.coeff*qb.coeff+2)*mesh p
    change (round p (mul a b)).radius ≤
      |a.center| *b.radius+|b.center| *a.radius+a.radius*b.radius+2*mesh p at hr
    calc
      _ ≤ |a.center| * b.radius + |b.center| * a.radius + a.radius*b.radius + 2*mesh p := hr
      _ ≤ (qa.mag+qa.coeff)*(qb.coeff*mesh p) +
          (qb.mag+qb.coeff)*(qa.coeff*mesh p) + qa.coeff*(qb.coeff*mesh p) + 2*mesh p :=
        add_le_add_right (add_le_add (add_le_add h1 h2) h3) _
      _ = _ := by ring

theorem total_bounds {ι : Type*} (p : ℕ) (s : Finset ι) (b : ι → Ball)
    (x : ι → ℚ) (q : ι → Budget) (h : ∀ i ∈ s, Bounds p (b i) (x i) (q i)) :
    Bounds p (rSum p s b) (∑ i ∈ s, x i) (total s q) := by
  refine ⟨(Finset.abs_sum_le_sum_abs _ _).trans
    (Finset.sum_le_sum fun i hi => (h i hi).1),
    rSum_encloses p s b x (fun i hi => (h i hi).2.1), ?_⟩
  have hh := Finset.sum_le_sum (fun i hi => (h i hi).2.2)
  rw [← Finset.sum_mul] at hh
  have hr := round_radius_le p (sum s b)
  change (round p (sum s b)).radius ≤ ((∑ i ∈ s, (q i).coeff)+2)*mesh p
  change (round p (sum s b)).radius ≤ (∑ i ∈ s, (b i).radius)+2*mesh p at hr
  nlinarith only [hr,hh]

end Budget
end Komorebi.RoundedPosterior
