import PaperXI.TameExponent

/-! Paper XI, Proposition 5.3. The interaction character is built from actual
finite-field norms, the actual Frobenius, and multiplication of characters.
Exponent coordinates on the two subfields come from one faithful common-field
character. Every pair of characters admits these compatible coordinates. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameNormPacket

variable (K M L Q : Type*) [Field K] [Field M] [Field L] [Field Q]
  [Finite K] [Finite M] [Finite L] [Fintype Q]
  [Algebra K L] [Algebra M L] [Algebra Q M] [Algebra Q L]

/-- The actual interaction character, with the second residue character shifted
by the chosen iterate of Frobenius before its norm lift. -/
def interaction (ξ : Kˣ →* ℂˣ) (η : Mˣ →* ℂˣ) (i : ℕ) : Lˣ →* ℂˣ :=
  ξ.comp (TameNorm.norm K L) *
    (η.comp (TameNorm.frobenius M Q i)).comp (TameNorm.norm M L)

omit [Finite K] in
/-- Norm lifting, Frobenius, and character multiplication give the refined exponent. -/
theorem refined_exponent (χ : Lˣ →* ℂˣ) (a b i : ℕ) :
    interaction K M L Q ((χ.comp (TameNorm.embedding K L)) ^ a)
      ((χ.comp (TameNorm.embedding M L)) ^ b) i =
    χ ^ (a * TameNorm.normExponent K L +
      b * Fintype.card Q ^ i * TameNorm.normExponent M L) := by
  unfold interaction
  rw [TameNorm.norm_lift, TameNorm.shifted_lower_norm_lift]
  exact TameExponent.product χ _ _

omit [Finite K] in
/-- Triviality concerns the actual multiplicative character, and follows from
faithfulness rather than being assumed as an exponent-model axiom. -/
theorem refined_trivial_iff (χ : Lˣ →* ℂˣ) (hχ : Function.Injective χ)
    (a b i : ℕ) :
    interaction K M L Q ((χ.comp (TameNorm.embedding K L)) ^ a)
      ((χ.comp (TameNorm.embedding M L)) ^ b) i = 1 ↔
    ((a * TameNorm.normExponent K L +
      b * Fintype.card Q ^ i * TameNorm.normExponent M L : ℕ) :
        ZMod (Nat.card L - 1)) = 0 := by
  rw [refined_exponent, TameExponent.pow_eq_one_iff χ hχ]

omit [Finite K] in
/-- The boxed source formula for actual residue fields of sizes q^n, q^m, q^ell. -/
theorem source_formula (χ : Lˣ →* ℂˣ) (q n m ell : ℕ)
    (hQ : Fintype.card Q = q) (hK : Nat.card K = q ^ n)
    (hM : Nat.card M = q ^ m) (hL : Nat.card L = q ^ ell) (a b i : ℕ) :
    interaction K M L Q ((χ.comp (TameNorm.embedding K L)) ^ a)
      ((χ.comp (TameNorm.embedding M L)) ^ b) i =
    χ ^ (a * ((q ^ ell - 1) / (q ^ n - 1)) +
      b * q ^ i * ((q ^ ell - 1) / (q ^ m - 1))) := by
  simpa only [TameNorm.normExponent, hQ, hK, hM, hL] using
    refined_exponent K M L Q χ a b i

omit [Finite K] in
/-- The source zero-exponent criterion in Z/(q^ell-1). -/
theorem source_trivial_iff (χ : Lˣ →* ℂˣ) (hχ : Function.Injective χ)
    (q n m ell : ℕ) (hQ : Fintype.card Q = q) (hK : Nat.card K = q ^ n)
    (hM : Nat.card M = q ^ m) (hL : Nat.card L = q ^ ell) (a b i : ℕ) :
    interaction K M L Q ((χ.comp (TameNorm.embedding K L)) ^ a)
      ((χ.comp (TameNorm.embedding M L)) ^ b) i = 1 ↔
    ((a * ((q ^ ell - 1) / (q ^ n - 1)) +
      b * q ^ i * ((q ^ ell - 1) / (q ^ m - 1)) : ℕ) :
        ZMod (q ^ ell - 1)) = 0 := by
  rw [source_formula K M L Q χ q n m ell hQ hK hM hL,
    TameExponent.pow_eq_one_iff χ hχ, hL]

omit [Finite K] [Finite M] [Finite L] [Fintype Q] [Algebra Q M] [Algebra Q L] in
/-- Compatible basic characters on the subfields are faithful. -/
theorem restricted_faithful (χ : Lˣ →* ℂˣ) (hχ : Function.Injective χ) :
    Function.Injective (χ.comp (TameNorm.embedding K L)) ∧
    Function.Injective (χ.comp (TameNorm.embedding M L)) :=
  ⟨hχ.comp (TameNorm.embedding_injective K L),
    hχ.comp (TameNorm.embedding_injective M L)⟩

omit [Finite L] [Fintype Q] [Algebra Q M] [Algebra Q L] in
/-- Every given pair of residue characters admits compatible exponent coordinates;
no relation between independently chosen generators is postulated. -/
theorem exists_compatible_exponents (χ : Lˣ →* ℂˣ) (hχ : Function.Injective χ)
    (ξ : Kˣ →* ℂˣ) (η : Mˣ →* ℂˣ) :
    ∃ a < Nat.card K - 1, ∃ b < Nat.card M - 1,
      ξ = (χ.comp (TameNorm.embedding K L)) ^ a ∧
      η = (χ.comp (TameNorm.embedding M L)) ^ b := by
  obtain ⟨a, ha, hξ⟩ := TameExponent.exists_exponent _
    (restricted_faithful K M L χ hχ).1 ξ
  obtain ⟨b, hb, hη⟩ := TameExponent.exists_exponent _
    (restricted_faithful K M L χ hχ).2 η
  exact ⟨a, ha, b, hb, hξ, hη⟩

/-- Complete source-level existence statement, starting with arbitrary actual
characters and constructing a faithful coordinate system for every interaction. -/
theorem source (ξ : Kˣ →* ℂˣ) (η : Mˣ →* ℂˣ)
    (q n m ell : ℕ) (hQ : Fintype.card Q = q) (hK : Nat.card K = q ^ n)
    (hM : Nat.card M = q ^ m) (hL : Nat.card L = q ^ ell) :
    ∃ χ : Lˣ →* ℂˣ, Function.Injective χ ∧
      ∃ a < q ^ n - 1, ∃ b < q ^ m - 1,
      ξ = (χ.comp (TameNorm.embedding K L)) ^ a ∧
      η = (χ.comp (TameNorm.embedding M L)) ^ b ∧
      ∀ i : ℕ,
        interaction K M L Q ξ η i =
          χ ^ (a * ((q ^ ell - 1) / (q ^ n - 1)) +
            b * q ^ i * ((q ^ ell - 1) / (q ^ m - 1))) ∧
        (interaction K M L Q ξ η i = 1 ↔
          ((a * ((q ^ ell - 1) / (q ^ n - 1)) +
            b * q ^ i * ((q ^ ell - 1) / (q ^ m - 1)) : ℕ) :
              ZMod (q ^ ell - 1)) = 0) := by
  let χ := TameExponent.faithfulCharacter L
  have hχ := TameExponent.faithfulCharacter_injective L
  obtain ⟨a, ha, b, hb, hξ, hη⟩ := exists_compatible_exponents K M L χ hχ ξ η
  refine ⟨χ, hχ, a, by simpa only [hK] using ha,
    b, by simpa only [hM] using hb, hξ, hη, ?_⟩
  intro i
  rw [hξ, hη]
  exact ⟨source_formula K M L Q χ q n m ell hQ hK hM hL a b i,
    source_trivial_iff K M L Q χ hχ q n m ell hQ hK hM hL a b i⟩

end PaperXI.TameNormPacket
