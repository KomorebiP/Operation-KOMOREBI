module
public import KomorebiPhysics.LadderAdjoints
public import KomorebiPhysics.LadderRouting

/-! Exact nonzero ladder/routing examples, normalization and sign controls,
and genuine unboundedness on norm-one vectors. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace LadderExamples
open BoundedSpectral LadderDomains LadderRouting ResidueProjectors
open scoped BigOperators lp

theorem single_norm (n : ℕ) : ‖(single n 1 : Space)‖ = 1 := by
  exact (lp.norm_single (by norm_num : 0 < (2 : ENNReal)) n (1 : ℂ)).trans norm_one

theorem lower_basis_norm (n : ℕ) : ‖lower (single (n+1) 1)‖ = Real.sqrt (n+1 : ℕ) := by
  rw [lower_single_succ, lp.norm_single (by norm_num : 0 < (2 : ENNReal)), mul_one,
    Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (Real.sqrt_nonneg _)]

theorem raise_basis_norm (n : ℕ) : ‖raise (single n 1)‖ = Real.sqrt (n+1 : ℕ) := by
  rw [raise_single, lp.norm_single (by norm_num : 0 < (2 : ENNReal)), mul_one,
    Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (Real.sqrt_nonneg _)]

theorem lower_unbounded : ¬ ∃ C : ℝ, ∀ x : domain, ‖lower x‖ ≤ C * ‖(x : Space)‖ := by
  rintro ⟨C,h⟩
  obtain ⟨n,hn⟩ := exists_nat_gt (C^2)
  have hb := h (single (n+1) 1)
  rw [lower_basis_norm, single_norm, mul_one] at hb
  have hs := Real.sq_sqrt (Nat.cast_nonneg (α := ℝ) (n+1))
  push_cast at hs
  nlinarith [Real.sqrt_nonneg ((n+1 : ℕ) : ℝ)]

theorem raise_unbounded : ¬ ∃ C : ℝ, ∀ x : domain, ‖raise x‖ ≤ C * ‖(x : Space)‖ := by
  rintro ⟨C,h⟩
  obtain ⟨n,hn⟩ := exists_nat_gt (C^2)
  have hb := h (single n 1)
  rw [raise_basis_norm, single_norm, mul_one] at hb
  have hs := Real.sq_sqrt (Nat.cast_nonneg (α := ℝ) (n+1))
  push_cast at hs
  nlinarith [Real.sqrt_nonneg ((n+1 : ℕ) : ℝ)]

theorem no_bounded_lower_extension : ¬ ∃ A : Space →L[ℂ] Space,
    ∀ x : domain, lower x = A x := by
  rintro ⟨A,hA⟩
  apply lower_unbounded
  refine ⟨‖A‖, fun x => ?_⟩
  rw [hA]
  exact A.le_opNorm x

theorem no_bounded_raise_extension : ¬ ∃ A : Space →L[ℂ] Space,
    ∀ x : domain, raise x = A x := by
  rintro ⟨A,hA⟩
  apply raise_unbounded
  refine ⟨‖A‖, fun x => ?_⟩
  rw [hA]
  exact A.le_opNorm x

theorem packet_single_of_label (M : ℕ) [NeZero M] (r : ZMod M) (n : ℕ) (c : ℂ)
    (h : (n : ZMod M) = r) : packet M r (single n c) = single n c := by
  apply Subtype.ext
  change projector M r (lp.single 2 n c) = lp.single 2 n c
  rw [projector_single, ite_eq_left h]

theorem lower_nine : lower (single 9 1) = lp.single 2 8 (3 : ℂ) := by
  change lower (single (8+1) 1) = _
  rw [lower_single_succ]
  norm_num

theorem raise_eight : raise (single 8 1) = lp.single 2 9 (3 : ℂ) := by
  rw [raise_single]
  norm_num

/-- Modulo three, lowering lane zero wraps to lane two, not lane zero. -/
theorem lowering_wraparound :
    projector 3 2 (lower (packet 3 0 (single 9 1))) = lp.single 2 8 (3 : ℂ) := by
  rw [packet_single_of_label 3 0 9 1 (by decide), lower_nine, projector_single]
  have h : (8 : ZMod 3) = 2 := by decide
  simp only [h, ite_true]

theorem raising_wraparound :
    projector 3 0 (raise (packet 3 2 (single 8 1))) = lp.single 2 9 (3 : ℂ) := by
  rw [packet_single_of_label 3 2 8 1 (by decide), raise_eight, projector_single]
  have h : (9 : ZMod 3) = 0 := by decide
  simp only [h, ite_true]

theorem lowering_wrong_lane : projector 3 0 (lower (packet 3 0 (single 9 1))) = 0 :=
  lower_routing 3 0 0 (by decide) _

theorem raising_wrong_lane : projector 3 1 (raise (packet 3 2 (single 8 1))) = 0 :=
  raise_routing 3 1 2 (by decide) _

theorem wraparound_nonzero :
    projector 3 2 (lower (packet 3 0 (single 9 1))) ≠ 0 := by
  rw [lowering_wraparound]
  intro h
  have hn := congrArg (fun x : Space => x 8) h
  norm_num at hn

theorem vacuum_lowering : lower (single 0 1) = 0 := lower_single_zero 1

theorem vacuum_raising : raise (single 0 1) = lp.single 2 1 (1 : ℂ) := by
  rw [raise_single]
  norm_num

theorem wrong_square_root_amplitude : lower (single 9 1) ≠ lp.single 2 8 (9 : ℂ) := by
  rw [lower_nine]
  intro h
  have hn := congrArg (fun x : Space => x 8) h
  norm_num at hn

theorem lower_nine_norm_squared : ‖lower (single 9 1)‖ ^ 2 = 9 := by
  rw [lower_nine, lp.norm_single (by norm_num : 0 < (2 : ENNReal))]
  norm_num

theorem unnormalized_character_sum :
    ∑ k : ZMod 3, ZMod.stdAddChar (-((1 : ZMod 3)*k)) *
      ZMod.stdAddChar (k*(1 : ZMod 3)) = (3 : ℂ) := by
  have h := ResidueCharacters.selection 3 (1 : ZMod 3) 1
  simp only [ite_true] at h
  linear_combination 3 * h

end LadderExamples
end KomorebiPhysics
