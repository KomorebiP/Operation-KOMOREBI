module
public import LogicalHorizon

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation
universe u v w z
variable {X : Type u} {A : Type v} {O : Type w} {V : Type z}

def twoVariables (x y : X) : Fin 2 → X :=
  fun i => if i.val = 0 then x else y

def pairObservation (word : List A) (j : O) : Formula A O V 2 :=
  .equal (.probe 0 word j) (.probe 1 word j)

theorem behavior_iff_all_pair_formulas (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ word j,
      (pairObservation word j : Formula A O V 2).Holds S (twoVariables x y) := Iff.rfl

def TestsAgree (S : System X A O V) (tests : List (List A × O)) (x y : X) : Prop :=
  ∀ t ∈ tests, behavior S x t.1 t.2 = behavior S y t.1 t.2

/-- Compile a finite observation code into a formula defining equality of its codes. -/
def testEqualityFormula : List (List A × O) → Formula A O V 2
  | [] => .neg .falsum
  | t::ts => .conj (.equal (.probe 0 t.1 t.2) (.probe 1 t.1 t.2)) (testEqualityFormula ts)

theorem testEqualityFormula_holds (S : System X A O V) (tests : List (List A × O)) (x y : X) :
    (testEqualityFormula tests : Formula A O V 2).Holds S (twoVariables x y) ↔
      TestsAgree S tests x y := by
  induction tests with
  | nil => simp [testEqualityFormula, Formula.Holds, TestsAgree]
  | cons t ts ih =>
    change (behavior S x t.1 t.2 = behavior S y t.1 t.2 ∧
      (testEqualityFormula ts : Formula A O V 2).Holds S (twoVariables x y)) ↔ _
    rw [ih]
    simp only [TestsAgree, List.mem_cons]
    constructor
    · rintro ⟨h,hs⟩ u hu
      rcases hu with hu | hu
      · subst u; exact h
      · exact hs u hu
    · intro h
      exact ⟨h t (Or.inl rfl), fun u hu => h u (Or.inr hu)⟩

theorem testEqualityFormula_qrank (tests : List (List A × O)) :
    (testEqualityFormula tests : Formula A O V 2).qrank = 0 := by
  induction tests with
  | nil => rfl
  | cons t ts ih => simp [testEqualityFormula, Formula.qrank, ih]

def testsDepth : List (List A × O) → Nat
  | [] => 0
  | t::ts => max t.1.length (testsDepth ts)

theorem testEqualityFormula_depth (tests : List (List A × O)) :
    (testEqualityFormula tests : Formula A O V 2).depth = testsDepth tests := by
  induction tests with
  | nil => rfl
  | cons t ts ih => simp [testEqualityFormula, Formula.depth, ValueTerm.depth, testsDepth, ih]

/-- A local closure certificate turns a finite code into an all-word definability theorem. -/
theorem certified_finite_definability (S : System X A O V) (tests : List (List A × O))
    (hout : ∀ x y, TestsAgree S tests x y → ∀ j, S.observe j x = S.observe j y)
    (hstep : ∀ x y, TestsAgree S tests x y → ∀ a,
      TestsAgree S tests (S.step a x) (S.step a y)) (x y : X) :
    (testEqualityFormula tests : Formula A O V 2).Holds S (twoVariables x y) ↔ ObsEq S x y := by
  rw [testEqualityFormula_holds]
  constructor
  · exact invariant_relation_sound S (TestsAgree S tests) hout hstep
  · intro h t _
    exact h t.1 t.2

/-- Merely checking the tests is not enough: closure and output hypotheses above
are the soundness certificate, and need independent proofs in every instance. -/
def finiteCode (S : System X A O V) (tests : List (List A × O)) (x : X) : List V :=
  tests.map (fun t => behavior S x t.1 t.2)

theorem finiteCode_equal_iff (S : System X A O V) (tests : List (List A × O)) (x y : X) :
    finiteCode S tests x = finiteCode S tests y ↔ TestsAgree S tests x y := by
  induction tests with
  | nil => simp [finiteCode, TestsAgree]
  | cons t ts ih =>
    change (behavior S x t.1 t.2 :: finiteCode S ts x) =
      (behavior S y t.1 t.2 :: finiteCode S ts y) ↔ _
    rw [List.cons.injEq, ih]
    simp only [TestsAgree, List.mem_cons]
    constructor
    · rintro ⟨ht,hs⟩ u hu
      rcases hu with hu | hu
      · subst u; exact ht
      · exact hs u hu
    · intro h; exact ⟨h t (Or.inl rfl), fun u hu => h u (Or.inr hu)⟩

end Komorebi.LogicalResolution
