import CrossRadixBellCommonHull
import Mathlib.RingTheory.Polynomial.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

noncomputable section
open Polynomial
open scoped BigOperators

namespace KomorebiCrossRadix

/-- The positive affine section operator on bounded quasi-polynomial profiles. -/
def quasiPolynomialSectionLinearMap
    (T d m r : ℕ) (hm : 0 < m) : Module.End ℂ (DegreeBoundedProfile T d) where
  toFun := quasiPolynomialSectionProfile T d m r hm
  map_add' P Q := by
    funext k
    apply Subtype.ext
    simp [quasiPolynomialSectionProfile]
  map_smul' c P := by
    funext k
    apply Subtype.ext
    simp [quasiPolynomialSectionProfile]

@[simp] theorem quasiPolynomialSectionLinearMap_apply
    (T d m r : ℕ) (hm : 0 < m) (P : DegreeBoundedProfile T d) :
    quasiPolynomialSectionLinearMap T d m r hm P =
      quasiPolynomialSectionProfile T d m r hm P := rfl

/-- Composition of positive affine profile sections. -/
theorem quasiPolynomialSectionProfile_comp
    (T d m r l s : ℕ) (hm : 0 < m) (hl : 0 < l)
    (P : DegreeBoundedProfile T d) :
    quasiPolynomialSectionProfile T d l s hl
        (quasiPolynomialSectionProfile T d m r hm P) =
      quasiPolynomialSectionProfile T d (m * l) (m * s + r) (Nat.mul_pos hm hl) P := by
  funext k
  apply Subtype.ext
  simp only [quasiPolynomialSectionProfile, boundedAffinePolynomialEquiv_apply]
  rw [Polynomial.comp_assoc]
  congr 1
  · congr 1
    push_cast
    ring
  · simp only [Polynomial.add_comp, Polynomial.mul_comp, Polynomial.C_comp, Polynomial.X_comp]
    simp only [Nat.cast_mul, Nat.cast_add, map_mul, map_add]
    ring

/-- The identity affine section fixes every bounded profile. -/
theorem quasiPolynomialSectionProfile_one_zero
    (T d : ℕ) (P : DegreeBoundedProfile T d) :
    quasiPolynomialSectionProfile T d 1 0 (by decide) P = P := by
  funext k
  apply Subtype.ext
  simp [quasiPolynomialSectionProfile]

/-- Positive affine orbit of a bounded quasi-polynomial profile. -/
def ProfileAffineOrbit (T d : ℕ) (P : DegreeBoundedProfile T d) :
    Set (DegreeBoundedProfile T d) :=
  {Q | ∃ m r : ℕ, ∃ hm : 0 < m,
    Q = quasiPolynomialSectionProfile T d m r hm P}

/-- The absolute linear orbit hull under all positive affine sections. -/
def ProfileOrbitHull (T d : ℕ) (P : DegreeBoundedProfile T d) :
    Submodule ℂ (DegreeBoundedProfile T d) :=
  Submodule.span ℂ (ProfileAffineOrbit T d P)

lemma profile_mem_ProfileAffineOrbit
    (T d : ℕ) (P : DegreeBoundedProfile T d) :
    P ∈ ProfileAffineOrbit T d P := by
  refine ⟨1, 0, by decide, ?_⟩
  symm
  exact quasiPolynomialSectionProfile_one_zero T d P

lemma profile_mem_ProfileOrbitHull
    (T d : ℕ) (P : DegreeBoundedProfile T d) :
    P ∈ ProfileOrbitHull T d P :=
  Submodule.subset_span (profile_mem_ProfileAffineOrbit T d P)

lemma ProfileAffineOrbit_section_closed
    (T d l s : ℕ) (hl : 0 < l) (P Q : DegreeBoundedProfile T d)
    (hQ : Q ∈ ProfileAffineOrbit T d P) :
    quasiPolynomialSectionProfile T d l s hl Q ∈ ProfileAffineOrbit T d P := by
  rcases hQ with ⟨m, r, hm, rfl⟩
  refine ⟨m * l, m * s + r, Nat.mul_pos hm hl, ?_⟩
  exact quasiPolynomialSectionProfile_comp T d m r l s hm hl P

/-- The orbit span is invariant under every positive affine section. -/
theorem ProfileOrbitHull_section_closed
    (T d l s : ℕ) (hl : 0 < l) (P : DegreeBoundedProfile T d)
    {Q : DegreeBoundedProfile T d} (hQ : Q ∈ ProfileOrbitHull T d P) :
    quasiPolynomialSectionProfile T d l s hl Q ∈ ProfileOrbitHull T d P := by
  let L := quasiPolynomialSectionLinearMap T d l s hl
  change L Q ∈ ProfileOrbitHull T d P
  refine Submodule.span_induction (p := fun Q _ => L Q ∈ ProfileOrbitHull T d P) ?_ ?_ ?_ ?_ hQ
  · intro x hx
    exact Submodule.subset_span (ProfileAffineOrbit_section_closed T d l s hl P x hx)
  · simpa only [map_zero] using (ProfileOrbitHull T d P).zero_mem
  · intro x y _ _ hx hy
    rw [map_add]
    exact (ProfileOrbitHull T d P).add_mem hx hy
  · intro c x _ hx
    rw [map_smul]
    exact (ProfileOrbitHull T d P).smul_mem c hx

/-- `ProfileOrbitHull` is minimal among linear subspaces containing `P` and invariant under
all positive affine profile sections. -/
theorem ProfileOrbitHull_minimal
    (T d : ℕ) (P : DegreeBoundedProfile T d)
    (H : Submodule ℂ (DegreeBoundedProfile T d))
    (hP : P ∈ H)
    (hclosed : ∀ m r : ℕ, ∀ hm : 0 < m, ∀ Q ∈ H,
      quasiPolynomialSectionProfile T d m r hm Q ∈ H) :
    ProfileOrbitHull T d P ≤ H := by
  rw [ProfileOrbitHull, Submodule.span_le]
  intro Q hQ
  rcases hQ with ⟨m, r, hm, rfl⟩
  exact hclosed m r hm P hP

/-- The minimal profile orbit hull never exceeds the full bounded profile dimension. -/
theorem ProfileOrbitHull_finrank_le
    (T d : ℕ) [NeZero T] (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (ProfileOrbitHull T d P) ≤ T * (d + 1) := by
  calc
    Module.finrank ℂ (ProfileOrbitHull T d P) ≤
        Module.finrank ℂ (DegreeBoundedProfile T d) :=
      Submodule.finrank_le (ProfileOrbitHull T d P)
    _ = T * (d + 1) := degreeBoundedProfile_finrank d

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.quasiPolynomialSectionProfile_comp
#print axioms KomorebiCrossRadix.ProfileOrbitHull_section_closed
#print axioms KomorebiCrossRadix.ProfileOrbitHull_minimal
#print axioms KomorebiCrossRadix.ProfileOrbitHull_finrank_le
