module
public import Mathlib.Data.Fintype.Card
public import Mathlib.Data.Fintype.Sigma
public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 3.1, 3.2, 3.4, 3.6, 3.8, 3.9, 3.10, 4.2.
Counts come from explicit finite address/event types. A modeled multiply-accumulate
costs two scalar operations; this is not a measurement of GPU instructions/time.
The thin output product accumulates into the diagonal result.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators

/-- Scalar storage addresses for a finite collection of rectangular blocks. -/
abbrev PacketEntry (E : Type*) (rows cols : E → ℕ) :=
  (e : E) × (Fin (rows e) × Fin (cols e))

/-- Two operations per scalar coefficient and right-hand side, by declared model. -/
abbrev PacketOperation (E : Type*) (rows cols : E → ℕ) (q : ℕ) :=
  PacketEntry E rows cols × Fin q × Bool

theorem packet_storage_count {E : Type*} [Fintype E] (rows cols : E → ℕ) :
    Fintype.card (PacketEntry E rows cols) = ∑ e, rows e * cols e := by
  simp [PacketEntry, Fintype.card_sigma, Fintype.card_prod]

theorem packet_application_count {E : Type*} [Fintype E] (rows cols : E → ℕ) (q : ℕ) :
    Fintype.card (PacketOperation E rows cols q) = 2 * q * ∑ e, rows e * cols e := by
  simp [PacketOperation, Fintype.card_prod]
  ring

theorem dense_storage_count (n : ℕ) : Fintype.card (Fin n × Fin n) = n ^ 2 := by
  simp [pow_two]

theorem dense_application_count (n q : ℕ) :
    Fintype.card ((Fin n × Fin n) × Fin q × Bool) = 2 * n ^ 2 * q := by
  simp [Fintype.card_prod]
  ring

theorem equal_diagonal_storage {I : Type*} [Fintype I] (b : ℕ) :
    Fintype.card (PacketEntry I (fun _ => b) (fun _ => b)) = (Fintype.card I * b) * b := by
  simp [mul_assoc]

theorem equal_diagonal_work {I : Type*} [Fintype I] (b q : ℕ) :
    Fintype.card (PacketOperation I (fun _ => b) (fun _ => b) q) =
      2 * q * (Fintype.card I * b) * b := by
  simp
  ring

/-- The complete BDLR scalar representation, including both thin factors. -/
abbrev BDLREntry (I : Type*) (width : I → ℕ) (n r : ℕ) :=
  PacketEntry I width width ⊕ ((Fin n × Fin r) ⊕ (Fin n × Fin r))

theorem bdlr_storage_count {I : Type*} [Fintype I] (width : I → ℕ) (n r : ℕ) :
    Fintype.card (BDLREntry I width n r) = (∑ i, width i ^ 2) + 2 * n * r := by
  simp [BDLREntry, pow_two]
  ring

/-- The three stages are diagonal application and two thin products. -/
abbrev BDLROperation (I : Type*) (width : I → ℕ) (n r q : ℕ) :=
  PacketOperation I width width q ⊕
    (((Fin n × Fin r) × Fin q × Bool) ⊕ ((Fin n × Fin r) × Fin q × Bool))

theorem bdlr_application_count {I : Type*} [Fintype I]
    (width : I → ℕ) (n r q : ℕ) :
    Fintype.card (BDLROperation I width n r q) =
      2 * q * ((∑ i, width i ^ 2) + 2 * n * r) := by
  simp [BDLROperation, pow_two]
  ring

theorem equal_bdlr_storage {I : Type*} [Fintype I] (b r : ℕ) :
    Fintype.card (BDLREntry I (fun _ => b) (Fintype.card I * b) r) =
      (Fintype.card I * b) * (b + 2 * r) := by
  simp
  ring

theorem equal_bdlr_work {I : Type*} [Fintype I] (b r q : ℕ) :
    Fintype.card (BDLROperation I (fun _ => b) (Fintype.card I * b) r q) =
      2 * q * (Fintype.card I * b) * (b + 2 * r) := by
  simp
  ring

theorem equal_block_reduction (n b : ℝ) (hn : n ≠ 0) (hb : b ≠ 0) :
    n ^ 2 / (n * b) = n / b := by
  field_simp

theorem equal_bdlr_reduction (n b r q : ℝ) (hn : n ≠ 0) (hq : q ≠ 0)
    (hbr : b + 2 * r ≠ 0) :
    n ^ 2 / (n * (b + 2 * r)) = n / (b + 2 * r) ∧
    (2 * q * n ^ 2) / (2 * q * n * (b + 2 * r)) = n / (b + 2 * r) := by
  constructor <;> field_simp

/-- One block read, one source read, and target read plus write for each edge. -/
abbrev StreamEvent (E : Type*) (rows cols : E → ℕ) (q : ℕ) :=
  (e : E) × ((Fin (rows e) × Fin (cols e)) ⊕
    ((Fin (cols e) × Fin q) ⊕ ((Fin (rows e) × Fin q) × Bool)))

theorem streaming_value_count {E : Type*} [Fintype E] (rows cols : E → ℕ) (q : ℕ) :
    Fintype.card (StreamEvent E rows cols q) =
      ∑ e, (rows e * cols e + cols e * q + 2 * rows e * q) := by
  simp only [StreamEvent, Fintype.card_sigma, Fintype.card_sum, Fintype.card_prod,
    Fintype.card_fin, Fintype.card_bool]
  apply Finset.sum_congr rfl
  intro e _
  ring

theorem streaming_byte_count {E : Type*} [Fintype E]
    (rows cols : E → ℕ) (q bytesPerScalar : ℕ) :
    Fintype.card (Fin bytesPerScalar × StreamEvent E rows cols q) =
      bytesPerScalar * ∑ e, (rows e * cols e + cols e * q + 2 * rows e * q) := by
  change bytesPerScalar * Fintype.card (StreamEvent E rows cols q) = _
  rw [streaming_value_count]

/-- Both physical capacity inequalities are hypotheses, not conclusions of the model. -/
theorem roofline_time_bound (F B P W T : ℝ) (hP : 0 < P) (hW : 0 < W)
    (hF : F ≤ P * T) (hB : B ≤ W * T) : max (F / P) (B / W) ≤ T := by
  apply max_le
  · apply (div_le_iff₀ hP).2
    nlinarith
  · apply (div_le_iff₀ hW).2
    nlinarith

theorem roofline_work_rate (F B P W T : ℝ) (hF : 0 ≤ F) (hB : 0 < B)
    (hT : 0 < T) (hp : F ≤ P * T) (hw : B ≤ W * T) :
    F / T ≤ min P (W * (F / B)) := by
  apply le_min
  · apply (div_le_iff₀ hT).2
    nlinarith
  · apply (div_le_iff₀ hT).2
    have hprod := mul_le_mul_of_nonneg_left hw hF
    have hclear : F * B ≤ (W * F) * T := by nlinarith
    calc
      F ≤ (W * F * T) / B := (le_div_iff₀ hB).2 hclear
      _ = W * (F / B) * T := by ring

theorem dense_capacity_threshold (n M s : ℝ) (hn : 0 ≤ n) (hM : 0 ≤ M) (hs : 0 < s) :
    n ^ 2 * s ≤ M ↔ n ≤ Real.sqrt (M / s) := by
  rw [Real.le_sqrt hn (div_nonneg hM (le_of_lt hs)), le_div_iff₀ hs]

theorem bdlr_capacity_threshold (n b r s M : ℕ) :
    n * (b + 2 * r) * s ≤ M ↔ s * (n * b + 2 * n * r) ≤ M := by
  ring

/-- An explicit scalar addition for each entry is a concrete O(n^2) remainder. -/
abbrev MaterializeOperation (n r : ℕ) :=
  ((Fin n × Fin n) × Fin r × Bool) ⊕ (Fin n × Fin n)

theorem materialization_work_count (n r : ℕ) :
    Fintype.card (MaterializeOperation n r) = 2 * n ^ 2 * r + n ^ 2 := by
  simp [MaterializeOperation]
  ring

theorem materialization_quadratic_remainder (n r : ℕ) :
    Fintype.card (MaterializeOperation n r) - 2 * n ^ 2 * r ≤ n ^ 2 := by
  rw [materialization_work_count]
  omega

/-- Sparse indices are excluded exactly as in the source's scalar-value model. -/
abbrev SparseLowRankEntry (z n r : ℕ) := Fin z ⊕ ((Fin n × Fin r) ⊕ (Fin n × Fin r))

theorem sparse_low_rank_storage_count (z n r : ℕ) :
    Fintype.card (SparseLowRankEntry z n r) = z + 2 * n * r := by
  simp [SparseLowRankEntry]
  ring

theorem sparse_low_rank_work_count (z n r q : ℕ) :
    Fintype.card (SparseLowRankEntry z n r × Fin q × Bool) = 2 * q * (z + 2 * n * r) := by
  simp
  ring

end KomorebiPaperVIII
