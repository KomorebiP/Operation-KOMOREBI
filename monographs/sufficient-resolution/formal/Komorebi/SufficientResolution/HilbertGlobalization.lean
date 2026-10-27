import Komorebi.SufficientResolution.OrthogonalResolution
import Komorebi.SufficientResolution.Globalization

/-!
# Harmonic representatives of the existing globalization quotient

The middle orthogonal component is identified with the actual algebraic
obstruction quotient defined in block 01. The equivalence is constructed in
both directions. It is a linear equivalence, not a claimed quotient-norm isometry.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.HilbertGlobalization

open OrthogonalResolution

variable {G V W : Type*}
variable [AddCommGroup G] [Module ℝ G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)

/-- The original chain condition supplies the nesting required by the orthogonal theorem. -/
 theorem range_le_kernel (h : delta.toLinearMap.comp A = 0) :
    LinearMap.range A ≤ LinearMap.ker delta.toLinearMap :=
  Globalization.realizable_compatible A delta.toLinearMap h

variable [(LinearMap.range A).HasOrthogonalProjection]
variable [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection]

/-- Every orthogonal best local reconstruction is an actual global image. -/
 theorem exists_best_global_image (v : V) :
    ∃ g : G, A g = realized (LinearMap.range A) v :=
  realized_mem (LinearMap.range A) v

 theorem best_global_image_error (h : delta.toLinearMap.comp A = 0) (v : V) :
    ∃ g : G, ‖v - A g‖ ^ 2 =
      ‖obstruction (LinearMap.range A) (LinearMap.ker delta.toLinearMap) v‖ ^ 2 +
      ‖inconsistency (LinearMap.ker delta.toLinearMap) v‖ ^ 2 := by
  obtain ⟨g, hg⟩ := exists_best_global_image A v
  exact ⟨g, by rw [hg]; exact error_norm_sq _ _ (range_le_kernel A delta h) v⟩

/-- Uniqueness of the best represented vector does not imply uniqueness of its global preimage. -/
 theorem best_global_image_unique (v : V) (g : G) :
    ‖v - A g‖ = Metric.infDist v (LinearMap.range A : Set V) ↔
      A g = realized (LinearMap.range A) v := by
  rw [infDist_eq_error]
  exact best_approximation_unique _ v (LinearMap.mem_range_self A g)

 theorem class_zero_iff_component_zero (v : LinearMap.ker delta.toLinearMap) :
    Globalization.obstructionClass A delta.toLinearMap v = 0 ↔
      obstruction (LinearMap.range A) (LinearMap.ker delta.toLinearMap) (v : V) = 0 := by
  rw [Globalization.obstructionClass_zero_iff,
    obstruction_zero_iff_of_compatible _ _ _ v.2]
  rfl

/-- Compatible data mapped to their canonical orthogonal obstruction representative. -/
def harmonicFromKernel (h : delta.toLinearMap.comp A = 0) :
    LinearMap.ker delta.toLinearMap →ₗ[ℝ]
      harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) where
  toFun v := ⟨obstruction _ _ (v : V), obstruction_mem _ _ (range_le_kernel A delta h) v⟩
  map_add' x y := Subtype.ext ((obstruction _ _).map_add (x : V) (y : V))
  map_smul' a x := Subtype.ext ((obstruction _ _).map_smul a (x : V))

 theorem harmonicFromKernel_zero_iff (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    harmonicFromKernel A delta h v = 0 ↔
      v ∈ Globalization.realizationsInKernel A delta.toLinearMap := by
  rw [Subtype.ext_iff]
  change obstruction (LinearMap.range A) (LinearMap.ker delta.toLinearMap) (v : V) = 0 ↔
    (v : V) ∈ LinearMap.range A
  exact obstruction_zero_iff_of_compatible _ _ _ v.2

 theorem harmonicFromKernel_kernel (h : delta.toLinearMap.comp A = 0) :
    LinearMap.ker (harmonicFromKernel A delta h) =
      Globalization.realizationsInKernel A delta.toLinearMap := by
  ext v
  exact harmonicFromKernel_zero_iff A delta h v

/-- The map is defined on the quotient itself, not merely on chosen inputs. -/
def quotientToHarmonic (h : delta.toLinearMap.comp A = 0) :
    Globalization.ObstructionSpace A delta.toLinearMap →ₗ[ℝ]
      harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) :=
  (Globalization.realizationsInKernel A delta.toLinearMap).liftQ
    (harmonicFromKernel A delta h) (by rw [harmonicFromKernel_kernel])

/-- Include a harmonic vector in the compatible space and then take its class. -/
def harmonicToQuotient :
    harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) →ₗ[ℝ]
      Globalization.ObstructionSpace A delta.toLinearMap :=
  (Globalization.realizationsInKernel A delta.toLinearMap).mkQ.comp
    (Submodule.inclusion (show harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) ≤
      LinearMap.ker delta.toLinearMap from inf_le_left))

 theorem quotientToHarmonic_class (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    quotientToHarmonic A delta h (Globalization.obstructionClass A delta.toLinearMap v) =
      harmonicFromKernel A delta h v := rfl

 theorem harmonic_roundtrip (h : delta.toLinearMap.comp A = 0)
    (v : harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap)) :
    quotientToHarmonic A delta h (harmonicToQuotient A delta v) = v := by
  apply Subtype.ext
  exact obstruction_on_harmonic _ _ _ v.2

 theorem quotient_roundtrip (h : delta.toLinearMap.comp A = 0)
    (v : Globalization.ObstructionSpace A delta.toLinearMap) :
    harmonicToQuotient A delta (quotientToHarmonic A delta h v) = v := by
  refine Submodule.Quotient.induction_on _ v ?_
  intro x
  change (Submodule.Quotient.mk _ : Globalization.ObstructionSpace A delta.toLinearMap) =
    Submodule.Quotient.mk x
  apply (Submodule.Quotient.eq _).mpr
  change (obstruction (LinearMap.range A) (LinearMap.ker delta.toLinearMap) (x : V) - (x : V)) ∈
    LinearMap.range A
  change delta.ker.starProjection (x : V) - (LinearMap.range A).starProjection (x : V) - (x : V) ∈
    LinearMap.range A
  rw [Submodule.starProjection_eq_self_iff.mpr x.2]
  have he : (x : V) - (LinearMap.range A).starProjection (x : V) - (x : V) =
      -(LinearMap.range A).starProjection (x : V) := by abel
  rw [he]
  exact (LinearMap.range A).neg_mem ((LinearMap.range A).starProjection_apply_mem x)

/-- Algebraic obstruction classes have unique harmonic representatives. -/
def obstructionEquivHarmonic (h : delta.toLinearMap.comp A = 0) :
    Globalization.ObstructionSpace A delta.toLinearMap ≃ₗ[ℝ]
      harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) where
  toLinearMap := quotientToHarmonic A delta h
  invFun := harmonicToQuotient A delta
  left_inv := quotient_roundtrip A delta h
  right_inv := harmonic_roundtrip A delta h

 theorem harmonic_represents_class (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    harmonicToQuotient A delta (harmonicFromKernel A delta h v) =
      Globalization.obstructionClass A delta.toLinearMap v :=
  quotient_roundtrip A delta h (Globalization.obstructionClass A delta.toLinearMap v)

 theorem same_class_iff_same_harmonic (h : delta.toLinearMap.comp A = 0)
    (v w : LinearMap.ker delta.toLinearMap) :
    Globalization.obstructionClass A delta.toLinearMap v =
      Globalization.obstructionClass A delta.toLinearMap w ↔
      harmonicFromKernel A delta h v = harmonicFromKernel A delta h w := by
  exact (obstructionEquivHarmonic A delta h).injective.eq_iff.symm

end Komorebi.SufficientResolution.HilbertGlobalization
