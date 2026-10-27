import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.RingTheory.Localization.Integer
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Fintype.Lattice

/-! Primitive normalization over a discrete valuation ring.  A nonzero finite
family over the fraction field can be rescaled so that all entries are integral
and one entry is exactly one.  Neither a lattice normalization nor an integral
comparison is supplied as a premise. -/
set_option autoImplicit false

namespace PaperX.PrimitiveMatrix

variable {R : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
variable {K : Type*} [Field K] [Algebra R K] [IsFractionRing R K]

/-- Divide a nonzero integral finite family by an entry of least valuation. -/
theorem integral_family_normalization {ι : Type*} [Finite ι]
    (a : ι → R) (ha : ∃ i, a i ≠ 0) :
    ∃ (b : R) (p : ι → R), b ≠ 0 ∧ (∀ i, a i = b * p i) ∧ ∃ i, p i = 1 := by
  classical
  obtain ⟨j, hj⟩ := ha
  let : Nonempty ι := ⟨j⟩
  obtain ⟨i, hi⟩ := Finite.exists_min (fun i => IsDiscreteValuationRing.addVal R (a i))
  have hd : ∀ k, a i ∣ a k := fun k =>
    IsDiscreteValuationRing.addVal_le_iff_dvd.mp (hi k)
  have hn : a i ≠ 0 := by
    intro h
    have := hd j
    rw [h, zero_dvd_iff] at this
    exact hj this
  choose p hp using hd
  refine ⟨a i, p, hn, hp, i, ?_⟩
  apply mul_left_cancel₀ hn
  simpa using (hp i).symm

/-- Actual fraction-field normalization, with an entry equal to one. -/
theorem fraction_family_normalization {ι : Type*} [Finite ι]
    (q : ι → K) (hq : ∃ i, q i ≠ 0) :
    ∃ (s : K) (p : ι → R), s ≠ 0 ∧
      (∀ i, algebraMap R K (p i) = s * q i) ∧ ∃ i, p i = 1 := by
  classical
  obtain ⟨b, hb⟩ := IsLocalization.exist_integer_multiples_of_finite
    (nonZeroDivisors R) q
  choose a ha using hb
  have hb0 : (b : R) ≠ 0 := nonZeroDivisors.ne_zero b.property
  have hbK : algebraMap R K (b : R) ≠ 0 := by
    exact fun h => hb0 ((IsFractionRing.injective R K) (h.trans (map_zero _).symm))
  have han : ∃ i, a i ≠ 0 := by
    obtain ⟨i, hi⟩ := hq
    refine ⟨i, ?_⟩
    intro h
    have he := ha i
    rw [h, map_zero, Algebra.smul_def] at he
    exact (mul_ne_zero hbK hi) he.symm
  obtain ⟨d, p, hd, hp, hpi⟩ := integral_family_normalization a han
  have hdK : algebraMap R K d ≠ 0 :=
    fun h => hd ((IsFractionRing.injective R K) (h.trans (map_zero _).symm))
  refine ⟨algebraMap R K (b : R) / algebraMap R K d, p,
    div_ne_zero hbK hdK, ?_, hpi⟩
  intro i
  apply (mul_left_cancel₀ hdK)
  have he := ha i
  rw [hp i, map_mul, Algebra.smul_def] at he
  rw [he]
  field_simp

variable {n : Type*} [Fintype n]

/-- A nonzero matrix is a scalar multiple of a primitive integral matrix. -/
theorem matrix_normalization (Q : Matrix n n K) (hQ : Q ≠ 0) :
    ∃ (s : K) (P : Matrix n n R), s ≠ 0 ∧
      P.map (algebraMap R K) = s • Q ∧ ∃ i j, P i j = 1 := by
  classical
  have hn : ∃ ij : n × n, Q ij.1 ij.2 ≠ 0 := by
    by_contra h
    push Not at h
    apply hQ
    ext i j
    exact h (i, j)
  obtain ⟨s, p, hs, hp, ij, hij⟩ := fraction_family_normalization (R := R)
    (fun ij : n × n => Q ij.1 ij.2) hn
  refine ⟨s, fun i j => p (i, j), hs, ?_, ij.1, ij.2, hij⟩
  ext i j
  exact hp (i, j)

/-- Primitive normalization preserves every integral intertwining equation.
The indexing type may be an arbitrary group; the proof uses only its supplied
matrices and hence also applies to several actions at once. -/
theorem intertwiner_normalization {G : Type*}
    (ρ τ : G → Matrix n n R) (Q : Matrix n n K) (hQ : Q ≠ 0)
    (hinter : ∀ g, (ρ g).map (algebraMap R K) * Q =
      Q * (τ g).map (algebraMap R K)) :
    ∃ (s : K) (P : Matrix n n R), s ≠ 0 ∧
      P.map (algebraMap R K) = s • Q ∧
      (∃ i j, P i j = 1) ∧ ∀ g, ρ g * P = P * τ g := by
  obtain ⟨s, P, hs, hP, hprim⟩ := matrix_normalization (R := R) Q hQ
  refine ⟨s, P, hs, hP, hprim, ?_⟩
  intro g
  have hm : (ρ g * P).map (algebraMap R K) =
      (P * τ g).map (algebraMap R K) := by
    simp only [Matrix.map_mul, hP, Matrix.mul_smul, Matrix.smul_mul, hinter g]
  ext i j
  exact IsFractionRing.injective R K (congrFun (congrFun hm i) j)

/-- A nonsingular comparison in positive rank admits a nonsingular primitive
integral comparison, preserving the actual actions. -/
theorem nonsingular_intertwiner_normalization [Nonempty n] [DecidableEq n]
    {G : Type*} (ρ τ : G → Matrix n n R) (Q : Matrix n n K)
    (hQ : Q.det ≠ 0)
    (hinter : ∀ g, (ρ g).map (algebraMap R K) * Q =
      Q * (τ g).map (algebraMap R K)) :
    ∃ P : Matrix n n R, P.det ≠ 0 ∧ (∃ i j, P i j = 1) ∧
      ∀ g, ρ g * P = P * τ g := by
  have hn : Q ≠ 0 := by
    intro h
    apply hQ
    simp [h]
  obtain ⟨s, P, hs, hP, hprim, hcomm⟩ := intertwiner_normalization ρ τ Q hn hinter
  refine ⟨P, ?_, hprim, hcomm⟩
  have hdet : (P.map (algebraMap R K)).det ≠ 0 := by
    rw [hP, Matrix.det_smul]
    exact mul_ne_zero (pow_ne_zero _ hs) hQ
  intro h
  apply hdet
  change ((algebraMap R K).mapMatrix P).det = 0
  rw [← RingHom.map_det, h, map_zero]

end PaperX.PrimitiveMatrix
