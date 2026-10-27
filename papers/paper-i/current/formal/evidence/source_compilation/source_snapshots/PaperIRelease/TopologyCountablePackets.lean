import KomorebiVerification.TopologicalCompletion
import Mathlib.Analysis.Normed.Group.Seminorm

/-! # Unconditional countable packet coordinates

The carrier is the literal space of unconditionally summable packet
sequences. Its norm is the supremum over finite coefficient-weighted sums.
-/

noncomputable section
open scoped BigOperators
open Set Function Filter

namespace PaperIRelease.TopologyCountablePackets

variable {𝕜 X : Type*} [NontriviallyNormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X]

/-- Countably many mutually annihilating bounded projections with
unconditional reconstruction and an explicit uniform multiplier bound. -/
structure Projectors (𝕜 X : Type*) [NontriviallyNormedField 𝕜]
    [NormedAddCommGroup X] [NormedSpace 𝕜 X] where
  proj : ℕ → X →L[𝕜] X
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  annihilate : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, HasSum (fun i ↦ proj i x) x
  K : ℝ
  nonneg_K : 0 ≤ K
  bound : ∀ (F : Finset ℕ) (a : ℕ → 𝕜), (∀ n, ‖a n‖ ≤ 1) →
    ‖∑ n ∈ F, a n • proj n‖ ≤ K

namespace Projectors

/-- The operator norms whose supremum is the manuscript constant `K`. -/
def multiplierNorms (P : ℕ → X →L[𝕜] X) : Set ℝ :=
  {v | ∃ F : Finset ℕ, ∃ a : ℕ → 𝕜, (∀ n, ‖a n‖ ≤ 1) ∧
    v = ‖∑ n ∈ F, a n • P n‖}

/-- Construct the packet theorem's data using the exact supremum constant,
from the manuscript's boundedness hypothesis on finite multiplier sums. -/
def ofSupBound (P : ℕ → X →L[𝕜] X)
    (hid : ∀ i x, P i (P i x) = P i x)
    (hann : ∀ {i j}, i ≠ j → ∀ x, P i (P j x) = 0)
    (hsum : ∀ x, HasSum (fun i ↦ P i x) x)
    (hbound : BddAbove (multiplierNorms P)) : Projectors 𝕜 X where
  proj := P
  idempotent := hid
  annihilate := hann
  complete := hsum
  K := sSup (multiplierNorms P)
  nonneg_K := le_csSup hbound ⟨∅, fun _ ↦ 0, by simp, by simp⟩
  bound F a ha := le_csSup hbound ⟨F, a, ha, rfl⟩

variable (P : Projectors 𝕜 X)

/-- Exactly the sequences in the packet ranges whose series converges
unconditionally. `Summable` uses the net over all finite subsets. -/
def packetSequences : Submodule 𝕜 (ℕ → X) where
  carrier := {x | (∀ n, x n ∈ (P.proj n).range) ∧ Summable x}
  zero_mem' := ⟨fun _ ↦ Submodule.zero_mem _, summable_zero⟩
  add_mem' := by
    rintro x y ⟨hx, hxs⟩ ⟨hy, hys⟩
    exact ⟨fun n ↦ Submodule.add_mem _ (hx n) (hy n), hxs.add hys⟩
  smul_mem' := by
    rintro c x ⟨hx, hxs⟩
    exact ⟨fun n ↦ Submodule.smul_mem _ c (hx n), hxs.const_smul c⟩

/-- The packet carrier as a type with the signed-sum norm, rather than
the unrelated product topology on all sequences. -/
def PacketSpace : Type _ := P.packetSequences

instance packetAddCommGroup : AddCommGroup P.PacketSpace :=
  inferInstanceAs (AddCommGroup P.packetSequences)

instance packetModule : Module 𝕜 P.PacketSpace :=
  inferInstanceAs (Module 𝕜 P.packetSequences)

@[ext]
theorem PacketSpace.ext (x y : P.PacketSpace) (h : ∀ n, x.val n = y.val n) : x = y :=
  Subtype.ext (funext h)

@[simp]
theorem packet_neg_val (x : P.PacketSpace) (n : ℕ) : (-x).val n = -x.val n := rfl

/-- Analysis takes the actual projector coordinates. -/
def analysis : X →ₗ[𝕜] P.PacketSpace where
  toFun x := ⟨fun n ↦ P.proj n x, ⟨fun n ↦ ⟨x, rfl⟩, (P.complete x).summable⟩⟩
  map_add' _ _ := by ext n; exact map_add _ _ _
  map_smul' _ _ := by ext n; exact map_smul _ _ _

/-- Synthesis is the unconditional sum in the original ambient space. -/
def synthesis : P.PacketSpace →ₗ[𝕜] X where
  toFun x := ∑' n, x.val n
  map_add' x y := x.property.2.tsum_add y.property.2
  map_smul' c x := x.property.2.tsum_const_smul c

@[simp]
theorem synthesis_analysis (x : X) : P.synthesis (P.analysis x) = x :=
  (P.complete x).tsum_eq

@[simp]
theorem analysis_synthesis (x : P.PacketSpace) : P.analysis (P.synthesis x) = x := by
  ext n
  change P.proj n (∑' j, x.val j) = x.val n
  rw [(P.proj n).map_tsum x.property.2]
  rw [tsum_eq_single n]
  · obtain ⟨y, hy⟩ := x.property.1 n
    rw [← hy]
    exact P.idempotent n y
  · intro j hj
    obtain ⟨y, hy⟩ := x.property.1 j
    rw [← hy]
    exact P.annihilate hj.symm y

/-- Algebraic analysis and synthesis are inverse on the literal
unconditionally summable packet carrier. -/
def packetLinearEquiv : X ≃ₗ[𝕜] P.PacketSpace :=
  LinearEquiv.ofLinearMap P.analysis P.synthesis
    (LinearMap.ext P.analysis_synthesis) (LinearMap.ext P.synthesis_analysis)

/-- All finite coefficient-weighted sum norms from the printed definition. -/
def signedValues (x : P.PacketSpace) : Set ℝ :=
  {v | ∃ F : Finset ℕ, ∃ a : ℕ → 𝕜, (∀ n, ‖a n‖ ≤ 1) ∧
    v = ‖∑ n ∈ F, a n • x.val n‖}

theorem signedValues_nonempty (x : P.PacketSpace) : (P.signedValues x).Nonempty :=
  ⟨0, ∅, fun _ ↦ 0, by simp, by simp⟩

theorem signed_sum_le (x : P.PacketSpace) (F : Finset ℕ) (a : ℕ → 𝕜)
    (ha : ∀ n, ‖a n‖ ≤ 1) :
    ‖∑ n ∈ F, a n • x.val n‖ ≤ P.K * ‖P.synthesis x‖ := by
  have hx : ∀ n, P.proj n (P.synthesis x) = x.val n := by
    intro n
    exact congrArg (fun z : P.PacketSpace ↦ z.val n) (P.analysis_synthesis x)
  calc
    ‖∑ n ∈ F, a n • x.val n‖ = ‖(∑ n ∈ F, a n • P.proj n) (P.synthesis x)‖ := by
      simp only [sum_apply, smul_apply, hx]
    _ ≤ ‖∑ n ∈ F, a n • P.proj n‖ * ‖P.synthesis x‖ :=
      ContinuousLinearMap.le_opNorm _ _
    _ ≤ P.K * ‖P.synthesis x‖ := mul_le_mul_of_nonneg_right (P.bound F a ha) (norm_nonneg _)

theorem signedValues_bddAbove (x : P.PacketSpace) : BddAbove (P.signedValues x) := by
  refine ⟨P.K * ‖P.synthesis x‖, ?_⟩
  rintro v ⟨F, a, ha, rfl⟩
  exact P.signed_sum_le x F a ha

/-- The literal unconditional signed-sum norm. -/
def unconditionalNorm (x : P.PacketSpace) : ℝ := sSup (P.signedValues x)

theorem signed_sum_le_norm (x : P.PacketSpace) (F : Finset ℕ) (a : ℕ → 𝕜)
    (ha : ∀ n, ‖a n‖ ≤ 1) :
    ‖∑ n ∈ F, a n • x.val n‖ ≤ P.unconditionalNorm x :=
  le_csSup (P.signedValues_bddAbove x) ⟨F, a, ha, rfl⟩

theorem norm_le_K_synthesis (x : P.PacketSpace) :
    P.unconditionalNorm x ≤ P.K * ‖P.synthesis x‖ := by
  apply csSup_le (P.signedValues_nonempty x)
  rintro v ⟨F, a, ha, rfl⟩
  exact P.signed_sum_le x F a ha

theorem synthesis_norm_le (x : P.PacketSpace) : ‖P.synthesis x‖ ≤ P.unconditionalNorm x := by
  apply le_of_tendsto x.property.2.hasSum.norm
  apply Eventually.of_forall
  intro F
  simpa using P.signed_sum_le_norm x F (fun _ ↦ 1) (by simp)

theorem unconditionalNorm_add_le (x y : P.PacketSpace) :
    P.unconditionalNorm (x + y) ≤ P.unconditionalNorm x + P.unconditionalNorm y := by
  apply csSup_le (P.signedValues_nonempty (x + y))
  rintro v ⟨F, a, ha, rfl⟩
  change ‖∑ n ∈ F, a n • (x.val n + y.val n)‖ ≤ _
  simp_rw [smul_add, Finset.sum_add_distrib]
  exact (norm_add_le _ _).trans
    (add_le_add (P.signed_sum_le_norm x F a ha) (P.signed_sum_le_norm y F a ha))

theorem unconditionalNorm_neg (x : P.PacketSpace) :
    P.unconditionalNorm (-x) = P.unconditionalNorm x := by
  have h : P.signedValues (-x) = P.signedValues x := by
    ext v
    simp [signedValues, smul_neg,
      Finset.sum_neg_distrib, norm_neg]
  exact congrArg sSup h

theorem unconditionalNorm_zero : P.unconditionalNorm 0 = 0 := by
  apply le_antisymm
  · simpa using P.norm_le_K_synthesis 0
  · simpa using P.synthesis_norm_le 0

theorem eq_zero_of_unconditionalNorm_eq_zero (x : P.PacketSpace)
    (hx : P.unconditionalNorm x = 0) : x = 0 := by
  have hs : P.synthesis x = 0 := by
    apply norm_eq_zero.mp
    exact le_antisymm (hx ▸ P.synthesis_norm_le x) (norm_nonneg _)
  rw [← P.analysis_synthesis x, hs, map_zero]

/-- The signed-sum supremum is a norm on the full packet sequence carrier. -/
def packetNorm : AddGroupNorm P.PacketSpace where
  toFun := P.unconditionalNorm
  map_zero' := P.unconditionalNorm_zero
  add_le' := P.unconditionalNorm_add_le
  neg' := P.unconditionalNorm_neg
  eq_zero_of_map_eq_zero' := P.eq_zero_of_unconditionalNorm_eq_zero

instance packetNormedAddCommGroup : NormedAddCommGroup P.PacketSpace :=
  P.packetNorm.toNormedAddCommGroup

@[simp]
theorem packet_norm_eq (x : P.PacketSpace) : ‖x‖ = P.unconditionalNorm x := rfl

instance packetNormedSpace : NormedSpace 𝕜 P.PacketSpace where
  norm_smul_le c x := by
    change P.unconditionalNorm (c • x) ≤ ‖c‖ * P.unconditionalNorm x
    apply csSup_le (P.signedValues_nonempty (c • x))
    rintro v ⟨F, a, ha, rfl⟩
    change ‖∑ n ∈ F, a n • (c • x.val n)‖ ≤ _
    have he : (∑ n ∈ F, a n • (c • x.val n)) =
        c • (∑ n ∈ F, a n • x.val n) := by
      simp only [Finset.smul_sum, smul_smul]
      congr 1
      ext n
      rw [mul_comm]
    rw [he, norm_smul]
    exact mul_le_mul_of_nonneg_left (P.signed_sum_le_norm x F a ha) (norm_nonneg c)

/-- Analysis and synthesis are inverse bounded linear maps for the exact
unconditional signed-sum norm. -/
def packetEquiv : X ≃L[𝕜] P.PacketSpace :=
  P.packetLinearEquiv.toContinuousLinearEquivOfBounds P.K 1
    (fun x ↦ by simpa [packetLinearEquiv] using P.norm_le_K_synthesis (P.analysis x))
    (fun x ↦ by simpa [packetLinearEquiv] using P.synthesis_norm_le x)

@[simp]
theorem packetEquiv_apply (x : X) : P.packetEquiv x = P.analysis x := rfl

@[simp]
theorem packetEquiv_symm_apply (x : P.PacketSpace) : P.packetEquiv.symm x = P.synthesis x := rfl

/-- Completeness of the countable packet space follows from its constructed
uniform equivalence with the Banach ambient space. -/
instance packetCompleteSpace [CompleteSpace X] : CompleteSpace P.PacketSpace :=
  (P.packetEquiv.isUniformEmbedding.isUniformInducing.completeSpace_congr
    P.packetEquiv.surjective).mp inferInstance

/-- Quantitative analysis bound from the stated uniform multiplier bound. -/
theorem analysis_opNorm_le : ‖P.packetEquiv.toContinuousLinearMap‖ ≤ P.K := by
  apply ContinuousLinearMap.opNorm_le_bound _ P.nonneg_K
  intro x
  change P.unconditionalNorm (P.analysis x) ≤ P.K * ‖x‖
  simpa using P.norm_le_K_synthesis (P.analysis x)

/-- Quantitative synthesis bound, with constant exactly one. -/
theorem synthesis_opNorm_le : ‖P.packetEquiv.symm.toContinuousLinearMap‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro x
  change ‖P.synthesis x‖ ≤ 1 * P.unconditionalNorm x
  simpa using P.synthesis_norm_le x

end Projectors

end PaperIRelease.TopologyCountablePackets
