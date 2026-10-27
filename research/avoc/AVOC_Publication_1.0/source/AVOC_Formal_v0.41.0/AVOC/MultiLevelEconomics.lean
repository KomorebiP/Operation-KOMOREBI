import AVOC.MultiLevelRank
import AVOC.AffineSearchGuard

namespace Komorebi.AVOC.Affine.MultiLevelEconomics

open Factorization SearchGuard MultiLevelRank

variable {R : Type} [Field R] [DecidableEq R] {n m : Nat}
variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]

/-- Declared net value of one terminal implementation choice.  This rational
formula avoids silently truncating negative savings in `Nat`. -/
def netGain (calls baseline setup perCall : Nat) : ℚ :=
  (calls : ℚ) * ((baseline : ℚ) - (perCall : ℚ)) - (setup : ℚ)


theorem netGain_nonpositive_of_no_saving (calls baseline setup perCall : Nat)
    (h : baseline ≤ perCall) : netGain calls baseline setup perCall ≤ 0 := by
  unfold netGain
  have hd : (baseline : ℚ) - (perCall : ℚ) ≤ 0 := by exact sub_nonpos.mpr (by exact_mod_cast h)
  have hm : (calls : ℚ) * ((baseline : ℚ) - (perCall : ℚ)) ≤ 0 :=
    mul_nonpos_of_nonneg_of_nonpos (by positivity) hd
  have hs : 0 ≤ (setup : ℚ) := by positivity
  linarith


theorem netGain_antitone_setup (calls baseline perCall : Nat) {a b : Nat} (h : a ≤ b) :
    netGain calls baseline b perCall ≤ netGain calls baseline a perCall := by
  unfold netGain
  exact sub_le_sub_left (by exact_mod_cast h) _


theorem netGain_antitone_perCall (calls baseline setup : Nat) {a b : Nat} (h : a ≤ b) :
    netGain calls baseline setup b ≤ netGain calls baseline setup a := by
  unfold netGain
  have hc : (0 : ℚ) ≤ calls := by positivity
  have hd : (baseline : ℚ) - (b : ℚ) ≤ (baseline : ℚ) - (a : ℚ) := by
    exact sub_le_sub_left (by exact_mod_cast h) _
  exact sub_le_sub_right (mul_le_mul_of_nonneg_left hd hc) _

/-- The current sound rank floor bounds the best possible deployment saving of
any exact two-dense-stage factorization for every retained world. -/
theorem state_factor_saving_le_opportunity
    (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c)) (hs : RankSound c s)
    (w : Ω) (hw : w ∈ s.worlds) (calls baseline : Nat) :
    calls * (baseline - factorCost n m (c.matrix w).rank) ≤
      opportunity calls baseline (menuFloor baseline n m s.lower) := by
  have hr : s.lower ≤ (c.matrix w).rank := state_lower_rank c s hs w hw
  have hc : menuFloor baseline n m s.lower ≤ factorCost n m (c.matrix w).rank :=
    (menuFloor_le_factor baseline n m s.lower).trans (factorCost_mono hr)
  exact opportunity_bound calls baseline _ _ hc

/-- If the optimistic opportunity allowed by the current rank floor is already
no larger than a justified remaining setup lower bound, no exact two-dense-stage
factorization can have positive remaining net gain in any retained world. -/
theorem state_cold_denial_sound
    (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c)) (hs : RankSound c s)
    (w : Ω) (hw : w ∈ s.worlds) (calls baseline lowerSetup actualSetup : Nat)
    (hsetup : lowerSetup ≤ actualSetup)
    (hstop : opportunity calls baseline (menuFloor baseline n m s.lower) ≤ lowerSetup) :
    calls * baseline ≤ actualSetup + calls * factorCost n m (c.matrix w).rank := by
  have hf : menuFloor baseline n m s.lower ≤ baseline := menuFloor_le_original _ _ _ _
  have hc : menuFloor baseline n m s.lower ≤ factorCost n m (c.matrix w).rank :=
    (menuFloor_le_factor baseline n m s.lower).trans
      (factorCost_mono (state_lower_rank c s hs w hw))
  exact no_positive_net_of_setup_lower_bound calls baseline _ lowerSetup actualSetup _
    hf hc hsetup hstop

/-- A constant warm-cache payoff is represented exactly by the controller's
uniform-catalogue expectation. -/
theorem constant_reuse_reward (m : MultiLevel.Model Ω P) (s : MultiLevel.State m)
    (q : ℚ) (h : m.reusePayoff = fun _ => q) :
    MultiLevel.reward m s .reuse = q := by
  simp [MultiLevel.reward, h, MultiLevel.average_const]

end Komorebi.AVOC.Affine.MultiLevelEconomics
