import KomorebiSpace.AdjacentResolution
import KomorebiSpace.CofinalTransports
import KomorebiSpace.RealizationFaithfulness

set_option autoImplicit false

/-!
# Boundaries: transient strict information and nonfaithful realization

These examples show why we use finite-stage eventual agreement rather than
literal equality of strict presentations or equality of functions on limits.
-/

namespace KomorebiSpace
namespace ReindexingExamples
open Resolution

/-- Nonempty at every level, but there is no natural number at least every n. -/
def tails : Resolution where
  Obj n := {m : ℕ // n ≤ m}
  restrict := fun h x => ⟨x.val, h.trans x.property⟩
  restrict_refl := by intro n x; rfl
  restrict_trans := by intros; rfl

theorem tails_level_nonempty (n : ℕ) : Nonempty (tails.Obj n) :=
  ⟨⟨n, Nat.le_refl n⟩⟩

theorem tails_no_point (x : tails.Point) : False := by
  let m := (x.val 0).val
  have he := congrArg Subtype.val (x.property 0 (m+1) (Nat.zero_le _))
  have hb : m+1 ≤ (x.val (m+1)).val := (x.val (m+1)).property
  change (x.val (m+1)).val = m at he
  omega

def boolConstant : Resolution where
  Obj _ := Bool
  restrict := fun _ x => x
  restrict_refl := by intros; rfl
  restrict_trans := by intros; rfl

def constantToBool (b : Bool) : ReindexedMap tails boolConstant where
  level := fun n => n
  monotone := fun _ _ h => h
  app := fun _ _ => b
  naturality := by intros; rfl

theorem constants_not_eventually_equal :
    ¬ ReindexedMap.EventuallyEq (constantToBool false) (constantToBool true) := by
  intro h
  obtain ⟨k, hf, hg, hk⟩ := h 0
  have hbad : false = true := hk ⟨k, Nat.le_refl k⟩
  cases hbad

theorem distinct_classes_same_realization :
    EventualHom.mk (constantToBool false) ≠ EventualHom.mk (constantToBool true) ∧
    (EventualHom.mk (constantToBool false)).onLimit =
      (EventualHom.mk (constantToBool true)).onLimit := by
  constructor
  · intro h
    exact constants_not_eventually_equal
      ((EventualHom.mk_eq_iff _ _).mp h)
  · funext x
    exact False.elim (tails_no_point x)

/-- A single transient Boolean coordinate, absent at all subsequent levels. -/
def transientObj : ℕ → Type
  | 0 => Bool
  | _+1 => PUnit

def transientDown : ∀ n, transientObj (n+1) → transientObj n
  | 0 => fun _ => false
  | _+1 => fun x => x

def transient : Resolution := Adjacent.resolution transientObj transientDown

def eraseApp : ∀ n, transientObj n → transientObj n
  | 0 => fun _ => false
  | _+1 => fun x => x

def erase : Map transient transient := Adjacent.map eraseApp (by
  intro n x
  cases n <;> rfl)

theorem strict_maps_differ : Map.id transient ≠ erase := by
  intro h
  have hb := congrArg (fun f : Map transient transient => f.app 0 true) h
  change true = false at hb
  cases hb

theorem successor_monotone : Monotone Nat.succ := by
  intro i j h; omega

theorem successor_cofinal : UnboundedSchedule Nat.succ := by
  intro n; exact ⟨n, Nat.le_succ n⟩

/-- Literal strict maps can become equal after a cofinal schedule drops an initial level. -/
theorem sampled_strict_maps_equal :
    Map.sample (Map.id transient) Nat.succ successor_monotone =
    Map.sample erase Nat.succ successor_monotone := by
  apply Map.ext
  intro n x
  rfl

/-- In the eventual quotient the transient difference was already removed. -/
theorem transient_classes_equal :
    EventualHom.ofMap (Map.id transient) = EventualHom.ofMap erase := by
  apply (cofinalHomEquiv transient transient Nat.succ Nat.succ
    successor_monotone successor_monotone successor_cofinal successor_cofinal).injective
  rw [Map.sample_class, Map.sample_class, sampled_strict_maps_equal]

theorem strict_reindexing_not_injective :
    ¬ Function.Injective (fun f : Map transient transient =>
      Map.sample f Nat.succ successor_monotone) := by
  intro h
  exact strict_maps_differ (h sampled_strict_maps_equal)

end ReindexingExamples
end KomorebiSpace
