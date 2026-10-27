import KomorebiLSM.FiniteInstrument

/-! Strictly positive beliefs span the entire finite real vector space.
The proof uses explicit interior priors rather than an assumed spanning condition. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open FiniteBayes
universe u
variable {I : Type u} [Fintype I] [Nonempty I]

def IsStrictPrior (p : I → ℝ) : Prop := IsPrior p ∧ ∀ i, 0 < p i

noncomputable def uniformPrior : I → ℝ := fun _ => (Fintype.card I : ℝ)⁻¹

theorem uniform_strict : IsStrictPrior (uniformPrior : I → ℝ) := by
  have hc : (0 : ℝ) < Fintype.card I := by exact_mod_cast Fintype.card_pos
  refine ⟨⟨fun _ => (inv_pos.mpr hc).le, ?_⟩, fun _ => inv_pos.mpr hc⟩
  simp [uniformPrior, ne_of_gt hc]

noncomputable def positiveProbe [DecidableEq I] (i : I) : I → ℝ :=
  (1/2 : ℝ) • uniformPrior + (1/2 : ℝ) • pointMass i

theorem positiveProbe_strict [DecidableEq I] (i : I) : IsStrictPrior (positiveProbe i) := by
  have hu := uniform_strict (I := I)
  have hp := point_prior i
  have pos : ∀ j, 0 < positiveProbe i j := by
    intro j
    change 0 < (1/2 : ℝ) * uniformPrior j + (1/2 : ℝ) * pointMass i j
    exact add_pos_of_pos_of_nonneg (mul_pos (by norm_num) (hu.2 j))
      (mul_nonneg (by norm_num) (hp.1 j))
  refine ⟨⟨fun j => (pos j).le, ?_⟩, pos⟩
  simp only [positiveProbe, Pi.add_apply, Pi.smul_apply, smul_eq_mul,
    Finset.sum_add_distrib, ← Finset.mul_sum, hu.1.2, hp.2]
  norm_num

theorem linearMap_zero_of_strict_priors {E : Type*} [AddCommGroup E] [Module ℝ E]
    (F : (I → ℝ) →ₗ[ℝ] E)
    (h : ∀ p, IsStrictPrior p → F p = 0) : F = 0 := by
  classical
  have hu := h uniformPrior uniform_strict
  have hi : ∀ i, F (pointMass i) = 0 := by
    intro i
    have hp := h (positiveProbe i) (positiveProbe_strict i)
    simp only [positiveProbe, map_add, map_smul, hu, smul_zero, zero_add] at hp
    exact (smul_eq_zero.mp hp).resolve_left (by norm_num)
  apply LinearMap.ext
  intro p
  rw [vector_eq_sum_pointMass p, map_sum]
  simp only [map_smul, hi, smul_zero, Finset.sum_const_zero, LinearMap.zero_apply]

theorem linearMap_eq_of_strict_priors {E : Type*} [AddCommGroup E] [Module ℝ E]
    (F G : (I → ℝ) →ₗ[ℝ] E)
    (h : ∀ p, IsStrictPrior p → F p = G p) : F = G := by
  apply sub_eq_zero.mp
  exact linearMap_zero_of_strict_priors (F-G) (fun p hp => by simp [h p hp])

/-- Any nonzero nonnegative branch has positive evidence at every strict belief. -/
theorem nonnegative_branch_mass_pos (M : Matrix I I ℝ)
    (hM : ∀ j i, 0 ≤ M j i) (h0 : M ≠ 0)
    (p : I → ℝ) (hp : ∀ i, 0 < p i) : 0 < mass (M.mulVecLin p) := by
  classical
  obtain ⟨j, i, hji⟩ : ∃ j i, 0 < M j i := by
    by_contra h
    push Not at h
    apply h0
    ext j i
    exact le_antisymm (h j i) (hM j i)
  rw [mass_apply]
  apply Finset.sum_pos'
  · intro k _
    exact Finset.sum_nonneg (fun i _ => mul_nonneg (hM k i) (hp i).le)
  · refine ⟨j, Finset.mem_univ j, ?_⟩
    exact Finset.sum_pos' (fun i _ => mul_nonneg (hM j i) (hp i).le)
      ⟨i, Finset.mem_univ i, mul_pos hji (hp i)⟩

end Komorebi.LSM.FiniteInstruments
