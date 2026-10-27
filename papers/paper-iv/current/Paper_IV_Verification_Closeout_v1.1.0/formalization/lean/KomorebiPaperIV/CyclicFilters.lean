/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.RingTheory.PowerSeries.Basic

/-!
# Cyclic coefficient projectors

The analytic root-of-unity average in Paper IV acts on formal coefficients by
retaining one congruence class.  This file takes that coefficient action as the
formal definition and proves the projector laws without convergence hypotheses.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommSemiring R]

/-- The formal cyclic projector retaining degrees congruent to `j` modulo `N`. -/
def cyclicProjector (N j : ℕ) (f : R⟦X⟧) : R⟦X⟧ :=
  PowerSeries.mk fun n => if n % N = j % N then PowerSeries.coeff n f else 0

@[simp]
theorem coeff_cyclicProjector (N j n : ℕ) (f : R⟦X⟧) :
    PowerSeries.coeff n (cyclicProjector N j f) =
      if n % N = j % N then PowerSeries.coeff n f else 0 := by
  simp [cyclicProjector]

theorem cyclicProjector_idempotent (N j : ℕ) (f : R⟦X⟧) :
    cyclicProjector N j (cyclicProjector N j f) = cyclicProjector N j f := by
  ext n
  by_cases h : n % N = j % N <;> simp [h]

theorem cyclicProjector_orthogonal {N i j : ℕ} (hij : i % N ≠ j % N) (f : R⟦X⟧) :
    cyclicProjector N i (cyclicProjector N j f) = 0 := by
  ext n
  by_cases hi : n % N = i % N
  · have hj : n % N ≠ j % N := fun h => hij (hi.symm.trans h)
    simp only [coeff_cyclicProjector, hi, hij, ↓reduceIte, map_zero]
  · simp [hi]

theorem cyclicProjector_eq_zero_of_residue_ne {N j n : ℕ} (h : n % N ≠ j % N)
    (f : R⟦X⟧) :
    PowerSeries.coeff n (cyclicProjector N j f) = 0 := by
  simp [h]

theorem cyclicProjector_eq_of_mod_eq {N i j : ℕ} (hij : i % N = j % N) (f : R⟦X⟧) :
    cyclicProjector N i f = cyclicProjector N j f := by
  ext n
  simp only [coeff_cyclicProjector]
  rw [hij]

theorem cyclicProjector_add (N j : ℕ) (f g : R⟦X⟧) :
    cyclicProjector N j (f + g) = cyclicProjector N j f + cyclicProjector N j g := by
  ext n
  by_cases h : n % N = j % N <;> simp [h]

theorem cyclicProjector_sum {I : Type*} (N j : ℕ) (s : Finset I) (f : I → R⟦X⟧) :
    cyclicProjector N j (∑ i ∈ s, f i) = ∑ i ∈ s, cyclicProjector N j (f i) := by
  classical
  induction s using Finset.induction_on with
  | empty =>
      ext n
      simp [cyclicProjector]
  | @insert a s ha ih =>
      rw [Finset.sum_insert ha, Finset.sum_insert ha, cyclicProjector_add, ih]

/-- The `N` residue projectors resolve the identity. -/
theorem sum_cyclicProjector {N : ℕ} (hN : 0 < N) (f : R⟦X⟧) :
    (∑ j ∈ Finset.range N, cyclicProjector N j f) = f := by
  ext n
  rw [map_sum]
  rw [Finset.sum_eq_single (n % N)]
  · simp [Nat.mod_eq_of_lt (Nat.mod_lt n hN)]
  · intro j hj hne
    have hjN : j < N := Finset.mem_range.mp hj
    have hmod : j % N = j := Nat.mod_eq_of_lt hjN
    have hres : n % N ≠ j % N := by simpa [hmod] using hne.symm
    simp [hres]
  · exact fun hmem => (hmem (Finset.mem_range.mpr (Nat.mod_lt n hN))).elim

/-- Multiplying two pure packets adds their labels modulo `N`. -/
theorem cyclicProjector_product_packet (N i j : ℕ) (f g : R⟦X⟧) :
    cyclicProjector N ((i + j) % N)
        (cyclicProjector N i f * cyclicProjector N j g) =
      cyclicProjector N i f * cyclicProjector N j g := by
  ext n
  by_cases hn : n % N = (i + j) % N
  · simp [hn]
  · simp only [coeff_cyclicProjector, hn, Nat.mod_mod, ↓reduceIte]
    symm
    rw [PowerSeries.coeff_mul]
    apply Finset.sum_eq_zero
    intro p hp
    by_cases hi : p.1 % N = i % N
    · by_cases hj : p.2 % N = j % N
      · exfalso
        apply hn
        have hpadd : p.1 + p.2 = n := Finset.mem_antidiagonal.mp hp
        calc
          n % N = (p.1 + p.2) % N := by rw [hpadd]
          _ = (p.1 % N + p.2 % N) % N := Nat.add_mod _ _ _
          _ = (i % N + j % N) % N := by rw [hi, hj]
          _ = (i + j) % N := (Nat.add_mod i j N).symm
      · simp [hj]
    · simp [hi]

/-- A projector with any other label kills a pure packet product. -/
theorem cyclicProjector_product_other {N i j k : ℕ}
    (hk : k % N ≠ (i + j) % N) (f g : R⟦X⟧) :
    cyclicProjector N k (cyclicProjector N i f * cyclicProjector N j g) = 0 := by
  rw [← cyclicProjector_product_packet N i j f g]
  apply cyclicProjector_orthogonal (R := R)
  simpa using hk

/-- The full cyclic product law, expressed as a finite double packet sum. -/
theorem cyclic_product_law {N : ℕ} (hN : 0 < N) (k : ℕ) (f g : R⟦X⟧) :
    cyclicProjector N k (f * g) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k % N then
          cyclicProjector N i f * cyclicProjector N j g
        else 0 := by
  calc
    cyclicProjector N k (f * g) =
        cyclicProjector N k
          ((∑ i ∈ Finset.range N, cyclicProjector N i f) *
            (∑ j ∈ Finset.range N, cyclicProjector N j g)) := by
      rw [sum_cyclicProjector hN, sum_cyclicProjector hN]
    _ = ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
          if (i + j) % N = k % N then
            cyclicProjector N i f * cyclicProjector N j g
          else 0 := by
      rw [Finset.sum_mul]
      simp_rw [Finset.mul_sum]
      rw [cyclicProjector_sum]
      apply Finset.sum_congr rfl
      intro i hi
      rw [cyclicProjector_sum]
      apply Finset.sum_congr rfl
      intro j hj
      by_cases hlabel : (i + j) % N = k % N
      · simp only [hlabel, ↓reduceIte]
        rw [cyclicProjector_eq_of_mod_eq (i := k) (j := (i + j) % N)
          (by simpa using hlabel.symm)]
        exact cyclicProjector_product_packet N i j f g
      · simp only [hlabel, ↓reduceIte]
        exact cyclicProjector_product_other (R := R) (fun h => hlabel h.symm) f g

end

end Komorebi.PaperIV
