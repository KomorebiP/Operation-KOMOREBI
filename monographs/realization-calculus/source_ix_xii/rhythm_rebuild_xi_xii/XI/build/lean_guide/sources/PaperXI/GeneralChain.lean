import PaperXI.MonodromyChain

/-! Proposition 2.3 for any operator satisfying the stated block support.
The transfer model is constructed from the operator; it is not an extra hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonodromyChain
open scoped BigOperators
variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W]
variable {m : ℕ}

def ChainSupported (N : Module.End K (Fin m → W)) : Prop :=
  ∀ i j : Fin m, i.val + 1 ≠ j.val → projector i * N * projector j = 0

theorem arbitrary_block_reconstruction (N : Module.End K (Fin m → W))
    (hN : ChainSupported N) :
    N = ∑ i : Fin m, ∑ j : Fin m,
      if i.val + 1 = j.val then projector i * N * projector j else 0 := by
  have h : ∀ i j : Fin m,
      (if i.val + 1 = j.val then projector i * N * projector j else 0) =
        projector i * N * projector j := by
    intro i j
    split
    · rfl
    · rename_i hij; exact (hN i j hij).symm
  simp_rw [h]
  simp only [← Finset.mul_sum, projector_sum, mul_one, ← Finset.sum_mul, one_mul]

theorem projector_eq_single (j : Fin m) (x : Fin m → W) :
    projector (K := K) j x = Pi.single j (x j) := by
  funext i
  by_cases h : i = j
  · subst i; simp
  · simp [h]

def extractedTransfers (N : Module.End K (Fin m → W)) (i : ℕ) : Module.End K W :=
  if h : i + 1 < m then
    (LinearMap.proj ⟨i, by omega⟩).comp
      (N.comp (LinearMap.single K (fun _ : Fin m => W) ⟨i + 1, h⟩))
  else 0

theorem coordinate_block_zero (N : Module.End K (Fin m → W)) (hN : ChainSupported N)
    (i j : Fin m) (h : i.val + 1 ≠ j.val) (x : Fin m → W) :
    N (projector (K := K) j x) i = 0 := by
  have hx := congrArg (fun f : Module.End K (Fin m → W) => f x i) (hN i j h)
  simpa [Module.End.mul_apply] using hx

/-- Any chain-supported operator is exactly its extracted transfer chain. -/
theorem eq_extracted_shift (N : Module.End K (Fin m → W)) (hN : ChainSupported N) :
    N = shift (extractedTransfers N) := by
  apply LinearMap.ext
  intro x
  funext i
  have hx : N x i = ∑ j : Fin m, N (projector (K := K) j x) i := by
    have hp := congrArg (fun f : Module.End K (Fin m → W) => N (f x) i)
      (projector_sum (K := K) (W := W) (m := m))
    simpa [LinearMap.sum_apply, map_sum, Finset.sum_apply] using hp.symm
  rw [hx, shift_apply]
  by_cases hi : i.val + 1 < m
  · rw [dite_eq_left hi]
    rw [Finset.sum_eq_single (⟨i.val + 1, hi⟩ : Fin m)]
    · simp [extractedTransfers, hi, projector_eq_single]
    · intro j _ hj
      apply coordinate_block_zero N hN i j
      intro he
      apply hj
      apply Fin.ext
      exact he.symm
    · simp
  · rw [dite_eq_right hi]
    apply Finset.sum_eq_zero
    intro j _
    exact coordinate_block_zero N hN i j (by omega) x

theorem arbitrary_nilpotent_bound (N : Module.End K (Fin m → W))
    (hN : ChainSupported N) : N ^ m = 0 := by
  rw [eq_extracted_shift N hN]
  exact nilpotent_bound _

theorem arbitrary_power_paths (N : Module.End K (Fin m → W)) (hN : ChainSupported N)
    (r : ℕ) (x : Fin m → W) (i : Fin m) :
    (N ^ r) x i = if h : i.val + r < m then
      path (extractedTransfers N) i.val r (x ⟨i.val + r, h⟩) else 0 := by
  calc
    (N ^ r) x i = (shift (extractedTransfers N) ^ r) x i := by
      conv_lhs => rw [eq_extracted_shift N hN]
    _ = _ := pow_apply _ _ _ _

end PaperXI.MonodromyChain
