import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 4394863ab5e1501fa96bc212d2efb1d0c1a1aa91c6c063f9b6d086889aa628bd
   Canonical certificate JSON SHA256: c95557a0c6418a001a83a40273e765183c79a2e3ae331ebe8585834c6b208e64
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom149
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 3125 (((([[[422, 1382, 2161, 2712], [1903, 1948, 1425, 397], [1316, 489, 2493, 1136], [2740, 1710, 724, 569]], [[2544, 761, 2548, 1006], [700, 2335, 243, 1972], [2007, 2783, 2393, 2029], [1475, 435, 1958, 547]], [[1602, 2746, 2378, 2127], [1559, 1191, 150, 2970], [3057, 2550, 2597, 662], [1123, 1514, 409, 2522]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 4 := fun i j => Fin.ofNat 3125 ((([[1426, 1137, 565, 2015], [3043, 3060, 2509, 1388]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 3125 (([1426, 1137, 565, 2015] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 3125 (([3043, 3060, 2509, 1388] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 3125 (([1998, 1293, 466, 826] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 3125 (([1599, 1501, 904, 310] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def data : CertificateData R 4 4 3 2 4 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[1, 1537, 1690, 2515], [0, 1, 481, 1472], [0, 0, 1, 2203], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[2973, 3017, 869, 0], [2554, 654, 1077, 752], [36, 2912, 1578, 1305], [2740, 2830, 2644, 227]], [[1774, 938, 1591, 1866], [2892, 1899, 1303, 138], [1432, 729, 1388, 2863], [1475, 2110, 548, 2758]], [[960, 3, 1650, 2986], [32, 915, 910, 1686], [2026, 2055, 604, 2541], [1123, 463, 1711, 2308]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[1426, 0, 0, 0], [3043, 969, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[1076, 0, 0, 0], [678, 129, 0, 0], [704, 2803, 404, 0], [1928, 3050, 446, 436]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 4 4 := fun i j => Fin.ofNat 3125 ((([[1426, 1137, 565, 2015], [3043, 3060, 2509, 1388], [1998, 1293, 466, 826], [1599, 1501, 904, 310]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.elim0 i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 4) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 4) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 4 4 where
  width := by decide
  weights := fun i => Fin.ofNat 3125 (([1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 3125 ((([[1, 1588, 107, 2353], [0, 1, 2644, 1921], [0, 0, 1, 922], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[1, 1537, 1690, 2515], [0, 1, 481, 1472], [0, 0, 1, 2203], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 4 4 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0], [1588, 1, 0, 0], [107, 2644, 1, 0], [2353, 1921, 922, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 4) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom149
