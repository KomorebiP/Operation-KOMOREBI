import Mathlib.Algebra.Group.Monoid

namespace KomorebiCrossRadix

universe u

/-- Arithmetic/polyphase section: keep indices `m*n+r`. -/
def coeffSection {A : Type u} (m r : Nat) (f : Nat → A) (n : Nat) : A :=
  f (m * n + r)

@[simp] theorem coeffSection_one_zero {A : Type u} (f : Nat → A) :
    coeffSection 1 0 f = f := by
  funext n
  simp [coeffSection]

theorem coeffSection_comp {A : Type u}
    (l s m r : Nat) (f : Nat → A) (n : Nat) :
    coeffSection m r (coeffSection l s f) n =
      coeffSection (l * m) (l * r + s) f n := by
  simp [coeffSection, Nat.mul_add, Nat.mul_assoc, Nat.add_assoc]

/-- Exact exponential factorization under an arithmetic section. -/
theorem pow_section_factor
    {M : Type u} [Monoid M] (z : M) (m r n : Nat) :
    z ^ (m * n + r) = (z ^ m) ^ n * z ^ r := by
  rw [pow_add, pow_mul]

/-- A power of a torsion element depends only on the exponent modulo its period. -/
theorem pow_eq_pow_mod_of_pow_eq_one
    {M : Type u} [Monoid M] (z : M) (T m : Nat) (hT : z ^ T = 1) :
    z ^ m = z ^ (m % T) := by
  calc
    z ^ m = z ^ (m % T + T * (m / T)) := by
      rw [Nat.mod_add_div]
    _ = z ^ (m % T) * z ^ (T * (m / T)) := by rw [pow_add]
    _ = z ^ (m % T) * (z ^ T) ^ (m / T) := by rw [pow_mul]
    _ = z ^ (m % T) := by simp [hT]

/-- Every power of a `T`-torsion element has a representative among addresses `< T`. -/
theorem torsion_power_has_finite_address
    {M : Type u} [Monoid M] (z : M) (T m : Nat)
    (hTpos : 0 < T) (hT : z ^ T = 1) :
    ∃ r, r < T ∧ z ^ m = z ^ r := by
  refine ⟨m % T, Nat.mod_lt _ hTpos, ?_⟩
  exact pow_eq_pow_mod_of_pow_eq_one z T m hT

/-- Taking an arithmetic section preserves the same torsion period. -/
theorem torsion_closed_under_section_root
    {M : Type u} [CommMonoid M] (z : M) (T m : Nat)
    (hT : z ^ T = 1) :
    (z ^ m) ^ T = 1 := by
  calc
    (z ^ m) ^ T = z ^ (m * T) := by rw [pow_mul]
    _ = z ^ (T * m) := by rw [Nat.mul_comm]
    _ = (z ^ T) ^ m := by rw [pow_mul]
    _ = 1 := by simp [hT]

/-- Pure cyclotomic packets are closed under arbitrary arithmetic sections. -/
theorem cyclotomic_exponential_section
    {M : Type u} [CommMonoid M] (z : M) (T m r : Nat)
    (hT : z ^ T = 1) :
    (∀ n, coeffSection m r (fun q => z ^ q) n = (z ^ m) ^ n * z ^ r) ∧
    (z ^ m) ^ T = 1 := by
  constructor
  · intro n
    exact pow_section_factor z m r n
  · exact torsion_closed_under_section_root z T m hT

/-- The new section root normalizes to one of finitely many torsion addresses. -/
theorem cyclotomic_section_root_finite
    {M : Type u} [CommMonoid M] (z : M) (T m : Nat)
    (hTpos : 0 < T) (hT : z ^ T = 1) :
    ∃ q, q < T ∧ z ^ m = z ^ q :=
  torsion_power_has_finite_address z T m hTpos hT

/-- Two successive resolution paths flatten to one affine section. -/
theorem two_resolution_paths_flatten {A : Type u}
    (l s m r : Nat) (f : Nat → A) :
    coeffSection m r (coeffSection l s f) =
      coeffSection (l * m) (l * r + s) f := by
  funext n
  exact coeffSection_comp l s m r f n

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.coeffSection_comp
#print axioms KomorebiCrossRadix.pow_eq_pow_mod_of_pow_eq_one
#print axioms KomorebiCrossRadix.cyclotomic_exponential_section
#print axioms KomorebiCrossRadix.cyclotomic_section_root_finite
#print axioms KomorebiCrossRadix.two_resolution_paths_flatten
