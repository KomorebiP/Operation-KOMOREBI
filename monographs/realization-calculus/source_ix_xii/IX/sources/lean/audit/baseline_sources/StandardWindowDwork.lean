module

public import EulerDefect
public import ResidueZeroDwork
public import ExponentialSection
public import DifferenceStepMultiples
public import GlobalEulerBoundary

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.StandardWindowDwork

open PowerSeries HurwitzDworkClosure DworkAlgebra DworkClosure WindowIndependence

variable (p : ℕ) [Fact p.Prime]

/-- Actual normalized-section Hurwitz coefficients: inverse binomial pivots in Z_p. -/
def kernelCoefficients (m j : ℕ) (hj : j<p) (d : ℕ) : ℤ_[p] :=
  if m*p∣d then ((diagonalUnit p m j hj (d/(m*p)))⁻¹ : ℤ_[p]ˣ) else 0

/-- At supported degrees the integral construction equals the explicit reciprocal binomial. -/
theorem kernel_coe (m j : ℕ) (hj : j<p) (d : ℕ) (hd : m*p∣d) :
    (kernelCoefficients p m j hj d : ℚ_[p]) =
      (((d+j).choose d : ℕ) : ℚ_[p])⁻¹ := by
  have hh : m*p*(d/(m*p))=d := Nat.mul_div_cancel' hd
  have hu : (diagonalUnit p m j hj (d/(m*p)) : ℤ_[p]) =
      (((d+j).choose d : ℕ) : ℤ_[p]) := by
    rw [diagonalUnit_coe, hh]
  have hi : (((d+j).choose d : ℕ) : ℤ_[p]) * kernelCoefficients p m j hj d = 1 := by
    rw [kernelCoefficients, ite_eq_left hd, ← hu]
    simp
  have hiq := congrArg (fun x:ℤ_[p] => (x:ℚ_[p])) hi
  have hn : (((d+j).choose d : ℕ) : ℚ_[p]) ≠ 0 :=
    Nat.cast_ne_zero.mpr (Nat.choose_ne_zero (by omega))
  change (((d+j).choose d : ℕ) : ℚ_[p]) * (kernelCoefficients p m j hj d : ℚ_[p]) = 1 at hiq
  exact (mul_eq_one_iff_eq_inv₀ hn).mp (by simpa [mul_comm] using hiq)

@[simp] theorem kernel_constant (m j : ℕ) (hj : j<p) :
    kernelCoefficients p m j hj 0=1 := by
  apply Subtype.ext
  have h := kernel_coe p m j hj 0 (dvd_zero _)
  simpa using h

theorem kernel_support (m j : ℕ) (hj : j<p) (d : ℕ) (hd : ¬p∣d) :
    kernelCoefficients p m j hj d=0 := by
  have hN : ¬m*p∣d := fun h => hd (dvd_trans (dvd_mul_left p m) h)
  simp [kernelCoefficients, hN]

/-- The algebraic zero-address section is literally the first member of the kernel family. -/
theorem kernel_zero_address (m : ℕ) :
    kernelCoefficients p m 0 (Fact.out : p.Prime).pos =
      ResidueZeroDwork.sectionCoefficients p (m*p) := by
  funext d
  by_cases hd : m*p∣d
  · apply Subtype.ext
    rw [kernel_coe p m 0 _ d hd]
    simp [ResidueZeroDwork.sectionCoefficients, hd]
  · simp [kernelCoefficients, ResidueZeroDwork.sectionCoefficients, hd]

/-- Exact Euler-operator relation between consecutive normalized source sections. -/
theorem kernel_euler_step (m j : ℕ) (hj : j+1<p) :
    EulerDefect.eulerOperator (j+1) (kernelCoefficients p m (j+1) hj) =
      fun d => ((j+1:ℕ):ℤ_[p])*kernelCoefficients p m j (by omega) d := by
  funext d
  by_cases hd : m*p∣d
  · apply Subtype.ext
    change ((d:ℚ_[p])+((j+1:ℕ):ℚ_[p]))*(kernelCoefficients p m (j+1) hj d:ℚ_[p]) =
      ((j+1:ℕ):ℚ_[p])*(kernelCoefficients p m j (by omega) d:ℚ_[p])
    rw [kernel_coe p m (j+1) hj d hd, kernel_coe p m j _ d hd]
    have h1 : (((d+(j+1)).choose d : ℕ):ℚ_[p])≠0 :=
      Nat.cast_ne_zero.mpr (Nat.choose_ne_zero (by omega))
    have h2 : (((d+j).choose d : ℕ):ℚ_[p])≠0 :=
      Nat.cast_ne_zero.mpr (Nat.choose_ne_zero (by omega))
    have h := Nat.choose_mul_succ_eq (d+j) d
    have hs : d+j+1-d=j+1 := by omega
    rw [hs] at h
    have hq : (((d+j).choose d:ℕ):ℚ_[p])*((d+j+1:ℕ):ℚ_[p]) =
        (((d+j+1).choose d:ℕ):ℚ_[p])*((j+1:ℕ):ℚ_[p]) := by exact_mod_cast h
    rw [Nat.add_assoc] at hq
    push_cast at hq ⊢
    field_simp
    linear_combination hq
  · simp [EulerDefect.eulerOperator, kernelCoefficients, hd]

/-- Constant multiplication commutes with every actual differential defect. -/
theorem defectIter_mul_const (a : ℤ_[p]) (L s : ℕ) (f : ℕ → ℤ_[p]) (d : ℕ) :
    DworkCriterion.defectIter p L s (fun n => a*f n) d =
      a*DworkCriterion.defectIter p L s f d := by
  induction s generalizing d with
  | zero => rfl
  | succ s ih =>
    rw [DworkCriterion.defectIter_succ, DworkCriterion.defectIter_succ, ih, ih, mul_sub]

theorem flat_mul_const (a : ℤ_[p]) (f : ℕ → ℤ_[p]) (hf : DworkCriterion.flat p f) :
    DworkCriterion.flat p (fun n => a*f n) := by
  intro s d
  rw [defectIter_mul_const]
  exact dvd_mul_of_dvd_right (hf s d) a

/-- Every actual standard-window normalized source is flat to every order. -/
theorem kernel_flat (m j : ℕ) (hm : m∣p-1) (hj : j<p) :
    DworkCriterion.flat p (kernelCoefficients p m j hj) := by
  induction j with
  | zero => rw [kernel_zero_address]; exact ResidueZeroDwork.section_flat p m hm
  | succ j ih =>
    apply EulerDefect.flat_of_euler_flat p (j+1)
      (Nat.not_dvd_of_pos_of_lt (Nat.zero_lt_succ j) hj)
    · exact kernel_support p m (j+1) hj
    · rw [kernel_euler_step p m j hj]
      exact flat_mul_const p _ _ (ih (by omega))

/-- The integral kernel equals the original factorial-ratio series after encoding. -/
theorem kernel_encoding (m j : ℕ) (hm : 0<m) (hj : j<p) :
    encodeIntegral p (kernelCoefficients p m j hj) =
      PowerSeries.map (algebraMap ℚ ℚ_[p])
        (PowerSeries.expand (m*p) (Nat.mul_pos hm (Fact.out : p.Prime).pos).ne'
          (Congruential.sectionKernel (m*p) j)) := by
  have hN : 0<m*p := Nat.mul_pos hm (Fact.out : p.Prime).pos
  ext d
  by_cases hd : m*p∣d
  · obtain ⟨r,rfl⟩ := hd
    simp only [encodeIntegral, EGF.encode, coeff_mk, coeff_map, coeff_expand_mul,
      Congruential.sectionKernel, map_div₀, map_natCast]
    rw [kernel_coe p m j hj _ (dvd_mul_right _ _)]
    rw [Nat.cast_choose ℚ_[p] (by omega : m*p*r≤m*p*r+j)]
    rw [show m*p*r+j-m*p*r=j by omega]
    have h1 : ((m*p*r).factorial:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    have h2 : (j.factorial:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    have h3 : ((m*p*r+j).factorial:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    field_simp
  · simp [encodeIntegral, EGF.encode, kernelCoefficients, hd,
      coeff_expand_of_not_dvd (m*p) hN.ne' _ hd]

/-- The packed integral lift equals the original rational packet after encoding and scalar extension. -/
theorem packet_encoding (m j : ℕ) (hm : 0<m) (hj : j<p) :
    encodeIntegral p (DworkCriterion.packed (m*p) (coeffPadic p m j hj)) =
      PowerSeries.map (algebraMap ℚ ℚ_[p])
        (ExponentialSection.expandedPacket (m*p) (Nat.mul_pos hm (Fact.out : p.Prime).pos).ne' j) := by
  have hN : 0<m*p := Nat.mul_pos hm (Fact.out : p.Prime).pos
  ext d
  by_cases hd : m*p∣d
  · obtain ⟨r,rfl⟩ := hd
    simp only [encodeIntegral, EGF.encode, coeff_mk, coeff_map,
      ExponentialSection.packet_coefficient_at_address, map_div₀, map_natCast]
    rw [DworkCriterion.packed_multiple _ hN, coeffPadic_coe]
    rfl
  · simp [encodeIntegral, EGF.encode, DworkCriterion.packed, hd,
      ExponentialSection.expandedPacket, coeff_expand_of_not_dvd (m*p) hN.ne' _ hd]

/-- The reciprocal equation is transported from the proved original generating-function identity. -/
theorem window_is_reciprocal (m j : ℕ) (hm : 0<m) (hj : j<p) :
    encodeIntegral p (DworkCriterion.packed (m*p) (coeffPadic p m j hj)) =
      (encodeIntegral p (kernelCoefficients p m j hj))⁻¹ := by
  have hN := (Nat.mul_pos hm (Fact.out : p.Prime).pos).ne'
  have hi := congrArg (fun F : PowerSeries ℚ =>
    PowerSeries.map (algebraMap ℚ ℚ_[p]) (PowerSeries.expand (m*p) hN F))
      (Congruential.packet_times_kernel (m*p) j)
  simp only [map_mul, map_one] at hi
  have hc : constantCoeff (encodeIntegral p (kernelCoefficients p m j hj))=1 := by
    simp [encodeIntegral, EGF.encode]
  apply (PowerSeries.eq_inv_iff_mul_eq_one (by rw [hc]; exact one_ne_zero)).mpr
  rw [packet_encoding p m j hm hj, kernel_encoding p m j hm hj]
  exact hi

/-- Unconditional all-order flatness of the original normalized Euler packets in 0<=j<p. -/
theorem standard_window_flat (m j : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<p) :
    DworkCriterion.flat p (DworkCriterion.packed (m*p) (coeffPadic p m j hj)) := by
  apply (flat_encode_iff p _).mp
  rw [window_is_reciprocal p m j hmpos hj]
  apply flat_reciprocal
  · exact (flat_encode_iff p _).mpr (kernel_flat p m j hm hj)
  · simp [encodeIntegral, EGF.encode]

/-- The full saturated higher-power bound for every standard-window residue, every row and order. -/
theorem standard_window_global_bound (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<p) :
    (p:ℤ_[p])^(min k (m*n))∣
      Mahler.difference (u*((p-1)/m)) k (coeffPadic p m j hj) n := by
  apply StepMultiples.saturated_multiple_step (p:ℤ_[p]) m ((p-1)/m) (coeffPadic p m j hj)
  intro k n
  exact DworkCriterion.saturated_bound_of_flat p m (Fact.out : p.Prime).pos hm hmpos
    (coeffPadic p m j hj) (standard_window_flat p m j hm hmpos hj) k n

/-- Valuation at zero remains infinity in the actual completed ring. -/
theorem standard_window_global_order (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<p) :
    (min k (m*n) : WithTop ℕ) ≤ PadicBounds.order p
      (Mahler.difference (u*((p-1)/m)) k (coeffPadic p m j hj) n) :=
  (PadicBounds.nat_le_order_iff p _ _).mpr
    (standard_window_global_bound p m j u k n hm hmpos hj)

end KomorebiPaperIX.StandardWindowDwork
