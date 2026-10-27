module

public import HurwitzConvolution
public import DifferenceFiltration

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DworkCriterion

open Hurwitz Mahler DifferenceFiltration

variable {R : Type*} [CommRing R]

/-- The actual operator U^(p+L)-U^p on Hurwitz coefficients. -/
def defect (p L : ℕ) (f : ℕ → R) (d : ℕ) : R := f (d+p+L)-f (d+p)

def defectIter (p L s : ℕ) (f : ℕ → R) : ℕ → R := (defect p L)^[s] f

@[simp] theorem defectIter_zero (p L : ℕ) (f : ℕ → R) : defectIter p L 0 f=f := rfl

theorem defectIter_succ (p L s : ℕ) (f : ℕ → R) (d : ℕ) :
    defectIter p L (s+1) f d = defectIter p L s f (d+p+L) - defectIter p L s f (d+p) := by
  rw [defectIter, Function.iterate_succ_apply']
  rfl

/-- Exact operator dictionary before any sparse-support specialization. -/
theorem defect_is_shifted_difference (p L s : ℕ) (f : ℕ → R) (d : ℕ) :
    defectIter p L s f d = difference L s f (d+p*s) := by
  induction s generalizing d with
  | zero => simp
  | succ s ih =>
    rw [defectIter_succ, ih, ih, difference_succ]
    congr 1 <;> congr 1 <;> ring

/-- The actual sparse Hurwitz coefficient sequence associated to the packet e. -/
def packed (N : ℕ) (e : ℕ → R) (d : ℕ) : R :=
  if N∣d then e (d/N) else 0

@[simp] theorem packed_multiple (N : ℕ) (hN : 0<N) (e : ℕ → R) (n : ℕ) :
    packed N e (N*n)=e n := by
  simp [packed, Nat.mul_div_right, hN]

/-- Whole-degree differences agree with differences of the original packet sequence. -/
theorem packet_difference (N h k n : ℕ) (hN : 0<N) (e : ℕ → R) :
    difference (N*h) k (packed N e) (N*n) = difference h k e n := by
  induction k generalizing n with
  | zero => simp [hN]
  | succ k ih =>
    rw [difference_succ, difference_succ, ← Nat.mul_add, ih, ih]

/-- Low-order extraction at the nonnegative degree N*n-p*k. -/
theorem defect_packet_extraction (p m h k n : ℕ) (hN : 0<m*p)
    (hk : k≤m*n) (e : ℕ → R) :
    defectIter p (m*p*h) k (packed (m*p) e) (m*p*n-p*k) = difference h k e n := by
  rw [defect_is_shifted_difference]
  have hd : p*k≤m*p*n := by
    calc
      p*k ≤ p*(m*n) := Nat.mul_le_mul_left p hk
      _ = m*p*n := by ring
  rw [Nat.sub_add_cancel hd, packet_difference (m*p) h k n hN e]

/-- Dwork-flatness stated as ideal divisibility, not field divisibility or a finite valuation default. -/
def flat (p : ℕ) (f : ℕ → R) : Prop :=
  ∀ s d, (p:R)^s ∣ defectIter p (p*(p-1)) s f d

/-- A sufficient condition for the full base-step bound. The flatness premise is explicit.
This theorem does not construct a flat integral lift of the general Euler packet. -/
theorem saturated_bound_of_flat (p m : ℕ) (hp : 0<p) (hm : m∣p-1)
    (hmpos : 0<m) (e : ℕ → R) (H : flat p (packed (m*p) e)) (k n : ℕ) :
    (p:R)^(min k (m*n)) ∣ difference ((p-1)/m) k e n := by
  apply saturated_bound_of_triangular
  intro r s hs
  have h := H s (m*p*r-p*s)
  have he : m*p*((p-1)/m) = p*(p-1) := by
    calc
      m*p*((p-1)/m) = p*(m*((p-1)/m)) := by ring
      _ = p*(p-1) := by rw [Nat.mul_div_cancel' hm]
  rw [← he, defect_packet_extraction p m ((p-1)/m) s r (Nat.mul_pos hmpos hp) hs e] at h
  exact h

end KomorebiPaperIX.DworkCriterion
