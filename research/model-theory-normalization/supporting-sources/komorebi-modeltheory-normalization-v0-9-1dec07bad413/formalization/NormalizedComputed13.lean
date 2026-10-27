module
public import NormalizedDiscovery
@[expose] public section
namespace Komorebi.NormalizedRegression.NormalizedComputed13
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c156_R := ZMod (2^1)
def c156_A : Fin 1 → Mat c156_R 4 4 := ![![![0, 1, 1, 0], ![1, 0, 1, 1], ![0, 1, 1, 1], ![1, 0, 1, 0]]]
def c156_O : Mat c156_R 2 4 := ![![1, 1, 1, 1], ![0, 1, 0, 1]]
def c156_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 1)]
theorem c156_computed : normalizedPrimeDiscover 2 1 4
    (fun a => rowRight (c156_A a)) c156_O = some c156_result := by decide +kernel
theorem c156_code : FiniteCodeCertificate (linearSystem c156_A c156_O) c156_result :=
  normalizedPrimeDiscover_code 2 1 4 c156_A c156_O c156_result c156_computed

abbrev c157_R := ZMod (3^1)
def c157_A : Fin 2 → Mat c157_R 4 4 := ![![![1, 1, 0, 0], ![1, 0, 2, 0], ![1, 0, 0, 2], ![2, 1, 1, 0]], ![![2, 2, 0, 1], ![1, 0, 0, 1], ![1, 1, 2, 1], ![2, 0, 2, 1]]]
def c157_O : Mat c157_R 1 4 := ![![0, 1, 0, 1]]
def c157_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c157_computed : normalizedPrimeDiscover 3 1 4
    (fun a => rowRight (c157_A a)) c157_O = some c157_result := by decide +kernel
theorem c157_code : FiniteCodeCertificate (linearSystem c157_A c157_O) c157_result :=
  normalizedPrimeDiscover_code 3 1 4 c157_A c157_O c157_result c157_computed

abbrev c158_R := ZMod (5^1)
def c158_A : Fin 3 → Mat c158_R 4 4 := ![![![1, 2, 3, 3], ![3, 0, 4, 4], ![0, 0, 2, 3], ![0, 4, 0, 1]], ![![0, 0, 3, 0], ![3, 4, 1, 3], ![4, 3, 4, 4], ![3, 1, 3, 0]], ![![1, 0, 3, 0], ![4, 2, 1, 2], ![3, 1, 0, 2], ![1, 3, 1, 4]]]
def c158_O : Mat c158_R 2 4 := ![![1, 2, 0, 3], ![0, 0, 0, 0]]
def c158_result : List (Test 3 2) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c158_computed : normalizedPrimeDiscover 5 1 4
    (fun a => rowRight (c158_A a)) c158_O = some c158_result := by decide +kernel
theorem c158_code : FiniteCodeCertificate (linearSystem c158_A c158_O) c158_result :=
  normalizedPrimeDiscover_code 5 1 4 c158_A c158_O c158_result c158_computed

abbrev c159_R := ZMod (2^2)
def c159_A : Fin 1 → Mat c159_R 4 4 := ![![![1, 0, 0, 1], ![2, 1, 3, 1], ![3, 3, 2, 3], ![3, 3, 0, 2]]]
def c159_O : Mat c159_R 1 4 := ![![3, 0, 1, 3]]
def c159_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem c159_computed : normalizedPrimeDiscover 2 2 4
    (fun a => rowRight (c159_A a)) c159_O = some c159_result := by decide +kernel
theorem c159_code : FiniteCodeCertificate (linearSystem c159_A c159_O) c159_result :=
  normalizedPrimeDiscover_code 2 2 4 c159_A c159_O c159_result c159_computed

abbrev c160_R := ZMod (3^2)
def c160_A : Fin 2 → Mat c160_R 4 4 := ![![![4, 3, 3, 8], ![5, 2, 0, 6], ![4, 8, 3, 3], ![3, 0, 1, 0]], ![![0, 5, 4, 6], ![3, 3, 7, 5], ![0, 8, 7, 4], ![5, 0, 7, 6]]]
def c160_O : Mat c160_R 2 4 := ![![5, 5, 3, 2], ![3, 8, 2, 6]]
def c160_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c160_computed : normalizedPrimeDiscover 3 2 4
    (fun a => rowRight (c160_A a)) c160_O = some c160_result := by decide +kernel
theorem c160_code : FiniteCodeCertificate (linearSystem c160_A c160_O) c160_result :=
  normalizedPrimeDiscover_code 3 2 4 c160_A c160_O c160_result c160_computed

abbrev c161_R := ZMod (5^2)
def c161_A : Fin 3 → Mat c161_R 4 4 := ![![![2, 17, 14, 23], ![24, 22, 13, 7], ![21, 1, 9, 10], ![10, 13, 19, 21]], ![![8, 8, 0, 21], ![17, 7, 10, 12], ![21, 19, 8, 22], ![19, 10, 4, 24]], ![![11, 20, 8, 1], ![2, 11, 19, 0], ![10, 13, 21, 22], ![2, 3, 6, 23]]]
def c161_O : Mat c161_R 1 4 := ![![20, 0, 5, 5]]
def c161_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c161_computed : normalizedPrimeDiscover 5 2 4
    (fun a => rowRight (c161_A a)) c161_O = some c161_result := by decide +kernel
theorem c161_code : FiniteCodeCertificate (linearSystem c161_A c161_O) c161_result :=
  normalizedPrimeDiscover_code 5 2 4 c161_A c161_O c161_result c161_computed

abbrev c162_R := ZMod (2^3)
def c162_A : Fin 1 → Mat c162_R 4 4 := ![![![7, 1, 1, 6], ![5, 3, 0, 6], ![2, 5, 1, 1], ![4, 6, 0, 0]]]
def c162_O : Mat c162_R 2 4 := ![![5, 7, 0, 7], ![1, 1, 4, 0]]
def c162_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c162_computed : normalizedPrimeDiscover 2 3 4
    (fun a => rowRight (c162_A a)) c162_O = some c162_result := by decide +kernel
theorem c162_code : FiniteCodeCertificate (linearSystem c162_A c162_O) c162_result :=
  normalizedPrimeDiscover_code 2 3 4 c162_A c162_O c162_result c162_computed

abbrev c163_R := ZMod (3^3)
def c163_A : Fin 2 → Mat c163_R 4 4 := ![![![23, 9, 26, 7], ![18, 0, 3, 2], ![15, 11, 16, 25], ![13, 8, 23, 20]], ![![25, 15, 0, 20], ![0, 23, 25, 16], ![7, 20, 18, 0], ![14, 22, 6, 13]]]
def c163_O : Mat c163_R 1 4 := ![![19, 23, 4, 1]]
def c163_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c163_computed : normalizedPrimeDiscover 3 3 4
    (fun a => rowRight (c163_A a)) c163_O = some c163_result := by decide +kernel
theorem c163_code : FiniteCodeCertificate (linearSystem c163_A c163_O) c163_result :=
  normalizedPrimeDiscover_code 3 3 4 c163_A c163_O c163_result c163_computed

abbrev c164_R := ZMod (5^3)
def c164_A : Fin 3 → Mat c164_R 4 4 := ![![![104, 15, 50, 10], ![108, 2, 122, 119], ![81, 63, 119, 1], ![113, 38, 57, 94]], ![![48, 13, 120, 73], ![115, 93, 26, 118], ![81, 55, 42, 53], ![22, 46, 85, 35]], ![![12, 83, 51, 50], ![10, 28, 115, 78], ![1, 16, 51, 59], ![66, 21, 99, 117]]]
def c164_O : Mat c164_R 2 4 := ![![0, 0, 0, 0], ![0, 0, 0, 0]]
def c164_result : List (Test 3 2) := []
theorem c164_computed : normalizedPrimeDiscover 5 3 4
    (fun a => rowRight (c164_A a)) c164_O = some c164_result := by decide +kernel
theorem c164_code : FiniteCodeCertificate (linearSystem c164_A c164_O) c164_result :=
  normalizedPrimeDiscover_code 5 3 4 c164_A c164_O c164_result c164_computed

abbrev c165_R := ZMod (2^4)
def c165_A : Fin 1 → Mat c165_R 4 4 := ![![![3, 15, 3, 12], ![7, 1, 15, 6], ![15, 15, 4, 10], ![4, 11, 14, 11]]]
def c165_O : Mat c165_R 1 4 := ![![4, 12, 13, 5]]
def c165_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem c165_computed : normalizedPrimeDiscover 2 4 4
    (fun a => rowRight (c165_A a)) c165_O = some c165_result := by decide +kernel
theorem c165_code : FiniteCodeCertificate (linearSystem c165_A c165_O) c165_result :=
  normalizedPrimeDiscover_code 2 4 4 c165_A c165_O c165_result c165_computed

abbrev c166_R := ZMod (3^4)
def c166_A : Fin 2 → Mat c166_R 4 4 := ![![![53, 14, 32, 38], ![30, 53, 41, 14], ![50, 37, 3, 10], ![28, 72, 25, 62]], ![![14, 34, 71, 31], ![29, 65, 63, 80], ![22, 73, 73, 42], ![47, 28, 46, 10]]]
def c166_O : Mat c166_R 2 4 := ![![60, 61, 8, 68], ![56, 44, 19, 65]]
def c166_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c166_computed : normalizedPrimeDiscover 3 4 4
    (fun a => rowRight (c166_A a)) c166_O = some c166_result := by decide +kernel
theorem c166_code : FiniteCodeCertificate (linearSystem c166_A c166_O) c166_result :=
  normalizedPrimeDiscover_code 3 4 4 c166_A c166_O c166_result c166_computed

abbrev c167_R := ZMod (5^4)
def c167_A : Fin 3 → Mat c167_R 4 4 := ![![![228, 259, 128, 311], ![28, 321, 151, 149], ![301, 573, 80, 432], ![245, 608, 616, 353]], ![![411, 190, 566, 104], ![489, 471, 221, 479], ![304, 267, 101, 93], ![50, 353, 375, 486]], ![![526, 452, 527, 315], ![489, 49, 584, 583], ![334, 588, 234, 169], ![49, 539, 422, 325]]]
def c167_O : Mat c167_R 1 4 := ![![457, 324, 495, 238]]
def c167_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c167_computed : normalizedPrimeDiscover 5 4 4
    (fun a => rowRight (c167_A a)) c167_O = some c167_result := by decide +kernel
theorem c167_code : FiniteCodeCertificate (linearSystem c167_A c167_O) c167_result :=
  normalizedPrimeDiscover_code 5 4 4 c167_A c167_O c167_result c167_computed

end Komorebi.NormalizedRegression.NormalizedComputed13
