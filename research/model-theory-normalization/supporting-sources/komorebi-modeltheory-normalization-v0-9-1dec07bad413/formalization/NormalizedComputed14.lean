module
public import NormalizedDiscovery
@[expose] public section
namespace Komorebi.NormalizedRegression.NormalizedComputed14
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c168_R := ZMod (2^5)
def c168_A : Fin 1 → Mat c168_R 4 4 := ![![![27, 28, 4, 29], ![14, 19, 14, 27], ![16, 8, 25, 27], ![3, 3, 28, 12]]]
def c168_O : Mat c168_R 2 4 := ![![16, 16, 16, 0], ![16, 0, 16, 0]]
def c168_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0,0], 0)]
theorem c168_computed : normalizedPrimeDiscover 2 5 4
    (fun a => rowRight (c168_A a)) c168_O = some c168_result := by decide +kernel
theorem c168_code : FiniteCodeCertificate (linearSystem c168_A c168_O) c168_result :=
  normalizedPrimeDiscover_code 2 5 4 c168_A c168_O c168_result c168_computed

abbrev c169_R := ZMod (3^5)
def c169_A : Fin 2 → Mat c169_R 4 4 := ![![![32, 180, 15, 20], ![59, 86, 189, 61], ![134, 9, 112, 209], ![81, 1, 99, 94]], ![![177, 114, 54, 45], ![92, 125, 240, 197], ![150, 83, 136, 114], ![5, 176, 145, 7]]]
def c169_O : Mat c169_R 1 4 := ![![73, 8, 194, 48]]
def c169_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c169_computed : normalizedPrimeDiscover 3 5 4
    (fun a => rowRight (c169_A a)) c169_O = some c169_result := by decide +kernel
theorem c169_code : FiniteCodeCertificate (linearSystem c169_A c169_O) c169_result :=
  normalizedPrimeDiscover_code 3 5 4 c169_A c169_O c169_result c169_computed

abbrev c170_R := ZMod (5^5)
def c170_A : Fin 3 → Mat c170_R 4 4 := ![![![422, 1382, 2161, 2712], ![1903, 1948, 1425, 397], ![1316, 489, 2493, 1136], ![2740, 1710, 724, 569]], ![![2544, 761, 2548, 1006], ![700, 2335, 243, 1972], ![2007, 2783, 2393, 2029], ![1475, 435, 1958, 547]], ![![1602, 2746, 2378, 2127], ![1559, 1191, 150, 2970], ![3057, 2550, 2597, 662], ![1123, 1514, 409, 2522]]]
def c170_O : Mat c170_R 2 4 := ![![1426, 1137, 565, 2015], ![3043, 3060, 2509, 1388]]
def c170_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c170_computed : normalizedPrimeDiscover 5 5 4
    (fun a => rowRight (c170_A a)) c170_O = some c170_result := by decide +kernel
theorem c170_code : FiniteCodeCertificate (linearSystem c170_A c170_O) c170_result :=
  normalizedPrimeDiscover_code 5 5 4 c170_A c170_O c170_result c170_computed

abbrev c171_R := ZMod (2^1)
def c171_A : Fin 1 → Mat c171_R 5 5 := ![![![0, 0, 0, 0, 1], ![0, 0, 0, 0, 1], ![0, 1, 1, 1, 1], ![0, 0, 0, 1, 0], ![1, 1, 0, 0, 0]]]
def c171_O : Mat c171_R 1 5 := ![![1, 1, 1, 1, 1]]
def c171_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c171_computed : normalizedPrimeDiscover 2 1 5
    (fun a => rowRight (c171_A a)) c171_O = some c171_result := by decide +kernel
theorem c171_code : FiniteCodeCertificate (linearSystem c171_A c171_O) c171_result :=
  normalizedPrimeDiscover_code 2 1 5 c171_A c171_O c171_result c171_computed

abbrev c172_R := ZMod (3^1)
def c172_A : Fin 2 → Mat c172_R 5 5 := ![![![0, 0, 1, 2, 1], ![1, 1, 1, 1, 0], ![1, 2, 2, 0, 1], ![0, 0, 2, 0, 1], ![2, 1, 2, 1, 1]], ![![0, 0, 0, 2, 2], ![2, 1, 2, 1, 0], ![1, 2, 1, 0, 0], ![1, 1, 2, 1, 1], ![0, 2, 2, 0, 1]]]
def c172_O : Mat c172_R 2 5 := ![![0, 0, 1, 0, 0], ![0, 2, 2, 0, 2]]
def c172_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c172_computed : normalizedPrimeDiscover 3 1 5
    (fun a => rowRight (c172_A a)) c172_O = some c172_result := by decide +kernel
theorem c172_code : FiniteCodeCertificate (linearSystem c172_A c172_O) c172_result :=
  normalizedPrimeDiscover_code 3 1 5 c172_A c172_O c172_result c172_computed

abbrev c173_R := ZMod (5^1)
def c173_A : Fin 3 → Mat c173_R 5 5 := ![![![0, 2, 0, 3, 2], ![0, 2, 3, 1, 1], ![2, 3, 1, 2, 4], ![3, 0, 3, 1, 3], ![1, 2, 2, 4, 2]], ![![1, 1, 3, 0, 1], ![2, 2, 0, 3, 2], ![3, 4, 1, 4, 1], ![2, 3, 4, 1, 3], ![0, 4, 3, 1, 2]], ![![3, 2, 4, 2, 1], ![3, 0, 2, 4, 2], ![4, 1, 4, 1, 1], ![0, 3, 4, 2, 3], ![4, 2, 0, 2, 2]]]
def c173_O : Mat c173_R 1 5 := ![![1, 4, 0, 0, 4]]
def c173_result : List (Test 3 1) := [([], 0), ([0], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c173_computed : normalizedPrimeDiscover 5 1 5
    (fun a => rowRight (c173_A a)) c173_O = some c173_result := by decide +kernel
theorem c173_code : FiniteCodeCertificate (linearSystem c173_A c173_O) c173_result :=
  normalizedPrimeDiscover_code 5 1 5 c173_A c173_O c173_result c173_computed

abbrev c174_R := ZMod (2^2)
def c174_A : Fin 1 → Mat c174_R 5 5 := ![![![1, 0, 2, 1, 3], ![3, 1, 2, 0, 1], ![2, 0, 2, 2, 2], ![2, 3, 0, 2, 0], ![2, 3, 2, 2, 0]]]
def c174_O : Mat c174_R 2 5 := ![![1, 3, 3, 0, 3], ![2, 1, 3, 3, 2]]
def c174_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c174_computed : normalizedPrimeDiscover 2 2 5
    (fun a => rowRight (c174_A a)) c174_O = some c174_result := by decide +kernel
theorem c174_code : FiniteCodeCertificate (linearSystem c174_A c174_O) c174_result :=
  normalizedPrimeDiscover_code 2 2 5 c174_A c174_O c174_result c174_computed

abbrev c175_R := ZMod (3^2)
def c175_A : Fin 2 → Mat c175_R 5 5 := ![![![7, 6, 5, 8, 1], ![3, 1, 2, 2, 7], ![8, 4, 2, 1, 6], ![3, 1, 7, 6, 7], ![7, 6, 7, 8, 4]], ![![6, 2, 8, 1, 5], ![4, 7, 8, 6, 0], ![2, 1, 8, 2, 3], ![1, 7, 4, 0, 8], ![6, 0, 3, 8, 0]]]
def c175_O : Mat c175_R 1 5 := ![![6, 6, 6, 3, 0]]
def c175_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([0,1], 0)]
theorem c175_computed : normalizedPrimeDiscover 3 2 5
    (fun a => rowRight (c175_A a)) c175_O = some c175_result := by decide +kernel
theorem c175_code : FiniteCodeCertificate (linearSystem c175_A c175_O) c175_result :=
  normalizedPrimeDiscover_code 3 2 5 c175_A c175_O c175_result c175_computed

abbrev c176_R := ZMod (5^2)
def c176_A : Fin 3 → Mat c176_R 5 5 := ![![![8, 3, 20, 15, 0], ![10, 17, 7, 17, 23], ![23, 14, 8, 4, 4], ![18, 10, 21, 8, 2], ![17, 4, 18, 8, 13]], ![![22, 14, 5, 15, 8], ![5, 15, 1, 4, 20], ![24, 12, 23, 2, 21], ![10, 9, 5, 18, 21], ![11, 16, 16, 22, 23]], ![![10, 24, 10, 3, 23], ![0, 6, 22, 11, 3], ![21, 15, 20, 0, 11], ![9, 14, 20, 21, 9], ![2, 13, 10, 2, 8]]]
def c176_O : Mat c176_R 2 5 := ![![14, 15, 6, 2, 19], ![11, 22, 22, 4, 19]]
def c176_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem c176_computed : normalizedPrimeDiscover 5 2 5
    (fun a => rowRight (c176_A a)) c176_O = some c176_result := by decide +kernel
theorem c176_code : FiniteCodeCertificate (linearSystem c176_A c176_O) c176_result :=
  normalizedPrimeDiscover_code 5 2 5 c176_A c176_O c176_result c176_computed

abbrev c177_R := ZMod (2^3)
def c177_A : Fin 1 → Mat c177_R 5 5 := ![![![6, 2, 6, 0, 0], ![1, 0, 4, 1, 7], ![4, 7, 0, 0, 7], ![2, 3, 6, 4, 2], ![0, 1, 4, 3, 3]]]
def c177_O : Mat c177_R 1 5 := ![![0, 0, 0, 0, 0]]
def c177_result : List (Test 1 1) := []
theorem c177_computed : normalizedPrimeDiscover 2 3 5
    (fun a => rowRight (c177_A a)) c177_O = some c177_result := by decide +kernel
theorem c177_code : FiniteCodeCertificate (linearSystem c177_A c177_O) c177_result :=
  normalizedPrimeDiscover_code 2 3 5 c177_A c177_O c177_result c177_computed

abbrev c178_R := ZMod (3^3)
def c178_A : Fin 2 → Mat c178_R 5 5 := ![![![9, 26, 6, 11, 22], ![5, 3, 16, 21, 5], ![20, 21, 14, 18, 23], ![22, 10, 10, 0, 11], ![4, 1, 18, 10, 24]], ![![11, 7, 16, 1, 12], ![13, 23, 3, 6, 16], ![18, 0, 21, 9, 3], ![23, 19, 18, 12, 1], ![15, 18, 12, 9, 17]]]
def c178_O : Mat c178_R 2 5 := ![![1, 26, 5, 18, 8], ![1, 8, 11, 8, 14]]
def c178_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c178_computed : normalizedPrimeDiscover 3 3 5
    (fun a => rowRight (c178_A a)) c178_O = some c178_result := by decide +kernel
theorem c178_code : FiniteCodeCertificate (linearSystem c178_A c178_O) c178_result :=
  normalizedPrimeDiscover_code 3 3 5 c178_A c178_O c178_result c178_computed

abbrev c179_R := ZMod (5^3)
def c179_A : Fin 3 → Mat c179_R 5 5 := ![![![32, 102, 60, 71, 42], ![88, 6, 107, 17, 38], ![29, 84, 118, 61, 84], ![52, 65, 94, 65, 43], ![68, 84, 122, 55, 44]], ![![86, 96, 83, 4, 9], ![58, 110, 97, 87, 94], ![53, 24, 18, 6, 39], ![104, 47, 51, 52, 67], ![45, 102, 67, 16, 95]], ![![16, 104, 75, 74, 22], ![74, 42, 118, 43, 116], ![48, 29, 7, 71, 96], ![69, 101, 1, 22, 98], ![61, 24, 89, 66, 22]]]
def c179_O : Mat c179_R 1 5 := ![![26, 33, 34, 59, 59]]
def c179_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c179_computed : normalizedPrimeDiscover 5 3 5
    (fun a => rowRight (c179_A a)) c179_O = some c179_result := by decide +kernel
theorem c179_code : FiniteCodeCertificate (linearSystem c179_A c179_O) c179_result :=
  normalizedPrimeDiscover_code 5 3 5 c179_A c179_O c179_result c179_computed

end Komorebi.NormalizedRegression.NormalizedComputed14
