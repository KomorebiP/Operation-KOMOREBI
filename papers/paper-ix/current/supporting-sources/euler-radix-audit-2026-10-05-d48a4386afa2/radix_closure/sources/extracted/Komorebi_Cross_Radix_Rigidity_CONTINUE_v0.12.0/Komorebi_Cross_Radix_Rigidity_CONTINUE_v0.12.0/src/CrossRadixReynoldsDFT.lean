import CrossRadixWidthOperatorBasis
import Mathlib.Analysis.Fourier.ZMod

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

abbrev ResidueProfile (T : ℕ) := ZMod T → ℂ

variable {T : ℕ}

/-- The raw Fourier mask attached to a divisor width `g | T`.
It keeps precisely the Fourier modes whose standard representative is divisible by `g`. -/
def rawWidthMask (g : DivIdx T) : ResidueProfile T :=
  fun k => if g.1 ∣ k.val then 1 else 0

/-- Diagonal Fourier-side projector for a divisor width. -/
def freqWidthEnd (g : DivIdx T) : Module.End ℂ (ResidueProfile T) where
  toFun := fun x k => rawWidthMask g k * x k
  map_add' := by intro x y; funext k; simp [mul_add]
  map_smul' := by intro a x; funext k; simp [mul_left_comm]

@[simp] lemma freqWidthEnd_apply (g : DivIdx T) (x : ResidueProfile T) (k : ZMod T) :
    freqWidthEnd g x k = rawWidthMask g k * x k := rfl

lemma freqWidthEnd_idempotent (g : DivIdx T) :
    (freqWidthEnd g).comp (freqWidthEnd g) = freqWidthEnd g := by
  apply LinearMap.ext
  intro x
  funext k
  simp only [LinearMap.comp_apply, freqWidthEnd_apply, rawWidthMask]
  split <;> simp

lemma freqWidthEnd_commute (g h : DivIdx T) :
    (freqWidthEnd g).comp (freqWidthEnd h) =
      (freqWidthEnd h).comp (freqWidthEnd g) := by
  apply LinearMap.ext
  intro x
  funext k
  simp only [LinearMap.comp_apply, freqWidthEnd_apply]
  ring

/-- A point in the range of an idempotent linear endomorphism is fixed by it. -/
lemma apply_eq_self_of_mem_range_of_idempotent
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (hP : P.comp P = P) {x : V}
    (hx : x ∈ LinearMap.range P) : P x = x := by
  rcases hx with ⟨y, rfl⟩
  exact LinearMap.congr_fun hP y

/-- Constructive range intersection for commuting idempotents. -/
lemma range_comp_eq_inf_of_commuting_idempotents
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P Q : Module.End ℂ V)
    (hP : P.comp P = P) (hQ : Q.comp Q = Q)
    (hcomm : P.comp Q = Q.comp P) :
    LinearMap.range (P.comp Q) = LinearMap.range P ⊓ LinearMap.range Q := by
  ext x
  constructor
  · rintro ⟨y, rfl⟩
    constructor
    · exact ⟨Q y, rfl⟩
    · refine ⟨P y, ?_⟩
      exact LinearMap.congr_fun hcomm.symm y
  · intro hx
    have hxP : x ∈ LinearMap.range P := hx.1
    have hxQ : x ∈ LinearMap.range Q := hx.2
    have hPx : P x = x := apply_eq_self_of_mem_range_of_idempotent P hP hxP
    have hQx : Q x = x := apply_eq_self_of_mem_range_of_idempotent Q hQ hxQ
    refine ⟨x, ?_⟩
    simp only [LinearMap.comp_apply, hQx, hPx]

section PositiveMask

variable (hT : 0 < T)

lemma rawWidthMask_mul (g h : DivIdx T) (k : ZMod T) :
    rawWidthMask g k * rawWidthMask h k = rawWidthMask (lcmIdx hT g h) k := by
  simp only [rawWidthMask, lcmIdx]
  by_cases hg : g.1 ∣ k.val <;> by_cases hh : h.1 ∣ k.val <;>
    simp [Nat.lcm_dvd_iff, hg, hh]

lemma freqWidthEnd_comp_lcm (g h : DivIdx T) :
    (freqWidthEnd g).comp (freqWidthEnd h) = freqWidthEnd (lcmIdx hT g h) := by
  apply LinearMap.ext
  intro x
  funext k
  simp only [LinearMap.comp_apply, freqWidthEnd_apply]
  rw [← mul_assoc, rawWidthMask_mul hT g h k]

end PositiveMask

section FourierPhysical

variable [NeZero T]

/-- Canonical physical width projector obtained by transporting the exact Fourier mask
through Mathlib's finite DFT on `ZMod T`. The separate Reynolds-average module identifies
this operator with the subgroup averaging formula. -/
def reynoldsProjector (g : DivIdx T) : Module.End ℂ (ResidueProfile T) :=
  (ZMod.dft (N := T) (E := ℂ)).symm.toLinearMap.comp
    ((freqWidthEnd g).comp (ZMod.dft (N := T) (E := ℂ)).toLinearMap)

/-- Exact DFT diagonalization: the physical projector is conjugate to a literal `0/1` mask. -/
lemma dft_reynoldsProjector (g : DivIdx T) (x : ResidueProfile T) :
    ZMod.dft (N := T) (E := ℂ) (reynoldsProjector g x) =
      freqWidthEnd g (ZMod.dft (N := T) (E := ℂ) x) := by
  simp [reynoldsProjector]

lemma reynoldsProjector_idempotent (g : DivIdx T) :
    (reynoldsProjector g).comp (reynoldsProjector g) = reynoldsProjector g := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  simp only [LinearMap.comp_apply, dft_reynoldsProjector]
  exact LinearMap.congr_fun (freqWidthEnd_idempotent g) _

lemma reynoldsProjector_commute (g h : DivIdx T) :
    (reynoldsProjector g).comp (reynoldsProjector h) =
      (reynoldsProjector h).comp (reynoldsProjector g) := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  simp only [LinearMap.comp_apply, dft_reynoldsProjector]
  exact LinearMap.congr_fun (freqWidthEnd_commute g h) _

/-- DFT-side support characterization of the range of the physical projector. -/
lemma mem_range_reynoldsProjector_iff_dft_fixed (g : DivIdx T) (x : ResidueProfile T) :
    x ∈ LinearMap.range (reynoldsProjector g) ↔
      freqWidthEnd g (ZMod.dft (N := T) (E := ℂ) x) =
        ZMod.dft (N := T) (E := ℂ) x := by
  constructor
  · intro hx
    have hfix := apply_eq_self_of_mem_range_of_idempotent
      (reynoldsProjector g) (reynoldsProjector_idempotent g) hx
    have := congrArg (fun y => ZMod.dft (N := T) (E := ℂ) y) hfix
    simpa only [dft_reynoldsProjector] using this
  · intro hfreq
    refine ⟨x, ?_⟩
    apply (ZMod.dft (N := T) (E := ℂ)).injective
    rw [dft_reynoldsProjector]
    exact hfreq

end FourierPhysical

section PositiveFourierPhysical

variable (hT : 0 < T) [NeZero T]

lemma reynoldsProjector_comp_lcm (g h : DivIdx T) :
    (reynoldsProjector g).comp (reynoldsProjector h) =
      reynoldsProjector (lcmIdx hT g h) := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  simp only [LinearMap.comp_apply, dft_reynoldsProjector]
  exact LinearMap.congr_fun (freqWidthEnd_comp_lcm hT g h) _

/-- Two canonical physical width ranges intersect exactly at the lcm width. -/
lemma reynoldsProjector_range_inf (g h : DivIdx T) :
    LinearMap.range (reynoldsProjector (lcmIdx hT g h)) =
      LinearMap.range (reynoldsProjector g) ⊓ LinearMap.range (reynoldsProjector h) := by
  rw [← reynoldsProjector_comp_lcm hT g h]
  exact range_comp_eq_inf_of_commuting_idempotents
    (reynoldsProjector g) (reynoldsProjector h)
    (reynoldsProjector_idempotent g)
    (reynoldsProjector_idempotent h)
    (reynoldsProjector_commute g h)

end PositiveFourierPhysical

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.dft_reynoldsProjector
#print axioms KomorebiCrossRadix.reynoldsProjector_comp_lcm
#print axioms KomorebiCrossRadix.reynoldsProjector_range_inf
