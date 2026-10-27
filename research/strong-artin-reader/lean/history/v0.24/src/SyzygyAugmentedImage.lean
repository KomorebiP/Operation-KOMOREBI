import SyzygyCompatibleTarget
import AuxiliaryColumnCompletion

/-! Attach the compatible-target theorem to the existing auxiliary-column map.
The selection hypothesis keeps the full syzygy space rather than demanding
that a redundant transpose kernel vanish. -/

namespace Komorebi.StrongArtin.SyzygyAugmentedImage

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.SyzygyCompatibleTarget

noncomputable section

variable {k U W I : Type*} [Field k]
  [AddCommGroup U] [Module k U] [AddCommGroup W] [Module k W]

/-- A functional kills an augmented Jacobian iff it kills the original
Jacobian and every selected column. -/
theorem mem_augmented_dualKernel_iff
    (J : U →ₗ[k] W) (column : I → W) (Q : Finset I)
    (phi : Module.Dual k W) :
    phi ∈ LinearMap.ker (augmentedMap J column Q).dualMap ↔
      phi ∈ obstructionDual J ∧ ∀ i ∈ Q, phi (column i) = 0 := by
  classical
  constructor
  · intro h
    have hz := LinearMap.mem_ker.mp h
    constructor
    · rw [mem_obstructionDual]
      intro u
      have hu := LinearMap.congr_fun hz (u, 0)
      simpa [augmentedMap_apply] using hu
    · intro i hi
      let qi : Q := ⟨i, hi⟩
      have hu := LinearMap.congr_fun hz (0, Pi.single qi 1)
      simpa [augmentedMap, auxiliaryMap, qi,
        Fintype.linearCombination_apply_single] using hu
  · rintro ⟨hJ, hcol⟩
    apply LinearMap.mem_ker.mpr
    apply LinearMap.ext
    rintro ⟨u, a⟩
    change phi (augmentedMap J column Q (u, a)) = 0
    rw [augmentedMap_apply, map_add, map_sum]
    have hu := (mem_obstructionDual J phi).mp hJ u
    simp only [map_smul, hu, zero_add]
    apply Finset.sum_eq_zero
    intro i _
    simp [hcol i.1 i.2]

/-- The syzygy-corrected selection hypothesis gives the exact augmented dual kernel. -/
theorem augmented_dualKernel_eq_syzygies
    (J : U →ₗ[k] W) (column : I → W) (Q : Finset I)
    (S : Submodule k (Module.Dual k W))
    (hselected : ∀ phi : Module.Dual k W,
      (phi ∈ obstructionDual J ∧ ∀ i ∈ Q, phi (column i) = 0) ↔ phi ∈ S) :
    LinearMap.ker (augmentedMap J column Q).dualMap = S := by
  ext phi
  rw [mem_augmented_dualKernel_iff, hselected]

/-- The nonlinear equation space must be restricted to this target, not all W. -/
theorem augmented_range_eq_compatibleTarget
    (J : U →ₗ[k] W) (column : I → W) (Q : Finset I)
    (S : Submodule k (Module.Dual k W))
    (hselected : ∀ phi : Module.Dual k W,
      (phi ∈ obstructionDual J ∧ ∀ i ∈ Q, phi (column i) = 0) ↔ phi ∈ S) :
    LinearMap.range (augmentedMap J column Q) = compatibleTarget S :=
  range_eq_compatibleTarget_of_dualKernel_eq _ S
    (augmented_dualKernel_eq_syzygies J column Q S hselected)

/-- Exact solvability criterion for selected auxiliary corrections. -/
theorem auxiliary_correction_exists_iff
    (J : U →ₗ[k] W) (column : I → W) (Q : Finset I)
    (S : Submodule k (Module.Dual k W))
    (hselected : ∀ phi : Module.Dual k W,
      (phi ∈ obstructionDual J ∧ ∀ i ∈ Q, phi (column i) = 0) ↔ phi ∈ S)
    (error : W) :
    (∃ z : U × (Q → k), augmentedMap J column Q z + error = 0) ↔
      ∀ phi ∈ S, phi error = 0 := by
  rw [correction_exists_iff_compatible _ S
    (augmented_dualKernel_eq_syzygies J column Q S hselected),
    mem_compatibleTarget]

end
end Komorebi.StrongArtin.SyzygyAugmentedImage

#print axioms Komorebi.StrongArtin.SyzygyAugmentedImage.augmented_range_eq_compatibleTarget
#print axioms Komorebi.StrongArtin.SyzygyAugmentedImage.auxiliary_correction_exists_iff
