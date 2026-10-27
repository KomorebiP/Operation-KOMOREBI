module
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Tactic.Ring
public import Mathlib.Data.Fintype.Card

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.ResidueLiftDigits

variable {d : ℕ}

/-- Correction classes modulo q are precisely the classes of shifted integers
modulo q^(L+1). This includes q=1 and L=0. -/
theorem shift_cast_eq_iff (q L : ℕ) (hq : 0 < q) (x s t : ℤ) :
    ((x + (q : ℤ)^L * s : ℤ) : ZMod (q^(L+1))) =
      ((x + (q : ℤ)^L * t : ℤ) : ZMod (q^(L+1))) ↔
    (s : ZMod q) = (t : ZMod q) := by
  rw [ZMod.intCast_eq_intCast_iff_dvd_sub,
    ZMod.intCast_eq_intCast_iff_dvd_sub]
  have hqL : (q : ℤ)^L ≠ 0 :=
    pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hq))
  rw [show (x + (q : ℤ)^L * t) - (x + (q : ℤ)^L * s) =
    (q : ℤ)^L * (t - s) by ring]
  rw [Nat.cast_pow, pow_succ, mul_dvd_mul_iff_left hqL]

/-- Actual residue vectors at the next level lying over the prescribed
integer vector x. The predicate uses canonical integer representatives. -/
abbrev ResidueFiber (q L : ℕ) (x : Fin d → ℤ) :=
  {y : Fin d → ZMod (q^(L+1)) //
    ∀ i, (q : ℤ)^L ∣ ((y i).val : ℤ) - x i}

/-- The actual next residue represented by a correction digit. -/
def digitResidue (q L : ℕ) (x : Fin d → ℤ) (t : Fin d → ZMod q) :
    Fin d → ZMod (q^(L+1)) :=
  fun i => ((x i + (q : ℤ)^L * ((t i).val : ℤ) : ℤ) : ZMod (q^(L+1)))

theorem digitResidue_mem (q L : ℕ) (hq : 0 < q)
    (x : Fin d → ℤ) (t : Fin d → ZMod q) :
    ∀ i, (q : ℤ)^L ∣ ((digitResidue q L x t i).val : ℤ) - x i := by
  let : NeZero (q^(L+1)) := ⟨pow_ne_zero _ (Nat.ne_of_gt hq)⟩
  intro i
  have heq : (((digitResidue q L x t i).val : ℤ) : ZMod (q^(L+1))) =
      ((x i + (q : ℤ)^L * ((t i).val : ℤ) : ℤ) : ZMod (q^(L+1))) := by
    simp [digitResidue]
  have hlarge := (ZMod.intCast_eq_intCast_iff_dvd_sub _ _ (q^(L+1))).mp heq
  rw [Nat.cast_pow] at hlarge
  have hlower : (q : ℤ)^L ∣
      (x i + (q : ℤ)^L * ((t i).val : ℤ)) - ((digitResidue q L x t i).val : ℤ) :=
    dvd_trans (pow_dvd_pow (q : ℤ) (Nat.le_succ L)) hlarge
  have hsum := dvd_sub (dvd_mul_right ((q : ℤ)^L) ((t i).val : ℤ)) hlower
  have hid : (q : ℤ)^L * ((t i).val : ℤ) -
      ((x i + (q : ℤ)^L * ((t i).val : ℤ)) - ((digitResidue q L x t i).val : ℤ)) =
      ((digitResidue q L x t i).val : ℤ) - x i := by ring
  rwa [hid] at hsum

theorem digitResidue_injective (q L : ℕ) (hq : 0 < q) (x : Fin d → ℤ) :
    Function.Injective (digitResidue q L x) := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  intro s t h
  funext i
  have hi := (shift_cast_eq_iff q L hq (x i)
    ((s i).val : ℤ) ((t i).val : ℤ)).mp (congrFun h i)
  simpa using hi

theorem digitResidue_surjective (q L : ℕ) (hq : 0 < q) (x : Fin d → ℤ)
    (y : ResidueFiber q L x) :
    ∃ t : Fin d → ZMod q, digitResidue q L x t = y.val := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  let : NeZero (q^(L+1)) := ⟨pow_ne_zero _ (Nat.ne_of_gt hq)⟩
  choose s hs using y.property
  refine ⟨fun i => (s i : ZMod q), ?_⟩
  funext i
  have hi := (shift_cast_eq_iff q L hq (x i)
    (((s i : ZMod q)).val : ℤ) (s i)).mpr (by simp)
  change digitResidue q L x (fun i => (s i : ZMod q)) i = _ at hi
  rw [hi]
  have hy : x i + (q : ℤ)^L * s i = ((y.val i).val : ℤ) := by
    have hh := hs i
    exact (sub_eq_iff_eq_add'.mp hh).symm
  rw [hy]
  simp

/-- All q^d correction digit vectors bijectively parametrize the actual
next-level residue vectors over x. Integer corrections themselves are not
counted: they have infinitely many representatives. -/
def digitEquivResidue (q L : ℕ) (hq : 0 < q) (x : Fin d → ℤ) :
    (Fin d → ZMod q) ≃ ResidueFiber q L x :=
  Equiv.ofBijective
    (fun t => ⟨digitResidue q L x t, digitResidue_mem q L hq x t⟩)
    ⟨fun _ _ h => digitResidue_injective q L hq x (congrArg Subtype.val h),
      fun y => by
        obtain ⟨t, ht⟩ := digitResidue_surjective q L hq x y
        exact ⟨t, Subtype.ext ht⟩⟩

@[simp] theorem digitEquivResidue_apply (q L : ℕ) (hq : 0 < q)
    (x : Fin d → ℤ) (t : Fin d → ZMod q) :
    (digitEquivResidue q L hq x t).val = digitResidue q L x t := rfl

/-- The canonical representative of an actual digit residue differs from
its shifted integer representative by a multiple of the full next modulus. -/
theorem next_modulus_dvd_val_sub_shift (q L : ℕ) (hq : 0 < q)
    (x : Fin d → ℤ) (t : Fin d → ZMod q) (i : Fin d) :
    (q : ℤ)^(L+1) ∣
      (((digitEquivResidue q L hq x t).val i).val : ℤ) -
        (x i + (q : ℤ)^L * ((t i).val : ℤ)) := by
  let : NeZero (q^(L+1)) := ⟨pow_ne_zero _ (Nat.ne_of_gt hq)⟩
  have heq : ((x i + (q : ℤ)^L * ((t i).val : ℤ) : ℤ) : ZMod (q^(L+1))) =
      ((((digitEquivResidue q L hq x t).val i).val : ℤ) : ZMod (q^(L+1))) := by
    simp [digitEquivResidue_apply, digitResidue]
  have h := (ZMod.intCast_eq_intCast_iff_dvd_sub _ _ (q^(L+1))).mp heq
  simpa only [Nat.cast_pow] using h

/-- Exactly q^d distinct next residue vectors lie above each lower residue,
including the degenerate modulus q=1 and the zero-dimensional case. -/
theorem residueFiber_card (q L : ℕ) (hq : 0 < q) (x : Fin d → ℤ) :
    Nat.card (ResidueFiber q L x) = q^d := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  rw [← Nat.card_congr (digitEquivResidue q L hq x)]
  simp [Nat.card_eq_fintype_card]

#print axioms shift_cast_eq_iff
#print axioms ResidueFiber
#print axioms digitResidue
#print axioms digitResidue_mem
#print axioms digitResidue_injective
#print axioms digitResidue_surjective
#print axioms digitEquivResidue
#print axioms digitEquivResidue_apply
#print axioms next_modulus_dvd_val_sub_shift
#print axioms residueFiber_card

end Komorebi.ResidueLiftDigits
