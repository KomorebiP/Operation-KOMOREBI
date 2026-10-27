import KomorebiSpace.GroupViewSystems
import Mathlib.CategoryTheory.Groupoid

set_option autoImplicit false

/-!
# The groupoid of cocycles and framed gauge changes

Gauge changes are identity on a prescribed view domain. The orbit quotient
forgets automorphisms; the groupoid deliberately retains them. Its objects
are coherent cocycles, not arbitrary inconsistent transition labels.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

/-- Allowed gauge changes keep every prescribed local trivialization fixed. -/
def basedGauge (_F : GroupViewSystem V G) (U : Set V) : Subgroup (∀ v, G v) where
  carrier := {a | ∀ v : U, a v.val = 1}
  one_mem' := by intro v; rfl
  mul_mem' := by intro a b ha hb v; change a v.val * b v.val = 1; rw [ha v, hb v, one_mul]
  inv_mem' := by intro a ha v; change (a v.val)⁻¹ = 1; rw [ha v, inv_one]

/-- A wrapper keeps the framing domain visible to typeclass inference. -/
structure GaugeObject (U : Set V) where
  labels : F.Cocycle

namespace GaugeObject
variable {F} {U : Set V}
structure Hom (c d : F.GaugeObject U) where
  change : F.basedGauge U
  target : F.gauge change.val c.labels = d.labels

@[ext] theorem Hom.ext {c d : F.GaugeObject U} {a b : Hom c d}
    (h : a.change = b.change) : a = b := by cases a; cases b; cases h; rfl

def identity (c : F.GaugeObject U) : Hom c c :=
  ⟨1, F.gauge_one c.labels⟩

def compose {c d e : F.GaugeObject U} (a : Hom c d) (b : Hom d e) : Hom c e :=
  ⟨b.change * a.change, by
    change F.gauge (b.change.val * a.change.val) c.labels = e.labels
    rw [← F.gauge_mul, a.target, b.target]⟩

def reverse {c d : F.GaugeObject U} (a : Hom c d) : Hom d c :=
  ⟨a.change⁻¹, by
    change F.gauge a.change.val⁻¹ d.labels = c.labels
    rw [← a.target, F.gauge_inv_gauge]⟩

instance : Groupoid (F.GaugeObject U) where
  Hom := Hom
  id := identity
  comp := compose
  id_comp := by intro c d a; apply Hom.ext; exact mul_one _
  comp_id := by intro c d a; apply Hom.ext; exact one_mul _
  assoc := by intro b c d e a h k; apply Hom.ext; exact (mul_assoc _ _ _).symm
  inv := reverse
  inv_comp := by intro c d a; apply Hom.ext; exact mul_inv_cancel _
  comp_inv := by intro c d a; apply Hom.ext; exact inv_mul_cancel _

@[simp] theorem composition_change {c d e : F.GaugeObject U}
    (a : c ⟶ d) (b : d ⟶ e) : (a ≫ b).change = b.change * a.change := rfl

@[simp] theorem inverse_change {c d : F.GaugeObject U} (a : c ⟶ d) :
    (Groupoid.inv a).change = a.change⁻¹ := rfl
end GaugeObject

/-- Explicit orbit relation. This is not defined by solvability of an extension. -/
def GaugeEquivalent (U : Set V) (c d : F.Cocycle) : Prop :=
  ∃ a : F.basedGauge U, F.gauge a.val c = d

theorem gaugeEquivalent_refl (U : Set V) (c : F.Cocycle) : F.GaugeEquivalent U c c :=
  ⟨1, F.gauge_one c⟩

theorem gaugeEquivalent_symm {U : Set V} {c d : F.Cocycle}
    (h : F.GaugeEquivalent U c d) : F.GaugeEquivalent U d c := by
  obtain ⟨a, ha⟩ := h
  refine ⟨a⁻¹, ?_⟩
  change F.gauge a.val⁻¹ d = c
  rw [← ha, F.gauge_inv_gauge]

theorem gaugeEquivalent_trans {U : Set V} {c d e : F.Cocycle}
    (h : F.GaugeEquivalent U c d) (k : F.GaugeEquivalent U d e) :
    F.GaugeEquivalent U c e := by
  obtain ⟨a, ha⟩ := h
  obtain ⟨b, hb⟩ := k
  refine ⟨b * a, ?_⟩
  change F.gauge (b.val * a.val) c = e
  rw [← F.gauge_mul, ha, hb]

def gaugeSetoid (U : Set V) : Setoid F.Cocycle where
  r := F.GaugeEquivalent U
  iseqv := ⟨F.gaugeEquivalent_refl U, F.gaugeEquivalent_symm, F.gaugeEquivalent_trans⟩

/-- A pointed orbit set; no group operation is asserted in the noncommutative case. -/
def Orbit (U : Set V) := Quotient (F.gaugeSetoid U)

def orbitClass (U : Set V) (c : F.Cocycle) : F.Orbit U := Quotient.mk _ c

def neutralClass (U : Set V) : F.Orbit U := F.orbitClass U F.trivial

theorem orbitClass_eq_iff (U : Set V) (c d : F.Cocycle) :
    F.orbitClass U c = F.orbitClass U d ↔ F.GaugeEquivalent U c d :=
  Quotient.eq

theorem morphism_nonempty_iff_class (U : Set V) (c d : F.GaugeObject U) :
    Nonempty (c ⟶ d) ↔ F.orbitClass U c.labels = F.orbitClass U d.labels := by
  rw [F.orbitClass_eq_iff]
  constructor
  · rintro ⟨a⟩; exact ⟨a.change, a.target⟩
  · rintro ⟨a, ha⟩; exact ⟨⟨a, ha⟩⟩

theorem iso_nonempty_iff_class (U : Set V) (c d : F.GaugeObject U) :
    Nonempty (c ≅ d) ↔ F.orbitClass U c.labels = F.orbitClass U d.labels := by
  rw [← F.morphism_nonempty_iff_class]
  constructor
  · rintro ⟨a⟩; exact ⟨a.hom⟩
  · rintro ⟨a⟩; exact ⟨(Groupoid.isoEquivHom c d).symm a⟩

/-- Automorphisms are the stabilizer, not an additional set of inequivalent objects. -/
def stabilizer (U : Set V) (c : F.Cocycle) : Subgroup (F.basedGauge U) where
  carrier := {a | F.gauge a.val c = c}
  one_mem' := F.gauge_one c
  mul_mem' := by
    intro a b ha hb
    change F.gauge (a.val * b.val) c = c
    rw [← F.gauge_mul, hb, ha]
  inv_mem' := by
    intro a ha
    change F.gauge a.val⁻¹ c = c
    calc
      _ = F.gauge a.val⁻¹ (F.gauge a.val c) := by rw [ha]
      _ = c := F.gauge_inv_gauge a.val c

theorem stabilizer_characterization (U : Set V) (c : F.Cocycle) (a : F.basedGauge U) :
    a ∈ F.stabilizer U c ↔
      ∀ v w (f : v ⟶ w), a.val v = c.edge f * F.pull f (a.val w) * (c.edge f)⁻¹ := by
  constructor
  · intro h v w f
    have he := congrArg (fun t : F.Cocycle => t.edge f) h
    change a.val v * c.edge f * (F.pull f (a.val w))⁻¹ = c.edge f at he
    calc
      _ = (a.val v * c.edge f * (F.pull f (a.val w))⁻¹) *
        F.pull f (a.val w) * (c.edge f)⁻¹ := by group
      _ = _ := by rw [he]
  · intro h
    apply Cocycle.ext
    intro v w f
    change a.val v * c.edge f * (F.pull f (a.val w))⁻¹ = c.edge f
    rw [h v w f]
    group

theorem trivial_stabilizer_iff (U : Set V) (a : F.basedGauge U) :
    a ∈ F.stabilizer U F.trivial ↔
      ∀ v w (f : v ⟶ w), F.pull f (a.val w) = a.val v := by
  rw [F.stabilizer_characterization]
  simp only [trivial, one_mul, inv_one, mul_one]
  exact forall_congr' (fun _ => forall_congr' (fun _ => forall_congr' (fun _ => eq_comm)))

/-- Fixing one arrow parametrizes every other arrow by a source automorphism. -/
def morphismParameters (U : Set V) {c d : F.GaugeObject U} (a : c ⟶ d) :
    F.stabilizer U c.labels ≃ (c ⟶ d) where
  toFun h := ⟨a.change * h.val, by
    change F.gauge (a.change.val * h.val.val) c.labels = d.labels
    rw [← F.gauge_mul, h.property, a.target]⟩
  invFun b := ⟨a.change⁻¹ * b.change, by
    change F.gauge (a.change.val⁻¹ * b.change.val) c.labels = c.labels
    rw [← F.gauge_mul, b.target, ← a.target, F.gauge_inv_gauge]⟩
  left_inv h := by apply Subtype.ext; change _⁻¹ * (_ * _) = _; group
  right_inv b := by apply GaugeObject.Hom.ext; change _ * (_⁻¹ * _) = _; group

theorem morphism_unique_iff_stabilizer (U : Set V) {c d : F.GaugeObject U} (a : c ⟶ d) :
    Subsingleton (c ⟶ d) ↔ Subsingleton (F.stabilizer U c.labels) :=
  (F.morphismParameters U a).subsingleton_congr.symm

end GroupViewSystem
end KomorebiSpace
