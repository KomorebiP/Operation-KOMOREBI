import KomorebiLSM.PositiveLift
import Mathlib.Topology.Algebra.Module.FiniteDimension
import Mathlib.Topology.Order.Compact
import Mathlib.Topology.Maps.Proper.Basic

/-! Closedness is derived for normalized finite generators, including redundant
ones. Compactifying coefficient witnesses avoids assuming a closed linear image. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveLift
open scoped BigOperators
open FiniteBayes FiniteInstruments
variable {E J : Type*} [AddCommGroup E] [Module ℝ E] [Fintype J]
variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [T2Space E] [FiniteDimensional ℝ E]

/-- Nonnegative prior coordinates lie in the finite unit box. -/
theorem prior_box {a : J → ℝ} (ha : IsPrior a) : ∀ j, a j ∈ Set.Icc (0 : ℝ) 1 := by
  intro j
  refine ⟨ha.1 j, ?_⟩
  rw [← ha.2]
  exact Finset.single_le_sum (fun i _ => ha.1 i) (Finset.mem_univ j)

omit [T2Space E] [FiniteDimensional ℝ E] in
/-- The actual finite probability simplex is compact. -/
theorem priors_compact : IsCompact {a : J → ℝ | IsPrior a} := by
  have he : {a : J → ℝ | IsPrior a} =
      {a | ∀ j, a j ∈ Set.Icc (0 : ℝ) 1} ∩ {a | ∑ j, a j = 1} := by
    ext a
    constructor
    · intro ha; exact ⟨prior_box ha,ha.2⟩
    · rintro ⟨ha,hs⟩; exact ⟨fun j => (ha j).1,hs⟩
  rw [he]
  exact (isCompact_pi_infinite (fun _ => isCompact_Icc)).inter_right
    (isClosed_eq (by fun_prop) continuous_const)

theorem normalizedHull_compact (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) : IsCompact (normalizedHull V l) := by
  rw [normalizedHull_eq_prior_image V l hn]
  exact priors_compact.image V.continuous_of_finiteDimensional

theorem normalizedHull_convex (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    Convex ℝ (normalizedHull V l) := by
  intro x hx y hy a b ha hb hab
  refine ⟨hull_convex V hx.1 hy.1 ha hb hab, ?_⟩
  simpa only [map_add,map_smul,smul_eq_mul,hx.2,hy.2,mul_one] using hab

/-- Normalized generators keep coefficient witnesses in a compact unit box. -/
theorem hull_closed (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) : IsClosed (hull V) := by
  let K : Set (J → ℝ) := {a | ∀ j, a j ∈ Set.Icc (0 : ℝ) 1}
  have hk : IsCompact K := isCompact_pi_infinite (fun _ => isCompact_Icc)
  letI : CompactSpace K := isCompact_iff_compactSpace.mp hk
  let F : Set (E × K) := {z | (1 + l z.1) • V z.2.val = z.1}
  have hf : IsClosed F := isClosed_eq
    ((continuous_const.add (l.continuous_of_finiteDimensional.comp continuous_fst)).smul
      (V.continuous_of_finiteDimensional.comp (continuous_subtype_val.comp continuous_snd)))
    continuous_fst
  have he : hull V = {x | 0 ≤ l x} ∩ (Prod.fst '' F) := by
    ext x
    constructor
    · intro hx
      have hm : 0 ≤ l x := hull_mass_nonneg V l hn hx
      obtain ⟨a,ha,haV⟩ := hx
      have hpos : 0 < 1 + l x := by linarith
      let b : J → ℝ := (1 + l x)⁻¹ • a
      have hb : b ∈ K := by
        intro j
        change 0 ≤ (1 + l x)⁻¹ * a j ∧ (1 + l x)⁻¹ * a j ≤ 1
        refine ⟨mul_nonneg (inv_nonneg.mpr hpos.le) (ha j), ?_⟩
        rw [mul_comm,← div_eq_mul_inv]
        apply (div_le_one hpos).mpr
        have hle : a j ≤ ∑ i, a i :=
          Finset.single_le_sum (fun i _ => ha i) (Finset.mem_univ j)
        have hsum : ∑ i, a i = l x := (normalized_mass V l hn a).symm.trans (congrArg l haV)
        rw [hsum] at hle
        linarith
      refine ⟨hm,⟨(x,⟨b,hb⟩),?_,rfl⟩⟩
      change (1+l x) • V ((1+l x)⁻¹ • a) = x
      rw [map_smul,smul_smul,mul_inv_cancel₀ (ne_of_gt hpos),one_smul,haV]
    · rintro ⟨hx,⟨⟨y,b⟩,hF,hxy⟩⟩
      change y = x at hxy
      subst y
      refine ⟨(1+l x) • b.val,fun j => mul_nonneg (by linarith) (b.property j).1, ?_⟩
      rw [map_smul]
      exact hF
  rw [he]
  exact (isClosed_le continuous_const l.continuous_of_finiteDimensional).inter
    (isClosedMap_fst_of_compactSpace F hf)

end Komorebi.LSM.PositiveLift
