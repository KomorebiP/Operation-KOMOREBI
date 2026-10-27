import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.Basis
import Mathlib.NumberTheory.Divisors
import Mathlib.Basic.Complex.Basic

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

abbrev DivIdx (T : ℕ) := {c : ℕ // c ∈ T.divisors}
abbrev DivCoord (T : ℕ) := DivIdx T → ℂ

variable {T : ℕ}

def widthVec (g : DivIdx T) : DivCoord T :=
  fun c => if g.1 ∣ c.1 then 1 else 0

def zetaMatrix : Matrix (DivIdx T) (DivIdx T) ℂ :=
  fun c g => if g.1 ∣ c.1 then 1 else 0

section PositivePeriod

variable (hT : 0 < T)
include hT

private lemma dividx_pos (c : DivIdx T) : 0 < c.1 := by
  have hc : c.1 ∣ T := (Nat.mem_divisors.mp c.2).1
  exact Nat.pos_of_dvd_of_pos hc hT

lemma zetaMatrix_isLowerTriangular : (zetaMatrix (T := T)).IsLowerTriangular := by
  intro c g hcg
  simp only [zetaMatrix]
  split
  · rename_i hd
    have hle : g.1 ≤ c.1 := Nat.le_of_dvd (dividx_pos hT c) hd
    exact (not_le_of_gt hcg) hle |>.elim
  · rfl

lemma zetaMatrix_det : (zetaMatrix (T := T)).det = 1 := by
  rw [Matrix.det_of_isLowerTriangular _ (zetaMatrix_isLowerTriangular hT)]
  simp [zetaMatrix]

lemma zetaMatrix_det_isUnit : IsUnit (zetaMatrix (T := T)).det := by
  rw [zetaMatrix_det hT]
  exact isUnit_one

def zetaEquiv : DivCoord T ≃ₗ[ℂ] DivCoord T :=
  Matrix.toLinearEquiv (Pi.basisFun ℂ (DivIdx T)) (zetaMatrix (T := T))
    (zetaMatrix_det_isUnit hT)

def widthBasis : Module.Basis (DivIdx T) ℂ (DivCoord T) :=
  (Pi.basisFun ℂ (DivIdx T)).map (zetaEquiv hT)

lemma zetaEquiv_basisFun (g : DivIdx T) :
    zetaEquiv hT ((Pi.basisFun ℂ (DivIdx T)) g) = widthVec g := by
  change Matrix.toLin (Pi.basisFun ℂ (DivIdx T)) (Pi.basisFun ℂ (DivIdx T))
      (zetaMatrix (T := T)) ((Pi.basisFun ℂ (DivIdx T)) g) = widthVec g
  rw [Matrix.toLin_self]
  funext c
  rw [Finset.sum_apply]
  rw [Finset.sum_eq_single c]
  · simp [Pi.basisFun_apply, zetaMatrix, widthVec]
  · intro b hb hbc
    have hs : (Pi.single b (1 : ℂ) : DivCoord T) c = 0 :=
      Pi.single_eq_of_ne (M := fun _ : DivIdx T => ℂ) hbc.symm (1 : ℂ)
    rw [Pi.basisFun_apply]
    simp [hs]
  · intro hc
    exact (hc (Finset.mem_attach _ c)).elim

lemma widthBasis_apply (g : DivIdx T) : widthBasis hT g = widthVec g := by
  rw [widthBasis, Module.Basis.map_apply]
  exact zetaEquiv_basisFun hT g

end PositivePeriod

/-- Diagonal action of divisor coordinates on the divisor-coordinate space. -/
def diagOp : DivCoord T →ₗ[ℂ] Module.End ℂ (DivCoord T) where
  toFun a :=
    { toFun := fun x c => a c * x c
      map_add' := by intro x y; funext c; simp [mul_add]
      map_smul' := by intro r x; funext c; simp [mul_left_comm] }
  map_add' := by intro a b; ext x c; simp [add_mul]
  map_smul' := by intro r a; ext x c; simp [mul_assoc]

lemma diagOp_injective : Function.Injective (diagOp (T := T)) := by
  intro a b hab
  funext c
  have h := congrArg (fun L : Module.End ℂ (DivCoord T) => L (fun _ => 1) c) hab
  simpa [diagOp] using h

abbrev ProjectorAlg (T : ℕ) := LinearMap.range (diagOp (T := T))

def diagEquiv : DivCoord T ≃ₗ[ℂ] ProjectorAlg T :=
  LinearEquiv.ofInjective (diagOp (T := T)) (diagOp_injective (T := T))

section PositiveOperatorBasis

variable (hT : 0 < T)
include hT

/-- The actual width-projector basis in the diagonal endomorphism algebra. -/
def widthOperatorBasis : Module.Basis (DivIdx T) ℂ (ProjectorAlg T) :=
  (widthBasis hT).map (diagEquiv (T := T))

lemma widthOperatorBasis_apply (g : DivIdx T) :
    widthOperatorBasis hT g = diagEquiv (T := T) (widthVec g) := by
  rw [widthOperatorBasis, Module.Basis.map_apply, widthBasis_apply hT]

/-- The number of independent width-projector operators is exactly the number of divisors of T. -/
lemma projectorAlg_finrank : Module.finrank ℂ (ProjectorAlg T) = Fintype.card (DivIdx T) := by
  exact Module.finrank_eq_card_basis (widthOperatorBasis hT)

end PositiveOperatorBasis

end KomorebiCrossRadix

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Composition of diagonal operators is pointwise multiplication of divisor coordinates. -/
lemma diagOp_comp (a b : DivCoord T) :
    (diagOp a).comp (diagOp b) = diagOp (fun c => a c * b c) := by
  ext x c
  simp [diagOp, mul_assoc]

section PositiveLCM

variable (hT : 0 < T)
include hT

/-- Canonical divisor index obtained by joining two width classes. -/
def lcmIdx (g h : DivIdx T) : DivIdx T := by
  refine ⟨Nat.lcm g.1 h.1, Nat.mem_divisors.mpr ⟨?_, hT.ne'⟩⟩
  exact Nat.lcm_dvd (Nat.mem_divisors.mp g.2).1 (Nat.mem_divisors.mp h.2).1

/-- The actual diagonal width operator associated with a divisor class. -/
def widthEnd (g : DivIdx T) : Module.End ℂ (DivCoord T) :=
  diagOp (widthVec g)

lemma widthVec_mul (g h c : DivIdx T) :
    widthVec g c * widthVec h c = widthVec (lcmIdx hT g h) c := by
  simp only [widthVec, lcmIdx]
  by_cases hg : g.1 ∣ c.1 <;> by_cases hh : h.1 ∣ c.1 <;>
    simp [Nat.lcm_dvd_iff, hg, hh]

/-- Canonical widths multiply by least common multiple. -/
lemma widthEnd_comp_lcm (g h : DivIdx T) :
    (widthEnd g).comp (widthEnd h) = widthEnd (lcmIdx hT g h) := by
  rw [widthEnd, widthEnd, widthEnd, diagOp_comp]
  congr 1
  funext c
  exact widthVec_mul hT g h c


lemma widthOperatorBasis_val (g : DivIdx T) :
    (widthOperatorBasis hT g : ProjectorAlg T).1 = widthEnd g := by
  rw [widthOperatorBasis_apply hT]
  rfl

lemma widthEnd_idempotent (g : DivIdx T) :
    (widthEnd g).comp (widthEnd g) = widthEnd g := by
  simpa [lcmIdx, Nat.lcm_self] using widthEnd_comp_lcm hT g g

lemma widthEnd_commute (g h : DivIdx T) :
    (widthEnd g).comp (widthEnd h) = (widthEnd h).comp (widthEnd g) := by
  rw [widthEnd_comp_lcm hT, widthEnd_comp_lcm hT]
  congr 1
  apply Subtype.ext
  exact Nat.lcm_comm _ _

end PositiveLCM

end KomorebiCrossRadix
