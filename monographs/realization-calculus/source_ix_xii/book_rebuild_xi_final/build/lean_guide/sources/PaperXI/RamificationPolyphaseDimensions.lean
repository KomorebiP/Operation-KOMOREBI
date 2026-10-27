import PaperXI.RamificationPolyphase
import PaperXI.RamificationSeparation
import Mathlib.Tactic

/-! # Dimension and conductor accounting for ramification details

The literal depth projectors split every successive fixed space into its previous
coarse part and one newly visible detail range.  In finite dimension, the detail
ranks telescope to the whole representation and give a finite tail formula for
every lower-numbering codimension.
-/
set_option autoImplicit false
noncomputable section
open scoped Classical BigOperators

namespace PaperXI.RamificationPolyphaseDimensions

open PaperXI.ResidueWeil
open PaperXI.ValuationRamification
open PaperXI.ValuationConductor
open PaperXI.RamificationPolyphase
open PaperXI.FiniteAverage

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [Fintype D]
  [MulSemiringAction D R]
variable (F : RingAut (IsLocalRing.ResidueField R))
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ (Pullback (residue R D) F) V)

/-- The actual subspace carried by the detail projector at depth `i`. -/
def detailSpace (i : ℕ) : Submodule ℂ V :=
  LinearMap.range
    (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i)

omit [Fintype D] in
/-- Fixed spaces increase as the lower ramification subgroup decreases. -/
theorem fixed_mono {i j : ℕ} (hij : i ≤ j) :
    fixed R D F ρ i ≤ fixed R D F ρ j := by
  intro v hv g
  have h := hv (lowerInclusion (R := R) (D := D) hij g)
  change ρ (lift R D F i (lowerInclusion (R := R) (D := D) hij g)) v = v at h
  change ρ (lift R D F j g) v = v
  simpa only [lift_lowerInclusion] using h

/-- The next fixed space is the sum of the preceding fixed space and the new
detail channel. -/
theorem fixed_succ_eq_sup_detail (i : ℕ) :
    fixed R D F ρ (i+1) = fixed R D F ρ i ⊔ detailSpace R D F ρ i := by
  apply le_antisymm
  · intro v hv
    have hcoarse : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v ∈
        fixed R D F ρ i :=
      invariant _ v
    have hdetail : detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i v ∈
        detailSpace R D F ρ i :=
      ⟨v, rfl⟩
    have hnext : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v = v :=
      fixes _ hv
    have hdecomp : v =
        depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v +
          detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
      rw [detailProjector_apply, hnext]
      abel
    rw [hdecomp]
    exact Submodule.add_mem _
      ((le_sup_left : fixed R D F ρ i ≤ fixed R D F ρ i ⊔ detailSpace R D F ρ i)
        hcoarse)
      ((le_sup_right : detailSpace R D F ρ i ≤ fixed R D F ρ i ⊔ detailSpace R D F ρ i)
        hdetail)
  · apply sup_le
    · exact fixed_mono R D F ρ (Nat.le_succ i)
    · rw [detailSpace, detailProjector_range]
      exact inf_le_left

/-- The previous fixed space and the new detail channel intersect trivially. -/
theorem fixed_disjoint_detail (i : ℕ) :
    Disjoint (fixed R D F ρ i) (detailSpace R D F ρ i) := by
  rw [disjoint_iff_inf_le]
  intro v hv
  have hvfix : v ∈ fixed R D F ρ i := hv.1
  have hvdetail : v ∈ detailSpace R D F ρ i := hv.2
  have hfix : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v = v :=
    fixes _ hvfix
  have hker : v ∈ LinearMap.ker
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i) := by
    rw [detailSpace, detailProjector_range] at hvdetail
    exact hvdetail.2
  have hzero := LinearMap.mem_ker.mp hker
  have hvzero : v = 0 := hfix.symm.trans hzero
  rw [hvzero]
  exact Submodule.zero_mem _

variable [FiniteDimensional ℂ V]

/-- Successive fixed-space dimensions differ by the rank of the corresponding
detail channel. -/
theorem finrank_fixed_succ (i : ℕ) :
    Module.finrank ℂ (fixed R D F ρ (i+1)) =
      Module.finrank ℂ (fixed R D F ρ i) +
        Module.finrank ℂ (detailSpace R D F ρ i) := by
  have h := Submodule.finrank_sup_add_finrank_inf_eq
    (fixed R D F ρ i) (detailSpace R D F ρ i)
  rw [← fixed_succ_eq_sup_detail R D F ρ i,
    (fixed_disjoint_detail R D F ρ i).eq_bot] at h
  simpa using h

/-- Prefix form of the ramification multiresolution dimension identity. -/
theorem finrank_fixed_eq_base_add_details (n : ℕ) :
    Module.finrank ℂ (fixed R D F ρ n) =
      Module.finrank ℂ (fixed R D F ρ 0) +
        ∑ i ∈ Finset.range n, Module.finrank ℂ (detailSpace R D F ρ i) := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [finrank_fixed_succ R D F ρ n, ih, Finset.sum_range_succ, add_assoc]

/-- Once the lower filtration is trivial, the inertia-fixed rank plus all detail
ranks equals the full representation dimension. -/
theorem finrank_eq_inertia_add_details {N : ℕ} (hN : lower R D N = ⊥) :
    Module.finrank ℂ V =
      Module.finrank ℂ (fixed R D F ρ 0) +
        ∑ i ∈ Finset.range N, Module.finrank ℂ (detailSpace R D F ρ i) := by
  have h := finrank_fixed_eq_base_add_details R D F ρ N
  rw [fixed_top_of_lower_bot R D F ρ N hN] at h
  simpa using h


section Termination

variable [IsNoetherianRing R] [FaithfulSMul D R]

omit [FiniteDimensional ℂ V] in
/-- For a finite faithful action on a Noetherian local ring, the finite
polyphase reconstruction exists without supplying a cutoff. -/
theorem exists_identity_eq_inertia_add_details :
    ∃ N : ℕ, (1 : Module.End ℂ V) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) 0 +
        ∑ i ∈ Finset.range N,
          detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  obtain ⟨N, hN⟩ := PaperXI.RamificationSeparation.eventually_trivial R D
  exact ⟨N, identity_eq_inertia_add_details (R := R) (D := D)
    (F := F) (ρ := ρ) (hN N le_rfl)⟩

/-- The corresponding finite-dimensional rank decomposition also exists under
the same derived termination hypotheses. -/
theorem exists_finrank_eq_inertia_add_details :
    ∃ N : ℕ, Module.finrank ℂ V =
      Module.finrank ℂ (fixed R D F ρ 0) +
        ∑ i ∈ Finset.range N, Module.finrank ℂ (detailSpace R D F ρ i) := by
  obtain ⟨N, hN⟩ := PaperXI.RamificationSeparation.eventually_trivial R D
  exact ⟨N, finrank_eq_inertia_add_details R D F ρ (hN N le_rfl)⟩

end Termination

/-- Each lower fixed-space codimension is the sum of the unresolved detail
ranks at that depth and above, up to any valid triviality cutoff. -/
theorem codimension_eq_detail_tail {i N : ℕ} (hiN : i ≤ N)
    (hN : lower R D N = ⊥) :
    codimension R D F ρ i =
      ∑ j ∈ Finset.Ico i N, Module.finrank ℂ (detailSpace R D F ρ j) := by
  have hNdim := finrank_eq_inertia_add_details R D F ρ hN
  have hidim := finrank_fixed_eq_base_add_details R D F ρ i
  have hsplit := Finset.sum_range_add_sum_Ico
    (fun j => Module.finrank ℂ (detailSpace R D F ρ j)) hiN
  unfold codimension
  omega

/-- The conventional lower-numbering summand is exactly its ramification-group
weight times the unresolved polyphase tail. -/
theorem summand_eq_weight_mul_detail_tail {i N : ℕ} (hiN : i ≤ N)
    (hN : lower R D N = ⊥) :
    summand R D F ρ i =
      (Nat.card (lower R D i) : ℝ) / (Nat.card (lower R D 0) : ℝ) *
        (∑ j ∈ Finset.Ico i N,
          (Module.finrank ℂ (detailSpace R D F ρ j) : ℝ)) := by
  unfold summand
  rw [codimension_eq_detail_tail R D F ρ hiN hN]
  norm_cast

end PaperXI.RamificationPolyphaseDimensions
