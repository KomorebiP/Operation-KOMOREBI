import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 9edbc0a62c2599b19cd2becad8a8579b73a76ba61e779f1498110421579f70de
   Canonical certificate JSON SHA256: ea3c09d43661987d98f418a47ddae722be4ead7bd52c990f32a04b07de0ace8a
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom179
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 3125 (((([[[359, 2215, 2375, 2102, 1953, 1435], [309, 1145, 1384, 530, 1804, 2344], [2729, 173, 2574, 1085, 1277, 771], [66, 1152, 2718, 2419, 244, 1813], [320, 2980, 2464, 472, 2510, 2751], [2846, 1564, 1215, 1239, 630, 579]], [[1627, 1438, 1488, 2392, 2593, 692], [2659, 410, 1711, 1555, 3021, 2288], [1281, 656, 1767, 807, 242, 664], [2354, 166, 2721, 499, 1561, 239], [2792, 1104, 1433, 1048, 3060, 253], [2670, 2348, 1762, 2224, 2157, 2234]], [[1317, 697, 2576, 644, 2240, 1708], [2485, 2313, 2357, 1837, 1253, 462], [1454, 1472, 3058, 1872, 1942, 2856], [2517, 1084, 1644, 222, 183, 3085], [1615, 562, 3105, 1042, 993, 1400], [174, 2072, 2132, 2904, 1655, 1600]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 3125 ((([[2358, 1712, 158, 579, 2077, 2544], [2315, 331, 2650, 2342, 2649, 1444]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 3125 (([2358, 1712, 158, 579, 2077, 2544] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 3125 (([2315, 331, 2650, 2342, 2649, 1444] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 3125 (([2915, 2078, 2510, 2642, 2654, 1881] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 3125 (([1752, 2556, 1450, 350, 2579, 862] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 3125 (([142, 2036, 1700, 2320, 130, 2821] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 3125 (([2090, 3090, 2606, 2802, 1277, 1185] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row5 row1_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 3125 (([2715, 610, 288, 126, 1806, 2864] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row1 (actions 1) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [1] 1 :=
  observed_row_prepend actions observations 1 [] 1 row1 row6 row1_sound row6_local x
def data : CertificateData R 6 6 3 2 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[1, 2039, 1601, 863, 694, 343], [0, 1, 260, 1307, 634, 2919], [0, 0, 1865, 1, 2242, 2039], [0, 0, 1, 0, 356, 174], [0, 0, 0, 0, 1, 2109], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[1630, 1521, 2862, 0, 0, 0], [215, 2415, 2577, 466, 2942, 2610], [710, 2513, 768, 1241, 455, 1968], [2478, 2422, 2510, 520, 2262, 923], [2534, 255, 2771, 1875, 2707, 3098], [2846, 1695, 1651, 3079, 85, 1546]], [[2919, 641, 816, 1331, 0, 0], [1255, 1485, 2146, 2883, 1726, 1724], [1463, 164, 489, 542, 2946, 933], [438, 2900, 1952, 910, 129, 460], [2572, 2478, 1832, 1259, 3105, 2697], [2670, 1968, 838, 2542, 2092, 689]], [[1874, 1206, 1286, 176, 1207, 0], [2060, 2832, 2536, 2128, 3078, 2251], [2343, 674, 2245, 64, 932, 2266], [420, 2567, 1216, 2976, 1234, 2144], [2956, 2501, 2618, 2857, 2017, 525], [174, 411, 3065, 473, 2082, 684]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[2358, 0, 0, 0, 0, 0], [2315, 1921, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([1], 1)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[2522, 0, 0, 0, 0, 0, 0], [795, 231, 0, 0, 0, 0, 0], [1110, 1027, 3056, 0, 0, 0, 0], [2567, 2687, 209, 1312, 0, 0, 0], [2875, 2915, 100, 2434, 2296, 0, 0], [1006, 2313, 1748, 2535, 2871, 0, 669]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 3125 ((([[2358, 1712, 158, 579, 2077, 2544], [2315, 331, 2650, 2342, 2649, 1444], [2915, 2078, 2510, 2642, 2654, 1881], [1752, 2556, 1450, 350, 2579, 862], [142, 2036, 1700, 2320, 130, 2821], [2090, 3090, 2606, 2802, 1277, 1185], [2715, 610, 288, 126, 1806, 2864]] : List (List Nat)).getD i.val []).getD j.val 0)
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
  change := fun i j => Fin.ofNat 3125 ((([[1, 1086, 1610, 889, 303, 3120], [0, 1, 1818, 2920, 2640, 1839], [0, 0, 0, 1, 2769, 630], [0, 0, 1, 1260, 2323, 1389], [0, 0, 0, 0, 1, 1016], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[1, 2039, 1601, 863, 694, 343], [0, 1, 260, 1307, 634, 2919], [0, 0, 1865, 1, 2242, 2039], [0, 0, 1, 0, 356, 174], [0, 0, 0, 0, 1, 2109], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0, 0, 0], [1086, 1, 0, 0, 0, 0], [414, 2865, 1, 0, 0, 0], [889, 2920, 1, 1260, 0, 0], [303, 2640, 2769, 2323, 1, 0], [3120, 1839, 630, 1389, 1016, 1], [0, 2500, 0, 2500, 625, 625]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom179
