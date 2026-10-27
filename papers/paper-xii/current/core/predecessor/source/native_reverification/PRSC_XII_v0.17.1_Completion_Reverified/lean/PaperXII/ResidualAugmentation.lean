import PaperXII.AuxiliaryGroupAlgebra
import PaperXII.LocalIdempotents
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.CharP.Algebra
import Mathlib.GroupTheory.PGroup
import Mathlib.RingTheory.Nilpotent.Basic

set_option autoImplicit false

/-! Paper XII, the locality conclusion of 5.2 and Corollary 5.3 in the
finite abelian p-group context of Section 5. The argument only needs an
abelian p-group; finiteness is unnecessary. Augmentation is the actual
group-algebra homomorphism, not an abstract residue map. -/
namespace PaperXII.ResidualAugmentation

open scoped MonoidAlgebra
open PaperXII.AuxiliaryGroupAlgebra

variable {k G : Type*} [Field k] [CommGroup G]
variable {p : ℕ} [Fact p.Prime] [CharP k p]

/-- Every group-basis difference is nilpotent in residue characteristic p. -/
theorem generator_nilpotent (hG : IsPGroup p G) (g : G) :
    IsNilpotent (MonoidAlgebra.single g (1 : k) - 1) := by
  let : CharP k[G] p := charP_of_injective_algebraMap (algebraMap k k[G]).injective p
  obtain ⟨n, hn⟩ := hG g
  refine ⟨p ^ n, ?_⟩
  rw [sub_pow_char_pow, MonoidAlgebra.single_pow, hn, one_pow, one_pow]
  simp [MonoidAlgebra.one_def]

/-- Subtracting the scalar augmentation leaves a nilpotent element. -/
theorem augmentation_difference_nilpotent (hG : IsPGroup p G) (x : k[G]) :
    IsNilpotent (x - algebraMap k k[G] (augmentation x)) := by
  induction x using MonoidAlgebra.induction_on with
  | of g =>
      simpa [augmentation_single, MonoidAlgebra.one_def] using
        generator_nilpotent (k := k) hG g
  | add x y hx hy =>
      simpa only [map_add, add_sub_add_comm] using
        (Commute.all _ _).isNilpotent_add hx hy
  | smul r x hx =>
      simpa only [map_smul, Algebra.algebraMap_eq_smul_one, smul_sub,
        smul_smul, smul_eq_mul] using hx.smul r

/-- The actual augmentation ideal consists of nilpotents. -/
theorem augmentation_kernel_nilpotent (hG : IsPGroup p G) (x : k[G])
    (hx : augmentation x = 0) : IsNilpotent x := by
  simpa [hx] using augmentation_difference_nilpotent hG x

/-- A group-algebra element is invertible exactly when its augmentation is nonzero. -/
theorem isUnit_iff_augmentation_ne_zero (hG : IsPGroup p G) (x : k[G]) :
    IsUnit x ↔ augmentation x ≠ 0 := by
  constructor
  · intro hx
    exact (hx.map augmentation.toMonoidHom).ne_zero
  · intro hx
    have hu : IsUnit (algebraMap k k[G] (augmentation x)) :=
      (isUnit_iff_ne_zero.mpr hx).map (algebraMap k k[G])
    simpa using (augmentation_difference_nilpotent hG x).isUnit_add_left_of_commute
      hu (Commute.all _ _)

/-- The residual group algebra is local. -/
theorem isLocalRing (hG : IsPGroup p G) : IsLocalRing k[G] := by
  apply IsLocalRing.of_isUnit_or_isUnit_one_sub_self
  intro x
  by_cases hx : augmentation x = 0
  · right
    apply (isUnit_iff_augmentation_ne_zero hG _).mpr
    simp [hx]
  · exact Or.inl ((isUnit_iff_augmentation_ne_zero hG x).mpr hx)

/-- Corollary 5.3: there are no nontrivial residual character projectors. -/
theorem idempotent_eq_zero_or_one (hG : IsPGroup p G) (e : k[G])
    (he : e * e = e) : e = 0 ∨ e = 1 := by
  let := isLocalRing (k := k) hG
  exact PaperXII.LocalIdempotents.eq_zero_or_one e he

end PaperXII.ResidualAugmentation
