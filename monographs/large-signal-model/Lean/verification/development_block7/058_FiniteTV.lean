import KomorebiLSM.NormalizedDefect

/-! Finite total variation uses the actual half-sum of absolute probability differences. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteTV
open scoped BigOperators
open FiniteBayes FiniteInstruments
variable {I : Type*} [Fintype I]

noncomputable def l1 (x : I → ℝ) : ℝ := ∑ i, |x i|
noncomputable def distance (p q : I → ℝ) : ℝ := l1 (p-q)/2

theorem l1_nonneg (x : I → ℝ) : 0 ≤ l1 x := Finset.sum_nonneg (fun i _ => abs_nonneg (x i))
@[simp] theorem l1_zero : l1 (0 : I → ℝ)=0 := by simp [l1]
@[simp] theorem l1_neg (x : I → ℝ) : l1 (-x)=l1 x := by simp [l1]

theorem l1_add_le (x y : I → ℝ) : l1 (x+y) ≤ l1 x+l1 y := by
  simp only [l1,Pi.add_apply,← Finset.sum_add_distrib]
  exact Finset.sum_le_sum (fun i _ => abs_add_le (x i) (y i))

theorem l1_sub_le (x y : I → ℝ) : l1 (x-y) ≤ l1 x+l1 y := by
  simpa only [sub_eq_add_neg,l1_neg] using l1_add_le x (-y)

theorem l1_smul (a : ℝ) (x : I → ℝ) : l1 (a • x)=|a| * l1 x := by
  simp only [l1,Pi.smul_apply,smul_eq_mul,abs_mul,Finset.mul_sum]

theorem abs_mass_le_l1 (x : I → ℝ) : |mass x| ≤ l1 x :=
  Finset.abs_sum_le_sum_abs x Finset.univ

theorem l1_of_nonneg (x : I → ℝ) (hx : ∀ i, 0 ≤ x i) : l1 x=mass x := by
  simp only [l1,mass_apply,abs_of_nonneg (hx _)]

theorem l1_prior (p : I → ℝ) (hp : IsPrior p) : l1 p=1 :=
  (l1_of_nonneg p hp.1).trans (mass_prior p hp)

theorem distance_nonneg (p q : I → ℝ) : 0 ≤ distance p q :=
  div_nonneg (l1_nonneg _) (by norm_num)

@[simp] theorem distance_self (p : I → ℝ) : distance p p=0 := by simp [distance]

theorem distance_comm (p q : I → ℝ) : distance p q=distance q p := by
  simp only [distance,l1,Pi.sub_apply,abs_sub_comm]

theorem distance_triangle (p q r : I → ℝ) : distance p r ≤ distance p q+distance q r := by
  have he : p-r=(p-q)+(q-r) := by abel
  have h := l1_add_le (p-q) (q-r)
  rw [← he] at h
  unfold distance
  linarith

theorem distance_le_one (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q) :
    distance p q ≤ 1 := by
  have h := l1_sub_le p q
  rw [l1_prior p hp,l1_prior q hq] at h
  unfold distance
  linarith

section Events
variable [DecidableEq I]

noncomputable def restrict (p : I → ℝ) (H : Finset I) (i : I) : ℝ := if i∈H then p i else 0
noncomputable def eventMass (p : I → ℝ) (H : Finset I) : ℝ := ∑ i ∈ H, p i
noncomputable def conditional (p : I → ℝ) (H : Finset I) : I → ℝ := normalize mass (restrict p H)

theorem restrict_nonneg (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) (H : Finset I) :
    ∀ i, 0 ≤ restrict p H i := by
  intro i
  unfold restrict
  split_ifs
  · exact hp i
  · exact le_rfl

theorem restrict_mass (p : I → ℝ) (H : Finset I) : mass (restrict p H)=eventMass p H := by
  simp [mass_apply,restrict,eventMass]

theorem eventMass_nonneg (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) (H : Finset I) :
    0 ≤ eventMass p H := Finset.sum_nonneg (fun i _ => hp i)

theorem conditional_prior (p : I → ℝ) (hp : IsPrior p) (H : Finset I)
    (hH : 0<eventMass p H) : IsPrior (conditional p H) :=
  normalized_prior _ (restrict_nonneg p hp.1 H) (by rwa [restrict_mass])

theorem restrict_sub (p q : I → ℝ) (H : Finset I) :
    restrict p H-restrict q H=restrict (p-q) H := by
  funext i
  simp only [restrict,Pi.sub_apply]
  split_ifs <;> simp

theorem l1_restrict (x : I → ℝ) (H : Finset I) : l1 (restrict x H)=∑ i ∈ H, |x i| := by
  simp [l1,restrict,apply_ite abs]

theorem restriction_complement (x : I → ℝ) (H : Finset I) :
    l1 (restrict x H)+l1 (restrict x Hᶜ)=l1 x := by
  rw [l1_restrict,l1_restrict]
  exact Finset.sum_add_sum_compl H (fun i => |x i|)

theorem event_complement (x : I → ℝ) (H : Finset I) :
    eventMass x H+eventMass x Hᶜ=mass x :=
  Finset.sum_add_sum_compl H x

theorem eventMass_sub (p q : I → ℝ) (H : Finset I) :
    eventMass (p-q) H=eventMass p H-eventMass q H := by
  simp only [eventMass,Pi.sub_apply,Finset.sum_sub_distrib]

/-- The omitted complement contributes at least the difference of event masses. -/
theorem restriction_budget (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q) (H : Finset I) :
    l1 (restrict p H-restrict q H)+|eventMass p H-eventMass q H| ≤ l1 (p-q) := by
  have hm : mass (p-q)=0 := by rw [map_sub,mass_prior p hp,mass_prior q hq]; ring
  have hc := event_complement (p-q) H
  rw [hm,eventMass_sub,eventMass_sub] at hc
  have ha := abs_mass_le_l1 (restrict (p-q) Hᶜ)
  rw [restrict_mass,eventMass_sub] at ha
  have he : eventMass p Hᶜ-eventMass q Hᶜ= -(eventMass p H-eventMass q H) := by linarith
  rw [he,abs_neg] at ha
  rw [restrict_sub]
  linarith [restriction_complement (p-q) H]

theorem event_difference_le_distance (p q : I → ℝ) (hp : IsPrior p) (hq : IsPrior q)
    (H : Finset I) : |eventMass p H-eventMass q H| ≤ distance p q := by
  have hb := restriction_budget p q hp hq H
  have ha := abs_mass_le_l1 (restrict (p-q) H)
  rw [restrict_mass,eventMass_sub] at ha
  rw [restrict_sub] at hb
  unfold distance
  linarith

end Events

section Marginals
variable {J : Type*} [Fintype J] [DecidableEq J]

theorem aggregate_l1_le (c : I → J) (x : I → ℝ) : l1 (aggregate c x) ≤ l1 x := by
  calc
    l1 (aggregate c x) ≤ ∑ j, ∑ i, |if c i=j then x i else 0| := by
      apply Finset.sum_le_sum
      intro j _
      exact Finset.abs_sum_le_sum_abs _ _
    _ = l1 x := by
      rw [Finset.sum_comm]
      simp [l1,apply_ite abs]

theorem aggregate_sub (c : I → J) (p q : I → ℝ) :
    aggregate c p-aggregate c q=aggregate c (p-q) := by
  funext j
  simp only [aggregate,Pi.sub_apply,← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i _
  split_ifs <;> simp

/-- Forgetting part of a finite record cannot increase total variation. -/
theorem distance_aggregate_le (c : I → J) (p q : I → ℝ) :
    distance (aggregate c p) (aggregate c q) ≤ distance p q := by
  unfold distance
  rw [aggregate_sub]
  exact div_le_div_of_nonneg_right (aggregate_l1_le c (p-q)) (by norm_num)

end Marginals
end Komorebi.LSM.FiniteTV
