import AVOC.CalibrationSchedule
import Mathlib.Algebra.BigOperators.Group.Finset.Powerset
import Mathlib.Data.List.FinRange
import Mathlib.Data.Fin.Tuple.Take

namespace Komorebi.AVOC.ObservationStream

open Finset CalibrationSchedule

/-- A length-`n` outcome vector, represented by its successful positions. -/
abbrev Sample (n : Nat) := Finset (Fin n)

/-- Ordered Boolean list used by the reveal process. -/
def sampleList {n : Nat} (s : Sample n) : List Bool :=
  List.ofFn (fun i : Fin n => decide (i ∈ s))

@[simp] theorem sampleList_length {n : Nat} (s : Sample n) :
    (sampleList s).length = n := by simp [sampleList]

@[simp] theorem sampleList_count_true {n : Nat} (s : Sample n) :
    (sampleList s).count true = s.card := by
  classical
  have h := (List.nodup_finRange n).card_eq_countP (P := fun i => i ∈ s)
  simpa [sampleList, List.ofFn_eq_map, List.count, List.countP_map, Function.comp_def] using h.symm

/-- Probability of one complete Bernoulli outcome vector, before aggregating
vectors with the same number of successes. -/
def vectorMass (n : Nat) (p : ℚ) (sample : Sample n) : ℚ :=
  p ^ sample.card * (1 - p) ^ (n - sample.card)

/-- The binomial coefficient arises by counting complete vectors, not from an
assumed law for the observed success count. -/
theorem vectorMass_card_sum (n k : Nat) (p : ℚ) :
    (∑ s : Sample n, if s.card = k then vectorMass n p s else 0) =
      FiniteCalibration.mass n k p := by
  classical
  calc
    _ = ∑ s ∈ (univ : Finset (Fin n)).powersetCard k, vectorMass n p s := by
      rw [powersetCard_eq_filter, powerset_univ, sum_filter]
    _ = (n.choose k : ℚ) * (p ^ k * (1 - p) ^ (n - k)) := by
      simpa [vectorMass, nsmul_eq_mul] using
        (sum_powersetCard k (univ : Finset (Fin n))
          (fun j => p ^ j * (1 - p) ^ (n - j)))
    _ = _ := by unfold FiniteCalibration.mass; ring

theorem vectorMass_sum_one (n : Nat) (p : ℚ) :
    ∑ s : Sample n, vectorMass n p s = 1 := by
  classical
  calc
    _ = ∑ j ∈ range (n + 1),
        ∑ s ∈ (univ : Finset (Fin n)).powersetCard j, vectorMass n p s := by
      simpa using sum_powerset (univ : Finset (Fin n)) (vectorMass n p)
    _ = ∑ j ∈ range (n + 1), FiniteCalibration.mass n j p := by
      apply sum_congr rfl
      intro j _
      rw [powersetCard_eq_filter, powerset_univ, sum_filter]
      exact vectorMass_card_sum n j p
    _ = 1 := FiniteCalibration.mass_sum_one n p

/-- Explicit independent Bernoulli stream model. This supplies a nonempty
realization of the primitive full-vector contract for every rational parameter. -/
def bernoulliLaw (n : Nat) (p : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) : Law (Sample n) where
  weight := vectorMass n p
  nonneg := fun s => by unfold vectorMass; positivity
  sum_one := vectorMass_sum_one n p

variable {Ω : Type*} [Fintype Ω]

/-- Primitive joint outcome law: all exact ordered outcome patterns have the
Bernoulli product probability. The success count law is derived below. -/
def ProductLaw (law : Law Ω) (n : Nat) (p : ℚ) (stream : Ω → Sample n) : Prop :=
  ∀ s, eventMass law (fun ω => stream ω = s) = vectorMass n p s

/-- Agreement with a specified pattern on already inspected positions. -/
def Matches {n : Nat} (seen target sample : Sample n) : Prop :=
  ∀ i ∈ seen, (i ∈ sample ↔ i ∈ target)

/-- Primitive conditional independence contract. After every finite revealed
pattern, a fresh position has success mass `p` times the history mass. This is
multiplication-only, so impossible histories impose no conditioning division. -/
def ConditionalLaw (law : Law Ω) (n : Nat) (p : ℚ) (stream : Ω → Sample n) : Prop :=
  ∀ (seen target : Sample n) (i : Fin n), i ∉ seen →
    eventMass law (fun ω => Matches seen target (stream ω) ∧ i ∈ stream ω) =
      p * eventMass law (fun ω => Matches seen target (stream ω))

theorem eventMass_split (law : Law Ω) (a b : Ω → Prop) :
    eventMass law (fun ω => a ω ∧ b ω) +
      eventMass law (fun ω => a ω ∧ ¬ b ω) = eventMass law a := by
  classical
  unfold eventMass
  rw [← sum_add_distrib]
  apply sum_congr rfl
  intro ω _
  by_cases ha : a ω <;> by_cases hb : b ω <;> simp [ha, hb]

theorem vectorMass_eq_product {n : Nat} (p : ℚ) (s : Sample n) :
    vectorMass n p s = ∏ i : Fin n, if i ∈ s then p else 1 - p := by
  classical
  rw [prod_ite]
  simp [vectorMass, ← compl_eq_univ_sdiff, ← sdiff_eq_filter, card_compl]

/-- The conditional fresh-outcome contract determines every finite pattern's
joint probability. -/
theorem conditional_pattern_mass (law : Law Ω) (n : Nat) (p : ℚ)
    (stream : Ω → Sample n) (h : ConditionalLaw law n p stream)
    (seen target : Sample n) :
    eventMass law (fun ω => Matches seen target (stream ω)) =
      ∏ i ∈ seen, if i ∈ target then p else 1 - p := by
  classical
  induction seen using Finset.induction_on with
  | empty => simp [Matches, eventMass, law.sum_one]
  | @insert i seen hi ih =>
    have hs := h seen target i hi
    have he := eventMass_split law (fun ω => Matches seen target (stream ω))
      (fun ω => i ∈ stream ω)
    rw [prod_insert hi]
    by_cases hit : i ∈ target
    · have hm : (fun ω => Matches (insert i seen) target (stream ω)) =
          (fun ω => Matches seen target (stream ω) ∧ i ∈ stream ω) := by
        funext ω
        simp [Matches, hit, and_comm]
      rw [hm, hs, ih, ite_eq_left hit]
    · have hm : (fun ω => Matches (insert i seen) target (stream ω)) =
          (fun ω => Matches seen target (stream ω) ∧ i ∉ stream ω) := by
        funext ω
        simp [Matches, hit, and_comm]
      rw [hm, ite_eq_right hit]
      rw [ih] at hs he
      linarith

/-- Thus one-step conditional independence implies the primitive product law. -/
theorem conditional_implies_product (law : Law Ω) (n : Nat) (p : ℚ)
    (stream : Ω → Sample n) (h : ConditionalLaw law n p stream) :
    ProductLaw law n p stream := by
  classical
  intro target
  have hm : (fun ω => Matches univ target (stream ω)) =
      (fun ω => stream ω = target) := by
    funext ω
    simp [Matches, Finset.ext_iff]
  have hp := conditional_pattern_mass law n p stream h univ target
  rw [hm, ← vectorMass_eq_product] at hp
  exact hp

def streamCount {n : Nat} (stream : Ω → Sample n) (ω : Ω) : Fin (n + 1) :=
  ⟨(stream ω).card, Nat.lt_succ_iff.mpr (by simpa using card_le_univ (stream ω))⟩

theorem bernoulliLaw_product (n : Nat) (p : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    ProductLaw (bernoulliLaw n p hp0 hp1) n p id := by
  classical
  intro s
  simp [eventMass, bernoulliLaw, eq_comm]

/-- A primitive independent stream implies the exact binomial count law used by
finite calibration. This conclusion does not assume a count distribution. -/
theorem count_fiber_eq_binomial (law : Law Ω) (n : Nat) (p : ℚ)
    (stream : Ω → Sample n) (h : ProductLaw law n p stream) (k : Fin (n + 1)) :
    eventMass law (fun ω => streamCount stream ω = k) =
      FiniteCalibration.mass n k.val p := by
  classical
  have he : (fun ω => streamCount stream ω = k) =
      (fun ω => (stream ω).card = k.val) := by
    funext ω
    simp [streamCount, Fin.ext_iff]
  rw [he, statistic_eventMass law stream (fun s => s.card = k.val)]
  change (∑ s : Sample n, if s.card = k.val then
    eventMass law (fun ω => stream ω = s) else 0) = _
  simp_rw [show ∀ s, eventMass law (fun ω => stream ω = s) = vectorMass n p s from h]
  exact vectorMass_card_sum n k.val p

/-- Direct form using the primitive conditional fresh-outcome contract. -/
theorem conditional_count_fiber_eq_binomial (law : Law Ω) (n : Nat) (p : ℚ)
    (stream : Ω → Sample n) (h : ConditionalLaw law n p stream) (k : Fin (n + 1)) :
    eventMass law (fun ω => streamCount stream ω = k) =
      FiniteCalibration.mass n k.val p :=
  count_fiber_eq_binomial law n p stream (conditional_implies_product law n p stream h) k

/-- Calibration is now a consequence of the primitive outcome-stream contract. -/
theorem stream_failure_le (law : Law Ω) (n m : Nat) (hm : 0 < m)
    (alpha p : ℚ) (ha : 0 ≤ alpha) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (stream : Ω → Sample n) (h : ProductLaw law n p stream) :
    eventMass law (fun ω =>
      ¬ FiniteCalibration.Contains n (streamCount stream ω).val m alpha p) ≤ alpha := by
  exact binomial_failure_le law n m hm alpha p ha hp0 hp1 (streamCount stream)
    (count_fiber_eq_binomial law n p stream h)

/-- Ordered report lists have the same count fibers as their success-position
representation. This is the interface to the operational reveal process. -/
theorem sampleList_count_fiber_eq_binomial (law : Law Ω) (n : Nat) (p : ℚ)
    (stream : Ω → Sample n) (h : ProductLaw law n p stream) (k : Fin (n + 1)) :
    eventMass law (fun ω => (sampleList (stream ω)).count true = k.val) =
      FiniteCalibration.mass n k.val p := by
  have he : (fun ω => (sampleList (stream ω)).count true = k.val) =
      (fun ω => streamCount stream ω = k) := by
    funext ω
    simp [streamCount, Fin.ext_iff]
  rw [he]
  exact count_fiber_eq_binomial law n p stream h k

/-- Calibration follows directly from one-step conditional fresh-outcome
probabilities; no success-count distribution is supplied as a hypothesis. -/
theorem conditional_stream_failure_le (law : Law Ω) (n m : Nat) (hm : 0 < m)
    (alpha p : ℚ) (ha : 0 ≤ alpha) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (stream : Ω → Sample n) (h : ConditionalLaw law n p stream) :
    eventMass law (fun ω =>
      ¬ FiniteCalibration.Contains n (streamCount stream ω).val m alpha p) ≤ alpha :=
  stream_failure_le law n m hm alpha p ha hp0 hp1 stream
    (conditional_implies_product law n p stream h)

/-- The first `n` positions of a common latent source of length `N`. -/
def truncateSample {N : Nat} (n : Nat) (hn : n ≤ N) (s : Sample N) : Sample n :=
  univ.filter (fun i => Fin.castLE hn i ∈ s)

@[simp] theorem mem_truncateSample {N n : Nat} (hn : n ≤ N) (s : Sample N) (i : Fin n) :
    i ∈ truncateSample n hn s ↔ Fin.castLE hn i ∈ s := by
  simp [truncateSample]

/-- Truncating a success-position representation takes the same prefix of the
ordered outcome list. -/
theorem sampleList_truncate {N n : Nat} (hn : n ≤ N) (s : Sample N) :
    sampleList (truncateSample n hn s) = (sampleList s).take n := by
  unfold sampleList
  rw [← Fin.ofFn_take_eq_take_ofFn hn]
  congr 1
  funext i
  simp only [Fin.take_apply, mem_truncateSample]

theorem matches_truncate {N n : Nat} (hn : n ≤ N)
    (seen target : Sample n) (s : Sample N) :
    Matches seen target (truncateSample n hn s) ↔
      Matches (seen.image (Fin.castLE hn)) (target.image (Fin.castLE hn)) s := by
  simp [Matches, mem_image, Fin.castLE_inj]

/-- A predeclared prefix of a source inherits the fresh-outcome contract. This
allows several scheduled sample sizes to share the same per-identity stream. -/
theorem conditional_truncate (law : Law Ω) (N : Nat) (p : ℚ)
    (stream : Ω → Sample N) (h : ConditionalLaw law N p stream)
    (n : Nat) (hn : n ≤ N) :
    ConditionalLaw law n p (fun ω => truncateSample n hn (stream ω)) := by
  classical
  intro seen target i hi
  have hfresh : Fin.castLE hn i ∉ seen.image (Fin.castLE hn) := by
    simpa only [mem_image, Fin.castLE_inj, exists_eq_right] using hi
  have hx := h (seen.image (Fin.castLE hn)) (target.image (Fin.castLE hn))
    (Fin.castLE hn i) hfresh
  simpa only [mem_truncateSample, matches_truncate] using hx

/-- Primitive conditional laws yield binomial counts at every predeclared
prefix, without assuming independent checkpoint counts. -/
theorem prefix_count_fiber_eq_binomial (law : Law Ω) (N : Nat) (p : ℚ)
    (stream : Ω → Sample N) (h : ConditionalLaw law N p stream)
    (n : Nat) (hn : n ≤ N) (k : Fin (n + 1)) :
    eventMass law (fun ω => streamCount (fun ω => truncateSample n hn (stream ω)) ω = k) =
      FiniteCalibration.mass n k.val p :=
  conditional_count_fiber_eq_binomial law n p (fun ω => truncateSample n hn (stream ω))
    (conditional_truncate law N p stream h n hn) k

/-- Equivalent prefix theorem at the operational list/count interface. -/
theorem prefix_list_count_fiber_eq_binomial (law : Law Ω) (N : Nat) (p : ℚ)
    (stream : Ω → Sample N) (h : ConditionalLaw law N p stream)
    (n : Nat) (hn : n ≤ N) (k : Fin (n + 1)) :
    eventMass law (fun ω => ((sampleList (stream ω)).take n).count true = k.val) =
      FiniteCalibration.mass n k.val p := by
  simpa only [sampleList_truncate] using
    sampleList_count_fiber_eq_binomial law n p (fun ω => truncateSample n hn (stream ω))
      (conditional_implies_product law n p _ (conditional_truncate law N p stream h n hn)) k

/-- A concrete nontrivial conditional model, with one fair latent outcome. -/
def fairOne (b : Bool) : Sample 1 := if b then univ else ∅

theorem fairOne_conditional : ConditionalLaw fairBoolLaw 1 (1 / 2) fairOne := by
  intro seen target i hi
  fin_cases seen <;> fin_cases target <;> fin_cases i <;>
    simp_all [Matches, eventMass, fairBoolLaw, fairOne]

/-- Two perfectly correlated fair bits: each coordinate is fair, but their
count is not binomial. This guards against replacing the conditional contract
with marginal success frequencies alone. -/
def correlatedPair (b : Bool) : Sample 2 := if b then univ else ∅

theorem correlatedPair_marginal (i : Fin 2) :
    eventMass fairBoolLaw (fun b => i ∈ correlatedPair b) = 1 / 2 := by
  norm_num [eventMass, fairBoolLaw, correlatedPair, Fintype.sum_bool]

theorem correlatedPair_one_success_mass :
    eventMass fairBoolLaw (fun b => streamCount correlatedPair b = (1 : Fin 3)) = 0 := by
  norm_num [eventMass, fairBoolLaw, correlatedPair, streamCount, Fintype.sum_bool,
    Fin.ext_iff]

theorem correlatedPair_not_product : ¬ ProductLaw fairBoolLaw 2 (1 / 2) correlatedPair := by
  intro h
  have hc := count_fiber_eq_binomial fairBoolLaw 2 (1 / 2) correlatedPair h (1 : Fin 3)
  rw [correlatedPair_one_success_mass] at hc
  norm_num [FiniteCalibration.mass] at hc

end Komorebi.AVOC.ObservationStream
