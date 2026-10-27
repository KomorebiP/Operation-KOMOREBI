import CrossRadixMobiusSpectralAlgebra
import Mathlib.Data.Nat.Squarefree
import Mathlib.Algebra.GCDMonoid.FinsetLemmas
import Mathlib.NumberTheory.Padics.PadicVal.Basic

noncomputable section
open scoped ArithmeticFunction.Moebius BigOperators

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Conductor of the primitive shell labelled by the divisor `c`. -/
def shellConductor (c : DivIdx T) : ℕ := T / c.1

lemma shell_label_pos (hT : 0 < T) (c : DivIdx T) : 0 < c.1 := by
  exact Nat.pos_of_dvd_of_pos (Nat.mem_divisors.mp c.2).1 hT

lemma shellConductor_pos (hT : 0 < T) (c : DivIdx T) : 0 < shellConductor c := by
  apply Nat.div_pos
  · exact Nat.le_of_dvd hT (Nat.mem_divisors.mp c.2).1
  · exact shell_label_pos hT c

/-- The widths occurring with nonzero coefficient in the Möbius primitive-shell formula. -/
def MobiusShellWidth (c : DivIdx T) (r : ℕ) : ℕ := c.1 * r

/-- Primewise denominator depth predicted by the Möbius shell formula: the shell label
contributes its existing depth, and a prime appearing in the conductor contributes at most
one additional denominator because only squarefree Möbius indices survive. -/
def shellPrimeDenomDepth (p : ℕ) (c : DivIdx T) : ℕ :=
  c.1.factorization p + if p ∣ shellConductor c then 1 else 0

/-- Every nonzero Möbius width has prime depth bounded by the shell label plus one conductor bit. -/
theorem mobius_shell_width_factorization_le
    (hT : 0 < T) (c : DivIdx T) {r p : ℕ}
    (hr : r ∈ (shellConductor c).divisors)
    (hmu : ArithmeticFunction.moebius r ≠ 0) :
    (MobiusShellWidth c r).factorization p ≤ shellPrimeDenomDepth p c := by
  have hc0 : c.1 ≠ 0 := (shell_label_pos hT c).ne'
  have hq0 : shellConductor c ≠ 0 := (shellConductor_pos hT c).ne'
  have hrdiv : r ∣ shellConductor c := (Nat.mem_divisors.mp hr).1
  have hr0 : r ≠ 0 := by
    exact fun hrz => hq0 (by simpa [hrz] using hrdiv)
  have hrsq : Squarefree r := ArithmeticFunction.moebius_ne_zero_iff_squarefree.mp hmu
  rw [MobiusShellWidth, Nat.factorization_mul hc0 hr0]
  by_cases hpq : p ∣ shellConductor c
  · simp only [shellPrimeDenomDepth, hpq, ite_true]
    exact Nat.add_le_add_left (hrsq.natFactorization_le_one p) _
  · have hpr : ¬ p ∣ r := fun hpr => hpq (dvd_trans hpr hrdiv)
    have hfac : r.factorization p = 0 := Nat.factorization_eq_zero_of_not_dvd hpr
    simp [shellPrimeDenomDepth, hpq, hfac]

/-- The bound is exact prime-by-prime: some active Möbius width attains it. -/
theorem exists_mobius_shell_width_factorization_eq
    (hT : 0 < T) (c : DivIdx T) (p : ℕ) (hp : p.Prime) :
    ∃ r ∈ (shellConductor c).divisors,
      ArithmeticFunction.moebius r ≠ 0 ∧
      (MobiusShellWidth c r).factorization p = shellPrimeDenomDepth p c := by
  have hc0 : c.1 ≠ 0 := (shell_label_pos hT c).ne'
  have hq0 : shellConductor c ≠ 0 := (shellConductor_pos hT c).ne'
  by_cases hpq : p ∣ shellConductor c
  · refine ⟨p, Nat.mem_divisors.mpr ⟨hpq, hq0⟩, ?_, ?_⟩
    · rw [ArithmeticFunction.moebius_apply_prime hp]
      norm_num
    · rw [MobiusShellWidth, Nat.factorization_mul hc0 hp.ne_zero]
      have hpf : p.factorization p = 1 := by
        rw [hp.factorization]
        simp
      simp [shellPrimeDenomDepth, hpq, hpf]
  · refine ⟨1, Nat.mem_divisors.mpr ⟨one_dvd _, hq0⟩, ?_, ?_⟩
    · simp
    · simp [MobiusShellWidth, shellPrimeDenomDepth, hpq]

/-- Padic-valuation restatement of the exact Möbius denominator-depth bound. -/
theorem mobius_shell_width_padicValNat_le
    (hT : 0 < T) (c : DivIdx T) {r p : ℕ} [Fact p.Prime]
    (hr : r ∈ (shellConductor c).divisors)
    (hmu : ArithmeticFunction.moebius r ≠ 0) :
    padicValNat p (MobiusShellWidth c r) ≤
      padicValNat p c.1 + if p ∣ shellConductor c then 1 else 0 := by
  simpa only [Nat.factorization_def _ (Fact.out : p.Prime), shellPrimeDenomDepth] using
    mobius_shell_width_factorization_le (p := p) (r := r) hT c hr hmu

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.mobius_shell_width_factorization_le
#print axioms KomorebiCrossRadix.exists_mobius_shell_width_factorization_eq
#print axioms KomorebiCrossRadix.mobius_shell_width_padicValNat_le

namespace KomorebiCrossRadix

/-- Active Möbius indices in the primitive-shell expansion. -/
def mobiusShellSupport {T : ℕ} (c : DivIdx T) : Finset ℕ :=
  (shellConductor c).divisors.filter (fun r => ArithmeticFunction.moebius r ≠ 0)

/-- Least common multiple of every denominator width that actually appears in the primitive-shell expansion. -/
def shellCommonDenom {T : ℕ} (c : DivIdx T) : ℕ :=
  (mobiusShellSupport c).lcm (MobiusShellWidth c)

lemma mem_mobiusShellSupport {T : ℕ} {c : DivIdx T} {r : ℕ} :
    r ∈ mobiusShellSupport c ↔
      r ∈ (shellConductor c).divisors ∧ ArithmeticFunction.moebius r ≠ 0 := by
  simp [mobiusShellSupport]

lemma MobiusShellWidth_ne_zero {T : ℕ} (hT : 0 < T) (c : DivIdx T)
    {r : ℕ} (hr : r ∈ mobiusShellSupport c) :
    MobiusShellWidth c r ≠ 0 := by
  have hc0 : c.1 ≠ 0 := (shell_label_pos hT c).ne'
  have hq0 : shellConductor c ≠ 0 := (shellConductor_pos hT c).ne'
  have hrdiv : r ∣ shellConductor c := (Nat.mem_divisors.mp (mem_mobiusShellSupport.mp hr).1).1
  have hr0 : r ≠ 0 := fun hrz => hq0 (by simpa [hrz] using hrdiv)
  exact mul_ne_zero hc0 hr0

/-- Exact prime exponent of the least common denominator of the primitive-shell Möbius expansion. -/
theorem shellCommonDenom_factorization
    {T : ℕ} (hT : 0 < T) (c : DivIdx T) (p : ℕ) (hp : p.Prime) :
    (shellCommonDenom c).factorization p = shellPrimeDenomDepth p c := by
  rw [shellCommonDenom, Finset.factorization_lcm]
  · apply le_antisymm
    · apply Finset.sup_le
      intro r hr
      exact mobius_shell_width_factorization_le hT c
        (mem_mobiusShellSupport.mp hr).1 (mem_mobiusShellSupport.mp hr).2
    · obtain ⟨r, hrdiv, hmu, heq⟩ :=
        exists_mobius_shell_width_factorization_eq hT c p hp
      have hr : r ∈ mobiusShellSupport c := mem_mobiusShellSupport.mpr ⟨hrdiv, hmu⟩
      rw [← heq]
      exact Finset.le_sup (f := fun r : ℕ => (MobiusShellWidth c r).factorization p) hr
  · intro r hr
    exact MobiusShellWidth_ne_zero hT c hr

/-- Padic form of the exact shell common-denominator formula. -/
theorem shellCommonDenom_padicValNat
    {T p : ℕ} [Fact p.Prime] (hT : 0 < T) (c : DivIdx T) :
    padicValNat p (shellCommonDenom c) =
      padicValNat p c.1 + if p ∣ shellConductor c then 1 else 0 := by
  simpa only [Nat.factorization_def _ (Fact.out : p.Prime), shellPrimeDenomDepth] using
    shellCommonDenom_factorization hT c p (Fact.out : p.Prime)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.shellCommonDenom_factorization
#print axioms KomorebiCrossRadix.shellCommonDenom_padicValNat

namespace KomorebiCrossRadix

lemma shellCommonDenom_ne_zero {T : ℕ} (hT : 0 < T) (c : DivIdx T) :
    shellCommonDenom c ≠ 0 := by
  rw [shellCommonDenom, Finset.lcm_ne_zero_iff]
  intro r hr
  exact MobiusShellWidth_ne_zero hT c hr

lemma shellCommonDenom_pos {T : ℕ} (hT : 0 < T) (c : DivIdx T) :
    0 < shellCommonDenom c := Nat.pos_of_ne_zero (shellCommonDenom_ne_zero hT c)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.shellCommonDenom_ne_zero

namespace KomorebiCrossRadix

lemma mobiusShellWidth_dvd_period {T : ℕ} (c : DivIdx T)
    {r : ℕ} (hr : r ∈ mobiusShellSupport c) :
    MobiusShellWidth c r ∣ T := by
  have hcT : c.1 ∣ T := (Nat.mem_divisors.mp c.2).1
  have hrq : r ∣ shellConductor c :=
    (Nat.mem_divisors.mp (mem_mobiusShellSupport.mp hr).1).1
  have hmul : c.1 * r ∣ c.1 * shellConductor c := Nat.mul_dvd_mul_left c.1 hrq
  have hcq : c.1 * shellConductor c = T := by
    simpa [shellConductor] using Nat.mul_div_cancel' hcT
  simpa [MobiusShellWidth, hcq] using hmul

lemma one_mem_mobiusShellSupport {T : ℕ} (hT : 0 < T) (c : DivIdx T) :
    1 ∈ mobiusShellSupport c := by
  rw [mem_mobiusShellSupport]
  constructor
  · exact Nat.mem_divisors.mpr ⟨one_dvd _, (shellConductor_pos hT c).ne'⟩
  · simp

lemma shell_label_dvd_commonDenom {T : ℕ} (hT : 0 < T) (c : DivIdx T) :
    c.1 ∣ shellCommonDenom c := by
  have h : c.1 ∣ (mobiusShellSupport c).lcm (MobiusShellWidth c) := by
    simpa [MobiusShellWidth] using
      (Finset.dvd_lcm (f := MobiusShellWidth c) (one_mem_mobiusShellSupport hT c))
  exact h

lemma shellCommonDenom_dvd_period {T : ℕ} (c : DivIdx T) :
    shellCommonDenom c ∣ T := by
  rw [shellCommonDenom]
  exact Finset.lcm_dvd fun r hr => mobiusShellWidth_dvd_period c hr

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.shell_label_dvd_commonDenom
#print axioms KomorebiCrossRadix.shellCommonDenom_dvd_period
