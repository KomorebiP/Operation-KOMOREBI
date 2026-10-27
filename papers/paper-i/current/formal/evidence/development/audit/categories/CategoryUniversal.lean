import PaperIRelease.CategoryExport
import Mathlib.CategoryTheory.Limits.Preserves.Shapes.Terminal

/-!
Universal-construction part of the realization profile.

A tensor product can be represented as an initial object of its category of
bilinear maps; a completion as an initial complete target of the specified
continuous/uniform map. To use either construction, the declared profile must
supply the appropriate structured categories, an induced functor on them,
its compatibility with the underlying realization functor, and actual
preservation evidence. No tensor or completion preservation is inferred from
additivity alone. The theorems below transport the universal object and its
uniquely induced morphisms from exactly those conditional inputs.
-/

set_option autoImplicit false

noncomputable section

namespace Komorebi.PaperIRelease.CategoryExport

open CategoryTheory CategoryTheory.Limits

universe u v u' v' uS vS uT vT
variable {C : Type u} [Category.{v} C]
variable {D : Type u'} [Category.{v'} D]

/-- Preserve an initial universal object under the declared preservation instance. -/
def transportInitial (F : C ⥤ D) [PreservesColimit (Functor.empty.{0} C) F]
    {X : C} (hX : IsInitial X) : IsInitial (F.obj X) :=
  hX.isInitialObj F X

/-- The uniquely induced arrow is transported, rather than supplied as an assumption. -/
theorem transportInitial_map (F : C ⥤ D) [PreservesColimit (Functor.empty.{0} C) F]
    {X : C} (hX : IsInitial X) (Y : C) :
    F.map (hX.to Y) = (transportInitial F hX).to (F.obj Y) :=
  (transportInitial F hX).hom_ext _ _

/-- Preserve a terminal universal object under the declared preservation instance. -/
def transportTerminal (F : C ⥤ D) [PreservesLimit (Functor.empty.{0} C) F]
    {X : C} (hX : IsTerminal X) : IsTerminal (F.obj X) :=
  hX.isTerminalObj F X

/-- The uniquely induced arrow into a terminal universal object is transported. -/
theorem transportTerminal_map (F : C ⥤ D) [PreservesLimit (Functor.empty.{0} C) F]
    {X : C} (hX : IsTerminal X) (Y : C) :
    F.map (hX.from Y) = (transportTerminal F hX).from (F.obj Y) :=
  (transportTerminal F hX).hom_ext _ _

variable {S : Type uS} [Category.{vS} S]
variable {T : Type uT} [Category.{vT} T]

/-- A profile's induced structured functor and underlying compatibility isomorphism
carry the actual initial-object arrow diagram to the realized category. -/
theorem transportInitial_underlying
    (F : C ⥤ D) (US : S ⥤ C) (UT : T ⥤ D) (G : S ⥤ T)
    [PreservesColimit (Functor.empty.{0} S) G]
    (comparison : G ⋙ UT ≅ US ⋙ F) {X : S} (hX : IsInitial X) (Y : S) :
    UT.map ((transportInitial G hX).to (G.obj Y)) ≫ comparison.hom.app Y =
      comparison.hom.app X ≫ F.map (US.map (hX.to Y)) := by
  rw [← transportInitial_map G hX Y]
  exact comparison.hom.naturality (hX.to Y)

/-- The dual terminal-object comparison diagram, with the same explicit profile data. -/
theorem transportTerminal_underlying
    (F : C ⥤ D) (US : S ⥤ C) (UT : T ⥤ D) (G : S ⥤ T)
    [PreservesLimit (Functor.empty.{0} S) G]
    (comparison : G ⋙ UT ≅ US ⋙ F) {X : S} (hX : IsTerminal X) (Y : S) :
    UT.map ((transportTerminal G hX).from (G.obj Y)) ≫ comparison.hom.app X =
      comparison.hom.app Y ≫ F.map (US.map (hX.from Y)) := by
  rw [← transportTerminal_map G hX Y]
  exact comparison.hom.naturality (hX.from Y)

end Komorebi.PaperIRelease.CategoryExport
