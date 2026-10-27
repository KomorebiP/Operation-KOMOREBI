import ResonantScalarHorizon
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Algebra.Group.Pi.Units

namespace Komorebi.StrongArtin.EffectiveResonance

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The matrix statement is restricted to roots in the fixed diagonal algebra. -/
theorem diagonal_root_iff_finite_horizon (d : ℕ) (hd : d ≠ 0)
    (u a : ι → PadicInt p) (ha : ∀ i, IsUnit (a i)) (m : ℕ) (hm : 0 < m) :
    (∃ x : ι → PadicInt p,
      IsUnit (Matrix.diagonal x) ∧
      (Matrix.diagonal x) ^ d = Matrix.diagonal u ∧
      ∀ i, PadicInt.toZModPow m (x i) = PadicInt.toZModPow m (a i)) ↔
    ∀ i, ∃ b : ZMod (p ^ scalarHorizon p d m),
      b ^ d = PadicInt.toZModPow (scalarHorizon p d m) (u i) ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m (a i) := by
  constructor
  · rintro ⟨x, _, hx, hxa⟩ i
    apply (scalar_root_iff_finite_horizon d hd (u i) (a i) (ha i) m hm).mp
    refine ⟨x i, ?_, hxa i⟩
    have he := congrArg (fun M : Matrix ι ι (PadicInt p) => M i i) hx
    simpa [Matrix.diagonal_pow] using he
  · intro h
    have hex : ∀ i, ∃ z : PadicInt p, z ^ d = u i ∧
        PadicInt.toZModPow m z = PadicInt.toZModPow m (a i) := fun i =>
      (scalar_root_iff_finite_horizon d hd (u i) (a i) (ha i) m hm).mpr (h i)
    choose x hx using hex
    refine ⟨x, ?_, ?_, fun i => (hx i).2⟩
    · apply Matrix.isUnit_diagonal.mpr
      exact Pi.isUnit_iff.mpr (fun i => unit_of_same_positive_prefix hm (ha i) (hx i).2)
    · rw [Matrix.diagonal_pow]
      congr 1
      funext i
      exact (hx i).1

/-- Produce an actual unit of the p-adic matrix ring from the finite certificates. -/
theorem exists_diagonal_matrix_unit_root (d : ℕ) (hd : d ≠ 0)
    (u a : ι → PadicInt p) (ha : ∀ i, IsUnit (a i)) (m : ℕ) (hm : 0 < m)
    (h : ∀ i, ∃ b : ZMod (p ^ scalarHorizon p d m),
      b ^ d = PadicInt.toZModPow (scalarHorizon p d m) (u i) ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m (a i)) :
    ∃ F : (Matrix ι ι (PadicInt p))ˣ,
      (F.val) ^ d = Matrix.diagonal u ∧
      (PadicInt.toZModPow m).mapMatrix F.val =
        Matrix.diagonal (fun i => PadicInt.toZModPow m (a i)) := by
  obtain ⟨x, hunit, hpow, hx⟩ :=
    (diagonal_root_iff_finite_horizon d hd u a ha m hm).mpr h
  obtain ⟨F, hF⟩ := hunit
  refine ⟨F, by simpa [hF] using hpow, ?_⟩
  rw [hF]
  ext i j
  by_cases hij : i = j
  · subst j
    simpa using hx i
  · simp [hij]

end Komorebi.StrongArtin.EffectiveResonance
