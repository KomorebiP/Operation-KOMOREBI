module
public import MatrixObservationCode
public import StandardObservationConsequences

@[expose] public section
namespace Komorebi.ModelTheory.MatrixBridge
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory.Standard
open FirstOrder.Language
variable {R : Type} {d t k o l : Nat}

/-- Only State, observation functions and permitted action words occur.
    The encoding matrix is not a new function or relation symbol. -/
def matrixCodeFormula (c : CertificateData R d t k o l) :
    (observationLanguage (Fin k) (Fin o) R).Formula (Fin 2) :=
  guardedCodeFormula (matrixTests c)

theorem matrixCodeFormula_isQF (c : CertificateData R d t k o l) :
    (matrixCodeFormula c).IsQF := guardedCodeFormula_isQF (matrixTests c)

variable [Lean.Grind.Semiring R]

/-- Both wrong-sort inputs are excluded by the actual first-order formula. -/
theorem matrixCodeFormula_semantics (c : CertificateData R d t k o l) (h : Valid c)
    (e : Fin 2 → TaggedCarrier (Vec R d) R) :
    taggedRealize (sourceSystem c) (matrixCodeFormula c) e ↔
      ∃ env : Fin 2 → Vec R d, e = (fun i => Sum.inl (env i)) ∧
        mv c.encoding (env 0) = mv c.encoding (env 1) := by
  change taggedRealize (sourceSystem c) (guardedCodeFormula (matrixTests c)) e ↔ _
  rw [guardedCodeFormula_semantics _ _ (matrixFiniteCodeCertificate c h)]
  simp only [taggedBehaviorSet, Set.mem_ofPred_eq, matrix_behavior_exact c h]

/-- The definable relation is the kernel of the discovered encoding on the state sort. -/
def matrixEncodingRelation (c : CertificateData R d t k o l) :
    Set (Fin 2 → TaggedCarrier (Vec R d) R) :=
  {e | ∃ env : Fin 2 → Vec R d, e = (fun i => Sum.inl (env i)) ∧
    mv c.encoding (env 0) = mv c.encoding (env 1)}

theorem matrix_encoding_definable (c : CertificateData R d t k o l) (h : Valid c) :
    letI := taggedStructure (sourceSystem c)
    (∅ : Set (TaggedCarrier (Vec R d) R)).Definable
      (observationLanguage (Fin k) (Fin o) R) (matrixEncodingRelation c) := by
  let _ := taggedStructure (sourceSystem c)
  apply Set.empty_definable_iff.mpr
  refine ⟨matrixCodeFormula c, ?_⟩
  ext e
  exact (matrixCodeFormula_semantics c h e).symm

theorem matrix_formula_on_states (c : CertificateData R d t k o l) (h : Valid c)
    (env : Fin 2 → Vec R d) :
    standardRealize (sourceSystem c) (toMathlib (codeRelationFormula (matrixTests c))) env ↔
      mv c.encoding (env 0) = mv c.encoding (env 1) :=
  (standard_finite_definition _ _ (matrixFiniteCodeCertificate c h) env).trans
    (matrix_behavior_exact c h _ _)

/-- Quantifiers range over the actual encoded image, not the free target ambient space. -/
theorem matrix_image_preserves_formulas (c : CertificateData R d t k o l) (h : Valid c)
    {n : Nat} (f : ObsFO (Fin k) (Fin o) R n) (env : Fin n → Vec R d) :
    standardRealize (sourceSystem c) (toMathlib f) env ↔
      standardRealize (imageSystem c h) (toMathlib f)
        (fun i => (imageTransport c h).encode (env i)) :=
  standard_observational_transport (imageTransport c h) (image_surjective c h) f env

/-- One genuine original-language term for each certificate observation witness. -/
def matrixObservationTerm (c : CertificateData R d t k o l) (i : Fin l) :
    (observationLanguage (Fin k) (Fin o) R).Term (Fin 1) :=
  observedTerm (c.tests i).1 (c.tests i).2 (.var 0)

def matrixLogicalCode (c : CertificateData R d t k o l)
    (env : Fin 1 → TaggedCarrier (Vec R d) R) (i : Fin l) :
    TaggedCarrier (Vec R d) R :=
  termRealize (sourceSystem c) (matrixObservationTerm c i) env

theorem matrixLogicalCode_term_definable (c : CertificateData R d t k o l) (i : Fin l) :
    letI := taggedStructure (sourceSystem c)
    (∅ : Set (TaggedCarrier (Vec R d) R)).TermDefinable
      (observationLanguage (Fin k) (Fin o) R) (fun env => matrixLogicalCode c env i) := by
  let _ := taggedStructure (sourceSystem c)
  apply Set.termDefinable_empty_iff.mpr
  exact ⟨matrixObservationTerm c i, rfl⟩

theorem matrixLogicalCode_values (c : CertificateData R d t k o l)
    (x : Vec R d) (i : Fin l) :
    matrixLogicalCode c (fun _ => Sum.inl x) i =
      Sum.inr (behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2) :=
  observedTerm_realize (sourceSystem c) (c.tests i).1 (c.tests i).2
    (.var 0) (fun _ => Sum.inl x) x rfl

/-- These term-definable coordinates code precisely the same quotient as the matrix. -/
theorem matrixLogicalCode_exact (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) :
    matrixLogicalCode c (fun _ => Sum.inl x) = matrixLogicalCode c (fun _ => Sum.inl y) ↔
      mv c.encoding x = mv c.encoding y := by
  rw [← matrix_code_encoding c h x y, matrix_code_rows]
  constructor
  · intro he
    funext i
    have hi := congrFun he i
    rw [matrixLogicalCode_values, matrixLogicalCode_values] at hi
    change dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) x =
      dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) y
    rw [wordRow_behavior, wordRow_behavior]
    exact Sum.inr.inj hi
  · intro he
    funext i
    rw [matrixLogicalCode_values, matrixLogicalCode_values]
    apply congrArg Sum.inr
    have hi := congrFun he i
    change dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) x =
      dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) y at hi
    simpa only [wordRow_behavior, sourceSystem] using hi

end Komorebi.ModelTheory.MatrixBridge
