module
public import ObservationalFirstOrder

@[expose] public section

namespace Komorebi.ModelTheory
open Komorebi.Representation
universe u v w z
variable {X : Type u} {A : Type v} {O : Type w} {V : Type z}

abbrev ObservationTest (A : Type v) (O : Type w) := List A × O

def CodeEqual (S : System X A O V) (tests : List (ObservationTest A O)) (x y : X) : Prop :=
  ∀ t ∈ tests, behavior S x t.1 t.2 = behavior S y t.1 t.2

/-- Local, checkable obligations. The conclusion "all words agree" is not a field. -/
structure FiniteCodeCertificate (S : System X A O V) (tests : List (ObservationTest A O)) where
  outputs : ∀ x y, CodeEqual S tests x y → ∀ j, S.observe j x = S.observe j y
  steps : ∀ x y, CodeEqual S tests x y → ∀ a,
    CodeEqual S tests (S.step a x) (S.step a y)

def codeRelationFormula : List (ObservationTest A O) → ObsFO A O V 2
  | [] => .truth
  | (w,j)::ts => .conj (.compare (0,w) j (1,w) j) (codeRelationFormula ts)

theorem codeRelationFormula_semantics (S : System X A O V)
    (tests : List (ObservationTest A O)) (e : Fin 2 → X) :
    (codeRelationFormula tests).Sat S e ↔ CodeEqual S tests (e 0) (e 1) := by
  induction tests with
  | nil => simp [codeRelationFormula, ObsFO.Sat, CodeEqual]
  | cons t ts ih =>
    rcases t with ⟨w,j⟩
    simp only [codeRelationFormula, ObsFO.Sat, ih, termObservation]
    constructor
    · rintro ⟨hw,ht⟩ t hm
      rcases List.mem_cons.mp hm with he | he
      · subst t; exact hw
      · exact ht t he
    · intro h
      exact ⟨h (w,j) (List.mem_cons_self),fun t ht => h t (List.mem_cons_of_mem _ ht)⟩

theorem codeRelationFormula_quantifier_free (tests : List (ObservationTest A O)) :
    (codeRelationFormula (V := V) tests).quantifierRank = 0 := by
  induction tests with
  | nil => rfl
  | cons t ts ih =>
    rcases t with ⟨w,j⟩
    simp [codeRelationFormula, ObsFO.quantifierRank, ih]

theorem certified_code_exact (S : System X A O V) (tests : List (ObservationTest A O))
    (cert : FiniteCodeCertificate S tests) (x y : X) :
    CodeEqual S tests x y ↔ ObsEq S x y := by
  constructor
  · exact invariant_relation_sound S (CodeEqual S tests) cert.outputs cert.steps
  · intro he t _
    exact he t.1 t.2

theorem finite_observational_definition (S : System X A O V)
    (tests : List (ObservationTest A O)) (cert : FiniteCodeCertificate S tests)
    (e : Fin 2 → X) :
    (codeRelationFormula tests).Sat S e ↔ ObsEq S (e 0) (e 1) :=
  (codeRelationFormula_semantics S tests e).trans (certified_code_exact S tests cert _ _)

/-- The actual coding map is a tuple of observable terms, not a chosen quotient label. -/
def observationCode (S : System X A O V) (tests : List (ObservationTest A O))
    (x : X) : List V := tests.map (fun t => behavior S x t.1 t.2)

theorem observationCode_eq_iff (S : System X A O V) (tests : List (ObservationTest A O))
    (x y : X) : observationCode S tests x = observationCode S tests y ↔ CodeEqual S tests x y := by
  induction tests with
  | nil => simp [observationCode,CodeEqual]
  | cons t ts ih =>
    simp only [observationCode,List.map_cons,List.cons.injEq]
    constructor
    · rintro ⟨ht,hs⟩ u hu
      rcases List.mem_cons.mp hu with he | he
      · subst u; exact ht
      · exact ih.mp hs u he
    · intro h
      exact ⟨h t List.mem_cons_self,ih.mpr (fun u hu => h u (List.mem_cons_of_mem _ hu))⟩

theorem certified_observationCode (S : System X A O V) (tests : List (ObservationTest A O))
    (cert : FiniteCodeCertificate S tests) (x y : X) :
    observationCode S tests x = observationCode S tests y ↔ ObsEq S x y :=
  (observationCode_eq_iff S tests x y).trans (certified_code_exact S tests cert x y)

end Komorebi.ModelTheory
