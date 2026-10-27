module
public import BoundedDiscovery
@[expose] public section
namespace Komorebi.BoundedRegression.BoundedComputed15
open Komorebi.Discovery Komorebi.Discovery.BoundedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c180_R := ZMod (2^4)
def c180_A : Fin 1 → Mat c180_R 5 5 := ![![![8, 5, 4, 14, 14], ![14, 4, 3, 10, 0], ![4, 12, 8, 11, 11], ![10, 7, 2, 2, 10], ![6, 2, 3, 2, 9]]]
def c180_O : Mat c180_R 2 5 := ![![11, 7, 5, 15, 13], ![14, 8, 15, 11, 2]]
def c180_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c180_computed : boundedPrimeDiscover 2 4 5
    (fun a => rowRight (c180_A a)) c180_O = some c180_result := by decide +kernel
theorem c180_code : FiniteCodeCertificate (linearSystem c180_A c180_O) c180_result :=
  boundedPrimeDiscover_code 2 4 5 c180_A c180_O c180_result c180_computed

abbrev c181_R := ZMod (3^4)
def c181_A : Fin 2 → Mat c181_R 5 5 := ![![![67, 35, 20, 56, 25], ![1, 1, 58, 54, 33], ![42, 48, 80, 17, 7], ![19, 54, 20, 20, 60], ![39, 2, 29, 55, 65]], ![![11, 57, 23, 51, 3], ![23, 77, 48, 66, 33], ![11, 4, 13, 43, 50], ![8, 0, 66, 28, 26], ![21, 42, 48, 55, 21]]]
def c181_O : Mat c181_R 1 5 := ![![30, 60, 25, 52, 17]]
def c181_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c181_computed : boundedPrimeDiscover 3 4 5
    (fun a => rowRight (c181_A a)) c181_O = some c181_result := by decide +kernel
theorem c181_code : FiniteCodeCertificate (linearSystem c181_A c181_O) c181_result :=
  boundedPrimeDiscover_code 3 4 5 c181_A c181_O c181_result c181_computed

abbrev c182_R := ZMod (5^4)
def c182_A : Fin 3 → Mat c182_R 5 5 := ![![![268, 144, 159, 343, 415], ![132, 118, 156, 320, 123], ![14, 451, 581, 616, 522], ![129, 578, 466, 123, 60], ![613, 260, 435, 522, 512]], ![![600, 480, 119, 228, 559], ![486, 510, 619, 445, 189], ![104, 471, 459, 113, 57], ![408, 92, 176, 370, 517], ![194, 172, 537, 585, 241]], ![![139, 573, 318, 393, 37], ![351, 553, 231, 226, 183], ![37, 15, 174, 106, 530], ![46, 606, 525, 224, 85], ![273, 20, 89, 12, 188]]]
def c182_O : Mat c182_R 2 5 := ![![500, 0, 250, 250, 0], ![125, 500, 0, 250, 250]]
def c182_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem c182_computed : boundedPrimeDiscover 5 4 5
    (fun a => rowRight (c182_A a)) c182_O = some c182_result := by decide +kernel
theorem c182_code : FiniteCodeCertificate (linearSystem c182_A c182_O) c182_result :=
  boundedPrimeDiscover_code 5 4 5 c182_A c182_O c182_result c182_computed

abbrev c183_R := ZMod (2^5)
def c183_A : Fin 1 → Mat c183_R 5 5 := ![![![7, 24, 19, 15, 9], ![12, 29, 18, 19, 3], ![29, 5, 29, 29, 27], ![10, 15, 30, 16, 8], ![31, 20, 23, 25, 3]]]
def c183_O : Mat c183_R 1 5 := ![![15, 1, 30, 24, 4]]
def c183_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c183_computed : boundedPrimeDiscover 2 5 5
    (fun a => rowRight (c183_A a)) c183_O = some c183_result := by decide +kernel
theorem c183_code : FiniteCodeCertificate (linearSystem c183_A c183_O) c183_result :=
  boundedPrimeDiscover_code 2 5 5 c183_A c183_O c183_result c183_computed

abbrev c184_R := ZMod (3^5)
def c184_A : Fin 2 → Mat c184_R 5 5 := ![![![190, 61, 168, 113, 0], ![16, 1, 13, 131, 109], ![15, 17, 145, 1, 57], ![66, 46, 167, 80, 219], ![82, 90, 236, 120, 79]], ![![182, 240, 208, 122, 72], ![17, 129, 228, 181, 105], ![40, 131, 146, 133, 106], ![164, 47, 217, 2, 17], ![151, 162, 56, 95, 197]]]
def c184_O : Mat c184_R 2 5 := ![![171, 200, 177, 159, 118], ![199, 74, 135, 218, 222]]
def c184_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c184_computed : boundedPrimeDiscover 3 5 5
    (fun a => rowRight (c184_A a)) c184_O = some c184_result := by decide +kernel
theorem c184_code : FiniteCodeCertificate (linearSystem c184_A c184_O) c184_result :=
  boundedPrimeDiscover_code 3 5 5 c184_A c184_O c184_result c184_computed

abbrev c185_R := ZMod (5^5)
def c185_A : Fin 3 → Mat c185_R 5 5 := ![![![1331, 1876, 1173, 1684, 1937], ![556, 1499, 2714, 2283, 447], ![2803, 664, 2344, 1296, 1713], ![1422, 841, 2661, 2983, 3011], ![340, 110, 1368, 2398, 1549]], ![![697, 1148, 1073, 245, 517], ![26, 521, 2207, 1239, 2122], ![360, 1178, 355, 1939, 2263], ![1484, 2820, 1204, 2834, 2234], ![2608, 78, 445, 267, 2914]], ![![1649, 1259, 339, 2615, 1617], ![2869, 2745, 1957, 2747, 870], ![2567, 2842, 1321, 2954, 1983], ![2180, 2801, 2172, 2718, 1193], ![2544, 1971, 1024, 1694, 839]]]
def c185_O : Mat c185_R 1 5 := ![![1490, 937, 878, 624, 1892]]
def c185_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c185_computed : boundedPrimeDiscover 5 5 5
    (fun a => rowRight (c185_A a)) c185_O = some c185_result := by decide +kernel
theorem c185_code : FiniteCodeCertificate (linearSystem c185_A c185_O) c185_result :=
  boundedPrimeDiscover_code 5 5 5 c185_A c185_O c185_result c185_computed

abbrev c186_R := ZMod (2^1)
def c186_A : Fin 1 → Mat c186_R 6 6 := ![![![0, 1, 1, 0, 1, 0], ![1, 0, 1, 0, 0, 1], ![1, 0, 0, 1, 1, 0], ![0, 1, 0, 1, 1, 0], ![0, 0, 1, 1, 0, 0], ![1, 1, 1, 1, 0, 0]]]
def c186_O : Mat c186_R 2 6 := ![![1, 1, 0, 0, 1, 1], ![0, 0, 1, 0, 1, 0]]
def c186_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c186_computed : boundedPrimeDiscover 2 1 6
    (fun a => rowRight (c186_A a)) c186_O = some c186_result := by decide +kernel
theorem c186_code : FiniteCodeCertificate (linearSystem c186_A c186_O) c186_result :=
  boundedPrimeDiscover_code 2 1 6 c186_A c186_O c186_result c186_computed

abbrev c187_R := ZMod (3^1)
def c187_A : Fin 2 → Mat c187_R 6 6 := ![![![2, 2, 2, 1, 1, 1], ![2, 0, 2, 2, 1, 0], ![0, 0, 0, 0, 1, 0], ![2, 0, 2, 1, 0, 1], ![0, 0, 1, 2, 2, 1], ![1, 0, 1, 1, 2, 2]], ![![2, 2, 0, 0, 1, 1], ![0, 0, 2, 0, 1, 2], ![0, 2, 2, 1, 1, 0], ![2, 2, 2, 1, 0, 1], ![1, 2, 0, 0, 2, 0], ![0, 2, 2, 0, 0, 0]]]
def c187_O : Mat c187_R 1 6 := ![![1, 1, 1, 2, 1, 0]]
def c187_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([1,1], 0)]
theorem c187_computed : boundedPrimeDiscover 3 1 6
    (fun a => rowRight (c187_A a)) c187_O = some c187_result := by decide +kernel
theorem c187_code : FiniteCodeCertificate (linearSystem c187_A c187_O) c187_result :=
  boundedPrimeDiscover_code 3 1 6 c187_A c187_O c187_result c187_computed

abbrev c188_R := ZMod (5^1)
def c188_A : Fin 3 → Mat c188_R 6 6 := ![![![3, 2, 1, 4, 3, 1], ![4, 3, 3, 0, 3, 3], ![2, 4, 2, 2, 0, 4], ![1, 1, 2, 2, 0, 3], ![3, 2, 4, 1, 4, 3], ![4, 0, 0, 3, 3, 4]], ![![2, 3, 0, 2, 4, 2], ![2, 4, 3, 1, 3, 0], ![2, 4, 3, 1, 2, 0], ![1, 1, 0, 4, 4, 3], ![2, 3, 0, 2, 2, 0], ![1, 1, 3, 1, 2, 0]], ![![0, 4, 3, 0, 4, 2], ![2, 0, 0, 3, 4, 4], ![0, 4, 1, 0, 2, 1], ![1, 2, 1, 2, 1, 0], ![3, 2, 4, 4, 0, 0], ![4, 2, 4, 1, 3, 0]]]
def c188_O : Mat c188_R 2 6 := ![![2, 3, 3, 3, 3, 3], ![4, 0, 3, 4, 1, 4]]
def c188_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c188_computed : boundedPrimeDiscover 5 1 6
    (fun a => rowRight (c188_A a)) c188_O = some c188_result := by decide +kernel
theorem c188_code : FiniteCodeCertificate (linearSystem c188_A c188_O) c188_result :=
  boundedPrimeDiscover_code 5 1 6 c188_A c188_O c188_result c188_computed

abbrev c189_R := ZMod (2^2)
def c189_A : Fin 1 → Mat c189_R 6 6 := ![![![1, 3, 3, 1, 1, 0], ![0, 2, 2, 0, 1, 1], ![2, 3, 3, 3, 3, 0], ![1, 0, 1, 3, 3, 1], ![3, 1, 1, 3, 2, 3], ![3, 1, 3, 2, 3, 3]]]
def c189_O : Mat c189_R 1 6 := ![![0, 0, 0, 0, 0, 2]]
def c189_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
theorem c189_computed : boundedPrimeDiscover 2 2 6
    (fun a => rowRight (c189_A a)) c189_O = some c189_result := by decide +kernel
theorem c189_code : FiniteCodeCertificate (linearSystem c189_A c189_O) c189_result :=
  boundedPrimeDiscover_code 2 2 6 c189_A c189_O c189_result c189_computed

abbrev c190_R := ZMod (3^2)
def c190_A : Fin 2 → Mat c190_R 6 6 := ![![![1, 8, 2, 8, 5, 1], ![4, 1, 5, 8, 8, 8], ![1, 6, 8, 3, 7, 3], ![5, 6, 6, 8, 5, 2], ![6, 7, 2, 2, 7, 3], ![1, 4, 4, 5, 1, 5]], ![![5, 4, 1, 0, 0, 0], ![7, 8, 5, 6, 7, 4], ![8, 5, 4, 3, 4, 7], ![6, 7, 3, 2, 3, 3], ![2, 2, 4, 5, 2, 5], ![3, 3, 8, 1, 4, 1]]]
def c190_O : Mat c190_R 2 6 := ![![0, 0, 0, 0, 0, 0], ![0, 0, 0, 0, 0, 0]]
def c190_result : List (Test 2 2) := []
theorem c190_computed : boundedPrimeDiscover 3 2 6
    (fun a => rowRight (c190_A a)) c190_O = some c190_result := by decide +kernel
theorem c190_code : FiniteCodeCertificate (linearSystem c190_A c190_O) c190_result :=
  boundedPrimeDiscover_code 3 2 6 c190_A c190_O c190_result c190_computed

abbrev c191_R := ZMod (5^2)
def c191_A : Fin 3 → Mat c191_R 6 6 := ![![![20, 21, 12, 18, 2, 6], ![2, 2, 10, 22, 18, 14], ![2, 2, 1, 0, 3, 20], ![8, 18, 2, 4, 13, 20], ![2, 9, 5, 19, 10, 22], ![10, 2, 5, 11, 9, 17]], ![![1, 13, 24, 5, 7, 23], ![8, 5, 5, 24, 18, 1], ![4, 5, 21, 20, 6, 5], ![0, 1, 6, 23, 5, 0], ![8, 2, 12, 13, 4, 1], ![7, 15, 19, 21, 12, 17]], ![![16, 23, 14, 24, 6, 21], ![23, 14, 0, 1, 22, 1], ![10, 10, 23, 13, 5, 17], ![23, 0, 5, 2, 5, 0], ![5, 12, 15, 16, 1, 10], ![24, 13, 21, 24, 14, 2]]]
def c191_O : Mat c191_R 1 6 := ![![22, 19, 4, 10, 21, 15]]
def c191_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c191_computed : boundedPrimeDiscover 5 2 6
    (fun a => rowRight (c191_A a)) c191_O = some c191_result := by decide +kernel
theorem c191_code : FiniteCodeCertificate (linearSystem c191_A c191_O) c191_result :=
  boundedPrimeDiscover_code 5 2 6 c191_A c191_O c191_result c191_computed

end Komorebi.BoundedRegression.BoundedComputed15
