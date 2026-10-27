module
public import BoundedDiscovery
@[expose] public section
namespace Komorebi.BoundedRegression.BoundedComputed05
open Komorebi.Discovery Komorebi.Discovery.BoundedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c060_R := ZMod (2^4)
def c060_A : Fin 1 → Mat c060_R 3 3 := ![![![15, 5, 9], ![14, 6, 5], ![15, 7, 2]]]
def c060_O : Mat c060_R 2 3 := ![![0, 0, 0], ![0, 0, 0]]
def c060_result : List (Test 1 2) := []
theorem c060_computed : boundedPrimeDiscover 2 4 3
    (fun a => rowRight (c060_A a)) c060_O = some c060_result := by decide +kernel
theorem c060_code : FiniteCodeCertificate (linearSystem c060_A c060_O) c060_result :=
  boundedPrimeDiscover_code 2 4 3 c060_A c060_O c060_result c060_computed

abbrev c061_R := ZMod (3^4)
def c061_A : Fin 2 → Mat c061_R 3 3 := ![![![9, 78, 10], ![48, 19, 63], ![34, 28, 75]], ![![53, 1, 76], ![6, 14, 48], ![5, 18, 9]]]
def c061_O : Mat c061_R 1 3 := ![![76, 64, 33]]
def c061_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c061_computed : boundedPrimeDiscover 3 4 3
    (fun a => rowRight (c061_A a)) c061_O = some c061_result := by decide +kernel
theorem c061_code : FiniteCodeCertificate (linearSystem c061_A c061_O) c061_result :=
  boundedPrimeDiscover_code 3 4 3 c061_A c061_O c061_result c061_computed

abbrev c062_R := ZMod (5^4)
def c062_A : Fin 3 → Mat c062_R 3 3 := ![![![160, 517, 144], ![590, 142, 456], ![497, 266, 206]], ![![136, 113, 520], ![493, 130, 537], ![535, 151, 204]], ![![282, 292, 605], ![375, 467, 617], ![485, 126, 288]]]
def c062_O : Mat c062_R 2 3 := ![![89, 88, 344], ![264, 398, 38]]
def c062_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c062_computed : boundedPrimeDiscover 5 4 3
    (fun a => rowRight (c062_A a)) c062_O = some c062_result := by decide +kernel
theorem c062_code : FiniteCodeCertificate (linearSystem c062_A c062_O) c062_result :=
  boundedPrimeDiscover_code 5 4 3 c062_A c062_O c062_result c062_computed

abbrev c063_R := ZMod (2^5)
def c063_A : Fin 1 → Mat c063_R 3 3 := ![![![13, 29, 18], ![0, 8, 25], ![5, 2, 10]]]
def c063_O : Mat c063_R 1 3 := ![![16, 16, 0]]
def c063_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c063_computed : boundedPrimeDiscover 2 5 3
    (fun a => rowRight (c063_A a)) c063_O = some c063_result := by decide +kernel
theorem c063_code : FiniteCodeCertificate (linearSystem c063_A c063_O) c063_result :=
  boundedPrimeDiscover_code 2 5 3 c063_A c063_O c063_result c063_computed

abbrev c064_R := ZMod (3^5)
def c064_A : Fin 2 → Mat c064_R 3 3 := ![![![210, 234, 106], ![198, 108, 88], ![31, 167, 0]], ![![134, 136, 111], ![198, 36, 175], ![121, 87, 5]]]
def c064_O : Mat c064_R 2 3 := ![![218, 69, 14], ![193, 136, 176]]
def c064_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c064_computed : boundedPrimeDiscover 3 5 3
    (fun a => rowRight (c064_A a)) c064_O = some c064_result := by decide +kernel
theorem c064_code : FiniteCodeCertificate (linearSystem c064_A c064_O) c064_result :=
  boundedPrimeDiscover_code 3 5 3 c064_A c064_O c064_result c064_computed

abbrev c065_R := ZMod (5^5)
def c065_A : Fin 3 → Mat c065_R 3 3 := ![![![2173, 2544, 1397], ![1021, 486, 1535], ![1572, 361, 2817]], ![![2288, 2418, 2357], ![2124, 1439, 652], ![718, 1107, 2369]], ![![2742, 560, 1777], ![1221, 571, 2366], ![20, 2849, 1531]]]
def c065_O : Mat c065_R 1 3 := ![![2434, 1545, 60]]
def c065_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c065_computed : boundedPrimeDiscover 5 5 3
    (fun a => rowRight (c065_A a)) c065_O = some c065_result := by decide +kernel
theorem c065_code : FiniteCodeCertificate (linearSystem c065_A c065_O) c065_result :=
  boundedPrimeDiscover_code 5 5 3 c065_A c065_O c065_result c065_computed

abbrev c066_R := ZMod (2^1)
def c066_A : Fin 1 → Mat c066_R 4 4 := ![![![1, 1, 0, 1], ![0, 1, 1, 1], ![0, 1, 1, 0], ![0, 0, 1, 0]]]
def c066_O : Mat c066_R 2 4 := ![![0, 1, 1, 1], ![0, 0, 0, 1]]
def c066_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c066_computed : boundedPrimeDiscover 2 1 4
    (fun a => rowRight (c066_A a)) c066_O = some c066_result := by decide +kernel
theorem c066_code : FiniteCodeCertificate (linearSystem c066_A c066_O) c066_result :=
  boundedPrimeDiscover_code 2 1 4 c066_A c066_O c066_result c066_computed

abbrev c067_R := ZMod (3^1)
def c067_A : Fin 2 → Mat c067_R 4 4 := ![![![1, 1, 2, 1], ![2, 2, 1, 2], ![0, 0, 1, 1], ![0, 0, 0, 1]], ![![2, 1, 0, 0], ![0, 1, 2, 1], ![2, 1, 2, 0], ![2, 2, 1, 1]]]
def c067_O : Mat c067_R 1 4 := ![![2, 2, 2, 2]]
def c067_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c067_computed : boundedPrimeDiscover 3 1 4
    (fun a => rowRight (c067_A a)) c067_O = some c067_result := by decide +kernel
theorem c067_code : FiniteCodeCertificate (linearSystem c067_A c067_O) c067_result :=
  boundedPrimeDiscover_code 3 1 4 c067_A c067_O c067_result c067_computed

abbrev c068_R := ZMod (5^1)
def c068_A : Fin 3 → Mat c068_R 4 4 := ![![![0, 2, 0, 0], ![3, 0, 2, 0], ![3, 3, 1, 4], ![0, 3, 3, 0]], ![![1, 0, 3, 0], ![3, 1, 4, 1], ![0, 1, 0, 1], ![1, 1, 0, 2]], ![![2, 0, 4, 0], ![0, 2, 3, 1], ![3, 4, 3, 2], ![0, 2, 3, 3]]]
def c068_O : Mat c068_R 2 4 := ![![3, 3, 3, 3], ![4, 4, 2, 3]]
def c068_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c068_computed : boundedPrimeDiscover 5 1 4
    (fun a => rowRight (c068_A a)) c068_O = some c068_result := by decide +kernel
theorem c068_code : FiniteCodeCertificate (linearSystem c068_A c068_O) c068_result :=
  boundedPrimeDiscover_code 5 1 4 c068_A c068_O c068_result c068_computed

abbrev c069_R := ZMod (2^2)
def c069_A : Fin 1 → Mat c069_R 4 4 := ![![![0, 3, 1, 3], ![3, 2, 2, 0], ![2, 1, 2, 3], ![0, 3, 2, 1]]]
def c069_O : Mat c069_R 1 4 := ![![1, 1, 3, 1]]
def c069_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c069_computed : boundedPrimeDiscover 2 2 4
    (fun a => rowRight (c069_A a)) c069_O = some c069_result := by decide +kernel
theorem c069_code : FiniteCodeCertificate (linearSystem c069_A c069_O) c069_result :=
  boundedPrimeDiscover_code 2 2 4 c069_A c069_O c069_result c069_computed

abbrev c070_R := ZMod (3^2)
def c070_A : Fin 2 → Mat c070_R 4 4 := ![![![4, 2, 3, 1], ![0, 2, 3, 5], ![0, 4, 1, 5], ![3, 2, 2, 3]], ![![6, 7, 4, 4], ![3, 4, 5, 3], ![6, 8, 3, 4], ![5, 4, 3, 6]]]
def c070_O : Mat c070_R 2 4 := ![![3, 6, 3, 3], ![3, 0, 3, 3]]
def c070_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c070_computed : boundedPrimeDiscover 3 2 4
    (fun a => rowRight (c070_A a)) c070_O = some c070_result := by decide +kernel
theorem c070_code : FiniteCodeCertificate (linearSystem c070_A c070_O) c070_result :=
  boundedPrimeDiscover_code 3 2 4 c070_A c070_O c070_result c070_computed

abbrev c071_R := ZMod (5^2)
def c071_A : Fin 3 → Mat c071_R 4 4 := ![![![2, 3, 23, 12], ![12, 8, 13, 2], ![12, 16, 15, 17], ![16, 6, 12, 11]], ![![14, 10, 3, 5], ![10, 7, 0, 10], ![1, 19, 14, 8], ![15, 1, 12, 12]], ![![19, 24, 18, 22], ![12, 7, 5, 19], ![23, 15, 5, 19], ![22, 17, 8, 6]]]
def c071_O : Mat c071_R 1 4 := ![![1, 8, 11, 6]]
def c071_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c071_computed : boundedPrimeDiscover 5 2 4
    (fun a => rowRight (c071_A a)) c071_O = some c071_result := by decide +kernel
theorem c071_code : FiniteCodeCertificate (linearSystem c071_A c071_O) c071_result :=
  boundedPrimeDiscover_code 5 2 4 c071_A c071_O c071_result c071_computed

end Komorebi.BoundedRegression.BoundedComputed05
