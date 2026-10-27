import CrossRadixMobiusSpectralAlgebra
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Algebra.BigOperators.GroupWithZero.Finset

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Among divisors of consecutive prime powers, the top prime power is the unique new divisor. -/
lemma prime_power_unique_separator {p j g : ℕ} (hp : p.Prime) (hj : 0 < j) :
    (g ∣ p ^ j ∧ ¬ g ∣ p ^ (j - 1)) ↔ g = p ^ j := by
  constructor
  · rintro ⟨hgj, hnot⟩
    obtain ⟨k, hkj, rfl⟩ := (Nat.dvd_prime_pow hp).mp hgj
    have hnotle : ¬ k ≤ j - 1 := by
      intro hle
      apply hnot
      exact (Nat.pow_dvd_pow_iff_le_right hp.one_lt).mpr hle
    have hkj' : k = j := by omega
    rw [hkj']
  · rintro rfl
    constructor
    · exact dvd_refl _
    · intro h
      have hle := (Nat.pow_dvd_pow_iff_le_right hp.one_lt).mp h
      omega

/-- Build the canonical divisor coordinate from a proof of divisibility. -/
def divisorIdxOfDvd (hT : 0 < T) (n : ℕ) (hn : n ∣ T) : DivIdx T :=
  ⟨n, Nat.mem_divisors.mpr ⟨hn, hT.ne'⟩⟩

lemma divisorIdxOfDvd_val (hT : 0 < T) (n : ℕ) (hn : n ∣ T) :
    (divisorIdxOfDvd hT n hn).1 = n := rfl

/-- A prime-power width is the unique canonical width that separates adjacent valuation levels. -/
lemma width_unique_prime_power_separator
    (hT : 0 < T) {p j : ℕ} (hp : p.Prime) (hj : 0 < j)
    (hpjT : p ^ j ∣ T) (g : DivIdx T) :
    widthVec g (divisorIdxOfDvd hT (p ^ j) hpjT) ≠
      widthVec g (divisorIdxOfDvd hT (p ^ (j - 1))
        (dvd_trans ((Nat.pow_dvd_pow_iff_le_right hp.one_lt).mpr (by omega)) hpjT))
      ↔ g.1 = p ^ j := by
  have hprev : p ^ (j - 1) ∣ p ^ j :=
    (Nat.pow_dvd_pow_iff_le_right hp.one_lt).mpr (by omega)
  by_cases hgj : g.1 ∣ p ^ j
  · by_cases hgprev : g.1 ∣ p ^ (j - 1)
    · have hne : g.1 ≠ p ^ j := by
        intro heq
        exact ((prime_power_unique_separator hp hj).mpr heq).2 hgprev
      simp [widthVec, divisorIdxOfDvd, hgj, hgprev, hne]
    · have heq : g.1 = p ^ j :=
        (prime_power_unique_separator hp hj).mp ⟨hgj, hgprev⟩
      have hnotpow : ¬ p ^ j ∣ p ^ (j - 1) := by
        intro hpow
        have hle := (Nat.pow_dvd_pow_iff_le_right hp.one_lt).mp hpow
        omega
      simp [widthVec, divisorIdxOfDvd, heq, hnotpow]
  · have hgprev : ¬ g.1 ∣ p ^ (j - 1) := by
      intro h
      exact hgj (dvd_trans h hprev)
    have hne : g.1 ≠ p ^ j := by
      intro heq
      exact hgj (heq ▸ dvd_refl (p ^ j))
    simp [widthVec, divisorIdxOfDvd, hgj, hgprev, hne]

/-- Prime-power threshold signatures separate all divisor coordinates. -/
lemma eq_of_prime_power_thresholds
    {x y : DivIdx T}
    (h : ∀ (p k : ℕ), p.Prime → 0 < k → p ^ k ∣ T →
      (p ^ k ∣ x.1 ↔ p ^ k ∣ y.1)) : x = y := by
  apply Subtype.ext
  apply Nat.dvd_antisymm
  · rw [Nat.dvd_iff_prime_pow_dvd_dvd]
    intro p k hp hpkx
    by_cases hk : k = 0
    · subst k
      simp
    · have hpkT : p ^ k ∣ T := dvd_trans hpkx (Nat.mem_divisors.mp x.2).1
      exact (h p k hp (Nat.pos_of_ne_zero hk) hpkT).mp hpkx
  · rw [Nat.dvd_iff_prime_pow_dvd_dvd]
    intro p k hp hpky
    by_cases hk : k = 0
    · subst k
      simp
    · have hpkT : p ^ k ∣ T := dvd_trans hpky (Nat.mem_divisors.mp y.2).1
      exact (h p k hp (Nat.pos_of_ne_zero hk) hpkT).mpr hpky

/-- Equivalent form: equality of all prime-power width bits forces equality of divisor coordinates. -/
lemma eq_of_prime_power_width_values
    (hT : 0 < T) {x y : DivIdx T}
    (h : ∀ (p k : ℕ) (_hp : p.Prime) (_hk : 0 < k) (hpkT : p ^ k ∣ T),
      widthVec (divisorIdxOfDvd hT (p ^ k) hpkT) x =
        widthVec (divisorIdxOfDvd hT (p ^ k) hpkT) y) : x = y := by
  apply eq_of_prime_power_thresholds
  intro p k hp hk hpkT
  have hv := h p k hp hk hpkT
  by_cases hx : p ^ k ∣ x.1 <;> by_cases hy : p ^ k ∣ y.1 <;>
    simp [widthVec, divisorIdxOfDvd, hx, hy] at hv ⊢

end KomorebiCrossRadix

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- A family of canonical widths separates divisor coordinates if every distinct pair is detected by one width. -/
def SeparatesWidths (S : Set (DivIdx T)) : Prop :=
  ∀ ⦃x y : DivIdx T⦄, x ≠ y → ∃ g, g ∈ S ∧ widthVec g x ≠ widthVec g y

/-- The canonical family of all nontrivial prime-power divisors of `T`. -/
def primePowerWidthSet : Set (DivIdx T) :=
  {g | IsPrimePow g.1}

/-- Prime-power widths separate every pair of divisor coordinates. -/
lemma primePowerWidthSet_separates (hT : 0 < T) :
    SeparatesWidths (primePowerWidthSet (T := T)) := by
  intro x y hxy
  by_contra hnone
  push Not at hnone
  have heq : x = y := by
    apply eq_of_prime_power_width_values hT
    intro p k hp hk hpkT
    let g : DivIdx T := divisorIdxOfDvd hT (p ^ k) hpkT
    have hgpp : g ∈ primePowerWidthSet (T := T) := by
      change IsPrimePow (p ^ k)
      exact hp.isPrimePow.pow hk.ne'
    exact hnone g hgpp
  exact hxy heq

/-- Every separating family of canonical widths must contain every prime-power width. -/
lemma primePowerWidthSet_minimal (hT : 0 < T) {S : Set (DivIdx T)}
    (hsep : SeparatesWidths S) : primePowerWidthSet (T := T) ⊆ S := by
  intro q hqpp
  change IsPrimePow q.1 at hqpp
  obtain ⟨p, k, hp, hk, hpkq⟩ := (isPrimePow_nat_iff q.1).mp hqpp
  have hqT : q.1 ∣ T := (Nat.mem_divisors.mp q.2).1
  have hpkT : p ^ k ∣ T := hpkq ▸ hqT
  have hprevpow : p ^ (k - 1) ∣ p ^ k :=
    (Nat.pow_dvd_pow_iff_le_right hp.one_lt).mpr (by omega)
  let qprev : DivIdx T :=
    divisorIdxOfDvd hT (p ^ (k - 1)) (dvd_trans hprevpow hpkT)
  have hneq : qprev ≠ q := by
    intro heq
    have hv := congrArg Subtype.val heq
    change p ^ (k - 1) = q.1 at hv
    rw [← hpkq] at hv
    have hexp := Nat.pow_right_injective hp.two_le hv
    omega
  obtain ⟨g, hgS, hdiff⟩ := hsep hneq
  have hqk : q = divisorIdxOfDvd hT (p ^ k) hpkT := by
    apply Subtype.ext
    exact hpkq.symm
  have hdiff' :
      widthVec g (divisorIdxOfDvd hT (p ^ k) hpkT) ≠
        widthVec g (divisorIdxOfDvd hT (p ^ (k - 1))
          (dvd_trans hprevpow hpkT)) := by
    simpa [qprev, hqk] using hdiff.symm
  have hgval : g.1 = p ^ k := by
    apply (width_unique_prime_power_separator hT hp hk hpkT g).mp
    exact hdiff'
  have hgq : g = q := by
    apply Subtype.ext
    exact hgval.trans hpkq
  simpa [hgq] using hgS

/-- Prime-power widths are the unique least separating family under inclusion. -/
lemma primePowerWidthSet_least_separating (hT : 0 < T) :
    SeparatesWidths (primePowerWidthSet (T := T)) ∧
      ∀ S : Set (DivIdx T), SeparatesWidths S → primePowerWidthSet (T := T) ⊆ S := by
  exact ⟨primePowerWidthSet_separates hT, fun S hS => primePowerWidthSet_minimal hT hS⟩

end KomorebiCrossRadix

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Natural-number labels of all prime-power divisors of `T`. -/
def primePowerDivisors (T : ℕ) : Finset ℕ :=
  T.divisors.filter IsPrimePow

/-- The Boolean literal attached to threshold `q` for the target shell `c`. -/
def thresholdLiteral (c : DivIdx T) (q : ℕ) : DivCoord T :=
  if q ∣ c.1 then rawWidthVec (T := T) q
  else fun x => 1 - rawWidthVec (T := T) q x

/-- Boolean product of all prime-power threshold literals selecting shell `c`. -/
def primePowerShellFormula (c : DivIdx T) : DivCoord T :=
  fun x => ∏ q ∈ primePowerDivisors T, thresholdLiteral c q x

/-- Prime-power widths generate every primitive shell by a finite Boolean product. -/
lemma primePowerShellFormula_eq_shell (hT : 0 < T) (c : DivIdx T) :
    primePowerShellFormula c = shellVec c := by
  funext x
  simp only [primePowerShellFormula]
  by_cases hxc : x = c
  · subst x
    rw [shellVec, ite_eq_left rfl]
    apply Finset.prod_eq_one
    intro q hq
    by_cases hqc : q ∣ c.1
    · simp [thresholdLiteral, rawWidthVec, hqc]
    · simp [thresholdLiteral, rawWidthVec, hqc]
  · rw [shellVec, ite_eq_right hxc]
    obtain ⟨g, hgpp, hdiff⟩ := primePowerWidthSet_separates hT hxc
    have hgPrimePow : IsPrimePow g.1 := hgpp
    have hgmem : g.1 ∈ primePowerDivisors T := by
      rw [primePowerDivisors, Finset.mem_filter]
      exact ⟨g.2, hgPrimePow⟩
    have hzero : thresholdLiteral c g.1 x = 0 := by
      by_cases hgc : g.1 ∣ c.1 <;> by_cases hgx : g.1 ∣ x.1
      · have : False := hdiff (by simp [widthVec, hgc, hgx])
        exact this.elim
      · simp [thresholdLiteral, rawWidthVec, hgc, hgx]
      · simp [thresholdLiteral, rawWidthVec, hgc, hgx]
      · have : False := hdiff (by simp [widthVec, hgc, hgx])
        exact this.elim
    exact Finset.prod_eq_zero hgmem hzero

/-- Operator form: every primitive shell projector is generated by prime-power width projectors and complements. -/
lemma primePowerShellOperator_formula (hT : 0 < T) (c : DivIdx T) :
    diagOp (primePowerShellFormula c) = shellEnd c := by
  rw [primePowerShellFormula_eq_shell hT c]
  rfl

end KomorebiCrossRadix
