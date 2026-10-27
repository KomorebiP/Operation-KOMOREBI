module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.EchelonComputed08
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c096_R := ZMod (2^1)
def c096_A : Fin 1 → Mat c096_R 6 6 := ![![![1, 1, 0, 1, 1, 0], ![0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 1, 1], ![0, 1, 0, 1, 1, 1], ![1, 0, 0, 1, 1, 0], ![1, 1, 0, 0, 1, 0]]]
def c096_O : Mat c096_R 2 6 := ![![0, 0, 0, 1, 0, 0], ![0, 0, 1, 0, 0, 1]]
def c096_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c096_computed : fastPrimeDiscover 2 1 6
    (fun a => rowRight (c096_A a)) c096_O = some c096_result := by decide +kernel
theorem c096_code : FiniteCodeCertificate (linearSystem c096_A c096_O) c096_result :=
  fastPrimeDiscover_code 2 1 6 c096_A c096_O c096_result c096_computed

abbrev c097_R := ZMod (3^1)
def c097_A : Fin 2 → Mat c097_R 6 6 := ![![![1, 2, 0, 2, 1, 2], ![0, 0, 1, 2, 2, 0], ![2, 1, 2, 0, 0, 1], ![1, 2, 1, 0, 1, 1], ![2, 2, 0, 0, 2, 2], ![1, 1, 1, 2, 1, 2]], ![![1, 0, 2, 0, 2, 1], ![0, 1, 0, 1, 1, 2], ![2, 1, 2, 1, 2, 1], ![1, 1, 0, 1, 2, 0], ![0, 0, 0, 0, 1, 0], ![2, 1, 1, 2, 0, 0]]]
def c097_O : Mat c097_R 1 6 := ![![1, 2, 0, 1, 1, 0]]
def c097_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c097_computed : fastPrimeDiscover 3 1 6
    (fun a => rowRight (c097_A a)) c097_O = some c097_result := by decide +kernel
theorem c097_code : FiniteCodeCertificate (linearSystem c097_A c097_O) c097_result :=
  fastPrimeDiscover_code 3 1 6 c097_A c097_O c097_result c097_computed

abbrev c098_R := ZMod (5^1)
def c098_A : Fin 3 → Mat c098_R 6 6 := ![![![4, 1, 4, 4, 3, 3], ![4, 2, 0, 1, 3, 0], ![0, 0, 4, 4, 1, 1], ![1, 0, 4, 2, 1, 4], ![3, 2, 2, 0, 2, 0], ![0, 3, 3, 2, 3, 3]], ![![3, 2, 1, 3, 1, 2], ![0, 4, 4, 2, 0, 2], ![0, 3, 2, 2, 4, 4], ![3, 1, 3, 0, 3, 3], ![1, 4, 1, 2, 4, 4], ![4, 4, 2, 0, 4, 2]], ![![1, 2, 2, 0, 2, 0], ![3, 3, 4, 4, 2, 2], ![3, 4, 2, 1, 1, 3], ![4, 1, 2, 1, 0, 0], ![1, 3, 4, 3, 2, 0], ![0, 3, 3, 1, 0, 0]]]
def c098_O : Mat c098_R 2 6 := ![![0, 3, 1, 0, 1, 4], ![2, 3, 3, 2, 4, 1]]
def c098_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c098_computed : fastPrimeDiscover 5 1 6
    (fun a => rowRight (c098_A a)) c098_O = some c098_result := by decide +kernel
theorem c098_code : FiniteCodeCertificate (linearSystem c098_A c098_O) c098_result :=
  fastPrimeDiscover_code 5 1 6 c098_A c098_O c098_result c098_computed

abbrev c099_R := ZMod (2^2)
def c099_A : Fin 1 → Mat c099_R 6 6 := ![![![0, 2, 3, 2, 0, 2], ![3, 1, 3, 0, 0, 3], ![0, 2, 3, 0, 3, 1], ![3, 2, 2, 1, 2, 3], ![2, 2, 1, 2, 3, 2], ![2, 3, 0, 0, 2, 0]]]
def c099_O : Mat c099_R 1 6 := ![![0, 0, 0, 0, 0, 0]]
def c099_result : List (Test 1 1) := []
theorem c099_computed : fastPrimeDiscover 2 2 6
    (fun a => rowRight (c099_A a)) c099_O = some c099_result := by decide +kernel
theorem c099_code : FiniteCodeCertificate (linearSystem c099_A c099_O) c099_result :=
  fastPrimeDiscover_code 2 2 6 c099_A c099_O c099_result c099_computed

abbrev c100_R := ZMod (3^2)
def c100_A : Fin 2 → Mat c100_R 6 6 := ![![![7, 6, 7, 5, 4, 4], ![2, 4, 4, 7, 8, 1], ![2, 4, 1, 3, 2, 4], ![5, 5, 4, 4, 2, 6], ![2, 7, 2, 2, 6, 1], ![1, 0, 4, 7, 7, 3]], ![![0, 6, 2, 0, 0, 2], ![0, 3, 7, 8, 1, 3], ![5, 0, 3, 8, 0, 5], ![7, 7, 3, 1, 5, 7], ![4, 6, 7, 4, 1, 4], ![7, 7, 3, 5, 2, 0]]]
def c100_O : Mat c100_R 2 6 := ![![2, 6, 4, 0, 3, 4], ![6, 6, 3, 3, 5, 2]]
def c100_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([0,0], 0)]
theorem c100_computed : fastPrimeDiscover 3 2 6
    (fun a => rowRight (c100_A a)) c100_O = some c100_result := by decide +kernel
theorem c100_code : FiniteCodeCertificate (linearSystem c100_A c100_O) c100_result :=
  fastPrimeDiscover_code 3 2 6 c100_A c100_O c100_result c100_computed

abbrev c101_R := ZMod (5^2)
def c101_A : Fin 3 → Mat c101_R 6 6 := ![![![4, 6, 24, 15, 5, 20], ![1, 21, 10, 18, 8, 14], ![20, 23, 16, 16, 23, 5], ![7, 12, 4, 22, 23, 14], ![10, 12, 0, 8, 24, 1], ![6, 13, 7, 13, 22, 12]], ![![11, 21, 18, 18, 23, 11], ![4, 15, 14, 16, 14, 18], ![0, 16, 2, 7, 10, 17], ![7, 10, 15, 9, 1, 0], ![6, 18, 5, 2, 5, 21], ![19, 24, 2, 18, 2, 21]], ![![8, 2, 11, 10, 17, 24], ![10, 24, 16, 12, 19, 19], ![19, 10, 19, 19, 21, 13], ![14, 9, 19, 10, 15, 0], ![16, 11, 14, 13, 12, 15], ![9, 2, 14, 0, 15, 7]]]
def c101_O : Mat c101_R 1 6 := ![![17, 11, 9, 11, 15, 20]]
def c101_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c101_computed : fastPrimeDiscover 5 2 6
    (fun a => rowRight (c101_A a)) c101_O = some c101_result := by decide +kernel
theorem c101_code : FiniteCodeCertificate (linearSystem c101_A c101_O) c101_result :=
  fastPrimeDiscover_code 5 2 6 c101_A c101_O c101_result c101_computed

abbrev c102_R := ZMod (2^3)
def c102_A : Fin 1 → Mat c102_R 6 6 := ![![![4, 0, 3, 4, 6, 4], ![7, 1, 0, 7, 5, 1], ![5, 5, 5, 3, 2, 0], ![4, 6, 6, 7, 1, 7], ![4, 1, 1, 6, 0, 5], ![4, 0, 6, 4, 4, 7]]]
def c102_O : Mat c102_R 2 6 := ![![3, 5, 7, 7, 7, 2], ![4, 3, 0, 0, 2, 1]]
def c102_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c102_computed : fastPrimeDiscover 2 3 6
    (fun a => rowRight (c102_A a)) c102_O = some c102_result := by decide +kernel
theorem c102_code : FiniteCodeCertificate (linearSystem c102_A c102_O) c102_result :=
  fastPrimeDiscover_code 2 3 6 c102_A c102_O c102_result c102_computed

abbrev c103_R := ZMod (3^3)
def c103_A : Fin 2 → Mat c103_R 6 6 := ![![![20, 9, 23, 5, 1, 2], ![14, 13, 22, 19, 18, 2], ![5, 18, 25, 6, 9, 26], ![5, 13, 15, 2, 22, 8], ![11, 16, 20, 10, 20, 4], ![2, 19, 19, 26, 5, 5]], ![![9, 2, 8, 24, 19, 9], ![1, 23, 5, 26, 0, 15], ![5, 14, 12, 9, 4, 15], ![26, 10, 13, 8, 21, 18], ![17, 16, 11, 2, 12, 0], ![14, 25, 8, 6, 10, 6]]]
def c103_O : Mat c103_R 1 6 := ![![2, 14, 16, 19, 2, 3]]
def c103_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c103_computed : fastPrimeDiscover 3 3 6
    (fun a => rowRight (c103_A a)) c103_O = some c103_result := by decide +kernel
theorem c103_code : FiniteCodeCertificate (linearSystem c103_A c103_O) c103_result :=
  fastPrimeDiscover_code 3 3 6 c103_A c103_O c103_result c103_computed

abbrev c104_R := ZMod (5^3)
def c104_A : Fin 3 → Mat c104_R 6 6 := ![![![68, 99, 104, 107, 33, 11], ![97, 106, 110, 103, 17, 96], ![51, 57, 47, 103, 82, 66], ![58, 15, 85, 59, 95, 81], ![3, 67, 122, 121, 98, 120], ![91, 39, 122, 45, 6, 50]], ![![119, 124, 124, 6, 103, 71], ![82, 53, 82, 119, 82, 30], ![27, 56, 41, 104, 13, 68], ![69, 112, 12, 58, 21, 78], ![106, 79, 40, 32, 49, 55], ![17, 78, 96, 104, 68, 96]], ![![61, 117, 70, 90, 4, 119], ![112, 51, 77, 83, 59, 72], ![55, 37, 109, 105, 68, 21], ![26, 24, 80, 9, 79, 55], ![9, 52, 88, 62, 41, 55], ![124, 110, 122, 64, 60, 17]]]
def c104_O : Mat c104_R 2 6 := ![![43, 20, 70, 92, 82, 15], ![6, 1, 112, 77, 90, 28]]
def c104_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c104_computed : fastPrimeDiscover 5 3 6
    (fun a => rowRight (c104_A a)) c104_O = some c104_result := by decide +kernel
theorem c104_code : FiniteCodeCertificate (linearSystem c104_A c104_O) c104_result :=
  fastPrimeDiscover_code 5 3 6 c104_A c104_O c104_result c104_computed

abbrev c105_R := ZMod (2^4)
def c105_A : Fin 1 → Mat c105_R 6 6 := ![![![9, 9, 11, 2, 0, 9], ![9, 14, 0, 15, 7, 12], ![12, 11, 9, 0, 12, 12], ![8, 10, 3, 6, 15, 9], ![6, 12, 4, 5, 3, 9], ![4, 2, 1, 8, 0, 2]]]
def c105_O : Mat c105_R 1 6 := ![![8, 8, 8, 8, 8, 8]]
def c105_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c105_computed : fastPrimeDiscover 2 4 6
    (fun a => rowRight (c105_A a)) c105_O = some c105_result := by decide +kernel
theorem c105_code : FiniteCodeCertificate (linearSystem c105_A c105_O) c105_result :=
  fastPrimeDiscover_code 2 4 6 c105_A c105_O c105_result c105_computed

abbrev c106_R := ZMod (3^4)
def c106_A : Fin 2 → Mat c106_R 6 6 := ![![![57, 35, 22, 33, 57, 75], ![0, 10, 70, 69, 35, 58], ![77, 52, 8, 19, 62, 65], ![73, 28, 12, 12, 53, 42], ![27, 54, 39, 54, 65, 45], ![36, 45, 80, 11, 60, 55]], ![![70, 22, 13, 58, 73, 9], ![51, 22, 57, 80, 51, 44], ![16, 48, 28, 5, 30, 13], ![5, 32, 39, 39, 8, 55], ![23, 65, 32, 31, 9, 44], ![68, 1, 73, 37, 18, 19]]]
def c106_O : Mat c106_R 2 6 := ![![15, 22, 30, 60, 51, 51], ![78, 3, 10, 57, 17, 53]]
def c106_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c106_computed : fastPrimeDiscover 3 4 6
    (fun a => rowRight (c106_A a)) c106_O = some c106_result := by decide +kernel
theorem c106_code : FiniteCodeCertificate (linearSystem c106_A c106_O) c106_result :=
  fastPrimeDiscover_code 3 4 6 c106_A c106_O c106_result c106_computed

abbrev c107_R := ZMod (5^4)
def c107_A : Fin 3 → Mat c107_R 6 6 := ![![![77, 439, 412, 410, 606, 239], ![396, 89, 51, 94, 573, 290], ![340, 167, 288, 569, 315, 448], ![550, 80, 25, 398, 150, 495], ![577, 338, 287, 225, 337, 207], ![441, 308, 184, 119, 141, 111]], ![![348, 157, 144, 109, 325, 590], ![380, 464, 610, 482, 377, 38], ![545, 515, 225, 59, 505, 80], ![614, 560, 497, 438, 127, 19], ![274, 333, 100, 90, 593, 222], ![21, 434, 596, 341, 218, 16]], ![![165, 427, 489, 136, 195, 230], ![115, 173, 394, 535, 150, 342], ![194, 330, 208, 577, 582, 402], ![423, 71, 414, 177, 607, 177], ![433, 135, 182, 55, 287, 595], ![550, 498, 592, 170, 73, 69]]]
def c107_O : Mat c107_R 1 6 := ![![377, 601, 552, 440, 45, 153]]
def c107_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0), ([2,0], 0)]
theorem c107_computed : fastPrimeDiscover 5 4 6
    (fun a => rowRight (c107_A a)) c107_O = some c107_result := by decide +kernel
theorem c107_code : FiniteCodeCertificate (linearSystem c107_A c107_O) c107_result :=
  fastPrimeDiscover_code 5 4 6 c107_A c107_O c107_result c107_computed

end Komorebi.EchelonRegression.EchelonComputed08
