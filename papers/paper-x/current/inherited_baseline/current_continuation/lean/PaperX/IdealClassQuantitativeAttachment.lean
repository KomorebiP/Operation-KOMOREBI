import Mathlib.NumberTheory.NumberField.Ideal.Asymptotics

/-!
# Exact attachment of ordinary ideal-class counts to a cone lattice count

This file exposes actual ideal and lattice counting identities used by the
qualitative theorem in Mathlib. It does not assume or prove a quantitative
lattice estimate. The fixed representative is in the inverse ideal class.
-/

set_option backward.isDefEq.respectTransparency.types false
noncomputable section

open Ideal
open scoped nonZeroDivisors Real Pointwise Classical
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.euclidean NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units Submodule

namespace PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The actual number of nonzero integral ideals in a fixed ideal class. -/
def classCount (C : ClassGroup (𝓞 K)) (s : ℝ) : ℕ :=
  Nat.card {I : (Ideal (𝓞 K))⁰ //
    absNorm (I : Ideal (𝓞 K)) ≤ s ∧ ClassGroup.mk0 I = C}

/-- The ordinary fundamental cone truncated by the actual field norm. -/
def coneRegion (s : ℝ) : Set (euclidean.mixedSpace K) :=
  {x | toMixed K x ∈ fundamentalCone K ∧ mixedEmbedding.norm (toMixed K x) ≤ s}

/-- The Euclidean image of the lattice of an actual nonzero integral ideal. -/
abbrev idealEuclideanLattice (J : (Ideal (𝓞 K))⁰) : Submodule ℤ (euclidean.mixedSpace K) :=
  ZLattice.comap ℝ (E := mixedSpace K) (F := euclidean.mixedSpace K)
    (idealLattice K (FractionalIdeal.mk0 K J)) (toMixed K).toLinearMap

/-- The actual finite count in the truncated cone and the ideal lattice. -/
def latticeCount (J : (Ideal (𝓞 K))⁰) (s : ℝ) : ℕ :=
  Nat.card (coneRegion K s ∩ idealEuclideanLattice K J : Set (euclidean.mixedSpace K))

/-- Multiplication by an inverse-class ideal turns ideals in `C` into principal ideals. -/
theorem classCount_eq_principal_count {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹) (s : ℝ) :
    classCount K C s =
      Nat.card {I : (Ideal (𝓞 K))⁰ // (J : Ideal (𝓞 K)) ∣ I ∧
        IsPrincipal (I : Ideal (𝓞 K)) ∧
        absNorm (I : Ideal (𝓞 K)) ≤ s * absNorm (J : Ideal (𝓞 K))} := by
  unfold classCount
  simp_rw [← nonZeroDivisors_dvd_iff_dvd_coe]
  refine Nat.card_congr ?_
  refine ((Equiv.dvd J).subtypeEquiv fun I ↦ ?_).trans
    (Equiv.subtypeSubtypeEquivSubtypeInter (fun I : (Ideal (𝓞 K))⁰ ↦ J ∣ I) _)
  rw [← ClassGroup.mk0_eq_one_iff (SetLike.coe_mem _)]
  simp_rw [Equiv.dvd_apply, Submonoid.coe_mul, ← Submonoid.mul_def, _root_.map_mul, hJ,
    inv_mul_eq_one, Nat.cast_mul, mul_comm s, eq_comm, and_comm, and_congr_left_iff]
  exact fun _ ↦
    (mul_le_mul_iff_of_pos_left (Nat.cast_pos.mpr (absNorm_pos_of_nonZeroDivisors J))).symm

/-- The cone lattice points are precisely the bounded generators in the fundamental cone. -/
def coneLatticeEquiv (J : (Ideal (𝓞 K))⁰) (s : ℝ) :
    (coneRegion K s ∩ idealEuclideanLattice K J : Set (euclidean.mixedSpace K)) ≃
      {a : idealSet K J // mixedEmbedding.norm (a : mixedSpace K) ≤ s} := by
  classical
  unfold coneRegion idealEuclideanLattice
  rw [ZLattice.coe_comap]
  refine (((toMixed K).toEquiv.image _).trans (Equiv.subtypeEquivProp ?_)).trans
    (Equiv.subtypeSubtypeEquivSubtypeInter _ (mixedEmbedding.norm · ≤ s)).symm
  ext
  simp_rw [mem_idealSet, Set.mem_image, Set.mem_inter_iff, Set.mem_preimage, SetLike.mem_coe,
    mem_idealLattice, FractionalIdeal.coe_mk0]
  constructor
  · rintro ⟨_, ⟨⟨hx₁, hx₂⟩, _, ⟨x, hx₃, rfl⟩, h⟩, rfl⟩
    exact ⟨⟨hx₁, x, hx₃, h⟩, hx₂⟩
  · rintro ⟨⟨hx₁, ⟨x, hx₂, rfl⟩⟩, hx₃⟩
    exact ⟨(toMixed K).symm (mixedEmbedding K x),
      ⟨⟨hx₁, hx₃⟩, ⟨(x : K), by simp [hx₂], rfl⟩⟩, rfl⟩

/-- The torsion factor is exact, including at negative and zero thresholds. -/
theorem latticeCount_eq_classCount_mul_torsion {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹) (s : ℝ) :
    latticeCount K J (s * absNorm (J : Ideal (𝓞 K))) =
      classCount K C s * torsionOrder K := by
  unfold latticeCount
  rw [Nat.card_congr (coneLatticeEquiv K J _), ← card_isPrincipal_dvd_norm_le,
    classCount_eq_principal_count K hJ]

/-- The unit truncation is the actual norm-le-one cone used by Mathlib. -/
theorem coneRegion_one : coneRegion K 1 = toMixed K ⁻¹' normLeOne K := by
  ext x
  simp [coneRegion]

/-- Positive dilation of the unit cone raises the norm threshold by the degree. -/
theorem smul_coneRegion_one {t : ℝ} (ht : 0 < t) :
    t • coneRegion K 1 = coneRegion K (t ^ Module.finrank ℚ K) := by
  ext x
  simp_rw [Set.mem_smul_set_iff_inv_smul_mem₀ ht.ne', coneRegion, Set.mem_ofPred_eq,
    map_smul, mixedEmbedding.norm_smul, abs_of_nonneg (inv_pos.mpr ht).le,
    inv_pow, inv_mul_le_iff₀ (pow_pos ht _), mul_one, and_congr_left_iff]
  intro _
  exact smul_mem_iff_mem (inv_ne_zero ht.ne')

end PaperX.IdealClassQuantitative
