import KTG.Transport

namespace KTG

universe uA uB uC uD

/-- A transport square is flat when the two relational path composites define
    exactly the same source-to-target relation. -/
def FlatSquare
    {A : Type uA} {B : Type uB} {C : Type uC} {D : Type uD}
    (top : KRel A B) (right : KRel B D)
    (left : KRel A C) (bottom : KRel C D) : Prop :=
  ∀ a d,
    KRel.comp top right a d ↔ KRel.comp left bottom a d

/-- A witness of non-flatness: a source/target pair reachable along one path but
    not the other. -/
def CurvatureWitness
    {A : Type uA} {B : Type uB} {C : Type uC} {D : Type uD}
    (top : KRel A B) (right : KRel B D)
    (left : KRel A C) (bottom : KRel C D) : Prop :=
  ∃ a d,
    (KRel.comp top right a d ∧ ¬ KRel.comp left bottom a d) ∨
    (KRel.comp left bottom a d ∧ ¬ KRel.comp top right a d)

end KTG
