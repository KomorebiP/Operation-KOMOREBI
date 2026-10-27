import PaperXI.MonodromyChain

set_option autoImplicit false
noncomputable section
namespace PaperXI.MonodromyChain
variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W]
variable {m : ℕ}

theorem identity_path (i r : ℕ) : path (K := K) (W := W) (fun _ => 1) i r = 1 := by
  induction r with
  | zero => rfl
  | succ r ih => simp [ih]

/-- The bound in Proposition 2.3 cannot be decreased uniformly: the identity
transfer chain has no vanishing power before m. -/
theorem identity_shift_power_ne_zero [Nontrivial W] {r : ℕ} (hr : r < m) :
    (shift (K := K) (W := W) (m := m) (fun _ => 1)) ^ r ≠ 0 := by
  obtain ⟨w, hw⟩ := exists_ne (0 : W)
  intro h
  have hm : 0 < m := by omega
  have hx := congrArg (fun f : Module.End K (Fin m → W) => f (fun _ => w) ⟨0, hm⟩) h
  have hz : w = 0 := by simpa [pow_apply, hr, identity_path] using hx
  exact hw hz

end PaperXI.MonodromyChain
