module
public import NormalizedDiscovery
@[expose] public section
namespace Komorebi.NormalizedRegression.NormalizedComputed12
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c144_R := ZMod (2^2)
def c144_A : Fin 1 → Mat c144_R 3 3 := ![![![1, 1, 2], ![3, 3, 0], ![2, 2, 2]]]
def c144_O : Mat c144_R 2 3 := ![![2, 1, 2], ![1, 1, 1]]
def c144_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c144_computed : normalizedPrimeDiscover 2 2 3
    (fun a => rowRight (c144_A a)) c144_O = some c144_result := by decide +kernel
theorem c144_code : FiniteCodeCertificate (linearSystem c144_A c144_O) c144_result :=
  normalizedPrimeDiscover_code 2 2 3 c144_A c144_O c144_result c144_computed

abbrev c145_R := ZMod (3^2)
def c145_A : Fin 2 → Mat c145_R 3 3 := ![![![1, 1, 5], ![0, 2, 0], ![1, 0, 0]], ![![0, 7, 4], ![2, 7, 8], ![2, 8, 7]]]
def c145_O : Mat c145_R 1 3 := ![![7, 5, 8]]
def c145_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c145_computed : normalizedPrimeDiscover 3 2 3
    (fun a => rowRight (c145_A a)) c145_O = some c145_result := by decide +kernel
theorem c145_code : FiniteCodeCertificate (linearSystem c145_A c145_O) c145_result :=
  normalizedPrimeDiscover_code 3 2 3 c145_A c145_O c145_result c145_computed

abbrev c146_R := ZMod (5^2)
def c146_A : Fin 3 → Mat c146_R 3 3 := ![![![9, 0, 3], ![10, 13, 19], ![8, 19, 2]], ![![0, 24, 18], ![3, 17, 7], ![10, 10, 22]], ![![24, 22, 21], ![8, 14, 20], ![5, 8, 0]]]
def c146_O : Mat c146_R 2 3 := ![![2, 6, 5], ![9, 1, 7]]
def c146_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c146_computed : normalizedPrimeDiscover 5 2 3
    (fun a => rowRight (c146_A a)) c146_O = some c146_result := by decide +kernel
theorem c146_code : FiniteCodeCertificate (linearSystem c146_A c146_O) c146_result :=
  normalizedPrimeDiscover_code 5 2 3 c146_A c146_O c146_result c146_computed

abbrev c147_R := ZMod (2^3)
def c147_A : Fin 1 → Mat c147_R 3 3 := ![![![6, 2, 0], ![5, 5, 6], ![6, 0, 4]]]
def c147_O : Mat c147_R 1 3 := ![![4, 4, 0]]
def c147_result : List (Test 1 1) := [([], 0)]
theorem c147_computed : normalizedPrimeDiscover 2 3 3
    (fun a => rowRight (c147_A a)) c147_O = some c147_result := by decide +kernel
theorem c147_code : FiniteCodeCertificate (linearSystem c147_A c147_O) c147_result :=
  normalizedPrimeDiscover_code 2 3 3 c147_A c147_O c147_result c147_computed

abbrev c148_R := ZMod (3^3)
def c148_A : Fin 2 → Mat c148_R 3 3 := ![![![18, 9, 26], ![9, 1, 24], ![26, 22, 4]], ![![8, 10, 13], ![23, 18, 15], ![16, 8, 26]]]
def c148_O : Mat c148_R 2 3 := ![![25, 23, 3], ![20, 4, 4]]
def c148_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c148_computed : normalizedPrimeDiscover 3 3 3
    (fun a => rowRight (c148_A a)) c148_O = some c148_result := by decide +kernel
theorem c148_code : FiniteCodeCertificate (linearSystem c148_A c148_O) c148_result :=
  normalizedPrimeDiscover_code 3 3 3 c148_A c148_O c148_result c148_computed

abbrev c149_R := ZMod (5^3)
def c149_A : Fin 3 → Mat c149_R 3 3 := ![![![77, 101, 14], ![27, 120, 50], ![49, 1, 54]], ![![78, 67, 118], ![48, 117, 101], ![84, 92, 110]], ![![27, 38, 37], ![68, 75, 63], ![77, 49, 18]]]
def c149_O : Mat c149_R 1 3 := ![![96, 51, 95]]
def c149_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c149_computed : normalizedPrimeDiscover 5 3 3
    (fun a => rowRight (c149_A a)) c149_O = some c149_result := by decide +kernel
theorem c149_code : FiniteCodeCertificate (linearSystem c149_A c149_O) c149_result :=
  normalizedPrimeDiscover_code 5 3 3 c149_A c149_O c149_result c149_computed

abbrev c150_R := ZMod (2^4)
def c150_A : Fin 1 → Mat c150_R 3 3 := ![![![12, 3, 2], ![15, 2, 3], ![10, 15, 12]]]
def c150_O : Mat c150_R 2 3 := ![![2, 1, 6], ![5, 11, 2]]
def c150_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c150_computed : normalizedPrimeDiscover 2 4 3
    (fun a => rowRight (c150_A a)) c150_O = some c150_result := by decide +kernel
theorem c150_code : FiniteCodeCertificate (linearSystem c150_A c150_O) c150_result :=
  normalizedPrimeDiscover_code 2 4 3 c150_A c150_O c150_result c150_computed

abbrev c151_R := ZMod (3^4)
def c151_A : Fin 2 → Mat c151_R 3 3 := ![![![16, 31, 53], ![25, 49, 2], ![47, 75, 50]], ![![9, 31, 44], ![80, 80, 67], ![11, 26, 6]]]
def c151_O : Mat c151_R 1 3 := ![![0, 0, 0]]
def c151_result : List (Test 2 1) := []
theorem c151_computed : normalizedPrimeDiscover 3 4 3
    (fun a => rowRight (c151_A a)) c151_O = some c151_result := by decide +kernel
theorem c151_code : FiniteCodeCertificate (linearSystem c151_A c151_O) c151_result :=
  normalizedPrimeDiscover_code 3 4 3 c151_A c151_O c151_result c151_computed

abbrev c152_R := ZMod (5^4)
def c152_A : Fin 3 → Mat c152_R 3 3 := ![![![451, 436, 276], ![479, 93, 432], ![589, 339, 233]], ![![484, 347, 456], ![427, 476, 265], ![207, 564, 148]], ![![456, 254, 330], ![443, 360, 400], ![63, 151, 0]]]
def c152_O : Mat c152_R 2 3 := ![![37, 453, 286], ![34, 229, 482]]
def c152_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c152_computed : normalizedPrimeDiscover 5 4 3
    (fun a => rowRight (c152_A a)) c152_O = some c152_result := by decide +kernel
theorem c152_code : FiniteCodeCertificate (linearSystem c152_A c152_O) c152_result :=
  normalizedPrimeDiscover_code 5 4 3 c152_A c152_O c152_result c152_computed

abbrev c153_R := ZMod (2^5)
def c153_A : Fin 1 → Mat c153_R 3 3 := ![![![27, 29, 9], ![7, 17, 9], ![16, 8, 6]]]
def c153_O : Mat c153_R 1 3 := ![![16, 8, 24]]
def c153_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c153_computed : normalizedPrimeDiscover 2 5 3
    (fun a => rowRight (c153_A a)) c153_O = some c153_result := by decide +kernel
theorem c153_code : FiniteCodeCertificate (linearSystem c153_A c153_O) c153_result :=
  normalizedPrimeDiscover_code 2 5 3 c153_A c153_O c153_result c153_computed

abbrev c154_R := ZMod (3^5)
def c154_A : Fin 2 → Mat c154_R 3 3 := ![![![116, 198, 222], ![107, 204, 174], ![233, 118, 207]], ![![175, 226, 161], ![216, 153, 179], ![158, 1, 62]]]
def c154_O : Mat c154_R 2 3 := ![![162, 0, 162], ![162, 0, 0]]
def c154_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c154_computed : normalizedPrimeDiscover 3 5 3
    (fun a => rowRight (c154_A a)) c154_O = some c154_result := by decide +kernel
theorem c154_code : FiniteCodeCertificate (linearSystem c154_A c154_O) c154_result :=
  normalizedPrimeDiscover_code 3 5 3 c154_A c154_O c154_result c154_computed

abbrev c155_R := ZMod (5^5)
def c155_A : Fin 3 → Mat c155_R 3 3 := ![![![2481, 458, 154], ![1844, 1174, 1557], ![498, 1764, 589]], ![![1001, 1571, 2305], ![1475, 48, 1870], ![1439, 2881, 1601]], ![![2436, 873, 1668], ![405, 1803, 791], ![2667, 589, 1326]]]
def c155_O : Mat c155_R 1 3 := ![![2013, 514, 992]]
def c155_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c155_computed : normalizedPrimeDiscover 5 5 3
    (fun a => rowRight (c155_A a)) c155_O = some c155_result := by decide +kernel
theorem c155_code : FiniteCodeCertificate (linearSystem c155_A c155_O) c155_result :=
  normalizedPrimeDiscover_code 5 5 3 c155_A c155_O c155_result c155_computed

end Komorebi.NormalizedRegression.NormalizedComputed12
