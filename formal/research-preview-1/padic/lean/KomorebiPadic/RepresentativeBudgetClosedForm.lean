import KomorebiPadic.CompilerComplexity
import Mathlib.Data.Nat.Choose.Basic

/-!
# Exact closed form for the full radix-representative budget

Block 09 bounded the exact suffix-window work by

`radixRepresentativeBudget p B = ∑ Q ∈ Icc 1 B, ((Q - 1) / p + 1)`.

This module evaluates that finite sum exactly.  The theorem is totalized over
all natural `p` and `B`, including `p = 0`, `p = 1`, and `B = 0` under Lean's
natural-number division and remainder conventions.

For `d = (B - 1) / p` and `s = (B - 1) % p`, the final result is

`B + (p * d * (d - 1)) / 2 + d * (s + 1)`.

The same budget is first proved in the equivalent quotient/remainder form

`B + p * choose (B / p) 2 + (B / p) * (B % p)`.
- Eases induction and makes the totalized zero-base case transparent.
-/

namespace KomorebiPadic

open scoped BigOperators

/-- Quotient/remainder closed form indexed by the endpoint `B`. -/
def radixRepresentativeBudgetQRClosedForm (p B : ℕ) : ℕ :=
  B + p * (B / p).choose 2 + (B / p) * (B % p)

/-- Appending quotient `B + 1` contributes exactly `B / p + 1`. -/
theorem radixRepresentativeBudget_succ (p B : ℕ) :
    radixRepresentativeBudget p (B + 1) =
      radixRepresentativeBudget p B + B / p + 1 := by
  unfold radixRepresentativeBudget
  rw [Finset.sum_Icc_succ_top (by omega)]
  simp only [Nat.add_sub_cancel]
  omega

/-- Exact quotient/remainder evaluation of the full representative budget.
This statement is valid for every natural base, including base zero. -/
theorem radixRepresentativeBudget_eq_qrClosedForm (p B : ℕ) :
    radixRepresentativeBudget p B =
      radixRepresentativeBudgetQRClosedForm p B := by
  induction B with
  | zero => simp [radixRepresentativeBudget, radixRepresentativeBudgetQRClosedForm]
  | succ B ih =>
      rw [radixRepresentativeBudget_succ, ih]
      unfold radixRepresentativeBudgetQRClosedForm
      by_cases hp0 : p = 0
      · subst p
        simp
      · have hp : 0 < p := Nat.pos_of_ne_zero hp0
        let q := B / p
        let s := B % p
        have hdecomp : p * q + s = B := by
          simpa [q, s] using Nat.div_add_mod B p
        have hslt : s < p := by
          dsimp [s]
          exact Nat.mod_lt B hp
        by_cases hroll : s + 1 = p
        · have hsucc_eq : B + 1 = p * (q + 1) := by
            rw [← hdecomp]
            calc
              p * q + s + 1 = p * q + p := by omega
              _ = p * (q + 1) := by ring
          have hdivsucc : (B + 1) / p = q + 1 := by
            rw [hsucc_eq]
            exact Nat.mul_div_cancel_left (q + 1) hp
          have hmodsucc : (B + 1) % p = 0 := by
            rw [hsucc_eq]
            exact Nat.mul_mod_right p (q + 1)
          have hchoose : (q + 1).choose 2 = q.choose 2 + q := by
            simpa [Nat.add_comm] using Nat.choose_succ_succ q 1
          change B + p * q.choose 2 + q * s + q + 1 =
            B + 1 + p * ((B + 1) / p).choose 2 +
              ((B + 1) / p) * ((B + 1) % p)
          rw [hdivsucc, hmodsucc, hchoose]
          simp only [Nat.mul_zero, Nat.add_zero]
          nlinarith [hroll]
        · have hnroll : s + 1 < p := by omega
          have hsucc_eq : B + 1 = p * q + (s + 1) := by omega
          have hdivsucc : (B + 1) / p = q := by
            rw [hsucc_eq, Nat.mul_add_div hp]
            rw [Nat.div_eq_of_lt hnroll]
            omega
          have hmodsucc : (B + 1) % p = s + 1 := by
            rw [hsucc_eq, Nat.mul_add_mod, Nat.mod_eq_of_lt hnroll]
          change B + p * q.choose 2 + q * s + q + 1 =
            B + 1 + p * ((B + 1) / p).choose 2 +
              ((B + 1) / p) * ((B + 1) % p)
          rw [hdivsucc, hmodsucc]
          ring

/-- Quotient of the last represented radix block. -/
def lastRadixBlockQuotient (p B : ℕ) : ℕ :=
  (B - 1) / p

/-- Remainder of the last represented radix block. -/
def lastRadixBlockRemainder (p B : ℕ) : ℕ :=
  (B - 1) % p

/-- Closed form using a binomial coefficient for the triangular full-block
contribution. -/
def radixRepresentativeBudgetLastBlockForm (p B : ℕ) : ℕ :=
  B + p * (lastRadixBlockQuotient p B).choose 2 +
    lastRadixBlockQuotient p B * (lastRadixBlockRemainder p B + 1)

/-- Convert the endpoint quotient/remainder formula to the final-block form.
The proof includes both the rollover and non-rollover radix cases. -/
theorem radixRepresentativeBudget_eq_lastBlockForm (p B : ℕ) :
    radixRepresentativeBudget p B =
      radixRepresentativeBudgetLastBlockForm p B := by
  rw [radixRepresentativeBudget_eq_qrClosedForm]
  unfold radixRepresentativeBudgetQRClosedForm
  unfold radixRepresentativeBudgetLastBlockForm
  unfold lastRadixBlockQuotient lastRadixBlockRemainder
  by_cases hB0 : B = 0
  · subst B
    simp
  by_cases hp0 : p = 0
  · subst p
    simp
  have hB : 0 < B := Nat.pos_of_ne_zero hB0
  have hp : 0 < p := Nat.pos_of_ne_zero hp0
  let d := (B - 1) / p
  let s := (B - 1) % p
  have hdecomp : p * d + s = B - 1 := by
    simpa [d, s] using Nat.div_add_mod (B - 1) p
  have hslt : s < p := by
    dsimp [s]
    exact Nat.mod_lt (B - 1) hp
  have hBform : B = p * d + (s + 1) := by omega
  by_cases hroll : s + 1 = p
  · have hBmul : B = p * (d + 1) := by
      rw [hBform, hroll]
      ring
    have hdiv : B / p = d + 1 := by
      rw [hBmul]
      exact Nat.mul_div_cancel_left (d + 1) hp
    have hmod : B % p = 0 := by
      rw [hBmul]
      exact Nat.mul_mod_right p (d + 1)
    have hchoose : (d + 1).choose 2 = d.choose 2 + d := by
      simpa [Nat.add_comm] using Nat.choose_succ_succ d 1
    change B + p * (B / p).choose 2 + (B / p) * (B % p) =
      B + p * d.choose 2 + d * (s + 1)
    rw [hdiv, hmod, hchoose]
    simp only [Nat.mul_zero, Nat.add_zero]
    nlinarith [hroll]
  · have hnroll : s + 1 < p := by omega
    have hdiv : B / p = d := by
      rw [hBform, Nat.mul_add_div hp, Nat.div_eq_of_lt hnroll]
      omega
    have hmod : B % p = s + 1 := by
      rw [hBform, Nat.mul_add_mod, Nat.mod_eq_of_lt hnroll]
    change B + p * (B / p).choose 2 + (B / p) * (B % p) =
      B + p * d.choose 2 + d * (s + 1)
    rw [hdiv, hmod]

/-- Arithmetic closed form stated without a binomial coefficient. -/
def radixRepresentativeBudgetClosedForm (p B : ℕ) : ℕ :=
  let d := lastRadixBlockQuotient p B
  let s := lastRadixBlockRemainder p B
  B + (p * d * (d - 1)) / 2 + d * (s + 1)

/-- Exact closed formula

`R(p,B) = B + p*d*(d-1)/2 + d*(s+1)`,

where `d = (B-1)/p` and `s = (B-1)%p`.  It is valid under Lean's
totalized natural arithmetic for all `p,B`. -/
theorem radixRepresentativeBudget_eq_closedForm (p B : ℕ) :
    radixRepresentativeBudget p B =
      radixRepresentativeBudgetClosedForm p B := by
  rw [radixRepresentativeBudget_eq_lastBlockForm]
  unfold radixRepresentativeBudgetLastBlockForm
  unfold radixRepresentativeBudgetClosedForm
  dsimp
  let d := (B - 1) / p
  let s := (B - 1) % p
  change B + p * d.choose 2 + d * (s + 1) =
    B + (p * d * (d - 1)) / 2 + d * (s + 1)
  rw [Nat.choose_two_right]
  have hdvd : 2 ∣ d * (d - 1) := Nat.two_dvd_mul_sub_one d
  have hdiv : (p * d * (d - 1)) / 2 = p * (d * (d - 1) / 2) := by
    calc
      (p * d * (d - 1)) / 2 = (p * (d * (d - 1))) / 2 := by
        rw [Nat.mul_assoc]
      _ = p * (d * (d - 1) / 2) := Nat.mul_div_assoc p hdvd
  rw [hdiv]

/-- Explicit, definition-free statement of the closed form. -/
theorem radixRepresentativeBudget_eq_closedForm_explicit (p B : ℕ) :
    radixRepresentativeBudget p B =
      let d := (B - 1) / p
      let s := (B - 1) % p
      B + (p * d * (d - 1)) / 2 + d * (s + 1) := by
  simpa [radixRepresentativeBudgetClosedForm,
    lastRadixBlockQuotient, lastRadixBlockRemainder] using
    radixRepresentativeBudget_eq_closedForm p B

/-- The empty endpoint has zero cost at every base. -/
@[simp] theorem radixRepresentativeBudget_zero_endpoint (p : ℕ) :
    radixRepresentativeBudget p 0 = 0 := by
  simp [radixRepresentativeBudget]

/-- At totalized base zero every summand is one. -/
@[simp] theorem radixRepresentativeBudget_zero_base (B : ℕ) :
    radixRepresentativeBudget 0 B = B := by
  rw [radixRepresentativeBudget_eq_closedForm]
  simp [radixRepresentativeBudgetClosedForm,
    lastRadixBlockQuotient, lastRadixBlockRemainder]

/-- At base one the budget is the triangular number `1 + ... + B`. -/
@[simp] theorem radixRepresentativeBudget_one_base (B : ℕ) :
    radixRepresentativeBudget 1 B = B * (B + 1) / 2 := by
  rw [radixRepresentativeBudget_eq_qrClosedForm]
  unfold radixRepresentativeBudgetQRClosedForm
  simp only [Nat.div_one, Nat.mod_one, Nat.mul_zero, Nat.add_zero, one_mul]
  have hchoose : (B + 1).choose 2 = B.choose 2 + B := by
    simpa [Nat.add_comm] using Nat.choose_succ_succ B 1
  calc
    B + B.choose 2 = (B + 1).choose 2 := by omega
    _ = (B + 1) * ((B + 1) - 1) / 2 := Nat.choose_two_right (B + 1)
    _ = B * (B + 1) / 2 := by
      rw [Nat.add_sub_cancel, Nat.mul_comm]

/-- Closed parameter-sensitive replacement for the finite-sum budget bound. -/
def maximumLayerCompilerClosedBudgetBound (p r h : ℕ) : ℕ :=
  let B := quotientSearchBound p r h
  let d := lastRadixBlockQuotient p B
  let s := lastRadixBlockRemainder p B
  2 * B + p + (p * d * (d - 1)) / 2 + d * (s + 1)

/-- The Block 09 finite-sum envelope is exactly the Block 10 closed envelope. -/
theorem maximumLayerCompilerBudgetBound_eq_closedBudgetBound
    (p r h : ℕ) :
    maximumLayerCompilerBudgetBound p r h =
      maximumLayerCompilerClosedBudgetBound p r h := by
  unfold maximumLayerCompilerBudgetBound
  unfold maximumLayerCompilerClosedBudgetBound
  dsimp
  rw [radixRepresentativeBudget_eq_closedForm]
  unfold radixRepresentativeBudgetClosedForm
  dsimp
  omega

/-- Exact compiler work is bounded by the closed parameter-sensitive formula. -/
theorem maximumLayerCompilerTotalTests_le_closedBudgetBound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerClosedBudgetBound p r h := by
  calc
    maximumLayerCompilerTotalTests p r h ≤
        maximumLayerCompilerBudgetBound p r h :=
      maximumLayerCompilerTotalTests_le_budgetBound hp hr
    _ = maximumLayerCompilerClosedBudgetBound p r h :=
      maximumLayerCompilerBudgetBound_eq_closedBudgetBound p r h

/-- Proof-carrying closed-form complexity certificate.  It retains the complete
Block 09 certificate and records the quotient-block decomposition used to
remove the finite sum from the sharper resource envelope. -/
structure MaximumLayerCompilerClosedFormCertificate (p r h : ℕ) where
  complexity : MaximumLayerCompilerComplexityCertificate p r h
  quotientBound : ℕ
  blockQuotient : ℕ
  blockRemainder : ℕ
  quotientBound_exact : quotientBound = quotientSearchBound p r h
  blockQuotient_exact :
    blockQuotient = lastRadixBlockQuotient p quotientBound
  blockRemainder_exact :
    blockRemainder = lastRadixBlockRemainder p quotientBound
  quotientBound_pos : 0 < quotientBound
  divmod_decomposition :
    p * blockQuotient + blockRemainder = quotientBound - 1
  remainder_lt_base : blockRemainder < p
  representativeBudget_exact :
    radixRepresentativeBudget p quotientBound =
      quotientBound + (p * blockQuotient * (blockQuotient - 1)) / 2 +
        blockQuotient * (blockRemainder + 1)
  closedBound_exact :
    maximumLayerCompilerBudgetBound p r h =
      maximumLayerCompilerClosedBudgetBound p r h
  totalTests_le_closed :
    complexity.totalTests ≤ maximumLayerCompilerClosedBudgetBound p r h

/-- Construct the closed-form certificate at prime base and positive precision. -/
def maximumLayerCompilerClosedFormCertificate
    (p r h : ℕ) (hp : p.Prime) (hr : 0 < r) :
    MaximumLayerCompilerClosedFormCertificate p r h where
  complexity := maximumLayerCompilerComplexityCertificate p r h hp hr
  quotientBound := quotientSearchBound p r h
  blockQuotient := lastRadixBlockQuotient p (quotientSearchBound p r h)
  blockRemainder := lastRadixBlockRemainder p (quotientSearchBound p r h)
  quotientBound_exact := rfl
  blockQuotient_exact := rfl
  blockRemainder_exact := rfl
  quotientBound_pos := quotientSearchBound_pos p r h
  divmod_decomposition := by
    simpa [lastRadixBlockQuotient, lastRadixBlockRemainder] using
      Nat.div_add_mod (quotientSearchBound p r h - 1) p
  remainder_lt_base := by
    unfold lastRadixBlockRemainder
    exact Nat.mod_lt _ hp.pos
  representativeBudget_exact := by
    simpa [radixRepresentativeBudgetClosedForm,
      lastRadixBlockQuotient, lastRadixBlockRemainder] using
      radixRepresentativeBudget_eq_closedForm p (quotientSearchBound p r h)
  closedBound_exact :=
    maximumLayerCompilerBudgetBound_eq_closedBudgetBound p r h
  totalTests_le_closed := by
    change maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerClosedBudgetBound p r h
    exact maximumLayerCompilerTotalTests_le_closedBudgetBound hp hr

end KomorebiPadic
