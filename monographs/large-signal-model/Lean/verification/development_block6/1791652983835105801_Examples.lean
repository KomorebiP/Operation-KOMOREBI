import KomorebiLSM.Polynomial
import KomorebiLSM.LinearRefinement
import KomorebiLSM.MemoryBounds
import Mathlib.Tactic.NormNum

/-! Exact examples and hypothesis-boundary counterexamples.
All assertions are ordinary kernel-checked proofs, not native execution.
-/
set_option autoImplicit false
namespace Komorebi.LSM.Examples

abbrev V := ℚ × ℚ

def retainFirst : V →ₗ[ℚ] V where
  toFun x := (x.1, 0)
  map_add' := by intro x y; ext <;> simp
  map_smul' := by intro a x; ext <;> simp

def swap : V →ₗ[ℚ] V where
  toFun x := (x.2, x.1)
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

theorem retain_idempotent (x : V) : retainFirst (retainFirst x) = retainFirst x := rfl

theorem preserved_signal_need_not_close :
    ¬ FiberConstant retainFirst (fun x => retainFirst (swap x)) := by
  intro h
  have hbad := congrArg Prod.fst (h (0,0) (0,1) rfl)
  norm_num [retainFirst, swap] at hbad

theorem full_two_steps_return : retainFirst (swap (swap (1,0))) = (1,0) := rfl

theorem separately_compressed_steps_lose_return :
    retainFirst (swap (retainFirst (swap (retainFirst (1,0))))) = (0,0) := rfl

theorem return_defect_is_nonzero : closureDefect retainFirst swap ≠ 0 := by
  intro h
  have hx := congrArg (fun f : V →ₗ[ℚ] V => (f (0,1)).1) h
  norm_num [closureDefect, unresolved, retainFirst, swap] at hx

/-- An arbitrary ambient redundant vector need not be fixed by consistency projection. -/
def redundantArchive : Realization ℚ V where
  analysis x := (x,x)
  synthesis c := c.1
  reconstruct _ := rfl

theorem redundant_not_all_consistent : ¬ redundantArchive.Consistent (0,1) := by
  rintro ⟨x, hx⟩
  have h0 := congrArg Prod.fst hx
  have h1 := congrArg Prod.snd hx
  simp only [redundantArchive] at h0 h1
  norm_num [h0] at h1

theorem redundant_projection_changes_vector :
    redundantArchive.projector (0,1) = (0,0) := rfl

theorem strict_refinement_has_no_initializer :
    ¬ ∃ J : ℚ → V, ∀ x : V, J x.1 = x := by
  apply no_factor_of_witness (fun x : V => x.1) (fun x : V => x) (0,0) (0,1) rfl
  intro h
  have hh := congrArg Prod.snd h
  norm_num at hh

theorem independent_squares_are_not_the_square_of_sum :
    ((1:ℚ)+1)^2 ≠ (1:ℚ)^2 + 1^2 := by norm_num

theorem cross_packet_term (x y : ℚ) : (x+y)^2 = x^2 + 2*x*y + y^2 := by ring

/-- The exact two-coordinate system in the frozen manuscript. -/
def signalStep : V →ₗ[ℚ] V where
  toFun x := ((1/2)*x.1+x.2, (1/4)*x.1+(1/3)*x.2)
  map_add' := by intro x y; ext <;> simp <;> ring
  map_smul' := by intro a x; ext <;> simp <;> ring

theorem manuscript_first_step : signalStep (1,0) = (1/2,1/4) := by
  norm_num [signalStep]

theorem manuscript_second_step : signalStep (signalStep (1,0)) = (1/2,5/24) := by
  norm_num [signalStep]

theorem manuscript_third_observation : (signalStep (signalStep (signalStep (1,0)))).1 = 11/24 := by
  norm_num [signalStep]

theorem manuscript_omitted_return :
    (retainFirst (signalStep (signalStep (1,0)))).1 -
      (retainFirst (signalStep (retainFirst (signalStep (1,0))))).1 = 1/4 := by
  norm_num [retainFirst, signalStep]

end Komorebi.LSM.Examples
