import PaperX.NumberFieldPrimeRestriction

/-! Restriction of an actual absolute arithmetic Frobenius element to an
arbitrary normal number field. The prime downstairs is the contraction of the
same absolute prime. Decomposition membership, the arithmetic p-power residue
action, and inertia membership are transported along the chosen integral
embedding. The existence statements construct one simultaneous absolute and
finite witness; no finite Frobenius witness is assumed separately. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NumberFieldFrobeniusRestriction
open NumberField AbsoluteIntegralFrobenius NumberFieldPrimeRestriction
open scoped Pointwise

variable (L : Type*) [Field L] [NumberField L] [Normal ℚ L]
  (Q : Ideal IntegralClosure)

/-- Absolute decomposition elements restrict to the decomposition group of the
actual contracted prime. No maximality assumption is needed for this transfer. -/
theorem restriction_mem_stabilizer (γ : GQ)
    (hγ : γ ∈ MulAction.stabilizer GQ Q) :
    AbsoluteGaloisRestriction.restriction L γ ∈
      MulAction.stabilizer Gal(L/ℚ) (restrictedPrime L Q) := by
  apply MulAction.mem_stabilizer_iff.mpr
  ext x
  rw [Ideal.mem_pointwise_smul_iff_inv_smul_mem]
  change integralEmbedding L ((AbsoluteGaloisRestriction.restriction L γ)⁻¹ • x) ∈ Q ↔
    integralEmbedding L x ∈ Q
  rw [← (AbsoluteGaloisRestriction.restriction L).map_inv
    (show Field.absoluteGaloisGroup ℚ from γ)]
  change integralEmbedding L (AbsoluteGaloisRestriction.restriction L (γ⁻¹) • x) ∈ Q ↔
    integralEmbedding L x ∈ Q
  erw [integralEmbedding_smul L (γ⁻¹) x]
  have hinv : γ⁻¹ • Q = Q :=
    MulAction.mem_stabilizer_iff.mp ((MulAction.stabilizer GQ Q).inv_mem hγ)
  simpa only [hinv] using
    (Ideal.smul_mem_pointwise_smul_iff (a := γ⁻¹) (S := Q) (x := integralEmbedding L x))

/-- Absolute ideal inertia restricts into the actual finite ideal inertia. -/
theorem restriction_mem_inertia (γ : GQ) (hγ : γ ∈ Q.inertia GQ) :
    AbsoluteGaloisRestriction.restriction L γ ∈
      (restrictedPrime L Q).inertia Gal(L/ℚ) := by
  intro x
  change integralEmbedding L (AbsoluteGaloisRestriction.restriction L γ • x - x) ∈ Q
  rw [map_sub, integralEmbedding_smul]
  exact hγ (integralEmbedding L x)

/-- An arithmetic p-power residue action restricts to the same arithmetic
p-power action on the actual residue field of the contracted prime. -/
theorem restriction_residue_power (p : ℕ) (γ : GQ)
    (hγ : ∀ x : IntegralClosure, Ideal.Quotient.mk Q (γ • x) =
      (Ideal.Quotient.mk Q x) ^ p) :
    ∀ x : 𝓞 L,
      Ideal.Quotient.mk (restrictedPrime L Q) (AbsoluteGaloisRestriction.restriction L γ • x) =
        (Ideal.Quotient.mk (restrictedPrime L Q) x) ^ p := by
  intro x
  rw [← map_pow]
  apply Ideal.Quotient.eq.mpr
  change integralEmbedding L (AbsoluteGaloisRestriction.restriction L γ • x - x ^ p) ∈ Q
  rw [map_sub, integralEmbedding_smul, map_pow]
  apply Ideal.Quotient.eq.mp
  simpa only [map_pow] using hγ (integralEmbedding L x)

/-- Actual arithmetic Frobenius data restrict together to the contracted prime. -/
theorem restriction_arithmeticFrobenius (p : ℕ) (γ : GQ)
    (hstab : γ ∈ MulAction.stabilizer GQ Q)
    (hres : ∀ x : IntegralClosure, Ideal.Quotient.mk Q (γ • x) =
      (Ideal.Quotient.mk Q x) ^ p) :
    AbsoluteGaloisRestriction.restriction L γ ∈
        MulAction.stabilizer Gal(L/ℚ) (restrictedPrime L Q) ∧
      ∀ x : 𝓞 L,
        Ideal.Quotient.mk (restrictedPrime L Q) (AbsoluteGaloisRestriction.restriction L γ • x) =
          (Ideal.Quotient.mk (restrictedPrime L Q) x) ^ p :=
  ⟨restriction_mem_stabilizer L Q γ hstab, restriction_residue_power L Q p γ hres⟩

/-- At any supplied actual maximal ideal above p, the constructed absolute
Frobenius also gives a finite Frobenius at its contraction. The same element
and the same contracted prime occur in both conclusions. -/
theorem exists_simultaneous_frobenius_at (p : ℕ) [Fact p.Prime]
    [Q.IsMaximal] [Q.LiesOver (Ideal.span {(p : ℤ)})] :
    ∃ γ : GQ, γ ∈ MulAction.stabilizer GQ Q ∧
      (∀ x : IntegralClosure, Ideal.Quotient.mk Q (γ • x) =
        (Ideal.Quotient.mk Q x) ^ p) ∧
      AbsoluteGaloisRestriction.restriction L γ ∈
        MulAction.stabilizer Gal(L/ℚ) (restrictedPrime L Q) ∧
      ∀ x : 𝓞 L,
        Ideal.Quotient.mk (restrictedPrime L Q) (AbsoluteGaloisRestriction.restriction L γ • x) =
          (Ideal.Quotient.mk (restrictedPrime L Q) x) ^ p := by
  obtain ⟨γ, hγ⟩ := AbsoluteIntegralFrobenius.exists_frobenius_at p Q
  exact ⟨γ.val, γ.property, hγ, restriction_arithmeticFrobenius L Q p γ.val γ.property hγ⟩

omit Q in
/-- For each rational prime, construct an actual absolute prime, its actual
maximal contraction to the number field, and a single absolute element which
has arithmetic Frobenius action at both primes. This does not assert that the
prime is unramified or that any prescribed finite automorphism occurs. -/
theorem exists_simultaneous_frobenius (p : ℕ) [Fact p.Prime] :
    ∃ Q : Ideal IntegralClosure,
      Q.IsMaximal ∧ Q.LiesOver (Ideal.span {(p : ℤ)}) ∧
      (restrictedPrime L Q).IsMaximal ∧
      (restrictedPrime L Q).LiesOver (Ideal.span {(p : ℤ)}) ∧
      ∃ γ : GQ, γ ∈ MulAction.stabilizer GQ Q ∧
        (∀ x : IntegralClosure, Ideal.Quotient.mk Q (γ • x) =
          (Ideal.Quotient.mk Q x) ^ p) ∧
        AbsoluteGaloisRestriction.restriction L γ ∈
          MulAction.stabilizer Gal(L/ℚ) (restrictedPrime L Q) ∧
        ∀ x : 𝓞 L,
          Ideal.Quotient.mk (restrictedPrime L Q) (AbsoluteGaloisRestriction.restriction L γ • x) =
            (Ideal.Quotient.mk (restrictedPrime L Q) x) ^ p := by
  obtain ⟨Q, hmax, hover, γ, hγ⟩ := AbsoluteIntegralFrobenius.exists_frobenius p
  let : Q.IsMaximal := hmax
  let : Q.LiesOver (Ideal.span {(p : ℤ)}) := hover
  exact ⟨Q, hmax, hover, restrictedPrime_isMaximal L p Q,
    restrictedPrime_liesOver L p Q, γ.val, γ.property, hγ,
    restriction_arithmeticFrobenius L Q p γ.val γ.property hγ⟩

end PaperX.NumberFieldFrobeniusRestriction
