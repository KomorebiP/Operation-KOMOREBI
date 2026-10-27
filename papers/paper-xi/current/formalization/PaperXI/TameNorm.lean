import Mathlib.FieldTheory.Finite.GaloisField
import Mathlib.Data.ZMod.Basic
import Mathlib.Basic.Complex.Basic

/-! Paper XI, 5.3: norm lifting and Frobenius on actual finite-field unit characters.
The characters on subfields are restrictions of one character of the common field.
This is the compatible choice of exponent coordinates used by the source formula. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameNorm

variable (K L : Type*) [Field K] [Field L] [Algebra K L] [Finite L]

/-- The actual field embedding on multiplicative groups. -/
def embedding : Kˣ →* Lˣ := Units.map (algebraMap K L).toMonoidHom

omit [Finite L] in
theorem embedding_injective : Function.Injective (embedding K L) := by
  intro x y h
  apply Units.ext
  exact (algebraMap K L).injective (congrArg (fun u : Lˣ => (u : L)) h)

/-- The actual field norm on multiplicative groups. -/
def norm : Lˣ →* Kˣ := Units.map (Algebra.norm K (S := L))

/-- The finite-field norm exponent, expressed using field cardinalities. -/
def normExponent : ℕ := (Nat.card L - 1) / (Nat.card K - 1)

theorem embedding_norm (x : Lˣ) :
    embedding K L (norm K L x) = x ^ normExponent K L := by
  apply Units.ext
  exact FiniteField.algebraMap_norm_eq_pow

/-- Pulling a character back by the actual norm multiplies its exponent. -/
theorem norm_lift (χ : Lˣ →* ℂˣ) (a : ℕ) :
    (((χ.comp (embedding K L)) ^ a).comp (norm K L)) =
      χ ^ (a * normExponent K L) := by
  apply MonoidHom.ext
  intro x
  change χ (embedding K L (norm K L x)) ^ a = χ x ^ (a * normExponent K L)
  rw [embedding_norm, map_pow, ← pow_mul, Nat.mul_comm]

/-- Actual units norm lifting preserves nontriviality because the norm is onto. -/
theorem norm_lift_eq_one_iff (χ : Kˣ →* ℂˣ) :
    χ.comp (norm K L) = 1 ↔ χ = 1 := by
  constructor
  · intro h
    apply MonoidHom.ext
    intro x
    obtain ⟨y, rfl⟩ := FiniteField.unitsMap_norm_surjective K L x
    exact congrArg (fun f : Lˣ →* ℂˣ => f y) h
  · intro h
    simp [h]

variable (Q : Type*) [Field Q] [Fintype Q] [Algebra Q L]

/-- The actual iterate of the relative finite-field Frobenius on units. -/
def frobenius (i : ℕ) : Lˣ →* Lˣ :=
  Units.map (((FiniteField.frobeniusAlgEquivOfAlgebraic Q L) ^ i).toAlgHom.toMonoidHom)

@[simp] theorem frobenius_apply (i : ℕ) (x : Lˣ) :
    frobenius L Q i x = x ^ (Fintype.card Q ^ i) := by
  apply Units.ext
  change ((FiniteField.frobeniusAlgEquivOfAlgebraic Q L) ^ i) (x : L) = _
  rw [AlgEquiv.coe_pow, FiniteField.coe_frobeniusAlgEquivOfAlgebraic_iterate]
  rfl

theorem frobenius_character (χ : Lˣ →* ℂˣ) (i : ℕ) :
    χ.comp (frobenius L Q i) = χ ^ (Fintype.card Q ^ i) := by
  apply MonoidHom.ext
  intro x
  simp [MonoidHom.comp_apply]

/-- The norm lift of the Frobenius-shifted subfield character, evaluated on
an actual common-field unit. -/
theorem shifted_norm_lift (χ : Lˣ →* ℂˣ) (a i : ℕ) :
    ((((χ.comp (embedding K L)) ^ a).comp (norm K L)).comp
      (frobenius L Q i)) = χ ^ (a * Fintype.card Q ^ i * normExponent K L) := by
  rw [norm_lift]
  apply MonoidHom.ext
  intro x
  change χ (frobenius L Q i x) ^ (a * normExponent K L) = _
  rw [frobenius_apply, map_pow, ← pow_mul]
  congr 1
  ac_rfl

/-- Norm and the actual q-Frobenius commute on units. -/
theorem norm_frobenius [Finite K] [Algebra Q K] (i : ℕ) (x : Lˣ) :
    norm K L (frobenius L Q i x) = frobenius K Q i (norm K L x) := by
  rw [frobenius_apply, frobenius_apply, map_pow]

/-- The source ordering: shift the lower-field character, then lift by the norm. -/
theorem shifted_lower_norm_lift [Finite K] [Algebra Q K]
    (χ : Lˣ →* ℂˣ) (a i : ℕ) :
    ((((χ.comp (embedding K L)) ^ a).comp (frobenius K Q i)).comp
      (norm K L)) = χ ^ (a * Fintype.card Q ^ i * normExponent K L) := by
  rw [← shifted_norm_lift K L Q χ a i]
  apply MonoidHom.ext
  intro x
  simp only [MonoidHom.comp_apply, norm_frobenius]

end PaperXI.TameNorm
