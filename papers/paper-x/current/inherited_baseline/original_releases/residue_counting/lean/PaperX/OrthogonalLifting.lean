import PaperX.CornerProjectors
import PaperX.OrthogonalPartial
import PaperX.PrecisionAveraging

/-! Simultaneous lifting of complete labeled orthogonal projector families.
All averaging takes place before correction. The retained depth therefore does
not depend on the number of labels. -/
set_option autoImplicit false
namespace PaperX.OrthogonalLifting
open PaperX.RepresentationLimits PaperX.MatrixProjector
open PaperX.OrthogonalProjectors PaperX.OrthogonalPartial
open PaperX.CornerProjectors
open scoped BigOperators

variable {R Γ ι J : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι] [Fintype J]

/-- Lift an arbitrary finite subset of a supplied orthogonal family, keeping
all selected components mutually orthogonal in the integral carrier. -/
theorem exists_partial (I : Ideal R) [IsAdicComplete I R]
    (k : ℕ) (hk : 0 < k) (ρ : MatrixRep R Γ ι)
    (Q : Family (reduce I ρ k) J) (A : J → Matrix ι ι R)
    (hA : ∀ i, (A i).map (Ideal.Quotient.mk (I^k)) = (Q.projector i).matrix)
    (hcomm : ∀ i g, ρ g * A i = A i * ρ g) (s : Finset J) :
    ∃ P : J → Projector ρ,
      (∀ i ∈ s, (P i).matrix.map (Ideal.Quotient.mk (I^k)) = (Q.projector i).matrix) ∧
      ∀ i ∈ s, ∀ j ∈ s, i ≠ j → (P i).matrix * (P j).matrix = 0 := by
  classical
  induction s using Finset.induction_on with
  | empty =>
    exact ⟨fun _ => ⟨0, by simp, fun _ => by simp⟩, by simp, by simp⟩
  | @insert a s ha ih =>
    obtain ⟨P, hred, horth⟩ := ih
    let f := Ideal.Quotient.mk (I^k)
    let C := complement P s horth
    have hCred : C.matrix.map f = 1 - ∑ j ∈ s, (Q.projector j).matrix := by
      change f.mapMatrix (1 - ∑ j ∈ s, (P j).matrix) = _
      rw [map_sub, map_one, map_sum]
      congr 1
      exact Finset.sum_congr rfl fun j hj => hred j hj
    have hleft : C.matrix.map f * (A a).map f = (A a).map f := by
      rw [hCred, hA, sub_mul, one_mul, Finset.sum_mul]
      have hz : ∑ j ∈ s, (Q.projector j).matrix * (Q.projector a).matrix = 0 := by
        apply Finset.sum_eq_zero
        intro j hj
        exact Q.orthogonal j a (by intro h; subst j; exact ha hj)
      rw [hz, sub_zero]
    have hright : (A a).map f * C.matrix.map f = (A a).map f := by
      rw [hCred, hA, mul_sub, mul_one, Finset.mul_sum]
      have hz : ∑ j ∈ s, (Q.projector a).matrix * (Q.projector j).matrix = 0 := by
        apply Finset.sum_eq_zero
        intro j hj
        exact Q.orthogonal a j (by intro h; subst j; exact ha hj)
      rw [hz, sub_zero]
    obtain ⟨E, hEred, hCE, hEC⟩ := exists_in_corner I k hk ρ C (A a) (hcomm a)
      (by rw [hA]; simpa only [pow_two] using (Q.projector a).idempotent)
      hleft hright
    refine ⟨Function.update P a E, ?_, ?_⟩
    · intro i hi
      rcases Finset.mem_insert.mp hi with h | h
      · subst i
        simpa only [Function.update_self] using hEred.trans (hA a)
      · have hia : i ≠ a := by intro hi; subst i; exact ha h
        simpa only [Function.update_of_ne hia] using hred i h
    · intro i hi j hj hij
      by_cases hia : i = a
      · subst i
        have hja : j ≠ a := Ne.symm hij
        have hjs : j ∈ s := (Finset.mem_insert.mp hj).resolve_left hja
        simp only [Function.update_self, Function.update_of_ne hja]
        calc
          E.matrix * (P j).matrix = (E.matrix * C.matrix) * (P j).matrix := by rw [hEC]
          _ = E.matrix * (C.matrix * (P j).matrix) := by rw [mul_assoc]
          _ = 0 := by rw [complement_mul_projector P s horth j hjs, mul_zero]
      · by_cases hja : j = a
        · subst j
          have his : i ∈ s := (Finset.mem_insert.mp hi).resolve_left hia
          simp only [Function.update_self, Function.update_of_ne hia]
          calc
            (P i).matrix * E.matrix = (P i).matrix * (C.matrix * E.matrix) := by rw [hCE]
            _ = ((P i).matrix * C.matrix) * E.matrix := by rw [mul_assoc]
            _ = 0 := by rw [projector_mul_complement P s horth i his, zero_mul]
        · simp only [Function.update_of_ne hia, Function.update_of_ne hja]
          exact horth i ((Finset.mem_insert.mp hi).resolve_left hia)
            j ((Finset.mem_insert.mp hj).resolve_left hja) hij

/-- Completeness recovers the sum-to-one equation, including the empty label
case, after all individual orthogonal projectors have been lifted. -/
theorem exists_family_of_equivariant_lifts (I : Ideal R) [IsAdicComplete I R]
    (k : ℕ) (hk : 0 < k) (ρ : MatrixRep R Γ ι)
    (Q : Family (reduce I ρ k) J) (A : J → Matrix ι ι R)
    (hA : ∀ i, (A i).map (Ideal.Quotient.mk (I^k)) = (Q.projector i).matrix)
    (hcomm : ∀ i g, ρ g * A i = A i * ρ g) :
    ∃ E : Family ρ J,
      ∀ i, (E.projector i).matrix.map (Ideal.Quotient.mk (I^k)) = (Q.projector i).matrix := by
  classical
  obtain ⟨P, hred, horth⟩ := exists_partial I k hk ρ Q A hA hcomm Finset.univ
  let C := complement P Finset.univ horth
  have hCzero : C.matrix.map (Ideal.Quotient.mk (I^k)) = 0 := by
    change (Ideal.Quotient.mk (I^k)).mapMatrix (1 - ∑ i, (P i).matrix) = 0
    rw [map_sub, map_one, map_sum]
    have hsum : ∑ i, (P i).matrix.map (Ideal.Quotient.mk (I^k)) = 1 := by
      calc
        _ = ∑ i, (Q.projector i).matrix := Finset.sum_congr rfl fun i _ => hred i (Finset.mem_univ i)
        _ = 1 := Q.total
    change 1 - (∑ i, (P i).matrix.map (Ideal.Quotient.mk (I^k))) = 0
    rw [hsum, sub_self]
  have hC := eq_zero_of_idempotent_reduces_zero I k hk C.matrix C.idempotent hCzero
  have htotal : ∑ i, (P i).matrix = 1 := (sub_eq_zero.mp hC).symm
  exact ⟨⟨P, fun i j hij => horth i (Finset.mem_univ i) j (Finset.mem_univ j) hij,
    htotal⟩, fun i => hred i (Finset.mem_univ i)⟩

 /-- Simultaneous lifting loses at most the one averaging cost `e`, independent
of the number of labels. The integral carrier is supplied; the projectors and
their complete orthogonal decomposition are constructed. -/
theorem exists_family_lift [IsDomain R] [Fintype Γ]
    (π : R) [IsAdicComplete (Ideal.span {π}) R]
    (e k : ℕ) (hk : 0 < k) (ρ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (Q : Family (reduce (Ideal.span {π}) ρ (e+k)) J) :
    ∃ E : Family ρ J,
      ∀ i, (E.projector i).matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        (Q.projector i).matrix.map
          (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) := by
  choose A hA hcomm using fun i =>
    PaperX.PrecisionAveraging.exists_intertwiner_lift π e k ρ ρ hΓ hdiv
      (Q.projector i).matrix (Q.projector i).commutes
  exact exists_family_of_equivariant_lifts (Ideal.span {π}) k hk ρ
    (reduceFamily (Ideal.span {π}) ρ (Nat.le_add_left k e) Q) A hA hcomm

end PaperX.OrthogonalLifting
