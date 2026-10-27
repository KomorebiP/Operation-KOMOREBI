import PaperXI.PacketSupport
import Mathlib.Dynamics.PeriodicPts.Lemmas
import Mathlib.GroupTheory.OrderOfElement

/-! Minimal return period, exact finite orbit size, and stabilizing powers. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FrobeniusPeriod
open PaperXI.FrobeniusOrbit
variable {M : ℕ}

def permutation (q : (ZMod M)ˣ) : Equiv.Perm (ZMod M) := Units.mulLeft q

def period (q : (ZMod M)ˣ) (j : ZMod M) : ℕ := Function.minimalPeriod (permutation q) j

theorem iterate_label (q : (ZMod M)ˣ) (j : ZMod M) (n : ℕ) :
    (permutation q)^[n] j = ((q ^ n : (ZMod M)ˣ) : ZMod M) * j := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Function.iterate_succ_apply']
    change (q : ZMod M) * ((permutation q)^[n] j) = _
    rw [ih, pow_succ']
    simp [mul_assoc]

variable [NeZero M]

theorem period_pos (q : (ZMod M)ˣ) (j : ZMod M) : 0 < period q j :=
  Function.minimalPeriod_pos_of_mem_periodicPts ((permutation q).injective.mem_periodicPts j)

theorem period_le (q : (ZMod M)ˣ) (j : ZMod M) : period q j ≤ M := by
  simpa [period] using (Function.minimalPeriod_le_card (f := permutation q) (x := j))

omit [NeZero M] in
theorem return_label (q : (ZMod M)ˣ) (j : ZMod M) :
    ((q ^ period q j : (ZMod M)ˣ) : ZMod M) * j = j := by
  have h := Function.isPeriodicPt_minimalPeriod (permutation q) j
  change (permutation q)^[period q j] j = j at h
  rwa [iterate_label] at h

omit [NeZero M] in
/-- A natural power fixes the label exactly when the minimal period divides it. -/
theorem stabilizing_power_iff (q : (ZMod M)ˣ) (j : ZMod M) (n : ℕ) :
    ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = j ↔ period q j ∣ n := by
  rw [← iterate_label]
  exact Function.isPeriodicPt_iff_minimalPeriod_dvd

omit [NeZero M] in
theorem no_short_return (q : (ZMod M)ˣ) (j : ZMod M) {n : ℕ}
    (hn : 0 < n) (hnf : n < period q j) :
    ((q ^ n : (ZMod M)ˣ) : ZMod M) * j ≠ j := by
  intro h
  exact (Nat.le_of_dvd hn ((stabilizing_power_iff q j n).mp h)).not_gt hnf

omit [NeZero M] in
theorem related_iff_nat (q : (ZMod M)ˣ) (j k : ZMod M) :
    Related q j k ↔ ∃ n : ℕ, ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = k := by
  constructor
  · rintro ⟨z, hz⟩
    have hm : q ^ z ∈ Subgroup.zpowers q := ⟨z, rfl⟩
    have hp := (isOfFinOrder_of_finite q).mem_powers_iff_mem_zpowers.mpr hm
    obtain ⟨n, hn⟩ := hp
    change q ^ n = q ^ z at hn
    exact ⟨n, by rw [hn]; exact hz⟩
  · rintro ⟨n, hn⟩
    exact ⟨n, by simpa using hn⟩

theorem related_iff_bounded (q : (ZMod M)ˣ) (j k : ZMod M) :
    Related q j k ↔ ∃ n : ℕ, n < period q j ∧
      ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = k := by
  rw [related_iff_nat]
  constructor
  · rintro ⟨n, hn⟩
    refine ⟨n % period q j, Nat.mod_lt _ (period_pos q j), ?_⟩
    rw [← iterate_label, period, Function.iterate_mod_minimalPeriod_eq, iterate_label, hn]
  · rintro ⟨n, _, hn⟩; exact ⟨n, hn⟩

/-- Index every orbit label exactly once by the minimal positive period. -/
def orbitEquiv (q : (ZMod M)ˣ) (j : ZMod M) :
    Fin (period q j) ≃ {k : ZMod M // Related q j k} :=
  Equiv.ofBijective
    (fun n => ⟨((q ^ (n : ℕ) : (ZMod M)ˣ) : ZMod M) * j,
      (related_iff_nat q j _).mpr ⟨n, rfl⟩⟩) (by
    constructor
    · intro a b hab
      apply Fin.ext
      apply Function.iterate_injOn_Iio_minimalPeriod a.isLt b.isLt
      simpa only [iterate_label] using congrArg Subtype.val hab
    · intro k
      obtain ⟨n, hn, hk⟩ := (related_iff_bounded q j k).mp k.property
      exact ⟨⟨n, hn⟩, Subtype.ext hk⟩)

theorem orbit_card (q : (ZMod M)ˣ) (j : ZMod M) :
    Nat.card {k : ZMod M // Related q j k} = period q j := by
  rw [← Nat.card_congr (orbitEquiv q j), Nat.card_fin]

end PaperXI.FrobeniusPeriod
