import PaperXI.ValuationConductor
import PaperXI.FiniteAverage

/-! # Ramification polyphase projectors

The lower ramification filtration gives a nested family of literal finite-group
averaging projectors.  Successive differences are the depth-detail channels.
This is a representation-theoretic multiresolution theorem; it does not assert
existence of an intrinsic wild-break decomposition beyond the supplied lower
filtration.
-/
set_option autoImplicit false
noncomputable section
open scoped Classical BigOperators

namespace PaperXI.RamificationPolyphase

open PaperXI.ResidueWeil
open PaperXI.ValuationRamification
open PaperXI.ValuationConductor
open PaperXI.FiniteAverage

section AverageRestriction

variable {G H V : Type*} [Group G] [Fintype G] [Group H] [Fintype H]
variable [AddCommGroup V] [Module ℂ V]

/-- Averaging after one group operator does not change the average. -/
theorem average_comp_operator (ρ : Representation ℂ G V) (g : G) :
    (average ρ).comp (ρ g) = average ρ := by
  ext v
  change average ρ (ρ g v) = average ρ v
  rw [average_apply, average_apply]
  congr 1
  simp only [← Module.End.mul_apply, ← map_mul]
  exact Function.Bijective.sum_comp (Group.mulRight_bijective g) (fun h => ρ h v)

/-- Averaging over the ambient group after averaging over any mapped finite
subgroup gives the ambient average. -/
theorem average_comp_restricted_average (ρ : Representation ℂ G V) (f : H →* G) :
    (average ρ).comp (average (ρ.comp f)) = average ρ := by
  ext v
  change average ρ (average (ρ.comp f) v) = average ρ v
  rw [average_apply (ρ.comp f), map_smul, map_sum]
  have hs : ∀ h : H, average ρ ((ρ.comp f) h v) = average ρ v := by
    intro h
    exact LinearMap.congr_fun (average_comp_operator ρ (f h)) v
  simp_rw [hs]
  rw [Finset.sum_const, Finset.card_univ, ← Nat.cast_smul_eq_nsmul ℂ, smul_smul,
    inv_mul_cancel₀ (card_ne_zero (G := H)), one_smul]

/-- Averaging over a mapped finite subgroup fixes the ambient average. -/
theorem restricted_average_comp_average (ρ : Representation ℂ G V) (f : H →* G) :
    (average (ρ.comp f)).comp (average ρ) = average ρ := by
  ext v
  change average (ρ.comp f) (average ρ v) = average ρ v
  exact fixes (ρ.comp f) (fun h => invariant ρ v (f h))

end AverageRestriction

section LowerFiltration

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [Fintype D] [MulSemiringAction D R]
variable (F : RingAut (IsLocalRing.ResidueField R))
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ (Pullback (residue R D) F) V)

/-- Inclusion from a deeper lower group into a shallower lower group. -/
def lowerInclusion {i j : ℕ} (hij : i ≤ j) : lower R D j →* lower R D i where
  toFun g := ⟨g.val, antitone R D hij g.property⟩
  map_one' := rfl
  map_mul' _ _ := rfl

omit [Fintype D] in
@[simp] theorem lowerInclusion_val {i j : ℕ} (hij : i ≤ j)
    (g : lower R D j) : (lowerInclusion (R := R) (D := D) hij g : D) = g := rfl

omit [Fintype D] in
/-- Lower-group lifts commute with the canonical filtration inclusion. -/
theorem lift_lowerInclusion {i j : ℕ} (hij : i ≤ j) (g : lower R D j) :
    lift R D F i (lowerInclusion (R := R) (D := D) hij g) = lift R D F j g := rfl

/-- The literal averaging projector onto vectors fixed at depth `i`. -/
def depthProjector (i : ℕ) : Module.End ℂ V :=
  average (ρ.comp (lift R D F i))

/-- The range is the actual lower fixed space used by the conductor theory. -/
theorem depthProjector_range (i : ℕ) :
    LinearMap.range (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i) = fixed R D F ρ i :=
  range_eq _

/-- Every depth projector is idempotent. -/
theorem depthProjector_idempotent (i : ℕ) :
    (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i).comp (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i :=
  idempotent _

/-- A shallower projector composed after a deeper projector is the shallower
projector. -/
theorem depthProjector_comp_of_le {i j : ℕ} (hij : i ≤ j) :
    (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i).comp (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  let f := lowerInclusion (R := R) (D := D) hij
  have hrep : (ρ.comp (lift R D F i)).comp f = ρ.comp (lift R D F j) := by
    ext g v
    rfl
  change (average (ρ.comp (lift R D F i))).comp
      (average (ρ.comp (lift R D F j))) = average (ρ.comp (lift R D F i))
  rw [← hrep]
  exact average_comp_restricted_average (ρ.comp (lift R D F i)) f

/-- A deeper projector composed after a shallower projector is also the
shallower projector. -/
theorem depthProjector_comp_of_le_rev {i j : ℕ} (hij : i ≤ j) :
    (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j).comp (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  let f := lowerInclusion (R := R) (D := D) hij
  have hrep : (ρ.comp (lift R D F i)).comp f = ρ.comp (lift R D F j) := by
    ext g v
    rfl
  change (average (ρ.comp (lift R D F j))).comp
      (average (ρ.comp (lift R D F i))) = average (ρ.comp (lift R D F i))
  rw [← hrep]
  exact restricted_average_comp_average (ρ.comp (lift R D F i)) f

/-- The detail channel revealed between depths `i` and `i+1`. -/
def detailProjector (i : ℕ) : Module.End ℂ V :=
  depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i + 1) - depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i

@[simp] theorem detailProjector_apply (i : ℕ) (v : V) :
    detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i v =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v - depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := rfl

/-- Every ramification detail channel is itself an idempotent projector. -/
theorem detailProjector_idempotent (i : ℕ) :
    (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i).comp
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) =
      detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  ext v
  simp only [detailProjector_apply, LinearMap.comp_apply, map_sub]
  have hQQ : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_idempotent (R := R) (D := D) (F := F) (ρ := ρ) (i+1)) v
  have hPQ : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_succ i)) v
  have hQP : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_succ i)) v
  have hPP : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_idempotent (R := R) (D := D) (F := F) (ρ := ρ) i) v
  rw [hQQ, hPQ, hQP, hPP]
  abel

/-- A detail vector is killed by the preceding coarse projector. -/
theorem depthProjector_detailProjector (i : ℕ) :
    (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i).comp
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) = 0 := by
  ext v
  simp only [detailProjector_apply, LinearMap.comp_apply, map_sub, LinearMap.zero_apply]
  have hPQ : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_succ i)) v
  have hPP : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_idempotent (R := R) (D := D) (F := F) (ρ := ρ) i) v
  rw [hPQ, hPP, sub_self]

/-- The next projector fixes its corresponding detail channel. -/
theorem depthProjector_succ_detailProjector (i : ℕ) :
    (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)).comp
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) =
      detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  ext v
  simp only [detailProjector_apply, LinearMap.comp_apply, map_sub]
  have hQQ : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_idempotent (R := R) (D := D) (F := F) (ρ := ρ) (i+1)) v
  have hQP : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_succ i)) v
  rw [hQQ, hQP]

/-- A detail vector lies in the next fixed space. -/
theorem detailProjector_mem_next_fixed (i : ℕ) (v : V) :
    detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i v ∈ fixed R D F ρ (i+1) := by
  rw [← depthProjector_range]
  refine ⟨detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i v, ?_⟩
  simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
    (depthProjector_succ_detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) v

/-- The detail range is exactly the newly visible fixed space: fixed at depth
`i+1` and annihilated by the previous coarse projector. -/
theorem detailProjector_range (i : ℕ) :
    LinearMap.range (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) =
      fixed R D F ρ (i+1) ⊓ LinearMap.ker (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i) := by
  ext v
  constructor
  · rintro ⟨x, rfl⟩
    exact ⟨detailProjector_mem_next_fixed (R := R) (D := D) (F := F) (ρ := ρ) i x,
      LinearMap.mem_ker.mpr (LinearMap.congr_fun
        (depthProjector_detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) x)⟩
  · rintro ⟨hvnext, hvker⟩
    refine ⟨v, ?_⟩
    rw [detailProjector_apply]
    have hnext : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v = v :=
      fixes _ hvnext
    rw [hnext, LinearMap.mem_ker.mp hvker, sub_zero]

/-- Distinct detail channels compose to zero. -/
theorem detailProjector_comp_eq_zero {i j : ℕ} (hij : i < j) :
    (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i).comp
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) j) = 0 := by
  ext v
  have hi1j : i + 1 ≤ j := hij
  simp only [detailProjector_apply, LinearMap.comp_apply, map_sub, LinearMap.zero_apply]
  have h11 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (j+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.succ_le_succ (Nat.le_of_lt hij))) v
  have h01 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (j+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_trans (Nat.le_of_lt hij) (Nat.le_succ j))) v
  have h10 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ) hi1j) v
  have h00 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_of_lt hij)) v
  rw [h11, h01, h10, h00]
  abel

/-- Distinct detail channels compose to zero in the opposite order as well. -/
theorem detailProjector_comp_eq_zero_rev {i j : ℕ} (hij : i < j) :
    (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) j).comp
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) = 0 := by
  ext v
  have hi1j : i + 1 ≤ j := hij
  simp only [detailProjector_apply, LinearMap.comp_apply, map_sub, LinearMap.zero_apply]
  have h11 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (j+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.succ_le_succ (Nat.le_of_lt hij))) v
  have h10 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (i+1) v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ) hi1j) v
  have h01 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) (j+1)
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_trans (Nat.le_of_lt hij) (Nat.le_succ j))) v
  have h00 : depthProjector (R := R) (D := D) (F := F) (ρ := ρ) j
      (depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v) =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i v := by
    simpa only [LinearMap.comp_apply] using LinearMap.congr_fun
      (depthProjector_comp_of_le_rev (R := R) (D := D) (F := F) (ρ := ρ)
        (Nat.le_of_lt hij)) v
  rw [h11, h10, h01, h00]
  abel

/-- Finite telescoping reconstruction of a deeper fixed-space projector from
the inertia projector and the intervening detail channels. -/
theorem depthProjector_eq_zero_add_sum (n : ℕ) :
    depthProjector (R := R) (D := D) (F := F) (ρ := ρ) n = depthProjector (R := R) (D := D) (F := F) (ρ := ρ) 0 +
      ∑ i ∈ Finset.range n, detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ, ← add_assoc, ← ih]
      ext v
      simp [detailProjector]

/-- Once the lower filtration is trivial, the full identity decomposes into the
inertia-fixed channel plus finitely many depth details. -/
theorem identity_eq_inertia_add_details {N : ℕ} (hN : lower R D N = ⊥) :
    (1 : Module.End ℂ V) = depthProjector (R := R) (D := D) (F := F) (ρ := ρ) 0 +
      ∑ i ∈ Finset.range N, detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  rw [← depthProjector_eq_zero_add_sum (R := R) (D := D) (F := F) (ρ := ρ) N]
  ext v
  change v = depthProjector (R := R) (D := D) (F := F) (ρ := ρ) N v
  symm
  exact fixes _ (by
    intro g
    have hg : g = 1 := by simpa [hN] using g.property
    subst g
    simp)

end LowerFiltration

end PaperXI.RamificationPolyphase
