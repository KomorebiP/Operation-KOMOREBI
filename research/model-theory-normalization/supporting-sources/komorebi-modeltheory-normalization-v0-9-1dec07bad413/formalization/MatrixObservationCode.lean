module
public import MatrixCertificates
public import FiniteObservationCode

@[expose] public section

/- A matrix certificate yields a logical test certificate. No closure or
   all-word conclusion is assumed beyond the predecessor's finite equations. -/
namespace Komorebi.ModelTheory.MatrixBridge
open Komorebi.Representation
open Komorebi.Representation.Matrix
universe u
variable {R : Type u} {d t k o l : Nat}

/-- The source language sees only the genuine tests, not the chosen matrix basis. -/
def matrixTests (c : CertificateData R d t k o l) :
    List (ObservationTest (Fin k) (Fin o)) := List.ofFn c.tests

theorem matrixTests_length (c : CertificateData R d t k o l) :
    (matrixTests c).length = l := by simp [matrixTests]

theorem matrixTests_mem (c : CertificateData R d t k o l)
    (test : ObservationTest (Fin k) (Fin o)) :
    test ∈ matrixTests c ↔ ∃ i : Fin l, c.tests i = test := by
  simp [matrixTests, List.mem_ofFn]

variable [Lean.Grind.Semiring R]

theorem matrix_code_rows (c : CertificateData R d t k o l) (x y : Vec R d) :
    CodeEqual (sourceSystem c) (matrixTests c) x y ↔
      mv (testRows c) x = mv (testRows c) y := by
  constructor
  · intro h
    funext i
    change dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) x =
      dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) y
    rw [wordRow_behavior, wordRow_behavior]
    exact h (c.tests i) ((matrixTests_mem c _).mpr ⟨i, rfl⟩)
  · intro h test ht
    obtain ⟨i, rfl⟩ := (matrixTests_mem c test).mp ht
    have hi := congrFun h i
    change dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) x =
      dot (wordRow c.actions c.observations (c.tests i).1 (c.tests i).2) y at hi
    simpa only [wordRow_behavior, sourceSystem] using hi

/-- The test tuple and the encoding may have different lengths, but the same kernel. -/
theorem matrix_code_encoding (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) :
    CodeEqual (sourceSystem c) (matrixTests c) x y ↔
      mv c.encoding x = mv c.encoding y := by
  constructor
  · intro hc
    have hr := (matrix_code_rows c x y).mp hc
    have hp : c.encoding = mm c.combinations (testRows c) :=
      funext (fun i => funext (h.2.2 i))
    rw [hp, mv_mm, mv_mm, hr]
  · intro hp test _
    exact (matrix_behavior_exact c h x y).mpr hp test.1 test.2

/-- Derive both local code obligations from the actual matrix equations. -/
theorem matrixFiniteCodeCertificate (c : CertificateData R d t k o l) (h : Valid c) :
    FiniteCodeCertificate (sourceSystem c) (matrixTests c) := {
  outputs := by
    intro x y hc j
    have hp := (matrix_code_encoding c h x y).mp hc
    exact (transport_kernel_sound (matrixTransport c h) hp) [] j
  steps := by
    intro x y hc a
    apply (matrix_code_encoding c h _ _).mpr
    apply (matrix_behavior_exact c h _ _).mp
    exact obsEq_step _ ((matrix_behavior_exact c h x y).mpr
      ((matrix_code_encoding c h x y).mp hc)) a
}

theorem matrix_tests_behavior (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) :
    CodeEqual (sourceSystem c) (matrixTests c) x y ↔ ObsEq (sourceSystem c) x y :=
  certified_code_exact _ _ (matrixFiniteCodeCertificate c h) x y

/-- A universal finite-horizon witness follows from a certificate's finite test list. -/
def matrixTestHorizon (c : CertificateData R d t k o l) : Nat :=
  ((matrixTests c).map (fun test => test.1.length)).foldl Nat.max 0

/-- Source observation terms reconstruct the selected matrix encoding exactly. -/
theorem matrix_code_reconstruct (c : CertificateData R d t k o l) (h : Valid c)
    (x : Vec R d) :
    mv c.encoding x = mv c.combinations
      (fun i => behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2) := by
  have hp : c.encoding = mm c.combinations (testRows c) :=
    funext (fun i => funext (h.2.2 i))
  rw [hp, mv_mm]
  congr 1
  funext i
  exact wordRow_behavior c.actions c.observations (c.tests i).1 (c.tests i).2 x

/-- Conversely, all source test values can be evaluated from the compressed state. -/
theorem matrix_code_from_encoding (c : CertificateData R d t k o l) (h : Valid c)
    (x : Vec R d) (i : Fin l) :
    behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2 =
      behavior (targetSystem c) (mv c.encoding x) (c.tests i).1 (c.tests i).2 :=
  matrix_all_words c h x (c.tests i).1 (c.tests i).2

end Komorebi.ModelTheory.MatrixBridge
