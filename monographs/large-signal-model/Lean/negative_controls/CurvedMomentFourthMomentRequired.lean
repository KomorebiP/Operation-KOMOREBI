import KomorebiLSM.CurvedMomentPolynomial
import Mathlib.Tactic
set_option autoImplicit false
open Komorebi.LSM.CurvedMoment
open scoped BigOperators

-- A genuine finite probability experiment has the correct first three
-- reference moments and fourth moment 1/3. Its conditional L2 mean is 1/2.
def nodes : Fin 3 → ℝ := ![-1,0,1]
noncomputable def weights : Fin 3 → ℝ := ![1/6,2/3,1/6]
noncomputable def expect (f : ℝ→ℝ) : ℝ := ∑ i : Fin 3,weights i*f (nodes i)

example : ∀ i,0≤weights i := by intro i;fin_cases i <;> norm_num [weights]
example : expect (fun _ => 1)=1 := by norm_num [expect,weights,nodes,Fin.sum_univ_succ]
example : expect (fun u => u)=0 := by norm_num [expect,weights,nodes,Fin.sum_univ_succ]
example : expect (fun u => u^2)=1/3 := by norm_num [expect,weights,nodes,Fin.sum_univ_succ]
example : expect (fun u => u^3)=0 := by norm_num [expect,weights,nodes,Fin.sum_univ_succ]
example : expect (fun u => u^4)=1/3 := by norm_num [expect,weights,nodes,Fin.sum_univ_succ]

theorem actualLikelihood (u : ℝ) : likelihood 0 1 u (curve 1)=1+legendre u := by
  change 1+0*u*1+1*legendre u*1^2=1+legendre u
  ring

example : ∀ i,0≤weights i*likelihood 0 1 (nodes i) (curve 1) := by
  intro i
  simp_rw [actualLikelihood]
  fin_cases i <;> norm_num [weights,nodes,legendre]

example : expect (fun u => likelihood 0 1 u (curve 1))=1 := by
  simp_rw [actualLikelihood]
  norm_num [expect,weights,nodes,Fin.sum_univ_succ,legendre]

example : expect (fun u => legendre u*likelihood 0 1 u (curve 1))=1/5 := by
  simp_rw [actualLikelihood]
  norm_num [expect,weights,nodes,Fin.sum_univ_succ,legendre]
