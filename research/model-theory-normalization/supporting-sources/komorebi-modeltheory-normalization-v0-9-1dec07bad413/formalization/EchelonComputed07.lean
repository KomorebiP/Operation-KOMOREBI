module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.EchelonComputed07
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c084_R := ZMod (2^2)
def c084_A : Fin 1 → Mat c084_R 5 5 := ![![![0, 1, 0, 2, 0], ![2, 1, 1, 3, 3], ![2, 0, 1, 2, 1], ![0, 2, 1, 2, 2], ![0, 0, 0, 0, 3]]]
def c084_O : Mat c084_R 2 5 := ![![0, 2, 0, 0, 2], ![0, 0, 0, 2, 0]]
def c084_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c084_computed : fastPrimeDiscover 2 2 5
    (fun a => rowRight (c084_A a)) c084_O = some c084_result := by decide +kernel
theorem c084_code : FiniteCodeCertificate (linearSystem c084_A c084_O) c084_result :=
  fastPrimeDiscover_code 2 2 5 c084_A c084_O c084_result c084_computed

abbrev c085_R := ZMod (3^2)
def c085_A : Fin 2 → Mat c085_R 5 5 := ![![![1, 5, 0, 8, 8], ![8, 0, 6, 3, 1], ![6, 6, 4, 4, 3], ![4, 5, 3, 8, 7], ![2, 3, 8, 6, 6]], ![![5, 6, 5, 0, 6], ![4, 3, 2, 2, 3], ![2, 7, 2, 5, 5], ![1, 4, 4, 7, 2], ![8, 7, 7, 8, 2]]]
def c085_O : Mat c085_R 1 5 := ![![1, 0, 2, 2, 5]]
def c085_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c085_computed : fastPrimeDiscover 3 2 5
    (fun a => rowRight (c085_A a)) c085_O = some c085_result := by decide +kernel
theorem c085_code : FiniteCodeCertificate (linearSystem c085_A c085_O) c085_result :=
  fastPrimeDiscover_code 3 2 5 c085_A c085_O c085_result c085_computed

abbrev c086_R := ZMod (5^2)
def c086_A : Fin 3 → Mat c086_R 5 5 := ![![![5, 8, 19, 5, 3], ![22, 0, 0, 17, 0], ![15, 1, 16, 11, 14], ![13, 7, 4, 19, 1], ![0, 3, 8, 13, 2]], ![![12, 3, 11, 4, 10], ![8, 19, 3, 22, 14], ![4, 8, 3, 8, 21], ![2, 14, 19, 9, 1], ![24, 18, 7, 19, 0]], ![![23, 21, 23, 0, 5], ![21, 23, 17, 13, 18], ![13, 23, 9, 9, 11], ![10, 1, 15, 8, 18], ![9, 17, 15, 24, 15]]]
def c086_O : Mat c086_R 2 5 := ![![0, 0, 0, 0, 0], ![0, 0, 0, 0, 0]]
def c086_result : List (Test 3 2) := []
theorem c086_computed : fastPrimeDiscover 5 2 5
    (fun a => rowRight (c086_A a)) c086_O = some c086_result := by decide +kernel
theorem c086_code : FiniteCodeCertificate (linearSystem c086_A c086_O) c086_result :=
  fastPrimeDiscover_code 5 2 5 c086_A c086_O c086_result c086_computed

abbrev c087_R := ZMod (2^3)
def c087_A : Fin 1 → Mat c087_R 5 5 := ![![![6, 0, 4, 6, 1], ![7, 3, 7, 1, 7], ![5, 4, 1, 0, 4], ![1, 0, 1, 7, 7], ![1, 1, 2, 5, 0]]]
def c087_O : Mat c087_R 1 5 := ![![4, 1, 6, 7, 2]]
def c087_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c087_computed : fastPrimeDiscover 2 3 5
    (fun a => rowRight (c087_A a)) c087_O = some c087_result := by decide +kernel
theorem c087_code : FiniteCodeCertificate (linearSystem c087_A c087_O) c087_result :=
  fastPrimeDiscover_code 2 3 5 c087_A c087_O c087_result c087_computed

abbrev c088_R := ZMod (3^3)
def c088_A : Fin 2 → Mat c088_R 5 5 := ![![![1, 18, 5, 18, 4], ![16, 24, 12, 10, 0], ![19, 8, 7, 20, 23], ![4, 9, 5, 1, 12], ![22, 23, 1, 16, 6]], ![![21, 13, 22, 10, 7], ![20, 22, 8, 19, 4], ![14, 9, 20, 8, 23], ![2, 18, 7, 1, 5], ![19, 12, 4, 11, 12]]]
def c088_O : Mat c088_R 2 5 := ![![6, 13, 22, 8, 3], ![12, 5, 9, 16, 22]]
def c088_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c088_computed : fastPrimeDiscover 3 3 5
    (fun a => rowRight (c088_A a)) c088_O = some c088_result := by decide +kernel
theorem c088_code : FiniteCodeCertificate (linearSystem c088_A c088_O) c088_result :=
  fastPrimeDiscover_code 3 3 5 c088_A c088_O c088_result c088_computed

abbrev c089_R := ZMod (5^3)
def c089_A : Fin 3 → Mat c089_R 5 5 := ![![![101, 120, 94, 14, 114], ![41, 12, 12, 48, 97], ![78, 55, 52, 92, 34], ![46, 22, 31, 12, 90], ![44, 66, 51, 53, 121]], ![![75, 20, 44, 43, 11], ![117, 80, 29, 45, 35], ![47, 47, 123, 120, 69], ![58, 34, 51, 24, 39], ![48, 87, 116, 59, 21]], ![![19, 66, 59, 54, 73], ![102, 57, 76, 101, 66], ![106, 91, 0, 94, 117], ![89, 66, 65, 97, 51], ![74, 50, 101, 48, 72]]]
def c089_O : Mat c089_R 1 5 := ![![37, 85, 115, 110, 96]]
def c089_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c089_computed : fastPrimeDiscover 5 3 5
    (fun a => rowRight (c089_A a)) c089_O = some c089_result := by decide +kernel
theorem c089_code : FiniteCodeCertificate (linearSystem c089_A c089_O) c089_result :=
  fastPrimeDiscover_code 5 3 5 c089_A c089_O c089_result c089_computed

abbrev c090_R := ZMod (2^4)
def c090_A : Fin 1 → Mat c090_R 5 5 := ![![![12, 15, 0, 3, 11], ![12, 0, 6, 13, 1], ![9, 8, 15, 8, 10], ![2, 14, 13, 15, 3], ![14, 3, 0, 5, 13]]]
def c090_O : Mat c090_R 2 5 := ![![7, 3, 15, 10, 11], ![11, 8, 5, 10, 3]]
def c090_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c090_computed : fastPrimeDiscover 2 4 5
    (fun a => rowRight (c090_A a)) c090_O = some c090_result := by decide +kernel
theorem c090_code : FiniteCodeCertificate (linearSystem c090_A c090_O) c090_result :=
  fastPrimeDiscover_code 2 4 5 c090_A c090_O c090_result c090_computed

abbrev c091_R := ZMod (3^4)
def c091_A : Fin 2 → Mat c091_R 5 5 := ![![![9, 43, 18, 8, 34], ![48, 74, 48, 28, 54], ![26, 79, 40, 1, 35], ![17, 17, 42, 77, 64], ![26, 14, 35, 17, 17]], ![![22, 79, 68, 63, 14], ![69, 76, 64, 36, 56], ![69, 12, 14, 69, 20], ![0, 56, 30, 63, 0], ![21, 4, 75, 34, 71]]]
def c091_O : Mat c091_R 1 5 := ![![0, 54, 54, 27, 27]]
def c091_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c091_computed : fastPrimeDiscover 3 4 5
    (fun a => rowRight (c091_A a)) c091_O = some c091_result := by decide +kernel
theorem c091_code : FiniteCodeCertificate (linearSystem c091_A c091_O) c091_result :=
  fastPrimeDiscover_code 3 4 5 c091_A c091_O c091_result c091_computed

abbrev c092_R := ZMod (5^4)
def c092_A : Fin 3 → Mat c092_R 5 5 := ![![![229, 287, 50, 317, 544], ![192, 326, 502, 259, 466], ![239, 6, 59, 596, 134], ![283, 460, 37, 549, 29], ![545, 154, 354, 501, 561]], ![![228, 153, 350, 589, 583], ![308, 252, 467, 249, 140], ![445, 375, 621, 543, 346], ![512, 323, 353, 27, 602], ![400, 76, 346, 528, 58]], ![![82, 101, 106, 233, 309], ![387, 35, 357, 162, 203], ![619, 6, 428, 317, 154], ![236, 163, 175, 392, 141], ![253, 283, 491, 528, 194]]]
def c092_O : Mat c092_R 2 5 := ![![467, 203, 247, 46, 165], ![354, 10, 202, 138, 248]]
def c092_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c092_computed : fastPrimeDiscover 5 4 5
    (fun a => rowRight (c092_A a)) c092_O = some c092_result := by decide +kernel
theorem c092_code : FiniteCodeCertificate (linearSystem c092_A c092_O) c092_result :=
  fastPrimeDiscover_code 5 4 5 c092_A c092_O c092_result c092_computed

abbrev c093_R := ZMod (2^5)
def c093_A : Fin 1 → Mat c093_R 5 5 := ![![![10, 4, 17, 24, 20], ![21, 6, 5, 17, 26], ![18, 25, 23, 19, 26], ![16, 4, 3, 11, 6], ![28, 30, 21, 1, 17]]]
def c093_O : Mat c093_R 1 5 := ![![22, 7, 30, 3, 2]]
def c093_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c093_computed : fastPrimeDiscover 2 5 5
    (fun a => rowRight (c093_A a)) c093_O = some c093_result := by decide +kernel
theorem c093_code : FiniteCodeCertificate (linearSystem c093_A c093_O) c093_result :=
  fastPrimeDiscover_code 2 5 5 c093_A c093_O c093_result c093_computed

abbrev c094_R := ZMod (3^5)
def c094_A : Fin 2 → Mat c094_R 5 5 := ![![![215, 94, 41, 186, 191], ![193, 37, 116, 120, 48], ![59, 178, 156, 167, 0], ![226, 238, 110, 50, 146], ![215, 156, 204, 183, 44]], ![![86, 90, 135, 221, 87], ![79, 36, 108, 37, 108], ![235, 76, 133, 65, 53], ![71, 37, 8, 16, 13], ![108, 177, 123, 40, 155]]]
def c094_O : Mat c094_R 2 5 := ![![164, 193, 21, 41, 103], ![56, 46, 141, 64, 91]]
def c094_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c094_computed : fastPrimeDiscover 3 5 5
    (fun a => rowRight (c094_A a)) c094_O = some c094_result := by decide +kernel
theorem c094_code : FiniteCodeCertificate (linearSystem c094_A c094_O) c094_result :=
  fastPrimeDiscover_code 3 5 5 c094_A c094_O c094_result c094_computed

abbrev c095_R := ZMod (5^5)
def c095_A : Fin 3 → Mat c095_R 5 5 := ![![![2277, 1422, 1294, 646, 2433], ![2328, 158, 2137, 1258, 220], ![2566, 35, 2691, 704, 653], ![1372, 1235, 1365, 1613, 1122], ![3069, 2726, 2491, 985, 238]], ![![1049, 2380, 2211, 396, 1852], ![2244, 1796, 2669, 191, 2187], ![2182, 868, 2844, 2850, 1365], ![2060, 246, 2826, 889, 2211], ![2322, 2013, 405, 2041, 3073]], ![![1533, 460, 2443, 2423, 485], ![3028, 2990, 2875, 2341, 629], ![835, 1611, 561, 347, 1391], ![1471, 3055, 1398, 554, 663], ![600, 1904, 517, 206, 847]]]
def c095_O : Mat c095_R 1 5 := ![![1842, 2605, 1237, 1803, 619]]
def c095_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c095_computed : fastPrimeDiscover 5 5 5
    (fun a => rowRight (c095_A a)) c095_O = some c095_result := by decide +kernel
theorem c095_code : FiniteCodeCertificate (linearSystem c095_A c095_O) c095_result :=
  fastPrimeDiscover_code 5 5 5 c095_A c095_O c095_result c095_computed

end Komorebi.EchelonRegression.EchelonComputed07
