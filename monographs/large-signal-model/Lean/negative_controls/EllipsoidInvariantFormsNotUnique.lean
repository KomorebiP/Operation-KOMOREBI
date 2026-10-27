import KomorebiLSM.EllipsoidDiscovery
set_option autoImplicit false
open Komorebi.LSM.EllipsoidDiscovery Matrix
private def otherMetric : Matrix (Fin 2) (Fin 2) ℝ := Matrix.diagonal ![1,2]
private def displacement : Fin 2 → ℝ := ![1,0]
/-- Invariance and one boundary image do not imply metric uniqueness when the
actual symmetric invariant-form space has dimension greater than one. -/
example : ∃! H : Matrix (Fin 2) (Fin 2) ℝ,
    H∈invariantForms (-1) ∧ H.PosDef ∧ quadratic H displacement=1 := by
  have hp : otherMetric.PosDef := by
    apply Matrix.PosDef.diagonal
    intro i
    fin_cases i <;> norm_num [otherMetric]
  have hfirst : (1 : Matrix (Fin 2) (Fin 2) ℝ)∈invariantForms (-1) ∧
      (1 : Matrix (Fin 2) (Fin 2) ℝ).PosDef ∧ quadratic 1 displacement=1 := by
    refine ⟨⟨Matrix.isHermitian_one,by simp⟩,Matrix.PosDef.one,?_⟩
    norm_num [quadratic,displacement,dotProduct,Fin.sum_univ_succ]
  have hother : otherMetric∈invariantForms (-1) ∧ otherMetric.PosDef ∧
      quadratic otherMetric displacement=1 := by
    refine ⟨⟨hp.isHermitian,by simp⟩,hp,?_⟩
    norm_num [quadratic,otherMetric,displacement,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
  have hn : ¬∃! H : Matrix (Fin 2) (Fin 2) ℝ,
      H∈invariantForms (-1) ∧ H.PosDef ∧ quadratic H displacement=1 := by
    rintro ⟨H,hH,hu⟩
    have he : otherMetric=1 := (hu otherMetric hother).trans (hu 1 hfirst).symm
    have hd := congrFun (congrFun he 1) 1
    norm_num [otherMetric] at hd
  simp only [hn]
