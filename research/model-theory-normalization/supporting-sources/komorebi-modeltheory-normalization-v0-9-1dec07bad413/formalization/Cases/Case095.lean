module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: f6872bbe73c3caa2d0b829f04fdadd782ccaac81a39c260e86ffc93c86df2314
   Canonical certificate JSON SHA256: 620a7a78ad32101b945bf01965f41c5d7f80fafc950b54e6f41414b4305d0088
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic095
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 3125 (((([[[2277, 1422, 1294, 646, 2433], [2328, 158, 2137, 1258, 220], [2566, 35, 2691, 704, 653], [1372, 1235, 1365, 1613, 1122], [3069, 2726, 2491, 985, 238]], [[1049, 2380, 2211, 396, 1852], [2244, 1796, 2669, 191, 2187], [2182, 868, 2844, 2850, 1365], [2060, 246, 2826, 889, 2211], [2322, 2013, 405, 2041, 3073]], [[1533, 460, 2443, 2423, 485], [3028, 2990, 2875, 2341, 629], [835, 1611, 561, 347, 1391], [1471, 3055, 1398, 554, 663], [600, 1904, 517, 206, 847]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 5 := fun i j => Fin.ofNat 3125 ((([[1842, 2605, 1237, 1803, 619]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 3125 (([1842, 2605, 1237, 1803, 619] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 3125 (([3118, 808, 974, 2699, 1485] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 3125 (([385, 841, 1908, 3058, 1269] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 3125 (([2609, 193, 2080, 1461, 389] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 3125 (([2987, 1925, 67, 1350, 334] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row4 row1_sound row4_local x
def data : CertificateData R 5 5 3 1 5 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[1, 1815, 1061, 1309, 2557], [0, 1, 252, 749, 1068], [0, 0, 1, 824, 871], [0, 0, 0, 1, 639], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[2879, 2564, 0, 0, 0], [1155, 2161, 2390, 1439, 3094], [3068, 1726, 762, 1077, 1705], [3088, 929, 1388, 2428, 1451], [3069, 1241, 2300, 2705, 1872]], [[1030, 1623, 48, 0, 0], [3069, 60, 367, 2496, 1806], [209, 2560, 1729, 505, 2665], [1443, 1883, 2957, 516, 417], [2322, 83, 222, 1823, 66]], [[2402, 724, 2395, 2084, 0], [2902, 999, 235, 2880, 1243], [1164, 2155, 2881, 2679, 1945], [496, 721, 1938, 2233, 1211], [600, 404, 2734, 19, 1095]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[1842, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[928, 0, 0, 0, 0], [2317, 327, 0, 0, 0], [1678, 1248, 1061, 0, 0], [2564, 2063, 2420, 1392, 0], [428, 1797, 1695, 3023, 2308]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 5 5 := fun i j => Fin.ofNat 3125 ((([[1842, 2605, 1237, 1803, 619], [3118, 808, 974, 2699, 1485], [385, 841, 1908, 3058, 1269], [2609, 193, 2080, 1461, 389], [2987, 1925, 67, 1350, 334]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.elim0 i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 3)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 3125 (([1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 3125 ((([[1, 1310, 69, 1270, 1734], [0, 1, 2873, 649, 588], [0, 0, 1, 2301, 665], [0, 0, 0, 1, 2486], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[1, 1815, 1061, 1309, 2557], [0, 1, 252, 749, 1068], [0, 0, 1, 824, 871], [0, 0, 0, 1, 639], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 5 5 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0, 0], [1310, 1, 0, 0, 0], [69, 2873, 1, 0, 0], [1270, 649, 2301, 1, 0], [1734, 588, 665, 2486, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 5) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 3) (Fin 1)) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 3) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 5) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 5, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 5) R)).Definable
      (observationLanguage (Fin 3) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 3) (Fin 1) R n) (env : Fin n → Vec R 5) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 5) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 5) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 5) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic095
