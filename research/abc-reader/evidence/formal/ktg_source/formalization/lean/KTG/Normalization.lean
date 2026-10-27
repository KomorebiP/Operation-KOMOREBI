import KTG.Basic

namespace KTG

universe uA vA uB vB uC vC gA gB gC

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

/-- A normalization certificate is exactly the compatibility proof expected by
    a particular normalization structure. -/
def NormalizationWitness
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (N : KNormalization A B) (a : A.Obj) (b : B.Obj) : Prop :=
  N.compatible a b

/-- A normalization witness exposes the transported grade equation. -/
theorem normalization_grade_eq
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (N : KNormalization A B) {a : A.Obj} {b : B.Obj}
    (h : NormalizationWitness N a b) :
    N.gradeB b = N.sigma (N.gradeA a) :=
  N.preserves h

/-- A typed bridge between the target grades of one normalization and the source
    grades of a second normalization.  This avoids silently identifying grade
    spaces that may use different units or multiplicity conventions. -/
structure KGradeBridge
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {C : KContext.{uC, vC}}
    (N₁ : KNormalization A B) (N₂ : KNormalization B C) where
  bridge : N₁.GradeB → N₂.GradeA
  grade_compatible : ∀ b, N₂.gradeA b = bridge (N₁.gradeB b)

/-- Normalization equations compose only through an explicit typed grade bridge.
    The bridge is the formal location at which unit changes, multiplicities, or
    weights such as a later `j²` factor must be represented. -/
theorem normalization_composes_through_bridge
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {C : KContext.{uC, vC}}
    (N₁ : KNormalization A B) (N₂ : KNormalization B C)
    (G : KGradeBridge N₁ N₂)
    {a : A.Obj} {b : B.Obj} {c : C.Obj}
    (h₁ : NormalizationWitness N₁ a b)
    (h₂ : NormalizationWitness N₂ b c) :
    N₂.gradeB c =
      N₂.sigma (G.bridge (N₁.sigma (N₁.gradeA a))) := by
  calc
    N₂.gradeB c = N₂.sigma (N₂.gradeA b) := N₂.preserves h₂
    _ = N₂.sigma (G.bridge (N₁.gradeB b)) := by rw [G.grade_compatible b]
    _ = N₂.sigma (G.bridge (N₁.sigma (N₁.gradeA a))) := by
      rw [N₁.preserves h₁]

end KTG
