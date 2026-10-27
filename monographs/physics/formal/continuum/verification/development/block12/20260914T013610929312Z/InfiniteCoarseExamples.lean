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
open BoundedSpectral SpectralEvolution SpectralEvolutionExamples HarmonicSurrogates Classical
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

end InfiniteCoarseExamples
end KomorebiPhysics
