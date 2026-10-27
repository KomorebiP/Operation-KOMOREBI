import KomorebiSpace.AmplifiedViews
import KomorebiSpace.OverlapExamples

set_option autoImplicit false

/-!
# Nonisometric chains with exact exponential amplification

The graph has n edges. Each forward bond contracts by 1/2 and each reverse
bond expands by 2. The nonzero anchor 7 is protected. A candidate has directed
edge residual norm 1 but exact anchored repair error 2^n-1.
-/
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
namespace Examples

/-- A real scalar continuous linear equivalence, with inverse explicitly given. -/
def scale (a : ℝ) (ha : a ≠ 0) : ℝ ≃L[ℝ] ℝ :=
  (show ℝ ≃ₗ[ℝ] ℝ from
    { toFun := fun x => a*x
      invFun := fun x => a⁻¹*x
      left_inv := by intro x; change a⁻¹*(a*x)=x; rw [← mul_assoc, inv_mul_cancel₀ ha, one_mul]
      right_inv := by intro x; change a*(a⁻¹*x)=x; rw [← mul_assoc, mul_inv_cancel₀ ha, one_mul]
      map_add' := mul_add a
      map_smul' := by intro c x; change a*(c*x)=c*(a*x); ring }).toContinuousLinearEquiv

@[simp] theorem scale_apply (a : ℝ) (ha : a ≠ 0) (x : ℝ) : scale a ha x = a*x := rfl

@[simp] theorem scale_symm_apply (a : ℝ) (ha : a ≠ 0) (x : ℝ) :
    (scale a ha).symm x = a⁻¹*x := rfl

def chainFrames (n : ℕ) (i : Fin (n+1)) : ℝ ≃L[ℝ] ℝ :=
  scale ((2 : ℝ)^i.val) (pow_ne_zero _ (by norm_num))

def chainConnection (n : ℕ) : Connection (Fin (n+1)) ℝ :=
  Connection.ofFrames (chainFrames n)

@[simp] theorem chain_transport (n : ℕ) (i j : Fin (n+1)) (z : ℝ) :
    (chainConnection n).transport i j z =
      (2 : ℝ)^i.val * (((2 : ℝ)^j.val)⁻¹*z) := rfl

theorem chain_transport_forward (n : ℕ) (i j : Fin (n+1))
    (h : i.val+1=j.val) (z : ℝ) : (chainConnection n).transport i j z = z/2 := by
  rw [chain_transport, ← h, pow_succ]
  have hn : (2 : ℝ)^i.val ≠ 0 := pow_ne_zero _ (by norm_num)
  field_simp

theorem chain_transport_backward (n : ℕ) (i j : Fin (n+1))
    (h : i.val+1=j.val) (z : ℝ) : (chainConnection n).transport j i z = 2*z := by
  rw [chain_transport, ← h, pow_succ]
  have hn : (2 : ℝ)^i.val ≠ 0 := pow_ne_zero _ (by norm_num)
  field_simp

def chainRepair (n : ℕ) (x : Fin (n+1) → ℝ) (i : Fin (n+1)) : ℝ :=
  (2 : ℝ)^i.val * x 0

@[simp] theorem chainRepair_anchor (n : ℕ) (x : Fin (n+1) → ℝ) :
    chainRepair n x 0 = x 0 := by simp [chainRepair]

theorem chainRepair_parallel (n : ℕ) (x : Fin (n+1) → ℝ) :
    (chainConnection n).Parallel (OverlapTransport.Examples.chain n) (chainRepair n x) := by
  intro i j _
  rw [chain_transport]
  unfold chainRepair
  have hj : (2 : ℝ)^j.val ≠ 0 := pow_ne_zero _ (by norm_num)
  field_simp

/-- Equality with the general holonomy-based projector, not a second repair definition. -/
theorem chainRepair_is_constructed (n : ℕ) (x : Fin (n+1) → ℝ) :
    Rooted.orthogonalRepair (chainConnection n) (OverlapTransport.Examples.chainRouting n) x =
      chainRepair n x := by
  apply Rooted.parallel_unique (chainConnection n) (OverlapTransport.Examples.chainRouting n)
    (Rooted.orthogonalRepair_parallel _ _ x) (chainRepair_parallel n x)
  rw [Rooted.orthogonalRepair_anchor, chainRepair_anchor]
  apply Rooted.anchorProjection_fixes
  have he := Rooted.parallel_anchor_fixed (chainConnection n)
    (OverlapTransport.Examples.chainRouting n) (chainRepair n x) (chainRepair_parallel n x)
  simpa only [chainRepair_anchor] using he

def candidate (n : ℕ) (i : Fin (n+1)) : ℝ := 8*(2 : ℝ)^i.val-1

@[simp] theorem candidate_anchor (n : ℕ) : candidate n 0 = 7 := by norm_num [candidate]

theorem candidate_forward_defect (n : ℕ) (i j : Fin (n+1)) (h : i.val+1=j.val) :
    (chainConnection n).defect (candidate n) i j = 1/2 := by
  rw [Connection.defect, chain_transport_forward n i j h]
  simp only [candidate, ← h, pow_succ]
  ring

theorem candidate_backward_defect (n : ℕ) (i j : Fin (n+1)) (h : i.val+1=j.val) :
    (chainConnection n).defect (candidate n) j i = -1 := by
  rw [Connection.defect, chain_transport_backward n i j h]
  simp only [candidate, ← h, pow_succ]
  ring

theorem candidate_residual_le_one (n : ℕ) :
    ‖(chainConnection n).differential (OverlapTransport.Examples.chain n) (candidate n)‖ ≤ 1 := by
  apply (pi_norm_le_iff_of_nonneg zero_le_one).mpr
  intro a
  rw [Connection.differential_apply]
  rcases a.property with h | h
  · rw [candidate_forward_defect n _ _ h]; norm_num
  · rw [candidate_backward_defect n _ _ h]; norm_num

theorem candidate_residual_norm (n : ℕ) (hn : 0 < n) :
    ‖(chainConnection n).differential (OverlapTransport.Examples.chain n) (candidate n)‖ = 1 := by
  apply le_antisymm (candidate_residual_le_one n)
  let a : OverlapTransport.Edges (OverlapTransport.Examples.chain n) :=
    ⟨(⟨1,by omega⟩,⟨0,by omega⟩),Or.inr rfl⟩
  have he := norm_le_pi_norm
    ((chainConnection n).differential (OverlapTransport.Examples.chain n) (candidate n)) a
  change ‖(chainConnection n).defect (candidate n) ⟨1,by omega⟩ ⟨0,by omega⟩‖ ≤ _ at he
  rw [candidate_backward_defect n _ _ rfl] at he
  simpa using he

theorem candidate_error_coordinate (n : ℕ) (i : Fin (n+1)) :
    (candidate n-chainRepair n (candidate n)) i = (2 : ℝ)^i.val-1 := by
  change (8*(2 : ℝ)^i.val-1) - (2 : ℝ)^i.val * candidate n 0 = _
  rw [candidate_anchor]
  ring

theorem candidate_error_norm (n : ℕ) :
    ‖candidate n-chainRepair n (candidate n)‖ = (2 : ℝ)^n-1 := by
  have hp : ∀ k : ℕ, 1 ≤ (2 : ℝ)^k := fun k => one_le_pow₀ (by norm_num)
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg (sub_nonneg.mpr (hp n))).mpr
    intro i
    rw [candidate_error_coordinate, Real.norm_eq_abs, abs_of_nonneg (sub_nonneg.mpr (hp i.val))]
    apply sub_le_sub_right
    exact pow_le_pow_right₀ (by norm_num) (Nat.le_of_lt_succ i.isLt)
  · have h := norm_le_pi_norm (candidate n-chainRepair n (candidate n)) (Fin.last n)
    rw [candidate_error_coordinate] at h
    change ‖(2 : ℝ)^n-1‖ ≤ _ at h
    rw [Real.norm_eq_abs, abs_of_nonneg (sub_nonneg.mpr (hp n))] at h
    exact h

/-- Actual all-depth candidate and general-repair discrepancy. -/
theorem exponential_amplification (n : ℕ) (hn : 0 < n) :
    candidate n 0 = 7 ∧
    ‖(chainConnection n).differential (OverlapTransport.Examples.chain n) (candidate n)‖ = 1 ∧
    ‖candidate n-Rooted.orthogonalRepair (chainConnection n)
      (OverlapTransport.Examples.chainRouting n) (candidate n)‖ = (2 : ℝ)^n-1 := by
  rw [chainRepair_is_constructed]
  exact ⟨candidate_anchor n,candidate_residual_norm n hn,candidate_error_norm n⟩

/-- The old route-length-only bound fails on a three-edge nonisometric chain. -/
theorem length_only_bound_false :
    ¬ ‖candidate 3-Rooted.orthogonalRepair (chainConnection 3)
      (OverlapTransport.Examples.chainRouting 3) (candidate 3)‖ ≤
      (3 : ℝ)*‖(chainConnection 3).differential (OverlapTransport.Examples.chain 3) (candidate 3)‖ := by
  rw [chainRepair_is_constructed, candidate_error_norm, candidate_residual_norm 3 (by norm_num)]
  norm_num

/-- A fixed anchor can be amplified: global nonexpansiveness no longer follows. -/
theorem repair_not_nonexpansive :
    ¬ ∀ x : Fin 2 → ℝ,
      ‖Rooted.orthogonalRepair (chainConnection 1)
        (OverlapTransport.Examples.chainRouting 1) x‖ ≤ ‖x‖ := by
  intro h
  have hb := h (fun _ => 7)
  rw [chainRepair_is_constructed] at hb
  have hl := norm_le_pi_norm (chainRepair 1 (fun _ => (7 : ℝ))) (1 : Fin 2)
  have hx : ‖(fun _ : Fin 2 => (7 : ℝ))‖ = 7 := by simp
  rw [hx] at hb
  norm_num [chainRepair] at hl
  linarith

end Examples
end AmplifiedTransport
end KomorebiSpace
end
