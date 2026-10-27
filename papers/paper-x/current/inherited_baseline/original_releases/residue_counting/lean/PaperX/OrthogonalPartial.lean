import PaperX.OrthogonalProjectors

/-! Sums and complements of finite, not necessarily complete, orthogonal
families of actual equivariant projectors. -/
set_option autoImplicit false
namespace PaperX.OrthogonalPartial
open PaperX.RepresentationLimits PaperX.MatrixProjector
open scoped BigOperators

variable {R Γ ι J : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι]
  {ρ : MatrixRep R Γ ι}

variable (P : J → Projector ρ) (s : Finset J)
  (horth : ∀ i ∈ s, ∀ j ∈ s, i ≠ j → (P i).matrix * (P j).matrix = 0)

include horth in
theorem sum_mul_projector (i : J) (hi : i ∈ s) :
    (∑ j ∈ s, (P j).matrix) * (P i).matrix = (P i).matrix := by
  rw [Finset.sum_mul]
  exact Finset.sum_eq_single i
    (fun j hj hji => horth j hj i hi hji)
    (fun h => (h hi).elim) |>.trans (P i).idempotent

include horth in
theorem projector_mul_sum (i : J) (hi : i ∈ s) :
    (P i).matrix * (∑ j ∈ s, (P j).matrix) = (P i).matrix := by
  rw [Finset.mul_sum]
  exact Finset.sum_eq_single i
    (fun j hj hji => horth i hi j hj (Ne.symm hji))
    (fun h => (h hi).elim) |>.trans (P i).idempotent

include horth in
theorem sum_idempotent :
    (∑ i ∈ s, (P i).matrix) * (∑ i ∈ s, (P i).matrix) =
      ∑ i ∈ s, (P i).matrix := by
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl (fun i hi => sum_mul_projector P s horth i hi)

theorem sum_commutes (g : Γ) :
    ρ g * (∑ i ∈ s, (P i).matrix) = (∑ i ∈ s, (P i).matrix) * ρ g := by
  rw [Finset.mul_sum, Finset.sum_mul]
  exact Finset.sum_congr rfl (fun i _ => (P i).commutes g)

def complement : Projector ρ where
  matrix := 1 - ∑ i ∈ s, (P i).matrix
  idempotent := by
    simp only [sub_mul, mul_sub, one_mul, mul_one, sum_idempotent P s horth,
      sub_self, sub_zero]
  commutes g := by
    rw [mul_sub, sub_mul, mul_one, one_mul, sum_commutes P s g]

theorem complement_matrix :
    (complement P s horth).matrix = 1 - ∑ i ∈ s, (P i).matrix := rfl

theorem complement_mul_projector (i : J) (hi : i ∈ s) :
    (complement P s horth).matrix * (P i).matrix = 0 := by
  rw [complement_matrix, sub_mul, one_mul, sum_mul_projector P s horth i hi,
    sub_self]

theorem projector_mul_complement (i : J) (hi : i ∈ s) :
    (P i).matrix * (complement P s horth).matrix = 0 := by
  rw [complement_matrix, mul_sub, mul_one, projector_mul_sum P s horth i hi,
    sub_self]

theorem complement_add_sum :
    (complement P s horth).matrix + (∑ i ∈ s, (P i).matrix) = 1 := by
  exact sub_add_cancel _ _

/-- A family at one quotient precision, transported to a shallower precision
of the same supplied integral carrier. The matrix formula is definitional. -/
def reduceFamily [Fintype J] (I : Ideal R) (ρ : MatrixRep R Γ ι)
    {k m : ℕ} (h : k ≤ m)
    (Q : OrthogonalProjectors.Family (reduce I ρ m) J) :
    OrthogonalProjectors.Family (reduce I ρ k) J where
  projector i := {
    matrix := (Q.projector i).matrix.map (Ideal.Quotient.factorPow I h)
    idempotent := by rw [← Matrix.map_mul, (Q.projector i).idempotent]
    commutes g := by
      have hc := ((Q.projector i).changeCoefficients
        (Ideal.Quotient.factorPow I h)).commutes g
      change transition I h (reduce I ρ m) g *
        ((Q.projector i).matrix.map (Ideal.Quotient.factorPow I h)) =
        ((Q.projector i).matrix.map (Ideal.Quotient.factorPow I h)) *
          transition I h (reduce I ρ m) g at hc
      simpa only [transition_reduce] using hc }
  orthogonal i j hij := by
    change ((Q.projector i).matrix.map (Ideal.Quotient.factorPow I h)) *
      ((Q.projector j).matrix.map (Ideal.Quotient.factorPow I h)) = 0
    rw [← Matrix.map_mul, Q.orthogonal i j hij, Matrix.map_zero]
    exact map_zero _
  total := by
    change ∑ i, (Ideal.Quotient.factorPow I h).mapMatrix (Q.projector i).matrix = 1
    rw [← map_sum, Q.total, map_one]

theorem reduceFamily_matrix [Fintype J] (I : Ideal R) (ρ : MatrixRep R Γ ι)
    {k m : ℕ} (h : k ≤ m)
    (Q : OrthogonalProjectors.Family (reduce I ρ m) J) (i : J) :
    ((reduceFamily I ρ h Q).projector i).matrix =
      (Q.projector i).matrix.map (Ideal.Quotient.factorPow I h) := rfl

end PaperX.OrthogonalPartial
