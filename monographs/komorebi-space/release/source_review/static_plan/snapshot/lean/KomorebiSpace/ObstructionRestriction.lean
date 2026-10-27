import KomorebiSpace.SectionExactSequence

set_option autoImplicit false

/-!
# Restricting prescribed views and transporting their obstruction classes

If U is contained in W, the admissible-correction boundary for W is smaller.
Consequently Q_W maps canonically onto Q_U. Vanishing at W implies vanishing
at U, not conversely. All maps below use the actual view differential.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace AdditiveViewSystem
variable {V : Type u} [Category.{v} V]
variable {A : V → Type w} [∀ a, AddCommGroup (A a)]
variable (F : AdditiveViewSystem V A)

/-- Protecting more views permits fewer correction residuals. -/
theorem boundaries_antitone {U W : Set V} (h : U ⊆ W) :
    (F.problem W).boundaries ≤ (F.problem U).boundaries := by
  rintro r ⟨x,hx,hr⟩
  refine ⟨x,?_,hr⟩
  change F.observation U x = 0
  funext a
  exact congrFun hx (⟨a.val,h a.property⟩ : W)

/-- The canonical quotient homomorphism forgetting some protected views. -/
def forgetObstruction {U W : Set V} (h : U ⊆ W) :
    (F.problem W).Obstruction →+ (F.problem U).Obstruction :=
  QuotientAddGroup.map (F.problem W).boundaries (F.problem U).boundaries
    (AddMonoidHom.id _) (F.boundaries_antitone h)

@[simp] theorem forgetObstruction_class {U W : Set V} (h : U ⊆ W)
    (x : ∀ a, A a) :
    F.forgetObstruction h ((F.problem W).obstruction x) =
      (F.problem U).obstruction x := rfl

@[simp] theorem forgetObstruction_refl (U : Set V)
    (x : (F.problem U).Obstruction) :
    F.forgetObstruction (Set.Subset.refl U) x = x := by
  induction x using QuotientAddGroup.induction_on with
  | H x => rfl

theorem forgetObstruction_comp {U W Z : Set V} (h : U ⊆ W) (k : W ⊆ Z)
    (x : (F.problem Z).Obstruction) :
    F.forgetObstruction h (F.forgetObstruction k x) =
      F.forgetObstruction (h.trans k) x := by
  induction x using QuotientAddGroup.induction_on with
  | H x => rfl

/-- The map is onto as a map of obstruction groups. It need not be injective. -/
theorem forgetObstruction_surjective {U W : Set V} (h : U ⊆ W) :
    Function.Surjective (F.forgetObstruction h) := by
  intro x
  induction x using QuotientAddGroup.induction_on with
  | H r => exact ⟨(r : (F.problem W).Obstruction),rfl⟩

/-- Restriction of a partial realization transports its actual extension class. -/
theorem extensionClass_restrict {U W : Set V} (h : U ⊆ W)
    (s : F.views.Partial W) :
    F.forgetObstruction h (F.extensionClass W s) =
      F.extensionClass U (F.views.restrictPartial h s) := by
  change (F.problem U).obstruction (F.rawExtension W s) = _
  apply F.extensionClass_independent
  intro a
  exact F.rawExtension_observed W s ⟨a.val,h a.property⟩

/-- A genuinely obstructed restriction cannot be cured while preserving more data. -/
theorem obstruction_persists_under_prescription {U W : Set V} (h : U ⊆ W)
    (s : F.views.Partial W)
    (ho : F.extensionClass U (F.views.restrictPartial h s) ≠ 0) :
    F.extensionClass W s ≠ 0 := by
  intro hz
  apply ho
  rw [← F.extensionClass_restrict h s,hz,map_zero]

/-- Compatible extension to W implies compatible extension to every smaller U. -/
theorem vanishing_restricts {U W : Set V} (h : U ⊆ W)
    (s : F.views.Partial W) (ho : F.extensionClass W s = 0) :
    F.extensionClass U (F.views.restrictPartial h s) = 0 := by
  rw [← F.extensionClass_restrict h s,ho,map_zero]

end AdditiveViewSystem
end KomorebiSpace
