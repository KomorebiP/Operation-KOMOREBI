module
public import DyadicFourIsometry

@[expose] public section
set_option autoImplicit false

open KomorebiPaperIX

/-- Actual coefficient normalization is written out rather than supplied as
an assumed isometry hypothesis. The result is a bijective isometry. -/
example (j : ℕ) (hj : j < 4) :
    ∃! e : ℤ_[2] ≃ᵢ ℤ_[2], ∀ n : ℕ,
      (e (n : ℤ_[2]) : ℚ_[2]) =
        (((Congruential.unnormalized 4 j n - (j.factorial : ℚ)) /
          (2 : ℚ) ^ DyadicFourLeastPeriods.originalBonus j : ℚ) : ℚ_[2]) :=
  DyadicFourIsometry.existsUnique_isometry j hj

/-- Uniqueness includes continuous functions that are not assumed isometries. -/
example (j : ℕ) (hj : j < 4) (g : ℤ_[2] → ℤ_[2]) (hg : Continuous g)
    (hn : ∀ n : ℕ, (g (n : ℤ_[2]) : ℚ_[2]) =
      (((Congruential.unnormalized 4 j n - (j.factorial : ℚ)) /
        (2 : ℚ) ^ DyadicFourLeastPeriods.originalBonus j : ℚ) : ℚ_[2])) :
    g = DyadicFourIsometry.isometry j hj :=
  DyadicFourIsometry.unique_continuous j hj g hg hn

/-- Original coefficients interpolate on the packet index, not the degree index. -/
example (j : ℕ) (hj : j < 4) (n : ℕ) :
    (DyadicFourIsometry.originalExtension j hj (n : ℤ_[2]) : ℚ_[2]) =
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n) : ℚ_[2]) := by
  rw [NishibuchiCompletion.generalizedEuler_at_packet]
  exact DyadicFourIsometry.originalExtension_nat j hj n

example (j : ℕ) (hj : j < 4) (z : ℤ_[2]) :
    ∃! x : ℤ_[2], DyadicFourIsometry.originalExtension j hj x =
      (j.factorial : ℤ_[2]) + (2 : ℤ_[2]) ^ DyadicFourLeastPeriods.originalBonus j * z :=
  DyadicFourIsometry.unique_original_preimage j hj z

/-- The generic extension theorem uses the p-adic distance on embedded naturals. -/
example (p : ℕ) [Fact p.Prime] (f : ℕ → ℤ_[p])
    (h : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    ∃! e : ℤ_[p] ≃ᵢ ℤ_[p], ∀ n : ℕ, e (n : ℤ_[p]) = f n :=
  DensePadicIsometry.existsUnique_extensionEquiv p f h
