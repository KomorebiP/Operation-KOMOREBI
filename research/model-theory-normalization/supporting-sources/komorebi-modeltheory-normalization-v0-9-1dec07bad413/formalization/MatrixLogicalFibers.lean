module
public import MatrixLogicalBridge

@[expose] public section
namespace Komorebi.ModelTheory.MatrixBridge
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory.Standard
open FirstOrder.Language
variable {R : Type} [Lean.Grind.Semiring R] {d t k o l : Nat}

/-- Query a compressed state by the original observation language. No source
    representative is chosen by this constructor. -/
def fiberSource (c : CertificateData R d t k o l) (y : Vec R t) :
    List (ObservationTest (Fin k) (Fin o)) → ObsFO (Fin k) (Fin o) R 1
  | [] => .truth
  | (w,j) :: rest => .conj (.test (0,w) j (behavior (targetSystem c) y w j))
      (fiberSource c y rest)

theorem fiberSource_quantifierRank (c : CertificateData R d t k o l) (y : Vec R t)
    (tests : List (ObservationTest (Fin k) (Fin o))) :
    (fiberSource c y tests).quantifierRank = 0 := by
  induction tests with
  | nil => rfl
  | cons test rest ih =>
    rcases test with ⟨w,j⟩
    simpa only [fiberSource, ObsFO.quantifierRank, Nat.zero_max] using ih

theorem fiberSource_semantics (c : CertificateData R d t k o l) (y : Vec R t)
    (tests : List (ObservationTest (Fin k) (Fin o))) (x : Vec R d) :
    (fiberSource c y tests).Sat (sourceSystem c) (fun _ => x) ↔
      ∀ test ∈ tests, behavior (sourceSystem c) x test.1 test.2 =
        behavior (targetSystem c) y test.1 test.2 := by
  induction tests with
  | nil => simp [fiberSource, ObsFO.Sat]
  | cons test rest ih =>
    rcases test with ⟨w,j⟩
    simp only [fiberSource, ObsFO.Sat, termObservation, ih]
    constructor
    · rintro ⟨hw,ht⟩ test hm
      rcases List.mem_cons.mp hm with he | he
      · subst test; exact hw
      · exact ht test he
    · intro ht
      exact ⟨ht (w,j) List.mem_cons_self,
        fun test hm => ht test (List.mem_cons_of_mem _ hm)⟩

theorem matrix_fiber_exact (c : CertificateData R d t k o l) (h : Valid c)
    (y : EncodedImage c) (x : Vec R d) :
    (fiberSource c y.val (matrixTests c)).Sat (sourceSystem c) (fun _ => x) ↔
      mv c.encoding x = y.val := by
  obtain ⟨v,hv⟩ := y.property
  rw [fiberSource_semantics, ← hv]
  have heq : (∀ test ∈ matrixTests c,
      behavior (sourceSystem c) x test.1 test.2 =
      behavior (targetSystem c) (mv c.encoding v) test.1 test.2) ↔
      CodeEqual (sourceSystem c) (matrixTests c) x v := by
    simp only [CodeEqual, ← matrix_all_words c h]
  exact heq.trans (matrix_code_encoding c h x v)

def matrixFiberFormula (c : CertificateData R d t k o l) (y : Vec R t) :
    (observationLanguage (Fin k) (Fin o) R).Formula (Fin 1) :=
  stateGuard (.var (.inl 0)) ⊓ toMathlib (fiberSource c y (matrixTests c))

theorem matrixFiberFormula_isQF (c : CertificateData R d t k o l) (y : Vec R t) :
    (matrixFiberFormula c y).IsQF :=
  (BoundedFormula.IsAtomic.rel _ _).isQF.inf
    (toMathlib_isQF _ (fiberSource_quantifierRank c y (matrixTests c)))

theorem matrixFiberFormula_states (c : CertificateData R d t k o l) (h : Valid c)
    (y : EncodedImage c) (x : Vec R d) :
    standardRealize (sourceSystem c) (matrixFiberFormula c y.val) (fun _ => x) ↔
      mv c.encoding x = y.val := by
  let _ := taggedStructure (sourceSystem c)
  change FirstOrder.Language.Formula.Realize
    (stateGuard (.var (.inl 0)) ⊓ toMathlib (fiberSource c y.val (matrixTests c)))
      (fun _ => Sum.inl x) ↔ _
  rw [Formula.realize_inf]
  change True ∧ standardRealize (sourceSystem c)
    (toMathlib (fiberSource c y.val (matrixTests c))) (fun _ => x) ↔ _
  rw [true_and, toMathlib_correct]
  exact matrix_fiber_exact c h y x

theorem matrixFiberFormula_nonempty (c : CertificateData R d t k o l) (h : Valid c)
    (y : EncodedImage c) :
    ∃ x, standardRealize (sourceSystem c) (matrixFiberFormula c y.val) (fun _ => x) := by
  obtain ⟨x,hx⟩ := y.property
  exact ⟨x, (matrixFiberFormula_states c h y x).mpr hx⟩

theorem matrixFiberFormula_disjoint (c : CertificateData R d t k o l) (h : Valid c)
    (y z : EncodedImage c) (hne : y ≠ z) (x : Vec R d) :
    ¬ (standardRealize (sourceSystem c) (matrixFiberFormula c y.val) (fun _ => x) ∧
       standardRealize (sourceSystem c) (matrixFiberFormula c z.val) (fun _ => x)) := by
  rintro ⟨hy,hz⟩
  apply hne
  apply Subtype.ext
  exact ((matrixFiberFormula_states c h y x).mp hy).symm.trans
    ((matrixFiberFormula_states c h z x).mp hz)

end Komorebi.ModelTheory.MatrixBridge
