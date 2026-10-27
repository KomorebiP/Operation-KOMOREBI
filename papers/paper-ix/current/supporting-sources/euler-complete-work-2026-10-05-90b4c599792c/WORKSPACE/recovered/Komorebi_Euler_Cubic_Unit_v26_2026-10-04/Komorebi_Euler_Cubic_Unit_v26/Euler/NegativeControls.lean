module
public import Euler.ResidueCertificates
public import Euler.DiscriminantReduction
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open Polynomial

/-- The finite skeleton, not the infinite Euler residual. -/
def packetPoly : ℕ → Polynomial D
  | 0 => 1
  | n+1 => packetPoly n * (X-C (n:D)) * (2*X-C (2*(n:D)+1))

def syntheticLower3 : Polynomial D := -C 162+117*X-18*X^2
def syntheticTriple : Polynomial D := packetPoly 5+4*syntheticLower3

def tripleQuotient : Polynomial D :=
  32*X^7-528*X^6+3408*X^5-10760*X^4+16866*X^3-11745*X^2+2898*X+81

/-- This exactly reproduces the non-Euler triple-root control in the manuscript. -/
theorem syntheticTriple_factor :
    syntheticTriple=(X-C (2:D))^3*tripleQuotient := by
  norm_num [syntheticTriple, syntheticLower3, tripleQuotient, packetPoly, C_ofNat]
  ring

theorem syntheticTriple_cube_dvd : (X-C (2:D))^3 ∣ syntheticTriple := by
  exact ⟨tripleQuotient,syntheticTriple_factor⟩

lemma tripleQuotient_at_two : tripleQuotient.eval 2=1025 := by
  norm_num [tripleQuotient]

/-- A direct divisibility test certifies EXACT multiplicity three. -/
theorem syntheticTriple_not_fourth : ¬ (X-C (2:D))^4 ∣ syntheticTriple := by
  intro h
  rw [syntheticTriple_factor] at h
  have hx : (X-C (2:D) : Polynomial D) ≠ 0 := X_sub_C_ne_zero 2
  have hc : (X-C (2:D)) ∣ tripleQuotient := by
    simpa only [show 4=3+1 by decide, pow_succ] using
      (mul_dvd_mul_iff_left (pow_ne_zero 3 hx)).mp h
  have hz := (dvd_iff_isRoot).mp hc
  change tripleQuotient.eval (2:D)=0 at hz
  rw [tripleQuotient_at_two] at hz
  norm_num at hz

/-- The lower reduction in this counterexample is genuinely the simple mode X. -/
theorem syntheticLower3_reduction : syntheticLower3.map red=X := by
  have h162 : red (162:D)=0 := by
    change red ((162:ℕ):D)=0
    rw [map_natCast]
    rfl
  have h117 : red (117:D)=1 := by
    change red ((117:ℕ):D)=1
    rw [map_natCast]
    rfl
  have h18 : red (18:D)=0 := by
    change red ((18:ℕ):D)=0
    rw [map_natCast]
    rfl
  change (-C (162:D)+C (117:D)*X-C (18:D)*X^2).map red=X
  simp [h162,h117,h18]

def syntheticDouble : Polynomial D := packetPoly 4+30*(X-1)
def doubleQuotient : Polynomial D :=
  16*X^6-192*X^5+888*X^4-1952*X^3+1977*X^2-660*X-30

theorem syntheticDouble_factor : syntheticDouble=(X-1)^2*doubleQuotient := by
  norm_num [syntheticDouble, doubleQuotient, packetPoly, C_ofNat]
  ring

theorem syntheticDouble_square_dvd : (X-1)^2 ∣ syntheticDouble :=
  ⟨doubleQuotient,syntheticDouble_factor⟩

lemma doubleQuotient_at_one : doubleQuotient.eval 1=47 := by
  norm_num [doubleQuotient]

/-- A finite residue check cannot distinguish these two quadratics, despite
one having a double root and the other having none at the origin. -/
theorem same_binary_reduction :
    (X^2 : Polynomial D).map red = (X^2-C (2:D)).map red := by
  simp

/-- The cubic shape by itself is not a proof of nondegeneracy. -/
theorem cubic_zero_parameters_critical :
    CriticalZero (fun x : ℚ_[2] => x^3) 0 := by
  have h := (cubic_analytic_critical_iff (K:=ℚ_[2]) 1 0 0 0).mpr
    (by simp [CubicCritical])
  simpa using h
end Komorebi.Euler
