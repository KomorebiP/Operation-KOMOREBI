module
public import KomorebiPhysics.LadderDomains

/-! Mutual maximal adjoints and exact ladder norms. Adjoint domains are
identified by testing coordinate vectors, not inferred from notation. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace LadderDomains
open BoundedSpectral
open scoped BigOperators lp

theorem formalAdjoint : lower.IsFormalAdjoint raise := by
  change ∀ x y : domain, inner ℂ (lower x) (y : Space) = inner ℂ (x : Space) (raise y)
  intro x y
  calc
    inner ℂ (lower x) (y : Space) = ∑' n : ℕ, inner ℂ (lower x n) ((y : Space) n) :=
      lp.inner_eq_tsum _ _
    _ = ∑' n : ℕ, inner ℂ ((x : Space) (n+1)) (raise y (n+1)) := by
      apply tsum_congr
      intro n
      simp only [lower_apply, raise_succ, RCLike.inner_apply, map_mul, Complex.conj_ofReal]
      ring
    _ = inner ℂ (x : Space) (raise y) := by
      rw [lp.inner_eq_tsum, (lp.summable_inner (𝕜 := ℂ) (x : Space) (raise y)).tsum_eq_zero_add]
      simp only [raise_zero, inner_zero_right, zero_add]

theorem lower_adjoint_zero (y : lower.adjoint.domain) : lower.adjoint y 0 = 0 := by
  have h := (LinearPMap.adjoint_isFormalAdjoint (T := lower) dense_domain).symm (single 0 1) y
  change inner ℂ (lower (single 0 1)) (y : Space) =
    inner ℂ (lp.single 2 0 1 : Space) (lower.adjoint y) at h
  rw [lower_single_zero] at h
  simpa only [lp.inner_single_left, inner_zero_left,
    RCLike.inner_apply, map_one, mul_one, one_mul] using h.symm

theorem lower_adjoint_succ (y : lower.adjoint.domain) (n : ℕ) :
    lower.adjoint y (n+1) = (Real.sqrt (n+1 : ℕ) : ℂ) * (y : Space) n := by
  have h := (LinearPMap.adjoint_isFormalAdjoint (T := lower) dense_domain).symm (single (n+1) 1) y
  change inner ℂ (lower (single (n+1) 1)) (y : Space) =
    inner ℂ (lp.single 2 (n+1) 1 : Space) (lower.adjoint y) at h
  rw [lower_single_succ] at h
  simpa only [lp.inner_single_left, RCLike.inner_apply,
    mul_one, one_mul, map_one, Complex.conj_ofReal, mul_comm] using h.symm

theorem raise_adjoint_apply (y : raise.adjoint.domain) (n : ℕ) :
    raise.adjoint y n = (Real.sqrt (n+1 : ℕ) : ℂ) * (y : Space) (n+1) := by
  have h := (LinearPMap.adjoint_isFormalAdjoint (T := raise) dense_domain).symm (single n 1) y
  change inner ℂ (raise (single n 1)) (y : Space) =
    inner ℂ (lp.single 2 n 1 : Space) (raise.adjoint y) at h
  rw [raise_single] at h
  simpa only [lp.inner_single_left, RCLike.inner_apply,
    mul_one, one_mul, map_one, Complex.conj_ofReal, mul_comm] using h.symm

theorem lower_adjoint_domain_le : lower.adjoint.domain ≤ domain := by
  intro y hy
  apply (raise_mem_iff y).mp
  convert lp.memℓp (lower.adjoint ⟨y,hy⟩) using 1
  funext n
  cases n with
  | zero => exact (lower_adjoint_zero ⟨y,hy⟩).symm
  | succ n => exact (lower_adjoint_succ ⟨y,hy⟩ n).symm

theorem raise_adjoint_domain_le : raise.adjoint.domain ≤ domain := by
  intro y hy
  apply (lower_mem_iff y).mp
  convert lp.memℓp (raise.adjoint ⟨y,hy⟩) using 1
  funext n
  exact (raise_adjoint_apply ⟨y,hy⟩ n).symm

/-- Raising really is the maximal unbounded adjoint of lowering. -/
theorem lower_adjoint : lower.adjoint = raise := by
  apply le_antisymm
  · refine ⟨lower_adjoint_domain_le, ?_⟩
    intro x y hxy
    apply lp.ext
    funext n
    cases n with
    | zero => exact (lower_adjoint_zero x).trans (raise_zero y).symm
    | succ n =>
      calc
        _ = (Real.sqrt (n+1 : ℕ) : ℂ) * (x : Space) n := lower_adjoint_succ x n
        _ = (Real.sqrt (n+1 : ℕ) : ℂ) * (y : Space) n := congrArg (fun z : Space => (Real.sqrt (n+1 : ℕ) : ℂ) * z n) hxy
        _ = _ := (raise_succ y n).symm
  · exact formalAdjoint.le_adjoint dense_domain

theorem raise_adjoint : raise.adjoint = lower := by
  apply le_antisymm
  · refine ⟨raise_adjoint_domain_le, ?_⟩
    intro x y hxy
    apply lp.ext
    funext n
    calc
      _ = (Real.sqrt (n+1 : ℕ) : ℂ) * (x : Space) (n+1) := raise_adjoint_apply x n
      _ = (Real.sqrt (n+1 : ℕ) : ℂ) * (y : Space) (n+1) := congrArg (fun z : Space => (Real.sqrt (n+1 : ℕ) : ℂ) * z (n+1)) hxy
      _ = _ := (lower_apply y n).symm
  · exact formalAdjoint.symm.le_adjoint dense_domain

theorem lower_closed : lower.IsClosed := by
  rw [← raise_adjoint]
  exact LinearPMap.adjoint_isClosed dense_domain

theorem raise_closed : raise.IsClosed := by
  rw [← lower_adjoint]
  exact LinearPMap.adjoint_isClosed dense_domain

theorem lower_action_norm_sq (x : domain) :
    ‖lower x‖ ^ 2 = ∑' n : ℕ, (n : ℝ) * ‖(x : Space) n‖ ^ 2 := by
  have hs := (domain_iff (x : Space)).mp x.property
  rw [SpectralGraph.norm_sq_tsum, hs.tsum_eq_zero_add]
  simp only [Nat.cast_zero, zero_mul, zero_add]
  apply tsum_congr
  intro n
  exact lower_norm_sq (x : Space) n

theorem raise_action_norm_sq (x : domain) :
    ‖raise x‖ ^ 2 = ∑' n : ℕ, ((n : ℝ)+1) * ‖(x : Space) n‖ ^ 2 := by
  rw [SpectralGraph.norm_sq_tsum, (SpectralGraph.norm_sq_summable (raise x)).tsum_eq_zero_add]
  simp only [raise_zero, norm_zero, zero_pow (by omega : 2 ≠ 0), zero_add]
  apply tsum_congr
  intro n
  rw [raise_succ, SpectralGraph.weighted_norm_sq, Real.sq_sqrt (Nat.cast_nonneg _)]
  norm_cast

theorem ladder_norm_difference (x : domain) :
    ‖raise x‖ ^ 2 = ‖lower x‖ ^ 2 + ‖(x : Space)‖ ^ 2 := by
  rw [raise_action_norm_sq, lower_action_norm_sq, SpectralGraph.norm_sq_tsum]
  simp only [add_mul, one_mul]
  exact ((domain_iff (x : Space)).mp x.property).tsum_add
    (SpectralGraph.norm_sq_summable (x : Space))

end LadderDomains
end KomorebiPhysics
