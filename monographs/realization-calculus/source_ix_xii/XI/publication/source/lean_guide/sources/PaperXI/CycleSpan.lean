import PaperXI.PacketReturn

/-! The span of a finite Frobenius cycle with a nonzero closing scalar. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CycleSpan
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {f : ℕ}

def cycleVector (F : V ≃ₗ[K] V) (v : V) (a : Fin f) : V := (F ^ (a : ℕ)) v

def cycleSpan (F : V ≃ₗ[K] V) (v : V) (f : ℕ) : Submodule K V :=
  Submodule.span K (Set.range (cycleVector (f := f) F v))

theorem power_mem (F : V ≃ₗ[K] V) (v : V) {n : ℕ} (hn : n < f) :
    (F ^ n) v ∈ cycleSpan F v f := Submodule.subset_span ⟨⟨n, hn⟩, rfl⟩

theorem base_mem (F : V ≃ₗ[K] V) (v : V) (hf : 0 < f) : v ∈ cycleSpan F v f := by
  simpa using power_mem F v hf

theorem map_mem (F : V ≃ₗ[K] V) (v : V) (f : ℕ) (A : Module.End K V)
    (hA : ∀ a : Fin f, A (cycleVector F v a) ∈ cycleSpan F v f)
    {w : V} (hw : w ∈ cycleSpan F v f) : A w ∈ cycleSpan F v f := by
  induction hw using Submodule.span_induction with
  | mem w hw => obtain ⟨a, rfl⟩ := hw; exact hA a
  | zero => simp
  | add x y _ _ hx hy => simpa using (cycleSpan F v f).add_mem hx hy
  | smul c x _ hx => simpa using (cycleSpan F v f).smul_mem c hx

theorem forward_power (F : V ≃ₗ[K] V) (v : V) (n : ℕ) :
    F ((F ^ n) v) = (F ^ (n + 1)) v := by simp [pow_succ']

theorem backward_power (F : V ≃ₗ[K] V) (v : V) (n : ℕ) :
    F.symm ((F ^ (n + 1)) v) = (F ^ n) v := by simp [pow_succ']

/-- The inverse wrap uses the inverse of the actual closing scalar. -/
theorem inverse_wrap (F : V ≃ₗ[K] V) (v : V) (hf : 0 < f) {c : K} (hc : c ≠ 0)
    (hclose : (F ^ f) v = c • v) : F.symm v = c⁻¹ • (F ^ (f - 1)) v := by
  apply F.injective
  rw [F.apply_symm_apply, map_smul, forward_power, Nat.sub_add_cancel (by omega), hclose,
    smul_smul, inv_mul_cancel₀ hc, one_smul]

theorem forward_stable (F : V ≃ₗ[K] V) (v : V) (hf : 0 < f) {c : K}
    (hclose : (F ^ f) v = c • v) {w : V} (hw : w ∈ cycleSpan F v f) :
    F w ∈ cycleSpan F v f := by
  apply map_mem F v f F.toLinearMap (fun a => ?_) hw
  change F ((F ^ (a : ℕ)) v) ∈ _
  rw [forward_power]
  by_cases ha : (a : ℕ) + 1 < f
  · exact power_mem F v ha
  · have heq : (a : ℕ) + 1 = f := by have := a.isLt; omega
    rw [heq, hclose]
    exact (cycleSpan F v f).smul_mem c (base_mem F v hf)

theorem backward_stable (F : V ≃ₗ[K] V) (v : V) (hf : 0 < f) {c : K} (hc : c ≠ 0)
    (hclose : (F ^ f) v = c • v) {w : V} (hw : w ∈ cycleSpan F v f) :
    F.symm w ∈ cycleSpan F v f := by
  apply map_mem F v f F.symm.toLinearMap (fun a => ?_) hw
  change F.symm ((F ^ (a : ℕ)) v) ∈ _
  by_cases ha : (a : ℕ) = 0
  · rw [ha, pow_zero]
    change F.symm v ∈ _
    rw [inverse_wrap F v hf hc hclose]
    exact (cycleSpan F v f).smul_mem _ (power_mem F v (by omega))
  · have heq : (a : ℕ) = ((a : ℕ) - 1) + 1 := by omega
    rw [heq, backward_power]
    exact power_mem F v (by have := a.isLt; omega)

theorem span_ne_bot (F : V ≃ₗ[K] V) {v : V} (hv : v ≠ 0) (hf : 0 < f) :
    cycleSpan F v f ≠ ⊥ := by
  intro h
  have hm := base_mem F v hf
  rw [h] at hm
  exact hv (by simpa using hm)

end PaperXI.CycleSpan
