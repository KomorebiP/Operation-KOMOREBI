import PaperIRelease.TopologyDenseCompletion
import KomorebiVerification.SeedRankBasics

/-! # Actual free evaluation and restricted quotient completion -/

noncomputable section
open Set Function UniformSpace

namespace PaperIRelease.TopologyDenseCompletion

section FreePresentation

variable {A X : Type*} [Ring A] [AddCommGroup X] [Module A X]
variable [UniformSpace X] [IsUniformAddGroup X] [UniformContinuousConstSMul A X]
variable [CompleteSpace X] [T0Space X]

omit [IsUniformAddGroup X] [UniformContinuousConstSMul A X] [CompleteSpace X] [T0Space X] in
/-- Dense generation is exactly dense range of the actual seed evaluation
map, with no surjectivity assumption. -/
theorem dense_free_evaluation {ι : Type*} (s : ι → X)
    (hS : Dense (Submodule.span A (Set.range s) : Set X)) :
    DenseRange (Komorebi.SeedRankBasics.multiSeedMap A X s) := by
  change Dense (LinearMap.range (Komorebi.SeedRankBasics.multiSeedMap A X s) : Set X)
  rwa [Komorebi.SeedRankBasics.range_multiSeedMap]

/-- Literal finite free-presentation completion. `r = 0` and the zero
target are included. The equivalence is linear over the acting ring `A`,
so it simultaneously intertwines every element of the acting algebra. -/
def completedFreePresentation (r : ℕ) (s : Fin r → X)
    (hS : Dense (Submodule.span A (Set.range s) : Set X)) :=
  completedQuotientEquiv (Komorebi.SeedRankBasics.multiSeedMap A X s)
    (dense_free_evaluation s hS)

end FreePresentation

section RestrictedQuotient

variable {𝕜 X Y : Type*} [Ring 𝕜]
variable [AddCommGroup X] [Module 𝕜 X]
variable [AddCommGroup Y] [Module 𝕜 Y] [UniformSpace Y]
variable [IsUniformAddGroup Y] [UniformContinuousConstSMul 𝕜 Y]
variable [CompleteSpace Y] [T0Space Y]

omit [UniformSpace Y] [IsUniformAddGroup Y] [UniformContinuousConstSMul 𝕜 Y]
  [CompleteSpace Y] [T0Space Y] in
/-- The relation module of the restriction to `D` is exactly `D ∩ ker f`,
expressed as a submodule of `D`. -/
theorem restricted_kernel (f : X →ₗ[𝕜] Y) (D : Submodule 𝕜 X) :
    (f.comp D.subtype).ker = f.ker.comap D.subtype := rfl

omit [IsUniformAddGroup Y] [UniformContinuousConstSMul 𝕜 Y] [CompleteSpace Y] [T0Space Y] in
/-- Density of the image `f(D)` is density of the restricted presentation. -/
theorem restricted_dense (f : X →ₗ[𝕜] Y) (D : Submodule 𝕜 X)
    (hd : Dense (f '' (D : Set X))) : DenseRange (f.comp D.subtype) := by
  have he : Set.range (f.comp D.subtype) = f '' (D : Set X) := by
    ext y
    constructor
    · rintro ⟨x, rfl⟩
      exact ⟨x, x.property, rfl⟩
    · rintro ⟨x, hx, rfl⟩
      exact ⟨⟨x, hx⟩, rfl⟩
  change Dense (Set.range (f.comp D.subtype))
  rwa [he]

/-- The completed realization from the actual quotient `D/(D ∩ ker f)`.
Its topology is pulled back from `Y`; it need not be the quotient topology
inherited from the original domain. -/
def completedRestrictedQuotient (f : X →ₗ[𝕜] Y) (D : Submodule 𝕜 X)
    (hd : Dense (f '' (D : Set X))) :=
  completedQuotientEquiv (f.comp D.subtype) (restricted_dense f D hd)

end RestrictedQuotient

end PaperIRelease.TopologyDenseCompletion
