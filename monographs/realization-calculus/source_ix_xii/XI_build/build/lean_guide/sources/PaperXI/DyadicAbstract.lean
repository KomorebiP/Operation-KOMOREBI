import PaperXI.SymplecticCoordinates
import PaperXI.DyadicBasisConsequences
import PaperXI.DyadicBasisCounts

/-! Intrinsic Arf invariants and dyadic formulas under only the abstract
finite-dimensional alternating nondegenerate hypotheses. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicAbstract
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates

variable {V : Type*} [AddCommGroup V] [Module F2 V] [FiniteDimensional F2 V]

def coordinates (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    V ≃ₗ[F2] (Fin (Module.finrank F2 V / 2) → F2 × F2) :=
  Classical.choose (PaperXI.SymplecticCoordinates.exists_half_coordinates b ha hn)

theorem coordinates_form (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∀ x y, b x y = symplectic (coordinates b ha hn x) (coordinates b ha hn y) :=
  Classical.choose_spec (PaperXI.SymplecticCoordinates.exists_half_coordinates b ha hn)

def arf (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) : F2 :=
  PaperXI.DyadicBasis.basisArf (coordinates b ha hn) q

/-- The intrinsic Arf value agrees with the source's paired-basis definition
for every symplectic coordinate map and every finite index type. -/
theorem arf_eq_basis {ι : Type*} [Fintype ι]
    (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (e : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y)) (q : Refinement b) :
    arf b ha hn q = PaperXI.DyadicBasis.basisArf e q :=
  PaperXI.DyadicDimension.basisArf_independent (coordinates b ha hn) e
    (coordinates_form b ha hn) he q

/-- The literal finite Gauss sum; a finite enumeration is constructed from
the proved coordinate equivalence. -/
def gaussSum (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) : ℤ :=
  let : Fintype V := Fintype.ofEquiv
    (Fin (Module.finrank F2 V / 2) → F2 × F2) (coordinates b ha hn).symm.toEquiv
  ∑ x : V, sign (q.value x)

theorem gaussSum_eq_sum [Fintype V] (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) : gaussSum b ha hn q = ∑ x : V, sign (q.value x) := by
  unfold gaussSum
  rw [show Fintype.ofEquiv (Fin (Module.finrank F2 V / 2) → F2 × F2)
    (coordinates b ha hn).symm.toEquiv = ‹Fintype V› from Subsingleton.elim _ _]

/-- Paper XI 13.5, with no supplied coordinate hypothesis. -/
theorem gauss_sum (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) :
    gaussSum b ha hn q = sign (arf b ha hn q) * 2 ^ (Module.finrank F2 V / 2) := by
  let : Fintype V := Fintype.ofEquiv
    (Fin (Module.finrank F2 V / 2) → F2 × F2) (coordinates b ha hn).symm.toEquiv
  rw [gaussSum_eq_sum]
  simpa only [Fintype.card_fin, arf] using
    PaperXI.DyadicBasis.gauss_sum (coordinates b ha hn) (coordinates_form b ha hn) q

def normalizedGaussSign (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) : ℚ :=
  (gaussSum b ha hn q : ℚ) / (2 : ℚ) ^ (Module.finrank F2 V / 2)

theorem normalizedGaussSign_eq_sign (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) :
    normalizedGaussSign b ha hn q = (sign (arf b ha hn q) : ℚ) := by
  unfold normalizedGaussSign
  rw [gauss_sum]
  push_cast
  exact mul_div_cancel_right₀ _ (pow_ne_zero _ (by norm_num : (2 : ℚ) ≠ 0))

/-- Paper XI 13.8 for the actual refinement q + b(v,-). -/
theorem arf_translation (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) (v : V) :
    arf b ha hn (addLinear q (b v)) = arf b ha hn q + q.value v := by
  exact PaperXI.DyadicBasisConsequences.arf_translation
    (coordinates b ha hn) (coordinates_form b ha hn) q v

/-- Paper XI 13.7: both Arf invariants and opposite normalized Gauss signs
occur for the same polar form on every nonzero symplectic space. -/
theorem opposite_refinements [Nontrivial V] (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∃ q r : Refinement b,
      arf b ha hn q = 0 ∧ arf b ha hn r = 1 ∧
      normalizedGaussSign b ha hn q = 1 ∧ normalizedGaussSign b ha hn r = -1 := by
  let : Fintype V := Fintype.ofEquiv
    (Fin (Module.finrank F2 V / 2) → F2 × F2) (coordinates b ha hn).symm.toEquiv
  have hp : 0 < Module.finrank F2 V / 2 := by
    simpa only [Fintype.card_fin] using
      PaperXI.DyadicDimension.card_pos (coordinates b ha hn)
  obtain ⟨q, r, hq, hr, _⟩ := PaperXI.DyadicBasisConsequences.opposite_refinements
    (coordinates b ha hn) (coordinates_form b ha hn) ⟨0, hp⟩
  have hq' : arf b ha hn q = 0 := hq
  have hr' : arf b ha hn r = 1 := hr
  refine ⟨q, r, hq', hr', ?_, ?_⟩
  · rw [normalizedGaussSign_eq_sign, hq']
    norm_num [sign]
  · rw [normalizedGaussSign_eq_sign, hr']
    norm_num [sign]

/-- Paper XI 13.9, counting the complete even Arf fiber, including rank zero. -/
theorem even_count (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    (Nat.card {q : Refinement b // arf b ha hn q = 0} : ℚ) =
      (2 : ℚ) ^ (((Module.finrank F2 V / 2 : ℕ) : ℤ) - 1) *
        ((2 : ℚ) ^ (Module.finrank F2 V / 2) + 1) := by
  have h := PaperXI.DyadicBasisCounts.even_count
    (coordinates b ha hn) (coordinates_form b ha hn)
  simpa [arf] using h

/-- Paper XI 13.9, counting the complete odd Arf fiber, including rank zero. -/
theorem odd_count (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    (Nat.card {q : Refinement b // arf b ha hn q = 1} : ℚ) =
      (2 : ℚ) ^ (((Module.finrank F2 V / 2 : ℕ) : ℤ) - 1) *
        ((2 : ℚ) ^ (Module.finrank F2 V / 2) - 1) := by
  have h := PaperXI.DyadicBasisCounts.odd_count
    (coordinates b ha hn) (coordinates_form b ha hn)
  simpa [arf] using h

/-- The displayed 13.5 formula with the paper's explicit dimension 2r. -/
theorem gauss_sum_of_finrank [Fintype V] (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (q : Refinement b) (r : ℕ) (hdim : Module.finrank F2 V = 2 * r) :
    (∑ x : V, sign (q.value x)) = sign (arf b ha hn q) * 2 ^ r := by
  rw [← gaussSum_eq_sum b ha hn q, gauss_sum]
  have hr : Module.finrank F2 V / 2 = r := by omega
  rw [hr]

/-- The displayed even-refinement count with the paper's dimension parameter. -/
theorem even_count_of_finrank (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (r : ℕ) (hdim : Module.finrank F2 V = 2 * r) :
    (Nat.card {q : Refinement b // arf b ha hn q = 0} : ℚ) =
      (2 : ℚ) ^ ((r : ℤ) - 1) * ((2 : ℚ) ^ r + 1) := by
  have hr : Module.finrank F2 V / 2 = r := by omega
  simpa only [hr] using even_count b ha hn

/-- The displayed odd-refinement count with the paper's dimension parameter. -/
theorem odd_count_of_finrank (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (r : ℕ) (hdim : Module.finrank F2 V = 2 * r) :
    (Nat.card {q : Refinement b // arf b ha hn q = 1} : ℚ) =
      (2 : ℚ) ^ ((r : ℤ) - 1) * ((2 : ℚ) ^ r - 1) := by
  have hr : Module.finrank F2 V / 2 = r := by omega
  simpa only [hr] using odd_count b ha hn

end PaperXI.DyadicAbstract
