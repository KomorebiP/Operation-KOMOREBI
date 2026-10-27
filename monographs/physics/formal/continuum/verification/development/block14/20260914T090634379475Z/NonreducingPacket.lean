module
public import KomorebiPhysics.DiagonalResolvents
public import KomorebiPhysics.InfiniteCoarseExamples

/-! A genuine orthogonal packet that does not reduce the unbounded harmonic
Hamiltonian. It is the previously constructed first reflected coordinate.
The domain commutator is an explicitly constructed finite-rank bounded map. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace NonreducingPacket
open BoundedSpectral InfiniteCoarseExamples ResolventDomain
open scoped lp BigOperators

/-- A rank-one orthogonal projector on the actual infinite Hilbert space. -/
def packet (eig : ℕ → ℝ) : Space →L[ℂ] Space := (fine eig).atlas.proj 0

theorem packet_coordinate (eig : ℕ → ℝ) (x : Space) (n : ℕ) :
    packet eig x n = if n = 0 then (9/25 : ℂ) * x 0 + (12/25 : ℂ) * x 1
      else if n = 1 then (12/25 : ℂ) * x 0 + (16/25 : ℂ) * x 1 else 0 := by
  change mix (lp.single 2 0 (mix x 0)) n = _
  rw [mix_single_zero]
  have he : (lp.single 2 0 ((3/5 : ℂ) * mix x 0) +
      lp.single 2 1 ((4/5 : ℂ) * mix x 0) : Space) n =
      (lp.single 2 0 ((3/5 : ℂ) * mix x 0) : Space) n +
      (lp.single 2 1 ((4/5 : ℂ) * mix x 0) : Space) n := rfl
  rw [he, mix_coordinate]
  by_cases h0 : n = 0 <;> by_cases h1 : n = 1 <;> simp [h0, h1] <;> ring

theorem packet_idempotent (eig : ℕ → ℝ) (x : Space) :
    packet eig (packet eig x) = packet eig x := (fine eig).atlas.idempotent 0 x

theorem packet_selfAdjoint (eig : ℕ → ℝ) (x y : Space) :
    inner ℂ (packet eig x) y = inner ℂ x (packet eig y) := (fine eig).atlas.selfAdjoint 0 x y

theorem packet_preserves (eig : ℕ → ℝ) (x : (DiagonalDomain.operator eig).domain) :
    packet eig x ∈ (DiagonalDomain.operator eig).domain := (fine eig).preserves 0 x

/-- This two-coordinate skew exchange has norm exactly one. -/
def planeSkew : Space →L[ℂ] Space := entry 0 1 - entry 1 0

theorem planeSkew_apply (x : Space) :
    planeSkew x = lp.single 2 0 (x 1) - lp.single 2 1 (x 0) := rfl

theorem planeSkew_norm_sq (x : Space) :
    ‖planeSkew x‖ ^ 2 = ‖x 0‖ ^ 2 + ‖x 1‖ ^ 2 := by
  rw [planeSkew_apply, norm_sub_sq (𝕜 := ℂ)]
  simp [lp.inner_single_left, lp.norm_single (by norm_num : (0 : ENNReal) < 2)]
  ring

theorem planeSkew_state_bound (x : Space) : ‖planeSkew x‖ ≤ ‖x‖ := by
  have h := (DiagonalDomain.coordinateAtlas (I := ℕ)).finite_energy_le ({0, 1} : Finset ℕ) x
  have hh : ‖x 0‖ ^ 2 + ‖x 1‖ ^ 2 ≤ ‖x‖ ^ 2 := by
    simpa [StrongAtlas.energy, DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply,
      lp.norm_single (by norm_num : (0 : ENNReal) < 2)] using h
  rw [← planeSkew_norm_sq] at hh
  nlinarith [norm_nonneg (planeSkew x), norm_nonneg x]

theorem planeSkew_single_one : planeSkew (lp.single 2 1 1) = lp.single 2 0 1 := by
  simp [planeSkew_apply]

theorem planeSkew_norm : ‖planeSkew‖ = 1 := by
  apply le_antisymm
  · exact planeSkew.opNorm_le_bound (by norm_num) (by simpa using planeSkew_state_bound)
  · have h := planeSkew.le_opNorm (lp.single 2 1 (1 : ℂ))
    simpa [planeSkew_single_one, lp.norm_single (by norm_num : (0 : ENNReal) < 2)] using h

/-- An explicit extension of [H,P], valid for every real diagonal sequence. -/
def generatorCommutator (eig : ℕ → ℝ) : Space →L[ℂ] Space :=
  ((12/25 : ℂ) * ((eig 0 : ℂ) - eig 1)) • planeSkew

theorem generatorCommutator_coordinate (eig : ℕ → ℝ) (x : Space) (n : ℕ) :
    generatorCommutator eig x n =
      if n = 0 then ((12/25 : ℂ) * ((eig 0 : ℂ) - eig 1)) * x 1
      else if n = 1 then -((12/25 : ℂ) * ((eig 0 : ℂ) - eig 1)) * x 0 else 0 := by
  have he : generatorCommutator eig x n =
      ((12/25 : ℂ) * ((eig 0 : ℂ) - eig 1)) *
      ((lp.single 2 0 (x 1) : Space) n - (lp.single 2 1 (x 0) : Space) n) := rfl
  rw [he]
  by_cases h0 : n = 0 <;> by_cases h1 : n = 1 <;> simp [h0, h1]

theorem generatorCommutator_agrees (eig : ℕ → ℝ) (x : (DiagonalDomain.operator eig).domain) :
    DiagonalDomain.operator eig (restrict _ (packet eig) (packet_preserves eig) x) -
      packet eig (DiagonalDomain.operator eig x) = generatorCommutator eig x := by
  apply lp.ext
  funext n
  change (eig n : ℂ) * packet eig x n - packet eig (DiagonalDomain.operator eig x) n = _
  rw [packet_coordinate, packet_coordinate, generatorCommutator_coordinate]
  simp only [DiagonalDomain.operator_apply]
  by_cases h0 : n = 0
  · subst n
    norm_num
    ring
  · by_cases h1 : n = 1
    · subst n
      norm_num
      ring
    · simp [h0, h1]

def boundedCommutator (eig : ℕ → ℝ) :
    BoundedCommutator (DiagonalDomain.operator eig) (packet eig) where
  preserves := packet_preserves eig
  bound := generatorCommutator eig
  agrees := generatorCommutator_agrees eig

theorem generatorCommutator_norm (eig : ℕ → ℝ) :
    ‖generatorCommutator eig‖ = (12/25 : ℝ) * |eig 0 - eig 1| := by
  rw [generatorCommutator, norm_smul, planeSkew_norm, mul_one, norm_mul]
  have he : (eig 0 : ℂ) - eig 1 = ((eig 0 - eig 1 : ℝ) : ℂ) := by simp
  rw [he, Complex.norm_real, Real.norm_eq_abs]
  norm_num

/-- Every bounded diagonal resolvent has an exact two-coordinate commutator. -/
theorem diagonal_commutator (eig : ℕ → ℝ) (a : Symbol) :
    commutator (diagonal a) (packet eig) =
      ((12/25 : ℂ) * (a 0 - a 1)) • planeSkew := by
  ext x n
  change a n * packet eig x n - packet eig (diagonal a x) n =
    ((12/25 : ℂ) * (a 0 - a 1)) *
      ((lp.single 2 0 (x 1) : Space) n - (lp.single 2 1 (x 0) : Space) n)
  simp only [packet_coordinate, diagonal_apply]
  by_cases h0 : n = 0
  · subst n; simp; ring
  · by_cases h1 : n = 1
    · subst n; simp; ring
    · simp [h0, h1]

theorem diagonal_commutator_norm (eig : ℕ → ℝ) (a : Symbol) :
    ‖commutator (diagonal a) (packet eig)‖ = (12/25 : ℝ) * ‖a 0 - a 1‖ := by
  rw [diagonal_commutator, norm_smul, planeSkew_norm, mul_one, norm_mul]
  norm_num

end NonreducingPacket
end KomorebiPhysics
