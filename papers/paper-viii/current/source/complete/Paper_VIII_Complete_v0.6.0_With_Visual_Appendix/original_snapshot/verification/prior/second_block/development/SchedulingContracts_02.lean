module
public import Mathlib.Algebra.Order.Floor.Semiring
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Algebra.Order.AbsoluteValue.Basic
public import Mathlib.Data.Rat.Floor
public import Mathlib.Data.Finset.Card
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 10.2, 10.4--10.6, 11.3, with a mathematical implementation of 2.9.
Times are declared real-valued models, never claimed hardware measurements.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators

/-- Complete signature fields required for fair timing comparisons. -/
structure BenchmarkSignature (Case Output Reference Scope : Type*) where
  caseKey : Case
  outputContract : Output
  reference : Reference
  timingScope : Scope
  deriving DecidableEq

/-- Extra metadata such as measured time is deliberately absent from this relation. -/
def FairMatch {C O R S : Type*} (a b : BenchmarkSignature C O R S) : Prop :=
  a.caseKey = b.caseKey ∧ a.outputContract = b.outputContract ∧
    a.reference = b.reference ∧ a.timingScope = b.timingScope

theorem fair_match_iff_eq {C O R S : Type*} (a b : BenchmarkSignature C O R S) :
    FairMatch a b ↔ a = b := by
  constructor
  · rintro ⟨hc, ho, hr, hs⟩
    cases a; cases b
    simp_all
  · intro h; subst b; exact ⟨rfl, rfl, rfl, rfl⟩

theorem fair_matching_equivalence {C O R S : Type*} :
    Equivalence (FairMatch (C := C) (O := O) (R := R) (S := S)) := by
  constructor
  · intro a; exact (fair_match_iff_eq a a).2 rfl
  · intro a b h; exact (fair_match_iff_eq b a).2 ((fair_match_iff_eq a b).1 h).symm
  · intro a b c hab hbc
    exact (fair_match_iff_eq a c).2
      (((fair_match_iff_eq a b).1 hab).trans ((fair_match_iff_eq b c).1 hbc))

/-- A decoded run actually returns the explicit object and includes conversion time. -/
def decodedRun {X C Y : Type*} (compressed : X → C) (decode : C → Y)
    (runTime : X → ℝ) (decodeTime : C → ℝ) (x : X) : Y × ℝ :=
  (decode (compressed x), runTime x + decodeTime (compressed x))

theorem contract_conversion {X C Y : Type*} (compressed : X → C) (explicit : X → Y)
    (decode : C → Y) (runTime : X → ℝ) (decodeTime : C → ℝ)
    (hdecode : ∀ x, decode (compressed x) = explicit x) (x : X) :
    (decodedRun compressed decode runTime decodeTime x).1 = explicit x ∧
    (decodedRun compressed decode runTime decodeTime x).2 =
      runTime x + decodeTime (compressed x) := by
  exact ⟨hdecode x, rfl⟩

theorem direct_compressed_consumption {X C Y Z : Type*}
    (compressed : X → C) (explicit : X → Y) (decode : C → Y)
    (consume : Y → Z) (hdecode : ∀ x, decode (compressed x) = explicit x) :
    (fun x => consume (decode (compressed x))) = fun x => consume (explicit x) := by
  funext x
  rw [hdecode x]

theorem omitted_decode_understates_time {X C Y : Type*} (compressed : X → C)
    (decode : C → Y) (runTime : X → ℝ) (decodeTime : C → ℝ)
    (x : X) (h : 0 < decodeTime (compressed x)) :
    runTime x < (decodedRun compressed decode runTime decodeTime x).2 := by
  dsimp [decodedRun]
  linarith

/-- Active shape classes are exactly the image of the complete kernel signature. -/
def activeShapeClasses {E Shape : Type*} [Fintype E] [DecidableEq Shape]
    (key : E → Shape) : Finset Shape := Finset.univ.image key

theorem shape_launch_count {E Shape : Type*} [Fintype E] [DecidableEq Shape]
    (key : E → Shape) : (activeShapeClasses key).card ≤ Fintype.card E := by
  exact Finset.card_image_le

theorem each_block_has_shape {E Shape : Type*} [Fintype E] [DecidableEq Shape]
    (key : E → Shape) (e : E) : key e ∈ activeShapeClasses key := by
  exact Finset.mem_image_of_mem key (Finset.mem_univ e)

/-- Grouping does not duplicate or lose any block contribution. -/
theorem grouped_execution_output {E Shape V : Type*} [Fintype E] [DecidableEq Shape]
    [AddCommMonoid V] (key : E → Shape) (value : E → V) :
    (∑ k ∈ activeShapeClasses key, ∑ e ∈ Finset.univ.filter (fun e => key e = k), value e) =
      ∑ e, value e := by
  exact Finset.sum_fiberwise_of_maps_to (fun e _ => each_block_has_shape key e) value

theorem grouped_execution_work {E Shape : Type*} [Fintype E] [DecidableEq Shape]
    (key : E → Shape) (work : E → ℕ) :
    (∑ k ∈ activeShapeClasses key, ∑ e ∈ Finset.univ.filter (fun e => key e = k), work e) =
      ∑ e, work e := by
  exact grouped_execution_output key work

theorem amortization_threshold (setup baseline candidate reuse : ℝ)
    (h : candidate < baseline) :
    setup + reuse * candidate < reuse * baseline ↔ setup / (baseline - candidate) < reuse := by
  rw [div_lt_iff₀ (sub_pos.mpr h)]
  constructor <;> intro hh <;> nlinarith

theorem no_amortization (setup baseline candidate reuse : ℝ)
    (hs : 0 ≤ setup) (hr : 0 ≤ reuse) (h : baseline ≤ candidate) :
    ¬ setup + reuse * candidate < reuse * baseline := by
  have hm := mul_le_mul_of_nonneg_left h hr
  linarith

/-- Strict profitability, not mere break-even, gives floor plus one. -/
noncomputable def minimumReuse (setup baseline candidate : ℝ) : ℕ :=
  ⌊setup / (baseline - candidate)⌋₊ + 1

theorem integer_amortization_threshold (setup baseline candidate : ℝ)
    (hs : 0 ≤ setup) (h : candidate < baseline) (reuse : ℕ) :
    setup + (reuse : ℝ) * candidate < (reuse : ℝ) * baseline ↔
      minimumReuse setup baseline candidate ≤ reuse := by
  rw [amortization_threshold setup baseline candidate reuse h, minimumReuse]
  rw [← Nat.floor_lt (div_nonneg hs (le_of_lt (sub_pos.mpr h)))]
  omega

theorem minimum_reuse_attains (setup baseline candidate : ℝ)
    (hs : 0 ≤ setup) (h : candidate < baseline) :
    setup + (minimumReuse setup baseline candidate : ℝ) * candidate <
      (minimumReuse setup baseline candidate : ℝ) * baseline ∧
    ∀ reuse : ℕ, reuse < minimumReuse setup baseline candidate →
      ¬ setup + (reuse : ℝ) * candidate < (reuse : ℝ) * baseline := by
  constructor
  · exact (integer_amortization_threshold setup baseline candidate hs h _).2 le_rfl
  · intro reuse hr
    rw [integer_amortization_threshold setup baseline candidate hs h reuse]
    omega

theorem graph_replay_threshold (capture ordinary replay reuse : ℝ) (h : replay < ordinary) :
    capture + reuse * replay < reuse * ordinary ↔ capture / (ordinary - replay) < reuse := by
  exact amortization_threshold capture ordinary replay reuse h

/-- Necessity includes an actual per-use advantage; zero uses cannot be profitable. -/
theorem materialization_threshold (materialize compressed explicit reuse : ℝ)
    (hm : 0 ≤ materialize) (hr : 0 ≤ reuse) :
    materialize + reuse * explicit < reuse * compressed ↔
      explicit < compressed ∧ materialize / (compressed - explicit) < reuse := by
  constructor
  · intro h
    have he : explicit < compressed := by
      by_contra hn
      exact no_amortization materialize compressed explicit reuse hm hr (le_of_not_gt hn) h
    exact ⟨he, (amortization_threshold materialize compressed explicit reuse he).1 h⟩
  · rintro ⟨he, hs⟩
    exact (amortization_threshold materialize compressed explicit reuse he).2 hs

theorem zero_setup_first_use (baseline candidate : ℝ) (_h : candidate < baseline) :
    minimumReuse 0 baseline candidate = 1 := by
  simp [minimumReuse]

theorem exact_break_even_regression :
    minimumReuse 6 5 3 = 4 ∧
      ¬ (6 : ℝ) + 3 * 3 < 3 * 5 ∧ (6 : ℝ) + 4 * 3 < 4 * 5 := by
  norm_num [minimumReuse]

end KomorebiPaperVIII
