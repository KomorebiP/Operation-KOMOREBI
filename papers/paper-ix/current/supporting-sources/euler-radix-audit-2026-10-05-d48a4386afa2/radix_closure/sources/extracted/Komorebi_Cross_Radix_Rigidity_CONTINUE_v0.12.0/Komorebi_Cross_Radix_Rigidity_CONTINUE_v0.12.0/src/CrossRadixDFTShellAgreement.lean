import CrossRadixReynoldsDFT
import CrossRadixMobiusSpectralAlgebra

noncomputable section
open scoped BigOperators ArithmeticFunction.Moebius

namespace KomorebiCrossRadix

variable {T : ℕ}

section PositivePeriod
variable (hT : 0 < T)

/-- Every raw Fourier frequency is assigned to its canonical divisor shell by `gcd(T,k)`. -/
def frequencyShellIdx (k : ZMod T) : DivIdx T :=
  ⟨Nat.gcd T k.val, Nat.mem_divisors.mpr ⟨Nat.gcd_dvd_left T k.val, hT.ne'⟩⟩

@[simp] lemma frequencyShellIdx_val (k : ZMod T) :
    (frequencyShellIdx hT k).1 = Nat.gcd T k.val := rfl

/-- The raw Fourier `0/1` width mask is exactly the certified divisor width coordinate
evaluated on the canonical gcd-shell of the frequency. -/
lemma rawWidthMask_eq_widthVec_frequencyShell
    (g : DivIdx T) (k : ZMod T) :
    rawWidthMask g k = widthVec g (frequencyShellIdx hT k) := by
  have hgT : g.1 ∣ T := (Nat.mem_divisors.mp g.2).1
  by_cases hk : g.1 ∣ k.val
  · have hgcd : g.1 ∣ Nat.gcd T k.val := Nat.dvd_gcd hgT hk
    simp [rawWidthMask, widthVec, frequencyShellIdx, hk, hgcd]
  · have hngcd : ¬ g.1 ∣ Nat.gcd T k.val := by
      intro hgcd
      exact hk (dvd_trans hgcd (Nat.gcd_dvd_right T k.val))
    simp [rawWidthMask, widthVec, frequencyShellIdx, hk, hngcd]

/-- Raw primitive Fourier shell mask: exact equality of the gcd-shell label with `c`. -/
def rawShellMask (c : DivIdx T) : ResidueProfile T :=
  fun k => shellVec c (frequencyShellIdx hT k)

@[simp] lemma rawShellMask_apply (c : DivIdx T) (k : ZMod T) :
    rawShellMask hT c k = shellVec c (frequencyShellIdx hT k) := rfl

lemma rawShellMask_zero_or_one (c : DivIdx T) (k : ZMod T) :
    rawShellMask hT c k = 0 ∨ rawShellMask hT c k = 1 := by
  by_cases hc : frequencyShellIdx hT k = c
  · right
    simp [rawShellMask, shellVec, hc]
  · left
    simp [rawShellMask, shellVec, hc]

/-- The DFT width mask splits into the same primitive shells as the certified divisor algebra. -/
lemma rawWidthMask_eq_sum_rawShells (g : DivIdx T) :
    rawWidthMask g =
      ∑ c ∈ Finset.univ.filter (fun c : DivIdx T => g.1 ∣ c.1), rawShellMask hT c := by
  funext k
  rw [rawWidthMask_eq_widthVec_frequencyShell hT]
  have hs := congrFun (widthVec_eq_sum_shells g) (frequencyShellIdx hT k)
  rw [hs]
  simp only [Finset.sum_apply, rawShellMask_apply]

/-- The raw Fourier primitive shell is literally the already-certified divisor shell after
canonical gcd-shell labeling. Hence the saved Möbius inversion theorem transports without
changing coefficients or shell semantics. -/
lemma rawShellMask_mobius_agrees_with_certified
    (c : DivIdx T) (k : ZMod T) :
    rawShellMask hT c k =
      (∑ r ∈ (T / c.1).divisors,
        (((ArithmeticFunction.moebius r : ℤ) : ℂ) •
          rawWidthVec (T := T) (c.1 * r))) (frequencyShellIdx hT k) := by
  exact congrFun (shellVec_mobius_width hT c) (frequencyShellIdx hT k)

end PositivePeriod

section PositiveFourier
variable (hT : 0 < T) [NeZero T]

/-- Fourier-side primitive-shell diagonal operator. -/
def rawShellFreqEnd (c : DivIdx T) : Module.End ℂ (ResidueProfile T) where
  toFun := fun x k => rawShellMask hT c k * x k
  map_add' := by intro x y; funext k; simp [mul_add]
  map_smul' := by intro a x; funext k; simp [mul_left_comm]

/-- Physical primitive-shell projector obtained by DFT conjugation. -/
def dftShellProjector (c : DivIdx T) : Module.End ℂ (ResidueProfile T) :=
  (ZMod.dft (N := T) (E := ℂ)).symm.toLinearMap.comp
    ((rawShellFreqEnd hT c).comp (ZMod.dft (N := T) (E := ℂ)).toLinearMap)

lemma dft_dftShellProjector (c : DivIdx T) (x : ResidueProfile T) :
    ZMod.dft (N := T) (E := ℂ) (dftShellProjector hT c x) =
      rawShellFreqEnd hT c (ZMod.dft (N := T) (E := ℂ) x) := by
  simp [dftShellProjector]

omit [NeZero T] in
lemma rawShellFreqEnd_idempotent (c : DivIdx T) :
    (rawShellFreqEnd hT c).comp (rawShellFreqEnd hT c) = rawShellFreqEnd hT c := by
  apply LinearMap.ext
  intro x
  funext k
  change rawShellMask hT c k * (rawShellMask hT c k * x k) =
    rawShellMask hT c k * x k
  by_cases hc : frequencyShellIdx hT k = c
  · simp [rawShellMask, shellVec, hc]
  · simp [rawShellMask, shellVec, hc]

lemma dftShellProjector_idempotent (c : DivIdx T) :
    (dftShellProjector hT c).comp (dftShellProjector hT c) = dftShellProjector hT c := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  simp only [LinearMap.comp_apply, dft_dftShellProjector]
  exact LinearMap.congr_fun (rawShellFreqEnd_idempotent hT c) _

/-- Distinct certified divisor shells give orthogonal DFT shell projectors. -/
lemma dftShellProjector_orthogonal {c e : DivIdx T} (hce : c ≠ e) :
    (dftShellProjector hT c).comp (dftShellProjector hT e) = 0 := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  simp only [LinearMap.comp_apply, LinearMap.zero_apply]
  rw [dft_dftShellProjector, dft_dftShellProjector]
  simp only [map_zero]
  funext k
  change shellVec c (frequencyShellIdx hT k) *
    (shellVec e (frequencyShellIdx hT k) * ZMod.dft (N := T) (E := ℂ) x k) = 0
  rw [← mul_assoc, shellVec_mul_ne hce, zero_mul]

end PositiveFourier

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.rawWidthMask_eq_widthVec_frequencyShell
#print axioms KomorebiCrossRadix.rawWidthMask_eq_sum_rawShells
#print axioms KomorebiCrossRadix.rawShellMask_mobius_agrees_with_certified
#print axioms KomorebiCrossRadix.dftShellProjector_orthogonal
