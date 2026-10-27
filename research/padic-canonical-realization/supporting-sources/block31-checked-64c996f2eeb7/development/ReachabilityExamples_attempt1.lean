import KomorebiPadic.ReachableMaskAutomaton
import KomorebiPadic.IdealClosureExamples

/-! # Strictness and scope witnesses for correlated reachability
The correlated example is smaller than every coordinate-ideal product.
The span can still be larger than the orbit and can contain unobservable states.
-/
namespace KomorebiPadic
namespace LinearReachability
noncomputable section

variable {R I A : Type*} [CommRing R] [Fintype I]

def ofCoordinateSystem (M : CoordinateSupport.System R I A) : System R (I → R) A where
  initial := M.initial
  transition := M.transition

theorem ofCoordinateSystem_run (M : CoordinateSupport.System R I A) (ds : List A) (x : I → R) :
    run (ofCoordinateSystem M) ds x = CoordinateSupport.run M ds x := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (M.transition d x)

def correlated : System (ZMod 5) (Fin 3 → ZMod 5) (Fin 1) :=
  ofCoordinateSystem CoordinateSupport.correlatedSystem

def diagonal : Submodule (ZMod 5) (Fin 3 → ZMod 5) where
  carrier := {x | x 0 = x 1 ∧ x 2 = 0}
  zero_mem' := ⟨rfl,rfl⟩
  add_mem' hx hy := by constructor <;> simp only [Pi.add_apply, hx.1, hy.1, hx.2, hy.2, add_zero]
  smul_mem' a x hx := by constructor <;> simp only [Pi.smul_apply, hx.1, hx.2, smul_zero]

theorem diagonal_transition_zero (d : Fin 1) (x : Fin 3 → ZMod 5) (hx : x ∈ diagonal) :
    correlated.transition d x = 0 := by
  change x 0 = x 1 ∧ x 2 = 0 at hx
  funext j
  fin_cases j <;> simp [correlated, ofCoordinateSystem, CoordinateSupport.correlatedSystem,
    CoordinateSupport.matrixSystem, Fin.sum_univ_succ, hx.1]

theorem diagonal_closed : Closed correlated diagonal := by
  refine ⟨?_, fun d x hx => ?_⟩
  · change correlated.initial 0 = correlated.initial 1 ∧ correlated.initial 2 = 0
    norm_num [correlated, ofCoordinateSystem, CoordinateSupport.correlatedSystem, CoordinateSupport.matrixSystem]
  · rw [diagonal_transition_zero d x hx]
    exact diagonal.zero_mem

/-- This relation, rather than three independent full coordinates, is exact. -/
theorem correlated_reachable_eq_diagonal : reachable correlated = diagonal := by
  apply le_antisymm (reachable_le correlated diagonal diagonal_closed)
  intro x hx
  change x 0 = x 1 ∧ x 2 = 0 at hx
  have he : x = (x 0) • correlated.initial := by
    funext i
    fin_cases i <;> simp [correlated, ofCoordinateSystem, CoordinateSupport.correlatedSystem,
      CoordinateSupport.matrixSystem, Pi.smul_apply, hx.1, hx.2]
  rw [he]
  exact (reachable correlated).smul_mem _ (initial_mem_reachable correlated)

def diagonalEquiv : ZMod 5 ≃ₗ[ZMod 5] diagonal where
  toFun a := ⟨fun i => if i = 2 then 0 else a, by constructor <;> norm_num⟩
  invFun x := x.val 0
  left_inv a := by simp
  right_inv x := by
    apply Subtype.ext
    funext i
    have hx : x.val 0 = x.val 1 ∧ x.val 2 = 0 := x.property
    fin_cases i <;> simp [hx.1,hx.2]
  map_add' a b := by apply Subtype.ext; funext i; split_ifs <;> simp
  map_smul' a b := by apply Subtype.ext; funext i; split_ifs <;> simp

theorem correlated_reachable_card : Nat.card (State correlated) = 5 := by
  change Nat.card (reachable correlated) = 5
  rw [correlated_reachable_eq_diagonal, ← Nat.card_congr diagonalEquiv.toEquiv, Nat.card_zmod]

/-- The previous product of coordinate ideals is the entire three-coordinate box. -/
theorem correlated_ideal_full :
    CoordinateIdeal.least (p := 5) (r := 1) (by decide : 0 < 5) CoordinateSupport.correlatedSystem =
      fun _ => 1 := by
  let hp : 0 < 5 := by decide
  have hc := CoordinateIdeal.least_closed (p := 5) (r := 1) hp CoordinateSupport.correlatedSystem
  have hb := CoordinateIdeal.least_bound (p := 5) (r := 1) hp CoordinateSupport.correlatedSystem
  have h0 : 1 ≤ CoordinateIdeal.least hp (r := 1) CoordinateSupport.correlatedSystem (0 : Fin 3) := by
    exact hc.1 0
  have h1 : 1 ≤ CoordinateIdeal.least hp (r := 1) CoordinateSupport.correlatedSystem (1 : Fin 3) := by
    exact hc.1 1
  have h2 := hc.2 (0 : Fin 1) (0 : Fin 3) (2 : Fin 3)
  have he0 : CoordinateIdeal.least hp (r := 1) CoordinateSupport.correlatedSystem (0 : Fin 3) = 1 :=
    le_antisymm (hb 0) h0
  rw [he0] at h2
  have ht : PrimePowerIdeal.transfer 5 1
      (CoordinateSupport.correlatedSystem.transition 0 (Pi.single 0 1) 2) 1 = 1 := by
    rw [CoordinateSupport.correlatedSystem, CoordinateSupport.matrixSystem_column]
    decide +kernel
  rw [ht] at h2
  funext i
  fin_cases i
  · exact he0
  · exact le_antisymm (hb 1) h1
  · exact le_antisymm (hb 2) h2

theorem correlated_ideal_card :
    Nat.card (CoordinateIdeal.State (p := 5) (r := 1)
      (CoordinateIdeal.least (by decide : 0 < 5) CoordinateSupport.correlatedSystem)) = 125 := by
  rw [CoordinateIdeal.boxState_card (by decide : 0 < 5) _
    (CoordinateIdeal.least_bound (by decide : 0 < 5) CoordinateSupport.correlatedSystem), correlated_ideal_full]
  norm_num

def constantOrbit : System (ZMod 5) (ZMod 5) (Fin 1) where
  initial := 1
  transition _ := LinearMap.id

theorem constantOrbit_run (ds : List (Fin 1)) : run constantOrbit ds 1 = 1 := by
  induction ds with
  | nil => rfl
  | cons d ds ih => exact ih

theorem constantOrbit_reachable_top : reachable constantOrbit = ⊤ := by
  apply top_unique
  intro x _
  have h := (reachable constantOrbit).smul_mem x (initial_mem_reachable constantOrbit)
  simpa only [constantOrbit, smul_eq_mul, mul_one] using h

/-- The reachable linear module is not the set of states in the initial orbit. -/
theorem span_strictly_exceeds_orbit :
    (0 : ZMod 5) ∈ reachable constantOrbit ∧
      ∀ ds : List (Fin 1), run constantOrbit ds constantOrbit.initial ≠ 0 := by
  refine ⟨(reachable constantOrbit).zero_mem, ?_⟩
  intro ds
  change run constantOrbit ds 1 ≠ 0
  rw [constantOrbit_run]
  decide +kernel

/-- Reachability still permits invisible directions: zero output cannot distinguish them. -/
theorem reachability_is_not_observability :
    Nat.card (State constantOrbit) = 5 ∧
      ∀ ds : List (Fin 1), ∀ x : ZMod 5,
        (0 : ZMod 5 →ₗ[ZMod 5] ZMod 5) (run constantOrbit ds x) = 0 := by
  constructor
  · change Nat.card (reachable constantOrbit) = 5
    rw [constantOrbit_reachable_top]
    simp [Nat.card_eq_fintype_card]
  · intro ds x
    rfl
end
end LinearReachability
end KomorebiPadic
