import Mathlib.Data.ZMod.Basic
import Mathlib.RingTheory.Ideal.Span
import Mathlib.Data.Finset.Lattice.Fold
import Lean.Elab.Tactic.Omega

/-! # Prime-power coordinate ideals
Capped order assigns r to zero. Capacity c denotes p^(r-c)R.
-/
namespace KomorebiPadic
namespace PrimePowerIdeal

def powerIdeal (p r a : ℕ) : Ideal (ZMod (p^r)) := Ideal.span { (p : ZMod (p^r))^a }

theorem mem_powerIdeal_iff {p r a : ℕ} (hp : 0 < p) (ha : a ≤ r)
    (x : ZMod (p^r)) : x ∈ powerIdeal p r a ↔ p^a ∣ x.val := by
  let : NeZero (p^r) := ⟨ne_of_gt (pow_pos hp _)⟩
  rw [powerIdeal, Ideal.mem_span_singleton]
  constructor
  · rintro ⟨y, rfl⟩
    rw [ZMod.val_mul, ← Nat.cast_pow, ZMod.val_natCast]
    apply (Nat.dvd_mod_iff (pow_dvd_pow p ha)).mpr
    exact dvd_mul_of_dvd_left ((Nat.dvd_mod_iff (pow_dvd_pow p ha)).mpr (dvd_refl _)) _
  · rintro ⟨y, hy⟩
    refine ⟨(y : ZMod (p^r)), ?_⟩
    rw [← ZMod.natCast_zmod_val x, hy]
    simp

theorem powerIdeal_antitone (p r : ℕ) : Antitone (powerIdeal p r) := by
  intro a b hab
  rw [powerIdeal, Ideal.span_singleton_le_iff_mem, powerIdeal, Ideal.mem_span_singleton]
  exact pow_dvd_pow _ hab

@[simp] theorem powerIdeal_zero (p r : ℕ) : powerIdeal p r 0 = ⊤ := by simp [powerIdeal]
@[simp] theorem powerIdeal_precision (p r : ℕ) : powerIdeal p r r = ⊥ := by
  have hz : (p : ZMod (p^r))^r = 0 := by rw [← Nat.cast_pow, ZMod.natCast_self]
  simp [powerIdeal, hz]

def order (p r : ℕ) (x : ZMod (p^r)) : ℕ :=
  ((Finset.range (r+1)).filter (fun a => p^a ∣ x.val)).sup id

theorem order_le (p r : ℕ) (x : ZMod (p^r)) : order p r x ≤ r := by
  apply Finset.sup_le
  intro a ha
  have := (Finset.mem_filter.mp ha).1
  exact Nat.le_of_lt_succ (Finset.mem_range.mp this)

theorem order_spec {p r a : ℕ} (ha : a ≤ r) (x : ZMod (p^r)) :
    a ≤ order p r x ↔ p^a ∣ x.val := by
  constructor
  · intro h
    by_cases haz : a = 0
    · simp [haz]
    · obtain ⟨b, hb, hab⟩ := (Finset.le_sup_iff (Nat.pos_of_ne_zero haz)).mp h
      exact (pow_dvd_pow p hab).trans (Finset.mem_filter.mp hb).2
  · intro h
    exact Finset.le_sup (f := id) (Finset.mem_filter.mpr ⟨Finset.mem_range.mpr (Nat.lt_succ_of_le ha), h⟩)

theorem order_mem_iff {p r a : ℕ} (hp : 0 < p) (ha : a ≤ r) (x : ZMod (p^r)) :
    x ∈ powerIdeal p r a ↔ a ≤ order p r x := by
  rw [mem_powerIdeal_iff hp ha, order_spec ha]

def capacity (p r : ℕ) (x : ZMod (p^r)) : ℕ := r - order p r x

def capacityIdeal (p r n : ℕ) : Ideal (ZMod (p^r)) := powerIdeal p r (r-n)

theorem capacity_le (p r : ℕ) (x : ZMod (p^r)) : capacity p r x ≤ r := Nat.sub_le _ _

theorem capacity_le_iff {p r n : ℕ} (hp : 0 < p) (x : ZMod (p^r)) :
    capacity p r x ≤ n ↔ x ∈ capacityIdeal p r n := by
  rw [capacityIdeal, order_mem_iff hp (Nat.sub_le _ _)]
  unfold capacity
  omega

theorem capacityIdeal_mono (p r : ℕ) : Monotone (capacityIdeal p r) := by
  intro n m h
  exact powerIdeal_antitone p r (Nat.sub_le_sub_left h r)

@[simp] theorem capacityIdeal_zero (p r : ℕ) : capacityIdeal p r 0 = ⊥ := by simp [capacityIdeal]
@[simp] theorem capacityIdeal_full (p r : ℕ) : capacityIdeal p r r = ⊤ := by simp [capacityIdeal]

@[simp] theorem capacity_zero (p r : ℕ) : capacity p r (0 : ZMod (p^r)) = 0 := by
  have hl := (order_spec (le_refl r) (0 : ZMod (p^r))).mpr (by simp)
  unfold capacity
  omega

def transfer (p r : ℕ) (t : ZMod (p^r)) (n : ℕ) : ℕ :=
  capacity p r ((p : ZMod (p^r))^(r-n) * t)

theorem transfer_le (p r : ℕ) (t : ZMod (p^r)) (n : ℕ) : transfer p r t n ≤ r := capacity_le p r _

theorem mul_mem_of_generator {p r n m : ℕ} (t : ZMod (p^r))
    (ht : (p : ZMod (p^r))^(r-n)*t ∈ capacityIdeal p r m)
    {x : ZMod (p^r)} (hx : x ∈ capacityIdeal p r n) : x*t ∈ capacityIdeal p r m := by
  obtain ⟨y, hy⟩ := Ideal.mem_span_singleton'.mp hx
  rw [← hy]
  have h := (capacityIdeal p r m).mul_mem_left y ht
  simpa only [mul_assoc] using h

theorem transfer_spec {p r n m : ℕ} (hp : 0 < p) (t : ZMod (p^r)) :
    transfer p r t n ≤ m ↔ ∀ x ∈ capacityIdeal p r n, x*t ∈ capacityIdeal p r m := by
  rw [transfer, capacity_le_iff hp]
  constructor
  · exact fun h x hx => mul_mem_of_generator t h hx
  · intro h
    apply h
    exact Ideal.mem_span_singleton_self _

theorem transfer_mono {p r : ℕ} (hp : 0 < p) (t : ZMod (p^r)) : Monotone (transfer p r t) := by
  intro n m hnm
  apply (transfer_spec hp t).mpr
  intro x hx
  exact (transfer_spec hp t).mp le_rfl x (capacityIdeal_mono p r hnm hx)

@[simp] theorem transfer_zero (p r : ℕ) (t : ZMod (p^r)) : transfer p r t 0 = 0 := by
  unfold transfer
  have hz : (p : ZMod (p^r))^r = 0 := by rw [← Nat.cast_pow, ZMod.natCast_self]
  simp [hz]

end PrimePowerIdeal
end KomorebiPadic
