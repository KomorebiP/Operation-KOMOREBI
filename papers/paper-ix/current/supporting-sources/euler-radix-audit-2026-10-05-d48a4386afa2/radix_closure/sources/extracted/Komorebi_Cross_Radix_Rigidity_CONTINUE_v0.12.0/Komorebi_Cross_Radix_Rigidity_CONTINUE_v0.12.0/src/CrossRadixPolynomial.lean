import Mathlib.Algebra.Polynomial.Degree.Lemmas

namespace KomorebiCrossRadixPoly

universe u


/-- Arithmetic/polyphase section. -/
def coeffSection {A : Type u} (m r : Nat) (f : Nat → A) (n : Nat) : A :=
  f (m * n + r)

/-- Polynomial-exponential sequence `P(n) * z^n`. -/
def polyExp {R : Type u} [Semiring R]
    (P : Polynomial R) (z : R) (n : Nat) : R :=
  P.eval (n : R) * z ^ n

/-- Affine substitution induced by `n ↦ m*n+r`. -/
noncomputable def affineSubst {R : Type u} [Semiring R]
    (P : Polynomial R) (m r : Nat) : Polynomial R :=
  P.comp (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R))

/-- Exact section formula for a polynomial-exponential packet. -/
theorem coeffSection_polyExp
    {R : Type u} [CommRing R]
    (P : Polynomial R) (z : R) (m r n : Nat) :
    coeffSection m r (polyExp P z) n =
      z ^ r * polyExp (affineSubst P m r) (z ^ m) n := by
  simp only [coeffSection, polyExp, affineSubst, Polynomial.eval_comp,
    Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_C,
    Polynomial.eval_X, Nat.cast_add, Nat.cast_mul, pow_add, pow_mul]
  ac_rfl

/-- The affine polynomial used by a section has degree at most one. -/
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

/-- Arithmetic sectioning cannot increase the polynomial degree of `P(n)`. -/
theorem affineSubst_natDegree_le
    {R : Type u} [Semiring R]
    (P : Polynomial R) (m r : Nat) :
    (affineSubst P m r).natDegree ≤ P.natDegree := by
  unfold affineSubst
  calc
    (P.comp (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R))).natDegree
        ≤ P.natDegree *
          (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R)).natDegree :=
      Polynomial.natDegree_comp_le
    _ ≤ P.natDegree * 1 := Nat.mul_le_mul_left _ (affine_linear_natDegree_le_one m r)
    _ = P.natDegree := Nat.mul_one _

/-- Sectioning a polynomial-exponential packet produces another one of no larger degree. -/
theorem polynomial_exponential_section_closed
    {R : Type u} [CommRing R]
    (P : Polynomial R) (z : R) (m r : Nat) :
    ∃ Q : Polynomial R, ∃ w : R,
      Q.natDegree ≤ P.natDegree ∧
      ∀ n : Nat, coeffSection m r (polyExp P z) n = z ^ r * polyExp Q w n := by
  exact ⟨affineSubst P m r, z ^ m, affineSubst_natDegree_le P m r,
    fun n => coeffSection_polyExp P z m r n⟩

end KomorebiCrossRadixPoly

#print axioms KomorebiCrossRadixPoly.coeffSection_polyExp
#print axioms KomorebiCrossRadixPoly.affineSubst_natDegree_le
#print axioms KomorebiCrossRadixPoly.polynomial_exponential_section_closed
