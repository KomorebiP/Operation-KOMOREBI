import CrossRadixPrimeLocalFactorization

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

abbrev PrimeIdx (T : ℕ) := {p : ℕ // p ∈ T.primeFactors}
abbrev ValProfile (T : ℕ) := (p : PrimeIdx T) → Fin (T.factorization p.1 + 1)

/-- Send a divisor to its complete vector of prime valuations. -/
def divisorValProfile (hT : 0 < T) (c : DivIdx T) : ValProfile T :=
  fun p => ⟨c.1.factorization p.1,
    Nat.lt_succ_of_le (divisor_factorization_le hT c p.1)⟩

lemma divisorValProfile_injective (hT : 0 < T) :
    Function.Injective (divisorValProfile hT) := by
  intro x c hxc
  apply eq_of_factorization_eq_on_primeFactors hT
  intro p hpT
  have hpEq := congrFun hxc (⟨p, hpT⟩ : PrimeIdx T)
  exact congrArg Fin.val hpEq

lemma card_DivIdx_prime_product (hT : 0 < T) :
    Fintype.card (DivIdx T) = T.primeFactors.prod (fun p => T.factorization p + 1) := by
  rw [Fintype.card_coe]
  exact Nat.card_divisors (Nat.ne_of_gt hT)

lemma card_ValProfile_prime_product :
    Fintype.card (ValProfile T) = T.primeFactors.prod (fun p => T.factorization p + 1) := by
  rw [Fintype.card_pi]
  simp only [Fintype.card_fin]
  exact Finset.prod_attach T.primeFactors (fun p => T.factorization p + 1)

/-- Divisor labels are canonically equivalent to bounded prime-valuation vectors. -/
def divisorValProfileEquiv (hT : 0 < T) : DivIdx T ≃ ValProfile T :=
  Equiv.ofBijective (divisorValProfile hT) <|
    (Fintype.bijective_iff_injective_and_card (divisorValProfile hT)).2
      ⟨divisorValProfile_injective hT,
        (card_DivIdx_prime_product hT).trans card_ValProfile_prime_product.symm⟩

@[simp] lemma divisorValProfileEquiv_apply (hT : 0 < T) (c : DivIdx T) :
    divisorValProfileEquiv hT c = divisorValProfile hT c := rfl

end
end KomorebiCrossRadix

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

abbrev ValCoord (T : ℕ) := ValProfile T → ℂ

/-- Reindex the entire divisor-coordinate algebra by the prime-valuation product coordinates. -/
def divisorValCoordAlgEquiv (hT : 0 < T) : DivCoord T ≃ₐ[ℂ] ValCoord T :=
  (AlgEquiv.piCongrLeft ℂ (fun _ : DivIdx T => ℂ)
    (divisorValProfileEquiv hT).symm).symm

@[simp] lemma divisorValCoordAlgEquiv_apply (hT : 0 < T)
    (a : DivCoord T) (v : ValProfile T) :
    divisorValCoordAlgEquiv hT a v = a ((divisorValProfileEquiv hT).symm v) := rfl

/-- The coordinate algebra is literally a function algebra on the finite product of local valuation chains. -/
theorem divisorCoordinateAlgebra_prime_product (hT : 0 < T) :
    Nonempty (DivCoord T ≃ₐ[ℂ] ((p : PrimeIdx T) → Fin (T.factorization p.1 + 1)) → ℂ) := by
  exact ⟨divisorValCoordAlgEquiv hT⟩

end
end KomorebiCrossRadix
