module

public import UnitTriangular
public import StandardWindow
public import CongruentialEuler

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.WindowIndependence

variable (p : ℕ) [Fact p.Prime]

/-- Unit pivots are derived from Lucas, in the actual p-adic integer ring. -/
theorem diagonal_padic_isUnit (m j : ℕ) (hj : j < p) (n : ℕ) :
    IsUnit (((m*p*n+j).choose (m*p*n) : ℕ) : ℤ_[p]) := by
  rw [PadicInt.isUnit_iff, PadicInt.norm_natCast_eq_one_iff]
  exact (Fact.out : p.Prime).coprime_iff_not_dvd.mpr
    (StandardWindow.standard_diagonal_not_divisible p m n j hj)

/-- No rational-to-finite-field cast is used: first construct an integral lift. -/
def diagonalUnit (m j : ℕ) (hj : j < p) (n : ℕ) : ℤ_[p]ˣ :=
  (diagonal_padic_isUnit p m j hj n).unit

@[simp] theorem diagonalUnit_coe (m j : ℕ) (hj : j < p) (n : ℕ) :
    (diagonalUnit p m j hj n : ℤ_[p]) = ((m*p*n+j).choose (m*p*n) : ℕ) :=
  (diagonal_padic_isUnit p m j hj n).unit_spec

def coeffPadic (m j : ℕ) (hj : j < p) : ℕ → ℤ_[p] :=
  UnitTriangular.solve (fun n q => ((m*p*n+j).choose (m*p*q) : ℤ_[p]))
    (fun n => if n=0 then 1 else 0) (diagonalUnit p m j hj)

/-- The p-adic construction satisfies the literal manuscript recurrence. -/
theorem coeffPadic_row (m j : ℕ) (hj : j < p) (n : ℕ) :
    ∑ q ∈ Finset.range (n+1),
      ((m*p*n+j).choose (m*p*q) : ℤ_[p]) * coeffPadic p m j hj q =
        if n=0 then 1 else 0 := by
  have h := UnitTriangular.solve_row
    (fun n q => ((m*p*n+j).choose (m*p*q) : ℤ_[p]))
    (fun n => if n=0 then 1 else 0) (diagonalUnit p m j hj)
    (diagonalUnit_coe p m j hj) n
  change (∑ k : Fin n, ((m*p*n+j).choose (m*p*k) : ℤ_[p]) * coeffPadic p m j hj k) +
    ((m*p*n+j).choose (m*p*n) : ℤ_[p]) * coeffPadic p m j hj n = _ at h
  rw [Fin.sum_univ_eq_sum_range (fun q => ((m*p*n+j).choose (m*p*q) : ℤ_[p]) * coeffPadic p m j hj q) n] at h
  simpa only [Finset.sum_range_succ] using h

/-- The integral lift represents the original rational Euler packet, for every row. -/
theorem coeffPadic_coe (m j : ℕ) (hj : j < p) (n : ℕ) :
    (coeffPadic p m j hj n : ℚ_[p]) = (Congruential.coeff (m*p) j n : ℚ_[p]) := by
  have h := UnitTriangular.solve_map_to_field (algebraMap ℤ_[p] ℚ_[p])
    (fun n q => ((m*p*n+j).choose (m*p*q) : ℤ_[p]))
    (fun n => if n=0 then 1 else 0) (diagonalUnit p m j hj)
    (diagonalUnit_coe p m j hj)
  have hq := UnitTriangular.field_solve_map (algebraMap ℚ ℚ_[p])
    (fun n q => (Congruential.row (m*p) j n q : ℚ)) Congruential.rhs n
  have hv := congrFun h n
  simp [Congruential.row, Congruential.rhs] at hq
  simp only [map_natCast, apply_ite, map_one, map_zero] at hv
  change (coeffPadic p m j hj n : ℚ_[p]) = _ at hv
  simpa only [Congruential.coeff, Congruential.row, Congruential.rhs, Int.cast_natCast] using hv.trans hq.symm

/-- A genuine norm/integrality theorem, not a total field-divisibility assertion. -/
theorem standard_window_integral (m j : ℕ) (hj : j < p) (n : ℕ) :
    ‖(Congruential.coeff (m*p) j n : ℚ_[p])‖ ≤ 1 := by
  rw [← coeffPadic_coe p m j hj n]
  exact (coeffPadic p m j hj n).property

/-- The residual inverse is independently constructed from the Lucas-reduced rows. -/
def reduced (m : ℕ) : ℕ → ZMod p :=
  Triangular.solve (fun n q => ((m*n).choose (m*q) : ZMod p))
    (fun n => if n=0 then 1 else 0)

theorem reduced_row (m n : ℕ) :
    ∑ q ∈ Finset.range (n+1), ((m*n).choose (m*q) : ZMod p) * reduced p m q =
      if n=0 then 1 else 0 := by
  have h := Triangular.solve_row
    (fun n q => ((m*n).choose (m*q) : ZMod p))
    (fun n => if n=0 then 1 else 0) (by intro k; simp) n
  change (∑ k : Fin n, ((m*n).choose (m*k) : ZMod p) * reduced p m k) +
    ((m*n).choose (m*n) : ZMod p) * reduced p m n = _ at h
  rw [Fin.sum_univ_eq_sum_range (fun q => ((m*n).choose (m*q) : ZMod p) * reduced p m q) n] at h
  simpa only [Finset.sum_range_succ] using h

theorem reduced_unique (m : ℕ) (a : ℕ → ZMod p)
    (ha : ∀ n, ∑ q ∈ Finset.range (n+1), ((m*n).choose (m*q) : ZMod p) * a q =
      if n=0 then 1 else 0) : a = reduced p m := by
  apply Triangular.solve_unique
  · intro n; simp
  · intro n
    rw [Fin.sum_univ_eq_sum_range (fun q => ((m*n).choose (m*q) : ZMod p) * a q) n]
    simpa only [Finset.sum_range_succ] using ha n

/-- Corollary 8.3: reduction of the original integral packet is independent of j. -/
theorem residue_independence (m j : ℕ) (hj : j < p) (n : ℕ) :
    PadicInt.toZMod (coeffPadic p m j hj n) = reduced p m n := by
  have hall : (fun n => PadicInt.toZMod (coeffPadic p m j hj n)) = reduced p m := by
    apply reduced_unique
    intro r
    have h := congrArg (PadicInt.toZMod : ℤ_[p] →+* ZMod p) (coeffPadic_row p m j hj r)
    simp only [map_sum, map_mul, map_natCast] at h
    have hb : PadicInt.toZMod (if r=0 then (1:ℤ_[p]) else 0) =
        (if r=0 then (1:ZMod p) else 0) := by
      split_ifs <;> simp
    rw [hb] at h
    rw [← h]
    
    apply Finset.sum_congr rfl
    intro q _
    have hrow : (((m*p*r+j).choose (m*p*q) : ℕ) : ZMod p) =
        ((m*r).choose (m*q) : ℕ) :=
      (ZMod.natCast_eq_natCast_iff _ _ _).mpr
        (StandardWindow.lucas_row_reduction p m r q j hj)
    rw [hrow]
  exact congrFun hall n

theorem two_window_addresses_agree (m j k : ℕ) (hj : j < p) (hk : k < p) (n : ℕ) :
    PadicInt.toZMod (coeffPadic p m j hj n) =
      PadicInt.toZMod (coeffPadic p m k hk n) := by
  rw [residue_independence, residue_independence]

/-- Actual ideal congruence between the two lifted rational coefficients. -/
theorem two_window_addresses_congruent (m j k : ℕ) (hj : j < p) (hk : k < p) (n : ℕ) :
    (p : ℤ_[p]) ∣ coeffPadic p m j hj n - coeffPadic p m k hk n := by
  have h : PadicInt.toZMod (coeffPadic p m j hj n - coeffPadic p m k hk n) = 0 := by
    rw [map_sub, two_window_addresses_agree p m j k hj hk n, sub_self]
  rw [← RingHom.mem_ker, PadicInt.ker_toZMod, PadicInt.maximalIdeal_eq_span_p,
    Ideal.mem_span_singleton] at h
  exact h

@[simp] theorem reduced_zero (m : ℕ) : reduced p m 0 = 1 := by
  simp [reduced]

end KomorebiPaperIX.WindowIndependence
