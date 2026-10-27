import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: c0fd45cb20c3ab0c5c352d404eab89b6a33ef27f997faf9cf1a9158c89b99b8e
   Canonical certificate JSON SHA256: da6cbb76d165761327483e7d1a10234de0e52e8ef3e790736c028cca9c1aad0c
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom089
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 3125 (((([[[724, 1560, 885, 2546, 1128, 729], [73, 2514, 710, 2659, 160, 1800], [1038, 2447, 616, 2163, 2311, 2969], [2970, 263, 1847, 961, 745, 1890], [2447, 1128, 1684, 1877, 612, 2102], [790, 470, 1208, 114, 2390, 1720]], [[2979, 2844, 2145, 2544, 2434, 782], [2981, 1543, 154, 1441, 1023, 43], [2014, 2649, 2887, 1530, 1998, 405], [188, 1504, 1199, 381, 945, 1093], [1804, 2691, 2080, 478, 1283, 777], [2434, 940, 2908, 2156, 277, 2431]], [[2327, 1915, 1476, 2667, 62, 2263], [995, 76, 1216, 1433, 2644, 551], [2062, 772, 15, 1719, 3080, 3121], [663, 2382, 1743, 773, 2452, 1376], [959, 144, 2650, 886, 2594, 1100], [1779, 1359, 651, 244, 1473, 2482]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 3125 ((([[1423, 806, 1109, 737, 2988, 2679], [1430, 2147, 226, 542, 925, 1357]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 3125 (([1423, 806, 1109, 737, 2988, 2679] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 3125 (([1430, 2147, 226, 542, 925, 1357] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 3125 (([918, 2062, 272, 2643, 2534, 2999] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 3125 (([3048, 2077, 1752, 813, 1054, 2080] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 3125 (([1363, 266, 149, 2255, 1673, 734] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 3125 (([9, 1991, 2166, 276, 1341, 2709] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row5 row1_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 3125 (([1487, 773, 46, 2799, 219, 2783] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row2 (actions 0) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row2 row6 row2_sound row6_local x
def data : CertificateData R 6 6 3 2 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[1, 2772, 2333, 1294, 281, 48], [0, 1, 1053, 1756, 3060, 316], [0, 0, 1980, 2355, 1, 2469], [0, 0, 650, 3070, 0, 1], [0, 0, 235, 1, 0, 0], [0, 0, 1, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[2816, 3117, 1367, 0, 0, 0], [2117, 1034, 1531, 1738, 1191, 2480], [2547, 74, 2130, 1867, 2511, 3118], [2765, 2600, 2475, 25, 1199, 463], [25, 2883, 2325, 77, 2603, 2853], [1038, 111, 2223, 1357, 420, 1664]], [[751, 852, 3022, 737, 0, 0], [2610, 419, 2924, 2092, 854, 2115], [1185, 671, 2341, 1861, 2931, 1429], [1194, 2177, 2993, 1855, 1988, 2085], [1603, 2378, 2727, 538, 1761, 941], [2014, 1091, 729, 2826, 2628, 1252]], [[2656, 1735, 690, 2850, 836, 0], [1963, 2557, 556, 407, 2483, 2550], [3060, 1990, 531, 3084, 1767, 1259], [2489, 766, 244, 863, 812, 586], [858, 2301, 344, 1550, 935, 381], [2062, 533, 2053, 1235, 2528, 725]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[1423, 0, 0, 0, 0, 0], [1430, 687, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([0, 0], 0)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[112, 0, 0, 0, 0, 0, 0], [945, 373, 0, 0, 0, 0, 0], [104, 752, 1486, 0, 0, 0, 0], [80, 2430, 284, 1251, 0, 0, 0], [2838, 440, 1035, 1275, 2542, 0, 0], [374, 2968, 2906, 2015, 3092, 0, 107]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 3125 ((([[1423, 806, 1109, 737, 2988, 2679], [1430, 2147, 226, 542, 925, 1357], [918, 2062, 272, 2643, 2534, 2999], [3048, 2077, 1752, 813, 1054, 2080], [1363, 266, 149, 2255, 1673, 734], [9, 1991, 2166, 276, 1341, 2709], [1487, 773, 46, 2799, 219, 2783]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.cases (row6_sound) (fun i7 => Fin.elim0 i7) i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 3125 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 3125 ((([[1, 353, 789, 2863, 83, 2033], [0, 1, 65, 1699, 1114, 982], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 2890], [0, 0, 1, 656, 2475, 2495], [0, 0, 0, 1, 55, 2050]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[1, 2772, 2333, 1294, 281, 48], [0, 1, 1053, 1756, 3060, 316], [0, 0, 1980, 2355, 1, 2469], [0, 0, 650, 3070, 0, 1], [0, 0, 235, 1, 0, 0], [0, 0, 1, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0, 0, 0], [353, 1, 0, 0, 0, 0], [958, 2072, 1, 0, 0, 0], [1993, 1419, 0, 1, 770, 0], [2788, 272, 1, 0, 2870, 2475], [2033, 982, 1, 2890, 2495, 2050], [1875, 1250, 625, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom089
