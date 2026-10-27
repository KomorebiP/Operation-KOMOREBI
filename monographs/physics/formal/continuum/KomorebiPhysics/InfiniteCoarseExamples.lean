module
public import KomorebiPhysics.InfiniteCellAlgebra
public import KomorebiPhysics.SpectralCells
public import KomorebiPhysics.SpectralEvolutionExamples

/-! A non-spectral atlas on actual infinite l2, with infinite even/odd coarse
cells and an exact nonzero transfer on a constructed normalized global orbit. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace InfiniteCoarseExamples
open BoundedSpectral SpectralEvolution SpectralEvolutionExamples HarmonicSurrogates UnboundedExamples Classical
open scoped BigOperators Topology lp

def entry (i j : ℕ) : Space →L[ℂ] Space :=
  (lp.singleContinuousLinearMap ℂ (fun _ : ℕ => ℂ) 2 i).comp
    (lp.evalCLM ℂ (fun _ : ℕ => ℂ) 2 j)

theorem entry_apply (i j : ℕ) (x : Space) : entry i j x = lp.single 2 i (x j) := rfl

def mix : Space →L[ℂ] Space :=
  ContinuousLinearMap.id ℂ Space + (-2/5 : ℂ) • entry 0 0 +
    (4/5 : ℂ) • entry 0 1 + (4/5 : ℂ) • entry 1 0 - (8/5 : ℂ) • entry 1 1

theorem mix_coordinate (x : Space) (n : ℕ) :
    mix x n = if n = 0 then (3/5 : ℂ) * x 0 + (4/5 : ℂ) * x 1
      else if n = 1 then (4/5 : ℂ) * x 0 - (3/5 : ℂ) * x 1 else x n := by
  have he : mix x n = x n + (-2/5 : ℂ) * (lp.single 2 0 (x 0) : Space) n +
      (4/5 : ℂ) * (lp.single 2 0 (x 1) : Space) n +
      (4/5 : ℂ) * (lp.single 2 1 (x 0) : Space) n -
      (8/5 : ℂ) * (lp.single 2 1 (x 1) : Space) n := rfl
  rw [he]
  by_cases hn : n = 0
  · subst n
    simp
    ring
  · by_cases h1 : n = 1
    · subst n
      simp
      ring
    · simp [hn, h1]

theorem mix_involution (x : Space) : mix (mix x) = x := by
  apply lp.ext
  funext n
  simp only [mix_coordinate]
  by_cases h0 : n = 0 <;> by_cases h1 : n = 1 <;> simp [h0, h1] <;> ring

theorem entry_adjoint (i j : ℕ) (x y : Space) :
    inner ℂ (entry i j x) y = inner ℂ x (entry j i y) := by
  simp only [entry_apply, lp.inner_single_left, lp.inner_single_right]

theorem mix_selfAdjoint (x y : Space) : inner ℂ (mix x) y = inner ℂ x (mix y) := by
  simp only [mix, add_apply, sub_apply, smul_apply, ContinuousLinearMap.id_apply,
    inner_add_left, inner_add_right, inner_sub_left, inner_sub_right, inner_smul_left,
    inner_smul_right, entry_adjoint, map_neg, map_div₀, map_ofNat]
  ring

theorem mix_norm (x : Space) : ‖mix x‖ = ‖x‖ :=
  StrongAtlas.reflection_norm mix mix_selfAdjoint mix_involution x

/-- Finite-coordinate modification preserves every maximal real diagonal domain. -/
theorem mix_mem_domain (eig : ℕ → ℝ) (x : (DiagonalDomain.operator eig).domain) :
    mix x ∈ (DiagonalDomain.operator eig).domain := by
  change (ContinuousLinearMap.id ℂ Space + (-2/5 : ℂ) • entry 0 0 +
    (4/5 : ℂ) • entry 0 1 + (4/5 : ℂ) • entry 1 0 - (8/5 : ℂ) • entry 1 1) x ∈ _
  simp only [add_apply, sub_apply, smul_apply, ContinuousLinearMap.id_apply, entry_apply]
  exact (DiagonalDomain.domain eig).sub_mem
    ((DiagonalDomain.domain eig).add_mem
      ((DiagonalDomain.domain eig).add_mem
        ((DiagonalDomain.domain eig).add_mem x.property
          ((DiagonalDomain.domain eig).smul_mem _ (DiagonalDomain.single_mem eig 0 _)))
        ((DiagonalDomain.domain eig).smul_mem _ (DiagonalDomain.single_mem eig 0 _)))
      ((DiagonalDomain.domain eig).smul_mem _ (DiagonalDomain.single_mem eig 1 _)))
    ((DiagonalDomain.domain eig).smul_mem _ (DiagonalDomain.single_mem eig 1 _))

def fine (eig : ℕ → ℝ) : DomainAtlas (DiagonalDomain.operator eig) ℕ where
  atlas := DiagonalDomain.coordinateAtlas.reflect mix mix_selfAdjoint mix_involution
  preserves i x := by
    change mix (DiagonalDomain.coordinate i (mix x)) ∈ _
    exact mix_mem_domain eig ⟨lp.single 2 i (mix x i), DiagonalDomain.single_mem eig i _⟩

theorem fine_cell (eig : ℕ → ℝ) (C : Set ℕ) (x : Space) :
    (fine eig).atlas.cell C x = mix (SpectralCells.mask C (mix x)) :=
  DiagonalDomain.coordinateAtlas.reflect_cell mix mix_selfAdjoint mix_involution C x

theorem fine_cell_preserves (eig : ℕ → ℝ) (C : Set ℕ)
    (x : (DiagonalDomain.operator eig).domain) :
    (fine eig).atlas.cell C x ∈ (DiagonalDomain.operator eig).domain := by
  rw [fine_cell]
  let ux : (DiagonalDomain.operator eig).domain := ⟨mix x, mix_mem_domain eig x⟩
  exact mix_mem_domain eig ⟨SpectralCells.mask C ux, SpectralCells.mask_mem_domain eig C ux⟩

def parity (n : ℕ) : Fin 2 := ⟨n % 2, Nat.mod_lt n (by decide)⟩

def coarse (eig : ℕ → ℝ) : DomainAtlas (DiagonalDomain.operator eig) (Fin 2) :=
  (fine eig).coarsenOfPreserves parity (fun a x => fine_cell_preserves eig (parity ⁻¹' {a}) x)

theorem coarse_proj (eig : ℕ → ℝ) (a : Fin 2) (x : Space) :
    (coarse eig).atlas.proj a x = mix (SpectralCells.mask (parity ⁻¹' {a}) (mix x)) :=
  fine_cell eig _ x

theorem parity_even (n : ℕ) : parity (2 * n) = 0 := by
  apply Fin.ext
  simp [parity]

theorem parity_odd (n : ℕ) : parity (2 * n + 1) = 1 := by
  apply Fin.ext
  simp [parity]

theorem even_fiber_infinite : (parity ⁻¹' {(0 : Fin 2)}).Infinite :=
  Set.infinite_of_injective_forall_mem (f := fun n : ℕ => 2 * n)
    (by intro m n h; change 2 * m = 2 * n at h; omega) parity_even

theorem odd_fiber_infinite : (parity ⁻¹' {(1 : Fin 2)}).Infinite :=
  Set.infinite_of_injective_forall_mem (f := fun n : ℕ => 2 * n + 1)
    (by intro m n h; change 2 * m + 1 = 2 * n + 1 at h; omega) parity_odd

theorem coherentState_tail (n : ℕ) (h0 : n ≠ 0) (h1 : n ≠ 1) :
    (coherentState : Space) n = 0 := by
  have he : (coherentState : Space) n = (lp.single 2 0 (3/5) : Space) n +
      (lp.single 2 1 ((4/5) * Complex.I) : Space) n := rfl
  simp [he, h0, h1]

theorem even_mask_state :
    SpectralCells.mask (parity ⁻¹' {(0 : Fin 2)}) (mix (coherentState : Space)) =
      lp.single 2 0 ((9/25 : ℂ) + (16/25) * Complex.I) := by
  apply lp.ext
  funext n
  rw [SpectralCells.mask_apply, mix_coordinate]
  by_cases h0 : n = 0
  · subst n
    norm_num [parity, coherentState_zero, coherentState_one]
    ring
  · by_cases h1 : n = 1
    · subst n
      norm_num [parity]
    · simp [h0, h1, coherentState_tail n h0 h1]

theorem mix_single_zero (z : ℂ) :
    mix (lp.single 2 0 z) = lp.single 2 0 ((3/5 : ℂ) * z) +
      lp.single 2 1 ((4/5 : ℂ) * z) := by
  apply lp.ext
  funext n
  have he : (lp.single 2 0 ((3/5 : ℂ) * z) + lp.single 2 1 ((4/5 : ℂ) * z) : Space) n =
      (lp.single 2 0 ((3/5 : ℂ) * z) : Space) n +
      (lp.single 2 1 ((4/5 : ℂ) * z) : Space) n := rfl
  rw [mix_coordinate, he]
  by_cases h0 : n = 0 <;> by_cases h1 : n = 1 <;> simp [h0, h1]

theorem even_project_state :
    (coarse harmonicEigenvalue).atlas.proj 0 (coherentState : Space) =
      lp.single 2 0 ((3/5 : ℂ) * ((9/25) + (16/25) * Complex.I)) +
      lp.single 2 1 ((4/5 : ℂ) * ((9/25) + (16/25) * Complex.I)) := by
  rw [coarse_proj, even_mask_state, mix_single_zero]

theorem even_probability :
    (coarse harmonicEigenvalue).atlas.energy (coherentState : Space) 0 = 337/625 := by
  rw [StrongAtlas.energy, coarse_proj, mix_norm, even_mask_state,
    lp.norm_single (by norm_num : (0 : ENNReal) < 2)]
  rw [Complex.sq_norm, Complex.normSq_apply]
  norm_num [Complex.mul_re, Complex.mul_im]

theorem even_rate : (coarse harmonicEigenvalue).rate coherentState 0 = 288/625 := by
  rw [DomainAtlas.rate, even_project_state, inner_add_left,
    lp.inner_single_left, lp.inner_single_left]
  simp only [DiagonalDomain.operator_apply, coherentState_zero, coherentState_one, harmonicEigenvalue]
  norm_num [RCLike.inner_apply, map_div₀, map_ofNat, Complex.mul_re, Complex.mul_im]

theorem current_even_from_odd :
    (coarse harmonicEigenvalue).current coherentState 0 1 = 288/625 := by
  have h := (coarse harmonicEigenvalue).current_row_tsum (DiagonalDomain.symmetric harmonicEigenvalue)
    coherentState 0
  rw [tsum_fintype, Fin.sum_univ_two,
    (coarse harmonicEigenvalue).current_self (DiagonalDomain.symmetric harmonicEigenvalue),
    zero_add, even_rate] at h
  exact h

theorem current_odd_from_even :
    (coarse harmonicEigenvalue).current coherentState 1 0 = -288/625 := by
  rw [(coarse harmonicEigenvalue).current_antisymm (DiagonalDomain.symmetric harmonicEigenvalue),
    current_even_from_odd]
  ring

/-- The derivative comes from the constructed global spectral solution, not
an affine local witness or an assumed scalar balance. -/
theorem even_probability_hasDerivAt :
    HasDerivAt (fun t => (coarse harmonicEigenvalue).atlas.energy
      (evolution harmonicEigenvalue t (coherentState : Space)) 0) (288/625) 0 := by
  have h := (coarse harmonicEigenvalue).hasDerivAt_energy
    (ψ := fun s => domainEvolution harmonicEigenvalue s coherentState)
    (orbit_hasDerivAt harmonicEigenvalue coherentState 0) 0
  rw [domainEvolution_zero, even_rate] at h
  exact h

theorem infinite_even_energy_hasDerivAt :
    HasDerivAt (fun t => ∑' i : parity ⁻¹' {(0 : Fin 2)},
      (fine harmonicEigenvalue).atlas.energy
        (evolution harmonicEigenvalue t (coherentState : Space)) i) (288/625) 0 := by
  have he : (fun t => ∑' i : parity ⁻¹' {(0 : Fin 2)},
      (fine harmonicEigenvalue).atlas.energy (evolution harmonicEigenvalue t (coherentState : Space)) i) =
      (fun t => (coarse harmonicEigenvalue).atlas.energy
        (evolution harmonicEigenvalue t (coherentState : Space)) 0) := by
    funext t
    exact ((fine harmonicEigenvalue).atlas.coarsenInfinite_energy parity _ 0).symm
  rw [he]
  exact even_probability_hasDerivAt

theorem coarse_current_iterated_nonzero :
    (∑' i : parity ⁻¹' {(0 : Fin 2)}, ∑' j : parity ⁻¹' {(1 : Fin 2)},
      (fine harmonicEigenvalue).current coherentState i j) = 288/625 := by
  calc
    _ = (coarse harmonicEigenvalue).current coherentState 0 1 :=
      ((fine harmonicEigenvalue).coarse_current_iterated parity
        (fun a x => fine_cell_preserves harmonicEigenvalue (parity ⁻¹' {a}) x)
        (DiagonalDomain.symmetric harmonicEigenvalue) coherentState 0 1).symm
    _ = _ := current_even_from_odd

end InfiniteCoarseExamples
end KomorebiPhysics
