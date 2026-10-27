module
public import MatrixLogicalFibers
public import MatrixRowWitnesses

@[expose] public section
namespace Komorebi.ModelTheory.MatrixBridge
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory.Standard
variable {R : Type} [Lean.Grind.Semiring R] {d t k o l : Nat}

/-- A finite certificate supplies a genuine distinguishing word for every pair
    of differently encoded source states. -/
theorem matrix_distinguishing_test (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) (hne : mv c.encoding x ≠ mv c.encoding y) :
    ∃ i : Fin l, behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2 ≠
      behavior (sourceSystem c) y (c.tests i).1 (c.tests i).2 := by
  classical
  by_contra hn
  apply hne
  apply (matrix_code_encoding c h x y).mp
  intro test ht
  obtain ⟨i,rfl⟩ := (matrixTests_mem c test).mp ht
  by_contra hd
  exact hn ⟨i,hd⟩

/-- The witness becomes a standard first-order observation formula, not an
    arbitrary predicate naming one of the source states. -/
theorem matrix_distinguishing_formula (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) (hne : mv c.encoding x ≠ mv c.encoding y) :
    ∃ i : Fin l, ∃ value : R,
      standardRealize (sourceSystem c)
        (toMathlib (.test (n := 1) (0,(c.tests i).1) (c.tests i).2 value)) (fun _ => x) ∧
      ¬ standardRealize (sourceSystem c)
        (toMathlib (.test (n := 1) (0,(c.tests i).1) (c.tests i).2 value)) (fun _ => y) := by
  obtain ⟨i,hi⟩ := matrix_distinguishing_test c h x y hne
  refine ⟨i,behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2,?_,?_⟩
  · rw [toMathlib_correct]
    rfl
  · rw [toMathlib_correct]
    change ¬ (behavior (sourceSystem c) y (c.tests i).1 (c.tests i).2 =
      behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2)
    exact fun he => hi he.symm

/-- Each successful growth witness is converted to a logical non-merge certificate. -/
theorem growth_formula_distinguishes (c : CertificateData R d t k o l)
    (rows deltas : Mat R l d)
    (hrows : ∀ i x, dot (rows i) x =
      behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2)
    (hgrowth : ∀ i, (∀ j, j.val < i.val → dot (rows j) (deltas i) = 0) ∧
      dot (rows i) (deltas i) ≠ 0) (i : Fin l) :
    standardRealize (sourceSystem c)
      (toMathlib (.test (n := 1) (0,(c.tests i).1) (c.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem c)
      (toMathlib (.test (n := 1) (0,(c.tests i).1) (c.tests i).2 (0 : R))) (fun _ => deltas i) := by
  simp only [toMathlib_correct, ObsFO.Sat, termObservation]
  constructor
  · rw [← hrows, dot_zero]
  · rw [← hrows]
    exact (hgrowth i).2

end Komorebi.ModelTheory.MatrixBridge
