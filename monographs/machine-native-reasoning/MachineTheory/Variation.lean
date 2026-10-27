import MachineTheory.Bayes
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring
import Mathlib.Data.Fintype.BigOperators

/-!
Finite total variation on the exact real-valued distributions of Blocks 01--03.
The event and conditioning bounds refer to the same two laws and the same event.
No posterior is asserted at zero event mass.
-/
namespace Komorebi.MachineTheory.Variation
open scoped BigOperators
open Instrument
noncomputable section
variable {X Y Z : Type*}

def l1 [Fintype X] (p : X → ℝ) : ℝ := ∑ x, |p x|

def tv [Fintype X] (p q : X → ℝ) : ℝ := l1 (fun x => p x - q x) / 2

theorem l1_nonneg [Fintype X] (p : X → ℝ) : 0 ≤ l1 p :=
  Finset.sum_nonneg (fun x _ => abs_nonneg (p x))

theorem tv_nonneg [Fintype X] (p q : X → ℝ) : 0 ≤ tv p q :=
  div_nonneg (l1_nonneg _) (by norm_num)

theorem tv_self [Fintype X] (p : X → ℝ) : tv p p = 0 := by simp [tv, l1]

theorem tv_symm [Fintype X] (p q : X → ℝ) : tv p q = tv q p := by
  simp only [tv, l1, abs_sub_comm]

theorem tv_triangle [Fintype X] (p q r : X → ℝ) : tv p r ≤ tv p q + tv q r := by
  have h : l1 (fun x => p x-r x) ≤ l1 (fun x => p x-q x) + l1 (fun x => q x-r x) := by
    unfold l1
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_le_sum (fun x _ => abs_sub_le (p x) (q x) (r x))
  unfold tv
  linarith

theorem l1_mass [Fintype X] (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) : l1 p = mass p := by
  simp only [l1, mass, abs_of_nonneg (hp _)]

theorem abs_mass_le_l1 [Fintype X] (p : X → ℝ) : |mass p| ≤ l1 p := by
  exact Finset.abs_sum_le_sum_abs _ _

theorem l1_scale [Fintype X] (c : ℝ) (p : X → ℝ) : l1 (scale c p) = |c| * l1 p := by
  simp [l1, scale, abs_mul, Finset.mul_sum]

theorem tv_scale [Fintype X] (c : ℝ) (p q : X → ℝ) :
    tv (scale c p) (scale c q) = |c| * tv p q := by
  unfold tv
  have h : (fun x => scale c p x - scale c q x) = scale c (fun x => p x-q x) := by
    funext x; simp [scale, mul_sub]
  rw [h, l1_scale]; ring

theorem tv_le_one [Fintype X] (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q) : tv p q ≤ 1 := by
  have h : l1 (fun x => p x-q x) ≤ mass p + mass q := by
    unfold l1 mass
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_le_sum
    intro x _
    exact (abs_sub (p x) (q x)).trans_eq (by rw [abs_of_nonneg (hp.1 x), abs_of_nonneg (hq.1 x)])
  rw [hp.2, hq.2] at h
  unfold tv; linarith

/-- A signed finite sum is contracted by exact deterministic aggregation. -/
theorem l1_push_le [Fintype X] [Fintype Y] [DecidableEq Y]
    (f : X → Y) (p : X → ℝ) : l1 (push f p) ≤ l1 p := by
  calc
    l1 (push f p) ≤ ∑ y, ∑ x, if f x = y then |p x| else 0 := by
      apply Finset.sum_le_sum
      intro y _
      simpa only [push, abs_ite, abs_zero] using
        (Finset.abs_sum_le_sum_abs (fun x => if f x = y then p x else 0) Finset.univ)
    _ = l1 p := by
      rw [Finset.sum_comm]
      simp [l1]

theorem push_sub [Fintype X] [DecidableEq Y] (f : X → Y) (p q : X → ℝ) :
    push f (fun x => p x-q x) = fun y => push f p y-push f q y := by
  funext y
  simp only [push, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro x _
  split_ifs <;> simp

/-- Forgetting coordinates cannot increase total variation. -/
theorem tv_push_le [Fintype X] [Fintype Y] [DecidableEq Y]
    (f : X → Y) (p q : X → ℝ) : tv (push f p) (push f q) ≤ tv p q := by
  unfold tv
  rw [← push_sub]
  exact div_le_div_of_nonneg_right (l1_push_le f _) (by norm_num)

/-- Column-stochastic kernels, oriented like the inherited joint instrument. -/
structure Kernel (X Y : Type*) [Fintype Y] where
  entry : Y → X → ℝ
  nonnegative : ∀ y x, 0 ≤ entry y x
  normalized : ∀ x, ∑ y, entry y x = 1

theorem kernel_mass [Fintype X] [Fintype Y] (K : Kernel X Y) (p : X → ℝ) :
    mass (applyKernel K.entry p) = mass p := by
  unfold mass applyKernel
  rw [Finset.sum_comm]
  simp only [← Finset.sum_mul, K.normalized, one_mul]

theorem kernel_dist [Fintype X] [Fintype Y] (K : Kernel X Y)
    (p : X → ℝ) (hp : IsDist p) : IsDist (applyKernel K.entry p) :=
  ⟨apply_nonnegative _ K.nonnegative _ hp.1, (kernel_mass K p).trans hp.2⟩

theorem kernel_contraction [Fintype X] [Fintype Y] (K : Kernel X Y) (p q : X → ℝ) :
    tv (applyKernel K.entry p) (applyKernel K.entry q) ≤ tv p q := by
  have h : l1 (fun y => applyKernel K.entry p y-applyKernel K.entry q y) ≤ l1 (fun x => p x-q x) := by
    calc
      _ = ∑ y, |∑ x, K.entry y x * (p x-q x)| := by
        simp [l1, applyKernel, Finset.sum_sub_distrib, mul_sub]
      _ ≤ ∑ y, ∑ x, K.entry y x * |p x-q x| := by
        apply Finset.sum_le_sum; intro y _
        simpa only [abs_mul, abs_of_nonneg (K.nonnegative _ _)] using
          (Finset.abs_sum_le_sum_abs (fun x => K.entry y x*(p x-q x)) Finset.univ)
      _ = _ := by
        rw [Finset.sum_comm]
        simp only [← Finset.sum_mul, K.normalized, one_mul, l1]
  unfold tv; exact div_le_div_of_nonneg_right h (by norm_num)

/-- Convex mixing charges the full per-column law discrepancy. -/
theorem kernel_perturbation [Fintype X] [Fintype Y]
    (K L : Y → X → ℝ) (p : X → ℝ) (hp : IsDist p) (ε : ℝ)
    (hε : ∀ x, tv (fun y => K y x) (fun y => L y x) ≤ ε) :
    tv (applyKernel K p) (applyKernel L p) ≤ ε := by
  have h : l1 (fun y => applyKernel K p y-applyKernel L p y) ≤ 2*ε := by
    calc
      _ = ∑ y, |∑ x, (K y x-L y x)*p x| := by
        simp [l1, applyKernel, Finset.sum_sub_distrib, sub_mul]
      _ ≤ ∑ y, ∑ x, |K y x-L y x| *p x := by
        apply Finset.sum_le_sum; intro y _
        simpa only [abs_mul, abs_of_nonneg (hp.1 _)] using
          (Finset.abs_sum_le_sum_abs (fun x => (K y x-L y x)*p x) Finset.univ)
      _ = ∑ x, l1 (fun y => K y x-L y x)*p x := by
        rw [Finset.sum_comm]; simp [l1, Finset.sum_mul]
      _ ≤ ∑ x, (2*ε)*p x := by
        apply Finset.sum_le_sum; intro x _
        have he := hε x
        unfold tv at he
        exact mul_le_mul_of_nonneg_right (by linarith) (hp.1 x)
      _ = 2*ε := by rw [← Finset.mul_sum]; change (2*ε)*mass p=2*ε; rw [hp.2, mul_one]
  unfold tv; linarith

/-- Approximate simulation across different finite state types. -/
theorem push_kernel_step [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq Z]
    {W : Type*} [Fintype W] [DecidableEq W]
    (π : X → Z) (φ : Y → W) (K : Kernel X Y) (L : Kernel Z W)
    (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (ε : ℝ)
    (hε : ∀ x, tv (push φ (fun y => K.entry y x)) (fun w => L.entry w (π x)) ≤ ε) :
    tv (push φ (applyKernel K.entry p)) (applyKernel L.entry q) ≤ tv (push π p) q + ε := by
  let P : W → X → ℝ := fun w x => push φ (fun y => K.entry y x) w
  let Q : W → X → ℝ := fun w x => L.entry w (π x)
  have eqP : push φ (applyKernel K.entry p) = applyKernel P p := by
    funext w
    unfold push applyKernel
    have hi : ∀ y, (if φ y = w then ∑ x, K.entry y x * p x else 0) =
        ∑ x, (if φ y = w then K.entry y x else 0) * p x := by
      intro y
      split_ifs <;> simp_all
    simp_rw [hi]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro x _
    simp [P, push, Finset.sum_mul, ite_mul]
  have eqQ : applyKernel Q p = applyKernel L.entry (push π p) := by
    funext w
    unfold applyKernel push
    simp_rw [Finset.mul_sum, mul_ite, mul_zero]
    rw [Finset.sum_comm]
    simp [Q]
  rw [eqP]
  have h1 := kernel_perturbation P Q p hp ε hε
  have h2 := kernel_contraction L (push π p) q
  have h3 := tv_triangle (applyKernel P p) (applyKernel Q p) (applyKernel L.entry q)
  rw [eqQ] at h3 h1
  linarith

/-- Exact restriction, with zero outside the named event. -/
def restrict [DecidableEq X] (E : Finset X) (p : X → ℝ) : X → ℝ :=
  fun x => if x ∈ E then p x else 0

theorem restrict_nonneg [DecidableEq X] (E : Finset X) (p : X → ℝ)
    (hp : ∀ x, 0 ≤ p x) : ∀ x, 0 ≤ restrict E p x := by
  intro x; unfold restrict; split_ifs <;> simp_all

theorem mass_sub [Fintype X] (p q : X → ℝ) :
    mass (fun x => p x-q x) = mass p-mass q := by simp [mass, Finset.sum_sub_distrib]

theorem mass_split [Fintype X] [DecidableEq X] (E : Finset X) (p : X → ℝ) :
    mass (restrict E p) + mass (restrict Eᶜ p) = mass p := by
  unfold mass
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro x _
  by_cases h : x ∈ E <;> simp [restrict, h]

theorem l1_split [Fintype X] [DecidableEq X] (E : Finset X) (p q : X → ℝ) :
    l1 (fun x => restrict E p x-restrict E q x) +
      l1 (fun x => restrict Eᶜ p x-restrict Eᶜ q x) = l1 (fun x => p x-q x) := by
  unfold l1
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro x _
  by_cases h : x ∈ E <;> simp [restrict, h]

/-- The complement pays for the difference of event masses; this yields the sharp constant. -/
theorem restricted_discrepancy [Fintype X] [DecidableEq X]
    (E : Finset X) (p q : X → ℝ) (hm : mass p = mass q) :
    l1 (fun x => restrict E p x-restrict E q x) +
      |mass (restrict E p)-mass (restrict E q)| ≤ 2 * tv p q := by
  have hc := abs_mass_le_l1 (fun x => restrict Eᶜ p x-restrict Eᶜ q x)
  rw [mass_sub] at hc
  have he : mass (restrict Eᶜ p)-mass (restrict Eᶜ q) =
      -(mass (restrict E p)-mass (restrict E q)) := by
    have h1 := mass_split E p; have h2 := mass_split E q; linarith
  rw [he, abs_neg] at hc
  have hs := l1_split E p q
  unfold tv
  linarith

/-- Event probabilities differ by at most total variation, not twice that value. -/
theorem event_bound [Fintype X] [DecidableEq X]
    (E : Finset X) (p q : X → ℝ) (hm : mass p = mass q) :
    |mass (restrict E p)-mass (restrict E q)| ≤ tv p q := by
  have hi := abs_mass_le_l1 (fun x => restrict E p x-restrict E q x)
  rw [mass_sub] at hi
  have hc := restricted_discrepancy E p q hm
  linarith

theorem normalize_eq_scale [Fintype X] (p : X → ℝ) :
    normalize p = scale (1 / mass p) p := by
  funext x; simp [normalize, scale, div_eq_mul_inv, mul_comm]

theorem tv_scaled_same [Fintype X] (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) (c d : ℝ) :
    tv (scale c p) (scale d p) = |c-d| * mass p / 2 := by
  unfold tv
  have he : (fun x => scale c p x-scale d p x) = scale (c-d) p := by
    funext x; simp [scale, sub_mul]
  rw [he, l1_scale, l1_mass p hp]

/-- Normalization is controlled by unnormalized error and the discrepancy in mass. -/
theorem normalize_bound [Fintype X] (u v : X → ℝ) (hv : ∀ x, 0 ≤ v x)
    (huM : 0 < mass u) (hvM : 0 < mass v) :
    tv (normalize u) (normalize v) ≤
      (l1 (fun x => u x-v x) + |mass u-mass v|) / (2*mass u) := by
  have h := tv_triangle (scale (1/mass u) u) (scale (1/mass u) v) (scale (1/mass v) v)
  rw [tv_scale, tv_scaled_same v hv, abs_of_pos (one_div_pos.mpr huM)] at h
  have hid : (1 / mass u - 1 / mass v) = (mass v-mass u)/(mass u*mass v) := by
    field_simp
  rw [hid, abs_div, abs_mul, abs_of_pos huM, abs_of_pos hvM, abs_sub_comm (mass v)] at h
  have he : 1 / mass u * tv u v +
      |mass u-mass v| / (mass u*mass v) * mass v / 2 =
      (l1 (fun x => u x-v x) + |mass u-mass v|) / (2*mass u) := by
    unfold tv
    field_simp
  rw [he] at h
  simpa only [← normalize_eq_scale] using h

/-- Either denominator gives a valid conditioning bound. -/
theorem condition_left [Fintype X] [DecidableEq X]
    (E : Finset X) (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q)
    (hEp : 0 < mass (restrict E p)) (hEq : 0 < mass (restrict E q)) :
    tv (normalize (restrict E p)) (normalize (restrict E q)) ≤
      tv p q / mass (restrict E p) := by
  have hn := normalize_bound (restrict E p) (restrict E q) (restrict_nonneg E q hq.1) hEp hEq
  have hr := restricted_discrepancy E p q (hp.2.trans hq.2.symm)
  have hd := div_le_div_of_nonneg_right hr (show 0 ≤ 2*mass (restrict E p) by positivity)
  have he : (2*tv p q)/(2*mass (restrict E p)) = tv p q/mass (restrict E p) := by ring
  rw [he] at hd
  exact hn.trans hd

/-- Core 3.8's sharp symmetric conditioning factor. -/
theorem condition_bound [Fintype X] [DecidableEq X]
    (E : Finset X) (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q)
    (hEp : 0 < mass (restrict E p)) (hEq : 0 < mass (restrict E q)) :
    tv (normalize (restrict E p)) (normalize (restrict E q)) ≤
      min 1 (tv p q / max (mass (restrict E p)) (mass (restrict E q))) := by
  apply le_min
  · exact tv_le_one _ _
      (normalize_dist _ (restrict_nonneg E p hp.1) hEp)
      (normalize_dist _ (restrict_nonneg E q hq.1) hEq)
  · by_cases he : mass (restrict E p) ≤ mass (restrict E q)
    · rw [max_eq_right he, tv_symm p q, tv_symm (normalize (restrict E p))]
      exact condition_left E q p hq hp hEq hEp
    · rw [max_eq_left (le_of_not_ge he)]
      exact condition_left E p q hp hq hEp hEq

/-- Positive probability in either law above the whole-law defect excludes an impossible counterpart. -/
theorem event_positive [Fintype X] [DecidableEq X]
    (E : Finset X) (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q)
    (d : ℝ) (hd : tv p q ≤ d) (he : d < mass (restrict E p)) :
    0 < mass (restrict E q) := by
  have h := event_bound E p q (hp.2.trans hq.2.symm)
  have h1 := le_abs_self (mass (restrict E p)-mass (restrict E q))
  linarith

/-- Condition on the same event, then retain only the requested final output. -/
theorem conditional_output_bound [Fintype X] [Fintype Y] [DecidableEq X] [DecidableEq Y]
    (f : X → Y) (E : Finset X) (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q)
    (hEp : 0 < mass (restrict E p)) (hEq : 0 < mass (restrict E q))
    (d : ℝ) (hd : tv p q ≤ d) :
    tv (push f (normalize (restrict E p))) (push f (normalize (restrict E q))) ≤
      min 1 (d / max (mass (restrict E p)) (mass (restrict E q))) := by
  apply (tv_push_le f _ _).trans
  apply (condition_bound E p q hp hq hEp hEq).trans
  exact min_le_min_left 1
    (div_le_div_of_nonneg_right hd (le_trans (le_of_lt hEp) (le_max_left _ _)))

/-- A bounded common loss is Lipschitz in total variation with its full range as constant. -/
theorem expectation_bound [Fintype X] (p q f : X → ℝ)
    (hm : mass p = mass q) (B : ℝ) (_hB : 0 ≤ B) (hf : ∀ x, 0 ≤ f x ∧ f x ≤ B) :
    |(∑ x, f x*p x) - (∑ x, f x*q x)| ≤ B * tv p q := by
  have hz : ∑ x, (p x-q x) = 0 := by
    rw [Finset.sum_sub_distrib]; change mass p-mass q=0; rw [hm, sub_self]
  have he : (∑ x, f x*p x) - (∑ x, f x*q x) =
      ∑ x, (f x-B/2)*(p x-q x) := by
    calc
      _ = ∑ x, f x*(p x-q x) := by simp [mul_sub, Finset.sum_sub_distrib]
      _ = (∑ x, f x*(p x-q x)) - (B/2)*(∑ x, (p x-q x)) := by rw [hz, mul_zero, sub_zero]
      _ = _ := by
        rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
        apply Finset.sum_congr rfl
        intro x _
        ring
  rw [he]
  calc
    _ ≤ ∑ x, |(f x-B/2)*(p x-q x)| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ x, (B/2)*|p x-q x| := by
      apply Finset.sum_le_sum; intro x _
      rw [abs_mul]
      have hb : |f x-B/2| ≤ B/2 := by rw [abs_le]; constructor <;> linarith [hf x]
      exact mul_le_mul_of_nonneg_right hb (abs_nonneg _)
    _ = B*tv p q := by simp only [← Finset.mul_sum, tv, l1]; ring

/-- Composition of exact aggregation maps, including maps that are not surjective. -/
theorem push_comp [Fintype X] [Fintype Y] [DecidableEq Y] [DecidableEq Z]
    (f : X → Y) (g : Y → Z) (p : X → ℝ) : push g (push f p) = push (g ∘ f) p := by
  funext z
  unfold push
  have hi : ∀ y, (if g y=z then ∑ x, if f x=y then p x else 0 else 0) =
      ∑ x, if f x=y then (if g y=z then p x else 0) else 0 := by
    intro y
    by_cases h : g y=z <;> simp [h]
  simp_rw [hi]
  rw [Finset.sum_comm]
  simp

/-- Pushing the second coordinate retains its actual association with the first. -/
theorem push_pair_right [Fintype X] [Fintype Y] [DecidableEq Y] [DecidableEq Z]
    (f : X → Z) (p : Y → X → ℝ) (y : Y) (z : Z) :
    push (fun t : Y × X => (t.1, f t.2)) (fun t => p t.1 t.2) (y,z) = push f (p y) z := by
  simp [push, Fintype.sum_prod_type, Prod.mk.injEq, ite_and]

/-- Joint-law error with a common mixing distribution is the weighted row error. -/
theorem tv_weighted_rows [Fintype X] [Fintype Y]
    (w : Y → ℝ) (hw : ∀ y, 0 ≤ w y) (p q : Y → X → ℝ) :
    tv (fun t : Y × X => w t.1*p t.1 t.2) (fun t => w t.1*q t.1 t.2) =
      ∑ y, w y * tv (p y) (q y) := by
  simp only [tv, l1, Fintype.sum_prod_type, ← mul_sub, abs_mul, abs_of_nonneg (hw _),
    ← Finset.mul_sum, Finset.sum_div, mul_div_assoc]

/-- Mixing over the same policy cannot enlarge a uniform instrument-row error. -/
theorem tv_weighted_rows_le [Fintype X] [Fintype Y]
    (w : Y → ℝ) (hw : IsDist w) (p q : Y → X → ℝ) (ε : ℝ)
    (hε : ∀ y, tv (p y) (q y) ≤ ε) :
    tv (fun t : Y × X => w t.1*p t.1 t.2) (fun t => w t.1*q t.1 t.2) ≤ ε := by
  rw [tv_weighted_rows w hw.1]
  calc
    _ ≤ ∑ y, w y*ε := Finset.sum_le_sum (fun y _ => mul_le_mul_of_nonneg_left (hε y) (hw.1 y))
    _ = ε := by rw [← Finset.sum_mul]; change mass w*ε=ε; rw [hw.2, one_mul]

end
end Komorebi.MachineTheory.Variation
