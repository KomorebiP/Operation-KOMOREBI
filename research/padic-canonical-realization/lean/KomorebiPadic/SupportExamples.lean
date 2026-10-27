import KomorebiPadic.SupportMaskAutomaton
import Mathlib.Tactic.FinCases

/-! # Restriction witnesses for coordinate-support leastness
Correlated input cancellations and nonunit initial coefficients are not grounds
for removing a column needed by the whole coordinate-supported module.
-/
namespace KomorebiPadic
namespace CoordinateSupport

variable {R I A : Type*} [CommRing R] [Fintype I]

/-- Exact finite matrices, with row j and source-column i convention. -/
noncomputable def matrixSystem (v : I → R) (m : A → I → I → R) : System R I A where
  initial := v
  transition d :=
    { toFun := fun x j => ∑ i : I, m d j i * x i
      map_add' := by
        intro x y
        funext j
        simp [mul_add, Finset.sum_add_distrib]
      map_smul' := by
        intro a x
        funext j
        simp only [Pi.smul_apply, smul_eq_mul]
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro i _
        simp only [RingHom.id_apply]
        ring }

theorem matrixSystem_column [DecidableEq I] (v : I → R) (m : A → I → I → R) (d : A) (i j : I) :
    (matrixSystem v m).transition d (Pi.single i 1) j = m d j i := by
  classical
  simp [matrixSystem, Pi.single_apply]

/-- Both source columns reach position 2, but their particular initial values cancel. -/
noncomputable def correlatedSystem : System (ZMod 5) (Fin 3) (Fin 1) :=
  matrixSystem (fun i => if i = 2 then 0 else 1)
    (fun _ j i => if j = 2 then (if i = 0 then 1 else if i = 1 then -1 else 0) else 0)

theorem correlatedSystem_initial_step (d : Fin 1) :
    correlatedSystem.transition d correlatedSystem.initial = 0 := by
  funext j
  fin_cases j <;> (norm_num [correlatedSystem, matrixSystem, Fin.sum_univ_succ]; decide +kernel)

theorem correlatedSystem_least_full : least correlatedSystem = Finset.univ := by
  apply Finset.Subset.antisymm (Finset.subset_univ _)
  intro i _
  have h0 : (0 : Fin 3) ∈ least correlatedSystem :=
    mem_least_of_initial _ 0 (by norm_num [correlatedSystem, matrixSystem]; decide +kernel)
  have h1 : (1 : Fin 3) ∈ least correlatedSystem :=
    mem_least_of_initial _ 1 (by norm_num [correlatedSystem, matrixSystem]; decide +kernel)
  have h2 : (2 : Fin 3) ∈ least correlatedSystem :=
    mem_least_of_edge _ h0 ⟨0, by rw [correlatedSystem, matrixSystem_column]; norm_num; decide +kernel⟩
  fin_cases i <;> assumption

/-- Position 2 is never present in this orbit, despite being needed for coordinate invariance. -/
theorem correlatedSystem_orbit_coordinate_zero (ds : List (Fin 1)) :
    run correlatedSystem ds correlatedSystem.initial 2 = 0 := by
  cases ds with
  | nil => norm_num [run, correlatedSystem, matrixSystem]
  | cons d ds => rw [run, correlatedSystem_initial_step, run_zero]; rfl

/-- A zero divisor can similarly kill a nonzero matrix entry on the particular initial vector. -/
noncomputable def nilpotentSystem : System (ZMod 4) (Fin 2) (Fin 1) :=
  matrixSystem (fun i => if i = 0 then 2 else 0)
    (fun _ j i => if j = 1 ∧ i = 0 then 2 else 0)

theorem nilpotentSystem_least_full : least nilpotentSystem = Finset.univ := by
  apply Finset.Subset.antisymm (Finset.subset_univ _)
  intro i _
  have h0 : (0 : Fin 2) ∈ least nilpotentSystem :=
    mem_least_of_initial _ 0 (by norm_num [nilpotentSystem, matrixSystem]; decide +kernel)
  have h1 : (1 : Fin 2) ∈ least nilpotentSystem :=
    mem_least_of_edge _ h0 ⟨0, by rw [nilpotentSystem, matrixSystem_column]; norm_num; decide +kernel⟩
  fin_cases i <;> assumption

theorem nilpotentSystem_initial_step (d : Fin 1) :
    nilpotentSystem.transition d nilpotentSystem.initial = 0 := by
  funext j
  fin_cases j <;> (norm_num [nilpotentSystem, matrixSystem, Fin.sum_univ_succ] <;> decide +kernel)

end CoordinateSupport
end KomorebiPadic
