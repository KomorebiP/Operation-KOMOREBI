module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: c39e9dc80a33c2be9b855a5e5cc0bed48220ed9d6270983a981695930bafc30a
   Canonical certificate JSON SHA256: ccb17a5989e26f779d9b386835629e62759b3bfbe7cc930475e90679a83fec0c
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic193
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 27
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 27 (((([[[1, 2, 20, 21, 24, 15], [11, 4, 18, 5, 19, 5], [15, 26, 25, 5, 7, 14], [19, 12, 8, 3, 24, 21], [20, 21, 16, 11, 13, 20], [11, 16, 19, 9, 23, 5]], [[2, 24, 11, 22, 16, 22], [13, 15, 14, 21, 1, 1], [21, 8, 17, 12, 23, 15], [16, 22, 25, 25, 4, 6], [4, 12, 11, 24, 5, 21], [12, 13, 21, 5, 6, 16]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 27 ((([[18, 4, 10, 3, 13, 23]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 27 (([18, 4, 10, 3, 13, 23] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 27 (([26, 17, 1, 24, 25, 4] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 27 (([26, 13, 18, 22, 8, 21] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 27 (([13, 24, 7, 20, 3, 1] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row3 row1_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 27 (([16, 12, 15, 1, 26, 14] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 1) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 27 (([20, 7, 17, 18, 17, 6] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row2 (actions 1) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [1, 1] 0 :=
  observed_row_prepend actions observations 1 [1] 0 row2 row5 row2_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 27 (([23, 2, 14, 17, 9, 7] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row3 (actions 0) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0] 0 row3 row6 row3_sound row6_local x
def data : CertificateData R 6 6 2 1 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 27 ((([[18, 1, 16, 21, 10, 26], [1, 0, 19, 9, 1, 6], [0, 0, 9, 1, 5, 13], [0, 0, 6, 0, 1, 11], [0, 0, 1, 0, 0, 24], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 27 (((([[[11, 11, 0, 0, 0, 0], [19, 12, 25, 8, 0, 0], [19, 1, 1, 12, 21, 0], [2, 6, 17, 8, 1, 8], [5, 0, 8, 10, 26, 3], [16, 20, 6, 2, 19, 20]], [[10, 2, 7, 0, 0, 0], [5, 18, 19, 16, 7, 0], [26, 21, 15, 12, 24, 18], [14, 10, 10, 9, 2, 18], [23, 3, 0, 15, 6, 14], [13, 21, 2, 7, 2, 22]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 27 ((([[4, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([1, 0], 0), ([1, 1], 0), ([0, 0, 0], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 27 ((([[7, 0, 0, 0, 0, 0, 0], [20, 8, 0, 0, 0, 0, 0], [19, 17, 1, 0, 0, 0, 0], [2, 15, 7, 1, 0, 0, 0], [7, 7, 15, 17, 5, 0, 0], [14, 21, 15, 3, 17, 0, 17]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 27 ((([[18, 4, 10, 3, 13, 23], [26, 17, 1, 24, 25, 4], [26, 13, 18, 22, 8, 21], [13, 24, 7, 20, 3, 1], [16, 12, 15, 1, 26, 14], [20, 7, 17, 18, 17, 6], [23, 2, 14, 17, 9, 7]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.cases (row6_sound) (fun i7 => Fin.elim0 i7) i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 27 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 27 ((([[0, 1, 18, 17, 14, 20], [1, 9, 6, 5, 26, 0], [0, 0, 0, 0, 1, 3], [0, 0, 1, 22, 21, 24], [0, 0, 0, 1, 21, 25], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 27 ((([[18, 1, 16, 21, 10, 26], [1, 0, 19, 9, 1, 6], [0, 0, 9, 1, 5, 13], [0, 0, 6, 0, 1, 11], [0, 0, 1, 0, 0, 24], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 27 ((([[1, 0, 0, 0, 0, 0], [1, 9, 0, 0, 0, 0], [8, 2, 1, 0, 0, 0], [8, 2, 1, 18, 0, 0], [14, 26, 1, 21, 21, 0], [20, 0, 3, 24, 25, 1], [6, 0, 9, 18, 21, 3]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 2) (Fin 1)) := [([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([1, 0], 0), ([1, 1], 0), ([0, 0, 0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 2) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 6) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 6, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 6) R)).Definable
      (observationLanguage (Fin 2) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 2) (Fin 1) R n) (env : Fin n → Vec R 6) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 6) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 6) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 7) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic193
