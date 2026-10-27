import CrossRadixPrimePowerGeneratorCount

open scoped BigOperators

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- Exact local valuation selector built from two adjacent prime-power thresholds. -/
def localValuationVec (T p a : ℕ) : DivCoord T :=
  if a < T.factorization p then
    rawWidthVec (T := T) (p ^ a) - rawWidthVec (T := T) (p ^ (a + 1))
  else
    rawWidthVec (T := T) (p ^ a)

lemma divisor_ne_zero {T : ℕ} (hT : 0 < T) (x : DivIdx T) : x.1 ≠ 0 := by
  have hx : x.1 ∣ T := (Nat.mem_divisors.mp x.2).1
  intro hx0
  rw [hx0] at hx
  exact (Nat.ne_of_gt hT) (zero_dvd_iff.mp hx)

lemma divisor_factorization_le {T : ℕ} (hT : 0 < T) (x : DivIdx T) :
    x.1.factorization ≤ T.factorization := by
  apply (Nat.factorization_le_iff_dvd (divisor_ne_zero hT x) (Nat.ne_of_gt hT)).mpr
  exact (Nat.mem_divisors.mp x.2).1

lemma rawWidth_prime_pow_apply {T p a : ℕ} (hT : 0 < T) (hp : p.Prime)
    (x : DivIdx T) :
    rawWidthVec (T := T) (p ^ a) x =
      if a ≤ x.1.factorization p then 1 else 0 := by
  by_cases hle : a ≤ x.1.factorization p
  · have hdvd : p ^ a ∣ x.1 :=
      (hp.pow_dvd_iff_le_factorization (divisor_ne_zero hT x)).mpr hle
    simp [rawWidthVec, hdvd, hle]
  · have hndvd : ¬ p ^ a ∣ x.1 := by
      intro hdvd
      exact hle ((hp.pow_dvd_iff_le_factorization (divisor_ne_zero hT x)).mp hdvd)
    simp [rawWidthVec, hndvd, hle]

lemma localValuationVec_apply (hT : 0 < T) {p : ℕ} (hp : p.Prime)
    (c x : DivIdx T) :
    localValuationVec T p (c.1.factorization p) x =
      if x.1.factorization p = c.1.factorization p then 1 else 0 := by
  have hcle : c.1.factorization p ≤ T.factorization p := divisor_factorization_le hT c p
  have hxle : x.1.factorization p ≤ T.factorization p := divisor_factorization_le hT x p
  by_cases ha : c.1.factorization p < T.factorization p
  · simp only [localValuationVec, ha, ↓reduceIte]
    change rawWidthVec (T := T) (p ^ c.1.factorization p) x -
      rawWidthVec (T := T) (p ^ (c.1.factorization p + 1)) x = _
    rw [rawWidth_prime_pow_apply hT hp x, rawWidth_prime_pow_apply hT hp x]
    by_cases hxa : x.1.factorization p = c.1.factorization p
    · simp [hxa]
    · have hcases : x.1.factorization p < c.1.factorization p ∨
          c.1.factorization p + 1 ≤ x.1.factorization p := by omega
      rcases hcases with hlt | hge
      · have h1 : ¬ c.1.factorization p ≤ x.1.factorization p := by omega
        have h2 : ¬ c.1.factorization p + 1 ≤ x.1.factorization p := by omega
        simp [hxa, h1, h2]
      · have h1 : c.1.factorization p ≤ x.1.factorization p := by omega
        simp [hxa, h1, hge]
  · simp only [localValuationVec, ha, ↓reduceIte]
    rw [rawWidth_prime_pow_apply hT hp x]
    have hae : c.1.factorization p = T.factorization p := by omega
    by_cases hxa : x.1.factorization p = c.1.factorization p
    · simp [hxa]
    · have hlt : x.1.factorization p < c.1.factorization p := by omega
      have h1 : ¬ c.1.factorization p ≤ x.1.factorization p := by omega
      simp [hxa, h1]

/-- Product of one exact valuation selector for every prime dividing `T`. -/
def primeLocalShellFormula (c : DivIdx T) : DivCoord T :=
  fun x => ∏ p ∈ T.primeFactors, localValuationVec T p (c.1.factorization p) x

lemma eq_of_factorization_eq_on_primeFactors (hT : 0 < T) {x c : DivIdx T}
    (h : ∀ p ∈ T.primeFactors, x.1.factorization p = c.1.factorization p) : x = c := by
  apply Subtype.ext
  apply Nat.eq_of_factorization_eq (divisor_ne_zero hT x) (divisor_ne_zero hT c)
  intro p
  by_cases hpT : p ∈ T.primeFactors
  · exact h p hpT
  · have hTzero : T.factorization p = 0 := by
      have : p ∉ T.factorization.support := by simpa [Nat.support_factorization] using hpT
      exact Finsupp.notMem_support_iff.mp this
    have hxle := divisor_factorization_le hT x p
    have hcle := divisor_factorization_le hT c p
    omega

/-- Primitive shell factorizes prime-by-prime through adjacent valuation projectors. -/
theorem primeLocalShellFormula_eq_shell (hT : 0 < T) (c : DivIdx T) :
    primeLocalShellFormula c = shellVec c := by
  funext x
  simp only [primeLocalShellFormula]
  by_cases hxc : x = c
  · subst x
    rw [shellVec, ite_eq_left rfl]
    apply Finset.prod_eq_one
    intro p hpT
    have hp : p.Prime := (Nat.mem_primeFactors.mp hpT).1
    rw [localValuationVec_apply hT hp c c]
    simp
  · rw [shellVec, ite_eq_right hxc]
    by_contra hprod
    have hall : ∀ p ∈ T.primeFactors, x.1.factorization p = c.1.factorization p := by
      intro p hpT
      have hp : p.Prime := (Nat.mem_primeFactors.mp hpT).1
      by_contra hneq
      have hz : localValuationVec T p (c.1.factorization p) x = 0 := by
        rw [localValuationVec_apply hT hp c x]
        simp only [hneq, ↓reduceIte]
      have hzero : (∏ q ∈ T.primeFactors,
          localValuationVec T q (c.1.factorization q) x) = 0 :=
        Finset.prod_eq_zero hpT hz
      exact hprod hzero
    exact hxc (eq_of_factorization_eq_on_primeFactors hT hall)

/-- Operator version of the prime-local shell factorization. -/
theorem primeLocalShellOperator_formula (hT : 0 < T) (c : DivIdx T) :
    diagOp (primeLocalShellFormula c) = shellEnd c := by
  rw [primeLocalShellFormula_eq_shell hT c]
  rfl

end
end KomorebiCrossRadix

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

lemma divisor_dvd_iff_factorization_le_on_primeFactors (hT : 0 < T)
    (g x : DivIdx T) :
    g.1 ∣ x.1 ↔ ∀ p ∈ T.primeFactors, g.1.factorization p ≤ x.1.factorization p := by
  constructor
  · intro hgx p hpT
    have hfac : g.1.factorization ≤ x.1.factorization :=
      (Nat.factorization_le_iff_dvd (divisor_ne_zero hT g) (divisor_ne_zero hT x)).mpr hgx
    exact hfac p
  · intro hlocal
    apply (Nat.factorization_le_iff_dvd (divisor_ne_zero hT g) (divisor_ne_zero hT x)).mp
    intro p
    by_cases hpT : p ∈ T.primeFactors
    · exact hlocal p hpT
    · have hTzero : T.factorization p = 0 := by
        have hnot : p ∉ T.factorization.support := by
          simpa [Nat.support_factorization] using hpT
        exact Finsupp.notMem_support_iff.mp hnot
      have hgle := divisor_factorization_le hT g p
      have hxle := divisor_factorization_le hT x p
      omega

/-- Prime-by-prime cumulative-threshold factorization of a canonical width. -/
def primeLocalWidthFormula (g : DivIdx T) : DivCoord T :=
  fun x => ∏ p ∈ T.primeFactors, rawWidthVec (T := T) (p ^ g.1.factorization p) x

/-- Every canonical width is the product of its local prime-power thresholds. -/
theorem primeLocalWidthFormula_eq_width (hT : 0 < T) (g : DivIdx T) :
    primeLocalWidthFormula g = widthVec g := by
  funext x
  by_cases hgx : g.1 ∣ x.1
  · rw [widthVec, ite_eq_left hgx]
    simp only [primeLocalWidthFormula]
    apply Finset.prod_eq_one
    intro p hpT
    have hp : p.Prime := (Nat.mem_primeFactors.mp hpT).1
    rw [rawWidth_prime_pow_apply hT hp x]
    have hle := (divisor_dvd_iff_factorization_le_on_primeFactors hT g x).mp hgx p hpT
    simp [hle]
  · rw [widthVec, ite_eq_right hgx]
    simp only [primeLocalWidthFormula]
    have hnot : ¬ ∀ p ∈ T.primeFactors,
        g.1.factorization p ≤ x.1.factorization p := by
      exact fun h => hgx ((divisor_dvd_iff_factorization_le_on_primeFactors hT g x).mpr h)
    push Not at hnot
    obtain ⟨p, hpT, hfail⟩ := hnot
    have hp : p.Prime := (Nat.mem_primeFactors.mp hpT).1
    have hz : rawWidthVec (T := T) (p ^ g.1.factorization p) x = 0 := by
      rw [rawWidth_prime_pow_apply hT hp x]
      simp [hfail]
    exact Finset.prod_eq_zero hpT hz

/-- Dimension of the projector algebra in prime-factor coordinates. -/
theorem projectorAlg_finrank_prime_product (hT : 0 < T) :
    Module.finrank ℂ (ProjectorAlg T) =
      T.primeFactors.prod (fun p => T.factorization p + 1) := by
  rw [projectorAlg_finrank hT, Fintype.card_coe]
  exact Nat.card_divisors (Nat.ne_of_gt hT)

end
end KomorebiCrossRadix
