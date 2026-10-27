import Mathlib.RingTheory.Polynomial.Bernstein
import Mathlib.Algebra.MvPolynomial.Monad
import Mathlib.Analysis.SpecialFunctions.Bernstein
import Mathlib.Tactic

/-! Finite exact rational tensor-Bernstein witnesses and complete binary subdivision trees. -/
set_option autoImplicit false
namespace Komorebi.LSM.TensorBernsteinCertificate
open scoped BigOperators
open MvPolynomial
noncomputable section
abbrev Polynomial₂ := MvPolynomial (Fin 2) ℚ

noncomputable def value (p : Polynomial₂) (x : Fin 2 → ℝ) : ℝ :=
  MvPolynomial.eval₂ (algebraMap ℚ ℝ) x p

/-- All endpoints, widths, and submitted coefficients are rational. -/
structure Rectangle where
  lo : Fin 2 → ℚ
  hi : Fin 2 → ℚ
  proper : ∀ i,lo i<hi i

def Rectangle.width (R : Rectangle) (i : Fin 2) : ℚ := R.hi i-R.lo i

def Rectangle.domain (R : Rectangle) : Set (Fin 2 → ℝ) :=
  {x | ∀ i,x i∈Set.Icc (R.lo i : ℝ) (R.hi i : ℝ)}

def unitSquare : Set (Fin 2 → ℝ) := {x | ∀ i,x i∈Set.Icc (0 : ℝ) 1}

def Rectangle.localPolynomial (R : Rectangle) (p : Polynomial₂) : Polynomial₂ :=
  MvPolynomial.bind₁ (fun i => C (R.lo i)+C (R.width i)*X i) p

noncomputable def Rectangle.coordinate (R : Rectangle) (x : Fin 2 → ℝ) (i : Fin 2) : ℝ :=
  (x i-R.lo i)/(R.width i : ℝ)

theorem Rectangle.width_pos (R : Rectangle) (i : Fin 2) : 0<(R.width i : ℝ) := by
  exact_mod_cast sub_pos.mpr (R.proper i)

theorem Rectangle.coordinate_mem (R : Rectangle) {x : Fin 2 → ℝ} (hx : x∈R.domain) :
    R.coordinate x∈unitSquare := by
  intro i
  have hi := hx i
  have hw := R.width_pos i
  constructor
  · exact div_nonneg (sub_nonneg.mpr hi.1) hw.le
  · apply (div_le_one hw).mpr
    simpa [Rectangle.width] using sub_le_sub_right hi.2 (R.lo i : ℝ)

theorem Rectangle.value_local (R : Rectangle) (p : Polynomial₂) (x : Fin 2 → ℝ) :
    value (R.localPolynomial p) (R.coordinate x)=value p x := by
  change MvPolynomial.eval₂Hom (algebraMap ℚ ℝ) (R.coordinate x)
    (MvPolynomial.bind₁ (fun i => C (R.lo i)+C (R.width i)*X i) p)=_
  rw [MvPolynomial.eval₂Hom_bind₁]
  have he : (fun i => (MvPolynomial.eval₂Hom (algebraMap ℚ ℝ) (R.coordinate x))
      (C (R.lo i)+C (R.width i)*X i))=x := by
    funext i
    simp [Rectangle.coordinate]
    field_simp [(R.width_pos i).ne']
    ring
  rw [he]
  rfl

/-- The literal univariate Bernstein polynomial inserted in one tensor coordinate. -/
def basisPolynomial (n k : ℕ) (i : Fin 2) : Polynomial₂ :=
  C (n.choose k : ℚ)*X i^k*(1-X i)^(n-k)

noncomputable def basis (n k : ℕ) (x : ℝ) : ℝ :=
  (n.choose k : ℝ)*x^k*(1-x)^(n-k)

theorem basis_nonneg (n k : ℕ) {x : ℝ} (hx : x∈Set.Icc (0 : ℝ) 1) : 0≤basis n k x := by
  unfold basis
  have h0 := hx.1
  have h1 : 0≤1-x := sub_nonneg.mpr hx.2
  positivity

theorem basis_sum (n : ℕ) (x : ℝ) : ∑ k : Fin (n+1),basis n k x=1 := by
  have h := congrArg (Polynomial.eval x) (bernsteinPolynomial.sum ℝ n)
  rw [Fin.sum_univ_eq_sum_range (fun k => basis n k x)]
  simpa [basis,bernsteinPolynomial,Polynomial.eval_finsetSum] using h

theorem value_basisPolynomial (n k : ℕ) (i : Fin 2) (x : Fin 2 → ℝ) :
    value (basisPolynomial n k i) x=basis n k (x i) := by
  simp [value,basisPolynomial,basis]

def tensorPolynomial {m n : ℕ} (c : Fin (m+1) → Fin (n+1) → ℚ) : Polynomial₂ :=
  ∑ i,∑ j,C (c i j)*basisPolynomial m i 0*basisPolynomial n j 1

theorem value_tensorPolynomial {m n : ℕ} (c : Fin (m+1) → Fin (n+1) → ℚ)
    (x : Fin 2 → ℝ) : value (tensorPolynomial c) x=
      ∑ i,∑ j,(c i j : ℝ)*basis m i (x 0)*basis n j (x 1) := by
  simp [tensorPolynomial,value,MvPolynomial.eval₂_sum,basisPolynomial,basis]

/-- The identity is an exact equality of finitely supported rational polynomials. -/
structure LocalCertificate (p : Polynomial₂) (R : Rectangle) where
  degreeX : ℕ
  degreeY : ℕ
  coefficient : Fin (degreeX+1) → Fin (degreeY+1) → ℚ
  nonneg : ∀ i j,0≤coefficient i j
  identity : R.localPolynomial p=tensorPolynomial coefficient

theorem LocalCertificate.sound {p : Polynomial₂} {R : Rectangle} (cert : LocalCertificate p R)
    {x : Fin 2 → ℝ} (hx : x∈R.domain) : 0≤value p x := by
  rw [← R.value_local p x,cert.identity,value_tensorPolynomial]
  have hu := R.coordinate_mem hx
  apply Finset.sum_nonneg
  intro i _
  apply Finset.sum_nonneg
  intro j _
  exact mul_nonneg (mul_nonneg (by exact_mod_cast cert.nonneg i j)
    (basis_nonneg _ _ (hu 0))) (basis_nonneg _ _ (hu 1))

/-- A split is always a genuine midpoint split of the specified coordinate. -/
def Rectangle.lower (R : Rectangle) (axis : Fin 2) : Rectangle where
  lo := R.lo
  hi i := if i=axis then (R.lo i+R.hi i)/2 else R.hi i
  proper i := by
    split_ifs <;> linarith [R.proper i]

def Rectangle.upper (R : Rectangle) (axis : Fin 2) : Rectangle where
  lo i := if i=axis then (R.lo i+R.hi i)/2 else R.lo i
  hi := R.hi
  proper i := by
    split_ifs <;> linarith [R.proper i]

theorem Rectangle.split_cover (R : Rectangle) (axis : Fin 2) {x : Fin 2 → ℝ}
    (hx : x∈R.domain) : x∈(R.lower axis).domain ∨ x∈(R.upper axis).domain := by
  by_cases h : x axis≤((R.lo axis+R.hi axis)/2 : ℚ)
  · left
    intro i
    constructor
    · exact (hx i).1
    · by_cases he : i=axis
      · subst i
        simpa [Rectangle.lower] using h
      · simpa [Rectangle.lower,he] using (hx i).2
  · right
    intro i
    constructor
    · by_cases he : i=axis
      · subst i
        simpa [Rectangle.upper] using (le_of_lt (lt_of_not_ge h))
      · simpa [Rectangle.upper,he] using (hx i).1
    · exact (hx i).2

/-- Every internal node contains both children: an arbitrary rectangle list is not accepted. -/
inductive SubdivisionWitness (p : Polynomial₂) : Rectangle → Type
  | leaf {R} (certificate : LocalCertificate p R) : SubdivisionWitness p R
  | split {R} (axis : Fin 2) (lower : SubdivisionWitness p (R.lower axis))
      (upper : SubdivisionWitness p (R.upper axis)) : SubdivisionWitness p R

theorem SubdivisionWitness.sound {p : Polynomial₂} {R : Rectangle} (w : SubdivisionWitness p R)
    {x : Fin 2 → ℝ} (hx : x∈R.domain) : 0≤value p x := by
  induction w with
  | leaf cert => exact cert.sound hx
  | @split R axis lower upper ihl ihu =>
    rcases R.split_cover axis hx with hl|hu
    · exact ihl hl
    · exact ihu hu

def square : Rectangle where
  lo _ := -1
  hi _ := 1
  proper _ := by norm_num

theorem square_domain (x : Fin 2 → ℝ) :
    x∈square.domain ↔ ∀ i,x i∈Set.Icc (-1 : ℝ) 1 := by simp [Rectangle.domain,square]

end
end Komorebi.LSM.TensorBernsteinCertificate
