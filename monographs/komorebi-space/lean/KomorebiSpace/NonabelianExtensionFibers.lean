import KomorebiSpace.NonabelianExtension

set_option autoImplicit false

/-!
# Nonabelian extension fibers and invisible coherent changes

The action on trivializations is free and transitive when a base exists.
This must not be confused with the generally nontrivial stabilizers of
cocycle objects in the gauge groupoid.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

def invisible (U : Set V) : Subgroup (∀ v, G v) where
  carrier := {h | (∀ v w (f : v ⟶ w), F.pull f (h w) = h v) ∧ ∀ v : U, h v.val = 1}
  one_mem' := ⟨by intros; exact map_one _, by intros; rfl⟩
  mul_mem' := by
    intro a b ha hb
    constructor
    · intro v w f
      change F.pull f (a w * b w) = a v * b v
      rw [map_mul, ha.1, hb.1]
    · intro v
      change a v.val * b v.val = 1
      rw [ha.2 v, hb.2 v, one_mul]
  inv_mem' := by
    intro a ha
    constructor
    · intro v w f
      change F.pull f ((a w)⁻¹) = (a v)⁻¹
      rw [map_inv, ha.1]
    · intro v
      change (a v.val)⁻¹ = 1
      rw [ha.2 v, inv_one]

/-- The identity-label stabilizer is exactly the invisible coherent group. -/
def invisibleStabilizerEquiv (U : Set V) : F.invisible U ≃* F.stabilizer U F.trivial where
  toFun h := ⟨⟨h.val, h.property.2⟩, (F.trivial_stabilizer_iff U _).mpr h.property.1⟩
  invFun h := ⟨h.val.val, (F.trivial_stabilizer_iff U _).mp h.property, h.val.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_mul' _ _ := rfl

/-- A chosen twisted global extension parametrizes all the others by right multiplication. -/
def extensionParameters (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U)
    (base : (F.twistedViews c).Extensions U s) :
    F.invisible U ≃ (F.twistedViews c).Extensions U s where
  toFun h := ⟨⟨fun v => base.val.val v * h.val v, by
    intro v w f
    change c.edge f * F.pull f (base.val.val w * h.val w) = base.val.val v * h.val v
    rw [map_mul, ← mul_assoc]
    have hb := base.val.property v w f
    change c.edge f * F.pull f (base.val.val w) = base.val.val v at hb
    rw [hb, h.property.1]⟩, by
    apply ViewSystem.Partial.ext
    intro v
    change base.val.val v.val * h.val v.val = s.val v
    rw [h.property.2 v, mul_one]
    exact congrArg (fun t : (F.twistedViews c).Partial U => t.val v) base.property⟩
  invFun x := ⟨fun v => (base.val.val v)⁻¹ * x.val.val v, by
    constructor
    · intro v w f
      change F.pull f ((base.val.val w)⁻¹ * x.val.val w) = (base.val.val v)⁻¹ * x.val.val v
      rw [map_mul, map_inv]
      have hb := base.val.property v w f
      have hx := x.val.property v w f
      change c.edge f * F.pull f (base.val.val w) = base.val.val v at hb
      change c.edge f * F.pull f (x.val.val w) = x.val.val v at hx
      rw [← hb, ← hx]
      group
    · intro v
      change (base.val.val v.val)⁻¹ * x.val.val v.val = 1
      have hb := congrArg (fun t : (F.twistedViews c).Partial U => t.val v) base.property
      have hx := congrArg (fun t : (F.twistedViews c).Partial U => t.val v) x.property
      change base.val.val v.val = s.val v at hb
      change x.val.val v.val = s.val v at hx
      rw [hb, hx]; group⟩
  left_inv h := by apply Subtype.ext; funext v; change _⁻¹ * (_ * _) = _; group
  right_inv x := by
    apply Subtype.ext
    apply ViewSystem.Ambient.ext
    intro v
    change _ * (_⁻¹ * _) = _
    group

@[simp] theorem extensionParameters_coordinate (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (base : (F.twistedViews c).Extensions U s)
    (h : F.invisible U) (v : V) :
    (F.extensionParameters c U s base h).val.val v = base.val.val v * h.val v := rfl

@[simp] theorem extensionParameters_inverse (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (base x : (F.twistedViews c).Extensions U s) (v : V) :
    ((F.extensionParameters c U s base).symm x).val v = (base.val.val v)⁻¹ * x.val.val v := rfl

theorem extension_subsingleton_iff (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (base : (F.twistedViews c).Extensions U s) :
    Subsingleton ((F.twistedViews c).Extensions U s) ↔ Subsingleton (F.invisible U) :=
  (F.extensionParameters c U s base).subsingleton_congr.symm

theorem unique_extension_iff (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) :
    (∃! x : (F.twistedViews c).Ambient, (F.twistedViews c).restrict U x = s) ↔
      F.extensionOrbit c U s = F.neutralClass U ∧ Subsingleton (F.invisible U) := by
  constructor
  · rintro ⟨x, hx, hu⟩
    let base : (F.twistedViews c).Extensions U s := ⟨x, hx⟩
    refine ⟨(F.extensionOrbit_neutral_iff c U s).mpr ⟨base⟩, ?_⟩
    apply (F.extension_subsingleton_iff c U s base).mp
    refine ⟨fun a b => ?_⟩
    apply Subtype.ext
    exact (hu a.val a.property).trans (hu b.val b.property).symm
  · rintro ⟨ho, hh⟩
    obtain ⟨base⟩ := (F.extensionOrbit_neutral_iff c U s).mp ho
    have hs := (F.extension_subsingleton_iff c U s base).mpr hh
    refine ⟨base.val, base.property, ?_⟩
    intro x hx
    exact congrArg Subtype.val (hs.elim (⟨x, hx⟩ : (F.twistedViews c).Extensions U s) base)

theorem invisible_antitone {U W : Set V} (h : U ⊆ W) : F.invisible W ≤ F.invisible U := by
  intro a ha
  exact ⟨ha.1, fun v => ha.2 ⟨v.val, h v.property⟩⟩

end GroupViewSystem
end KomorebiSpace
