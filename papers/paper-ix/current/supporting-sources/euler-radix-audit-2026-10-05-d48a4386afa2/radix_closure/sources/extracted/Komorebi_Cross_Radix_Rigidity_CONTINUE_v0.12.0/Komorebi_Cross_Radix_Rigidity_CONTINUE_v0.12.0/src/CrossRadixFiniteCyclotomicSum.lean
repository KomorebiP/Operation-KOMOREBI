import Mathlib.Algebra.Polynomial.BigOperators

namespace KomorebiCrossRadix

universe u v

/-- Arithmetic/polyphase section. -/
def coeffSection {A : Type u} (m r : Nat) (f : Nat → A) (n : Nat) : A :=
  f (m * n + r)

/-- A power of a torsion element depends only on its exponent modulo its period. -/
theorem pow_eq_pow_mod_of_pow_eq_one
    {M : Type u} [Monoid M] (z : M) (T m : Nat) (hT : z ^ T = 1) :
    z ^ m = z ^ (m % T) := by
  calc
    z ^ m = z ^ (m % T + T * (m / T)) := by rw [Nat.mod_add_div]
    _ = z ^ (m % T) * z ^ (T * (m / T)) := by rw [pow_add]
    _ = z ^ (m % T) * (z ^ T) ^ (m / T) := by rw [pow_mul]
    _ = z ^ (m % T) := by simp [hT]

/-- Polynomial-exponential sequence. -/
def polyExp {R : Type u} [Semiring R]
    (P : Polynomial R) (z : R) (n : Nat) : R :=
  P.eval (n : R) * z ^ n

/-- Affine polynomial substitution induced by sectioning. -/
noncomputable def affineSubst {R : Type u} [Semiring R]
    (P : Polynomial R) (m r : Nat) : Polynomial R :=
  P.comp (Polynomial.C (m : R) * Polynomial.X + Polynomial.C (r : R))

/-- Exact section formula for one polynomial-exponential packet. -/
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

/-- A finite cyclotomic polynomial-exponential presentation. -/
def finiteCyclotomicSum
    {R : Type u} [CommRing R] {ι : Type v} [Fintype ι]
    (P : ι → Polynomial R) (q : ι → Nat) (z : R) (n : Nat) : R :=
  ∑ i : ι, polyExp (P i) (z ^ q i) n

/-- **Finite-sum cyclotomic section closure.** If all source root addresses are
inside a fixed torsion period `T` and all amplitudes have degree at most `d`,
then every arithmetic section has another finite presentation with the same
index set, the same degree bound, and root addresses still in `0,...,T-1`. -/
theorem finiteCyclotomicSum_section_closed
    {R : Type u} [CommRing R] {ι : Type v} [Fintype ι]
    (P : ι → Polynomial R) (q : ι → Nat) (z : R)
    (T d m r : Nat)
    (hTpos : 0 < T) (hT : z ^ T = 1)
    (hdeg : ∀ i, (P i).natDegree ≤ d) :
    ∃ Q : ι → Polynomial R, ∃ q' : ι → Nat,
      (∀ i, (Q i).natDegree ≤ d) ∧
      (∀ i, q' i < T) ∧
      (∀ i, (z ^ q' i) ^ T = 1) ∧
      ∀ n : Nat,
        coeffSection m r (finiteCyclotomicSum P q z) n =
          ∑ i : ι, (z ^ q i) ^ r * polyExp (Q i) (z ^ q' i) n := by
  let Q : ι → Polynomial R := fun i => affineSubst (P i) m r
  let q' : ι → Nat := fun i => (q i * m) % T
  refine ⟨Q, q', ?_, ?_, ?_, ?_⟩
  · intro i
    exact (affineSubst_natDegree_le (P i) m r).trans (hdeg i)
  · intro i
    exact Nat.mod_lt _ hTpos
  · intro i
    calc
      (z ^ q' i) ^ T = z ^ (q' i * T) := by rw [pow_mul]
      _ = z ^ (T * q' i) := by rw [Nat.mul_comm]
      _ = (z ^ T) ^ q' i := by rw [pow_mul]
      _ = 1 := by simp [hT]
  · intro n
    unfold coeffSection finiteCyclotomicSum
    apply Finset.sum_congr rfl
    intro i hi
    have hroot : (z ^ q i) ^ m = z ^ q' i := by
      calc
        (z ^ q i) ^ m = z ^ (q i * m) := by rw [← pow_mul]
        _ = z ^ ((q i * m) % T) := pow_eq_pow_mod_of_pow_eq_one z T (q i * m) hT
        _ = z ^ q' i := by rfl
    simpa [coeffSection, Q, hroot] using coeffSection_polyExp (P i) (z ^ q i) m r n

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.finiteCyclotomicSum_section_closed

namespace KomorebiCrossRadix

/-- A finite cyclotomic presentation can be re-normalized after sectioning by
absorbing the section-address scalar into the polynomial amplitude. -/
theorem finiteCyclotomicSum_section_closed_normalized
    {R : Type u} [CommRing R] {ι : Type v} [Fintype ι]
    (P : ι → Polynomial R) (q : ι → Nat) (z : R)
    (T d m r : Nat)
    (hTpos : 0 < T) (hT : z ^ T = 1)
    (hdeg : ∀ i, (P i).natDegree ≤ d) :
    ∃ Q : ι → Polynomial R, ∃ q' : ι → Nat,
      (∀ i, (Q i).natDegree ≤ d) ∧
      (∀ i, q' i < T) ∧
      ∀ n : Nat,
        coeffSection m r (finiteCyclotomicSum P q z) n =
          finiteCyclotomicSum Q q' z n := by
  let A : ι → Polynomial R := fun i => affineSubst (P i) m r
  let Q : ι → Polynomial R := fun i => Polynomial.C ((z ^ q i) ^ r) * A i
  let q' : ι → Nat := fun i => (q i * m) % T
  refine ⟨Q, q', ?_, ?_, ?_⟩
  · intro i
    exact (Polynomial.natDegree_C_mul_le ((z ^ q i) ^ r) (A i)).trans
      ((affineSubst_natDegree_le (P i) m r).trans (hdeg i))
  · intro i
    exact Nat.mod_lt _ hTpos
  · intro n
    unfold coeffSection finiteCyclotomicSum
    apply Finset.sum_congr rfl
    intro i hi
    have hroot : (z ^ q i) ^ m = z ^ q' i := by
      calc
        (z ^ q i) ^ m = z ^ (q i * m) := by rw [← pow_mul]
        _ = z ^ ((q i * m) % T) := pow_eq_pow_mod_of_pow_eq_one z T (q i * m) hT
        _ = z ^ q' i := by rfl
    have hsec := coeffSection_polyExp (P i) (z ^ q i) m r n
    simp only [coeffSection] at hsec
    rw [hroot] at hsec
    rw [hsec]
    simp only [Q, A, polyExp, Polynomial.eval_mul, Polynomial.eval_C]
    ac_rfl

/-- Agreement of two sequences from a fixed threshold onward. -/
def AgreesFrom {A : Type u} (N : Nat) (f g : Nat → A) : Prop :=
  ∀ n, N ≤ n → f n = g n

/-- Positive-width arithmetic sections preserve the same transient threshold. -/
theorem agreesFrom_coeffSection
    {A : Type u} (N m r : Nat) (f g : Nat → A)
    (hm : 0 < m) (hfg : AgreesFrom N f g) :
    AgreesFrom N (coeffSection m r f) (coeffSection m r g) := by
  intro n hn
  apply hfg
  have hm1 : 1 ≤ m := hm
  have hnm : n ≤ m * n := by
    simpa using Nat.mul_le_mul_right n hm1
  exact hn.trans (hnm.trans (Nat.le_add_right (m * n) r))

/-- **Eventual cyclotomic profile invariance.** If a sequence agrees after `N`
with a finite cyclotomic polynomial-exponential presentation of period `T`
and amplitude degree at most `d`, then every positive-width arithmetic section
again agrees after the *same* `N` with a presentation having the same `T` and
`d`. Thus sectioning cannot increase the transient threshold, torsion period,
or polynomial degree profile. -/
theorem eventualCyclotomicProfile_section_closed
    {R : Type u} [CommRing R] {ι : Type v} [Fintype ι]
    (a : Nat → R) (P : ι → Polynomial R) (q : ι → Nat) (z : R)
    (N T d m r : Nat)
    (hm : 0 < m) (hTpos : 0 < T) (hT : z ^ T = 1)
    (hdeg : ∀ i, (P i).natDegree ≤ d)
    (ha : AgreesFrom N a (finiteCyclotomicSum P q z)) :
    ∃ Q : ι → Polynomial R, ∃ q' : ι → Nat,
      (∀ i, (Q i).natDegree ≤ d) ∧
      (∀ i, q' i < T) ∧
      AgreesFrom N (coeffSection m r a) (finiteCyclotomicSum Q q' z) := by
  obtain ⟨Q, q', hQdeg, hq', hsec⟩ :=
    finiteCyclotomicSum_section_closed_normalized P q z T d m r hTpos hT hdeg
  refine ⟨Q, q', hQdeg, hq', ?_⟩
  have haSec := agreesFrom_coeffSection N m r a (finiteCyclotomicSum P q z) hm ha
  intro n hn
  calc
    coeffSection m r a n = coeffSection m r (finiteCyclotomicSum P q z) n := haSec n hn
    _ = finiteCyclotomicSum Q q' z n := hsec n

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.finiteCyclotomicSum_section_closed_normalized
#print axioms KomorebiCrossRadix.agreesFrom_coeffSection
#print axioms KomorebiCrossRadix.eventualCyclotomicProfile_section_closed

namespace KomorebiCrossRadix

/-- Fixed-radix section at depth `e` and address `s`. -/
def radixSection {A : Type u} (b e s : Nat) (f : Nat → A) : Nat → A :=
  coeffSection (b ^ e) s f

/-- The same eventual cyclotomic profile is valid for every depth of every
positive radix. The theorem deliberately does not require `s < b^e`; imposing
the usual residue-address bound is therefore a harmless specialization. -/
theorem eventualCyclotomicProfile_radixSection_closed
    {R : Type u} [CommRing R] {ι : Type v} [Fintype ι]
    (a : Nat → R) (P : ι → Polynomial R) (q : ι → Nat) (z : R)
    (N T d b e s : Nat)
    (hb : 0 < b) (hTpos : 0 < T) (hT : z ^ T = 1)
    (hdeg : ∀ i, (P i).natDegree ≤ d)
    (ha : AgreesFrom N a (finiteCyclotomicSum P q z)) :
    ∃ Q : ι → Polynomial R, ∃ q' : ι → Nat,
      (∀ i, (Q i).natDegree ≤ d) ∧
      (∀ i, q' i < T) ∧
      AgreesFrom N (radixSection b e s a) (finiteCyclotomicSum Q q' z) := by
  simpa [radixSection] using
    eventualCyclotomicProfile_section_closed a P q z N T d (b ^ e) s
      (Nat.pow_pos hb) hTpos hT hdeg ha

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.eventualCyclotomicProfile_radixSection_closed
