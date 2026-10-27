import KomorebiLSM.RationalBernsteinMargin

/-! Real entry budgets in the actual mass/real/imaginary coordinates. -/
set_option autoImplicit false
namespace Komorebi.LSM.ComplexCoefficientBox
open LorentzCylinder RobustOrientedMargin
open scoped BigOperators
abbrev RealMatrix := Matrix (Fin 3) (Fin 3) ℝ

noncomputable def row (E : RealMatrix) (i : Fin 3) : State ℂ →L[ℝ] ℝ :=
  ∑ j,E i j • RationalBernsteinMargin.coordinate j

noncomputable def matrixOperator (E : RealMatrix) : State ℂ →L[ℝ] State ℂ :=
  (row E 0).prod (Complex.equivRealProdCLM.symm.toContinuousLinearMap.comp
    ((row E 1).prod (row E 2)))

@[simp] theorem coordinate_matrixOperator (E : RealMatrix) (i : Fin 3) (z : State ℂ) :
    RationalBernsteinMargin.coordinate i (matrixOperator E z)=
      ∑ j,E i j*RationalBernsteinMargin.coordinate j z := by
  fin_cases i <;> simp [RationalBernsteinMargin.coordinate,matrixOperator,row]

@[simp] theorem matrixOperator_rat (E : RationalBernsteinMargin.RationalMatrix) :
    matrixOperator (fun i j => (E i j : ℝ))=RationalBernsteinMargin.matrixOperator E := rfl

theorem normalized_coordinate_bound (v : ℂ) (hv : ‖v‖≤1) (i : Fin 3) :
    |RationalBernsteinMargin.coordinate i (1,v)|≤1 := by
  fin_cases i
  · norm_num [RationalBernsteinMargin.coordinate]
  · exact (Complex.abs_re_le_norm v).trans hv
  · exact (Complex.abs_im_le_norm v).trans hv

theorem row_bound (E : RealMatrix) (v : ℂ) (hv : ‖v‖≤1) (i : Fin 3) :
    |RationalBernsteinMargin.coordinate i (matrixOperator E (1,v))|≤∑ j,|E i j| := by
  rw [coordinate_matrixOperator]
  calc
    _ ≤ ∑ j : Fin 3,|E i j*RationalBernsteinMargin.coordinate j (1,v)| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ _ := by
      apply Finset.sum_le_sum
      intro j _
      rw [abs_mul]
      exact (mul_le_mul_of_nonneg_left (normalized_coordinate_bound v hv j) (abs_nonneg _)).trans_eq (mul_one _)

theorem value_bound (E : RealMatrix) (v : ℂ) (hv : ‖v‖≤1) :
    probabilityCone.value (matrixOperator E (1,v))≤
      max (∑ j,|E 0 j|) ((∑ j,|E 1 j|)+(∑ j,|E 2 j|)) := by
  rw [value_eq]
  apply max_le_max (row_bound E v hv 0)
  exact (Complex.norm_le_abs_re_add_abs_im _).trans (add_le_add (row_bound E v hv 1) (row_bound E v hv 2))

theorem entry_row_bound (E : RealMatrix) (r : ℝ) (hE : ∀ i j,|E i j|≤r) (i : Fin 3) :
    (∑ j,|E i j|)≤3*r := by
  calc
    _ ≤ ∑ _j : Fin 3,r := Finset.sum_le_sum fun j _ => hE i j
    _ = _ := by simp

theorem coefficient_output_bounds (E : RealMatrix) (r : ℝ) (hE : ∀ i j,|E i j|≤r)
    (v : ℂ) (hv : ‖v‖≤1) :
    |(matrixOperator E (1,v)).1|≤3*r ∧ ‖(matrixOperator E (1,v)).2‖≤6*r := by
  have h0 := (row_bound E v hv 0).trans (entry_row_bound E r hE 0)
  have h1 := (row_bound E v hv 1).trans (entry_row_bound E r hE 1)
  have h2 := (row_bound E v hv 2).trans (entry_row_bound E r hE 2)
  refine ⟨h0,?_⟩
  have hn := Complex.norm_le_abs_re_add_abs_im (matrixOperator E (1,v)).2
  change |(matrixOperator E (1,v)).2.re|≤3*r at h1
  change |(matrixOperator E (1,v)).2.im|≤3*r at h2
  linarith

theorem polynomial_coordinate {n : ℕ} (E : Fin n → RealMatrix) (u : ℝ) (z : State ℂ) (i : Fin 3) :
    RationalBernsteinMargin.coordinate i (PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u z)=
      ∑ k : Fin n,u^(k : ℕ)*RationalBernsteinMargin.coordinate i (matrixOperator (E k) z) := by
  simp only [PolynomialGram.operatorPolynomial,sum_apply,smul_apply,map_sum,map_smul]
  rfl

theorem polynomial_row_bound {n : ℕ} (E : Fin n → RealMatrix) (u : ℝ)
    (hu : u∈Set.Icc (-1 : ℝ) 1) (v : ℂ) (hv : ‖v‖≤1) (i : Fin 3) :
    |RationalBernsteinMargin.coordinate i
      (PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v))|≤
        ∑ k : Fin n,∑ j,|E k i j| := by
  rw [polynomial_coordinate]
  calc
    _ ≤ ∑ k : Fin n,|u^(k : ℕ)*RationalBernsteinMargin.coordinate i (matrixOperator (E k) (1,v))| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ _ := by
      apply Finset.sum_le_sum
      intro k _
      rw [abs_mul]
      have hp : |u^(k : ℕ)|≤1 := by rw [abs_pow]; exact pow_le_one₀ (abs_nonneg _) (abs_le.mpr hu)
      exact (mul_le_mul hp (row_bound (E k) v hv i) (abs_nonneg _) (by norm_num)).trans_eq (one_mul _)

theorem polynomial_output_bounds {n : ℕ} (E : Fin n → RealMatrix) (r : Fin n → ℝ)
    (hE : ∀ k i j,|E k i j|≤r k) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (v : ℂ) (hv : ‖v‖≤1) :
    |(PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v)).1|≤3*∑ k,r k ∧
    ‖(PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v)).2‖≤6*∑ k,r k := by
  have hr (i : Fin 3) : (∑ k : Fin n,∑ j,|E k i j|)≤3*∑ k,r k := by
    calc
      _ ≤ ∑ k : Fin n,3*r k := Finset.sum_le_sum fun k _ => entry_row_bound (E k) (r k) (hE k) i
      _ = _ := (Finset.mul_sum _ _ _).symm
  have h0 := (polynomial_row_bound E u hu v hv 0).trans (hr 0)
  have h1 := (polynomial_row_bound E u hu v hv 1).trans (hr 1)
  have h2 := (polynomial_row_bound E u hu v hv 2).trans (hr 2)
  refine ⟨h0,?_⟩
  have hn := Complex.norm_le_abs_re_add_abs_im (PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v)).2
  change |(PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v)).2.re|≤3*∑ k,r k at h1
  change |(PolynomialGram.operatorPolynomial (fun k => matrixOperator (E k)) u (1,v)).2.im|≤3*∑ k,r k at h2
  linarith

end Komorebi.LSM.ComplexCoefficientBox
