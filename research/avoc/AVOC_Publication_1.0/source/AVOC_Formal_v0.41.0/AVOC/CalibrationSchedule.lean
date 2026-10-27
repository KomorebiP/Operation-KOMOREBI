import AVOC.FiniteCalibration

namespace Komorebi.AVOC.CalibrationSchedule

open Finset

/-- A finite exact rational probability space. Correlations between checkpoints
are unrestricted. This is a supplied sampling law, not a law inferred from logs. -/
structure Law (Ω : Type*) [Fintype Ω] where
  weight : Ω → ℚ
  nonneg : ∀ ω, 0 ≤ weight ω
  sum_one : ∑ ω, weight ω = 1

variable {Ω J K : Type*} [Fintype Ω]

noncomputable def eventMass (law : Law Ω) (event : Ω → Prop) : ℚ := by
  classical
  exact ∑ ω, if event ω then law.weight ω else 0

theorem eventMass_nonneg (law : Law Ω) (event : Ω → Prop) :
    0 ≤ eventMass law event := by
  classical
  unfold eventMass
  exact sum_nonneg (fun ω _ => by split <;> simp_all [law.nonneg])

theorem eventMass_mono (law : Law Ω) {a b : Ω → Prop}
    (h : ∀ ω, a ω → b ω) : eventMass law a ≤ eventMass law b := by
  classical
  unfold eventMass
  apply sum_le_sum
  intro ω _
  by_cases ha : a ω
  · simp [ha, h ω ha]
  · simp [ha]
    split <;> simp [law.nonneg]

theorem eventMass_add_compl (law : Law Ω) (event : Ω → Prop) :
    eventMass law event + eventMass law (fun ω => ¬ event ω) = 1 := by
  classical
  unfold eventMass
  rw [← sum_add_distrib]
  calc
    _ = ∑ ω, law.weight ω := by
      apply sum_congr rfl
      intro ω _
      by_cases h : event ω <;> simp [h]
    _ = 1 := law.sum_one

/-- The finite union bound requires no independence of the bad events. -/
theorem finite_union_le [Fintype J] (law : Law Ω) (bad : J → Ω → Prop) :
    eventMass law (fun ω => ∃ j, bad j ω) ≤ ∑ j, eventMass law (bad j) := by
  classical
  unfold eventMass
  calc
    _ ≤ ∑ ω, ∑ j, if bad j ω then law.weight ω else 0 := by
      apply sum_le_sum
      intro ω _
      by_cases h : ∃ j, bad j ω
      · obtain ⟨j, hj⟩ := h
        simp only [ite_eq_left (show ∃ j, bad j ω from ⟨j, hj⟩)]
        calc
          law.weight ω = if bad j ω then law.weight ω else 0 := by simp [hj]
          _ ≤ ∑ j, if bad j ω then law.weight ω else 0 := by
            apply single_le_sum (s := univ) (f := fun j => if bad j ω then law.weight ω else 0)
            · intro j _
              split <;> simp [law.nonneg]
            · exact mem_univ _
      · simp only [ite_eq_right h]
        apply sum_nonneg
        intro j _
        split <;> simp [law.nonneg]
    _ = _ := sum_comm

theorem scheduled_failure_le [Fintype J] (law : Law Ω)
    (bad : J → Ω → Prop) (alpha : J → ℚ)
    (h : ∀ j, eventMass law (bad j) ≤ alpha j) :
    eventMass law (fun ω => ∃ j, bad j ω) ≤ ∑ j, alpha j := by
  exact (finite_union_le law bad).trans (sum_le_sum (fun j _ => h j))

/-- Selection may depend on the complete observed outcome. The schedule and its
individual error budgets must have been fixed before sampling. No cross-checkpoint
independence or restriction on the data-dependent selector is required. -/
theorem selected_failure_le [Fintype J] (law : Law Ω)
    (bad : J → Ω → Prop) (alpha : J → ℚ)
    (h : ∀ j, eventMass law (bad j) ≤ alpha j) (select : Ω → J) :
    eventMass law (fun ω => bad (select ω) ω) ≤ ∑ j, alpha j := by
  apply (eventMass_mono law
    (b := fun ω => ∃ j, bad j ω) (fun ω hω => ⟨select ω, hω⟩)).trans
  exact scheduled_failure_le law bad alpha h

theorem simultaneous_coverage [Fintype J] (law : Law Ω)
    (bad : J → Ω → Prop) (alpha : J → ℚ)
    (h : ∀ j, eventMass law (bad j) ≤ alpha j) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ j, ¬ bad j ω) := by
  have hu := scheduled_failure_le law bad alpha h
  have hc := eventMass_add_compl law (fun ω => ∃ j, bad j ω)
  simp only [not_exists] at hc
  linarith

theorem selected_coverage [Fintype J] (law : Law Ω)
    (bad : J → Ω → Prop) (alpha : J → ℚ)
    (h : ∀ j, eventMass law (bad j) ≤ alpha j) (select : Ω → J) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ¬ bad (select ω) ω) := by
  have hu := selected_failure_le law bad alpha h select
  have hc := eventMass_add_compl law (fun ω => bad (select ω) ω)
  linarith

/-- Pushforward along a finite statistic, expressed using exact fiber masses. -/
theorem statistic_eventMass [Fintype K] (law : Law Ω)
    (stat : Ω → K) (event : K → Prop) [DecidablePred event] :
    eventMass law (fun ω => event (stat ω)) =
      ∑ k, if event k then eventMass law (fun ω => stat ω = k) else 0 := by
  classical
  unfold eventMass
  calc
    _ = ∑ ω, ∑ k, if stat ω = k then
        (if event k then law.weight ω else 0) else 0 := by
      apply sum_congr rfl
      intro ω _
      simp
    _ = ∑ k, ∑ ω, if stat ω = k then
        (if event k then law.weight ω else 0) else 0 := sum_comm
    _ = _ := by
      apply sum_congr rfl
      intro k _
      by_cases hk : event k <;> simp [hk]

/-- A canonical model exists for every admissible rational binomial parameter. -/
def binomialLaw (n : Nat) (p : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    Law (Fin (n + 1)) where
  weight := fun k => FiniteCalibration.mass n k.val p
  nonneg := fun k => FiniteCalibration.mass_nonneg n k.val hp0 hp1
  sum_one := by
    exact (Fin.sum_univ_eq_sum_range (fun k => FiniteCalibration.mass n k p)
      (n + 1)).trans (FiniteCalibration.mass_sum_one n p)

theorem binomialLaw_fiber (n : Nat) (p : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : Fin (n + 1)) :
    eventMass (binomialLaw n p hp0 hp1) (fun observed => observed = k) =
      FiniteCalibration.mass n k.val p := by
  classical
  simp [eventMass, binomialLaw, eq_comm]

/-- The exact count-law obligation is an equality of fiber probabilities. Logs
alone do not establish this obligation. A binomial sampling contract supplies it. -/
theorem binomial_failure_eq (law : Law Ω) (n m : Nat) (alpha p : ℚ)
    (count : Ω → Fin (n + 1))
    (count_law : ∀ k : Fin (n + 1),
      eventMass law (fun ω => count ω = k) = FiniteCalibration.mass n k.val p) :
    eventMass law (fun ω =>
      ¬ FiniteCalibration.Contains n (count ω).val m alpha p) =
        FiniteCalibration.missMass n m alpha p := by
  classical
  rw [statistic_eventMass law count
    (fun k : Fin (n+1) => ¬ FiniteCalibration.Contains n k.val m alpha p)]
  simp_rw [count_law, ite_not]
  unfold FiniteCalibration.missMass
  exact Fin.sum_univ_eq_sum_range (fun k =>
    if FiniteCalibration.Contains n k m alpha p then 0
    else FiniteCalibration.mass n k p) (n + 1)

theorem binomial_failure_le (law : Law Ω) (n m : Nat) (hm : 0 < m)
    (alpha p : ℚ) (ha : 0 ≤ alpha) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (count : Ω → Fin (n + 1))
    (count_law : ∀ k : Fin (n + 1),
      eventMass law (fun ω => count ω = k) = FiniteCalibration.mass n k.val p) :
    eventMass law (fun ω =>
      ¬ FiniteCalibration.Contains n (count ω).val m alpha p) ≤ alpha := by
  rw [binomial_failure_eq law n m alpha p count count_law]
  exact FiniteCalibration.missMass_le n m hm ha hp0 hp1

/-- Simultaneous validity on a finite schedule of predetermined sample sizes,
grids, error allocations, and operation strata. Counts may be arbitrarily
correlated across checkpoints. Only each checkpoint's binomial marginal is used. -/
theorem scheduled_binomial_failure_le [Fintype J] (law : Law Ω)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j)) :
    eventMass law (fun ω => ∃ j,
      ¬ FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j)) ≤
        ∑ j, alpha j := by
  apply scheduled_failure_le
  intro j
  exact binomial_failure_le law (n j) (m j) (hm j) (alpha j) (p j)
    (ha j) (hp0 j) (hp1 j) (count j) (count_law j)

/-- An adaptive choice among a predeclared finite set of checkpoints preserves
the allocated simultaneous error bound. This is not unrestricted optional
stopping and does not authorize inventing new checkpoints after observing data. -/
theorem selected_binomial_failure_le [Fintype J] (law : Law Ω)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j))
    (select : Ω → J) :
    eventMass law (fun ω =>
      ¬ FiniteCalibration.Contains (n (select ω)) (count (select ω) ω).val
        (m (select ω)) (alpha (select ω)) (p (select ω))) ≤ ∑ j, alpha j := by
  refine selected_failure_le law (fun j ω =>
    ¬ FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j))
    alpha ?_ select
  intro j
  exact binomial_failure_le law (n j) (m j) (hm j) (alpha j) (p j)
    (ha j) (hp0 j) (hp1 j) (count j) (count_law j)

theorem selected_binomial_coverage [Fintype J] (law : Law Ω)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j))
    (select : Ω → J) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω =>
      FiniteCalibration.Contains (n (select ω)) (count (select ω) ω).val
        (m (select ω)) (alpha (select ω)) (p (select ω))) := by
  have hu := selected_binomial_failure_le law n m alpha p hm ha hp0 hp1
    count count_law select
  have hc := eventMass_add_compl law (fun ω =>
    FiniteCalibration.Contains (n (select ω)) (count (select ω) ω).val
      (m (select ω)) (alpha (select ω)) (p (select ω)))
  linarith

theorem scheduled_binomial_coverage [Fintype J] (law : Law Ω)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j)) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ j,
      FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j)) := by
  have hu := scheduled_binomial_failure_le law n m alpha p hm ha hp0 hp1
    count count_law
  have hc := eventMass_add_compl law (fun ω => ∃ j,
    ¬ FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j))
  simp only [not_exists, not_not] at hc
  linarith

/-- Any pointwise verified controller guarantee that holds whenever all scheduled
bands cover their true parameters inherits the simultaneous coverage guarantee.
The pointwise implication must be proved separately; it is not assumed by a log. -/
theorem calibrated_conclusion_coverage [Fintype J] (law : Law Ω)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j))
    (conclusion : Ω → Prop)
    (validity : ∀ ω,
      (∀ j, FiniteCalibration.Contains (n j) (count j ω).val
        (m j) (alpha j) (p j)) → conclusion ω) :
    1 - ∑ j, alpha j ≤ eventMass law conclusion := by
  exact (scheduled_binomial_coverage law n m alpha p hm ha hp0 hp1
    count count_law).trans (eventMass_mono law validity)

def fairBoolLaw : Law Bool where
  weight := fun _ => 1 / 2
  nonneg := fun _ => by norm_num
  sum_one := by norm_num [Fintype.sum_bool]

/-- Each fixed event has error 1/2 in this deliberately dependent example. -/
theorem fairBool_fixed_failure (j : Bool) :
    eventMass fairBoolLaw (fun ω => ω = j) = 1 / 2 := by
  cases j <;> norm_num [eventMass, fairBoolLaw, Fintype.sum_bool]

/-- Choosing the index after observing the outcome makes the selected failure
certain. This disproves replacing the scheduled sum by one checkpoint's budget. -/
theorem fairBool_adaptive_failure :
    eventMass fairBoolLaw (fun ω => ω = (fun observed : Bool => observed) ω) = 1 := by
  norm_num [eventMass, fairBoolLaw, Fintype.sum_bool]

theorem fairBool_adaptive_exceeds_single_budget :
    (1 / 2 : ℚ) <
      eventMass fairBoolLaw (fun ω => ω = (fun observed : Bool => observed) ω) := by
  rw [fairBool_adaptive_failure]
  norm_num

end Komorebi.AVOC.CalibrationSchedule
