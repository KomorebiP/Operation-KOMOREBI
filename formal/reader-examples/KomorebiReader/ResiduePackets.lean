import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Algebra.Group.Equiv.Basic
import Mathlib.Data.Nat.ModEq

/-!
# Coefficient packets and transport through an additive coordinate equivalence

These results formalize coefficient masking, reconstruction and refinement used
in the factorial-lane and falling-factorial reader examples.  Coefficients may
belong to any additive commutative monoid.  Transport is conditional on an actual
additive equivalence between the specified carriers, so its inverse and
preservation of finite sums are part of the type.  The generic transport lemmas
also apply to finite-support or polynomial carriers once their equivalence and
projector laws have been supplied.  An arbitrary infinite coefficient sequence
is not identified with a polynomial.  No roots-of-unity formula, concrete
Stirling equivalence or analytic convergence statement is asserted here.
-/

set_option autoImplicit false

open scoped BigOperators

namespace Komorebi.Reader.ResiduePackets

variable {A B V W : Type*}
variable [AddCommMonoid A] [AddCommMonoid B] [AddCommMonoid V] [AddCommMonoid W]

/-- Keep precisely the coefficients whose indices have residue `r` modulo `N`.
The formula is defined also at `N = 0`; reconstruction requires `0 < N`. -/
def project (N r : ℕ) : (ℕ → A) →+ (ℕ → A) where
  toFun a k := if k % N = r then a k else 0
  map_zero' := by
    funext k
    simp
  map_add' a b := by
    funext k
    by_cases h : k % N = r <;> simp [h]

@[simp] theorem project_apply (N r : ℕ) (a : ℕ → A) (k : ℕ) :
    project N r a k = if k % N = r then a k else 0 := rfl

/-- Every packet projection is idempotent. -/
theorem project_idempotent (N r : ℕ) (a : ℕ → A) :
    project N r (project N r a) = project N r a := by
  funext k
  simp only [project_apply]
  split_ifs <;> rfl

/-- Different packet addresses cannot retain the same coefficient. -/
theorem project_orthogonal (N : ℕ) {r s : ℕ} (hrs : r ≠ s) (a : ℕ → A) :
    project N r (project N s a) = 0 := by
  funext k
  by_cases hk : k % N = r
  · simp [hk, hrs]
  · simp [hk]

/-- All residue packets reconstruct the entire coefficient sequence. -/
theorem reconstruct {N : ℕ} (hN : 0 < N) (a : ℕ → A) :
    (∑ r ∈ Finset.range N, project N r a) = a := by
  funext k
  simp only [Finset.sum_apply]
  rw [Finset.sum_eq_single (k % N)]
  · simp
  · intro r _ hr
    simp [Ne.symm hr]
  · intro h
    exact False.elim (h (Finset.mem_range.mpr (Nat.mod_lt k hN)))

/-- A finer packet lies wholly inside the coarse packet determined by its
address.  Divisibility of the moduli is necessary for this formula. -/
theorem project_refined_packet {N M : ℕ} (hNM : N ∣ M)
    (r s : ℕ) (a : ℕ → A) :
    project N r (project M s a) =
      if s % N = r then project M s a else 0 := by
  funext k
  by_cases hks : k % M = s
  · have hkn : k % N = s % N := by
      rw [← Nat.mod_mod_of_dvd k hNM, hks]
    by_cases hsr : s % N = r <;> simp [hks, hkn, hsr]
  · by_cases hsr : s % N = r <;> simp [hks, hsr]

/-- Refining from `N` to any positive multiple `M` preserves every coarse
packet exactly.  Only fine addresses with the matching coarse residue survive. -/
theorem refinement {N M : ℕ} (hM : 0 < M) (hNM : N ∣ M)
    (r : ℕ) (a : ℕ → A) :
    project N r a =
      ∑ s ∈ Finset.range M, if s % N = r then project M s a else 0 := by
  calc
    project N r a = project N r (∑ s ∈ Finset.range M, project M s a) := by
      rw [reconstruct hM]
    _ = ∑ s ∈ Finset.range M, project N r (project M s a) := map_sum _ _ _
    _ = _ := by
      apply Finset.sum_congr rfl
      intro s _
      exact project_refined_packet hNM r s a

/-- Carry an additive operation into new coordinates using its actual inverse. -/
def coordinateTransfer (e : V ≃+ W) (T : V →+ V) : W →+ W :=
  e.toAddMonoidHom.comp (T.comp e.symm.toAddMonoidHom)

@[simp] theorem coordinateTransfer_apply (e : V ≃+ W) (T : V →+ V) (w : W) :
    coordinateTransfer e T w = e (T (e.symm w)) := rfl

/-- Applying the transported operation to encoded data gives the encoding of
the operation on the original data. -/
theorem coordinateTransfer_on_coordinates (e : V ≃+ W)
    (T : V →+ V) (v : V) :
    coordinateTransfer e T (e v) = e (T v) := by
  simp

/-- Coordinate transfer respects composition in its original order. -/
theorem coordinateTransfer_comp (e : V ≃+ W) (T U : V →+ V) :
    coordinateTransfer e (T.comp U) =
      (coordinateTransfer e T).comp (coordinateTransfer e U) := by
  ext b
  simp

/-- Any supplied idempotent additive operator stays idempotent under transport. -/
theorem coordinateTransfer_idempotent (e : V ≃+ W) (P : V →+ V)
    (hP : ∀ v, P (P v) = P v) (w : W) :
    coordinateTransfer e P (coordinateTransfer e P w) = coordinateTransfer e P w := by
  simp only [coordinateTransfer_apply, e.symm_apply_apply, hP]

/-- Any supplied orthogonality relation survives transport. -/
theorem coordinateTransfer_orthogonal (e : V ≃+ W) (P Q : V →+ V)
    (hPQ : ∀ v, P (Q v) = 0) (w : W) :
    coordinateTransfer e P (coordinateTransfer e Q w) = 0 := by
  simp only [coordinateTransfer_apply, e.symm_apply_apply, hPQ, map_zero]

/-- Reconstruction by any supplied finite additive projector family is preserved
on the target carrier.  This statement does not enlarge either carrier. -/
theorem coordinateTransfer_reconstruct {I : Type*} (e : V ≃+ W)
    (P : I → V →+ V) (s : Finset I) (hP : ∀ v, ∑ i ∈ s, P i v = v) (w : W) :
    (∑ i ∈ s, coordinateTransfer e (P i) w) = w := by
  simp only [coordinateTransfer_apply]
  rw [← map_sum, hP, e.apply_symm_apply]

/-- Complete input and output families recover every interaction of the
transported operation, on any pair of additive-equivalent carriers. -/
theorem coordinateTransfer_block_reconstruction {I J : Type*} (e : V ≃+ W)
    (T : V →+ V) (P : I → V →+ V) (Q : J → V →+ V) (s : Finset I) (t : Finset J)
    (hP : ∀ v, ∑ i ∈ s, P i v = v) (hQ : ∀ v, ∑ j ∈ t, Q j v = v) (w : W) :
    coordinateTransfer e T w =
      ∑ i ∈ s, ∑ j ∈ t, coordinateTransfer e (P i)
        (coordinateTransfer e T (coordinateTransfer e (Q j) w)) := by
  symm
  calc
    _ = ∑ i ∈ s, coordinateTransfer e (P i)
        (∑ j ∈ t, coordinateTransfer e T (coordinateTransfer e (Q j) w)) := by
      apply Finset.sum_congr rfl
      intro i _
      exact (map_sum (coordinateTransfer e (P i)) _ _).symm
    _ = ∑ i ∈ s, coordinateTransfer e (P i) (coordinateTransfer e T w) := by
      rw [← map_sum, coordinateTransfer_reconstruct e Q t hQ]
    _ = _ := coordinateTransfer_reconstruct e P s hP _

/-- A projector in the new coordinates is the conjugate of its source
projector, with the source and target types fixed by `e`. -/
def transportedProject (e : (ℕ → A) ≃+ B) (N r : ℕ) : B →+ B :=
  coordinateTransfer e (project N r)

@[simp] theorem transportedProject_apply (e : (ℕ → A) ≃+ B)
    (N r : ℕ) (b : B) :
    transportedProject e N r b = e (project N r (e.symm b)) := rfl

theorem transported_idempotent (e : (ℕ → A) ≃+ B)
    (N r : ℕ) (b : B) :
    transportedProject e N r (transportedProject e N r b) =
      transportedProject e N r b := by
  simp only [transportedProject_apply, e.symm_apply_apply, project_idempotent]

theorem transported_orthogonal (e : (ℕ → A) ≃+ B)
    (N : ℕ) {r s : ℕ} (hrs : r ≠ s) (b : B) :
    transportedProject e N r (transportedProject e N s b) = 0 := by
  simp only [transportedProject_apply, e.symm_apply_apply, project_orthogonal N hrs,
    map_zero]

/-- Reconstruction survives the coordinate change because `e` preserves
finite sums, rather than merely being a bijection. -/
theorem transported_reconstruct (e : (ℕ → A) ≃+ B)
    {N : ℕ} (hN : 0 < N) (b : B) :
    (∑ r ∈ Finset.range N, transportedProject e N r b) = b := by
  simp only [transportedProject_apply]
  rw [← map_sum, reconstruct hN, e.apply_symm_apply]

/-- The coarse/fine refinement law also survives additive coordinate transport. -/
theorem transported_refinement (e : (ℕ → A) ≃+ B)
    {N M : ℕ} (hM : 0 < M) (hNM : N ∣ M) (r : ℕ) (b : B) :
    transportedProject e N r b =
      ∑ s ∈ Finset.range M, if s % N = r then transportedProject e M s b else 0 := by
  simp only [transportedProject_apply]
  rw [refinement hM hNM, map_sum]
  apply Finset.sum_congr rfl
  intro s _
  split_ifs <;> simp

/-- Keeping every input/output packet interaction reconstructs the transported
operation.  Input and output moduli may differ, and both must be positive. -/
theorem transfer_block_reconstruction (e : (ℕ → A) ≃+ B)
    (T : (ℕ → A) →+ (ℕ → A)) {N M : ℕ}
    (hN : 0 < N) (hM : 0 < M) (b : B) :
    coordinateTransfer e T b =
      ∑ r ∈ Finset.range N, ∑ s ∈ Finset.range M,
        transportedProject e N r
          (coordinateTransfer e T (transportedProject e M s b)) := by
  exact coordinateTransfer_block_reconstruction e T (project N) (project M)
    (Finset.range N) (Finset.range M) (reconstruct hN) (reconstruct hM) b

end Komorebi.Reader.ResiduePackets
