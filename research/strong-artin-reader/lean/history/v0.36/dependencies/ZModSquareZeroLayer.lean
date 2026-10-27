import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Group.Hom.Defs
import Mathlib.Tactic.Ring

/-! The actual mixed-characteristic additive layer.
For m != 0, multiplication by m identifies Z/p with the kernel Z/(mp) -> Z/m.
This is an additive equivalence, not a coefficient-ring section. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic

variable (p m : ℕ)

abbrev Upper := ZMod (m*p)
abbrev Lower := ZMod m

def reduction : Upper p m →+* Lower m :=
  ZMod.castHom (dvd_mul_right m p) (ZMod m)

def residue : Upper p m →+* ZMod p :=
  ZMod.castHom (dvd_mul_left p m) (ZMod p)

theorem reduction_surjective : Function.Surjective (reduction p m) :=
  ZMod.castHom_surjective _

def layerIntegerMap : ℤ →+ Upper p m where
  toFun z := (m : Upper p m) * (z : Upper p m)
  map_zero' := by simp
  map_add' a b := by simp [mul_add]

theorem layerIntegerMap_period : layerIntegerMap p m p = 0 := by
  change (m : ZMod (m*p)) * ((p : ℤ) : ZMod (m*p)) = 0
  simp only [Int.cast_natCast]
  rw [← Nat.cast_mul, ZMod.natCast_self]

def layerEmbedding : ZMod p →+ Upper p m :=
  ZMod.lift p ⟨layerIntegerMap p m, layerIntegerMap_period p m⟩

@[simp] theorem layerEmbedding_intCast (z : ℤ) :
    layerEmbedding p m (z : ZMod p) = (m : Upper p m) * (z : Upper p m) := by
  exact ZMod.lift_coe _ _ _

@[simp] theorem reduction_layerEmbedding (z : ZMod p) :
    reduction p m (layerEmbedding p m z) = 0 := by
  obtain ⟨a, rfl⟩ := ZMod.intCast_surjective z
  simp [reduction]

theorem layerEmbedding_injective (hm : m ≠ 0) :
    Function.Injective (layerEmbedding p m) := by
  apply (ZMod.lift_injective p).2
  intro z hz
  change (m : ZMod (m*p)) * (z : ZMod (m*p)) = 0 at hz
  have hz' : ((m : ℤ) * p) ∣ (m : ℤ) * z := by
    have := (ZMod.intCast_zmod_eq_zero_iff_dvd ((m : ℤ)*z) (m*p)).1
      (by simpa using hz)
    simpa using this
  have hd : (p : ℤ) ∣ z := (mul_dvd_mul_iff_left (by exact_mod_cast hm)).1 hz'
  exact (ZMod.intCast_zmod_eq_zero_iff_dvd z p).2 hd

theorem mem_kernel_iff_layerEmbedding (x : Upper p m) :
    reduction p m x = 0 ↔ ∃ z : ZMod p, layerEmbedding p m z = x := by
  constructor
  · obtain ⟨a, rfl⟩ := ZMod.intCast_surjective x
    intro ha
    have hm : (m : ℤ) ∣ a := (ZMod.intCast_zmod_eq_zero_iff_dvd a m).1
      (by simpa [reduction] using ha)
    obtain ⟨b, rfl⟩ := hm
    exact ⟨(b : ZMod p), by simp⟩
  · rintro ⟨z, rfl⟩
    exact reduction_layerEmbedding p m z

abbrev Layer := (reduction p m).toAddMonoidHom.ker

def layerEquiv (hm : m ≠ 0) : ZMod p ≃+ Layer p m :=
  AddEquiv.ofBijective
    (show ZMod p →+ Layer p m from
    { toFun := fun z => ⟨layerEmbedding p m z, reduction_layerEmbedding p m z⟩
      map_zero' := by apply Subtype.ext; exact map_zero _
      map_add' := by intro a b; apply Subtype.ext; exact map_add _ a b })
    ⟨fun a b h => layerEmbedding_injective p m hm (congrArg Subtype.val h),
      fun x => by
        obtain ⟨z,hz⟩ := (mem_kernel_iff_layerEmbedding p m x).1 x.property
        exact ⟨z, Subtype.ext hz⟩⟩

@[simp] theorem layerEquiv_val (hm : m ≠ 0) (z : ZMod p) :
    ((layerEquiv p m hm z : Layer p m) : Upper p m) = layerEmbedding p m z := rfl

/-- Multiplication on the layer depends only on the multiplier modulo p. -/
theorem mul_layerEmbedding (a : Upper p m) (z : ZMod p) :
    a * layerEmbedding p m z = layerEmbedding p m (residue p m a * z) := by
  obtain ⟨a, rfl⟩ := ZMod.intCast_surjective a
  obtain ⟨z, rfl⟩ := ZMod.intCast_surjective z
  simp only [layerEmbedding_intCast, map_intCast, ← Int.cast_mul]
  simp only [Int.cast_mul]
  ring

theorem layerEmbedding_mul (a : Upper p m) (z : ZMod p) :
    layerEmbedding p m z * a = layerEmbedding p m (z * residue p m a) := by
  rw [mul_comm, mul_layerEmbedding, mul_comm z]

theorem residue_layerEmbedding (hpm : p ∣ m) (z : ZMod p) :
    residue p m (layerEmbedding p m z) = 0 := by
  obtain ⟨z, rfl⟩ := ZMod.intCast_surjective z
  simp only [layerEmbedding_intCast, map_mul, map_natCast, map_intCast]
  rw [(ZMod.natCast_eq_zero_iff m p).2 hpm, zero_mul]

theorem reduction_squareZero (hpm : p ∣ m) (a b : Upper p m)
    (ha : reduction p m a = 0) (hb : reduction p m b = 0) : a*b=0 := by
  obtain ⟨x,rfl⟩ := (mem_kernel_iff_layerEmbedding p m a).1 ha
  obtain ⟨y,rfl⟩ := (mem_kernel_iff_layerEmbedding p m b).1 hb
  rw [mul_layerEmbedding, residue_layerEmbedding p m hpm, zero_mul, map_zero]

end Komorebi.StrongArtin.MixedCharacteristic
