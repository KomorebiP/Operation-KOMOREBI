module
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Data.Nat.Log
public import Mathlib.GroupTheory.Coset.Card
public import Mathlib.LinearAlgebra.Finsupp.LinearCombination
public import Mathlib.Tactic

@[expose] public section
namespace Komorebi.Discovery

/-- Exact base-p digit length of an actual finite submodule. -/
noncomputable def primeRank (p r d : ℕ)
    (U : Submodule (ZMod (p^r)) (Fin d → ZMod (p^r))) : ℕ :=
  Nat.log p (Nat.card U)

theorem ambient_card (p r d : ℕ) (hp : Nat.Prime p) :
    Nat.card (Fin d → ZMod (p^r)) = p^(r*d) := by
  haveI : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [Nat.card_fun]
  simp only [Nat.card_eq_fintype_card, Fintype.card_fin, ZMod.card, pow_mul]

theorem submodule_card_power (p r d : ℕ) (hp : Nat.Prime p)
    (U : Submodule (ZMod (p^r)) (Fin d → ZMod (p^r))) :
    ∃ s ≤ r*d, Nat.card U = p^s := by
  have hc := U.toAddSubgroup.card_addSubgroup_dvd_card
  change Nat.card U ∣ Nat.card (Fin d → ZMod (p^r)) at hc
  rw [ambient_card p r d hp] at hc
  exact (Nat.dvd_prime_pow hp).mp hc

theorem primeRank_bound (p r d : ℕ) (hp : Nat.Prime p)
    (U : Submodule (ZMod (p^r)) (Fin d → ZMod (p^r))) :
    primeRank p r d U ≤ r*d := by
  obtain ⟨s,hs,hc⟩ := submodule_card_power p r d hp U
  simpa only [primeRank, hc, Nat.log_pow hp.one_lt] using hs

theorem card_eq_pow_primeRank (p r d : ℕ) (hp : Nat.Prime p)
    (U : Submodule (ZMod (p^r)) (Fin d → ZMod (p^r))) :
    Nat.card U = p^(primeRank p r d U) := by
  obtain ⟨s,_,hc⟩ := submodule_card_power p r d hp U
  simp only [primeRank, hc, Nat.log_pow hp.one_lt]

theorem primeRank_strictMono (p r d : ℕ) (hp : Nat.Prime p) :
    StrictMono (primeRank p r d) := by
  haveI : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  intro U V huv
  have hcard : Nat.card U < Nat.card V := by
    exact Set.ncard_lt_ncard (SetLike.coe_ssubset_coe.mpr huv)
  rw [card_eq_pow_primeRank p r d hp U, card_eq_pow_primeRank p r d hp V] at hcard
  exact (Nat.pow_lt_pow_iff_right hp.one_lt).mp hcard

theorem primeRank_bot (p r d : ℕ) :
    primeRank p r d (⊥ : Submodule (ZMod (p^r)) (Fin d → ZMod (p^r))) = 0 := by
  simp [primeRank]

end Komorebi.Discovery
