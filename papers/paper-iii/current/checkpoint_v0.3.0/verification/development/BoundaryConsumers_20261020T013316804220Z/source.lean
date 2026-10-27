import KomorebiPaperIII.NonlinearPacketCoordinates
import KomorebiPaperIII.PacketDirectSum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-! External consumers, not production theorem-count additions. -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
open Komorebi.PaperIII.PacketCoordinates
namespace PaperIIIBoundary

abbrev V := ℚ × ℚ

def oblique0 : V →ₗ[ℚ] V where
  toFun x := (x.1 + x.2, 0)
  map_add' x y := by apply Prod.ext <;> simp [add_assoc, add_left_comm, add_comm]
  map_smul' c x := by apply Prod.ext <;> simp [mul_add]

def oblique1 : V →ₗ[ℚ] V where
  toFun x := (-x.2, x.2)
  map_add' x y := by apply Prod.ext <;> simp [add_comm]
  map_smul' c x := by apply Prod.ext <;> simp

def oblique : System ℚ V (Fin 2) where
  projector i := if i = 0 then oblique0 else oblique1
  complete := by
    apply LinearMap.ext
    intro x
    apply Prod.ext <;> simp [Fin.sum_univ_two, oblique0, oblique1]
  idempotent i := by
    fin_cases i <;> apply LinearMap.ext <;> intro x <;> apply Prod.ext <;>
      simp [oblique0, oblique1]
  orthogonal i j h := by
    fin_cases i <;> fin_cases j <;> try contradiction
    all_goals apply LinearMap.ext
    all_goals intro x
    all_goals apply Prod.ext <;> simp [oblique0, oblique1]

example : (oblique.analysis (2, 3) 0 : V) = (5, 0) := by
  norm_num [oblique, System.analysis, oblique0]
example : (oblique.analysis (2, 3) 1 : V) = (-3, 3) := by
  norm_num [oblique, System.analysis, oblique1]

example (x : V) : oblique.synthesis (oblique.analysis x) = x := oblique.synthesis_analysis x
example (z : oblique.Coordinates) : oblique.analysis (oblique.synthesis z) = z :=
  oblique.analysis_synthesis z
example (x : V) (i : Fin 2) : (oblique.directSumEquiv x i : V) = oblique.projector i x :=
  oblique.directSumEquiv_component x i

def mixed (x : V) : V := (x.1 * x.2, x.1^2 + x.2)
example : mixed (2, 3) = (6, 7) := by norm_num [mixed]
example : mixed (2, 3) ≠ ((mixed (2, 0)).1, (mixed (0, 3)).2) := by norm_num [mixed]
example : oblique.synthesis (coordinateMap oblique oblique mixed (oblique.analysis (2, 3))) = (6, 7) := by
  rw [coordinateMap_analysis, oblique.synthesis_analysis]
  norm_num [mixed]
example (f g : V → V) : coordinateMap oblique oblique (g ∘ f) =
    coordinateMap oblique oblique g ∘ coordinateMap oblique oblique f :=
  coordinateMap_comp oblique oblique oblique f g
example (f : V → V) (n : Nat) (x : V) :
    (coordinateMap oblique oblique f)^[n] (oblique.analysis x) = oblique.analysis x ↔
      (f^[n]) x = x := periodicPoint_iff oblique f n x

-- The advertised result requires neither scalar commutativity nor additive inverses.
universe u v w
example {R : Type u} [Semiring R] {M : Type v} [AddCommMonoid M] [Module R M]
    {I : Type w} [Fintype I] (P : System R M I) (x : M) :
    P.synthesis (P.analysis x) = x := P.synthesis_analysis x

end PaperIIIBoundary
