import Mathlib.Algebra.Polynomial.Degree.Lemmas

namespace KomorebiCrossRadix

universe u

/-- Arithmetic/polyphase section. -/
def coeffSection {A : Type u} (m r : Nat) (f : Nat → A) (n : Nat) : A :=
  f (m * n + r)

/-- A power of a torsion element depends only on its exponent modulo the torsion period. -/
theorem pow_eq_pow_mod_of_pow_eq_one
    {M : Type u} [Monoid M] (z : M) (T m : Nat) (hT : z ^ T = 1) :
    z ^ m = z ^ (m % T) := by
  calc
    z ^ m = z ^ (m % T + T * (m / T)) := by rw [Nat.mod_add_div]
    _ = z ^ (m % T) * z ^ (T * (m / T)) := by rw [pow_add]
    _ = z ^ (m % T) * (z ^ T) ^ (m / T) := by rw [pow_mul]
    _ = z ^ (m % T) := by simp [hT]

/-- Sectioning preserves a torsion period. -/
theorem torsion_closed_under_section_root
    {M : Type u} [CommMonoid M] (z : M) (T m : Nat) (hT : z ^ T = 1) :
    (z ^ m) ^ T = 1 := by
  calc
    (z ^ m) ^ T = z ^ (m * T) := by rw [pow_mul]
    _ = z ^ (T * m) := by rw [Nat.mul_comm]
    _ = (z ^ T) ^ m := by rw [pow_mul]
    _ = 1 := by simp [hT]

/-- Polynomial-exponential sequence `P(n) z^n`. -/
def polyExp {R : Type u} [Semiring R]
    (P : Polynomial R) (z : R) (n : Nat) : R :=
  P.eval (n : R) * z ^ n

/-- Affine polynomial substitution induced by the section address. -/
noncomputable def affineSubst {R : Type u} [Semiring R]
    (P : Polynomial R) (m r : Nat) : Polynomial R :=
  P.comp (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R))

/-- Exact section formula for polynomial-exponential packets. -/
theorem coeffSection_polyExp
    {R : Type u} [CommRing R]
    (P : Polynomial R) (z : R) (m r n : Nat) :
    coeffSection m r (polyExp P z) n =
      z ^ r * polyExp (affineSubst P m r) (z ^ m) n := by
  simp only [coeffSection, polyExp, affineSubst, Polynomial.eval_comp,
    Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_C,
    Polynomial.eval_X, Nat.cast_add, Nat.cast_mul, pow_add, pow_mul]
  ac_rfl

/-- The affine substitution polynomial has degree at most one. -/
theorem affine_linear_natDegree_le_one
    {R : Type u} [Semiring R] (m r : Nat) :
    (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R)).natDegree ≤ 1 := by
  have hmul :
      (Polynomial.C (m : R) * Polynomial.X).natDegree ≤ 1 := by
    calc
      (Polynomial.C (m : R) * Polynomial.X).natDegree
          ≤ (Polynomial.C (m : R)).natDegree + Polynomial.X.natDegree :=
        Polynomial.natDegree_mul_le
      _ ≤ 0 + 1 := Nat.add_le_add (by simp) Polynomial.natDegree_X_le
      _ = 1 := by rfl
  calc
    (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R)).natDegree
        ≤ max (Polynomial.C (m : R) * Polynomial.X).natDegree
            (Polynomial.C (r : R)).natDegree :=
      Polynomial.natDegree_add_le _ _
    _ ≤ max 1 0 := max_le_max hmul (by simp)
    _ = 1 := by rfl

/-- Affine sectioning does not increase polynomial degree. -/
theorem affineSubst_natDegree_le
    {R : Type u} [Semiring R] (P : Polynomial R) (m r : Nat) :
    (affineSubst P m r).natDegree ≤ P.natDegree := by
  unfold affineSubst
  calc
    (P.comp (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R))).natDegree
        ≤ P.natDegree *
          (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R)).natDegree :=
      Polynomial.natDegree_comp_le
    _ ≤ P.natDegree * 1 := Nat.mul_le_mul_left _ (affine_linear_natDegree_le_one m r)
    _ = P.natDegree := Nat.mul_one _

/-- **Cyclotomic packet closure.** An arithmetic section of a bounded-degree
polynomial-exponential packet is another packet of no larger degree. If the
source root has torsion period `T`, the new root has the same period and can
be normalized to one of the finite addresses `0,...,T-1`. -/
theorem cyclotomic_polyExp_section_closed
    {R : Type u} [CommRing R]
    (P : Polynomial R) (z : R) (T m r : Nat)
    (hTpos : 0 < T) (hT : z ^ T = 1) :
    ∃ Q : Polynomial R, ∃ w : R, ∃ q : Nat,
      Q.natDegree ≤ P.natDegree ∧
      q < T ∧
      w ^ T = 1 ∧
      w = z ^ q ∧
      ∀ n : Nat, coeffSection m r (polyExp P z) n = z ^ r * polyExp Q w n := by
  refine ⟨affineSubst P m r, z ^ m, m % T,
    affineSubst_natDegree_le P m r, Nat.mod_lt _ hTpos,
    torsion_closed_under_section_root z T m hT, ?_, ?_⟩
  · exact pow_eq_pow_mod_of_pow_eq_one z T m hT
  · intro n
    exact coeffSection_polyExp P z m r n

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.cyclotomic_polyExp_section_closed
