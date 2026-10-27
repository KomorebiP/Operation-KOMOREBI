import KomorebiRepair.RationalMenuCover

/-!
Proof-carrying branch-and-bound for rational menus.
A tree covers an interval of candidate subsets, without enumerating the
powerset in the verifier. Leaves prove a cost bound, linear infeasibility,
or exclusion by the original admissibility table. The all-subsets mode
uses no admissibility table. Costs are fixed nonnegative natural weights.
-/
set_option autoImplicit false
namespace KomorebiRepair.RationalCertificates

variable {m n q s : ℕ}

/-- `none` admits all selections; `some []` admits none. -/
def branchAllowed (table : Option (List (Finset (Fin q))))
    (S : Finset (Fin q)) : Bool :=
  match table with
  | none => true
  | some xs => tableAllowed xs S

structure BranchProblem (m n q s : ℕ) where
  D : Mat m n
  E : Mat m q
  R : Mat m s
  weights : Fin q → ℕ
  admitted : Option (List (Finset (Fin q)))

def BranchProblem.original (P : BranchProblem m n q s) : Problem m n q s :=
  ⟨P.D, P.E, P.R, branchAllowed P.admitted, additiveCost P.weights⟩

/-- The interval is the family lo ⊆ T ⊆ hi. -/
abbrev InInterval (lo hi T : Finset (Fin q)) : Prop := lo ⊆ T ∧ T ⊆ hi

/-- Checks the original finite table, not the subset universe. -/
def intervalExcluded (table : Option (List (Finset (Fin q))))
    (lo hi : Finset (Fin q)) : Bool :=
  match table with
  | none => false
  | some xs => xs.all (fun T => decide (¬ InInterval lo hi T))

theorem intervalExcluded_sound (table : Option (List (Finset (Fin q))))
    (lo hi T : Finset (Fin q)) (h : intervalExcluded table lo hi = true)
    (hT : InInterval lo hi T) : branchAllowed table T ≠ true := by
  cases table with
  | none => simp [intervalExcluded] at h
  | some xs =>
    have hx : ∀ S ∈ xs, decide (¬ InInterval lo hi S) = true := List.all_eq_true.mp h
    intro ha
    have hm : T ∈ xs := (tableAllowed_iff xs T).mp ha
    exact (of_decide_eq_true (hx T hm)) hT

theorem additiveCost_mono (weights : Fin q → ℕ) {S T : Finset (Fin q)}
    (h : S ⊆ T) : additiveCost weights S ≤ additiveCost weights T := by
  exact Finset.sum_le_sum_of_subset h

/-- none asks for impossibility; some c asks for a cost lower bound c. -/
def MeetsBound (threshold : Option ℕ) (cost : ℕ) : Prop :=
  match threshold with
  | none => False
  | some c => c ≤ cost

def boundCheck (threshold : Option ℕ) (cost : ℕ) : Bool :=
  match threshold with
  | none => false
  | some c => decide (c ≤ cost)

theorem boundCheck_mono (threshold : Option ℕ) {a b : ℕ}
    (h : boundCheck threshold a = true) (hab : a ≤ b) : MeetsBound threshold b := by
  cases threshold with
  | none => simp [boundCheck] at h
  | some c => exact Nat.le_trans (of_decide_eq_true h) hab

/-- Certificates contain no assumed theorem or assumed feasible map. -/
inductive BranchTree (m q : ℕ) where
  | bound : BranchTree m q
  | separator (Y : Mat 1 m) : BranchTree m q
  | inadmissible : BranchTree m q
  | split (j : Fin q) (excluded included : BranchTree m q) : BranchTree m q
  deriving Inhabited

/-- Structural recursion on a supplied finite proof tree. -/
def checkBranch (P : BranchProblem m n q s) (threshold : Option ℕ)
    (lo hi : Finset (Fin q)) : BranchTree m q → Bool
  | .bound => boundCheck threshold (P.original.cost lo)
  | .separator Y => checkSeparator P.original hi Y
  | .inadmissible => intervalExcluded P.admitted lo hi
  | .split j excluded included =>
      decide (j ∈ hi ∧ j ∉ lo) &&
      checkBranch P threshold lo (hi.erase j) excluded &&
      checkBranch P threshold (insert j lo) hi included

/-- Every target subset belongs to exactly the required branch; the checker
cannot omit the include child or the exclude child. -/
theorem checkBranch_sound (P : BranchProblem m n q s) (threshold : Option ℕ)
    (tree : BranchTree m q) :
    ∀ (lo hi : Finset (Fin q)), checkBranch P threshold lo hi tree = true →
    ∀ T : Finset (Fin q), InInterval lo hi T → P.original.allowed T = true →
      Feasible P.original T → MeetsBound threshold (P.original.cost T) := by
  induction tree with
  | bound =>
    intro lo hi h T hT _ _
    exact boundCheck_mono threshold h (additiveCost_mono P.weights hT.1)
  | separator Y =>
    intro lo hi h T hT _ hf
    have hs : Separates P.original hi Y := of_decide_eq_true h
    exact False.elim ((separator_sound P.original T Y
      (separates_subset P.original hi T Y hT.2 hs)) hf)
  | inadmissible =>
    intro lo hi h T hT ha _
    exact False.elim (intervalExcluded_sound P.admitted lo hi T h hT ha)
  | split j excluded included ihe ihi =>
    intro lo hi h T hT ha hf
    have hh : (decide (j ∈ hi ∧ j ∉ lo) &&
      checkBranch P threshold lo (hi.erase j) excluded) = true ∧
      checkBranch P threshold (insert j lo) hi included = true :=
      Bool.and_eq_true_iff.mp h
    have he := (Bool.and_eq_true_iff.mp hh.1).2
    by_cases hj : j ∈ T
    · exact ihi (insert j lo) hi hh.2 T
        ⟨Finset.insert_subset hj hT.1, hT.2⟩ ha hf
    · exact ihe lo (hi.erase j) he T
        ⟨hT.1, fun x hx => Finset.mem_erase.mpr
          ⟨fun hEq => hj (hEq ▸ hx), hT.2 hx⟩⟩ ha hf

def checkTreeOptimal (P : BranchProblem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) (tree : BranchTree m q) : Bool :=
  checkRepair P.original S U W &&
  checkBranch P (some (P.original.cost S)) ∅ Finset.univ tree

theorem checkTreeOptimal_sound (P : BranchProblem m n q s) (S : Finset (Fin q))
    (U : Mat n s) (W : Mat q s) (tree : BranchTree m q)
    (h : checkTreeOptimal P S U W tree = true) :
    P.original.allowed S = true ∧ Equation P.original S U W ∧
    ∀ T : Finset (Fin q), P.original.allowed T = true → Feasible P.original T →
      P.original.cost S ≤ P.original.cost T := by
  have hh := Bool.and_eq_true_iff.mp h
  have hr : P.original.allowed S = true ∧ Equation P.original S U W :=
    of_decide_eq_true hh.1
  refine ⟨hr.1, hr.2, ?_⟩
  intro T ha hf
  exact checkBranch_sound P (some (P.original.cost S)) tree ∅ Finset.univ hh.2 T
    ⟨Finset.empty_subset T, Finset.subset_univ T⟩ ha hf

def checkTreeNoRepair (P : BranchProblem m n q s) (tree : BranchTree m q) : Bool :=
  checkBranch P none ∅ Finset.univ tree

theorem checkTreeNoRepair_sound (P : BranchProblem m n q s) (tree : BranchTree m q)
    (h : checkTreeNoRepair P tree = true) :
    ∀ T : Finset (Fin q), P.original.allowed T = true → ¬ Feasible P.original T := by
  intro T ha hf
  exact checkBranch_sound P none tree ∅ Finset.univ h T
    ⟨Finset.empty_subset T, Finset.subset_univ T⟩ ha hf

/-- Echo literal weights and the optional table, without a powerset scan. -/
def branchInputJson (P : BranchProblem m n q s) : String :=
  "{\"D\":" ++ matrixJson P.D ++ ",\"E\":" ++ matrixJson P.E ++
  ",\"R\":" ++ matrixJson P.R ++ ",\"costs\":[" ++
  String.intercalate "," ((List.finRange q).map (fun i => toString (P.weights i))) ++
  "],\"admissible_masks\":" ++
  (match P.admitted with
   | none => "null"
   | some xs => "[" ++ String.intercalate "," (xs.map menuJson) ++ "]") ++ "}"

end KomorebiRepair.RationalCertificates
