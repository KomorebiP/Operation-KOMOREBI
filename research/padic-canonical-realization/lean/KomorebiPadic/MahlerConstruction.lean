import KomorebiPadic.CartierSection
import Mathlib.RingTheory.PowerSeries.Inverse

/-! # Normalized Mahler series by strictly causal coefficient recursion
No topology, convergence, or field structure is used. Expansion by a radix > 1
makes every positive output coefficient depend only on earlier input coefficients.
-/
namespace KomorebiPadic
variable {R : Type*} [CommRing R]

/-- Positive coefficient n of U*F(X^p) depends only on coefficients below n of F. -/
theorem mahlerStep_coeff_congr {p n : ℕ} (hp : 1 < p) (hn : 0 < n)
    (U F G : PowerSeries R)
    (hFG : ∀ j, j < n → PowerSeries.coeff j F = PowerSeries.coeff j G) :
    PowerSeries.coeff n (U * PowerSeries.expand p (by omega) F) =
      PowerSeries.coeff n (U * PowerSeries.expand p (by omega) G) := by
  rw [PowerSeries.coeff_mul, PowerSeries.coeff_mul]
  apply Finset.sum_congr rfl
  intro ij hij
  have hij' := Finset.mem_antidiagonal.mp hij
  have hj : ij.2 / p < n :=
    (Nat.div_le_div_right (by omega : ij.2 ≤ n)).trans_lt (Nat.div_lt_self hn hp)
  rw [PowerSeries.coeff_expand, PowerSeries.coeff_expand]
  split_ifs
  · rw [hFG _ hj]
  · rfl

/-- Prescribe coefficient zero and recursively apply the strictly causal operator.
The temporary tail is zero only beyond already constructed coefficients. -/
noncomputable def normalizedMahlerCoeff (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (n : ℕ) : R :=
  if n = 0 then 1 else
    PowerSeries.coeff n (U * PowerSeries.expand p (by omega)
      (PowerSeries.mk fun j => if hj : j < n then normalizedMahlerCoeff p hp U j else 0))
termination_by n

noncomputable def normalizedMahlerSeries (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) : PowerSeries R :=
  PowerSeries.mk (normalizedMahlerCoeff p hp U)

@[simp] theorem coeff_normalizedMahlerSeries (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (n : ℕ) :
    PowerSeries.coeff n (normalizedMahlerSeries p hp U) = normalizedMahlerCoeff p hp U n := by
  simp [normalizedMahlerSeries]

@[simp] theorem normalizedMahlerCoeff_zero (p : ℕ) (hp : 1 < p) (U : PowerSeries R) :
    normalizedMahlerCoeff p hp U 0 = 1 := by
  rw [normalizedMahlerCoeff]
  simp

@[simp] theorem normalizedMahlerSeries_constant (p : ℕ) (hp : 1 < p) (U : PowerSeries R) :
    PowerSeries.constantCoeff (normalizedMahlerSeries p hp U) = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, coeff_normalizedMahlerSeries,
    normalizedMahlerCoeff_zero]

/-- The constructed complete formal series solves F=U*F(X^p). -/
theorem normalizedMahlerSeries_equation (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (hU : PowerSeries.constantCoeff U = 1) :
    normalizedMahlerSeries p hp U =
      U * PowerSeries.expand p (by omega) (normalizedMahlerSeries p hp U) := by
  ext n
  by_cases hn : n = 0
  · subst n
    simp [PowerSeries.coeff_zero_eq_constantCoeff, hU]
  · rw [coeff_normalizedMahlerSeries, normalizedMahlerCoeff]
    simp only [hn, ↓reduceIte]
    apply mahlerStep_coeff_congr hp (Nat.pos_of_ne_zero hn)
    intro j hj
    simp [hj]

/-- Explicit finite coefficient recurrence for the constructed series. For n>0,
all referenced coefficients have index at most n/p, hence strictly below n. -/
theorem normalizedMahlerCoeff_recurrence (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (hU : PowerSeries.constantCoeff U = 1) (n : ℕ) :
    normalizedMahlerCoeff p hp U n =
      ∑ i ∈ Finset.range (n+1), PowerSeries.coeff i U *
        (if p ∣ n-i then normalizedMahlerCoeff p hp U ((n-i)/p) else 0) := by
  rw [← coeff_normalizedMahlerSeries]
  conv_lhs => rw [normalizedMahlerSeries_equation p hp U hU]
  rw [PowerSeries.coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  simp only [PowerSeries.coeff_expand, coeff_normalizedMahlerSeries]

/-- A normalized fixed point of the same multiplier is unique. -/
theorem normalizedMahlerSeries_unique (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (hU : PowerSeries.constantCoeff U = 1)
    (F : PowerSeries R) (hF : PowerSeries.constantCoeff F = 1)
    (hEq : F = U * PowerSeries.expand p (by omega) F) :
    F = normalizedMahlerSeries p hp U := by
  ext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n = 0
    · subst n
      simp [PowerSeries.coeff_zero_eq_constantCoeff, hF]
    · conv_lhs => rw [hEq]
      conv_rhs => rw [normalizedMahlerSeries_equation p hp U hU]
      exact mahlerStep_coeff_congr hp (Nat.pos_of_ne_zero hn) U _ _ ih

/-- Every normalized multiplier has exactly one normalized Mahler fixed point. -/
theorem existsUnique_normalizedMahlerSeries (p : ℕ) (hp : 1 < p)
    (U : PowerSeries R) (hU : PowerSeries.constantCoeff U = 1) :
    ∃! F : PowerSeries R, PowerSeries.constantCoeff F = 1 ∧
      F = U * PowerSeries.expand p (by omega) F := by
  refine ⟨normalizedMahlerSeries p hp U,
    ⟨normalizedMahlerSeries_constant p hp U, normalizedMahlerSeries_equation p hp U hU⟩, ?_⟩
  intro F hF
  exact normalizedMahlerSeries_unique p hp U hU F hF.1 hF.2

/-- The constructed normalized solution is a unit, even over rings with zero divisors. -/
theorem normalizedMahlerSeries_isUnit (p : ℕ) (hp : 1 < p) (U : PowerSeries R) :
    IsUnit (normalizedMahlerSeries p hp U) := by
  apply PowerSeries.isUnit_iff_constantCoeff.mpr
  rw [normalizedMahlerSeries_constant]
  exact isUnit_one


/-- The mask equation is equivalent to a normalized-multiplier fixed point when B is a unit. -/
theorem unitMahlerEquation_iff (p : ℕ) (hp : p ≠ 0)
    (A F : PowerSeries R) (u : (PowerSeries R)ˣ) :
    (u : PowerSeries R) * F = A * PowerSeries.expand p hp F ↔
      F = (A * (↑u⁻¹ : PowerSeries R)) * PowerSeries.expand p hp F := by
  constructor
  · intro h
    calc
      F = (↑u⁻¹ : PowerSeries R) * ((u : PowerSeries R) * F) := by simp
      _ = (A * (↑u⁻¹ : PowerSeries R)) * PowerSeries.expand p hp F := by rw [h]; ring
  · intro h
    calc
      (u : PowerSeries R) * F =
        (u : PowerSeries R) * ((A * (↑u⁻¹ : PowerSeries R)) * PowerSeries.expand p hp F) :=
          congrArg ((u : PowerSeries R) * ·) h
      _ = ((u : PowerSeries R) * (↑u⁻¹ : PowerSeries R)) * (A * PowerSeries.expand p hp F) := by ring
      _ = A * PowerSeries.expand p hp F := by simp

/-- The unit-normalized mask multiplier. -/
noncomputable def mahlerMaskMultiplier (A B : PowerSeries R) (hB : IsUnit B) : PowerSeries R :=
  A * (↑hB.unit⁻¹ : PowerSeries R)

theorem mahlerMaskMultiplier_constant (A B : PowerSeries R) (hB : IsUnit B)
    (hAB : PowerSeries.constantCoeff A = PowerSeries.constantCoeff B) :
    PowerSeries.constantCoeff (mahlerMaskMultiplier A B hB) = 1 := by
  have hu := congrArg (PowerSeries.constantCoeff : PowerSeries R → R) hB.unit.mul_inv
  simpa only [mahlerMaskMultiplier, map_mul, map_one, hB.unit_spec, hAB] using hu

/-- Construct the series from masks alone; the equation requires their constants to agree. -/
noncomputable def normalizedMahlerMaskSeries (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B) : PowerSeries R :=
  normalizedMahlerSeries p hp (mahlerMaskMultiplier A B hB)

@[simp] theorem normalizedMahlerMaskSeries_constant (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B) :
    PowerSeries.constantCoeff (normalizedMahlerMaskSeries p hp A B hB) = 1 :=
  normalizedMahlerSeries_constant p hp _

theorem normalizedMahlerMaskSeries_equation (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B)
    (hAB : PowerSeries.constantCoeff A = PowerSeries.constantCoeff B) :
    B * normalizedMahlerMaskSeries p hp A B hB =
      A * PowerSeries.expand p (by omega) (normalizedMahlerMaskSeries p hp A B hB) := by
  have h := (unitMahlerEquation_iff p (by omega) A
    (normalizedMahlerMaskSeries p hp A B hB) hB.unit).mpr
      (normalizedMahlerSeries_equation p hp _ (mahlerMaskMultiplier_constant A B hB hAB))
  simpa only [hB.unit_spec] using h

theorem normalizedMahlerMaskSeries_unique (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B)
    (hAB : PowerSeries.constantCoeff A = PowerSeries.constantCoeff B)
    (F : PowerSeries R) (hF : PowerSeries.constantCoeff F = 1)
    (hEq : B * F = A * PowerSeries.expand p (by omega) F) :
    F = normalizedMahlerMaskSeries p hp A B hB := by
  apply normalizedMahlerSeries_unique p hp _ (mahlerMaskMultiplier_constant A B hB hAB) F hF
  exact (unitMahlerEquation_iff p (by omega) A F hB.unit).mp (by simpa using hEq)

theorem existsUnique_normalizedMahlerMaskSeries (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B)
    (hAB : PowerSeries.constantCoeff A = PowerSeries.constantCoeff B) :
    ∃! F : PowerSeries R, PowerSeries.constantCoeff F = 1 ∧
      B * F = A * PowerSeries.expand p (by omega) F := by
  refine ⟨normalizedMahlerMaskSeries p hp A B hB,
    ⟨normalizedMahlerMaskSeries_constant p hp A B hB,
      normalizedMahlerMaskSeries_equation p hp A B hB hAB⟩, ?_⟩
  intro F hF
  exact normalizedMahlerMaskSeries_unique p hp A B hB hAB F hF.1 hF.2

/-- Equal mask constants are necessary, not only sufficient. -/
theorem normalizedMahlerMask_constants_necessary (p : ℕ) (hp : p ≠ 0)
    (A B F : PowerSeries R) (hF : PowerSeries.constantCoeff F = 1)
    (hEq : B * F = A * PowerSeries.expand p hp F) :
    PowerSeries.constantCoeff A = PowerSeries.constantCoeff B := by
  have h := congrArg (PowerSeries.constantCoeff : PowerSeries R → R) hEq
  simpa [hF] using h.symm

theorem exists_normalizedMahlerMask_iff (p : ℕ) (hp : 1 < p)
    (A B : PowerSeries R) (hB : IsUnit B) :
    (∃ F : PowerSeries R, PowerSeries.constantCoeff F = 1 ∧
      B * F = A * PowerSeries.expand p (by omega) F) ↔
    PowerSeries.constantCoeff A = PowerSeries.constantCoeff B := by
  constructor
  · rintro ⟨F, hF, hEq⟩
    exact normalizedMahlerMask_constants_necessary p (by omega) A B F hF hEq
  · intro hAB
    exact (existsUnique_normalizedMahlerMaskSeries p hp A B hB hAB).exists

/-- Coefficient homomorphisms preserve the canonical normalized fixed point. -/
theorem map_normalizedMahlerSeries {S : Type*} [CommRing S] (f : R →+* S)
    (p : ℕ) (hp : 1 < p) (U : PowerSeries R) (hU : PowerSeries.constantCoeff U = 1) :
    PowerSeries.map f (normalizedMahlerSeries p hp U) =
      normalizedMahlerSeries p hp (PowerSeries.map f U) := by
  apply normalizedMahlerSeries_unique p hp _
    (by change f (PowerSeries.constantCoeff U) = 1; rw [hU, map_one]) _
    (by change f (PowerSeries.constantCoeff (normalizedMahlerSeries p hp U)) = 1
        rw [normalizedMahlerSeries_constant, map_one])
  conv_lhs => rw [normalizedMahlerSeries_equation p hp U hU]
  rw [map_mul, PowerSeries.map_expand]

/-- Mask solutions commute with coefficient homomorphisms, by uniqueness, not by inverse choices. -/
theorem map_normalizedMahlerMaskSeries {S : Type*} [CommRing S] (f : R →+* S)
    (p : ℕ) (hp : 1 < p) (A B : PowerSeries R) (hB : IsUnit B)
    (hAB : PowerSeries.constantCoeff A = PowerSeries.constantCoeff B)
    (hB' : IsUnit (PowerSeries.map f B)) :
    PowerSeries.map f (normalizedMahlerMaskSeries p hp A B hB) =
      normalizedMahlerMaskSeries p hp (PowerSeries.map f A) (PowerSeries.map f B) hB' := by
  apply normalizedMahlerMaskSeries_unique p hp _ _ hB'
    (by change f (PowerSeries.constantCoeff A) = f (PowerSeries.constantCoeff B); rw [hAB]) _
    (by change f (PowerSeries.constantCoeff (normalizedMahlerMaskSeries p hp A B hB)) = 1
        rw [normalizedMahlerMaskSeries_constant, map_one])
  have h := congrArg (PowerSeries.map f)
    (normalizedMahlerMaskSeries_equation p hp A B hB hAB)
  simpa only [map_mul, PowerSeries.map_expand] using h

/-- A unit multiplier equal to one has canonical solution one. -/
@[simp] theorem normalizedMahlerSeries_one (p : ℕ) (hp : 1 < p) :
    normalizedMahlerSeries p hp (1 : PowerSeries R) = 1 := by
  symm
  apply normalizedMahlerSeries_unique p hp _ (by simp) _ (by simp)
  simp

/-- Radix one has distinct normalized solutions, so the strict radix hypothesis is essential. -/
theorem mahler_radix_one_nonunique :
    PowerSeries.constantCoeff (1 : PowerSeries ℤ) = 1 ∧
    PowerSeries.constantCoeff (1 + PowerSeries.X : PowerSeries ℤ) = 1 ∧
    (1 : PowerSeries ℤ) = PowerSeries.expand 1 (by decide) 1 ∧
    (1 + PowerSeries.X : PowerSeries ℤ) = PowerSeries.expand 1 (by decide) (1 + PowerSeries.X) ∧
    (1 : PowerSeries ℤ) ≠ 1 + PowerSeries.X := by
  refine ⟨by simp, by simp, by simp, by simp, ?_⟩
  intro h
  have hc := congrArg (PowerSeries.coeff 1) h
  simp at hc

end KomorebiPadic
