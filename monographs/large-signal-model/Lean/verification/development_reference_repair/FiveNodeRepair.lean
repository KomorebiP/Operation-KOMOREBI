import KomorebiLSM.CurvedMomentTV
import KomorebiLSM.PolynomialGram
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.Tactic

/-! Actual five-node and normalized Lebesgue references, with exact absolute
moments. The finite experiment and continuous experiment remain distinct. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory
open scoped BigOperators ENNReal
noncomputable section

namespace FiveNode

def node : Fin 5 → ℝ := ![-1,-1/2,0,1/2,1]
def weight : Fin 5 → ℝ≥0∞ := ![7/90,16/45,2/15,16/45,7/90]
def measure : Measure ℝ := ∑ i : Fin 5, weight i • Measure.dirac (node i)

theorem weight_ne_top (i : Fin 5) : weight i≠∞ := by
  fin_cases i <;> dsimp [weight] <;>
    exact ENNReal.div_ne_top (by norm_num) (by norm_num)

instance measure_probability : IsProbabilityMeasure measure := by
  constructor
  apply (ENNReal.toReal_eq_one_iff _).mp
  have he : measure Set.univ=∑ i : Fin 5,weight i := by
    simp [measure]
  rw [he,ENNReal.toReal_sum (fun i _ => weight_ne_top i)]
  norm_num [Fin.sum_univ_succ,weight]

theorem integral_eq (f : ℝ → ℝ) :
    (∫ u,f u∂measure)=∑ i : Fin 5,(weight i).toReal*f (node i) := by
  rw [measure,integral_finsetSum_measure]
  · simp only [integral_smul_measure,integral_dirac,smul_eq_mul]
  · intro i _
    exact (integrable_dirac (f:=f) (by simp)).smul_measure (weight_ne_top i)

theorem support : ∀ᵐ u∂measure,u∈Set.Icc (-1:ℝ) 1 := by
  rw [measure,ae_finsetSum_measure_iff]
  intro i _
  apply Measure.ae_smul_measure
  apply (ae_dirac_iff (p := fun x : ℝ => x∈Set.Icc (-1:ℝ) 1) measurableSet_Icc).mpr
  fin_cases i <;> norm_num [node]

theorem reference : Reference measure := by
  refine ⟨measure_probability,support,?_,?_,?_,?_⟩ <;>
    norm_num [integral_eq,weight,node,Fin.sum_univ_succ]

theorem absoluteFirst_eq : reference.absoluteFirst=23/45 := by
  norm_num [Reference.absoluteFirst,integral_eq,weight,node,Fin.sum_univ_succ]

theorem absoluteLegendre_eq : reference.absoluteLegendre=14/45 := by
  norm_num [Reference.absoluteLegendre,integral_eq,weight,node,Fin.sum_univ_succ,legendre]

theorem parameterBudget_eq (da db : ℝ) :
    reference.parameterBudget da db=(23*da+14*db)/90 := by
  rw [Reference.parameterBudget,absoluteFirst_eq,absoluteLegendre_eq]
  ring

theorem final_rectangle_budget : reference.parameterBudget (53/1000) (87/1000)=2437/90000 := by
  rw [parameterBudget_eq]
  norm_num

end FiveNode

end
end Komorebi.LSM.CurvedMoment
