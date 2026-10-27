import Mathlib.CategoryTheory.Linear.LinearFunctor
import Mathlib.CategoryTheory.Limits.Preserves.Basic

/-!
Paper I: typed equational realization.  The source expression is syntax, not
an assumed preservation theorem.  Evaluation commutes with a linear additive
functor by structural induction.  Universal constructions are transported only
under the corresponding mathlib preservation instance.
-/

set_option autoImplicit false

namespace Komorebi.PaperIRelease.CategoryExport

open CategoryTheory

universe u v w u' v' r

variable (R : Type r) (C : Type u) [Category.{v} C]

/-- Well-typed finite expressions over a declared family of generators. -/
inductive Expression (G : C → C → Type w) : C → C → Type (max u v w r) where
  | generator {X Y : C} : G X Y → Expression G X Y
  | identity (X : C) : Expression G X X
  | zero (X Y : C) : Expression G X Y
  | add {X Y : C} : Expression G X Y → Expression G X Y → Expression G X Y
  | neg {X Y : C} : Expression G X Y → Expression G X Y
  | scalar {X Y : C} : R → Expression G X Y → Expression G X Y
  | comp {X Y Z : C} : Expression G X Y → Expression G Y Z → Expression G X Z

variable {R C} [Semiring R] [Preadditive C] [CategoryTheory.Linear R C]
variable {G : C → C → Type w}

/-- Interpret source syntax using the specified primitive morphisms. -/
def evaluate (g : ∀ {X Y : C}, G X Y → (X ⟶ Y)) :
    {X Y : C} → Expression R C G X Y → (X ⟶ Y)
  | _, _, .generator a => g a
  | _, _, .identity X => 𝟙 X
  | _, _, .zero _ _ => 0
  | _, _, .add a b => evaluate g a + evaluate g b
  | _, _, .neg a => -evaluate g a
  | _, _, .scalar c a => c • evaluate g a
  | _, _, .comp a b => evaluate g a ≫ evaluate g b

variable {D : Type u'} [Category.{v'} D] [Preadditive D]
variable [CategoryTheory.Linear R D]

/-- Interpret the same source syntax after transporting its primitives. -/
def evaluateTransported (F : C ⥤ D)
    (g : ∀ {X Y : C}, G X Y → (X ⟶ Y)) :
    {X Y : C} → Expression R C G X Y → (F.obj X ⟶ F.obj Y)
  | _, _, .generator a => F.map (g a)
  | _, _, .identity X => 𝟙 (F.obj X)
  | _, _, .zero _ _ => 0
  | _, _, .add a b => evaluateTransported F g a + evaluateTransported F g b
  | _, _, .neg a => -evaluateTransported F g a
  | _, _, .scalar c a => c • evaluateTransported F g a
  | _, _, .comp a b => evaluateTransported F g a ≫ evaluateTransported F g b

/-- Every operation allowed by the declared syntax is transported. -/
theorem evaluate_transport (F : C ⥤ D) [F.Additive] [F.Linear R]
    (g : ∀ {X Y : C}, G X Y → (X ⟶ Y))
    {X Y : C} (e : Expression R C G X Y) :
    F.map (evaluate g e) = evaluateTransported F g e := by
  induction e with
  | generator => rfl
  | identity => simp [evaluate, evaluateTransported]
  | zero => simp [evaluate, evaluateTransported]
  | add a b ha hb => simp [evaluate, evaluateTransported, ha, hb]
  | neg a ha => simp [evaluate, evaluateTransported, ha]
  | scalar c a ha => simp [evaluate, evaluateTransported, ha]
  | comp a b ha hb => simp [evaluate, evaluateTransported, ha, hb]

/-- PSC-I-T-REALIZATION-EXPORT: a proved source equation gives its target equation. -/
theorem equation_transport (F : C ⥤ D) [F.Additive] [F.Linear R]
    (g : ∀ {X Y : C}, G X Y → (X ⟶ Y))
    {X Y : C} (a b : Expression R C G X Y)
    (h : evaluate g a = evaluate g b) :
    evaluateTransported F g a = evaluateTransported F g b := by
  rw [← evaluate_transport F g a, ← evaluate_transport F g b, h]

/-- Additive-only profiles obtain the same result using the canonical integer enrichment. -/
theorem additive_equation_transport
    {C₀ : Type u} {D₀ : Type u'} [Category.{v} C₀] [Category.{v'} D₀]
    [Preadditive C₀] [Preadditive D₀]
    (F : C₀ ⥤ D₀) [F.Additive] {G₀ : C₀ → C₀ → Type w}
    (g : ∀ {X Y : C₀}, G₀ X Y → (X ⟶ Y))
    {X Y : C₀} (a b : Expression ℤ C₀ G₀ X Y)
    (h : evaluate g a = evaluate g b) :
    evaluateTransported F g a = evaluateTransported F g b :=
  equation_transport F g a b h

open CategoryTheory.Limits

/-- Kernel, product and other limit diagrams pass under their declared preservation hypothesis. -/
noncomputable def transportLimit
    {J : Type*} [Category J] (K : J ⥤ C) (F : C ⥤ D)
    [PreservesLimit K F] (c : Cone K) (h : IsLimit c) :
    IsLimit (F.mapCone c) := isLimitOfPreserves F h

/-- Cokernel, quotient and other colimit diagrams use a separate preservation hypothesis. -/
noncomputable def transportColimit
    {J : Type*} [Category J] (K : J ⥤ C) (F : C ⥤ D)
    [PreservesColimit K F] (c : Cocone K) (h : IsColimit c) :
    IsColimit (F.mapCocone c) := isColimitOfPreserves F h

end Komorebi.PaperIRelease.CategoryExport
