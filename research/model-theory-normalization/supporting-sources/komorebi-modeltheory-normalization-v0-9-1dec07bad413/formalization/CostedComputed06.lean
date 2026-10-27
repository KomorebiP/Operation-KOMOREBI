module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch06
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev c072_R := ZMod (2^3)
def c072_A : Fin 1 → Mat c072_R 4 4 := ![![![1, 7, 6, 4], ![7, 6, 3, 3], ![3, 4, 1, 7], ![7, 1, 1, 4]]]
def c072_O : Mat c072_R 2 4 := ![![6, 3, 3, 5], ![4, 3, 3, 1]]
def c072_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0, 0], 0)]
theorem c072_computed : discoverEval 2 3 4 c072_A c072_O =
    (some c072_result, 1208) := by decide +kernel
theorem c072_all_words : FiniteCodeCertificate (linearSystem c072_A c072_O) c072_result :=
  discoverEval_code 2 3 4 c072_A c072_O c072_result
    (congrArg Prod.fst c072_computed)
abbrev c073_R := ZMod (3^3)
def c073_A : Fin 2 → Mat c073_R 4 4 := ![![![22, 22, 13, 24], ![22, 0, 21, 6], ![19, 23, 2, 0], ![14, 5, 13, 14]], ![![26, 14, 3, 3], ![12, 8, 16, 16], ![9, 15, 18, 6], ![19, 20, 8, 4]]]
def c073_O : Mat c073_R 1 4 := ![![0, 0, 0, 0]]
def c073_result : List (Test 2 1) := []
theorem c073_computed : discoverEval 3 3 4 c073_A c073_O =
    (some c073_result, 49) := by decide +kernel
theorem c073_all_words : FiniteCodeCertificate (linearSystem c073_A c073_O) c073_result :=
  discoverEval_code 3 3 4 c073_A c073_O c073_result
    (congrArg Prod.fst c073_computed)
abbrev c074_R := ZMod (5^3)
def c074_A : Fin 3 → Mat c074_R 4 4 := ![![![122, 32, 47, 33], ![15, 16, 4, 91], ![81, 96, 28, 33], ![0, 107, 7, 111]], ![![19, 62, 92, 116], ![56, 67, 116, 89], ![89, 50, 99, 79], ![12, 78, 75, 119]], ![![48, 106, 46, 6], ![56, 113, 122, 95], ![40, 16, 104, 121], ![21, 82, 16, 58]]]
def c074_O : Mat c074_R 2 4 := ![![104, 94, 58, 17], ![44, 98, 58, 7]]
def c074_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c074_computed : discoverEval 5 3 4 c074_A c074_O =
    (some c074_result, 1691) := by decide +kernel
theorem c074_all_words : FiniteCodeCertificate (linearSystem c074_A c074_O) c074_result :=
  discoverEval_code 5 3 4 c074_A c074_O c074_result
    (congrArg Prod.fst c074_computed)
abbrev c075_R := ZMod (2^4)
def c075_A : Fin 1 → Mat c075_R 4 4 := ![![![15, 1, 15, 6], ![8, 4, 6, 15], ![4, 14, 7, 12], ![4, 10, 11, 3]]]
def c075_O : Mat c075_R 1 4 := ![![3, 14, 6, 12]]
def c075_result : List (Test 1 1) := [([], 0), ([0], 0), ([0, 0], 0), ([0, 0, 0], 0)]
theorem c075_computed : discoverEval 2 4 4 c075_A c075_O =
    (some c075_result, 1116) := by decide +kernel
theorem c075_all_words : FiniteCodeCertificate (linearSystem c075_A c075_O) c075_result :=
  discoverEval_code 2 4 4 c075_A c075_O c075_result
    (congrArg Prod.fst c075_computed)
abbrev c076_R := ZMod (3^4)
def c076_A : Fin 2 → Mat c076_R 4 4 := ![![![7, 73, 80, 13], ![77, 47, 72, 37], ![17, 80, 62, 14], ![8, 16, 46, 27]], ![![18, 10, 27, 0], ![28, 62, 19, 15], ![73, 35, 57, 75], ![80, 16, 50, 68]]]
def c076_O : Mat c076_R 2 4 := ![![18, 76, 79, 0], ![56, 22, 38, 40]]
def c076_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c076_computed : discoverEval 3 4 4 c076_A c076_O =
    (some c076_result, 1358) := by decide +kernel
theorem c076_all_words : FiniteCodeCertificate (linearSystem c076_A c076_O) c076_result :=
  discoverEval_code 3 4 4 c076_A c076_O c076_result
    (congrArg Prod.fst c076_computed)
abbrev c077_R := ZMod (5^4)
def c077_A : Fin 3 → Mat c077_R 4 4 := ![![![299, 527, 250, 441], ![451, 406, 318, 302], ![234, 59, 177, 312], ![469, 250, 252, 243]], ![![395, 164, 160, 582], ![136, 189, 328, 150], ![406, 53, 261, 547], ![64, 432, 561, 139]], ![![531, 303, 385, 393], ![417, 43, 51, 304], ![74, 386, 27, 527], ![43, 437, 313, 578]]]
def c077_O : Mat c077_R 1 4 := ![![375, 0, 250, 250]]
def c077_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c077_computed : discoverEval 5 4 4 c077_A c077_O =
    (some c077_result, 1602) := by decide +kernel
theorem c077_all_words : FiniteCodeCertificate (linearSystem c077_A c077_O) c077_result :=
  discoverEval_code 5 4 4 c077_A c077_O c077_result
    (congrArg Prod.fst c077_computed)
abbrev c078_R := ZMod (2^5)
def c078_A : Fin 1 → Mat c078_R 4 4 := ![![![18, 0, 1, 27], ![10, 31, 20, 10], ![16, 28, 15, 20], ![25, 21, 30, 23]]]
def c078_O : Mat c078_R 2 4 := ![![23, 1, 19, 28], ![7, 25, 16, 5]]
def c078_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c078_computed : discoverEval 2 5 4 c078_A c078_O =
    (some c078_result, 1052) := by decide +kernel
theorem c078_all_words : FiniteCodeCertificate (linearSystem c078_A c078_O) c078_result :=
  discoverEval_code 2 5 4 c078_A c078_O c078_result
    (congrArg Prod.fst c078_computed)
abbrev c079_R := ZMod (3^5)
def c079_A : Fin 2 → Mat c079_R 4 4 := ![![![96, 129, 204, 234], ![194, 196, 159, 228], ![178, 201, 118, 143], ![12, 26, 131, 234]], ![![66, 22, 62, 139], ![217, 167, 237, 211], ![120, 101, 225, 199], ![203, 203, 6, 98]]]
def c079_O : Mat c079_R 1 4 := ![![206, 231, 30, 207]]
def c079_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([0, 1], 0), ([1, 1], 0)]
theorem c079_computed : discoverEval 3 5 4 c079_A c079_O =
    (some c079_result, 2315) := by decide +kernel
theorem c079_all_words : FiniteCodeCertificate (linearSystem c079_A c079_O) c079_result :=
  discoverEval_code 3 5 4 c079_A c079_O c079_result
    (congrArg Prod.fst c079_computed)
abbrev c080_R := ZMod (5^5)
def c080_A : Fin 3 → Mat c080_R 4 4 := ![![![2781, 4, 2809, 2360], ![2840, 1576, 1793, 2417], ![2471, 666, 20, 859], ![1063, 1901, 1256, 2242]], ![![401, 2351, 497, 2498], ![246, 1266, 2326, 221], ![1341, 125, 2490, 2472], ![1753, 2328, 2560, 2227]], ![![906, 3001, 682, 563], ![11, 1251, 1314, 1325], ![1536, 2787, 1181, 2031], ![1688, 1888, 1751, 619]]]
def c080_O : Mat c080_R 2 4 := ![![34, 872, 752, 1288], ![2123, 3020, 2824, 1286]]
def c080_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c080_computed : discoverEval 5 5 4 c080_A c080_O =
    (some c080_result, 1747) := by decide +kernel
theorem c080_all_words : FiniteCodeCertificate (linearSystem c080_A c080_O) c080_result :=
  discoverEval_code 5 5 4 c080_A c080_O c080_result
    (congrArg Prod.fst c080_computed)
abbrev c081_R := ZMod (2^1)
def c081_A : Fin 1 → Mat c081_R 5 5 := ![![![1, 0, 0, 0, 0], ![1, 0, 1, 1, 1], ![1, 1, 1, 0, 0], ![1, 1, 1, 1, 1], ![1, 1, 1, 1, 0]]]
def c081_O : Mat c081_R 1 5 := ![![1, 1, 1, 1, 1]]
def c081_result : List (Test 1 1) := [([], 0), ([0], 0), ([0, 0], 0)]
theorem c081_computed : discoverEval 2 1 5 c081_A c081_O =
    (some c081_result, 987) := by decide +kernel
theorem c081_all_words : FiniteCodeCertificate (linearSystem c081_A c081_O) c081_result :=
  discoverEval_code 2 1 5 c081_A c081_O c081_result
    (congrArg Prod.fst c081_computed)
abbrev c082_R := ZMod (3^1)
def c082_A : Fin 2 → Mat c082_R 5 5 := ![![![2, 2, 1, 0, 1], ![1, 2, 2, 2, 2], ![2, 2, 2, 0, 2], ![1, 0, 1, 1, 0], ![0, 2, 2, 2, 1]], ![![0, 0, 2, 2, 2], ![1, 1, 2, 1, 0], ![1, 2, 0, 0, 1], ![0, 1, 2, 0, 0], ![1, 2, 1, 1, 0]]]
def c082_O : Mat c082_R 2 5 := ![![1, 2, 2, 1, 2], ![0, 2, 0, 2, 2]]
def c082_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c082_computed : discoverEval 3 1 5 c082_A c082_O =
    (some c082_result, 2277) := by decide +kernel
theorem c082_all_words : FiniteCodeCertificate (linearSystem c082_A c082_O) c082_result :=
  discoverEval_code 3 1 5 c082_A c082_O c082_result
    (congrArg Prod.fst c082_computed)
abbrev c083_R := ZMod (5^1)
def c083_A : Fin 3 → Mat c083_R 5 5 := ![![![0, 1, 2, 0, 4], ![1, 4, 2, 1, 3], ![4, 4, 4, 2, 1], ![4, 4, 1, 1, 2], ![4, 1, 4, 0, 3]], ![![0, 2, 0, 3, 0], ![3, 0, 0, 3, 0], ![2, 3, 2, 4, 0], ![4, 3, 1, 2, 1], ![1, 0, 0, 1, 3]], ![![4, 1, 3, 2, 2], ![3, 4, 0, 0, 4], ![2, 4, 1, 1, 4], ![3, 4, 1, 1, 2], ![0, 0, 0, 1, 2]]]
def c083_O : Mat c083_R 1 5 := ![![3, 4, 0, 3, 1]]
def c083_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0)]
theorem c083_computed : discoverEval 5 1 5 c083_A c083_O =
    (some c083_result, 3169) := by decide +kernel
theorem c083_all_words : FiniteCodeCertificate (linearSystem c083_A c083_O) c083_result :=
  discoverEval_code 5 1 5 c083_A c083_O c083_result
    (congrArg Prod.fst c083_computed)
end Komorebi.CostedRegression.Batch06
