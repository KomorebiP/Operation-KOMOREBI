import KTG.Basic

namespace KTG

universe uA vA uB vB gA gB

/-- Grade/normalization data transported alongside the mathematical object.
    The `compatible` relation says when a source/target pair is intended to be a
    legitimate transported pair. -/
structure KNormalization
    (A : KContext.{uA, vA}) (B : KContext.{uB, vB}) where
  GradeA : Type gA
  GradeB : Type gB
  gradeA : A.Obj → GradeA
  gradeB : B.Obj → GradeB
  sigma : GradeA → GradeB
  compatible : A.Obj → B.Obj → Prop
  preserves : ∀ {a b}, compatible a b → gradeB b = sigma (gradeA a)

/-- A normalization certificate is just the compatibility proof expected by a
    particular normalization structure. -/
def NormalizationWitness
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (N : KNormalization A B) (a : A.Obj) (b : B.Obj) : Prop :=
  N.compatible a b

end KTG
