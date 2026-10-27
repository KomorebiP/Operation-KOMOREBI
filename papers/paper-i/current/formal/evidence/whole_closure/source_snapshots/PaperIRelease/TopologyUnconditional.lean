import KomorebiVerification.TopologicalCompletion
import Mathlib.Analysis.Normed.Operator.BanachSteinhaus
import Mathlib.Analysis.Normed.Module.DoubleDual
import Mathlib.Analysis.Normed.Module.FiniteDimension

/-! # The general unconditional sum norm -/

noncomputable section
open scoped BigOperators
open Set Function Filter Topology

namespace PaperIRelease.TopologyUnconditional

variable {𝕜 X : Type*} [RCLike 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]

/-- A finite collection of coefficients from the scalar closed unit ball. -/
def Coefficients (𝕜 : Type*) [RCLike 𝕜] :=
  Finset ℕ × {a : ℕ → 𝕜 // ∀ n, ‖a n‖ ≤ 1}

def finiteSum (x : ℕ → X) (c : Coefficients 𝕜) : X :=
  ∑ n ∈ c.1, c.2.val n • x n

/-- Unconditional summability bounds every finite unit-ball multiplier sum.
The proof applies uniform boundedness on the continuous dual, whose scalar
images are absolutely summable, and then the isometric double-dual embedding. -/
theorem summable_finiteSum_bounded (x : ℕ → X) (hx : Summable x) :
    ∃ C : ℝ, ∀ c : Coefficients 𝕜, ‖finiteSum x c‖ ≤ C := by
  let g : Coefficients 𝕜 → StrongDual 𝕜 (StrongDual 𝕜 X) :=
    fun c ↦ NormedSpace.inclusionInDoubleDual 𝕜 X (finiteSum x c)
  have hpoint : ∀ ℓ : StrongDual 𝕜 X, ∃ C : ℝ, ∀ c, ‖g c ℓ‖ ≤ C := by
    intro ℓ
    have hs : Summable (fun n ↦ ‖ℓ (x n)‖) := (ℓ.summable hx).norm
    refine ⟨∑' n, ‖ℓ (x n)‖, fun c ↦ ?_⟩
    change ‖ℓ (finiteSum x c)‖ ≤ _
    simp only [finiteSum, map_sum, map_smul]
    calc
      ‖∑ n ∈ c.1, c.2.val n • ℓ (x n)‖ ≤ ∑ n ∈ c.1, ‖c.2.val n • ℓ (x n)‖ :=
        norm_sum_le _ _
      _ ≤ ∑ n ∈ c.1, ‖ℓ (x n)‖ := by
        apply Finset.sum_le_sum
        intro n _
        rw [norm_smul]
        exact mul_le_of_le_one_left (norm_nonneg _) (c.2.property n)
      _ ≤ ∑' n, ‖ℓ (x n)‖ := hs.sum_le_tsum c.1 (fun _ _ ↦ norm_nonneg _)
  obtain ⟨C, hC⟩ := banach_steinhaus hpoint
  refine ⟨C, fun c ↦ ?_⟩
  have he : ‖g c‖ = ‖finiteSum x c‖ :=
    (NormedSpace.inclusionInDoubleDualLi 𝕜).norm_map (finiteSum x c)
  rw [← he]
  exact hC c

/-- A countable family of closed ambient subspaces. -/
structure ClosedPackets (𝕜 X : Type*) [RCLike 𝕜]
    [NormedAddCommGroup X] [NormedSpace 𝕜 X] where
  packet : ℕ → Submodule 𝕜 X
  closed : ∀ n, IsClosed (packet n : Set X)

namespace ClosedPackets

variable (Q : ClosedPackets 𝕜 X)

def sequences : Submodule 𝕜 (ℕ → X) where
  carrier := {x | (∀ n, x n ∈ Q.packet n) ∧ Summable x}
  zero_mem' := ⟨fun _ ↦ Submodule.zero_mem _, summable_zero⟩
  add_mem' := by
    rintro x y ⟨hx, hxs⟩ ⟨hy, hys⟩
    exact ⟨fun n ↦ Submodule.add_mem _ (hx n) (hy n), hxs.add hys⟩
  smul_mem' := by
    rintro c x ⟨hx, hxs⟩
    exact ⟨fun n ↦ Submodule.smul_mem _ c (hx n), hxs.const_smul c⟩

/-- A type synonym separates the signed-sum topology from the product
topology on the space of all sequences. -/
def Space : Type _ := Q.sequences

instance spaceAddCommGroup : AddCommGroup Q.Space :=
  inferInstanceAs (AddCommGroup Q.sequences)

instance spaceModule : Module 𝕜 Q.Space :=
  inferInstanceAs (Module 𝕜 Q.sequences)

@[ext]
theorem Space.ext (x y : Q.Space) (h : ∀ n, x.val n = y.val n) : x = y :=
  Subtype.ext (funext h)

@[simp] theorem space_zero_val (n : ℕ) : (0 : Q.Space).val n = 0 := rfl
@[simp] theorem space_add_val (x y : Q.Space) (n : ℕ) : (x + y).val n = x.val n + y.val n := rfl
@[simp] theorem space_neg_val (x : Q.Space) (n : ℕ) : (-x).val n = -x.val n := rfl
@[simp] theorem space_sub_val (x y : Q.Space) (n : ℕ) : (x - y).val n = x.val n - y.val n := rfl
@[simp] theorem space_smul_val (a : 𝕜) (x : Q.Space) (n : ℕ) : (a • x).val n = a • x.val n := rfl

def signedValues (x : Q.Space) : Set ℝ := range (fun c : Coefficients 𝕜 ↦ ‖finiteSum x.val c‖)

theorem signedValues_nonempty (x : Q.Space) : (Q.signedValues x).Nonempty := by
  refine ⟨0, ⟨∅, ⟨fun _ ↦ 0, by simp⟩⟩, ?_⟩
  simp [finiteSum]

theorem signedValues_bddAbove (x : Q.Space) : BddAbove (Q.signedValues x) := by
  obtain ⟨C, hC⟩ := summable_finiteSum_bounded (𝕜 := 𝕜) x.val x.property.2
  exact ⟨C, by rintro v ⟨c, rfl⟩; exact hC c⟩

/-- The norm is exactly the supremum printed in the unconditional sum
space definition, with no extra boundedness hypothesis on its members. -/
def unconditionalNorm (x : Q.Space) : ℝ := sSup (Q.signedValues x)

theorem finiteSum_le_norm (x : Q.Space) (c : Coefficients 𝕜) :
    ‖finiteSum x.val c‖ ≤ Q.unconditionalNorm x :=
  le_csSup (Q.signedValues_bddAbove x) ⟨c, rfl⟩

theorem coordinate_le_norm (x : Q.Space) (n : ℕ) : ‖x.val n‖ ≤ Q.unconditionalNorm x := by
  simpa [finiteSum] using
    Q.finiteSum_le_norm x (⟨{n}, ⟨fun _ ↦ 1, by simp⟩⟩ : Coefficients 𝕜)

theorem unconditionalNorm_add_le (x y : Q.Space) :
    Q.unconditionalNorm (x + y) ≤ Q.unconditionalNorm x + Q.unconditionalNorm y := by
  apply csSup_le (Q.signedValues_nonempty (x + y))
  rintro v ⟨c, rfl⟩
  change ‖∑ n ∈ c.1, c.2.val n • (x.val n + y.val n)‖ ≤ _
  simp_rw [smul_add, Finset.sum_add_distrib]
  exact (norm_add_le _ _).trans
    (add_le_add (Q.finiteSum_le_norm x c) (Q.finiteSum_le_norm y c))

theorem unconditionalNorm_neg (x : Q.Space) :
    Q.unconditionalNorm (-x) = Q.unconditionalNorm x := by
  have h : Q.signedValues (-x) = Q.signedValues x := by
    ext v
    simp [signedValues, finiteSum, smul_neg, Finset.sum_neg_distrib, norm_neg]
  exact congrArg sSup h

theorem unconditionalNorm_zero : Q.unconditionalNorm 0 = 0 := by
  apply le_antisymm
  · apply csSup_le (Q.signedValues_nonempty 0)
    rintro v ⟨c, rfl⟩
    simp [finiteSum]
  · simpa using Q.coordinate_le_norm 0 0

theorem eq_zero_of_unconditionalNorm_eq_zero (x : Q.Space)
    (hx : Q.unconditionalNorm x = 0) : x = 0 := by
  ext n
  apply norm_eq_zero.mp
  exact le_antisymm (hx ▸ Q.coordinate_le_norm x n) (norm_nonneg _)

def spaceNorm : AddGroupNorm Q.Space where
  toFun := Q.unconditionalNorm
  map_zero' := Q.unconditionalNorm_zero
  add_le' := Q.unconditionalNorm_add_le
  neg' := Q.unconditionalNorm_neg
  eq_zero_of_map_eq_zero' := Q.eq_zero_of_unconditionalNorm_eq_zero

instance spaceNormedAddCommGroup : NormedAddCommGroup Q.Space :=
  Q.spaceNorm.toNormedAddCommGroup

@[simp] theorem space_norm_eq (x : Q.Space) : ‖x‖ = Q.unconditionalNorm x := rfl

instance spaceNormedSpace : NormedSpace 𝕜 Q.Space where
  norm_smul_le a x := by
    change Q.unconditionalNorm (a • x) ≤ ‖a‖ * Q.unconditionalNorm x
    apply csSup_le (Q.signedValues_nonempty (a • x))
    rintro v ⟨c, rfl⟩
    change ‖∑ n ∈ c.1, c.2.val n • (a • x.val n)‖ ≤ _
    have he : (∑ n ∈ c.1, c.2.val n • (a • x.val n)) =
        a • (∑ n ∈ c.1, c.2.val n • x.val n) := by
      simp only [Finset.smul_sum, smul_smul]
      congr 1
      ext n
      rw [mul_comm]
    rw [he, norm_smul]
    exact mul_le_mul_of_nonneg_left (Q.finiteSum_le_norm x c) (norm_nonneg a)

theorem coordinate_dist_le (x y : Q.Space) (n : ℕ) :
    dist (x.val n) (y.val n) ≤ dist x y := by
  simpa only [dist_eq_norm, space_sub_val, space_norm_eq] using Q.coordinate_le_norm (x - y) n

/-- A Cauchy sequence in the signed-sum norm is Cauchy in every coordinate. -/
theorem coordinate_cauchy (u : ℕ → Q.Space) (hu : CauchySeq u) (n : ℕ) :
    CauchySeq (fun k ↦ (u k).val n) := by
  apply Metric.cauchySeq_iff.mpr
  intro ε hε
  obtain ⟨N, hN⟩ := Metric.cauchySeq_iff.mp hu ε hε
  exact ⟨N, fun i hi j hj ↦ (Q.coordinate_dist_le (u i) (u j) n).trans_lt (hN i hi j hj)⟩

/-- Every finite multiplier estimate passes to a coordinatewise limit.
The same Cauchy index works for all finite subsets and coefficients. -/
theorem finiteSum_limit_bound (u : ℕ → Q.Space) (y : ℕ → X)
    (hy : ∀ n, Tendsto (fun k ↦ (u k).val n) atTop (𝓝 (y n)))
    (N m : ℕ) (ε : ℝ) (hN : ∀ k ≥ N, ‖u k - u m‖ < ε)
    (c : Coefficients 𝕜) :
    ‖finiteSum (fun n ↦ y n - (u m).val n) c‖ ≤ ε := by
  have hlim : Tendsto (fun k ↦ finiteSum (u k - u m).val c) atTop
      (𝓝 (finiteSum (fun n ↦ y n - (u m).val n) c)) := by
    apply tendsto_finsetSum
    intro n _
    exact ((hy n).sub tendsto_const_nhds).const_smul (c.2.val n)
  apply le_of_tendsto hlim.norm
  filter_upwards [eventually_ge_atTop N] with k hk
  exact (Q.finiteSum_le_norm (u k - u m) c).trans (hN k hk).le

/-- Coordinate limits of a signed-norm Cauchy sequence approximate all
finite multiplier sums uniformly. -/
theorem finiteSum_uniform_limit (u : ℕ → Q.Space) (hu : CauchySeq u) (y : ℕ → X)
    (hy : ∀ n, Tendsto (fun k ↦ (u k).val n) atTop (𝓝 (y n))) :
    ∀ ε > 0, ∃ N, ∀ m ≥ N, ∀ c : Coefficients 𝕜,
      ‖finiteSum (fun n ↦ y n - (u m).val n) c‖ ≤ ε := by
  intro ε hε
  obtain ⟨N, hN⟩ := Metric.cauchySeq_iff.mp hu ε hε
  refine ⟨N, fun m hm c ↦ Q.finiteSum_limit_bound u y hy N m ε ?_ c⟩
  intro k hk
  simpa only [dist_eq_norm] using hN k hk m hm

/-- The coordinate limit is still unconditionally summable. -/
theorem summable_coordinate_limit [CompleteSpace X]
    (u : ℕ → Q.Space) (hu : CauchySeq u) (y : ℕ → X)
    (hy : ∀ n, Tendsto (fun k ↦ (u k).val n) atTop (𝓝 (y n))) : Summable y := by
  apply summable_iff_vanishing_norm.mpr
  intro ε hε
  obtain ⟨N, hN⟩ := Q.finiteSum_uniform_limit u hu y hy (ε / 2) (half_pos hε)
  obtain ⟨F, hF⟩ := summable_iff_vanishing_norm.mp (u N).property.2
    (ε / 2) (half_pos hε)
  refine ⟨F, fun G hG ↦ ?_⟩
  have hdiff : ‖∑ n ∈ G, (y n - (u N).val n)‖ ≤ ε / 2 := by
    simpa [finiteSum] using hN N le_rfl (⟨G, ⟨fun _ ↦ 1, by simp⟩⟩ : Coefficients 𝕜)
  have he : (∑ n ∈ G, y n) =
      (∑ n ∈ G, (y n - (u N).val n)) + (∑ n ∈ G, (u N).val n) := by
    rw [Finset.sum_sub_distrib]
    exact (sub_add_cancel _ _).symm
  rw [he]
  exact (norm_add_le _ _).trans_lt
    ((add_lt_add_of_le_of_lt hdiff (hF G hG)).trans_eq (add_halves ε))

/-- The literal unconditional sum space of arbitrary closed subspaces of
a real or complex Banach space is complete. -/
instance spaceCompleteSpace [CompleteSpace X] : CompleteSpace Q.Space := by
  apply Metric.complete_of_cauchySeq_tendsto
  intro u hu
  have hcoord : ∀ n, ∃ y : X, Tendsto (fun k ↦ (u k).val n) atTop (𝓝 y) :=
    fun n ↦ cauchySeq_tendsto_of_complete (Q.coordinate_cauchy u hu n)
  choose y hy using hcoord
  have hmem : ∀ n, y n ∈ Q.packet n := by
    intro n
    exact (Q.closed n).mem_of_tendsto (hy n) (Eventually.of_forall fun k ↦ (u k).property.1 n)
  let z : Q.Space := ⟨y, hmem, Q.summable_coordinate_limit u hu y hy⟩
  refine ⟨z, Metric.tendsto_atTop.mpr ?_⟩
  intro ε hε
  obtain ⟨N, hN⟩ := Q.finiteSum_uniform_limit u hu y hy (ε / 2) (half_pos hε)
  refine ⟨N, fun m hm ↦ ?_⟩
  rw [dist_comm, dist_eq_norm, space_norm_eq]
  have hnorm : Q.unconditionalNorm (z - u m) ≤ ε / 2 := by
    apply csSup_le (Q.signedValues_nonempty (z - u m))
    rintro v ⟨c, rfl⟩
    exact hN m hm c
  exact hnorm.trans_lt (half_lt_self hε)

end ClosedPackets

end PaperIRelease.TopologyUnconditional
