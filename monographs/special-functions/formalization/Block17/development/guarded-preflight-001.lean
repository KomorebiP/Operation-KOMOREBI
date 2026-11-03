import CoupledGuardedMajorant

namespace ScratchFixture0
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (R B : ℚ) (hR : 0 ≤ R) (budget : ℕ) (fits : ℚ → Bool) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ (R : ℝ)) : ‖p.toReal.complexComponent i z‖ ≤ (B : ℝ) := by
  exact guarded_majorant_disk_bound p hs hc R B hR budget fits i z hz
end
end ScratchFixture0

namespace ScratchFixture1
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : guardedFold (fun _ => true) (2/3) [2,1] = .ok (757/81) := by
  norm_num [guardedFold,majorantStep]
end
end ScratchFixture1

namespace ScratchFixture2
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : checkedMajorant (⟨1/2,1/2,1/2,1/2⟩ : RationalScales)
    (99/100) (some 0) (some 1) = .error (.resource .bits) := by
  norm_num [checkedMajorant,RationalScales.strictRational,guardedMajorant,buildLadder,guardedFold]
end
end ScratchFixture2

namespace ScratchFixture3
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : False := by sorry
end
end ScratchFixture3

namespace ScratchFixture4
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : buildLadder (1/2) 2 2 = .ok ([2,1],1/2) := by norm_num [buildLadder]
example : buildLadder (1/2) 1 2 = .error .steps := by norm_num [buildLadder]
example : guardedFold (fun _ => true) (2/3) [2,1] = .ok (500/81) := by
  norm_num [guardedFold,majorantStep]
example : guardedMajorant (1/2) 2 (fun _ => true) 2 = .ok (500/81) := by
  norm_num [guardedMajorant,buildLadder,guardedFold,majorantSeed,majorantStep]
example : guardedMajorant (1/2) 1 (fun _ => false) 2 = .error .steps := by
  norm_num [guardedMajorant,buildLadder]
example : guardedMajorant (1/2) 2 (fun _ => false) 2 = .error .bits := by
  norm_num [guardedMajorant,buildLadder,guardedFold]
example : guardedMajorant (1/2) 0 (fun _ => true) 1 = .error .steps := by
  exact guarded_majorant_no_steps _ _ _ (by norm_num)
example : checkedMajorant (⟨1/2,1/2,1/2,1/2⟩ : RationalScales) 0 none none = .ok 0 := by
  exact checked_zero_before_resources _ _ _ (by norm_num [RationalScales.strictRational])
example : checkedMajorant (⟨1,1/2,1/2,1/2⟩ : RationalScales) 0 none none = .error .scales := by
  exact checked_invalid_scales _ _ _ _ (by norm_num [RationalScales.strictRational])
example : checkedMajorant (⟨1/2,1/2,1/2,1/2⟩ : RationalScales) (99/100)
    (some 0) (some 1) = .ok (9900/199) := by
  have h := checked_small_seed_unchecked (⟨1/2,1/2,1/2,1/2⟩ : RationalScales) (99/100) 0 0
    (by norm_num [RationalScales.strictRational]) (by norm_num) (by norm_num)
  norm_num [majorantSeed] at h ⊢
  exact h
example : sizeFits 1 (9900/199) = false := by decide
example : checkedMajorant (⟨1/2,1/2,1/2,1/2⟩ : RationalScales) 2 (some 2) (some 1) =
    .error (.resource .bits) := by
  norm_num [checkedMajorant,RationalScales.strictRational,guardedMajorant,buildLadder,guardedFold,
    majorantSeed,majorantStep,sizeFits,rationalBitSize,integerWidth]
example (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t) : Q^xs.length*R < 1 :=
  ladder_adequate Q R t xs h
example (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (R B : ℚ) (hR : 0 ≤ R) (budget : ℕ) (fits : ℚ → Bool)
    (h : guardedMajorant p.maxScale budget fits R = .ok B) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ (R : ℝ)) : ‖p.toReal.complexComponent i z‖ ≤ (B : ℝ) :=
  guarded_majorant_disk_bound p hs hc R B hR budget fits h i z hz
end
end ScratchFixture4
