import PaperX.NormSignArithmetic
import PaperX.NormSignResidueCounting

/-! Arithmetic sign on positive dilations of the actual sign regions. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormSignArithmetic
open Set NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NormSignGeometry
open scoped Classical Pointwise
variable (K : Type*) [Field K] [NumberField K]

theorem realProduct_smul (t : ℝ) (x : mixedSpace K) :
    realProduct K (t • x) =
      t ^ Fintype.card {w : InfinitePlace K // IsReal w} * realProduct K x := by
  simp only [realProduct, Prod.smul_fst, Pi.smul_apply, smul_eq_mul,
    Finset.prod_mul_distrib, Finset.prod_const, Finset.card_univ]

theorem realProduct_pos_of_mem_smul_signCone {t : ℝ} (ht : 0 < t)
    {x : mixedSpace K} (hx : x ∈ t • signCone K true) : 0 < realProduct K x := by
  rcases hx with ⟨y, hy, rfl⟩
  rw [realProduct_smul]
  exact mul_pos (pow_pos ht _) hy.2

theorem realProduct_neg_of_mem_smul_signCone {t : ℝ} (ht : 0 < t)
    {x : mixedSpace K} (hx : x ∈ t • signCone K false) : realProduct K x < 0 := by
  rcases hx with ⟨y, hy, rfl⟩
  rw [realProduct_smul]
  exact mul_neg_of_pos_of_neg (pow_pos ht _) (neg_pos.mp hy.2)

theorem ne_zero_of_mem_smul_signCone {t : ℝ} (ht : 0 < t) {x : K}
    {positive : Bool} (hx : mixedEmbedding K x ∈ t • signCone K positive) : x ≠ 0 := by
  intro hzero
  rcases hx with ⟨y, hy, he⟩
  have he0 : t • y = 0 := by simpa only [hzero, map_zero] using he
  have hy0 : y = 0 := (smul_eq_zero.mp he0).resolve_left (ne_of_gt ht)
  subst y
  have hp := fundamentalCone.normAtPlace_pos_of_mem hy.1.1
    (Classical.arbitrary (InfinitePlace K))
  simp at hp

theorem toMixed_mem_smul_signCone {t : ℝ} {positive : Bool}
    {x : euclidean.mixedSpace K} (hx : x ∈ t • signRegion K positive) :
    euclidean.toMixed K x ∈ t • signCone K positive := by
  rcases hx with ⟨y, hy, he⟩
  refine ⟨euclidean.toMixed K y, hy, ?_⟩
  simpa only [map_smul] using congrArg (euclidean.toMixed K) he

theorem integer_norm_pos_of_mem_smul_signRegion {t : ℝ} (ht : 0 < t)
    {x : 𝓞 K}
    (hx : (euclidean.toMixed K).symm (mixedEmbedding K (x : K)) ∈
      t • signRegion K true) : 0 < Algebra.norm ℤ x := by
  have hm : mixedEmbedding K (x : K) ∈ t • signCone K true := by
    simpa only [ContinuousLinearEquiv.apply_symm_apply] using toMixed_mem_smul_signCone K hx
  have hne : x ≠ 0 := by
    intro hzero
    exact ne_zero_of_mem_smul_signCone K ht hm (congrArg (fun z : 𝓞 K => (z : K)) hzero)
  exact (integer_norm_pos_iff K hne).mpr (realProduct_pos_of_mem_smul_signCone K ht hm)

theorem integer_norm_neg_of_mem_smul_signRegion {t : ℝ} (ht : 0 < t)
    {x : 𝓞 K}
    (hx : (euclidean.toMixed K).symm (mixedEmbedding K (x : K)) ∈
      t • signRegion K false) : Algebra.norm ℤ x < 0 := by
  have hm : mixedEmbedding K (x : K) ∈ t • signCone K false := by
    simpa only [ContinuousLinearEquiv.apply_symm_apply] using toMixed_mem_smul_signCone K hx
  have hne : x ≠ 0 := by
    intro hzero
    exact ne_zero_of_mem_smul_signCone K ht hm (congrArg (fun z : 𝓞 K => (z : K)) hzero)
  exact (integer_norm_neg_iff K hne).mpr (realProduct_neg_of_mem_smul_signCone K ht hm)

end PaperX.NormSignArithmetic
